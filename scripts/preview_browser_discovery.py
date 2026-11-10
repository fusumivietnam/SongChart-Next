"""Bounded, read-only discovery of the most recent verified READY Preview.

The Vercel project ID and repository identity are repository-owned policy.
Discovery never logs a token, deployment URL, or credential-bearing response.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from urllib.parse import quote

from preview_browser_preflight import DEPLOYMENT, HOST, SHA
from preview_browser_provenance import fetch_verified_deployment

PROJECT_ID = "prj_JTUUiO0Hb3QwiK7w6NWmvxwej43E"
MAX_AGE_MS = 30 * 24 * 60 * 60 * 1000


class DiscoveryBlocked(ValueError):
    """No control-plane detail or deployment metadata is disclosed."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def choose_ready_preview(records: object, *, now_ms: int) -> tuple[str, str, str]:
    """Pick a unique newest matching READY preview, or reject ambiguity."""
    if not isinstance(records, list) or len(records) > 20:
        raise DiscoveryBlocked("PREVIEW_LIST_INVALID")
    candidates = []
    for item in records:
        if not isinstance(item, dict) or not isinstance(item.get("meta"), dict):
            continue
        meta = item["meta"]
        deployment_id, host, sha = item.get("uid", item.get("id")), item.get("url"), meta.get("githubCommitSha")
        created = item.get("created")
        if (item.get("readyState") != "READY" or item.get("target") is not None
                or not isinstance(deployment_id, str) or not DEPLOYMENT.fullmatch(deployment_id)
                or not isinstance(host, str) or not HOST.fullmatch(host)
                or not isinstance(sha, str) or not SHA.fullmatch(sha)
                or meta.get("githubRepo") != "SongChart-Next" or meta.get("githubOrg") != "fusumivietnam"
                or not isinstance(created, int) or isinstance(created, bool)
                or not (0 <= now_ms - created <= MAX_AGE_MS)):
            continue
        candidates.append((created, deployment_id, host, sha))
    if not candidates:
        raise DiscoveryBlocked("NO_MATCHING_READY_PREVIEW")
    candidates.sort(reverse=True)
    if len(candidates) > 1 and candidates[0][0] == candidates[1][0]:
        raise DiscoveryBlocked("AMBIGUOUS_NEWEST_PREVIEW")
    _, deployment_id, host, sha = candidates[0]
    return "https://" + host, deployment_id, sha


def discover(*, api_token: str, team_id: str, opener=None,
             now_ms: int | None = None) -> tuple[str, str, str]:
    if not api_token or not re.fullmatch(r"team_[A-Za-z0-9]+", team_id):
        raise DiscoveryBlocked("CONFIG_MISSING")
    url = ("https://api.vercel.com/v6/deployments?projectId=" + quote(PROJECT_ID)
           + "&teamId=" + quote(team_id) + "&limit=20")
    transport = opener or urllib.request.build_opener(NoRedirect())
    request = urllib.request.Request(url, headers={"Authorization": "Bearer " + api_token,
                                                  "Accept": "application/json"})
    try:
        with transport.open(request, timeout=15) as response:
            if (response.status != 200 or response.geturl() != url
                    or response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json"):
                raise DiscoveryBlocked("API_RESPONSE_REJECTED")
            raw = response.read(1048577)
            if len(raw) > 1048576:
                raise DiscoveryBlocked("API_RESPONSE_TOO_LARGE")
        data = json.loads(raw)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, UnicodeError):
        raise DiscoveryBlocked("API_LOOKUP_FAILED") from None
    if not isinstance(data, dict):
        raise DiscoveryBlocked("API_RESPONSE_REJECTED")
    origin, deployment_id, sha = choose_ready_preview(
        data.get("deployments"), now_ms=now_ms if now_ms is not None else int(time.time() * 1000))
    # Re-fetch exact deployment from the authenticated control plane and apply
    # the existing full project/repository/source/READY provenance policy.
    try:
        fetch_verified_deployment(origin, deployment_id, sha,
                                  api_token=api_token, team_id=team_id,
                                  opener=opener)
    except (ValueError, urllib.error.URLError):
        raise DiscoveryBlocked("PROVENANCE_REJECTED") from None
    return origin, deployment_id, sha
