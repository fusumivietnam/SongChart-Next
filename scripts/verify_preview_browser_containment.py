#!/usr/bin/env python3
"""Opt-in real Chromium loopback egress proof; no Preview or credentials.

Requires hash-locked Python Playwright, an existing Chrome executable, and
openssl. Runs only in a disposable runner; retains no browser artifacts.
"""
from __future__ import annotations

import argparse
import http.server
import ssl
import subprocess
import tempfile
import threading
from pathlib import Path

from preview_browser_context import _install_origin_guard


class FixtureHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.hits.append(self.path)
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", self.server.foreign_origin + "/leak")
            self.end_headers()
            return
        if self.path == "/":
            html = ("<html><body><h1 id='fixture'>Fixture ready</h1>"
                    f"<img src='{self.server.foreign_origin}/asset' alt='external'>"
                    "</body></html>").encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return
        self.send_response(204)
        self.end_headers()

    def log_message(self, *_args):
        pass


def serve(cert: str, key: str):
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
    server.hits = []
    tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    tls.load_cert_chain(cert, key)
    server.socket = tls.wrap_socket(server.socket, server_side=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a no-secret Chromium origin containment fixture")
    parser.add_argument("--chrome", required=True, help="Installed Chrome/Chromium executable")
    args = parser.parse_args()
    from playwright.sync_api import Error as PlaywrightError, sync_playwright

    with tempfile.TemporaryDirectory(prefix="songchart-browser-fixture-") as directory:
        cert, key = str(Path(directory) / "cert.pem"), str(Path(directory) / "key.pem")
        subprocess.run(["openssl", "req", "-x509", "-nodes", "-newkey", "rsa:2048",
                        "-days", "1", "-subj", "/CN=localhost",
                        "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1",
                        "-keyout", key, "-out", cert], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        primary, primary_thread = serve(cert, key)
        foreign, foreign_thread = serve(cert, key)
        primary_origin = f"https://localhost:{primary.server_address[1]}"
        foreign_origin = f"https://localhost:{foreign.server_address[1]}"
        primary.foreign_origin = foreign_origin
        foreign.foreign_origin = foreign_origin
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(executable_path=args.chrome, headless=True)
                try:
                    context = browser.new_context(ignore_https_errors=True,
                                                  service_workers="block", accept_downloads=False)
                    try:
                        _install_origin_guard(context, primary_origin)
                        page = context.new_page()
                        page.goto(primary_origin + "/", wait_until="load", timeout=15000)
                        assert page.locator("#fixture").inner_text() == "Fixture ready"
                        page.evaluate("url => window.open(url, '_blank')", foreign_origin + "/popup")
                        page.evaluate("url => { try { new WebSocket(url); } catch (_) {} }",
                                      foreign_origin.replace("https://", "wss://") + "/socket")
                        try:
                            page.goto(primary_origin + "/redirect", timeout=10000)
                        except PlaywrightError:
                            pass  # Browser must stop at the intercepted external redirect.
                        page.wait_for_timeout(300)
                        assert not foreign.hits, "an external loopback origin received a browser request"
                    finally:
                        context.close()
                finally:
                    browser.close()
        finally:
            primary.shutdown()
            foreign.shutdown()
            primary_thread.join(timeout=5)
            foreign_thread.join(timeout=5)
    print("LOOPBACK BROWSER CONTAINMENT PASS; no credentials or artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
