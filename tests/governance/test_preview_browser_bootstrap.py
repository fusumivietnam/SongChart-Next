"""Offline assertions: no redirect following, no secret egress or network use."""
import sys
import unittest
import urllib.error
from email.message import Message
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from preview_browser_bootstrap import bootstrap, PreflightBlocked, RejectRedirect
from preview_browser_provenance import ApiLookupFailed

URL = "https://songchart-next-preview-i14zptt45-fusumivietnam.vercel.app"
SHA = "248d2d2235861415d0f16a6539e63313c85a6e48"
DEPLOYMENT = "dpl_CWpB5crLyTRswaguC972opHKUgCW"
COOKIE = "_vercel_jwt=mock-value; Path=/; Secure; HttpOnly; SameSite=Lax"
RECORD = {"deployment": {"id": DEPLOYMENT, "url": URL.removeprefix("https://"),
          "target": None, "readyState": "READY",
          "project": {"id": "prj_JTUUiO0Hb3QwiK7w6NWmvxwej43E"},
          "meta": {"githubCommitSha": SHA, "githubRepo": "SongChart-Next",
                   "githubOrg": "fusumivietnam"}}}


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
        control_plane_opener = Mock()
        opener.open.return_value = Response()
        with patch("preview_browser_bootstrap.fetch_verified_deployment", return_value=RECORD):
            result = bootstrap(URL, DEPLOYMENT, SHA, "fixture-secret",
                           api_token="fixture-token", team_id="team_fixture", opener=opener,
                           control_plane_opener=control_plane_opener)
        req = opener.open.call_args.args[0]
        self.assertEqual(req.full_url, URL + "/")
        self.assertEqual(req.get_header("X-vercel-protection-bypass"), "fixture-secret")
        self.assertEqual(req.get_header("X-vercel-set-bypass-cookie"), "true")
        self.assertEqual(result["name"], "_vercel_jwt")
        self.assertEqual(result["domain"], URL.removeprefix("https://"))

    def test_unverified_provenance_never_calls_transport(self):
        opener = Mock()
        control_plane_opener = Mock()
        with self.assertRaises(ValueError):
            bootstrap(URL, DEPLOYMENT, SHA, "fixture-secret",
                      api_token="", team_id="team_fixture", opener=opener,
                      control_plane_opener=control_plane_opener)
        opener.open.assert_not_called()

    def test_wrong_provenance_never_calls_transport(self):
        opener = Mock()
        control_plane_opener = Mock()
        with patch("preview_browser_bootstrap.fetch_verified_deployment", side_effect=ValueError("mismatch")):
            with self.assertRaises(ValueError):
                bootstrap(URL, DEPLOYMENT, SHA, "fixture-secret",
                          api_token="fixture-token", team_id="team_fixture",
                          opener=opener, control_plane_opener=control_plane_opener)
        opener.open.assert_not_called()

    def test_wrong_host_never_calls_transport(self):
        opener = Mock()
        control_plane_opener = Mock()
        with self.assertRaises(ValueError):
            bootstrap("https://evil.test", DEPLOYMENT, SHA, "fixture-secret",
                      api_token="fixture-token", team_id="team_fixture", opener=opener,
                           control_plane_opener=control_plane_opener)
        opener.open.assert_not_called()

    def test_rejects_off_origin_response(self):
        opener = Mock()
        control_plane_opener = Mock()
        opener.open.return_value = Response("https://evil.test/")
        with patch("preview_browser_bootstrap.fetch_verified_deployment", return_value=RECORD):
            with self.assertRaises(ValueError):
                bootstrap(URL, DEPLOYMENT, SHA, "fixture-secret",
                      api_token="fixture-token", team_id="team_fixture", opener=opener,
                           control_plane_opener=control_plane_opener)

    def test_redirect_handler_is_fail_closed(self):
        self.assertIsNone(RejectRedirect().redirect_request(None, None, 302, "", {}, "https://evil.test/"))

    def test_safe_input_classification_never_calls_transport(self):
        opener = Mock()
        with self.assertRaises(PreflightBlocked) as caught:
            bootstrap("https://evil.test", DEPLOYMENT, SHA, "fixture-secret",
                      api_token="fixture-token", team_id="team_fixture", opener=opener)
        self.assertEqual(caught.exception.code, "INPUT_INVALID")
        opener.open.assert_not_called()

    def test_safe_api_classification_never_sends_bypass(self):
        opener = Mock()
        with patch("preview_browser_bootstrap.fetch_verified_deployment",
                   side_effect=ApiLookupFailed("sensitive fixture detail")):
            with self.assertRaises(PreflightBlocked) as caught:
                bootstrap(URL, DEPLOYMENT, SHA, "fixture-secret",
                          api_token="fixture-token", team_id="team_fixture", opener=opener)
        self.assertEqual(caught.exception.code, "API_LOOKUP_FAILED")
        self.assertNotIn("sensitive", str(caught.exception))
        opener.open.assert_not_called()

    def test_safe_provenance_classification_never_sends_bypass(self):
        opener = Mock()
        with patch("preview_browser_bootstrap.fetch_verified_deployment",
                   side_effect=ValueError("sensitive fixture detail")):
            with self.assertRaises(PreflightBlocked) as caught:
                bootstrap(URL, DEPLOYMENT, SHA, "fixture-secret",
                          api_token="fixture-token", team_id="team_fixture", opener=opener)
        self.assertEqual(caught.exception.code, "PROVENANCE_REJECTED")
        opener.open.assert_not_called()

    def test_safe_bypass_and_cookie_classification(self):
        opener = Mock()
        with patch("preview_browser_bootstrap.fetch_verified_deployment", return_value=RECORD):
            opener.open.side_effect = urllib.error.HTTPError(URL, 403, "denied", {}, None)
            with self.assertRaises(PreflightBlocked) as denied:
                bootstrap(URL, DEPLOYMENT, SHA, "fixture-secret",
                          api_token="fixture-token", team_id="team_fixture", opener=opener)
            self.assertEqual(denied.exception.code, "BYPASS_REJECTED")
            opener.open.side_effect = urllib.error.URLError("unreachable")
            with self.assertRaises(PreflightBlocked) as unavailable:
                bootstrap(URL, DEPLOYMENT, SHA, "fixture-secret",
                          api_token="fixture-token", team_id="team_fixture", opener=opener)
            self.assertEqual(unavailable.exception.code, "BYPASS_UNAVAILABLE")
            opener.open.side_effect = None
            opener.open.return_value = Response(cookies=[])
            with self.assertRaises(PreflightBlocked) as invalid:
                bootstrap(URL, DEPLOYMENT, SHA, "fixture-secret",
                          api_token="fixture-token", team_id="team_fixture", opener=opener)
            self.assertEqual(invalid.exception.code, "COOKIE_INVALID")

    def test_accepts_vercel_same_origin_redirect_cookie_without_following(self):
        for code in (302, 303, 307, 308):
            for location in ("/", URL + "/"):
                with self.subTest(code=code, location=location):
                    headers = Message()
                    headers.add_header("Location", location)
                    headers.add_header("Set-Cookie", COOKIE)
                    opener = Mock()
                    opener.open.side_effect = urllib.error.HTTPError(URL + "/", code, "redirect", headers, None)
                    with patch("preview_browser_bootstrap.fetch_verified_deployment", return_value=RECORD):
                        cookie = bootstrap(URL, DEPLOYMENT, SHA, "fixture-secret",
                                           api_token="fixture-token", team_id="team_fixture", opener=opener)
                    self.assertEqual(cookie["name"], "_vercel_jwt")
                    opener.open.assert_called_once()

    def test_rejects_external_or_ambiguous_redirect_without_following(self):
        for location in ("https://evil.test/", "//evil.test/", "/corrections", "/?token=example", ""):
            with self.subTest(location=location):
                headers = Message()
                if location:
                    headers.add_header("Location", location)
                headers.add_header("Set-Cookie", COOKIE)
                opener = Mock()
                opener.open.side_effect = urllib.error.HTTPError(URL + "/", 307, "redirect", headers, None)
                with patch("preview_browser_bootstrap.fetch_verified_deployment", return_value=RECORD):
                    with self.assertRaises(PreflightBlocked) as blocked:
                        bootstrap(URL, DEPLOYMENT, SHA, "fixture-secret",
                                  api_token="fixture-token", team_id="team_fixture", opener=opener)
                self.assertEqual(blocked.exception.code, "BYPASS_REJECTED")
                opener.open.assert_called_once()

    def test_rejects_redirect_missing_cookie(self):
        headers = Message()
        headers.add_header("Location", "/")
        opener = Mock()
        opener.open.side_effect = urllib.error.HTTPError(URL + "/", 307, "redirect", headers, None)
        with patch("preview_browser_bootstrap.fetch_verified_deployment", return_value=RECORD):
            with self.assertRaises(PreflightBlocked) as blocked:
                bootstrap(URL, DEPLOYMENT, SHA, "fixture-secret",
                          api_token="fixture-token", team_id="team_fixture", opener=opener)
        self.assertEqual(blocked.exception.code, "COOKIE_INVALID")


if __name__ == "__main__":
    unittest.main()
