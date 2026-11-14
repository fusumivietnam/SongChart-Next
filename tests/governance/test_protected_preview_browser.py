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

    def test_read_response_failure_codes_are_fixed_and_do_not_expose_page_data(self):
        cases = (
            (None, 1, False, "HTTP_RESPONSE_MISSING"),
            (SimpleNamespace(status=401), 1, False, "HTTP_ACCESS_REJECTED"),
            (SimpleNamespace(status=403), 1, False, "HTTP_ACCESS_REJECTED"),
            (SimpleNamespace(status=404), 1, False, "HTTP_NOT_FOUND"),
            (SimpleNamespace(status=429), 1, False, "HTTP_RATE_LIMITED"),
            (SimpleNamespace(status=503), 1, False, "HTTP_SERVER_REJECTED"),
            (SimpleNamespace(status=418), 1, False, "HTTP_OTHER_REJECTED"),
            (SimpleNamespace(status=200), 0, False, "DOCUMENT_MISSING"),
            (SimpleNamespace(status=200), 1, True, "HORIZONTAL_OVERFLOW"),
        )
        for response, body_count, overflow, expected in cases:
            with self.subTest(expected=expected, response=response):
                page = SimpleNamespace(
                    locator=lambda _selector: SimpleNamespace(count=lambda: body_count),
                    evaluate=lambda _expression: overflow,
                )
                with self.assertRaises(runner.BrowserReadBlocked) as raised:
                    runner.verify_read_response(response, page)
                self.assertEqual(raised.exception.code, expected)
                self.assertNotIn(ORIGIN, str(raised.exception))
                self.assertNotIn("fixture-only", str(raised.exception))

    def test_bootstrap_503_is_retried_only_on_same_origin_and_stops_on_success(self):
        clock = [0]
        statuses = [503, 503, 200]
        seen = []
        def goto(url, **kwargs):
            seen.append((url, kwargs))
            return SimpleNamespace(status=statuses.pop(0))
        page = SimpleNamespace(goto=goto)
        result = runner.navigate_with_bootstrap_retry(
            page, ORIGIN + "/", monotonic=lambda: clock[0],
            sleep=lambda seconds: clock.__setitem__(0, clock[0] + seconds),
        )
        self.assertEqual(result.status, 200)
        self.assertEqual(len(seen), 3)
        self.assertEqual(clock[0], 4)
        self.assertTrue(all(url == ORIGIN + "/" for url, _kwargs in seen))
        self.assertTrue(all(kwargs["wait_until"] == "domcontentloaded" for _url, kwargs in seen))
        self.assertTrue(all(kwargs["timeout"] <= 15000 for _url, kwargs in seen))

    def test_bootstrap_retries_are_bounded_and_other_errors_are_not_retried(self):
        for first_status in (None, 401, 403, 404, 429, 500, 502, 504):
            with self.subTest(first_status=first_status):
                calls = []
                def goto(url, **kwargs):
                    calls.append(url)
                    return None if first_status is None else SimpleNamespace(status=first_status)
                result = runner.navigate_with_bootstrap_retry(
                    SimpleNamespace(goto=goto), ORIGIN + "/",
                    monotonic=lambda: 0, sleep=lambda _seconds: self.fail("unwanted retry"),
                )
                self.assertEqual(len(calls), 1)
                self.assertEqual(result.status if result is not None else None, first_status)

        clock = [0]
        calls = []
        def goto_503(url, **kwargs):
            calls.append((url, kwargs["timeout"]))
            return SimpleNamespace(status=503)
        result = runner.navigate_with_bootstrap_retry(
            SimpleNamespace(goto=goto_503), ORIGIN + "/",
            monotonic=lambda: clock[0],
            sleep=lambda seconds: clock.__setitem__(0, clock[0] + seconds),
        )
        self.assertEqual(result.status, 503)
        self.assertEqual(len(calls), 16)
        self.assertEqual(clock[0], 30)
        self.assertTrue(all(url == ORIGIN + "/" for url, _timeout in calls))
        with self.assertRaises(runner.BrowserReadBlocked) as raised:
            runner.verify_read_response(result, None)
        self.assertEqual(raised.exception.code, "HTTP_SERVER_REJECTED")

    def test_successful_read_response_has_no_extra_side_effects(self):
        page = SimpleNamespace(
            locator=lambda _selector: SimpleNamespace(count=lambda: 1),
            evaluate=lambda _expression: False,
        )
        self.assertIsNone(runner.verify_read_response(SimpleNamespace(status=200), page))


if __name__ == "__main__":
    unittest.main()
