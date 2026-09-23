#!/usr/bin/env python3
"""Validate authored governance and traceability; standard library only."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "governance"
LIFECYCLE = {"candidate", "approved", "implemented", "verified", "deployed", "watch"}
RESEARCH_STATES = {"registered", "evaluated", "accepted", "rejected", "deferred", "superseded"}
ENVIRONMENTS = {"development", "ci", "staging", "production"}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def load(name):
    data = json.loads((GOV / name).read_text(encoding="utf-8"))
    check(data.get("schema_version") == 1, f"{name}: unsupported schema")
    check(data.get("project") == "SongChart-Next", f"{name}: foreign project")
    return data


def local_file(reference):
    """Only project-relative authored paths; never absolute paths, traversal or URL as local source."""
    check(isinstance(reference, str) and reference and not reference.startswith(("http://", "https://", "/")), f"invalid local reference: {reference!r}")
    path = (ROOT / reference).resolve()
    check(path.is_relative_to(ROOT.resolve()) and path.is_file(), f"missing/unsafe local file: {reference}")
    return path


def unique(items, label):
    check(len(items) == len(set(items)), f"duplicate {label}")


def verify():
    cmap, tmap, amap = (load(name) for name in (
        "CAPABILITY_MAP.json", "TECHNOLOGY_REGISTRY.json", "ACTIVATION_TRIGGERS.json"
    ))
    research, infra = load("RESEARCH_REGISTRY.json"), load("INFRASTRUCTURE_REGISTRY.json")
    caps = cmap["capabilities"]
    capids = [c["id"] for c in caps]
    unique(capids, "capability IDs")
    by_cap = {c["id"]: c for c in caps}
    for c in caps:
        check(c["status"] in LIFECYCLE, f"{c['id']}: unknown lifecycle")
        check(isinstance(c["owner"], str) and c["owner"].strip(), f"{c['id']}: missing owner")
        check(all(d in by_cap and d != c["id"] for d in c["depends_on"]), f"{c['id']}: invalid dependency")
        if c["status"] in {"implemented", "verified", "deployed"}:
            path = c.get("implementation")
            check(isinstance(path, str) and path and
                  (ROOT / path).resolve().is_relative_to(ROOT.resolve()) and
                  (ROOT / path).exists(), f"{c['id']}: missing implementation")
        if c["status"] in {"verified", "deployed"}:
            check(c.get("verification_evidence"), f"{c['id']}: no verification evidence")
        if c["status"] == "deployed":
            check(c.get("deployment_evidence"), f"{c['id']}: no deployment evidence")
    visiting, seen = set(), set()
    def visit(cid):
        check(cid not in visiting, f"dependency cycle at {cid}")
        if cid in seen:
            return
        visiting.add(cid)
        for dependency in by_cap[cid]["depends_on"]:
            visit(dependency)
        visiting.remove(cid)
        seen.add(cid)
    for cid in capids:
        visit(cid)

    techs = tmap["technologies"]
    techids = [t["id"] for t in techs]
    unique(techids, "technology IDs")
    by_tech = {t["id"]: t for t in techs}
    for t in techs:
        check(t["capability"] in by_cap, f"{t['id']}: unknown capability")
        check(t["status"] in LIFECYCLE, f"{t['id']}: unknown technology status")
        check(isinstance(t.get("source"), str) and t["source"].startswith("https://"), f"{t['id']}: missing upstream")
        if t["status"] in {"implemented", "verified", "deployed"}:
            check(t.get("implementation"), f"{t['id']}: missing implementation reference")
            local_file(t["implementation"])
        if t["status"] in {"verified", "deployed"}:
            check(t.get("verification_evidence"), f"{t['id']}: missing verification evidence")

    triggers = amap["triggers"]
    unique([t["capability"] for t in triggers], "activation triggers")
    for t in triggers:
        check(t["capability"] in by_cap, f"trigger: unknown capability {t['capability']}")
        check(t["condition"] and t["evidence"] and t["decision"] == "human-review",
              f"trigger: invalid human-review gate {t['capability']}")

    records = research["research"]
    ids = [r["id"] for r in records]
    unique(ids, "research IDs")
    by_research = {r["id"]: r for r in records}
    for r in records:
        check(re.fullmatch(r"RES-[0-9]{4,}", r["id"]) is not None, f"invalid research ID {r['id']}")
        check(r["status"] in RESEARCH_STATES and r["title"].strip(), f"{r['id']}: invalid research record")
        source = r["source"]
        check(isinstance(source, str) and source, f"{r['id']}: missing provenance")
        if not source.startswith("https://"):
            local_file(source)
        check(len(r["capability_ids"]) == len(set(r["capability_ids"])) and
              all(cid in by_cap for cid in r["capability_ids"]), f"{r['id']}: invalid capabilities")
        if r["status"] in {"accepted", "rejected"}:
            check(r.get("decision_ref"), f"{r['id']}: decision reference required")
        if r.get("decision_ref") and not r["decision_ref"].startswith("https://"):
            local_file(r["decision_ref"])
        successor = r.get("superseded_by")
        check((r["status"] == "superseded") == bool(successor), f"{r['id']}: supersession mismatch")
        if successor:
            check(successor in by_research and successor != r["id"], f"{r['id']}: invalid successor")
    for rid in ids:
        visited = {rid}
        nxt = by_research[rid].get("superseded_by")
        while nxt:
            check(nxt not in visited, f"research supersession cycle {rid}")
            visited.add(nxt)
            nxt = by_research[nxt].get("superseded_by")

    instances = infra["instances"]
    unique([i["id"] for i in instances], "infrastructure instance IDs")
    for i in instances:
        check(i["capability_id"] in by_cap, f"{i['id']}: unknown capability")
        check(i["technology_id"] in by_tech, f"{i['id']}: unknown technology")
        check(by_tech[i["technology_id"]]["capability"] == i["capability_id"],
              f"{i['id']}: capability/technology ownership mismatch")
        check(i["environment"] in ENVIRONMENTS, f"{i['id']}: invalid environment")
        check(i["status"] in {"approved", "implemented", "verified", "deployed", "retired"},
              f"{i['id']}: invalid runtime status")
        check(i["runtime_owner"].strip() and i["failure_mode"].strip() and i["data_classification"].strip(),
              f"{i['id']}: incomplete ownership")
        local_file(i["configuration_ref"])
        for ref in ("backup_policy_ref", "recovery_policy_ref"):
            if i.get(ref):
                local_file(i[ref])
        if i["status"] in {"verified", "deployed"}:
            check(i["operational_evidence"], f"{i['id']}: missing operational evidence")
        if i["status"] == "deployed":
            check(i["environment"] == "production", f"{i['id']}: deployed must be production")

    for reference in (
        "AGENTS.md", "docs/product/PRODUCT_CHARTER.md", "docs/architecture/ARCHITECTURE.md",
        "design/DESIGN_AUTHORITY.md", "reference/README.md", "docs/roadmap/VERTICAL_SLICES.md",
        "docs/engineering/DELIVERY_CONTRACT.md", "docs/operations/ACCEPTANCE_GATES.md",
        "docs/operations/DEPENDENCY_POLICY.md", "docs/operations/ENVIRONMENT_POLICY.md",
        "docs/research/README.md", "governance/schemas/research.schema.json",
        "governance/schemas/infrastructure.schema.json",
    ):
        local_file(reference)
    print(f"PASS: {len(caps)} capabilities, {len(techs)} technologies, {len(triggers)} triggers, "
          f"{len(records)} registered research, {len(instances)} runtime instances; references consistent")


if __name__ == "__main__":
    verify()
