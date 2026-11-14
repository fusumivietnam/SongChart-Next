"""Offline network-free checks for the Codespaces public read smoke."""
import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import codespaces_public_read as smoke


class FakeResponse:
    def __init__(self, url, status=200, content_type="text/html", payload=b"UNREAD-SENSITIVE-BODY"):
        self.url, self.status = url, status
        self.headers = {"Content-Type": content_type}
        self.payload = payload
        self.read_calls = 0

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def geturl(self):
        return self.url

    def read(self, n=-1):
        self.read_calls += 1
        return self.payload[:n]


class FakeOpener:
    def __init__(self, overrides=None):
        self.overrides = overrides or {}
        self.seen = []
        self.responses = []

    def open(self, request, timeout):
        self.seen.append((request.full_url, request.get_method(), timeout))
        if request.full_url in self.overrides:
            value = self.overrides[request.full_url]
            if isinstance(value, Exception):
                raise value
            response = value
        elif request.full_url.endswith("/health"):
            response = FakeResponse(request.full_url, content_type="application/json",
                                    payload=b'{"status":"ok"}')
        else:
            response = FakeResponse(request.full_url)
        self.responses.append(response)
        return response


class CodespacesPublicReadTests(unittest.TestCase):
    def test_read_only_allowlist_passes_without_reading_html(self):
        opener = FakeOpener()
        results = smoke.verify(opener)
        self.assertEqual(len(results), len(smoke.HTML_ROUTES) + 1)
        self.assertTrue(all(ok for _path, ok in results))
        self.assertTrue(all(method == "GET" and timeout == 5 and url.startswith(smoke.ORIGIN)
                            for url, method, timeout in opener.seen))
        self.assertTrue(all(resp.read_calls == 0 for resp in opener.responses[1:]))
        self.assertEqual(opener.responses[0].read_calls, 1)

    def test_fail_closed_non200_redirect_malformed_health_and_unavailable(self):
        cases = (
            FakeResponse(smoke.ORIGIN + "/", status=503),
            FakeResponse("https://foreign.example/", status=200),
            FakeResponse(smoke.ORIGIN + "/", content_type="application/json"),
            TimeoutError("secret-bearing error details"),
        )
        for failure in cases:
            with self.subTest(failure=type(failure).__name__):
                opener = FakeOpener({smoke.ORIGIN + "/": failure})
                result = smoke.verify(opener)
                self.assertFalse(result[1][1])
        bad_health = FakeOpener({smoke.ORIGIN + "/health":
            FakeResponse(smoke.ORIGIN + "/health", content_type="application/json",
                         payload=json.dumps({"status": "unavailable"}).encode())})
        self.assertFalse(smoke.verify(bad_health)[0][1])

    def test_output_never_exposes_response_or_origin(self):
        with patch.object(smoke, "verify", return_value=[("/health", False), ("/", True)]):
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(smoke.main(), 1)
        self.assertIn("CODESPACES READ 00: FAIL", stdout.getvalue())
        self.assertNotIn(smoke.ORIGIN, stdout.getvalue())
        self.assertNotIn("/health", stdout.getvalue())
        self.assertNotIn("UNREAD-SENSITIVE-BODY", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
