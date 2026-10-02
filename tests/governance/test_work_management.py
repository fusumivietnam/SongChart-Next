import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "governance" / "GITHUB_WORK_MANAGEMENT.json"


class WorkManagementContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_identity_and_project_projection(self):
        self.assertEqual(self.data["schema_version"], 1)
        self.assertEqual(self.data["project"], "SongChart-Next")
        project = self.data["github_project"]
        self.assertEqual(project["owner"], "fusumivietnam")
        self.assertEqual(project["number"], 2)
        self.assertEqual(project["authority"], "derived projection only")
        self.assertEqual(
            project["required_fields"],
            ["Slice", "Capability", "Execution", "Gate", "Decision", "Evidence"],
        )

    def test_label_names_are_unique_and_namespaced(self):
        labels = self.data["issue_labels"]["required"]
        names = [item["name"] for item in labels]
        self.assertEqual(len(names), len(set(names)))
        allowed = {"type", "area", "priority", "state", "risk"}
        for name in names:
            namespace, separator, value = name.partition(":")
            self.assertEqual(separator, ":", name)
            self.assertIn(namespace, allowed, name)
            self.assertTrue(value, name)

    def test_priority_and_lifecycle_boundaries(self):
        constraints = self.data["issue_labels"]["constraints"]
        self.assertTrue(constraints["priority_is_human_decision"])
        self.assertEqual(
            constraints["capability_lifecycle_authority"],
            "governance/CAPABILITY_MAP.json",
        )

    def test_agent_profiles_exist_and_are_dormant(self):
        agents = self.data["agents"]
        self.assertEqual(agents["activation"], "dormant-until-eligible-copilot-plan")
        self.assertGreaterEqual(len(agents["profiles"]), 4)
        for relative in agents["profiles"]:
            path = ROOT / relative
            self.assertTrue(path.is_file(), relative)
            text = path.read_text(encoding="utf-8")
            self.assertIn("disable-model-invocation: true", text)
            self.assertIn("dormant-until-eligible-copilot-plan", text)

    def test_required_views_are_unique(self):
        views = self.data["github_project"]["required_views"]
        self.assertEqual(len(views), len(set(views)))
        self.assertIn("Delivery Board", views)
        self.assertIn("Decision Queue", views)


if __name__ == "__main__":
    unittest.main()
