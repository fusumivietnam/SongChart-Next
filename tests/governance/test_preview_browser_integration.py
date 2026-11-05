"""End-to-end offline proof that Vercel provenance gates the secret-bearing request.

Uses two entirely mocked HTTP transports. No tokens or network are used.
"""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from preview_browser_bootstrap import bootstrap

ORIGIN = "https://songchart-next-preview-i14zptt45-fusumivietnam.vercel.app"
SHA = "248d2d2235861415d0f16a6539e63313c85a6e48"
ID = "dpl_CWpB5crLyTRswaguC972opHKUgCW"
TEAM = "team_5fFxHCbJCkt0A0QxO86NLgLB"
API_URL = "https://api.vercel.com/v13/deployments/" + ID + "?teamId=" + TEAM
RECORD = {"id": ID, "url": ORIGIN.removeprefix("https://"), "target": None,
          "readyState": "READY",
          "project": {"id": "prj_JTUUiO0Hb3QwiK7w6NWmvxwej43E"},
          "meta": {"githubCommitSha": SHA, "githubRepo": "SongChart-Next",
                   "githubOrg": "fusumivietnam"}}


class Response:
    def __init__(self, url, body=b"", headers=None, status=200):
        self.url = url
        self.body = body
        self.status = status
        self.headers = headers or {}

    def geturl(self):
        return self.url

    def read(self, size):
        return self.body[:size]

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class IntegratedBootstrapTests(unittest.TestCase):
    def run_bootstrap(self, record):
        api = Mock()
        web = Mock()
        api.open.return_value = Response(API_URL, json.dumps(record).encode(),
                                         {"Content-Type": "application/json"})
        cookie = "_vercel_jwt=fixture-cookie; Path=/; Secure; HttpOnly; SameSite=Lax"
        headers = Mock()
        headers.get_all.return_value = [cookie]
        web.open.return_value = Response(ORIGIN + "/", headers=headers)
        error = None
        result = None
        try:
            result = bootstrap(ORIGIN, ID, SHA, "fixture-bypass",
                               api_token="fixture-vercel", team_id=TEAM,
                               control_plane_opener=api, opener=web)
        except ValueError as exc:
            error = exc
        return api, web, result, error

    def test_exact_provider_record_before_scoped_bypass(self):
        api, web, cookie, error = self.run_bootstrap(RECORD)
        self.assertIsNone(error)
        self.assertEqual(api.open.call_args.args[0].full_url, API_URL)
        self.assertEqual(web.open.call_args.args[0].full_url, ORIGIN + "/")
        self.assertEqual(cookie["domain"], ORIGIN.removeprefix("https://"))
        self.assertNotIn("fixture-vercel", str(web.open.call_args))
        self.assertNotIn("fixture-bypass", str(api.open.call_args))

    def test_mismatched_sha_never_sends_bypass(self):
        api, web, cookie, error = self.run_bootstrap({
            **RECORD, "meta": {**RECORD["meta"], "githubCommitSha": "0" * 40}})
        self.assertIsInstance(error, ValueError)
        self.assertIsNone(cookie)
        api.open.assert_called_once()
        web.open.assert_not_called()

    def test_production_target_never_sends_bypass(self):
        api, web, cookie, error = self.run_bootstrap({**RECORD, "target": "production"})
        self.assertIsInstance(error, ValueError)
        web.open.assert_not_called()


if __name__ == "__main__":
    unittest.main()
