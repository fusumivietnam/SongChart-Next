#!/usr/bin/env python3
"""Fail closed on repository-owned GitHub usage policy regressions."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
MAX_ARTIFACT_RETENTION_DAYS = 14
ALLOWED_BUILDKit_GHA_SCOPES = {"foundation-buildkit"}
HEAVY_WORKFLOWS = {
    "codespaces-contract.yml",
    "foundation-app.yml",
    "foundation-visual.yml",
    "g5-vps-baseline.yml",
    "research-cocoindex.yml",
    "vs01a-artist.yml",
    "vs01b-musicbrainz.yml",
    "vs02-release-recording.yml",
    "vs03-discovery-search.yml",
    "vs04-launch-proof.yml",
}


def fail(message: str) -> None:
    raise SystemExit(message)


def verify_artifact_retention() -> None:
    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text()
        for match in re.finditer(r"retention-days:\s*(\d+)", text):
            days = int(match.group(1))
            if days > MAX_ARTIFACT_RETENTION_DAYS:
                fail(
                    f"{path.relative_to(ROOT)} retains an artifact for {days} days; "
                    f"maximum is {MAX_ARTIFACT_RETENTION_DAYS}"
                )


def verify_heavy_workflow_concurrency() -> None:
    for name in sorted(HEAVY_WORKFLOWS):
        path = WORKFLOWS / name
        if not path.is_file():
            fail(f"missing heavy workflow: {path.relative_to(ROOT)}")
        text = path.read_text()
        if "concurrency:" not in text or "cancel-in-progress: true" not in text:
            fail(f"{path.relative_to(ROOT)} must cancel superseded in-progress runs")


def verify_buildkit_cache_scope() -> None:
    scopes: set[str] = set()
    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text()
        scopes.update(re.findall(r"type=gha,scope=([A-Za-z0-9_.-]+)", text))
    unexpected = scopes - ALLOWED_BUILDKit_GHA_SCOPES
    if unexpected:
        fail(f"unexpected BuildKit GitHub Actions cache scopes: {sorted(unexpected)}")


def verify_codespaces_machine_floor() -> None:
    path = ROOT / ".devcontainer" / "devcontainer.json"
    data = json.loads(path.read_text())
    requirements = data.get("hostRequirements", {})
    expected = {"cpus": 2, "memory": "8gb", "storage": "32gb"}
    if requirements != expected:
        fail(
            "Codespaces hostRequirements must stay at the quota-conscious baseline "
            f"{expected}; got {requirements}"
        )


def main() -> None:
    verify_artifact_retention()
    verify_heavy_workflow_concurrency()
    verify_buildkit_cache_scope()
    verify_codespaces_machine_floor()
    print("GitHub usage policy verified")


if __name__ == "__main__":
    main()
