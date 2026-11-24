"""Synthetic-only contract test for the #174 representative scenario registry."""
import json
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[2] / "tests/Fixtures/musicbrainz/offline-pilot/representative-groups.json"

class RepresentativePilotMatrixTest(unittest.TestCase):
    def test_scenario_matrix_is_bounded_synthetic_and_covers_core_gates(self):
        matrix = json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual(matrix["schema_version"], 1)
        self.assertEqual(matrix["owner_issue"], 174)
        self.assertIn("synthetic", matrix["scope"])
        groups = matrix["entity_groups"]
        self.assertEqual(len(groups), 8)
        self.assertEqual([g["id"] for g in groups], [f"G{i:02d}" for i in range(1,9)])
        allchecks = {check for group in groups for check in group["checks"]}
        for required in ("plain_performance", "credit_order", "no_title_merge",
                         "missing_work_allowed", "whole_record_quarantine", "invalid_mbid",
                         "downstream_ownership_gate", "recursive_supplementary_exclusion"):
            self.assertIn(required, allchecks)
        for group in groups:
            self.assertTrue(group["entities"])
            self.assertTrue(group["checks"])
            self.assertIn(group["expected"], ("evaluation_only", "quarantine", "evaluation_with_admission_blocked"))
            self.assertNotIn("external_id", group)
            self.assertNotIn("mbid", group)

if __name__ == "__main__":
    unittest.main()
