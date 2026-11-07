#!/usr/bin/env python3
"""Verify GitHub Actions ownership, evidence and credential boundaries."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
EXPECTED = {
    "agent-browser-pilot.yml", "archify-browser-contract.yml", "codespaces-contract.yml", "design-review-contract.yml", "foundation-app.yml",
    "foundation-visual.yml", "g5-vps-baseline.yml", "project-governance.yml", "project-os.yml",
    "project-projection-sync.yml", "research-cocoindex.yml", "roadmap-health.yml", "roadmap-reconcile.yml",
    "protected-preview-smoke.yml", "protected-preview-browser-preflight.yml",
    "vs01a-artist.yml", "vs01b-musicbrainz.yml", "vs02-release-recording.yml",
    "vs03-discovery-search.yml", "vs04-launch-proof.yml", "work-management-sync.yml",
}
RETIRED = {"docker-scaffold.yml"}
LEGACY_CHECKOUT_SHA = "11bd71901bbe5b1630ceea73d27597364c9af683"
NODE24_CHECKOUT_SHAS = {"df4cb1c069e1874edd31b4311f1884172cec0e10", "08c6903cd8c0fde910a37f88322edcfb5dd907a8"}
NODE24_UPLOAD_ARTIFACT_SHA = "b7c566a772e6b6bfb58ed0dc250532a479d7789f"  # v6.0.0
PR_MAIN_EVIDENCE = {
    "codespaces-contract.yml", "design-review-contract.yml", "foundation-app.yml",
    "foundation-visual.yml", "g5-vps-baseline.yml", "project-governance.yml", "project-os.yml",
    "vs01a-artist.yml", "vs01b-musicbrainz.yml", "vs02-release-recording.yml",
    "vs03-discovery-search.yml", "vs04-launch-proof.yml",
}


def main() -> int:
    errors: list[str] = []
    present = {p.name for p in WORKFLOWS.glob("*.y*ml")}
    for label, values in (("missing owned workflows", EXPECTED - present), ("workflow exists without ownership entry", present - EXPECTED), ("retired workflows still present", RETIRED & present)):
        if values:
            errors.append(f"{label}: {', '.join(sorted(values))}")
    contents = {name: (WORKFLOWS / name).read_text(encoding="utf-8") for name in EXPECTED if (WORKFLOWS / name).exists()}

    for name, expected_owned_paths in {
        "codespaces-contract.yml": (".devcontainer/**", "scripts/codespaces_doctor.sh"),
        "vs01b-musicbrainz.yml": ("app/Music/Providers/**", "docs/providers/MUSICBRAINZ.md"),
    }.items():
        content = contents.get(name, "")
        if "governance/TECHNOLOGY_REGISTRY.json" in content:
            errors.append(f"{name}: cross-cutting registry metadata must not trigger unrelated heavy verification")
        for owned_path in expected_owned_paths:
            if owned_path not in content:
                errors.append(f"{name}: owned path trigger missing: {owned_path}")

    protected_browser = contents.get("protected-preview-browser-preflight.yml", "")
    for required in (
        "workflow_dispatch:", "environment: preview-test", "github.ref == 'refs/heads/main'",
        "timeout-minutes: 10", "contents: read", "persist-credentials: false",
        "secrets.VERCEL_API_READ_TOKEN", "secrets.VERCEL_AUTOMATION_BYPASS_SECRET",
        "vars.VERCEL_TEAM_ID", "from preview_browser_bootstrap import bootstrap",
        "NO browser UX executed",
    ):
        if required not in protected_browser:
            errors.append(f"protected-preview-browser-preflight.yml: missing guarded preflight control: {required}")
    for forbidden in ("pull_request:", "push:", "upload-artifact", "contents: write", "set-bypass-cookie: samesitenone"):
        if forbidden in protected_browser:
            errors.append(f"protected-preview-browser-preflight.yml: disallowed auto-trigger/artifact/permission: {forbidden}")

    owners = sorted(name for name, c in contents.items() if "scripts/verify_project_os.py" in c)
    if owners != ["project-os.yml"]:
        errors.append(f"scripts/verify_project_os.py must be owned only by project-os.yml; found {owners}")

    pilot = contents.get("agent-browser-pilot.yml", "")
    for required in ("pull_request:", "workflow_dispatch:", "contents: read", "timeout-minutes: 10", "persist-credentials: false", "AGENT_BROWSER_EXECUTABLE_PATH", "127.0.0.1:8765", "agent-browser@0.41.1"):
        if required not in pilot:
            errors.append(f"agent-browser-pilot.yml: missing no-secret local browser control: {required}")
    for forbidden in ("secrets.", "environment: preview-test", "push:", "upload-artifact", "docker build"):
        if forbidden in pilot:
            errors.append(f"agent-browser-pilot.yml: forbidden credential, main-push, or artifact scope: {forbidden}")

    classifier = ROOT / "scripts" / "classify_ci_change.py"
    classifier_test = ROOT / "tests" / "governance" / "test_ci_change_classifier.py"
    if not classifier.is_file() or not classifier_test.is_file():
        errors.append("deterministic CI impact classifier and governance test are required")

    for name, content in contents.items():
        for upload_sha in re.findall(r"actions/upload-artifact@([0-9a-f]{40})", content):
            if upload_sha != NODE24_UPLOAD_ARTIFACT_SHA:
                errors.append(f"{name}: upload-artifact must use pinned Node.js 24 v6.0.0")
        if LEGACY_CHECKOUT_SHA in content:
            errors.append(f"{name}: legacy Node.js 20 checkout action is forbidden")
        for checkout_sha in re.findall(r"actions/checkout@([0-9a-f]{40})", content):
            if checkout_sha not in NODE24_CHECKOUT_SHAS:
                errors.append(f"{name}: checkout SHA must be approved Node.js 24 pin: {checkout_sha}")
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
        "types: [closed]", "workflow_dispatch:", "contents: read", "pull-requests: read", "actions: write",
        "persist-credentials: false", "secrets.ROADMAP_RECONCILE_TOKEN", "Do not reuse PROJECT_SYNC_TOKEN",
        "git push --force-with-lease", "any(.pull_requests[]?; .number == $pr)", "source-runs.json",
        ".created_at <= $merged_at", "project-projection-sync.yml", "Source PR: #${SOURCE_PR}",
    ):
        if required not in reconcile:
            errors.append(f"roadmap-reconcile.yml: missing safe-writer control: {required}")
    for forbidden in ("types: [closed, edited]", "issue_comment:", "github.event.comment.body"):
        if forbidden in reconcile:
            errors.append(f"roadmap-reconcile.yml: no-op trigger amplification must remain removed: {forbidden}")
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

    g5 = contents.get("g5-vps-baseline.yml", "")
    for required in ("compose.production.yaml", "--target production", "--target production-web", "scripts/production/smoke.sh", "Verify private service exposure"):
        if required not in g5:
            errors.append(f"g5-vps-baseline.yml: missing production-package control: {required}")
    if "secrets." in g5:
        errors.append("g5-vps-baseline.yml: disposable baseline verification must not consume repository production secrets")

    research = contents.get("research-cocoindex.yml", "")
    for required in ("workflow_dispatch:", "research/cocoindex/Dockerfile", "research/cocoindex/benchmark.py", "merge_blocking_semantic_judgement", "actions/upload-artifact@"):
        if required not in research:
            errors.append(f"research-cocoindex.yml: missing research boundary/control: {required}")
    if "secrets." in research:
        errors.append("research-cocoindex.yml: local research spike must not consume repository secrets")

    archify = contents.get("archify-browser-contract.yml", "")
    for required in ("workflow_dispatch:", "pull_request:", "fetch-depth: 0", "scripts/archify_example.sh", "browser-check", "ARCHIFY_UPDATE_CHECK_DISABLED"):
        if required not in archify:
            errors.append(f"archify-browser-contract.yml: missing disposable browser gate: {required}")
    if "secrets." in archify or "push:" in archify or "upload-artifact" in archify:
        errors.append("archify-browser-contract.yml: no secrets, main-push amplification or published HTML")

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
