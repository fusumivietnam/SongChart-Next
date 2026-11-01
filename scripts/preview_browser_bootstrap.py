"""Opt-in HTTPS cookie bootstrap for a reviewed protected Preview target.

Caller must first independently verify Vercel deployment provenance.
Does not write cookies or secrets to logs/disk; no automatic redirects.
"""
from __future__ import annotations

import urllib.error
import urllib.request

from preview_browser_cookie import verify_cookie
from preview_browser_preflight import validate
from preview_browser_provenance import fetch_verified_deployment


class RejectRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def bootstrap(origin: str, deployment_id: str, expected_sha: str, secret: str,
              *, api_token: str, team_id: str, opener=None, control_plane_opener=None) -> dict[str, object]:
    """Return a host-scoped browser cookie in memory; never log the returned object."""
    normalized = validate(origin, expected_sha, deployment_id, secret_present=bool(secret))
    # Must verify authenticated control-plane provenance before secret-bearing GET.
    fetch_verified_deployment(normalized, deployment_id, expected_sha,
                              api_token=api_token, team_id=team_id,
                              opener=control_plane_opener)
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
        raise ValueError("bypass bootstrap rejected by deployment") from None
    except (urllib.error.URLError, TimeoutError):
        raise ValueError("bypass bootstrap connection failed") from None
    return verify_cookie(normalized, final_url, status, headers)
