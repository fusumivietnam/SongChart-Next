"""Verify a Vercel control-plane deployment response against operator inputs.

Pure comparison only: the caller must obtain this record from the authenticated
Vercel API, not from deployment HTML or an operator-supplied JSON file.
"""
from __future__ import annotations

from urllib.parse import urlsplit
from typing import Any


def verify_deployment(record: dict[str, Any], *, origin: str, deployment_id: str,
                      expected_sha: str) -> None:
    deployment = record.get("deployment", record)
    if not isinstance(deployment, dict):
        raise ValueError("invalid Vercel deployment record")
    meta = deployment.get("meta")
    project = deployment.get("project")
    if not isinstance(meta, dict) or not isinstance(project, dict):
        raise ValueError("deployment provenance missing")
    host = urlsplit(origin).hostname
    if (deployment.get("id") != deployment_id
            or deployment.get("url") != host
            or deployment.get("target") is not None
            or deployment.get("readyState") != "READY"
            or project.get("id") != "prj_JTUUiO0Hb3QwiK7w6NWmvxwej43E"
            or meta.get("githubCommitSha") != expected_sha
            or meta.get("githubRepo") != "SongChart-Next"
            or meta.get("githubOrg") != "fusumivietnam"):
        raise ValueError("deployment source, environment, project or host mismatch")



def fetch_verified_deployment(origin: str, deployment_id: str, expected_sha: str,
                              *, api_token: str, team_id: str,
                              opener=None) -> dict[str, Any]:
    """Retrieve and verify provenance from the authenticated Vercel HTTPS API.

    Caller must supply a separately authorized read-scoped API token. Never
    accept a caller-provided deployment JSON as an authenticity substitute.
    """
    import json
    import urllib.error
    import urllib.request
    from urllib.parse import quote
    if not api_token or not team_id or not deployment_id.startswith("dpl_"):
        raise ValueError("authenticated Vercel API access is required")
    if not all(char.isalnum() or char in "_-" for char in deployment_id + team_id):
        raise ValueError("invalid Vercel control-plane identifier")
    api_url = (
        "https://api.vercel.com/v13/deployments/"
        + quote(deployment_id, safe="")
        + "?teamId=" + quote(team_id, safe="")
    )

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    transport = opener or urllib.request.build_opener(NoRedirect())
    request = urllib.request.Request(
        api_url,
        headers={"Authorization": "Bearer " + api_token,
                 "Accept": "application/json"},
    )
    try:
        with transport.open(request, timeout=15) as response:
            if response.status != 200 or response.geturl() != api_url:
                raise ValueError("Vercel API response origin/status mismatch")
            if not response.headers.get("Content-Type", "").lower().startswith("application/json"):
                raise ValueError("Vercel API response is not JSON")
            raw = response.read(1048577)
            if len(raw) > 1048576:
                raise ValueError("Vercel deployment response exceeds limit")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        raise ValueError("authenticated Vercel API lookup failed") from None
    try:
        deployment = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise ValueError("Vercel API returned invalid JSON") from None
    if not isinstance(deployment, dict):
        raise ValueError("invalid Vercel API response")
    verify_deployment(deployment, origin=origin,
                      deployment_id=deployment_id, expected_sha=expected_sha)
    return deployment
