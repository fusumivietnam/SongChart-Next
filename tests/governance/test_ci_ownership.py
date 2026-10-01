import subprocess
import sys
import unittest
from pathlib import Path


class CiOwnershipTest(unittest.TestCase):
    def test_ci_ownership_contract(self) -> None:
        root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            [sys.executable, "scripts/verify_ci_ownership.py"],
            cwd=root,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
