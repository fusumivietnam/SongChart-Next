#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

EXPECTED = {
    "codespaces-contract.yml",
    "foundation-app.yml",
    "foundation-visual.yml",
    "project-governance.yml",
    "roadmap-health.yml",
}
RETIRED = {"project-os.yml", "docker-scaffold.yml"}

errors: list[str] = []

present = {path.name for path in WORKFLOWS.glob("*.yml")}
missing = sorted(EXPECTED - present)
unexpected_retired = sorted(RETIRED & present)

if missing:
    errors.append(f"missing owned workflows: {', '.join(missing)}")
if unexpected_retired:
    errors.append(f"retired workflows still present: {', '.join(unexpected_retired)}")

contents = {
    name: (WORKFLOWS / name).read_text(encoding="utf-8")
    for name in EXPECTED
    if (WORKFLOWS / name).exists()
}

governance_owners = [
    name for name, content in contents.items()
    if "scripts/verify_project_os.py" in content
]
if governance_owners != ["project-governance.yml"]:
    errors.append(
        "scripts/verify_project_os.py must be owned only by project-governance.yml "
        f"inside GitHub Actions; found: {governance_owners}"
    )

for name, content in contents.items():
    runners = re.findall(r"^\s*runs-on:\s*(\S+)\s*$", content, flags=re.MULTILINE)
    if not runners:
        errors.append(f"{name}: no runs-on declaration found")
    elif any(runner != "ubuntu-24.04" for runner in runners):
        errors.append(f"{name}: runners must be pinned to ubuntu-24.04, found {runners}")

    for line in content.splitlines():
        match = re.search(r"\buses:\s*([^\s#]+)", line)
        if not match:
            continue
        ref = match.group(1)
        if ref.startswith("./"):
            continue
        if "@" not in ref:
            errors.append(f"{name}: action is not version-pinned: {ref}")
            continue
        action, version = ref.rsplit("@", 1)
        if not re.fullmatch(r"[0-9a-f]{40}", version):
            errors.append(
                f"{name}: external action {action} must be pinned to a 40-character commit SHA"
            )

for name in ("foundation-app.yml", "foundation-visual.yml", "codespaces-contract.yml"):
    content = contents.get(name, "")
    for required in (
        "pull_request:",
        "push:",
        "branches:",
        "- main",
        "workflow_dispatch:",
        "concurrency:",
        "github.event.pull_request.number || github.sha",
    ):
        if required not in content:
            errors.append(f"{name}: missing required PR/main exact-SHA control: {required}")

for name in ("foundation-app.yml", "foundation-visual.yml", "codespaces-contract.yml"):
    content = contents.get(name, "")
    if "github.event.pull_request.head.sha || github.sha" not in content:
        errors.append(f"{name}: must derive evidence SHA from PR head or main SHA")
    if "ref: ${{ env.EVIDENCE_SHA }}" not in content:
        errors.append(f"{name}: checkout must explicitly use EVIDENCE_SHA")

roadmap = contents.get("roadmap-health.yml", "")
if "roadmap-health-${{ github.event_name }}-" not in roadmap:
    errors.append("roadmap-health.yml: concurrency must isolate event families")
if "github.event.pull_request.number || github.event.issue.number || github.sha" not in roadmap:
    errors.append("roadmap-health.yml: concurrency must isolate PR/issue/main identities")

visual = contents.get("foundation-visual.yml", "")
if "local-review-contract:" in visual:
    errors.append("foundation-visual.yml: local review contract belongs to foundation-app.yml")

app = contents.get("foundation-app.yml", "")
if "DESIGN_REVIEW_SKIP_BUILD=1 bash scripts/design_review.sh" not in app:
    errors.append("foundation-app.yml: must own the human review command contract")

if errors:
    print("CI ownership verification failed:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("CI ownership verification passed.")
print("Owned workflows:")
for name in sorted(EXPECTED):
    print(f"- {name}")
