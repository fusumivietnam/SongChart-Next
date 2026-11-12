"""No-network contract for the reviewed-candidate protected browser runner."""
import sys
import os
import unittest
from contextlib import redirect_stdout
from io import StringIO
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
    def test_zero_input_discovers_and_partial_input_fails_closed(self):
        env = {"VERCEL_API_READ_TOKEN": "fixture", "VERCEL_TEAM_ID": "team_Abc123",
               "VERCEL_AUTOMATION_BYPASS_SECRET": "fixture"}
        with patch.dict(os.environ, env, clear=True), \
             patch.object(sys, "argv", ["probe", "--chrome", "/fixture/chrome"]), \
             patch.object(runner, "discover", return_value=(ORIGIN, "dpl_Abc123", SHA)) as discovery, \
             patch.object(runner, "run_probe") as probe:
            self.assertEqual(runner.main(), 0)
        discovery.assert_called_once()
        probe.assert_called_once()
        with patch.dict(os.environ, {**env, "DEPLOYMENT_URL": ORIGIN}, clear=True), \
             patch.object(sys, "argv", ["probe", "--chrome", "/fixture/chrome"]), \
             patch.object(runner, "discover") as discovery, \
             patch.object(runner, "run_probe") as probe:
            self.assertEqual(runner.main(), 1)
        discovery.assert_not_called()
        probe.assert_not_called()

    def test_handoff_stays_in_process_at_two_viewports(self):
        events = []
        output = StringIO()
        fake_playwright = SimpleNamespace(sync_playwright=lambda: FakePlaywright(events))
        with patch.dict(sys.modules, {"playwright": SimpleNamespace(sync_api=fake_playwright),
                                      "playwright.sync_api": fake_playwright}), \
             patch.object(runner, "bootstrap", return_value=COOKIE) as bootstrap, \
             patch.object(runner, "install_isolated_cookie", side_effect=lambda _c, _o, _k: events.append("cookie")):
            with redirect_stdout(output):
                runner.run_probe(origin=ORIGIN, deployment_id="dpl_Abc123", expected_sha=SHA,
                                 secret="fixture", api_token="fixture", team_id="fixture", chrome="/fixture/chrome")
        phases = output.getvalue()
        for name in ("chromium-launch-started", "chromium-launched", "mobile-guard-and-cookie-installed",
                     "mobile-navigation-started", "mobile-navigation-returned", "mobile-viewport-verified",
                     "desktop-guard-and-cookie-installed", "desktop-navigation-started",
                     "desktop-navigation-returned", "desktop-viewport-verified"):
            self.assertIn("PROTECTED PREVIEW PHASE: " + name, phases)
        self.assertNotIn(ORIGIN, phases)
        self.assertNotIn("fixture-only", phases)
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
