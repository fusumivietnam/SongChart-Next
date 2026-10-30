"""Offline, synthetic Vercel control-plane provenance contract tests."""
import copy
import importlib.util
from pathlib import Path
import unittest

source = Path(__file__).resolve().parents[2] / "scripts" / "preview_browser_provenance.py"
spec = importlib.util.spec_from_file_location("preview_browser_provenance", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ORIGIN = "https://songchart-next-preview-i14zptt45-fusumivietnam.vercel.app"
SHA = "248d2d2235861415d0f16a6539e63313c85a6e48"
ID = "dpl_CWpB5crLyTRswaguC972opHKUgCW"
RECORD = {"deployment": {
    "id": ID, "url": ORIGIN.removeprefix("https://"), "target": None,
    "readyState": "READY", "project": {"id": "prj_JTUUiO0Hb3QwiK7w6NWmvxwej43E"},
    "meta": {"githubCommitSha": SHA, "githubRepo": "SongChart-Next",
             "githubOrg": "fusumivietnam"}}}


class DeploymentProvenanceTests(unittest.TestCase):
    def test_exact_control_plane_record(self):
        module.verify_deployment(RECORD, origin=ORIGIN, deployment_id=ID, expected_sha=SHA)

    def test_invalid_fields_fail_closed(self):
        changes = (
            ("id", "dpl_other"), ("url", "attacker.example"),
            ("target", "production"), ("readyState", "BUILDING"),
        )
        for key, value in changes:
            record = copy.deepcopy(RECORD)
            record["deployment"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                module.verify_deployment(record, origin=ORIGIN, deployment_id=ID, expected_sha=SHA)

    def test_wrong_repository_project_or_commit(self):
        for group, key, value in (
            ("project", "id", "prj_other"),
            ("meta", "githubCommitSha", "0" * 40),
            ("meta", "githubRepo", "SongChart"),
            ("meta", "githubOrg", "another-owner"),
        ):
            record = copy.deepcopy(RECORD)
            record["deployment"][group][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                module.verify_deployment(record, origin=ORIGIN, deployment_id=ID, expected_sha=SHA)

    def test_missing_provenance(self):
        for record in ({}, {"deployment": None}, {"deployment": {"meta": {}}}):
            with self.assertRaises(ValueError):
                module.verify_deployment(record, origin=ORIGIN, deployment_id=ID, expected_sha=SHA)


if __name__ == "__main__":
    unittest.main()
