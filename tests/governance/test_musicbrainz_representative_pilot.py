"""Check synthetic #174 scenario plans, not provider/license approval or canonical admission."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "tests/Fixtures/musicbrainz/offline-pilot/representative-groups.json"
GRAPHS = ROOT / "tests/Fixtures/musicbrainz/offline-pilot/synthetic-graphs.json"

class RepresentativePilotMatrixTest(unittest.TestCase):
    def test_scenario_registry_and_abstract_graphs_remain_consistent(self):
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        graphs = json.loads(GRAPHS.read_text(encoding="utf-8"))
        self.assertEqual(matrix["schema_version"], 1)
        self.assertEqual(matrix["owner_issue"], 174)
        self.assertIn("synthetic", matrix["scope"])
        self.assertIn("synthetic", graphs["scope"])
        scenarios = matrix["entity_groups"]
        self.assertEqual([x["id"] for x in scenarios], [f"G{i:02d}" for i in range(1, 9)])
        self.assertEqual([x["id"] for x in graphs["graphs"]], [x["id"] for x in scenarios])
        required_checks = {
            "plain_performance", "credit_order", "no_title_merge",
            "missing_work_allowed", "whole_record_quarantine", "invalid_mbid",
            "downstream_ownership_gate", "recursive_supplementary_exclusion"
        }
        self.assertTrue(required_checks <= {c for x in scenarios for c in x["checks"]})
        allowed_types = {"artist", "release_group", "release", "medium", "track", "recording", "work"}
        allowed_relations = {"release_group", "medium", "track", "recording", "artist_credit", "performance"}
        for scenario, graph in zip(scenarios, graphs["graphs"]):
            self.assertEqual(graph["expected"], scenario["expected"])
            self.assertTrue(scenario["checks"])
            self.assertTrue(set(scenario["entities"]) <= allowed_types)
            nodes = graph["nodes"]
            aliases = [alias for _, alias in nodes]
            self.assertEqual(len(aliases), len(set(aliases)))
            self.assertTrue(all(kind in allowed_types for kind, _ in nodes))
            self.assertTrue(set(scenario["entities"]) <= {kind for kind, _ in nodes})
            self.assertFalse(any("-" in alias for alias in aliases), "Synthetic aliases must not resemble MBIDs")
            for relation, source, target in graph["links"]:
                self.assertIn(relation, allowed_relations)
                self.assertIn(source, aliases)
                self.assertIn(target, aliases)
            self.assertNotIn("canonical_id", graph)
            self.assertNotIn("provider_payload", graph)

    def test_negative_gates_are_explicit_and_positive_graph_links_are_consistent(self):
        graphs = {x["id"]: x for x in json.loads(GRAPHS.read_text(encoding="utf-8"))["graphs"]}
        self.assertIn(("performance", "REC01", "W01"), [tuple(x) for x in graphs["G01"]["links"]])
        self.assertEqual([c["position"] for c in graphs["G02"]["credits"]], [1, 2])
        self.assertEqual([c["artist"] for c in graphs["G02"]["credits"]], ["A02a", "A02b"])
        self.assertEqual([x[2] for x in graphs["G03"]["links"]], ["REC03", "REC03"])
        self.assertEqual(len([x for x in graphs["G04"]["links"] if x[0] == "performance"]), 2)
        self.assertFalse(any(x[0] == "performance" for x in graphs["G05"]["links"]))
        self.assertEqual(graphs["G06"]["expected"], "quarantine")
        self.assertEqual(set(graphs["G06"]["performance_attributes"]), {"cover", "live", "instrumental", "partial"})
        self.assertIn(graphs["G07"]["invalid_external_identity_for"], [x[1] for x in graphs["G07"]["nodes"]])
        self.assertEqual(graphs["G07"]["expected"], "quarantine")
        self.assertEqual(len(set(graphs["G08"]["isrcs"])), 1)
        self.assertGreater(len(graphs["G08"]["isrcs"]), 1)
        self.assertEqual(set(graphs["G08"]["supplementary_keys"]), {"tags", "rating", "annotation"})
        self.assertEqual(graphs["G08"]["expected"], "evaluation_with_admission_blocked")

if __name__ == "__main__":
    unittest.main()
