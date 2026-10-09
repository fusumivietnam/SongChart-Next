import json
import tempfile
import unittest
from pathlib import Path

from scripts import roadmap_reconcile_health as health


class RoadmapReconcileHealthTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "governance").mkdir()
        (root / "docs/roadmap").mkdir(parents=True)
        (root / "governance/CAPABILITY_MAP.json").write_text('{"capabilities":[]}', encoding="utf-8")
        (root / "docs/roadmap/VERTICAL_SLICES.md").write_text("# x", encoding="utf-8")
        (root / "README.md").write_text("# x", encoding="utf-8")
        self.root = root

    def tearDown(self):
        self.tmp.cleanup()

    def merged_pr(self, number=88):
        meta = {"schema_version": 1, "reconcile": ["capability-map"]}
        return {
            "number": number,
            "merged_at": "2026-10-09T00:00:00Z",
            "body": "<!-- songchart-reconcile " + json.dumps(meta) + " -->",
        }

    def test_unreconciled_merged_pr_is_warning(self):
        report = health.derive(self.root, {
            "status": "known",
            "truncated": False,
            "pull_requests": [self.merged_pr()],
        })
        self.assertEqual(report["findings"][0]["code"], "merged_pr.unreconciled")

    def test_authority_reference_clears_warning(self):
        (self.root / "governance/CAPABILITY_MAP.json").write_text(
            '{"verification_evidence":{"pr":88}}', encoding="utf-8"
        )
        report = health.derive(self.root, {
            "status": "known",
            "truncated": False,
            "pull_requests": [self.merged_pr()],
        })
        self.assertEqual(report["findings"], [])


if __name__ == "__main__":
    unittest.main()
