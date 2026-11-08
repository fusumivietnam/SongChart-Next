"""Offline fake-context contract: cookie never reaches foreign requests."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from preview_browser_context import BrowserContextRejected, _is_allowed_request, install_isolated_cookie

ORIGIN = "https://songchart-next-preview-i14zptt45-fusumivietnam.vercel.app"
COOKIE = {"name": "_vercel_jwt", "value": "fixture-only", "domain": ORIGIN[8:],
          "path": "/", "secure": True, "httpOnly": True, "sameSite": "Lax"}


class FakeContext:
    def __init__(self):
        self.routes = []
        self.socket_routes = []
        self.cookies = []
        self.events = []

    def route(self, pattern, handler):
        self.events.append("route")
        self.routes.append((pattern, handler))

    def route_web_socket(self, pattern, handler):
        self.events.append("socket_route")
        self.socket_routes.append((pattern, handler))

    def add_cookies(self, cookies):
        self.events.append("cookies")
        self.cookies.extend(cookies)


class FakeRoute:
    def __init__(self, url, status=200, location=None, fetch_error=False):
        self.request = SimpleNamespace(url=url)
        self.action = None
        self.response = SimpleNamespace(status=status, headers={"location": location} if location else {})
        self.fetch_error = fetch_error
        self.redirect_limit = None

    def fetch(self, *, max_redirects):
        self.redirect_limit = max_redirects
        if self.fetch_error:
            raise RuntimeError("fixture network failure")
        return self.response

    def fulfill(self, *, response):
        assert response is self.response
        self.action = "fulfilled"

    def abort(self):
        self.action = "aborted"


class BrowserContextTests(unittest.TestCase):
    def test_request_guard_supports_tls_loopback_fixture_without_weakening_preview_origin(self):
        self.assertTrue(_is_allowed_request("https://localhost:8765/", "https://localhost:8765"))
        self.assertFalse(_is_allowed_request("https://localhost:8766/", "https://localhost:8765"))
        self.assertFalse(_is_allowed_request("http://localhost:8765/", "https://localhost:8765"))
        self.assertFalse(_is_allowed_request("https://evil.test@localhost:8765/", "https://localhost:8765"))

    def test_installs_guard_before_host_only_cookie(self):
        context = FakeContext()
        install_isolated_cookie(context, ORIGIN, COOKIE)
        self.assertEqual(context.events, ["route", "socket_route", "cookies"])
        self.assertEqual(context.socket_routes[0][0], "**/*")
        socket = SimpleNamespace(close=lambda: context.events.append("socket_closed"))
        context.socket_routes[0][1](socket)
        self.assertEqual(context.events[-1], "socket_closed")
        self.assertEqual(context.cookies[0]["url"], ORIGIN + "/")
        self.assertNotIn("domain", context.cookies[0])
        self.assertEqual(context.routes[0][0], "**/*")

        callback = context.routes[0][1]
        for url, expected in ((ORIGIN + "/search", "fulfilled"),
                              ("https://evil.test/", "aborted"),
                              (ORIGIN.replace("https:", "http:") + "/", "aborted"),
                              ("https://evil.test@" + ORIGIN[8:] + "/", "aborted"),
                              (ORIGIN + ".evil.test/", "aborted")):
            with self.subTest(url=url):
                route = FakeRoute(url)
                callback(route)
                self.assertEqual(route.action, expected)
                self.assertEqual(route.redirect_limit, 0 if expected == "fulfilled" else None)

    def test_redirect_hops_are_checked_before_browser_can_follow(self):
        context = FakeContext()
        install_isolated_cookie(context, ORIGIN, COOKIE)
        callback = context.routes[0][1]
        for location, expected in (("/same-origin", "fulfilled"),
                                   (ORIGIN + "/other", "fulfilled"),
                                   ("https://evil.test/leak", "aborted"),
                                   ("//evil.test/leak", "aborted"),
                                   ("http://" + ORIGIN[8:] + "/leak", "aborted"),
                                   (None, "aborted")):
            with self.subTest(location=location):
                route = FakeRoute(ORIGIN + "/redirect", status=302, location=location)
                callback(route)
                self.assertEqual(route.action, expected)
                self.assertEqual(route.redirect_limit, 0)

        route = FakeRoute(ORIGIN + "/", fetch_error=True)
        callback(route)
        self.assertEqual(route.action, "aborted")

    def test_invalid_origin_and_cookie_never_reach_context(self):
        for origin, cookie in (("https://evil.test", COOKIE),
                               (ORIGIN + "/corrections", COOKIE),
                               (ORIGIN, {**COOKIE, "domain": "evil.test"}),
                               (ORIGIN, {**COOKIE, "secure": False}),
                               (ORIGIN, {**COOKIE, "value": ""}),
                               (ORIGIN, {**COOKIE, "sameSite": "None"})):
            context = FakeContext()
            with self.subTest(origin=origin, cookie=cookie["domain"]), self.assertRaises(BrowserContextRejected):
                install_isolated_cookie(context, origin, cookie)
            self.assertEqual(context.events, [])


if __name__ == "__main__":
    unittest.main()
