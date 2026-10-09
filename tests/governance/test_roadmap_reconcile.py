import json
import tempfile
import unittest
from pathlib import Path

from scripts import roadmap_reconcile as reconcile


class RoadmapReconcileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "governance").mkdir()
        (root / "docs/roadmap").mkdir(parents=True)
        (root / "governance/CAPABILITY_MAP.json").write_text(json.dumps({
            "schema_version": 1,
            "project": "SongChart-Next",
            "capabilities": [
                {
                    "id": "public-web",
                    "status": "verified",
                    "implementation": "resources/js/pages",
                    "scope": "old",
                    "verification_evidence": {
                        "type": "github-actions",
                        "pr": 81,
                        "head_sha": "old",
                        "merge_sha": "oldm",
                        "workflows": ["x"],
                        "verified_at": "2026-10-08",
                    },
                },
                {"id": "future", "status": "candidate", "implementation": None},
            ],
        }), encoding="utf-8")
        (root / "docs/roadmap/VERTICAL_SLICES.md").write_text(
            "# V\n\n## VS-03 — x\nOld\n\n## VS-04 — y\nLater\n", encoding="utf-8"
        )
        (root / "README.md").write_text(
            "# R\n\n## Current status\nOld\n\n## Next\nN\n", encoding="utf-8"
        )
        self.root = root
        self.pr = {
            "number": 88,
            "head": {"sha": "head88"},
            "merge_commit_sha": "merge88",
            "merged_at": "2026-10-09T00:00:00Z",
        }

    def tearDown(self):
        self.tmp.cleanup()

    def metadata(self):
        return {
            "schema_version": 1,
            "slice": "VS-03",
            "capabilities": ["public-web"],
            "lifecycle_effects": {"public-web": "verified"},
            "roadmap_scope_change": False,
            "decision_required": False,
            "technology_activation": False,
            "provider_activation": False,
            "deployment_effect": "none",
            "reconcile": ["capability-map", "vertical-slices", "readme"],
            "capability_scope_append": {"public-web": "new evidence."},
            "vertical_slice_note": "PR #88 done.",
            "readme_note": "VS-03c verified.",
        }

    def test_parse_metadata(self):
        body = "x\n<!-- songchart-reconcile " + json.dumps(self.metadata()) + " -->"
        self.assertEqual(reconcile.parse_metadata(body)["slice"], "VS-03")

    def test_decision_bearing_metadata_fails_closed(self):
        meta = self.metadata()
        meta["decision_required"] = True
        self.assertIn(
            "decision_required must be false for automatic reconciliation",
            reconcile.validate_metadata(meta),
        )

    def test_apply_is_idempotent_and_retains_evidence_history(self):
        meta = self.metadata()
        files = reconcile.apply(self.root, meta, self.pr, ["Roadmap health #1"])
        self.assertEqual(set(files), {
            "governance/CAPABILITY_MAP.json",
            "docs/roadmap/VERTICAL_SLICES.md",
            "README.md",
        })
        data = json.loads((self.root / "governance/CAPABILITY_MAP.json").read_text())
        cap = data["capabilities"][0]
        self.assertEqual(cap["verification_evidence"]["pr"], 88)
        self.assertEqual([item["pr"] for item in cap["verification_history"]], [81, 88])
        self.assertEqual(reconcile.apply(self.root, meta, self.pr, ["Roadmap health #1"]), [])

    def test_candidate_promotion_is_rejected(self):
        meta = self.metadata()
        meta["lifecycle_effects"] = {"future": "implemented"}
        with self.assertRaisesRegex(ValueError, "cannot promote from candidate"):
            reconcile.apply(self.root, meta, self.pr, [])


if __name__ == "__main__":
    unittest.main()
