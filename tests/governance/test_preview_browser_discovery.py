"""Offline policy tests for zero-input protected Preview selection."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from preview_browser_discovery import DiscoveryBlocked, choose_ready_preview, discover

NOW = 1794300000000
HOST = "songchart-next-preview-i14zptt45-fusumivietnam.vercel.app"


def candidate(created=NOW - 1000, **overrides):
    result = {"uid": "dpl_Abc123", "url": HOST, "created": created,
              "readyState": "READY", "target": None,
              "meta": {"githubCommitSha": "a" * 40, "githubRepo": "SongChart-Next",
                       "githubOrg": "fusumivietnam"}}
    return {**result, **overrides}


class DiscoveryTests(unittest.TestCase):
    def test_newest_matching_ready_preview_selected(self):
        older = candidate(created=NOW - 3000, uid="dpl_Older123")
        newer = candidate()
        self.assertEqual(choose_ready_preview([older, newer], now_ms=NOW),
                         ("https://" + HOST, "dpl_Abc123", "a" * 40))

    def test_ambiguous_or_untrusted_candidates_fail_closed(self):
        bad = [
            candidate(target="production"),
            candidate(readyState="BUILDING"),
            candidate(url="evil.test"),
            candidate(meta={"githubCommitSha": "a" * 40, "githubRepo": "SongChart"}),
            candidate(created=NOW - 31 * 24 * 60 * 60 * 1000),
        ]
        for item in bad:
            with self.subTest(item=item), self.assertRaises(DiscoveryBlocked):
                choose_ready_preview([item], now_ms=NOW)
        with self.assertRaisesRegex(DiscoveryBlocked, "AMBIGUOUS"):
            choose_ready_preview([candidate(), candidate(uid="dpl_Other123")], now_ms=NOW)
        with self.assertRaises(DiscoveryBlocked):
            choose_ready_preview([], now_ms=NOW)

    def test_never_skips_exact_control_plane_verification(self):
        import json
        body = json.dumps({"deployments": [candidate()]}).encode()

        class Response:
            status = 200
            headers = {"Content-Type": "application/json"}

            def geturl(self):
                return "https://api.vercel.com/v6/deployments?projectId=prj_JTUUiO0Hb3QwiK7w6NWmvxwej43E&teamId=team_Abc123&limit=20"

            def read(self, _limit):
                return body

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

        class Opener:
            def open(self, request, timeout):
                self.request = request
                return Response()

        opener = Opener()
        with patch("preview_browser_discovery.fetch_verified_deployment") as verified:
            result = discover(api_token="fixture", team_id="team_Abc123", opener=opener, now_ms=NOW)
        self.assertEqual(result, ("https://" + HOST, "dpl_Abc123", "a" * 40))
        verified.assert_called_once()
        self.assertEqual(opener.request.get_header("Authorization"), "Bearer fixture")


if __name__ == "__main__":
    unittest.main()
