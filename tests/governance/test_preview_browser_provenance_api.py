"""No-network regression tests for authenticated Vercel provenance lookup."""
import importlib.util
import json
from pathlib import Path
from unittest.mock import Mock
import unittest

source = Path(__file__).resolve().parents[2] / "scripts" / "preview_browser_provenance.py"
spec = importlib.util.spec_from_file_location("preview_browser_provenance_api", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ORIGIN = "https://songchart-next-preview-i14zptt45-fusumivietnam.vercel.app"
SHA = "248d2d2235861415d0f16a6539e63313c85a6e48"
ID = "dpl_CWpB5crLyTRswaguC972opHKUgCW"
TEAM = "team_5fFxHCbJCkt0A0QxO86NLgLB"
RECORD = {"id": ID, "url": ORIGIN.removeprefix("https://"), "target": None,
          "readyState": "READY",
          "project": {"id": "prj_JTUUiO0Hb3QwiK7w6NWmvxwej43E"},
          "meta": {"githubCommitSha": SHA, "githubRepo": "SongChart-Next",
                   "githubOrg": "fusumivietnam"}}


class Response:
    def __init__(self, url, data=RECORD, status=200, content_type="application/json"):
        self.url = url
        self.status = status
        self.headers = {"Content-Type": content_type}
        self.body = json.dumps(data).encode()

    def geturl(self):
        return self.url

    def read(self, length):
        return self.body[:length]

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class VercelApiTests(unittest.TestCase):
    def _lookup(self, opener, **kwargs):
        return module.fetch_verified_deployment(
            ORIGIN, ID, SHA, api_token="fixture-only", team_id=TEAM,
            opener=opener, **kwargs)

    def test_exact_authenticated_api_response(self):
        opener = Mock()
        url = "https://api.vercel.com/v13/deployments/" + ID + "?teamId=" + TEAM
        opener.open.return_value = Response(url)
        self.assertEqual(self._lookup(opener)["id"], ID)
        request = opener.open.call_args.args[0]
        self.assertEqual(request.full_url, url)
        self.assertEqual(request.get_header("Authorization"), "Bearer fixture-only")

    def test_rejects_missing_token_before_network(self):
        opener = Mock()
        with self.assertRaises(ValueError):
            module.fetch_verified_deployment(ORIGIN, ID, SHA,
                                             api_token="", team_id=TEAM, opener=opener)
        opener.open.assert_not_called()

    def test_rejects_off_origin_and_non_json(self):
        opener = Mock()
        for response in (Response("https://evil.test"),
                         Response("https://api.vercel.com/other"),
                         Response("https://api.vercel.com/v13/deployments/" + ID +
                                  "?teamId=" + TEAM, content_type="text/html")):
            opener.open.return_value = response
            with self.assertRaises(ValueError):
                self._lookup(opener)

    def test_rejects_malformed_identifiers_without_network(self):
        for deployment, team in (("dpl_", TEAM), ("dpl_valid/evil", TEAM), (ID, "team_"), (ID, "team_x?token=bad")):
            opener = Mock()
            with self.subTest(deployment=deployment, team=team), self.assertRaises(ValueError):
                module.fetch_verified_deployment(ORIGIN, deployment, SHA,
                    api_token="fixture-only", team_id=team, opener=opener)
            opener.open.assert_not_called()

    def test_rejects_jsonp_mime(self):
        opener = Mock()
        url = "https://api.vercel.com/v13/deployments/" + ID + "?teamId=" + TEAM
        opener.open.return_value = Response(url, content_type="application/jsonp")
        with self.assertRaises(ValueError):
            self._lookup(opener)

    def test_rejects_wrong_source(self):
        opener = Mock()
        url = "https://api.vercel.com/v13/deployments/" + ID + "?teamId=" + TEAM
        opener.open.return_value = Response(url, {**RECORD, "readyState": "BUILDING"})
        with self.assertRaises(ValueError):
            self._lookup(opener)


if __name__ == "__main__":
    unittest.main()
