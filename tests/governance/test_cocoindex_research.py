import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class CocoIndexResearchBoundaryTests(unittest.TestCase):
    def test_research_is_registered_but_not_technology_activated(self):
        research = json.loads((ROOT / "governance/RESEARCH_REGISTRY.json").read_text(encoding="utf-8"))
        record = next(item for item in research["research"] if item["id"] == "RES-0002")
        self.assertEqual(record["status"], "registered")
        self.assertEqual(record["capability_ids"], ["project-os"])
        self.assertIsNone(record["decision_ref"])

        technology = json.loads((ROOT / "governance/TECHNOLOGY_REGISTRY.json").read_text(encoding="utf-8"))
        ids = {item["id"] for item in technology["technologies"]}
        self.assertNotIn("cocoindex", ids)

    def test_spike_dependency_and_revision_are_pinned(self):
        requirements = (ROOT / "research/cocoindex/requirements.txt").read_text(encoding="utf-8")
        self.assertEqual(requirements.strip(), "cocoindex[sqlite,sentence_transformers]==1.0.25")
        note = (ROOT / "docs/research/RES-0002-cocoindex-repository-context.md").read_text(encoding="utf-8")
        self.assertIn("17c84f1a0f9bc5b0b4e1d8ebabb28bde79c4afa3", note)
        self.assertIn("Apache-2.0", note)
        self.assertIn("disposable derived data", note)

    def test_semantic_quality_is_not_a_merge_blocking_decision(self):
        workflow = (ROOT / ".github/workflows/research-cocoindex.yml").read_text(encoding="utf-8")
        self.assertIn("merge_blocking_semantic_judgement", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("TECHNOLOGY_REGISTRY", workflow)


if __name__ == "__main__":
    unittest.main()
