import subprocess
import sys
import unittest


class CIOwnershipTests(unittest.TestCase):
    def test_repository_ci_ownership_contract(self):
        result = subprocess.run(
            [sys.executable, "scripts/verify_ci_ownership.py"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CI ownership verification passed.", result.stdout)


if __name__ == "__main__":
    unittest.main()
