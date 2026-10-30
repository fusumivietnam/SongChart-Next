"""Validate a Vercel browser-bypass cookie without revealing its value.

No HTTP request is issued by this module. Only a reviewed caller may decide
whether to transfer the returned secret cookie into a same-origin browser.
"""
from __future__ import annotations

from http.cookies import SimpleCookie
from urllib.parse import urlsplit

COOKIE_NAME = "_vercel_jwt"


def verify_cookie(origin: str, response_url: str, status: int, set_cookie_headers: list[str]) -> dict[str, object]:
    """Fail closed if the bootstrap response is off-origin or the cookie is unsafe."""
    expected = urlsplit(origin)
    actual = urlsplit(response_url)
    if expected.scheme != "https" or actual.scheme != "https" or actual.netloc != expected.netloc:
        raise ValueError("bypass response must remain on the exact HTTPS Preview origin")
    if expected.path not in ("", "/") or expected.query or expected.fragment:
        raise ValueError("bootstrap origin must not contain a path or query")
    if not (200 <= status < 400):
        raise ValueError("bypass bootstrap did not succeed")
    if len(set_cookie_headers) != 1:
        raise ValueError("expected one isolated bypass cookie header")
    cookie = SimpleCookie()
    try:
        cookie.load(set_cookie_headers[0])
    except Exception:
        raise ValueError("invalid bypass cookie") from None
    if set(cookie.keys()) != {COOKIE_NAME}:
        raise ValueError("unexpected bypass cookie")
    value = cookie[COOKIE_NAME]
    if (not value.value or value["domain"] or value["path"] not in ("", "/")
            or not value["secure"] or value["samesite"].lower() not in ("lax", "strict")
            or value["max-age"] and not value["max-age"].isdigit()):
        raise ValueError("bypass cookie must be secure, host-only and restricted")
    # The only secret-containing result is kept in memory, never logged.
    return {"name": COOKIE_NAME, "value": value.value, "domain": expected.hostname, "path": "/", "secure": True, "httpOnly": bool(value["httponly"]), "sameSite": value["samesite"].capitalize()}
