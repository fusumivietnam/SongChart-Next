#!/usr/bin/env python3
"""Read-only, reproducible local project snapshot; no chat or cached status authority."""
import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "governance"


def git(*args):
    result = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def snapshot():
    def load(name):
        return json.loads((GOV / name).read_text(encoding="utf-8"))
    capabilities = load("CAPABILITY_MAP.json")["capabilities"]
    technologies = load("TECHNOLOGY_REGISTRY.json")["technologies"]
    research = load("RESEARCH_REGISTRY.json")["research"]
    instances = load("INFRASTRUCTURE_REGISTRY.json")["instances"]
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    head = git("rev-parse", "HEAD")
    dirty = git("status", "--porcelain")
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {"repository": "fusumivietnam/SongChart-Next", "branch": branch or "unknown",
                   "commit": head or "unknown", "working_tree_dirty": bool(dirty) if dirty is not None else None},
        "authority": {"roadmap": "docs/roadmap/VERTICAL_SLICES.md",
                      "execution": "GitHub Issues/PRs (query live; not inferred from files)",
                      "versions": "repository manifests/lockfiles (not technology candidates)"},
        "capabilities": [{"id": c["id"], "status": c["status"]} for c in capabilities],
        "technologies": [{"id": t["id"], "status": t["status"]} for t in technologies],
        "research": [{"id": r["id"], "status": r["status"]} for r in research],
        "runtime_instances": [{"id": i["id"], "status": i["status"]} for i in instances],
        "live_github": {"issues": "unknown", "pull_requests": "unknown", "ci": "unknown",
                        "deployment": "unknown", "reason": "Offline script does not query GitHub API"},
        "active_slice": "unknown; determine from live GitHub Issues/PRs and roadmap approvals",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable snapshot")
    args = parser.parse_args()
    state = snapshot()
    if args.json:
        print(json.dumps(state, indent=2))
    else:
        print(f"SongChart Next | {state['source']['branch']} @ {state['source']['commit']}")
        print(f"Working tree dirty: {state['source']['working_tree_dirty']}")
        print(f"Capabilities: {len(state['capabilities'])}; research: {len(state['research'])}; "
              f"runtime instances: {len(state['runtime_instances'])}")
        print("Live Issues/PRs/CI/deployment: UNKNOWN (query GitHub before claiming active work or completion)")
        print(f"Active slice: {state['active_slice']}")
        print("This snapshot is generated read-only, not an authority or a release verification.")


if __name__ == "__main__":
    main()
