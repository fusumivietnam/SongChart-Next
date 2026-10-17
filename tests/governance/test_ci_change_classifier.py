import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("classify_ci_change", ROOT / "scripts/classify_ci_change.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class CiChangeClassifierTests(unittest.TestCase):
    def test_governance_metadata_does_not_imply_runtime(self):
        result = MODULE.classify(["governance/TECHNOLOGY_REGISTRY.json"])
        self.assertTrue(result["governance"])
        self.assertFalse(result["application"])
        self.assertFalse(result["provider"])
        self.assertFalse(result["developer_environment"])
        self.assertFalse(result["production_package"])

    def test_provider_change_is_provider_and_application(self):
        result = MODULE.classify(["app/Music/Providers/MusicBrainz/MusicBrainzArtistClient.php"])
        self.assertTrue(result["provider"])
        self.assertTrue(result["application"])

    def test_production_compose_hits_database_and_production_package(self):
        result = MODULE.classify(["compose.production.yaml"])
        self.assertTrue(result["database"])
        self.assertTrue(result["production_package"])

    def test_frontend_change_hits_visual_and_application(self):
        result = MODULE.classify(["resources/js/pages/home/index.tsx"])
        self.assertTrue(result["frontend"])
        self.assertTrue(result["visual"])
        self.assertTrue(result["application"])

    def test_docs_only_is_not_application(self):
        result = MODULE.classify(["docs/operations/GITHUB_USAGE_GUARDRAILS.md"])
        self.assertTrue(result["documentation"])
        self.assertFalse(result["application"])
        self.assertFalse(result["production_package"])

    def test_preview_runtime_paths_are_classified_separately(self):
        result = MODULE.classify(["Dockerfile.vercel", "deploy/vercel/start.sh", "scripts/preview_smoke.py"])
        self.assertTrue(result["preview_runtime"])

    def test_governance_branch_rejects_runtime_change(self):
        violations = MODULE.preview_skip_branch_violation(
            "governance/runtime-mistake",
            ["governance/CAPABILITY_MAP.json", "app/Http/Controllers/HomeController.php"],
        )
        self.assertIn("application", violations)

    def test_docs_branch_allows_docs_only_change(self):
        violations = MODULE.preview_skip_branch_violation(
            "docs/preview-copy",
            ["docs/operations/VERCEL_PREVIEW.md"],
        )
        self.assertEqual(set(), violations)

    def test_regular_branch_is_not_blocked_by_preview_skip_assertion(self):
        violations = MODULE.preview_skip_branch_violation(
            "feature/runtime-change",
            ["app/Http/Controllers/HomeController.php"],
        )
        self.assertEqual(set(), violations)


if __name__ == "__main__":
    unittest.main()
