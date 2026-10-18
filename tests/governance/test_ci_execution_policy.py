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

    def test_public_web_scope_tracks_merged_correction_slices_without_promotion(self):
        import json
        capability_map = json.loads((ROOT / "governance/CAPABILITY_MAP.json").read_text(encoding="utf-8"))
        public_web = next(c for c in capability_map["capabilities"] if c["id"] == "public-web")
        admin = next(c for c in capability_map["capabilities"] if c["id"] == "admin-review")
        scope = public_web["scope"]
        self.assertEqual(public_web["status"], "verified")
        self.assertEqual(admin["status"], "candidate")
        self.assertNotIn("editorial/legal surfaces and the broader MVP public journey remain incomplete", scope)
        self.assertIn("VS-05c (PR #156)", scope)
        self.assertIn("VS-05d (PR #158)", scope)
        self.assertIn("no canonical mutation", scope)
        self.assertIn("production and commercial/live provider activation are not implied", scope)

    def test_approved_prelaunch_gates_do_not_automatically_activate_capabilities(self):
        import json
        charter = (ROOT / "docs/product/PRODUCT_CHARTER.md").read_text(encoding="utf-8")
        roadmap = (ROOT / "docs/roadmap/VERTICAL_SLICES.md").read_text(encoding="utf-8")
        capability_map = json.loads((ROOT / "governance/CAPABILITY_MAP.json").read_text(encoding="utf-8"))
        admin = next(c for c in capability_map["capabilities"] if c["id"] == "admin-review")
        self.assertEqual(admin["status"], "candidate")
        self.assertIn("Authenticated internal approve/reject review is required before MVP public launch", charter)
        self.assertIn("issue #174", charter)
        self.assertIn("issue #175", charter)
        self.assertIn("after product/code freeze", charter)
        self.assertIn("tracked by #173", roadmap)
        self.assertIn("Issue #174", roadmap)
        self.assertIn("Issue #175", roadmap)

    def test_reviewer_policy_is_approved_but_activation_stays_gated(self):
        import json
        policy = (ROOT / "docs/product/CORRECTION_INTAKE_POLICY.md").read_text(encoding="utf-8")
        roadmap = (ROOT / "docs/roadmap/VERTICAL_SLICES.md").read_text(encoding="utf-8")
        capability_map = json.loads((ROOT / "governance/CAPABILITY_MAP.json").read_text(encoding="utf-8"))
        triggers = json.loads((ROOT / "governance/ACTIVATION_TRIGGERS.json").read_text(encoding="utf-8"))
        admin = next(c for c in capability_map["capabilities"] if c["id"] == "admin-review")
        trigger = next(t for t in triggers["triggers"] if t["capability"] == "admin-review")
        self.assertEqual(admin["status"], "candidate")
        self.assertEqual(trigger["condition"], "Real unresolved claims require moderation")
        self.assertIn("One explicitly provisioned internal reviewer", policy)
        self.assertIn("mandatory, confirmed two-factor authentication (2FA)", policy)
        self.assertIn("never updates canonical", policy)
        self.assertIn("Owner-approved reviewer policy", roadmap)
        self.assertIn("never automatically mutates canonical data", roadmap)

    def test_design_samples_follow_existing_authority_and_activation(self):
        inventory = (ROOT / "design/PAGE_ARCHETYPES.md").read_text(encoding="utf-8")
        authority = (ROOT / "design/DESIGN_AUTHORITY.md").read_text(encoding="utf-8")
        samples = (ROOT / "design/MVP_PAGE_SAMPLES.md").read_text(encoding="utf-8")
        self.assertIn("MVP_PAGE_SAMPLES.md", authority)
        self.assertIn("MVP_PAGE_SAMPLES.md", inventory)
        self.assertIn("VS-05c public correction intake implemented/verified", inventory)
        self.assertIn("design candidate only", samples)
        for issue in ("#173", "#174", "#175"):
            self.assertIn(issue, samples)
        self.assertIn("no automatic canonical edit", samples)
        self.assertIn("confirmed 2FA", samples)

    def test_provider_rights_checkpoint_is_non_activating(self):
        policy = (ROOT / "docs/providers/MUSICBRAINZ.md").read_text(encoding="utf-8")
        self.assertIn("Public-data rights evaluation checkpoint", policy)
        self.assertIn("research, not activation", policy)
        self.assertIn("Hosted MusicBrainz Web Service", policy)
        self.assertIn("Core Artist/Release/Release Group/Recording/Work", policy)
        self.assertIn("Exit evidence still missing", policy)
        self.assertIn("commercial/public production remains blocked", policy)

    def test_vs04_operations_trigger_is_bounded(self):
        text = (ROOT / ".github/workflows/vs04-launch-proof.yml").read_text(encoding="utf-8")
        self.assertNotIn("- docs/operations/**", text)
        self.assertGreaterEqual(text.count("- docs/operations/VS04_*.md"), 2)


if __name__ == "__main__":
    unittest.main()
