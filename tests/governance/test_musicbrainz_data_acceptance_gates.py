"""Issue #174 acceptance criteria, no-network governance test."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATES = ROOT / "docs/providers/MUSICBRAINZ_DATA_ACCEPTANCE_GATES.json"
RIGHTS = ROOT / "docs/providers/MUSICBRAINZ_FIELD_RIGHTS_MATRIX.json"
RUBRIC = ROOT / "tests/Fixtures/musicbrainz/offline-pilot/quality-rubric.json"


class MusicBrainzDataAcceptanceGatesTest(unittest.TestCase):
    def test_distinct_synthetic_and_real_gates_are_fail_closed(self):
        gates = json.loads(GATES.read_text(encoding="utf-8"))
        rights = json.loads(RIGHTS.read_text(encoding="utf-8"))
        rubric = json.loads(RUBRIC.read_text(encoding="utf-8"))
        self.assertEqual(gates["owner_issue"], 174)
        self.assertEqual(gates["overall_decision"], "blocked_pending_rights_provenance_and_owner_approval")
        self.assertEqual(rights["decision"], "blocked_pending_owner_field_signoff")
        self.assertEqual(len(rubric["selected_group_ids"]), 8)
        items = gates["phases"]
        self.assertEqual(len(items), 10)
        self.assertEqual(len({x["id"] for x in items}), len(items))
        synthetic = [x for x in items if x["phase"] == "synthetic"]
        real = [x for x in items if x["phase"] != "synthetic"]
        self.assertEqual(len(synthetic), 3)
        self.assertEqual({x["decision"] for x in synthetic}, {"testable"})
        self.assertEqual(len(real), 7)
        for gate in real:
            self.assertEqual(gate["decision"], "blocked")
            self.assertTrue(gate["owner"])
            self.assertTrue(gate["criterion"])
            self.assertGreater(len(gate["evidence_required"]), 0)
        self.assertEqual({x["id"] for x in real},
                         {"RGT-01", "RGT-02", "OPS-01", "OPS-02",
                          "QLT-01", "QLT-02", "CAN-01"})

    def test_no_synthetic_evidence_promotes_rights_or_canonical_admission(self):
        gates = json.loads(GATES.read_text(encoding="utf-8"))
        evidence = gates["synthetic_evidence_counts"]
        self.assertEqual(evidence["authored_scenarios"], 8)
        for name in ("real_provider_rows", "full_application_joins",
                     "rights_approved_groups", "canonical_admissions"):
            self.assertEqual(evidence[name], 0)
        rights = json.loads(RIGHTS.read_text(encoding="utf-8"))
        self.assertTrue(all(
            x["decision"] in {"review_required", "exclude", "quarantine_nonempty",
                               "exclude_pending_review", "never_export_whole_object"}
            for x in rights["paths"]
        ))
        self.assertTrue(all(x["decision"] == "blocked" for x in rights["other_entity_archives"]))


if __name__ == "__main__":
    unittest.main()
