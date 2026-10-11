#!/usr/bin/env python3
"""Verify documentation ownership, references and generated freshness."""
from __future__ import annotations

import json
from pathlib import Path

from docs_generate import GENERATORS, REGISTRY_PATH, render_outputs

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_MODES = {"authored", "generated", "mixed"}


def _load(root: Path, path: str) -> dict:
    return json.loads((root / path).read_text(encoding="utf-8"))


def verify(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    registry_file = root / REGISTRY_PATH
    if not registry_file.exists():
        return [f"missing registry: {REGISTRY_PATH}"]
    registry = _load(root, REGISTRY_PATH)
    if registry.get("schema_version") != 1:
        errors.append("DOCUMENTATION_REGISTRY schema_version must be 1")
    documents = registry.get("documents")
    if not isinstance(documents, list) or not documents:
        return errors + ["DOCUMENTATION_REGISTRY documents must be a non-empty list"]

    seen: set[str] = set()
    generated_paths: set[str] = set()
    for document in documents:
        path = document.get("path")
        mode = document.get("mode")
        owner = document.get("owner")
        if not isinstance(path, str) or not path or path.startswith("/") or ".." in Path(path).parts:
            errors.append(f"invalid documentation path: {path!r}")
            continue
        if path in seen:
            errors.append(f"duplicate documentation path: {path}")
        seen.add(path)
        if mode not in ALLOWED_MODES:
            errors.append(f"{path}: invalid mode {mode!r}")
        if not isinstance(owner, str) or not owner:
            errors.append(f"{path}: owner is required")
        if not (root / path).exists():
            errors.append(f"{path}: registered document does not exist")
        sources = document.get("sources", [])
        if not isinstance(sources, list) or not sources:
            errors.append(f"{path}: at least one source is required")
        else:
            for source in sources:
                if not isinstance(source, str) or source.startswith("/") or ".." in Path(source).parts:
                    errors.append(f"{path}: invalid source {source!r}")
                elif not (root / source).exists():
                    errors.append(f"{path}: missing source {source}")
        if mode == "generated":
            generated_paths.add(path)
            generator = document.get("generator")
            if generator not in GENERATORS:
                errors.append(f"{path}: unknown generator {generator!r}")
        elif "generator" in document:
            errors.append(f"{path}: only generated documents may declare generator")

    projections = registry.get("projections", {})
    capability_ids = {item["id"] for item in _load(root, "governance/CAPABILITY_MAP.json")["capabilities"]}
    technology_ids = {item["id"] for item in _load(root, "governance/TECHNOLOGY_REGISTRY.json")["technologies"]}
    projection_references_valid = True
    for capability_id in projections.get("capabilities", []):
        if capability_id not in capability_ids:
            errors.append(f"unknown projected capability: {capability_id}")
            projection_references_valid = False
    for technology_id in projections.get("technologies", []):
        if technology_id not in technology_ids:
            errors.append(f"unknown projected technology: {technology_id}")
            projection_references_valid = False

    generated_dir = root / "docs" / "generated"
    if generated_dir.exists():
        for path in generated_dir.glob("*.md"):
            relative = path.relative_to(root).as_posix()
            if relative not in generated_paths:
                errors.append(f"unregistered generated document: {relative}")

    if projection_references_valid:
        for relative, expected in render_outputs(root).items():
            path = root / relative
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                errors.append(f"stale generated document: {relative}")

    readme = next((item for item in documents if item.get("path") == "README.md"), None)
    if readme is None or readme.get("mode") != "mixed" or readme.get("automation_owner") != "roadmap-reconcile":
        errors.append("README.md must remain mixed-mode and owned by roadmap-reconcile for automated status sections")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        print("Documentation verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Documentation registry and generated projections are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
