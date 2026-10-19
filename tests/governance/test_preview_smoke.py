from __future__ import annotations

import importlib.util
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "preview_smoke.py"
spec = importlib.util.spec_from_file_location("preview_smoke", MODULE_PATH)
assert spec and spec.loader
preview_smoke = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = preview_smoke
spec.loader.exec_module(preview_smoke)


class Handler(BaseHTTPRequestHandler):
    health_calls = 0
    invalid_content_type = False

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            type(self).health_calls += 1
            if type(self).health_calls == 1:
                self.send_response(503)
                self.send_header("Retry-After", "0")
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json" if type(self).invalid_content_type else "text/html; charset=utf-8")
        self.send_header("X-Robots-Tag", "noindex, nofollow")
        self.end_headers()
        self.wfile.write(b"<html><body>ok</body></html>")

    def log_message(self, format: str, *args: object) -> None:
        return


class PreviewSmokeContractTest(unittest.TestCase):
    def setUp(self) -> None:
        Handler.health_calls = 0
        Handler.invalid_content_type = False
        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_smoke_retries_bootstrap_then_checks_all_preview_routes(self) -> None:
        origin = f"http://127.0.0.1:{self.server.server_port}"
        results = preview_smoke.run_smoke(origin, attempts=3, sleep=lambda _: None)

        self.assertEqual(12, len(results))
        self.assertEqual(2, Handler.health_calls)
        self.assertEqual(
            ["health", "home", "search", "artist", "release", "recording", "corrections", "about", "privacy", "terms", "disclaimer", "support"],
            [result.name for result in results],
        )
        self.assertEqual(2, results[0].attempts)
        self.assertTrue(all(result.status == 200 for result in results))

    def test_rejects_non_html_response_even_if_status_and_noindex_are_valid(self) -> None:
        Handler.invalid_content_type = True
        origin = f"http://127.0.0.1:{self.server.server_port}"
        with self.assertRaisesRegex(RuntimeError, "home returned non-HTML content"):
            preview_smoke.run_smoke(origin, attempts=3, sleep=lambda _: None)

    def test_rejects_cross_origin_redirect(self) -> None:
        class RedirectingOpener:
            def open(self, request: object, timeout: int = 20) -> object:
                raise AssertionError("must use mocked request result")

        original = preview_smoke._request
        try:
            def cross_origin(*args: object, **kwargs: object) -> tuple[int, dict[str, str], bytes, int, str]:
                return 200, {"Content-Type": "application/json"}, b'{"status":"ok"}', 1, "https://other.example/health"
            preview_smoke._request = cross_origin
            with self.assertRaisesRegex(RuntimeError, "health redirected outside the preview origin"):
                preview_smoke.run_smoke("https://preview.example")
        finally:
            preview_smoke._request = original

    def test_fixture_routes_are_stable_and_preview_specific(self) -> None:
        paths = [path for _, path, _ in preview_smoke.ROUTES]
        self.assertIn("/search?q=Signals", paths)
        self.assertIn("/artists/01m4xhg00fj3qgdbn34j43731a/aster-echo", paths)
        self.assertIn("/releases/01m4xhg22zj51ctppzfqxe07y1/signals-at-dawn", paths)
        self.assertIn("/recordings/01m4xhg3et77xdjfkhwxedg1qm/signals-at-dawn", paths)
        self.assertIn("/corrections", paths)
        for page in ("/about", "/privacy", "/terms", "/disclaimer", "/support"):
            self.assertIn(page, paths)


if __name__ == "__main__":
    unittest.main()
