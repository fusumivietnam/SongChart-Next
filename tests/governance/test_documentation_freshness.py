from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from docs_generate import render_outputs  # noqa: E402
from docs_verify import verify  # noqa: E402


class DocumentationFreshnessTests(unittest.TestCase):
    def _fixture(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for directory in ("governance", "docs/generated"):
            (root / directory).mkdir(parents=True, exist_ok=True)
        (root / "README.md").write_text("# Fixture\n\n## Project state\nGenerated status only.\n", encoding="utf-8")
        (root / "docs/roadmap").mkdir(parents=True, exist_ok=True)
        (root / "docs/roadmap/VERTICAL_SLICES.md").write_text("fixture\n", encoding="utf-8")
        (root / "governance/ACTIVATION_TRIGGERS.json").write_text("{}\n", encoding="utf-8")
        capabilities = {
            "capabilities": [
                {"id": "public-web", "status": "verified"},
                {"id": "production-deploy", "status": "implemented"},
            ]
        }
        technologies = {
            "technologies": [
                {"id": "docker-compose", "status": "implemented"},
                {"id": "coolify", "status": "watch"},
            ]
        }
        (root / "governance/CAPABILITY_MAP.json").write_text(json.dumps(capabilities), encoding="utf-8")
        (root / "governance/TECHNOLOGY_REGISTRY.json").write_text(json.dumps(technologies), encoding="utf-8")
        registry = {
            "schema_version": 1,
            "projections": {
                "capabilities": ["public-web", "production-deploy"],
                "technologies": ["docker-compose", "coolify"],
            },
            "documents": [
                {
                    "path": "README.md",
                    "mode": "authored",
                    "owner": "project-os",
                    "sources": ["governance/CAPABILITY_MAP.json", "docs/roadmap/VERTICAL_SLICES.md"],
                },
                {
                    "path": "docs/generated/PROJECT_STATUS.md",
                    "mode": "generated",
                    "owner": "project-os",
                    "generator": "project_status_projection",
                    "sources": [
                        "governance/CAPABILITY_MAP.json",
                        "governance/TECHNOLOGY_REGISTRY.json",
                        "docs/roadmap/VERTICAL_SLICES.md",
                    ],
                },
            ],
        }
        (root / "governance/DOCUMENTATION_REGISTRY.json").write_text(json.dumps(registry), encoding="utf-8")
        for relative, content in render_outputs(root).items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return root

    def test_valid_registry_and_generated_projection(self) -> None:
        self.assertEqual([], verify(self._fixture()))

    def test_stale_generated_projection_is_detected(self) -> None:
        root = self._fixture()
        (root / "docs/generated/PROJECT_STATUS.md").write_text("stale\n", encoding="utf-8")
        self.assertIn(
            "stale generated document: docs/generated/PROJECT_STATUS.md",
            verify(root),
        )

    def test_unknown_projected_authority_id_is_detected(self) -> None:
        root = self._fixture()
        path = root / "governance/DOCUMENTATION_REGISTRY.json"
        registry = json.loads(path.read_text(encoding="utf-8"))
        registry["projections"]["capabilities"].append("not-a-capability")
        path.write_text(json.dumps(registry), encoding="utf-8")
        self.assertIn("unknown projected capability: not-a-capability", verify(root))

    def test_readme_mutable_status_markers_are_rejected(self) -> None:
        root = self._fixture()
        (root / "README.md").write_text(
            "# Fixture\n\n## Current status\n<!-- roadmap-reconcile:start -->\nstale\n<!-- roadmap-reconcile:end -->\n",
            encoding="utf-8",
        )
        errors = verify(root)
        self.assertTrue(any("forbidden mutable status marker" in error for error in errors))


    def test_research_probes_reference_existing_repository_paths(self) -> None:
        """Advisory research fixtures must not point to removed project authorities."""
        probes = json.loads((ROOT / "research/cocoindex/questions.json").read_text(encoding="utf-8"))
        for group in ("authority_questions", "impact_probes", "contradiction_probes"):
            for probe in probes[group]:
                for key in ("expect", "expect_any"):
                    for relative in probe.get(key, []):
                        with self.subTest(group=group, path=relative):
                            self.assertTrue((ROOT / relative).exists(), f"stale research probe path: {relative}")

if __name__ == "__main__":
    unittest.main()
