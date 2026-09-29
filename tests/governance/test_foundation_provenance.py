"""Foundation provenance report regression tests (stdlib only)."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "foundation_provenance.py"
spec = importlib.util.spec_from_file_location("foundation_provenance", MODULE_PATH)
prov = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prov)


class FoundationProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.old_root, self.old_dockerfile, self.old_compose = prov.ROOT, prov.DOCKERFILE, prov.COMPOSE
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "docs/engineering").mkdir(parents=True)
        (root / "Dockerfile").write_text(
            "FROM php:8.4-fpm-bookworm AS php-runtime\n"
            "FROM composer:2 AS composer-bin\n"
            "FROM php-runtime AS production\n",
            encoding="utf-8",
        )
        (root / "compose.yaml").write_text("services:\n  db:\n    image: postgres:18.6\n", encoding="utf-8")
        (root / "composer.lock").write_text(json.dumps({
            "content-hash": "abc",
            "packages": [
                {"name": "laravel/framework", "version": "v13.1.2"},
                {"name": "inertiajs/inertia-laravel", "version": "v3.0.0"},
            ],
            "packages-dev": [],
        }), encoding="utf-8")
        (root / "pnpm-lock.yaml").write_text(
            "lockfileVersion: '9.0'\n"
            "importers:\n"
            "  .:\n"
            "    dependencies:\n"
            "      react:\n"
            "        specifier: ^19.2.0\n"
            "        version: 19.3.0\n"
            "      vite:\n"
            "        specifier: ^8.0.0\n"
            "        version: 8.3.1\n",
            encoding="utf-8",
        )
        (root / "docs/engineering/UPSTREAM_STARTER.md").write_text(
            "Pinned Git commit: \`717b8f55aefd82d25d4119eaebdc8e3a72b8d7e5\`.\n",
            encoding="utf-8",
        )
        prov.ROOT = root
        prov.DOCKERFILE = root / "Dockerfile"
        prov.COMPOSE = root / "compose.yaml"

    def tearDown(self):
        prov.ROOT, prov.DOCKERFILE, prov.COMPOSE = self.old_root, self.old_dockerfile, self.old_compose
        self.tmp.cleanup()

    def test_external_container_images_only(self):
        refs = [x["reference"] for x in prov.dockerfile_images()]
        self.assertEqual(refs, ["php:8.4-fpm-bookworm", "composer:2"])
        self.assertEqual(prov.compose_postgres(), "postgres:18.6")

    def test_starter_revision(self):
        self.assertEqual(prov.starter_revision(), "717b8f55aefd82d25d4119eaebdc8e3a72b8d7e5")

    def test_lockfile_authority_parsing(self):
        composer = prov.parse_composer()
        pnpm = prov.parse_pnpm()
        self.assertEqual(composer["content_hash"], "abc")
        self.assertEqual(composer["selected"]["laravel/framework"], "v13.1.2")
        self.assertEqual(pnpm["lockfile_version"], "9.0")
        self.assertEqual(pnpm["selected"]["react"], "19.3.0")
        self.assertEqual(pnpm["selected"]["vite"], "8.3.1")


if __name__ == "__main__":
    unittest.main()
