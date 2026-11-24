"""#174 deterministic, network-free synthetic sample/coverage regression."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/evaluate_musicbrainz_synthetic_coverage.py"


def evaluate():
    spec = importlib.util.spec_from_file_location("synthetic_quality", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.evaluate()


class MusicBrainzSyntheticQualityTest(unittest.TestCase):
    def test_fixed_stratified_eight_group_census_and_metrics(self):
        report = evaluate()
        self.assertEqual(report["groups"], {"covered": 8, "planned": 8})
        self.assertEqual(report["entity_types"], {"represented": 7, "required": 7})
        self.assertEqual(report["relationship_types"], {"represented": 6, "required": 6})
        self.assertEqual(report["graph_links"]["resolved"], report["graph_links"]["total"])
        self.assertGreater(report["graph_links"]["total"], 0)
        self.assertEqual(report["outcomes"], {
            "evaluation_only": 5,
            "evaluation_with_admission_blocked": 1,
            "quarantine": 2,
        })
        self.assertEqual(report["strata"], {
            "full-journey": 1,
            "identity-and-relationship-complexity": 4,
            "negative-and-rights-gates": 3,
        })
        for key in ("actual_provider_rows_evaluated", "full_application_journeys_verified",
                    "rights_cleared_groups", "canonical_admissions"):
            self.assertEqual(report[key], 0)
        self.assertIn("synthetic", report["scope"])
        self.assertEqual(report, evaluate())


if __name__ == "__main__":
    unittest.main()
