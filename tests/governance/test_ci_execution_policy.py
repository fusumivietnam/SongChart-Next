import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class CiExecutionPolicyTests(unittest.TestCase):
    def test_reconciliation_only_listens_to_merged_close_or_dispatch(self):
        text = (ROOT / ".github/workflows/roadmap-reconcile.yml").read_text(encoding="utf-8")
        self.assertIn("types: [closed]", text)
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("types: [closed, edited]", text)
        self.assertNotIn("issue_comment:", text)
        self.assertNotIn("github.event.comment.body", text)

    def test_reconciliation_pr_provenance_uses_source_pr(self):
        text = (ROOT / ".github/workflows/roadmap-reconcile.yml").read_text(encoding="utf-8")
        self.assertIn("Source PR: #${SOURCE_PR}", text)
        self.assertNotIn("Owning Issue / slice / capability: #89 / FOUNDATION / project-os", text)

    def test_classifier_and_atomic_delivery_contract_are_registered(self):
        self.assertTrue((ROOT / "scripts/classify_ci_change.py").is_file())
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        delivery = (ROOT / "docs/engineering/DELIVERY_CONTRACT.md").read_text(encoding="utf-8")
        self.assertIn("AI-authored multi-file work", agents)
        self.assertIn("visible branch history atomic", delivery)

    def test_cross_authority_claims_do_not_regress(self):
        charter = (ROOT / "docs/product/PRODUCT_CHARTER.md").read_text(encoding="utf-8")
        architecture = (ROOT / "docs/architecture/ARCHITECTURE.md").read_text(encoding="utf-8")
        roadmap = (ROOT / "docs/roadmap/ROADMAP_GOVERNANCE.md").read_text(encoding="utf-8")
        self.assertIn("ADR-0015 selects the initial single-VPS Docker production baseline", charter)
        self.assertNotIn("Production deployment platform remains undecided", charter)
        self.assertIn("`governance/CAPABILITY_MAP.json` owns per-capability lifecycle", architecture)
        self.assertNotIn("Status: candidate architecture.", architecture)
        self.assertNotIn("refreshing the concise README status pointer", roadmap)
        self.assertIn("without editing README or generated projections", roadmap)

    def test_vs04_operations_trigger_is_bounded(self):
        text = (ROOT / ".github/workflows/vs04-launch-proof.yml").read_text(encoding="utf-8")
        self.assertNotIn("- docs/operations/**", text)
        self.assertGreaterEqual(text.count("- docs/operations/VS04_*.md"), 2)


if __name__ == "__main__":
    unittest.main()
