#!/usr/bin/env python3
"""Verify GitHub Actions ownership, evidence and credential boundaries."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
EXPECTED = {
    "codespaces-contract.yml", "design-review-contract.yml", "foundation-app.yml",
    "foundation-visual.yml", "project-governance.yml", "project-os.yml",
    "project-projection-sync.yml", "roadmap-health.yml", "roadmap-reconcile.yml",
    "vs01a-artist.yml", "vs01b-musicbrainz.yml", "vs02-release-recording.yml",
    "vs03-discovery-search.yml", "work-management-sync.yml",
}
RETIRED = {"docker-scaffold.yml"}
PR_MAIN_EVIDENCE = {
    "codespaces-contract.yml", "design-review-contract.yml", "foundation-app.yml",
    "foundation-visual.yml", "project-governance.yml", "project-os.yml",
    "vs01a-artist.yml", "vs01b-musicbrainz.yml", "vs02-release-recording.yml",
    "vs03-discovery-search.yml",
}


def main() -> int:
    errors: list[str] = []
    present = {p.name for p in WORKFLOWS.glob("*.y*ml")}
    for label, values in (("missing owned workflows", EXPECTED - present), ("workflow exists without ownership entry", present - EXPECTED), ("retired workflows still present", RETIRED & present)):
        if values:
            errors.append(f"{label}: {', '.join(sorted(values))}")
    contents = {name: (WORKFLOWS / name).read_text(encoding="utf-8") for name in EXPECTED if (WORKFLOWS / name).exists()}

    owners = sorted(name for name, c in contents.items() if "scripts/verify_project_os.py" in c)
    if owners != ["project-os.yml"]:
        errors.append(f"scripts/verify_project_os.py must be owned only by project-os.yml; found {owners}")

    for name, content in contents.items():
        runners = re.findall(r"^\s*runs-on:\s*(\S+)\s*$", content, flags=re.MULTILINE)
        if not runners or any(r != "ubuntu-24.04" for r in runners):
            errors.append(f"{name}: runners must be ubuntu-24.04; found {runners}")
        if "timeout-minutes:" not in content:
            errors.append(f"{name}: job timeout is required")
        for line in content.splitlines():
            m = re.search(r"\buses:\s*([^\s#]+)", line)
            if not m or m.group(1).startswith("./"):
                continue
            ref = m.group(1)
            if "@" not in ref or not re.fullmatch(r"[0-9a-f]{40}", ref.rsplit("@", 1)[1]):
                errors.append(f"{name}: external action must use a full 40-char commit SHA: {ref}")

    for name in PR_MAIN_EVIDENCE:
        content = contents.get(name, "")
        for required in ("pull_request:", "push:", "github.event.pull_request.head.sha || github.sha", "ref: ${{ env.EVIDENCE_SHA }}", "github.event.pull_request.number || github.sha"):
            if required not in content:
                errors.append(f"{name}: missing exact-SHA/concurrency control: {required}")

    roadmap = contents.get("roadmap-health.yml", "")
    for required in ("roadmap-health-${{ github.event_name }}-", "github.event.pull_request.number || github.event.issue.number || github.sha", "scripts/roadmap_reconcile_health.py"):
        if required not in roadmap:
            errors.append(f"roadmap-health.yml: missing control: {required}")
    if "push:\n    branches: [main]\n    paths:" in roadmap:
        errors.append("roadmap-health.yml: main push must not be path-filtered")

    reconcile = contents.get("roadmap-reconcile.yml", "")
    for required in (
        "types: [closed, edited]", "issue_comment:", "github.event.comment.body == '/roadmap-reconcile'",
        "workflow_dispatch:", "contents: read", "pull-requests: read", "actions: write",
        "secrets.ROADMAP_RECONCILE_TOKEN", "Do not reuse PROJECT_SYNC_TOKEN", "git push --force-with-lease",
        "any(.pull_requests[]?; .number == $pr)", "source-runs.json", ".created_at <= $merged_at",
        "project-projection-sync.yml",
    ):
        if required not in reconcile:
            errors.append(f"roadmap-reconcile.yml: missing safe-writer control: {required}")
    if "contents: write" in reconcile or "pull-requests: write" in reconcile:
        errors.append("roadmap-reconcile.yml: default GITHUB_TOKEN must remain read-only for repository/PR mutation")
    if "PROJECT_SYNC_TOKEN" in reconcile and "Do not reuse PROJECT_SYNC_TOKEN" not in reconcile:
        errors.append("roadmap-reconcile.yml must not consume PROJECT_SYNC_TOKEN")

    projection = contents.get("project-projection-sync.yml", "")
    for required in ("pull_request_target:", "ref: main", "PROJECT_SYNC_TOKEN: ${{ secrets.PROJECT_SYNC_TOKEN }}", "cancel-in-progress: false"):
        if required not in projection:
            errors.append(f"project-projection-sync.yml: missing trusted-writer control: {required}")
    work = contents.get("work-management-sync.yml", "")
    if "issues: write" not in work or "cancel-in-progress: false" not in work:
        errors.append("work-management-sync.yml: serialized issues write contract missing")

    project_token_owners = sorted(name for name, c in contents.items() if "PROJECT_SYNC_TOKEN: ${{ secrets.PROJECT_SYNC_TOKEN }}" in c)
    if project_token_owners != ["project-projection-sync.yml"]:
        errors.append(f"PROJECT_SYNC_TOKEN must have one workflow owner; found {project_token_owners}")
    reconcile_token_owners = sorted(name for name, c in contents.items() if "secrets.ROADMAP_RECONCILE_TOKEN" in c)
    if reconcile_token_owners != ["roadmap-reconcile.yml"]:
        errors.append(f"ROADMAP_RECONCILE_TOKEN must have one workflow owner; found {reconcile_token_owners}")

    for name, job in (("project-governance.yml", "governance:"), ("project-os.yml", "verify:"), ("roadmap-health.yml", "health:")):
        if job not in contents.get(name, ""):
            errors.append(f"{name}: required branch-protection job {job[:-1]} missing")

    if errors:
        print("CI ownership verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("CI ownership verification passed.")
    for name in sorted(EXPECTED):
        print(f"- {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
