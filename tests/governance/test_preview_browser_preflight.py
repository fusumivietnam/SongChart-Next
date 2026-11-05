"""No network, token disclosure, or browser launch in these tests."""
import importlib.util
import pathlib
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "preview_browser_preflight.py"
spec = importlib.util.spec_from_file_location("preview_browser_preflight", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

URL = "https://songchart-next-preview-i14zptt45-fusumivietnam.vercel.app"
SHA = "248d2d2235861415d0f16a6539e63313c85a6e48"
DEPLOYMENT = "dpl_CWpB5crLyTRswaguC972opHKUgCW"


class PreviewBrowserPreflightTests(unittest.TestCase):
    def test_exact_valid_input(self):
        self.assertEqual(module.validate(URL, SHA, DEPLOYMENT, secret_present=True), URL)
        self.assertEqual(module.validate(URL + "/", SHA, DEPLOYMENT, secret_present=True), URL)

    def test_unsafe_origins(self):
        for url in (URL.replace("https:", "http:"), URL + "/corrections",
                    URL + "?token=anything", URL + "#fragment",
                    URL.replace(".vercel.app", ".vercel.app.evil.test"),
                    "https://songchart-next-preview-fusumivietnam.vercel.app",
                    "https://user:pass@" + URL.split("://")[1],
                    URL + ":443", URL + "//evil", URL.upper()):
            with self.subTest(url=url), self.assertRaises(ValueError):
                module.validate(url, SHA, DEPLOYMENT, secret_present=True)

    def test_incorrect_sha_and_deployment(self):
        for sha in ("", SHA[:7], SHA.upper(), "x"*40):
            with self.subTest(sha=sha), self.assertRaises(ValueError):
                module.validate(URL, sha, DEPLOYMENT, secret_present=True)
        for deployment in ("", "dpl_", "dpl_abc/../xyz", "production"):
            with self.subTest(deployment=deployment), self.assertRaises(ValueError):
                module.validate(URL, SHA, deployment, secret_present=True)

    def test_missing_credential(self):
        with self.assertRaisesRegex(ValueError, "credential"):
            module.validate(URL, SHA, DEPLOYMENT, secret_present=False)


if __name__ == "__main__":
    unittest.main()
