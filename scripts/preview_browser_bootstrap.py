"""Opt-in HTTPS cookie bootstrap for a reviewed protected Preview target.

Caller must first independently verify Vercel deployment provenance.
Does not write cookies or secrets to logs/disk; no automatic redirects.
"""
from __future__ import annotations

import urllib.error
import urllib.request

from preview_browser_cookie import verify_cookie
from preview_browser_preflight import validate
from preview_browser_provenance import ApiLookupFailed, fetch_verified_deployment


class PreflightBlocked(ValueError):
    """Safe diagnostic category only; never include credential-bearing details."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class RejectRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def bootstrap(origin: str, deployment_id: str, expected_sha: str, secret: str,
              *, api_token: str, team_id: str, opener=None, control_plane_opener=None) -> dict[str, object]:
    """Return a host-scoped browser cookie in memory; never log the returned object."""
    try:
        normalized = validate(origin, expected_sha, deployment_id, secret_present=bool(secret))
    except ValueError:
        raise PreflightBlocked("INPUT_INVALID") from None
    # Must verify authenticated control-plane provenance before secret-bearing GET.
    try:
        fetch_verified_deployment(normalized, deployment_id, expected_sha,
                                  api_token=api_token, team_id=team_id,
                                  opener=control_plane_opener)
    except ApiLookupFailed:
        raise PreflightBlocked("API_LOOKUP_FAILED") from None
    except ValueError:
        raise PreflightBlocked("PROVENANCE_REJECTED") from None
    # Deliberately no cookie jar, proxy credentials or browser-wide authorization.
    transport = opener if opener is not None else urllib.request.build_opener(RejectRedirect())
    request = urllib.request.Request(
        normalized + "/",
        headers={"x-vercel-protection-bypass": secret,
                 "x-vercel-set-bypass-cookie": "true",
                 "User-Agent": "SongChart-Preview-UX/1"},
        method="GET",
    )
    try:
        with transport.open(request, timeout=15) as response:
            status = response.status
            final_url = response.geturl()
            headers = response.headers.get_all("Set-Cookie", [])
            # Do not read or retain response bodies.
    except urllib.error.HTTPError:
        raise PreflightBlocked("BYPASS_REJECTED") from None
    except (urllib.error.URLError, TimeoutError):
        raise PreflightBlocked("BYPASS_UNAVAILABLE") from None
    try:
        return verify_cookie(normalized, final_url, status, headers)
    except ValueError:
        raise PreflightBlocked("COOKIE_INVALID") from None
