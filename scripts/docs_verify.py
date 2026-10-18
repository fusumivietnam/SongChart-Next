#!/usr/bin/env python3
"""Verify documentation ownership, references and generated freshness."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

from docs_generate import GENERATORS, REGISTRY_PATH, render_outputs

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_MODES = {"authored", "generated"}
FORBIDDEN_README_STATUS = (
    "roadmap-reconcile:start",
    "roadmap-reconcile:end",
    "## Current status",
    "## Current delivery frontier",
)


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
        if "automation_owner" in document:
            errors.append(f"{path}: automation_owner is not allowed; authored authority or generated projection must be explicit")

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

    if generated_paths != {"docs/generated/PROJECT_STATUS.md"}:
        errors.append("generated status must be exactly docs/generated/PROJECT_STATUS.md")

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
    if readme is None or readme.get("mode") != "authored":
        errors.append("README.md must be authored and must not carry automated status sections")
    readme_path = root / "README.md"
    if readme_path.exists():
        readme_text = readme_path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_README_STATUS:
            if marker in readme_text:
                errors.append(f"README.md contains forbidden mutable status marker: {marker}")

    return errors


def audit_markdown(root: Path = ROOT) -> dict:
    """Read-only inventory from tracked Git paths; not a status or lifecycle authority."""
    process = subprocess.run(
        ["git", "ls-files", "-z", "--", "*.md"], cwd=root,
        capture_output=True, check=False,
    )
    if process.returncode:
        raise RuntimeError("Cannot enumerate Git-tracked Markdown: " + process.stderr.decode(errors="replace"))
    paths = sorted(p.decode("utf-8") for p in process.stdout.split(b"\0") if p)
    roles = {"generated": 0, "historical": 0, "authored": 0}
    missing_links = []
    # Advisory classification only. A directory contract is not per-file freshness registration.
    registered = {item["path"]: item["owner"] for item in _load(root, REGISTRY_PATH)["documents"]}
    research = {item["source"] for item in _load(root, "governance/RESEARCH_REGISTRY.json")["research"]}
    governed_prefixes = (
        ("docs/adr/", "architecture-decisions"),
        ("docs/architecture/", "architecture"),
        ("docs/architecture/adr/", "architecture-decisions"),
        ("design/", "design-authority"),
        ("docs/roadmap/", "roadmap-governance"),
        ("docs/operations/", "operations"),
        ("docs/providers/", "provider-policy"),
        ("docs/engineering/", "engineering"),
        ("docs/research/", "research-governance"),
        ("docs/product/", "product-scope"),
        ("docs/security/", "security-and-recovery"),
        (".github/", "github-workflows"),
        ("reference/", "developer-reference"),
    )
    coverage = {"registered": [], "governed": [], "unresolved": []}
    inbound = {relative: 0 for relative in paths}
    tracked = set(paths)
    # Explicit registry membership and GitHub entrypoint conventions are stronger
    # usage signals than an incoming Markdown link; neither proves current utility.
    registry_sources = {
        source for item in _load(root, REGISTRY_PATH)["documents"]
        for source in item.get("sources", []) if isinstance(source, str)
    }
    registry_sources.update(research)
    registry_sources.update(
        item.get("decision_ref") for item in _load(root, "governance/RESEARCH_REGISTRY.json")["research"]
        if item.get("decision_ref")
    )
    # Literal references from non-Markdown tracked text are weak evidence, but
    # enough to keep a candidate out of the no-reference inspection queue.
    # Limit scan size and avoid generated/vendor/lockfile content.
    tracked_files = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True,
    ).stdout.split(b"\\0")
    non_markdown_sources = []
    for entry in tracked_files:
        if not entry:
            continue
        name = entry.decode("utf-8")
        if name.endswith(".md") or name.endswith((".lock", ".svg", ".png", ".jpg", ".webp", ".map")):
            continue
        path = root / name
        if path.is_file() and path.stat().st_size <= 256_000:
            try:
                non_markdown_sources.append((name, path.read_text(encoding="utf-8")))
            except UnicodeDecodeError:
                continue
    literal_refs = {
        target: [name for name, body in non_markdown_sources if target in body][:5]
        for target in paths
    }
    implicit_entrypoints = {
        p for p in paths
        if p.startswith((".github/ISSUE_TEMPLATE/", ".github/agents/"))
        or p == ".github/PULL_REQUEST_TEMPLATE.md"
    }

    for relative in paths:
        role = "generated" if relative.startswith("docs/generated/") else (
            "historical" if relative.startswith(("docs/adr/", "docs/research/", "design/decisions/", "design/baselines/")) else "authored"
        )
        roles[role] += 1
        if relative in registered:
            coverage["registered"].append({"path": relative, "owner": registered[relative]})
        elif relative in research:
            coverage["governed"].append({"path": relative, "mechanism": "research-registry"})
        else:
            mechanism = next((owner for prefix, owner in governed_prefixes if relative.startswith(prefix)), None)
            if relative == "AGENTS.md":
                mechanism = "project-control"
            if mechanism:
                coverage["governed"].append({"path": relative, "mechanism": mechanism})
            else:
                coverage["unresolved"].append(relative)
        source = root / relative
        if not source.is_file():
            missing_links.append({"source": relative, "target": "<tracked file missing>"})
            continue
        body = source.read_text(encoding="utf-8")
        # Local inline Markdown links only; URL/anchors and image assets remain external/separate checks.
        body = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
        for match in re.finditer(r"(?<!!)\[[^\]\n]+\]\(([^\s)]+)(?:\s+[\"'][^\n]*?[\"'])?\)", body):
            target = match.group(1)
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith(("#", "/", "//", "mailto:")):
                continue
            path_part = unquote(parsed.path)
            if not path_part or path_part.startswith("#"):
                continue
            resolved = (source.parent / path_part).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                missing_links.append({"source": relative, "target": target})
            elif resolved.is_file():
                local = resolved.relative_to(root.resolve()).as_posix()
                if local in tracked:
                    inbound[local] += 1
    return {
        "source": "git ls-files (tracked Markdown at checked-out SHA)",
        "read_only": True,
        "tracked_markdown": len(paths),
        "roles": roles,
        "missing_relative_links": missing_links,
        "ownership_coverage": {
            "registered_count": len(coverage["registered"]),
            "governed_count": len(coverage["governed"]),
            "unresolved_count": len(coverage["unresolved"]),
            **coverage,
        },
        "unreferenced_candidates": [
            path for path, count in inbound.items()
            if count == 0 and path not in {"README.md", "AGENTS.md"}
        ],
        "orphan_triage": {
            "explicit_registry_or_entrypoint": [
                {"path": path, "signal": (
                    "registry-reference" if path in registry_sources or path in registered
                    else "github-entrypoint"
                )}
                for path, count in inbound.items()
                if count == 0 and path not in {"README.md", "AGENTS.md"} and (
                    path in registry_sources or path in registered or path in implicit_entrypoints
                )
            ],
            "non_markdown_literal_reference": [
                {"path": path, "sources": literal_refs[path]}
                for path, count in inbound.items()
                if count == 0 and path not in {"README.md", "AGENTS.md"}
                and path not in registry_sources and path not in registered
                and path not in implicit_entrypoints and literal_refs[path]
            ],
            "manual_review": [
                path for path, count in inbound.items()
                if count == 0
                and path not in {"README.md", "AGENTS.md"}
                and path not in registry_sources
                and path not in registered
                and path not in implicit_entrypoints
                and not literal_refs[path]
            ],
        },
        "note": "Directory governance, exact path literals in non-Markdown tracked text, and zero inbound Markdown references are advisory signals, not proof of file ownership, usage, redundancy or lifecycle. Generated/ADR/research files must never be deleted based on this audit.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit-json', action='store_true', help='print Git-tracked Markdown inventory and link diagnostics (read only)')
    args = parser.parse_args()
    if args.audit_json:
        print(json.dumps(audit_markdown(), indent=2, ensure_ascii=False))
        return 0
    errors = verify()
    if errors:
        print("Documentation verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Documentation registry and generated projection are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
