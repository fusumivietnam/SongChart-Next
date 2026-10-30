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
