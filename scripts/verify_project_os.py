#!/usr/bin/env python3
"""Standard-library verification of authored SongChart Next project registry."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "governance"


def load(name):
    path = GOV / name
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("schema_version") == 1, f"{name}: unsupported schema"
    assert data.get("project") == "SongChart-Next", f"{name}: foreign project"
    return data


def main():
    cmap = load("CAPABILITY_MAP.json")
    tmap = load("TECHNOLOGY_REGISTRY.json")
    amap = load("ACTIVATION_TRIGGERS.json")
    caps = cmap["capabilities"]
    ids = [c["id"] for c in caps]
    assert len(ids) == len(set(ids)), "duplicate capability IDs"
    allowed = {"candidate", "approved", "implemented", "verified", "deployed", "watch"}
    by_id = {c["id"]: c for c in caps}
    for c in caps:
        assert c["status"] in allowed, f"{c['id']}: unknown lifecycle"
        assert c["owner"].strip(), f"{c['id']}: owner required"
        assert all(d in by_id and d != c["id"] for d in c["depends_on"]), f"{c['id']}: invalid dependency"
        if c["status"] in {"implemented", "verified", "deployed"}:
            assert c["implementation"], f"{c['id']}: implementation evidence missing"
            assert (ROOT / c["implementation"]).exists(), f"{c['id']}: implementation path absent"
    visiting, seen = set(), set()
    def visit(cid):
        assert cid not in visiting, f"dependency cycle at {cid}"
        if cid in seen:
            return
        visiting.add(cid)
        for dep in by_id[cid]["depends_on"]:
            visit(dep)
        visiting.remove(cid)
        seen.add(cid)
    for cid in ids:
        visit(cid)
    tids = [t["id"] for t in tmap["technologies"]]
    assert len(tids) == len(set(tids)), "duplicate technology IDs"
    for t in tmap["technologies"]:
        assert t["capability"] in by_id, f"{t['id']}: unknown capability"
        assert t["status"] in allowed, f"{t['id']}: unknown status"
        assert t["source"].startswith("https://"), f"{t['id']}: source URL required"
    aids = [t["capability"] for t in amap["triggers"]]
    assert len(aids) == len(set(aids)), "duplicate activation triggers"
    for trigger in amap["triggers"]:
        assert trigger["capability"] in by_id, "trigger references unknown capability"
        assert trigger["condition"] and trigger["evidence"], "trigger needs condition and evidence"
        assert trigger["decision"] == "human-review", "no automatic activation permitted"
    for p in [
        "AGENTS.md", "docs/product/PRODUCT_CHARTER.md",
        "docs/architecture/ARCHITECTURE.md",
        "design/DESIGN_AUTHORITY.md", "reference/README.md",
        "docs/roadmap/VERTICAL_SLICES.md",
    ]:
        assert (ROOT / p).is_file(), f"missing authority: {p}"
    print(f"PASS: {len(caps)} capabilities, {len(tids)} technologies, {len(aids)} triggers; dependency graph acyclic")


if __name__ == "__main__":
    main()
