#!/usr/bin/env python3
"""Verify GitHub Actions ownership, evidence and credential boundaries."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

EXPECTED = {
    "codespaces-contract.yml",
    "design-review-contract.yml",
    "foundation-app.yml",
    "foundation-visual.yml",
    "project-governance.yml",
    "project-os.yml",
    "project-projection-sync.yml",
    "roadmap-health.yml",
    "roadmap-reconcile.yml",
    "vs01a-artist.yml",
    "vs01b-musicbrainz.yml",
    "vs02-release-recording.yml",
    "vs03-discovery-search.yml",
    "work-management-sync.yml",
}
RETIRED = {"docker-scaffold.yml"}
PR_MAIN_EVIDENCE = {
    "codespaces-contract.yml",
    "design-review-contract.yml",
    "foundation-app.yml",
    "foundation-visual.yml",
    "project-governance.yml",
    "project-os.yml",
    "vs01a-artist.yml",
    "vs01b-musicbrainz.yml",
    "vs02-release-recording.yml",
    "vs03-discovery-search.yml",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    present = {path.name for path in WORKFLOWS.glob("*.y*ml")}

    missing = sorted(EXPECTED - present)
    unexpected = sorted(present - EXPECTED)
    retired = sorted(RETIRED & present)
    if missing:
        fail(errors, "missing owned workflows: " + ", ".join(missing))
    if unexpected:
        fail(errors, "workflow exists without ownership entry: " + ", ".join(unexpected))
    if retired:
        fail(errors, "retired workflows still present: " + ", ".join(retired))

    contents = {
        name: (WORKFLOWS / name).read_text(encoding="utf-8")
        for name in EXPECTED
        if (WORKFLOWS / name).exists()
    }

    verify_owners = sorted(
        name for name, content in contents.items()
        if "scripts/verify_project_os.py" in content
    )
    if verify_owners != ["project-os.yml"]:
        fail(
            errors,
            "scripts/verify_project_os.py must be owned only by project-os.yml; "
            f"found {verify_owners}",
        )

    for name, content in contents.items():
        runners = re.findall(r"^\s*runs-on:\s*(\S+)\s*$", content, flags=re.MULTILINE)
        if not runners:
            fail(errors, f"{name}: no runs-on declaration")
        elif any(runner != "ubuntu-24.04" for runner in runners):
            fail(errors, f"{name}: runners must be ubuntu-24.04; found {runners}")

        if "timeout-minutes:" not in content:
            fail(errors, f"{name}: job timeout is required")

        for line in content.splitlines():
            match = re.search(r"\buses:\s*([^\s#]+)", line)
            if not match:
                continue
            ref = match.group(1)
            if ref.startswith("./"):
                continue
            if "@" not in ref:
                fail(errors, f"{name}: action is not pinned: {ref}")
                continue
            action, version = ref.rsplit("@", 1)
            if not re.fullmatch(r"[0-9a-f]{40}", version):
                fail(errors, f"{name}: {action} must use a full 40-char commit SHA")

    for name in PR_MAIN_EVIDENCE:
        content = contents.get(name, "")
        for required in (
            "pull_request:",
            "push:",
            "github.event.pull_request.head.sha || github.sha",
            "ref: ${{ env.EVIDENCE_SHA }}",
            "github.event.pull_request.number || github.sha",
        ):
            if required not in content:
                fail(errors, f"{name}: missing exact-SHA/concurrency control: {required}")

    roadmap = contents.get("roadmap-health.yml", "")
    if "roadmap-health-${{ github.event_name }}-" not in roadmap:
        fail(errors, "roadmap-health.yml: concurrency must isolate event families")
    if "github.event.pull_request.number || github.event.issue.number || github.sha" not in roadmap:
        fail(errors, "roadmap-health.yml: concurrency must isolate PR/Issue/main identities")
    if "github.event.pull_request.head.sha || github.sha" not in roadmap:
        fail(errors, "roadmap-health.yml: exact event SHA expression missing")
    if "ref: ${{ env.EVIDENCE_SHA }}" not in roadmap:
        fail(errors, "roadmap-health.yml: checkout must use EVIDENCE_SHA")
    if "push:\n    branches: [main]\n    paths:" in roadmap:
        fail(errors, "roadmap-health.yml: main push must not be path-filtered")
    if "scripts/roadmap_reconcile_health.py" not in roadmap:
        fail(errors, "roadmap-health.yml: reconciliation drift detector missing")

    reconcile = contents.get("roadmap-reconcile.yml", "")
    for required in (
        "types: [closed]",
        "workflow_dispatch:",
        "contents: write",
        "pull-requests: write",
        "actions: write",
        "cancel-in-progress: false",
        "ref: main",
        "scripts/roadmap_reconcile.py",
        "project-governance.yml",
        "project-os.yml",
        "roadmap-health.yml",
        "git push --force-with-lease",
        "project-projection-sync.yml",
    ):
        if required not in reconcile:
            fail(errors, f"roadmap-reconcile.yml: missing safe-writer control: {required}")
    if "PROJECT_SYNC_TOKEN" in reconcile:
        fail(errors, "roadmap-reconcile.yml must never receive PROJECT_SYNC_TOKEN")

    projection = contents.get("project-projection-sync.yml", "")
    for required in (
        "pull_request_target:",
        "ref: main",
        "PROJECT_SYNC_TOKEN: ${{ secrets.PROJECT_SYNC_TOKEN }}",
        "cancel-in-progress: false",
    ):
        if required not in projection:
            fail(errors, f"project-projection-sync.yml: missing trusted-writer control: {required}")
    if "issues: write" in projection:
        fail(errors, "project-projection-sync.yml: repository Issues permission must stay read-only")

    work = contents.get("work-management-sync.yml", "")
    if "issues: write" not in work:
        fail(errors, "work-management-sync.yml: issues: write is required")
    if "PROJECT_SYNC_TOKEN" in work:
        fail(errors, "work-management-sync.yml must never receive PROJECT_SYNC_TOKEN")
    if "cancel-in-progress: false" not in work:
        fail(errors, "work-management-sync.yml: mutating reconciliation must be serialized")

    token_owners = sorted(
        name for name, content in contents.items()
        if "PROJECT_SYNC_TOKEN" in content
    )
    if token_owners != ["project-projection-sync.yml"]:
        fail(errors, f"PROJECT_SYNC_TOKEN must have one workflow owner; found {token_owners}")

    for name, job in (
        ("project-governance.yml", "governance:"),
        ("project-os.yml", "verify:"),
        ("roadmap-health.yml", "health:"),
    ):
        if job not in contents.get(name, ""):
            fail(errors, f"{name}: required branch-protection job {job[:-1]} missing")

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
