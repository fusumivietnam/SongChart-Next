"""Pilot guardrail regression tests; no browser/network dependency."""

import os
import subprocess
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/agent_browser_pilot.sh"


class AgentBrowserPilotGuardTests(unittest.TestCase):
    def test_rejects_unsafe_origins_and_payloads_before_browser(self):
        for value in (
            "https://127.0.0.1:8000/",
            "http://example.com:8000/",
            "http://127.0.0.1:8000@evil.example/",
            "http://127.0.0.1:8000/?token=secret",
            "http://127.0.0.1:8000/#session",
            "http://127.0.0.1:8000/admin",
            "http://127.0.0.1/",
        ):
            with self.subTest(url=value):
                completed = subprocess.run(["bash", str(SCRIPT), value], capture_output=True, text=True, timeout=5)
                self.assertEqual(completed.returncode, 2)

    def test_local_route_passes_validation_without_browser_installed(self):
        completed = subprocess.run(
            ["bash", str(SCRIPT), "http://127.0.0.1:8000/search"],
            capture_output=True,
            text=True,
            env={**os.environ, "AGENT_BROWSER_BIN": "nonexistent-songchart-browser-cli"},
            timeout=5,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("Install the opt-in", completed.stderr)


if __name__ == "__main__":
    unittest.main()
