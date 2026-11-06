"""Candidate in-memory Playwright context handoff; never starts a browser.

The caller must first run the reviewed provenance/cookie bootstrap and create
an isolated Playwright context with service_workers='block'. No credential is
serialized, printed, or made available as a general request header.
"""
from __future__ import annotations

from urllib.parse import urlsplit

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


def _is_allowed_request(url: str, host: str) -> bool:
    try:
        parts = urlsplit(url)
        return parts.scheme == "https" and parts.hostname == host and parts.netloc == host
    except ValueError:
        return False


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

    def origin_only(route):
        if _is_allowed_request(route.request.url, host):
            route.continue_()
        else:
            route.abort()

    # Install the browser-wide egress guard BEFORE handing over the cookie.
    context.route("**/*", origin_only)
    # Playwright `url` form, not a Domain attribute, keeps this host-only.
    context.add_cookies([{
        "url": "https://" + host + "/",
        "name": "_vercel_jwt",
        "value": cookie["value"],
        "secure": True,
        "httpOnly": True,
        "sameSite": cookie["sameSite"],
    }])
