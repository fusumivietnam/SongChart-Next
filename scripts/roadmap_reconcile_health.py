#!/usr/bin/env python3
"""Read-only checks for post-merge roadmap reconciliation drift."""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METADATA_RE = re.compile(r"<!--\s*songchart-reconcile\s*(\{.*?\})\s*-->", re.I | re.S)


def parse_metadata(body):
    match = METADATA_RE.search(body or "")
    if not match:
        return None
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError:
        return {"invalid": True}
    return value if isinstance(value, dict) else {"invalid": True}


def api_get(repo, path, token):
    url = f"https://api.github.com/repos/{repo}{path}"
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "songchart-roadmap-reconcile-health",
    })
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def fetch_merged_prs(repo, token):
    if not token:
        return {"status": "unknown", "reason": "no GitHub token supplied", "pull_requests": []}
    try:
        pulls = api_get(repo, "/pulls?state=closed&per_page=100&sort=updated&direction=desc", token)
        return {"status": "known", "truncated": len(pulls) == 100, "pull_requests": pulls}
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        return {"status": "unknown", "reason": f"GitHub query failed: {type(exc).__name__}", "pull_requests": []}


def authority_mentions_pr(root, number):
    root = Path(root)
    cmap = (root / "governance/CAPABILITY_MAP.json").read_text(encoding="utf-8")
    roadmap = (root / "docs/roadmap/VERTICAL_SLICES.md").read_text(encoding="utf-8")
    readme = (root / "README.md").read_text(encoding="utf-8")
    if re.search(rf'"pr"\s*:\s*{int(number)}\b', cmap):
        return True
    marker = f"reconciliation:pr-{int(number)}"
    return marker in roadmap or f"PR #{int(number)}" in readme


def derive(root, live):
    findings = []
    if live["status"] == "unknown":
        findings.append({"code": "reconcile.live_unknown", "severity": "warning", "message": live.get("reason", "live GitHub unavailable")})
    else:
        if live.get("truncated"):
            findings.append({"code": "reconcile.live_truncated", "severity": "warning", "message": "Closed PR query reached 100 items."})
        for pr in live["pull_requests"]:
            if not pr.get("merged_at"):
                continue
            meta = parse_metadata(pr.get("body") or "")
            if not meta:
                continue
            if meta.get("invalid"):
                findings.append({"code": "merged_pr.invalid_reconcile_metadata", "severity": "error", "message": f"Merged PR #{pr['number']} has invalid reconciliation metadata.", "pr": pr["number"]})
                continue
            if meta.get("skip") is True or not meta.get("reconcile"):
                continue
            if not authority_mentions_pr(root, pr["number"]):
                findings.append({"code": "merged_pr.unreconciled", "severity": "warning", "message": f"Merged PR #{pr['number']} declares authority reconciliation but is not referenced by reconciled authorities.", "pr": pr["number"]})
    counts = {severity: sum(1 for item in findings if item["severity"] == severity) for severity in ("error", "warning", "info")}
    return {"schema_version": 1, "live_github": {k: v for k, v in live.items() if k != "pull_requests"}, "findings": findings, "summary": counts}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "fusumivietnam/SongChart-Next"))
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    parser.add_argument("--root", default=".")
    parser.add_argument("--live-github", action="store_true")
    parser.add_argument("--output-json")
    parser.add_argument("--fail-on-error", action="store_true")
    args = parser.parse_args()
    live = fetch_merged_prs(args.repo, args.token) if args.live_github else {"status": "unknown", "reason": "offline mode", "pull_requests": []}
    report = derive(args.root, live)
    for item in report["findings"]:
        print(f"[{item['severity'].upper()}] {item['code']}: {item['message']}")
    if not report["findings"]:
        print("Roadmap reconciliation health: no findings.")
    if args.output_json:
        Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 2 if args.fail_on_error and report["summary"]["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
