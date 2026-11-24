"""Evaluate bounded synthetic graph fixture coverage without provider data or writes."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "tests/Fixtures/musicbrainz/offline-pilot"
RUBRIC = BASE / "quality-rubric.json"
GRAPHS = BASE / "synthetic-graphs.json"
SCENARIOS = BASE / "representative-groups.json"


def evaluate():
    rubric = json.loads(RUBRIC.read_text(encoding="utf-8"))
    graphs = json.loads(GRAPHS.read_text(encoding="utf-8"))["graphs"]
    scenarios = json.loads(SCENARIOS.read_text(encoding="utf-8"))["entity_groups"]
    ids = [x["id"] for x in graphs]
    expected_ids = rubric["selected_group_ids"]
    if not (rubric["minimum_groups"] <= len(ids) <= rubric["maximum_groups"]):
        raise ValueError("synthetic cohort out of permitted size")
    if ids != expected_ids or ids != [x["id"] for x in scenarios] or len(ids) != len(set(ids)):
        raise ValueError("synthetic group identity mismatch")
    strata = [group_id for stratum in rubric["strata"] for group_id in stratum["ids"]]
    if len(strata) != len(ids) or set(strata) != set(ids):
        raise ValueError("missing or duplicated stratum assignment")
    nodes = set()
    edges = set()
    total_edges = 0
    valid_edges = 0
    outcomes = Counter()
    for graph, scenario in zip(graphs, scenarios):
        if graph["expected"] != scenario["expected"]:
            raise ValueError("expected outcome mismatch")
        aliases = [alias for _, alias in graph["nodes"]]
        if len(aliases) != len(set(aliases)):
            raise ValueError("duplicate node alias")
        alias_set = set(aliases)
        nodes.update(kind for kind, _ in graph["nodes"])
        if not set(scenario["entities"]) <= {kind for kind, _ in graph["nodes"]}:
            raise ValueError("scenario entity coverage mismatch")
        for kind, source, target in graph["links"]:
            total_edges += 1
            if source not in alias_set or target not in alias_set:
                raise ValueError("dangling synthetic edge")
            edges.add(kind)
            valid_edges += 1
        if "canonical_id" in graph or "provider_payload" in graph:
            raise ValueError("canonical or provider payload in synthetic fixture")
        outcomes[graph["expected"]] += 1
    if set(rubric["required_entity_types"]) - nodes or set(rubric["required_relationship_types"]) - edges:
        raise ValueError("required synthetic entity/relation type not represented")
    if dict(outcomes) != rubric["expected_outcomes"]:
        raise ValueError("scenario outcome distribution drift")
    return {
        "scope": rubric["scope"],
        "method": rubric["method"],
        "groups": {"covered": len(ids), "planned": len(expected_ids)},
        "graph_links": {"resolved": valid_edges, "total": total_edges},
        "entity_types": {"represented": len(nodes), "required": len(rubric["required_entity_types"])},
        "relationship_types": {"represented": len(edges), "required": len(rubric["required_relationship_types"])},
        "outcomes": dict(sorted(outcomes.items())),
        "strata": {stratum["name"]: len(stratum["ids"]) for stratum in rubric["strata"]},
        "actual_provider_rows_evaluated": 0,
        "full_application_journeys_verified": 0,
        "rights_cleared_groups": 0,
        "canonical_admissions": 0,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), sort_keys=True))
