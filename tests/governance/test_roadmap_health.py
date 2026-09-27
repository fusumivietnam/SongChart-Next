"""Roadmap controller regressions: authority is derived, never promoted from Issue/Project state."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts import roadmap_health as health


class RoadmapHealthTests(unittest.TestCase):
    def setUp(self):
        self.old_root, self.old_gov, self.old_roadmap = health.ROOT, health.GOV, health.ROADMAP
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        gov = root / "governance"
        gov.mkdir(parents=True)
        (root / "docs/roadmap").mkdir(parents=True)
        (root / "docs/roadmap/VERTICAL_SLICES.md").write_text(
            "# Vertical slices\n\n## FOUNDATION — build\n\n## VS-01a — Artist\n\n## VS-01b — live\n",
            encoding="utf-8",
        )
        (gov / "CAPABILITY_MAP.json").write_text(json.dumps({
            "schema_version": 1,
            "project": "SongChart-Next",
            "capabilities": [
                {"id": "project-os", "status": "implemented", "implementation": "governance/", "depends_on": []},
                {"id": "canonical-music-core", "status": "candidate", "implementation": None, "depends_on": []},
            ],
        }), encoding="utf-8")
        (gov / "ACTIVATION_TRIGGERS.json").write_text(json.dumps({
            "schema_version": 1, "project": "SongChart-Next", "triggers": []
        }), encoding="utf-8")
        (gov / "TECHNOLOGY_REGISTRY.json").write_text(json.dumps({
            "schema_version": 1, "project": "SongChart-Next", "technologies": []
        }), encoding="utf-8")
        (gov / "RESEARCH_REGISTRY.json").write_text(json.dumps({
            "schema_version": 1, "project": "SongChart-Next", "research": []
        }), encoding="utf-8")
        health.ROOT, health.GOV, health.ROADMAP = root, gov, root / "docs/roadmap/VERTICAL_SLICES.md"

    def tearDown(self):
        health.ROOT, health.GOV, health.ROADMAP = self.old_root, self.old_gov, self.old_roadmap
        self.tmp.cleanup()

    def test_parses_stable_slice_ids(self):
        self.assertEqual(health.parse_slices(), ["FOUNDATION", "VS-01A", "VS-01B"])

    def test_offline_is_unknown_not_guessed(self):
        report = health.derive({"status": "unknown", "reason": "offline", "issues": [], "pull_requests": []})
        self.assertEqual(report["live_github"]["status"], "unknown")
        self.assertTrue(any(f["code"] == "live.unknown" for f in report["findings"]))
        self.assertEqual(report["active_execution"], [])

    def test_open_foundation_issue_blocks_later_slice_conservatively(self):
        live = {
            "status": "known",
            "truncated": False,
            "pull_requests": [],
            "issues": [{
                "number": 10,
                "title": "FOUNDATION: runtime",
                "body": "**Slice ID:** FOUNDATION\n**Capability ID(s):** project-os",
                "state": "open",
                "html_url": "https://example.test/issues/10",
            }],
        }
        report = health.derive(live)
        self.assertEqual(report["active_execution"][0]["slice"], "FOUNDATION")
        self.assertEqual({x["slice"] for x in report["blocked_slices"]}, {"VS-01A", "VS-01B"})

    def test_closed_issue_does_not_promote_capability_or_count_active(self):
        live = {
            "status": "known",
            "truncated": False,
            "pull_requests": [],
            "issues": [{
                "number": 11,
                "title": "[VS-01a] Artist contract",
                "body": "**Slice ID:** VS-01a\n**Capability ID(s):** canonical-music-core",
                "state": "closed",
                "html_url": "https://example.test/issues/11",
            }],
        }
        report = health.derive(live)
        self.assertEqual(report["active_execution"], [])
        cap = json.loads((health.GOV / "CAPABILITY_MAP.json").read_text())["capabilities"][1]
        self.assertEqual(cap["status"], "candidate")

    def test_verified_without_evidence_is_controller_error(self):
        path = health.GOV / "CAPABILITY_MAP.json"
        data = json.loads(path.read_text())
        data["capabilities"][1].update(status="verified", implementation="app", verification_evidence=None)
        path.write_text(json.dumps(data), encoding="utf-8")
        report = health.derive({"status": "known", "truncated": False, "issues": [], "pull_requests": []})
        self.assertTrue(any(f["code"] == "capability.missing_verification_evidence" for f in report["findings"]))
        self.assertGreater(report["summary"]["error"], 0)

    def test_unlinked_research_issue_is_info_not_roadmap_failure(self):
        live = {
            "status": "known",
            "truncated": False,
            "pull_requests": [],
            "issues": [{
                "number": 12,
                "title": "Research: multilingual aliases",
                "body": "Research only",
                "state": "open",
                "html_url": "https://example.test/issues/12",
            }],
        }
        report = health.derive(live)
        self.assertTrue(any(f["code"] == "issue.unlinked_open" and f["severity"] == "info" for f in report["findings"]))
        self.assertEqual(report["summary"]["error"], 0)


if __name__ == "__main__":
    unittest.main()
