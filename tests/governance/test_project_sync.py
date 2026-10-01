import subprocess
import sys
import unittest
from scripts import project_sync as sync

class ProjectSyncTests(unittest.TestCase):
    def test_cli_help_runs_directly(self):
        result = subprocess.run([sys.executable, "scripts/project_sync.py", "--help"], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--owner", result.stdout)

    def test_projection_metadata(self):
        issue = {"body": "**Project Gate:** G2\n**Project Decision:** Approved\n**Verification evidence:** run-123"}
        self.assertEqual(sync.projection_metadata(issue), {"gate": "G2", "decision": "Approved", "verification": "run-123"})

    def test_primary_capability_order(self):
        issue = {"body": "**Capability ID(s):** public-web, canonical-music-core"}
        self.assertEqual(sync.primary_capability(issue, {"public-web", "canonical-music-core"}), "public-web")

    def test_execution_mapping(self):
        report = {
            "work_queue": {
                "ready": [{"issue": 1}],
                "in_progress": [{"issue": 2}],
                "in_review": [{"issue": 3}],
                "blocked": [{"issue": 4}],
            },
            "slices": [{"closed_issues": [{"number": 5}]}],
        }
        self.assertEqual(sync.issue_execution(report), {
            1: "Ready", 2: "In progress", 3: "In review", 4: "Blocked", 5: "Done"
        })

    def test_schema_vocab(self):
        specs = sync.desired_schema()
        self.assertIn("FOUNDATION", specs["Slice"]["options"])
        self.assertIn("Cross-cutting", specs["Slice"]["options"])
        self.assertIn("project-os", specs["Capability"]["options"])
        self.assertEqual(specs["Evidence"]["type"], "TEXT")

if __name__ == "__main__":
    unittest.main()
