#!/usr/bin/env python3
"""Reconcile GitHub repository work-management projections.

Only declared labels and explicitly managed milestones are created/updated.
Unmanaged repository metadata is never deleted. Uses the ephemeral repository
GITHUB_TOKEN; PROJECT_SYNC_TOKEN must not be supplied to this process.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "governance" / "GITHUB_WORK_MANAGEMENT.json"


def load_contract():
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or data.get("project") != "SongChart-Next":
        raise RuntimeError("invalid GitHub work-management contract")
    return data


def request_json(token, method, url, payload=None):
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "songchart-work-management-sync",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"GitHub API {method} {url} failed: HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"GitHub API {method} {url} failed: {type(exc).__name__}") from exc


def paged(token, url):
    page = 1
    result = []
    separator = "&" if "?" in url else "?"
    while True:
        batch = request_json(token, "GET", f"{url}{separator}per_page=100&page={page}") or []
        result.extend(batch)
        if len(batch) < 100:
            return result
        page += 1


def desired_labels(contract):
    return {
        item["name"]: {
            "name": item["name"],
            "description": item["description"],
            "color": item["color"].lower(),
        }
        for item in contract["issue_labels"]["required"]
    }


def desired_milestones(contract):
    desired = {}
    for item in contract["milestones"].get("managed", []):
        title = item["title"]
        desired[title] = {
            "title": title,
            "description": item.get("description") or "",
            "state": item.get("state", "open"),
            "due_on": item.get("due_on"),
        }
    return desired


def label_changes(current, desired):
    by_name = {item["name"]: item for item in current}
    changes = []
    for name, wanted in desired.items():
        have = by_name.get(name)
        if not have:
            changes.append(("create", name, wanted))
            continue
        patch = {}
        if (have.get("description") or "") != wanted["description"]:
            patch["description"] = wanted["description"]
        if (have.get("color") or "").lower() != wanted["color"]:
            patch["color"] = wanted["color"]
        if patch:
            changes.append(("update", name, patch))
    return changes


def milestone_changes(current, desired):
    by_title = {item["title"]: item for item in current}
    changes = []
    for title, wanted in desired.items():
        have = by_title.get(title)
        if not have:
            changes.append(("create", title, wanted))
            continue
        patch = {}
        for key in ("description", "state", "due_on"):
            have_value = have.get(key)
            wanted_value = wanted.get(key)
            if key == "description":
                have_value = have_value or ""
            if have_value != wanted_value:
                patch[key] = wanted_value
        if patch:
            changes.append(("update", title, {"number": have["number"], **patch}))
    return changes


def reconcile(token, repo, dry_run=False):
    contract = load_contract()
    base = f"https://api.github.com/repos/{repo}"
    current_labels = paged(token, f"{base}/labels")
    current_milestones = paged(token, f"{base}/milestones?state=all")
    label_plan = label_changes(current_labels, desired_labels(contract))
    milestone_plan = milestone_changes(current_milestones, desired_milestones(contract))

    applied = []
    if not dry_run:
        for action, name, payload in label_plan:
            if action == "create":
                request_json(token, "POST", f"{base}/labels", payload)
            else:
                encoded = urllib.parse.quote(name, safe="")
                request_json(token, "PATCH", f"{base}/labels/{encoded}", payload)
            applied.append(f"label {action}: {name}")
        for action, title, payload in milestone_plan:
            if action == "create":
                request_json(token, "POST", f"{base}/milestones", payload)
            else:
                number = payload.pop("number")
                request_json(token, "PATCH", f"{base}/milestones/{number}", payload)
            applied.append(f"milestone {action}: {title}")

    return {
        "repository": repo,
        "dry_run": dry_run,
        "desired_labels": len(desired_labels(contract)),
        "managed_milestones": len(desired_milestones(contract)),
        "label_changes": [f"{action}: {name}" for action, name, _ in label_plan],
        "milestone_changes": [f"{action}: {title}" for action, title, _ in milestone_plan],
        "applied": applied,
        "delete_unmanaged": False,
        "authority": "governance/GITHUB_WORK_MANAGEMENT.json",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "fusumivietnam/SongChart-Next"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-json")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN is required.", file=sys.stderr)
        return 2
    try:
        report = reconcile(token, args.repo, args.dry_run)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.output_json:
        Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
