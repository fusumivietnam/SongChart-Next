from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.scan_tracked_secrets import (
    describe_finding,
    runtime_env_paths,
    scan_file,
    scan_text,
)


class TrackedSecretScanTest(unittest.TestCase):
    def test_detects_high_confidence_credentials_without_exposing_values(self) -> None:
        fixtures = {
            "private": "-----BEGIN " + "PRIVATE KEY-----\nredacted\n",
            "github": "ghp_" + ("A" * 40),
            "aws": "AKIA" + ("A" * 16),
            "stripe": "sk_" + "live_" + ("A" * 20),
            "slack": "xoxb-" + ("A" * 24),
            "openai": "sk-" + ("A" * 24),
            "google": "AIza" + ("A" * 35),
        }

        for name, secret in fixtures.items():
            with self.subTest(name=name):
                findings = scan_text(secret, f"fixture/{name}.txt")
                self.assertTrue(findings)
                rendered = "\n".join(describe_finding(finding) for finding in findings)
                self.assertNotIn(secret, rendered)
                self.assertIn(f"fixture/{name}.txt:1:", rendered)

    def test_runtime_env_files_are_blocked_but_example_is_allowed(self) -> None:
        self.assertEqual(
            [".env", "config/.env.production"],
            runtime_env_paths([".env.example", ".env", "config/.env.production", "README.md"]),
        )

    def test_binary_files_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "binary.dat"
            path.write_bytes(b"prefix\x00ghp_" + (b"A" * 40))
            self.assertEqual([], scan_file(path, "binary.dat"))

    def test_placeholders_do_not_trigger(self) -> None:
        text = "GITHUB_TOKEN=replace-me\nAWS_ACCESS_KEY_ID=example\nSECRET_KEY=not-a-live-token\n"
        self.assertEqual([], scan_text(text, ".env.example"))


if __name__ == "__main__":
    unittest.main()
