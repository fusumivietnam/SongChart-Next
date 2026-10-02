import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPS = ROOT / "governance" / "CAPABILITY_MAP.json"
DESIGN = ROOT / "design" / "DESIGN_AUTHORITY.md"
DECISION = ROOT / "design" / "decisions" / "FOUNDATION_BASELINE_APPROVAL.md"
ROADMAP = ROOT / "docs" / "roadmap" / "VERTICAL_SLICES.md"


class DesignAuthorityApprovalTests(unittest.TestCase):
    def test_design_authority_is_approved_without_public_web_promotion(self):
        data = json.loads(CAPS.read_text(encoding="utf-8"))
        caps = {item["id"]: item for item in data["capabilities"]}
        design = caps["design-authority"]
        self.assertEqual(design["status"], "approved")
        self.assertEqual(design["implementation"], "design/DESIGN_AUTHORITY.md")
        self.assertEqual(design["decision"], "design/decisions/FOUNDATION_BASELINE_APPROVAL.md")
        self.assertEqual(caps["public-web"]["status"], "candidate")

    def test_approved_docs_do_not_claim_final_polish_or_product_completion(self):
        authority = DESIGN.read_text(encoding="utf-8")
        decision = DECISION.read_text(encoding="utf-8")
        roadmap = ROADMAP.read_text(encoding="utf-8")
        self.assertIn("Foundation baseline approved", authority)
        self.assertIn("not a final-brand-polish claim", authority)
        self.assertIn("sufficiently consistent, responsive, accessible and stable", decision)
        self.assertIn("does not imply VS-01a implementation", roadmap)
        self.assertNotIn("NOT YET APPROVED", authority)


if __name__ == "__main__":
    unittest.main()
