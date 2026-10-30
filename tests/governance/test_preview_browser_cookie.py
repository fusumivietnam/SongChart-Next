"""Credential-free regression tests for the bypass cookie contract."""
import importlib.util
from pathlib import Path
import unittest

src = Path(__file__).resolve().parents[2] / "scripts" / "preview_browser_cookie.py"
spec = importlib.util.spec_from_file_location("preview_browser_cookie", src)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ORIGIN = "https://songchart-next-preview-i14zptt45-fusumivietnam.vercel.app"
COOKIE = "_vercel_jwt=fixture-not-a-secret; Path=/; Secure; HttpOnly; SameSite=Lax"


class CookieBootstrapTests(unittest.TestCase):
    def test_accepts_host_only_cookie(self):
        parsed = mod.verify_cookie(ORIGIN, ORIGIN + "/", 200, [COOKIE])
        self.assertEqual(parsed["domain"], "songchart-next-preview-i14zptt45-fusumivietnam.vercel.app")
        self.assertEqual(parsed["name"], "_vercel_jwt")
        self.assertTrue(parsed["secure"])
        self.assertTrue(parsed["httpOnly"])

    def test_rejects_cross_origin_or_cleartext(self):
        for target in ("https://evil.test/", "http://" + ORIGIN.split("://", 1)[1]):
            with self.subTest(target=target), self.assertRaises(ValueError):
                mod.verify_cookie(ORIGIN, target, 302, [COOKIE])

    def test_rejects_unsafe_cookie(self):
        bad = ("_vercel_jwt=value; Domain=.vercel.app; Path=/; Secure; SameSite=Lax",
               "_vercel_jwt=value; Path=/; SameSite=Lax",
               "_vercel_jwt=value; Path=/; Secure; SameSite=None",
               "_vercel_jwt=value; Path=/; Secure; SameSite=Lax",
               "session=value; Path=/; Secure; SameSite=Lax",
               "_vercel_jwt=; Path=/; Secure; SameSite=Lax",
               "_vercel_jwt=value; Path=/corrections; Secure; SameSite=Lax")
        for header in bad:
            with self.subTest(header=header), self.assertRaises(ValueError):
                mod.verify_cookie(ORIGIN, ORIGIN, 200, [header])

    def test_rejects_redirect_status_even_with_cookie(self):
        for status in (301, 302, 303, 307, 308):
            with self.subTest(status=status), self.assertRaises(ValueError):
                mod.verify_cookie(ORIGIN, ORIGIN, status, [COOKIE])

    def test_rejects_missing_or_multiple_headers(self):
        for headers in ([], [COOKIE, COOKIE]):
            with self.assertRaises(ValueError):
                mod.verify_cookie(ORIGIN, ORIGIN, 200, headers)


if __name__ == "__main__":
    unittest.main()
