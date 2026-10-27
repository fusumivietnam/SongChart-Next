"""Keep Archify optional and outside SongChart application/runtime authority."""

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
ARCHIFY_COMMIT = "208acba8d412335185b2056fedf54b3405df43fb"
EXAMPLE_COMMIT = "600162d4b0bc531485d8df685c42745cb13baca6"
CATALOG_COMMIT = "cc31819fd074ec7d5f1e4d1b79cfdcbbf2c7e673"


class ArchifyDeveloperToolContractTest(unittest.TestCase):
    def test_registry_is_conditionally_approved_developer_analysis(self):
        registry = json.loads((ROOT / "governance/TECHNOLOGY_REGISTRY.json").read_text())
        archify, = [item for item in registry["technologies"] if item["id"] == "archify"]
        self.assertEqual(archify["capability"], "developer-analysis")
        self.assertEqual(archify["status"], "approved")
        self.assertIn(ARCHIFY_COMMIT, archify["version_authority"])
        self.assertIn("THIRD_PARTY_NOTICES.md", archify["license_review"])
        decision = (ROOT / "docs/adr/ADR-0017-archify-developer-visualization.md").read_text()
        self.assertIn("approved with conditions", decision)
        self.assertIn("cannot automatically alter canonical data", decision)

    def test_pinned_opt_in_installer_is_not_in_bootstrap(self):
        installer = (ROOT / ".devcontainer/install-archify.sh").read_text()
        self.assertIn(ARCHIFY_COMMIT, installer)
        self.assertIn('ARCHIFY_TARGET="$ARCHIFY_AGENT_SKILLS/archify"', installer)
        self.assertIn("Refusing to overwrite", installer)
        for path in (".devcontainer/post-create.sh", ".devcontainer/prebuild.sh", ".devcontainer/post-start.sh"):
            self.assertNotIn("install-archify", (ROOT / path).read_text())

    def test_example_keeps_historical_source_identity(self):
        example = json.loads((ROOT / "docs/architecture/examples/archify-public-read.architecture.json").read_text())
        self.assertEqual(example["meta"]["repository"]["revision"], EXAMPLE_COMMIT)
        self.assertTrue(all(node.get("sources") for node in example["components"]))
        self.assertEqual(example["meta"]["quality_profile"], "showcase")
        self.assertIn(EXAMPLE_COMMIT, (ROOT / "scripts/archify_example.sh").read_text())

    def test_disposable_ci_browser_gate_preserves_opt_in_boundary(self):
        workflow = (ROOT / ".github/workflows/archify-browser-contract.yml").read_text()
        for required in ("pull_request:", "workflow_dispatch:", "fetch-depth: 0", "browser-check", "scripts/archify_example.sh"):
            self.assertIn(required, workflow)
        self.assertIn("scripts/archify_catalog_example.sh", workflow)
        self.assertIn("'songchart-catalog-core'", workflow)
        self.assertIn("${example}.finalize.json", workflow)
        for forbidden in ("secrets.", "upload-artifact", "push:", "contents: write"):
            self.assertNotIn(forbidden, workflow)
        self.assertIn("archify-browser-contract.yml", (ROOT / "docs/operations/CI_WORKFLOW_OWNERSHIP.md").read_text())

    def test_catalog_erd_is_historical_source_backed_and_bounded(self):
        example = json.loads((ROOT / "docs/architecture/examples/archify-catalog-core.erd.json").read_text())
        self.assertEqual(example["diagram_type"], "erd")
        self.assertEqual(example["meta"]["repository"]["revision"], CATALOG_COMMIT)
        self.assertEqual(example["meta"]["quality_profile"], "standard")
        self.assertTrue(all(entity.get("sources") for entity in example["entities"]))
        entities = {entity["id"] for entity in example["entities"]}
        self.assertEqual(entities, {"release_groups", "releases", "release_media", "release_tracks", "recordings"})
        for entity in example["entities"]:
            for attribute in entity["attributes"]:
                if "fk" in ([attribute.get("key")] if isinstance(attribute.get("key"), str) else attribute.get("key", [])):
                    self.assertIn(attribute["references"].split(".")[0], entities)
        self.assertIn(CATALOG_COMMIT, (ROOT / "scripts/archify_catalog_example.sh").read_text())


if __name__ == "__main__":
    unittest.main()
