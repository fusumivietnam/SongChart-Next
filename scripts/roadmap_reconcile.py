#!/usr/bin/env python3
"""Prepare deterministic post-merge roadmap reconciliation patches.

This writer never approves product/technology/provider/deployment decisions. It only
applies metadata already reviewed in a merged PR and writes repository authorities
on a reconciliation branch/PR.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

METADATA_RE = re.compile(r"<!--\s*songchart-reconcile\s*(\{.*?\})\s*-->", re.I | re.S)
ALLOWED_TARGETS = {"implemented", "verified"}
ALLOWED_RECONCILE = {"capability-map", "vertical-slices", "readme"}
LIFECYCLE_ORDER = {"candidate": 0, "approved": 1, "implemented": 2, "verified": 3, "deployed": 4, "watch": -1}


def parse_metadata(body):
    match = METADATA_RE.search(body or "")
    if not match:
        return None
    value = json.loads(match.group(1))
    if not isinstance(value, dict):
        raise ValueError("songchart-reconcile metadata must be a JSON object")
    return value


def validate_metadata(meta):
    if meta is None:
        return ["missing songchart-reconcile metadata"]
    errors = []
    if meta.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if meta.get("skip") is True:
        return errors
    if meta.get("decision_required"):
        errors.append("decision_required must be false for automatic reconciliation")
    if meta.get("roadmap_scope_change"):
        errors.append("roadmap_scope_change must be false for automatic reconciliation")
    if meta.get("technology_activation"):
        errors.append("technology_activation must be false for automatic reconciliation")
    if meta.get("provider_activation"):
        errors.append("provider_activation must be false for automatic reconciliation")
    if meta.get("deployment_effect", "none") != "none":
        errors.append("deployment_effect must be none for automatic reconciliation")
    reconcile = meta.get("reconcile", [])
    if not isinstance(reconcile, list) or any(item not in ALLOWED_RECONCILE for item in reconcile):
        errors.append("reconcile contains unsupported target")
    effects = meta.get("lifecycle_effects", {})
    if not isinstance(effects, dict):
        errors.append("lifecycle_effects must be an object")
    else:
        for capability, target in effects.items():
            if not isinstance(capability, str) or target not in ALLOWED_TARGETS:
                errors.append(f"unsupported lifecycle effect: {capability} -> {target}")
    for field in ("capability_scope_append",):
        value = meta.get(field, {})
        if value and not isinstance(value, dict):
            errors.append(f"{field} must be an object")
    return errors


def evidence_entry(pr, workflow_names):
    merged_at = pr.get("merged_at") or datetime.now(timezone.utc).isoformat()
    return {
        "type": "github-actions",
        "pr": int(pr["number"]),
        "head_sha": pr["head"]["sha"],
        "merge_sha": pr.get("merge_commit_sha"),
        "workflows": sorted(set(workflow_names)),
        "verified_at": merged_at[:10],
    }


def evidence_prs(cap):
    found = set()
    current = cap.get("verification_evidence")
    if isinstance(current, dict) and isinstance(current.get("pr"), int):
        found.add(current["pr"])
    for item in cap.get("verification_history") or []:
        if isinstance(item, dict) and isinstance(item.get("pr"), int):
            found.add(item["pr"])
    return found


def reconcile_capability_map(path, meta, pr, workflows):
    data = json.loads(path.read_text(encoding="utf-8"))
    capabilities = {item["id"]: item for item in data["capabilities"]}
    evidence = evidence_entry(pr, workflows)
    changed = False
    for capability_id, target in meta.get("lifecycle_effects", {}).items():
        if capability_id not in capabilities:
            raise ValueError(f"unknown capability: {capability_id}")
        cap = capabilities[capability_id]
        current = cap["status"]
        if current in {"candidate", "watch", "deployed"}:
            raise ValueError(f"automatic reconciliation cannot promote from {current}: {capability_id}")
        if LIFECYCLE_ORDER[target] < LIFECYCLE_ORDER[current]:
            raise ValueError(f"automatic reconciliation cannot demote {capability_id}: {current} -> {target}")
        if current == "approved" and target not in {"implemented", "verified"}:
            raise ValueError(f"unsupported approved transition for {capability_id}")
        if current == "implemented" and target not in {"implemented", "verified"}:
            raise ValueError(f"unsupported implemented transition for {capability_id}")
        if current == "verified" and target != "verified":
            raise ValueError(f"verified capability may only remain verified: {capability_id}")
        if current != target:
            cap["status"] = target
            changed = True
        if target == "verified" and int(pr["number"]) not in evidence_prs(cap):
            history = list(cap.get("verification_history") or [])
            previous = cap.get("verification_evidence")
            if isinstance(previous, dict) and previous.get("pr") not in {x.get("pr") for x in history if isinstance(x, dict)}:
                history.append(previous)
            history.append(evidence)
            cap["verification_history"] = history
            cap["verification_evidence"] = evidence
            changed = True
    for capability_id, sentence in meta.get("capability_scope_append", {}).items():
        if capability_id not in capabilities:
            raise ValueError(f"unknown capability scope target: {capability_id}")
        if not isinstance(sentence, str) or not sentence.strip():
            raise ValueError(f"empty capability scope append for {capability_id}")
        cap = capabilities[capability_id]
        scope = (cap.get("scope") or "").strip()
        sentence = sentence.strip()
        if sentence not in scope:
            cap["scope"] = (scope + " " + sentence).strip()
            changed = True
    if changed:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return changed


def section_bounds(text, slice_id):
    pattern = re.compile(rf"^##\s+{re.escape(slice_id)}\b.*$", re.I | re.M)
    match = pattern.search(text)
    if not match:
        raise ValueError(f"roadmap slice section not found: {slice_id}")
    next_heading = re.search(r"^##\s+", text[match.end():], re.M)
    end = match.end() + (next_heading.start() if next_heading else len(text) - match.end())
    return match.start(), end


def reconcile_vertical_slices(path, meta, pr):
    note = meta.get("vertical_slice_note")
    if not note:
        return False
    slice_id = meta.get("slice")
    if not isinstance(slice_id, str) or not slice_id:
        raise ValueError("vertical_slice_note requires slice")
    text = path.read_text(encoding="utf-8")
    marker = f"<!-- reconciliation:pr-{int(pr['number'])} -->"
    if marker in text:
        return False
    _, end = section_bounds(text, slice_id)
    block = f"\n\n{marker}\n{note.strip()}\n"
    text = text[:end].rstrip() + block + "\n" + text[end:].lstrip("\n")
    path.write_text(text, encoding="utf-8")
    return True


def reconcile_readme(path, meta, pr):
    note = meta.get("readme_note")
    if not note:
        return False
    text = path.read_text(encoding="utf-8")
    start = "<!-- roadmap-reconcile:start -->"
    end = "<!-- roadmap-reconcile:end -->"
    block = (
        f"{start}\n"
        "Repository lifecycle authority remains `governance/CAPABILITY_MAP.json`; planned scope remains `docs/roadmap/VERTICAL_SLICES.md`; live execution remains GitHub Issues/PRs.\n\n"
        f"Latest reconciled product evidence: PR #{int(pr['number'])} — {note.strip()}\n"
        f"{end}"
    )
    if start in text and end in text:
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        updated = before + block + after
    else:
        heading = "## Current status"
        pos = text.find(heading)
        if pos < 0:
            raise ValueError("README Current status heading not found")
        line_end = text.find("\n", pos)
        updated = text[: line_end + 1] + "\n" + block + "\n" + text[line_end + 1 :]
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def apply(root, meta, pr, workflows):
    errors = validate_metadata(meta)
    if errors:
        raise ValueError("; ".join(errors))
    if meta.get("skip") is True:
        return []
    root = Path(root)
    changed = []
    targets = set(meta.get("reconcile", []))
    if "capability-map" in targets:
        path = root / "governance/CAPABILITY_MAP.json"
        if reconcile_capability_map(path, meta, pr, workflows):
            changed.append(str(path.relative_to(root)))
    if "vertical-slices" in targets:
        path = root / "docs/roadmap/VERTICAL_SLICES.md"
        if reconcile_vertical_slices(path, meta, pr):
            changed.append(str(path.relative_to(root)))
    if "readme" in targets:
        path = root / "README.md"
        if reconcile_readme(path, meta, pr):
            changed.append(str(path.relative_to(root)))
    return changed


def event_pr(event):
    pr = event.get("pull_request")
    if not isinstance(pr, dict):
        raise ValueError("event does not contain pull_request")
    return pr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--workflows-json", default="[]")
    parser.add_argument("--output-json")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    event = json.loads(Path(args.event).read_text(encoding="utf-8"))
    pr = event_pr(event)
    meta = parse_metadata(pr.get("body") or "")
    result = {
        "pr": pr.get("number"),
        "safe": False,
        "skip": False,
        "changed_files": [],
        "errors": [],
    }
    if meta is None:
        result["skip"] = True
        result["errors"] = ["missing songchart-reconcile metadata"]
    else:
        errors = validate_metadata(meta)
        if meta.get("skip") is True:
            result["skip"] = True
        elif errors:
            result["errors"] = errors
        else:
            result["safe"] = True
            if args.apply:
                workflows = json.loads(args.workflows_json)
                result["changed_files"] = apply(args.root, meta, pr, workflows)
    if args.output_json:
        Path(args.output_json).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 2 if result["errors"] and not result["skip"] else 0


if __name__ == "__main__":
    sys.exit(main())
