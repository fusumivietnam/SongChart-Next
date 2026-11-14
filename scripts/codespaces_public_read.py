#!/usr/bin/env python3
"""Read-only loopback public route smoke for the existing Codespaces Compose app.

Never prints response bodies, credentials, forwarded URLs, or user data.
Database fixtures and browser acceptance remain owned by existing CI.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

ORIGIN = "http://127.0.0.1:8000"
HTML_ROUTES = (
    "/", "/search?q=Signals", "/corrections", "/about", "/privacy",
    "/terms", "/disclaimer", "/support",
)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def verify(opener=None) -> list[tuple[str, bool]]:
    transport = opener or urllib.request.build_opener(NoRedirect())
    checks = (("/health", "health"),) + tuple((path, "html") for path in HTML_ROUTES)
    outcomes = []
    for path, kind in checks:
        ok = False
        try:
            request = urllib.request.Request(ORIGIN + path, method="GET")
            with transport.open(request, timeout=5) as response:
                content_type = response.headers.get("Content-Type", "").split(";", 1)[0].lower().strip()
                if response.status == 200 and response.geturl() == ORIGIN + path:
                    if kind == "health" and content_type == "application/json":
                        ok = json.loads(response.read(65)) == {"status": "ok"}
                    elif kind == "html" and content_type == "text/html":
                        ok = True
                # No HTML body is read, printed, or retained.
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
                ValueError, UnicodeError, json.JSONDecodeError):
            pass
        outcomes.append((path.split("?", 1)[0], ok))
    return outcomes


def main() -> int:
    results = verify()
    for index, (_path, passed) in enumerate(results):
        # Fixed test IDs, not request origins, URL values, or response bodies.
        print(f"CODESPACES READ {index:02d}: {'PASS' if passed else 'FAIL'}")
    if not all(passed for _path, passed in results):
        print("CODESPACES PUBLIC READ SMOKE FAILED; inspect local Compose health.")
        return 1
    print("CODESPACES PUBLIC READ SMOKE PASS; local read-only only, no browser or release acceptance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
