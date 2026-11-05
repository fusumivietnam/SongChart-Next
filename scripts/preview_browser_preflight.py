#!/usr/bin/env python3
"""Fail-closed input checks for an opt-in protected Preview browser verifier.

This module never sends credentials, authenticates a browser, or claims that a
Vercel deployment's source revision was independently confirmed.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from urllib.parse import urlsplit

SHA = re.compile(r"[0-9a-f]{40}\Z")
DEPLOYMENT = re.compile(r"dpl_[A-Za-z0-9]+\Z")
HOST = re.compile(r"songchart-next-preview-[a-z0-9-]+-fusumivietnam\.vercel\.app\Z")


def validate(origin: str, expected_sha: str, deployment_id: str, *, secret_present: bool) -> str:
    """Return normalized origin only for an explicitly scoped, guarded Preview."""
    parsed = urlsplit(origin)
    if (parsed.scheme != "https" or parsed.username is not None or parsed.password is not None
            or parsed.port is not None or parsed.query or parsed.fragment
            or parsed.path not in ("", "/") or not parsed.hostname
            or not HOST.fullmatch(parsed.hostname) or parsed.netloc != parsed.hostname):
        raise ValueError("deployment_url must be an exact deployment-specific HTTPS origin")
    if not SHA.fullmatch(expected_sha):
        raise ValueError("expected_sha must be a lowercase full-length Git SHA")
    if not DEPLOYMENT.fullmatch(deployment_id):
        raise ValueError("deployment_id is missing or invalid")
    if not secret_present:
        raise ValueError("protected preview credential is not configured")
    return f"https://{parsed.hostname}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate protected Preview inputs before browser startup")
    parser.add_argument("--deployment-url", required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--deployment-id", required=True)
    args = parser.parse_args()
    try:
        validate(args.deployment_url, args.expected_sha, args.deployment_id,
                 secret_present=bool(os.environ.get("VERCEL_AUTOMATION_BYPASS_SECRET")))
    except (ValueError, OverflowError) as error:
        print(f"PREVIEW PREFLIGHT BLOCKED: {error}", file=sys.stderr)
        return 2
    print("PREVIEW PREFLIGHT PASS: inputs and credential presence validated; provider provenance and browser UX NOT verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
