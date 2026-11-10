"""No-network contract for the reviewed-candidate protected browser runner."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import verify_protected_preview_browser as runner

ORIGIN = "https://songchart-next-preview-i14zptt45-fusumivietnam.vercel.app"
SHA = "a" * 40
COOKIE = {"name": "_vercel_jwt", "value": "fixture-only", "domain": ORIGIN[8:],
          "path": "/", "secure": True, "httpOnly": True, "sameSite": "Lax"}


class FakeContext:
    def __init__(self, events):
        self.events = events

    def close(self):
        self.events.append("context_closed")

    def new_page(self):
        events = self.events

        class Page:
            def goto(self, url, **kwargs):
                events.append("goto:" + url)
                return SimpleNamespace(status=200)

            def locator(self, selector):
                return SimpleNamespace(count=lambda: 1)

            def evaluate(self, expression):
                return False

        return Page()


class FakeBrowser:
    def __init__(self, events):
        self.events = events

    def new_context(self, **kwargs):
        self.events.append("context:" + str(kwargs["viewport"]["width"]))
        assert kwargs["service_workers"] == "block"
        assert kwargs["accept_downloads"] is False
        return FakeContext(self.events)

    def close(self):
        self.events.append("browser_closed")


class FakePlaywright:
    def __init__(self, events):
        self.chromium = SimpleNamespace(launch=lambda **kwargs: FakeBrowser(events))

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class ProtectedPreviewRunnerTests(unittest.TestCase):
    def test_handoff_stays_in_process_at_two_viewports(self):
        events = []
        fake_playwright = SimpleNamespace(sync_playwright=lambda: FakePlaywright(events))
        with patch.dict(sys.modules, {"playwright": SimpleNamespace(sync_api=fake_playwright),
                                      "playwright.sync_api": fake_playwright}), \
             patch.object(runner, "bootstrap", return_value=COOKIE) as bootstrap, \
             patch.object(runner, "install_isolated_cookie", side_effect=lambda _c, _o, _k: events.append("cookie")):
            runner.run_probe(origin=ORIGIN, deployment_id="dpl_Abc123", expected_sha=SHA,
                             secret="fixture", api_token="fixture", team_id="fixture", chrome="/fixture/chrome")
        self.assertEqual(bootstrap.call_count, 1)
        self.assertEqual(events, ["context:390", "cookie", "goto:" + ORIGIN + "/",
                                  "context_closed", "context:1440", "cookie",
                                  "goto:" + ORIGIN + "/", "context_closed", "browser_closed"])

    def test_bad_origin_never_bootstraps_or_starts_browser(self):
        with patch.object(runner, "bootstrap") as bootstrap, self.assertRaises(ValueError):
            runner.run_probe(origin="https://evil.test", deployment_id="dpl_Abc123", expected_sha=SHA,
                             secret="fixture", api_token="fixture", team_id="fixture", chrome="/fixture/chrome")
        bootstrap.assert_not_called()


if __name__ == "__main__":
    unittest.main()
