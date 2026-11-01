"""Offline assertions: no redirect following, no secret egress or network use."""
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from preview_browser_bootstrap import bootstrap, RejectRedirect

URL = "https://songchart-next-preview-i14zptt45-fusumivietnam.vercel.app"
SHA = "248d2d2235861415d0f16a6539e63313c85a6e48"
DEPLOYMENT = "dpl_CWpB5crLyTRswaguC972opHKUgCW"
COOKIE = "_vercel_jwt=mock-value; Path=/; Secure; HttpOnly; SameSite=Lax"


class Response:
    status = 200
    def __init__(self, target=URL + "/", cookies=None):
        self.target = target
        self.headers = Mock()
        self.headers.get_all.return_value = [COOKIE] if cookies is None else cookies

    def geturl(self):
        return self.target

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class BootstrapTests(unittest.TestCase):
    def test_scoped_request_and_no_browser_wide_header(self):
        opener = Mock()
        opener.open.return_value = Response()
        result = bootstrap(URL, DEPLOYMENT, SHA, "fixture-secret",
                           provenance_verified=True, opener=opener)
        req = opener.open.call_args.args[0]
        self.assertEqual(req.full_url, URL + "/")
        self.assertEqual(req.get_header("X-vercel-protection-bypass"), "fixture-secret")
        self.assertEqual(req.get_header("X-vercel-set-bypass-cookie"), "true")
        self.assertEqual(result["name"], "_vercel_jwt")
        self.assertEqual(result["domain"], URL.removeprefix("https://"))

    def test_unverified_provenance_never_calls_transport(self):
        opener = Mock()
        with self.assertRaises(ValueError):
            bootstrap(URL, DEPLOYMENT, SHA, "fixture-secret",
                      provenance_verified=False, opener=opener)
        opener.open.assert_not_called()

    def test_wrong_host_never_calls_transport(self):
        opener = Mock()
        with self.assertRaises(ValueError):
            bootstrap("https://evil.test", DEPLOYMENT, SHA, "fixture-secret",
                      provenance_verified=True, opener=opener)
        opener.open.assert_not_called()

    def test_rejects_off_origin_response(self):
        opener = Mock()
        opener.open.return_value = Response("https://evil.test/")
        with self.assertRaises(ValueError):
            bootstrap(URL, DEPLOYMENT, SHA, "fixture-secret",
                      provenance_verified=True, opener=opener)

    def test_redirect_handler_is_fail_closed(self):
        self.assertIsNone(RejectRedirect().redirect_request(None, None, 302, "", {}, "https://evil.test/"))


if __name__ == "__main__":
    unittest.main()
