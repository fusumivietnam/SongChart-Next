#!/usr/bin/env python3
"""Classify changed repository paths into deterministic CI impact categories.

Categories remain advisory for CI fan-out. The one enforced use is the Vercel
preview skip safety rule: branches deliberately skipped by Vercel must not carry
runtime-affecting changes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import PurePosixPath

CATEGORIES = (
    "governance",
    "documentation",
    "application",
    "database",
    "frontend",
    "provider",
    "production_package",
    "preview_runtime",
    "developer_environment",
    "visual",
)
PREVIEW_SKIP_PREFIXES = ("docs/", "governance/")
PREVIEW_RUNTIME_CATEGORIES = {
    "application",
    "database",
    "frontend",
    "provider",
    "production_package",
    "preview_runtime",
    "developer_environment",
    "visual",
}


def _starts(path: str, *prefixes: str) -> bool:
    return any(path == prefix or path.startswith(prefix.rstrip("/") + "/") for prefix in prefixes)


def classify_path(path: str) -> set[str]:
    path = str(PurePosixPath(path.strip()))
    impacts: set[str] = set()

    if _starts(path, "governance", "scripts", "tests/governance") or path in {"AGENTS.md", "README.md"}:
        impacts.add("governance")
    if _starts(path, "docs", "reference", "openapi") or path in {"README.md", "AGENTS.md"}:
        impacts.add("documentation")
    if _starts(path, "app", "bootstrap", "config", "routes", "tests/Feature", "tests/Unit") or path in {
        "composer.json", "composer.lock", ".env.example"
    }:
        impacts.add("application")
    if _starts(path, "database") or path in {"compose.yaml", "compose.production.yaml"}:
        impacts.add("database")
    if _starts(path, "resources") or path in {"package.json", "pnpm-lock.yaml", "pnpm-workspace.yaml"}:
        impacts.update({"frontend", "application"})
    if _starts(path, "app/Music/Providers", "docs/providers", "tests/Feature/Music/Providers"):
        impacts.update({"provider", "application"})
    if path in {"Dockerfile", "compose.production.yaml"} or _starts(path, "deploy/production", "scripts/production"):
        impacts.add("production_package")
    if path == "Dockerfile.vercel" or _starts(path, "deploy/vercel") or path == "scripts/preview_smoke.py":
        impacts.add("preview_runtime")
    if _starts(path, ".devcontainer") or path == ".github/workflows/codespaces-contract.yml":
        impacts.add("developer_environment")
    if _starts(path, "design", "resources/js", "resources/css") or path == ".github/workflows/foundation-visual.yml":
        impacts.add("visual")
    if path.startswith(".github/workflows/"):
        impacts.add("governance")

    return impacts


def classify(paths: list[str]) -> dict[str, bool]:
    active: set[str] = set()
    for path in paths:
        if path.strip():
            active.update(classify_path(path))
    return {category: category in active for category in CATEGORIES}


def preview_skip_branch_violation(branch: str, paths: list[str]) -> set[str]:
    if not branch.startswith(PREVIEW_SKIP_PREFIXES):
        return set()
    result = classify(paths)
    return {category for category in PREVIEW_RUNTIME_CATEGORIES if result.get(category)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", help="Changed repository paths. Reads stdin when omitted.")
    parser.add_argument("--json", action="store_true", help="Emit a JSON object instead of key=value lines.")
    parser.add_argument(
        "--assert-preview-skip-branch",
        metavar="BRANCH",
        help="Fail if a docs/* or governance/* branch contains runtime-affecting changes.",
    )
    args = parser.parse_args()
    paths = args.paths
    if not paths:
        import sys
        paths = [line.strip() for line in sys.stdin if line.strip()]

    if args.assert_preview_skip_branch:
        violations = preview_skip_branch_violation(args.assert_preview_skip_branch, paths)
        if violations:
            print(
                "preview-skip branch contains runtime-affecting changes: "
                + ", ".join(sorted(violations))
            )
            return 1
        print("preview-skip branch safety verified")
        return 0

    result = classify(paths)
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        for key, value in result.items():
            print(f"{key}={'true' if value else 'false'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
