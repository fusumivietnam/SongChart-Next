"""#174 no-network regression of field-rights decisions and synthetic graph coverage."""
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RIGHTS = ROOT / "docs/providers/MUSICBRAINZ_FIELD_RIGHTS_MATRIX.json"
GRAPHS = ROOT / "tests/Fixtures/musicbrainz/offline-pilot/synthetic-graphs.json"
SCENARIOS = ROOT / "tests/Fixtures/musicbrainz/offline-pilot/representative-groups.json"

class MusicBrainzFieldRightsCoverageTest(unittest.TestCase):
    def test_field_rights_fail_closed(self):
        matrix = json.loads(RIGHTS.read_text(encoding="utf-8"))
        self.assertEqual(matrix["schema_version"], 1)
        self.assertIn("synthetic_only", matrix["scope"])
        self.assertEqual(matrix["decision"], "blocked_pending_owner_field_signoff")
        rights = matrix["paths"]
        self.assertEqual(len(rights), 31)
        self.assertEqual(len({x["path"] for x in rights}), 31)
        decisions = {
            "core_candidate": "review_required",
            "supplementary_cc_by_nc_sa": "exclude",
            "semantics_unsupported": "quarantine_nonempty",
            "not_reviewed": "exclude_pending_review",
            "structural_container": "never_export_whole_object",
        }
        for row in rights:
            self.assertTrue(row["path"].startswith("$."))
            self.assertEqual(row["decision"], decisions[row["classification"]])
        bypath = {row["path"]: row for row in rights}
        for path in ("$.tags", "$.genres", "$.rating", "$.annotation",
                     "$.artist-credit[*].artist.tags", "$.artist-credit[*].artist.genres",
                     "$.relations[*].work.tags"):
            self.assertEqual(bypath[path]["classification"], "supplementary_cc_by_nc_sa")
        self.assertEqual(bypath["$.artist-credit[*]"]["decision"], "never_export_whole_object")
        self.assertEqual(bypath["$.artist-credit[*]"]["classification"], "structural_container")
        for key in ("attributes", "attribute-ids", "attribute-values"):
            self.assertEqual(bypath["$.relations[*]."+key]["decision"], "quarantine_nonempty")
        self.assertEqual({x["archive"] for x in matrix["other_entity_archives"]},
                         {"artist", "release-group", "release", "work"})
        self.assertTrue(all(x["decision"] == "blocked" for x in matrix["other_entity_archives"]))
        self.assertIn("upstream_license_discrepancy", matrix["sources"])

    def test_no_parent_container_is_licensed_by_leaf_review(self):
        matrix = json.loads(RIGHTS.read_text(encoding="utf-8"))
        rows = {x["path"]: x for x in matrix["paths"]}
        # A typed order position may be derived from an array, but its entire
        # nested object is not legally or semantically safe to project.
        self.assertEqual(rows["$.artist-credit[*]"]["decision"], "never_export_whole_object")
        approved_decisions = {"review_required"}
        for path, row in rows.items():
            if row["decision"] in approved_decisions:
                self.assertNotIn(path, {"$.artist-credit[*]", "$.relations[*]", "$.artist-credit"})
        # This is a triage map, not a usable runtime allowlist or a rights grant.
        self.assertEqual(matrix["decision"], "blocked_pending_owner_field_signoff")

    def test_eight_scenarios_structural_only(self):
        scenarios = json.loads(SCENARIOS.read_text(encoding="utf-8"))["entity_groups"]
        graphs = json.loads(GRAPHS.read_text(encoding="utf-8"))["graphs"]
        self.assertEqual(len(graphs), 8)
        self.assertEqual([x["id"] for x in graphs], [x["id"] for x in scenarios])
        self.assertEqual(Counter(x["expected"] for x in graphs),
            Counter({"evaluation_only": 5, "quarantine": 2, "evaluation_with_admission_blocked": 1}))
        for graph in graphs:
            aliases = [alias for _, alias in graph["nodes"]]
            self.assertEqual(len(aliases), len(set(aliases)))
            for kind, source, target in graph["links"]:
                self.assertIn(source, aliases)
                self.assertIn(target, aliases)
            self.assertNotIn("canonical_id", graph)
            self.assertNotIn("provider_payload", graph)
