"""Network-free Bash/curl tests. Python is used by CI, not Codespaces shell."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/codespaces_public_read.sh"
ROUTES = ("/health", "/", "/search?q=Signals", "/corrections", "/about", "/privacy", "/terms", "/disclaimer", "/support")

class CodespacesPublicReadTests(unittest.TestCase):
    def run_fixture(self, health='{"status":"ok"}', html="200|text/html; charset=UTF-8", fail_path=None):
        with tempfile.TemporaryDirectory() as temp:
            stub = Path(temp) / "curl"
            calls = Path(temp) / "calls"
            stub.write_text("""#!/usr/bin/env bash
set -euo pipefail
url=''
body=0
for arg in "$@"; do
  [[ "$arg" == http://127.0.0.1:8000/* ]] && url="$arg"
  [[ "$arg" == '--output' ]] && body=1
done
[[ -n "$url" ]] || exit 3
printf '%s\\n' "$url" >> "$CALLS"
if [[ "$url" == "$FAIL_PATH" ]]; then exit 22; fi
if [[ "$body" == 0 ]]; then
  printf '%s\\n200|application/json' "$HEALTH"
else
  printf '%s' "$HTML"
fi
""", encoding="utf-8")
            stub.chmod(0o755)
            env = dict(os.environ, PATH=temp + os.pathsep + os.environ.get("PATH", ""), CALLS=str(calls),
                       HEALTH=health, HTML=html, FAIL_PATH="http://127.0.0.1:8000" + fail_path if fail_path else "")
            proc = subprocess.run(["bash", str(SCRIPT)], env=env, text=True, capture_output=True, timeout=15)
            urls = calls.read_text(encoding="utf-8").splitlines() if calls.exists() else []
            return proc, urls

    def test_loopback_get_allowlist_and_no_host_python(self):
        proc, urls = self.run_fixture()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(urls, ["http://127.0.0.1:8000" + route for route in ROUTES])
        self.assertIn("CODESPACES READ 08: PASS", proc.stdout)
        self.assertNotIn("http://", proc.stdout)
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("python", source.lower())
        self.assertNotIn("--location", source)
        self.assertIn("--output /dev/null", source)

    def test_fail_closed(self):
        for health in ('{"status":"unavailable"}', '{"status":"ok","extra":1}'):
            proc, _ = self.run_fixture(health=health)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("CODESPACES READ 00: FAIL", proc.stdout)
            self.assertNotIn(health, proc.stdout)
        for html in ("503|text/html", "302|text/html", "200|application/json"):
            proc, _ = self.run_fixture(html=html)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("CODESPACES READ 01: FAIL", proc.stdout)
        proc, urls = self.run_fixture(fail_path="/privacy")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(len(urls), len(ROUTES))
        self.assertIn("CODESPACES READ 05: FAIL", proc.stdout)
        self.assertNotIn("http://", proc.stdout)

if __name__ == "__main__":
    unittest.main()
