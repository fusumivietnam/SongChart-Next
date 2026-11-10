"""Candidate in-memory Playwright context handoff; never starts a browser.

The caller must first run the reviewed provenance/cookie bootstrap and create
an isolated Playwright context with service_workers='block'. No credential is
serialized, printed, or made available as a general request header.
"""
from __future__ import annotations

from urllib.parse import urljoin, urlsplit

from preview_browser_preflight import HOST


class BrowserContextRejected(ValueError):
    """No credential-bearing diagnostic content is included in this error."""


def _origin_host(origin: str) -> str:
    parts = urlsplit(origin)
    if (parts.scheme != "https" or not parts.hostname or not HOST.fullmatch(parts.hostname)
            or parts.netloc != parts.hostname or parts.path not in ("", "/")
            or parts.query or parts.fragment):
        raise BrowserContextRejected("invalid Preview origin")
    return parts.hostname


def _is_allowed_request(url: str, allowed_origin: str) -> bool:
    try:
        parts = urlsplit(url)
        allowed = urlsplit(allowed_origin)
        return (parts.scheme == allowed.scheme == "https" and parts.netloc == allowed.netloc
                and parts.username is None and parts.password is None)
    except ValueError:
        return False


def _install_origin_guard(context, allowed_origin: str) -> None:
    """Guard each hop, including redirects, before releasing a browser response.

    ``route.continue_()`` hands redirects to Chromium without routing each hop;
    that can send a protected cookie/request outside the approved origin.
    Fetch exactly one hop and fulfill it only if its redirect target is safe.
    """
    def origin_only(route):
        if not _is_allowed_request(route.request.url, allowed_origin):
            route.abort()
            return

        try:
            response = route.fetch(max_redirects=0)
            if 300 <= response.status < 400:
                location = response.headers.get("location")
                if not location or not _is_allowed_request(
                    urljoin(route.request.url, location), allowed_origin
                ):
                    route.abort()
                    return
            route.fulfill(response=response)
        except Exception:
            # Network/redirect verification failures must not fall back to
            # Chromium's unguarded network continuation.
            route.abort()

    context.route("**/*", origin_only)
    # HTTP request routes do not govern WebSocket handshakes. This conservative
    # read-only probe never needs WebSockets; block them before cookie injection.
    context.route_web_socket("**/*", lambda socket: socket.close())


def install_isolated_cookie(context, origin: str, cookie: dict[str, object]) -> None:
    """Install a validated cookie after restricting requests in a fresh sync context.

    Context must be newly created with `service_workers='block'`. This is a
    contract-tested *handoff component*, not authorization to run live Preview.
    """
    host = _origin_host(origin)
    if (set(cookie) != {"name", "value", "domain", "path", "secure", "httpOnly", "sameSite"}
            or cookie["name"] != "_vercel_jwt" or not isinstance(cookie["value"], str)
            or not cookie["value"] or cookie["domain"] != host or cookie["path"] != "/"
            or cookie["secure"] is not True or cookie["httpOnly"] is not True
            or cookie["sameSite"] not in ("Lax", "Strict")):
        raise BrowserContextRejected("invalid isolated cookie contract")

    # Install the browser-wide egress guard BEFORE handing over the cookie.
    _install_origin_guard(context, "https://" + host)
    # Playwright `url` form, not a Domain attribute, keeps this host-only.
    context.add_cookies([{
        "url": "https://" + host + "/",
        "name": "_vercel_jwt",
        "value": cookie["value"],
        "secure": True,
        "httpOnly": True,
        "sameSite": cookie["sameSite"],
    }])
