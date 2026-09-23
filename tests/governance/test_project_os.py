"""Regressions for project-authority link and lifecycle integrity (stdlib only)."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import verify_project_os as verify


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.original_root, self.original_gov = verify.ROOT, verify.GOV
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "governance").mkdir()
        self.root.joinpath("governance").joinpath("CAPABILITY_MAP.json").write_text(json.dumps({
            "schema_version": 1, "project": "SongChart-Next",
            "capabilities": [{"id": "project-os", "owner": "songchart", "status": "candidate",
                              "depends_on": [], "implementation": None}]}))
        self.root.joinpath("governance").joinpath("TECHNOLOGY_REGISTRY.json").write_text(json.dumps({
            "schema_version": 1, "project": "SongChart-Next",
            "technologies": [{"id": "tech", "capability": "project-os", "status": "candidate",
                              "source": "https://example.org/tech"}]}))
        self.root.joinpath("governance").joinpath("ACTIVATION_TRIGGERS.json").write_text(json.dumps({
            "schema_version": 1, "project": "SongChart-Next", "triggers": []}))
        self.root.joinpath("governance").joinpath("RESEARCH_REGISTRY.json").write_text(json.dumps({
            "schema_version": 1, "project": "SongChart-Next", "research": []}))
        self.root.joinpath("governance").joinpath("INFRASTRUCTURE_REGISTRY.json").write_text(json.dumps({
            "schema_version": 1, "project": "SongChart-Next", "instances": []}))
        for ref in ("AGENTS.md", "docs/product/PRODUCT_CHARTER.md", "docs/architecture/ARCHITECTURE.md",
                    "design/DESIGN_AUTHORITY.md", "reference/README.md", "docs/roadmap/VERTICAL_SLICES.md",
                    "docs/engineering/DELIVERY_CONTRACT.md", "docs/operations/ACCEPTANCE_GATES.md",
                    "docs/operations/DEPENDENCY_POLICY.md", "docs/operations/ENVIRONMENT_POLICY.md",
                    "docs/research/README.md", "governance/schemas/research.schema.json",
                    "governance/schemas/infrastructure.schema.json"):
            p = self.root / ref
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("test")
        verify.ROOT = self.root
        verify.GOV = self.root / "governance"

    def tearDown(self):
        verify.ROOT, verify.GOV = self.original_root, self.original_gov
        self.tmp.cleanup()

    def edit(self, name, mutate):
        path = self.root / "governance" / name
        data = json.loads(path.read_text())
        mutate(data)
        path.write_text(json.dumps(data))

    def test_valid_bootstrap(self):
        verify.verify()

    def test_reject_duplicate_research_id(self):
        self.edit("RESEARCH_REGISTRY.json", lambda d: d["research"].extend([
            {"id": "RES-0001", "title": "sample", "source": "https://example.org/research",
             "status": "registered", "capability_ids": [], "decision_ref": None, "superseded_by": None}
        ] * 2))
        with self.assertRaisesRegex(ValueError, "duplicate research"):
            verify.verify()

    def test_reject_unknown_capability(self):
        self.edit("RESEARCH_REGISTRY.json", lambda d: d["research"].append(
            {"id": "RES-0001", "title": "sample", "source": "https://example.org/research",
             "status": "registered", "capability_ids": ["missing"], "decision_ref": None, "superseded_by": None}))
        with self.assertRaisesRegex(ValueError, "invalid capabilities"):
            verify.verify()

    def test_reject_fabricated_verified(self):
        self.edit("CAPABILITY_MAP.json", lambda d: d["capabilities"][0].update(
            status="verified", implementation="AGENTS.md"))
        with self.assertRaisesRegex(ValueError, "no verification evidence"):
            verify.verify()

    def test_reject_unlinked_runtime(self):
        self.edit("INFRASTRUCTURE_REGISTRY.json", lambda d: d["instances"].append({
            "id": "local-db", "capability_id": "missing", "technology_id": "tech",
            "environment": "development", "status": "approved",
            "configuration_ref": "AGENTS.md", "runtime_owner": "songchart",
            "data_classification": "local", "secrets_ref": None,
            "backup_policy_ref": None, "recovery_policy_ref": None,
            "failure_mode": "unavailable", "operational_evidence": []}))
        with self.assertRaisesRegex(ValueError, "unknown capability"):
            verify.verify()

    def test_reject_path_traversal(self):
        with self.assertRaisesRegex(ValueError, "invalid local reference|missing/unsafe local file"):
            verify.local_file("../AGENTS.md")


if __name__ == "__main__":
    unittest.main()
