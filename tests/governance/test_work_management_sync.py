import unittest
from scripts import work_management_sync as sync


class WorkManagementSyncTests(unittest.TestCase):
    def test_label_plan_creates_and_repairs_only_declared(self):
        current = [
            {"name": "type:bug", "description": "old", "color": "ffffff"},
            {"name": "unmanaged", "description": "leave me", "color": "000000"},
        ]
        desired = {
            "type:bug": {"name": "type:bug", "description": "Bug", "color": "d73a4a"},
            "type:feature": {"name": "type:feature", "description": "Feature", "color": "1f883d"},
        }
        plan = sync.label_changes(current, desired)
        self.assertEqual(
            [(action, name) for action, name, _ in plan],
            [("update", "type:bug"), ("create", "type:feature")],
        )
        self.assertNotIn("unmanaged", [name for _, name, _ in plan])

    def test_milestones_are_explicit_only(self):
        contract = {"milestones": {"managed": []}}
        self.assertEqual(sync.desired_milestones(contract), {})

    def test_milestone_plan_does_not_delete_unmanaged(self):
        current = [{"number": 1, "title": "Old", "description": "", "state": "open", "due_on": None}]
        desired = {
            "FOUNDATION": {
                "title": "FOUNDATION",
                "description": "Foundation checkpoint",
                "state": "open",
                "due_on": None,
            }
        }
        plan = sync.milestone_changes(current, desired)
        self.assertEqual([(a, n) for a, n, _ in plan], [("create", "FOUNDATION")])

    def test_contract_has_colors_and_no_implicit_milestones(self):
        contract = sync.load_contract()
        labels = contract["issue_labels"]["required"]
        self.assertTrue(labels)
        self.assertTrue(all(len(item["color"]) == 6 for item in labels))
        self.assertEqual(contract["milestones"]["managed"], [])
        self.assertFalse(contract["issue_labels"]["reconciliation"]["delete_unmanaged"])
        self.assertFalse(contract["milestones"]["reconciliation"]["delete_unmanaged"])


if __name__ == "__main__":
    unittest.main()
