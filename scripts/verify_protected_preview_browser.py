#!/usr/bin/env python3
"""Reviewed-candidate, manual-only protected Preview browser read probe.

No screenshots, traces, HAR, downloads, response bodies, credentials or URL
are emitted. Failure codes are deliberately constant and non-sensitive.
"""
from __future__ import annotations

import argparse
import os
import sys
import time

from preview_browser_bootstrap import PreflightBlocked, bootstrap
from preview_browser_context import install_isolated_cookie
from preview_browser_discovery import DiscoveryBlocked, discover
from preview_browser_preflight import validate


class BrowserReadBlocked(ValueError):
    """Fixed, non-sensitive read-verification outcome; never embeds page data."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def verify_read_response(response, page) -> None:
    """Validate a read-only viewport without exposing response or DOM content."""
    if response is None:
        raise BrowserReadBlocked("HTTP_RESPONSE_MISSING")
    if response.status >= 400:
        # Deliberately fixed categories; never log exact HTTP status, URL,
        # headers, cookies, response text, or page content.
        status = response.status
        if status in (401, 403):
            code = "HTTP_ACCESS_REJECTED"
        elif status == 404:
            code = "HTTP_NOT_FOUND"
        elif status == 429:
            code = "HTTP_RATE_LIMITED"
        elif 500 <= status < 600:
            code = "HTTP_SERVER_REJECTED"
        else:
            code = "HTTP_OTHER_REJECTED"
        raise BrowserReadBlocked(code)
    if page.locator("body").count() != 1:
        raise BrowserReadBlocked("DOCUMENT_MISSING")
    if page.evaluate("document.documentElement.scrollWidth > innerWidth + 1"):
        raise BrowserReadBlocked("HORIZONTAL_OVERFLOW")


def navigate_with_bootstrap_retry(page, url: str, *,
                                  monotonic=time.monotonic, sleep=time.sleep):
    """Retry only a bounded Preview startup 503; never bypass normal read checks."""
    deadline = monotonic() + 40
    response = None
    for attempt in range(16):
        remaining = deadline - monotonic()
        if remaining <= 0:
            break
        # Every attempt remains a normal browser navigation through the
        # already-installed same-origin guard and host-only cookie.
        response = page.goto(
            url, wait_until="domcontentloaded",
            timeout=max(1000, min(15000, int(remaining * 1000))),
        )
        if response is None or response.status != 503:
            return response
        if attempt == 15 or deadline - monotonic() <= 2:
            break
        sleep(2)
    return response


def run_probe(*, origin: str, deployment_id: str, expected_sha: str,
              secret: str, api_token: str, team_id: str, chrome: str) -> None:
    """Perform one provenance-bound in-memory bootstrap and two read-only visits."""
    normalized = validate(origin, expected_sha, deployment_id, secret_present=bool(secret))
    print("PROTECTED PREVIEW PHASE: input-validated", flush=True)
    # Import only after validating the CLI inputs, on a trusted ephemeral runner.
    from playwright.sync_api import sync_playwright
    cookie = bootstrap(normalized, deployment_id, expected_sha, secret,
                       api_token=api_token, team_id=team_id)
    print("PROTECTED PREVIEW PHASE: provenance-and-cookie-verified", flush=True)
    try:
        with sync_playwright() as playwright:
            print("PROTECTED PREVIEW PHASE: chromium-launch-started", flush=True)
            browser = playwright.chromium.launch(executable_path=chrome, headless=True)
            print("PROTECTED PREVIEW PHASE: chromium-launched", flush=True)
            try:
                for label, width, height in (("mobile", 390, 844), ("desktop", 1440, 1024)):
                    print(f"PROTECTED PREVIEW PHASE: {label}-context-started", flush=True)
                    context = browser.new_context(
                        viewport={"width": width, "height": height},
                        service_workers="block", accept_downloads=False,
                    )
                    try:
                        print(f"PROTECTED PREVIEW PHASE: {label}-context-created", flush=True)
                        install_isolated_cookie(context, normalized, cookie)
                        print(f"PROTECTED PREVIEW PHASE: {label}-guard-and-cookie-installed", flush=True)
                        page = context.new_page()
                        print(f"PROTECTED PREVIEW PHASE: {label}-navigation-started", flush=True)
                        response = navigate_with_bootstrap_retry(page, normalized + "/")
                        print(f"PROTECTED PREVIEW PHASE: {label}-navigation-returned", flush=True)
                        verify_read_response(response, page)
                        # No third-party navigation, form submission or page captures.
                        print(f"PROTECTED PREVIEW PHASE: {label}-viewport-verified", flush=True)
                    finally:
                        context.close()
            finally:
                browser.close()
    finally:
        # The cookie is never serialized or handed to a child process.
        del cookie


def main() -> int:
    parser = argparse.ArgumentParser(description="Manual, protected Preview read-only browser probe")
    parser.add_argument("--chrome", required=True)
    args = parser.parse_args()
    try:
        api_token, team_id = os.environ["VERCEL_API_READ_TOKEN"], os.environ["VERCEL_TEAM_ID"]
        supplied = (os.environ.get("DEPLOYMENT_URL", ""), os.environ.get("DEPLOYMENT_ID", ""),
                    os.environ.get("EXPECTED_SHA", ""))
        if not any(supplied):
            print("PROTECTED PREVIEW PHASE: discovery-started", flush=True)
            origin, deployment_id, expected_sha = discover(api_token=api_token, team_id=team_id)
            print("PROTECTED PREVIEW PHASE: discovery-verified", flush=True)
        elif all(supplied):
            origin, deployment_id, expected_sha = supplied
        else:
            raise ValueError("partial deployment inputs forbidden")
        run_probe(origin=origin, deployment_id=deployment_id,
                  expected_sha=expected_sha,
                  secret=os.environ["VERCEL_AUTOMATION_BYPASS_SECRET"],
                  api_token=api_token, team_id=team_id, chrome=args.chrome)
    except DiscoveryBlocked as error:
        print(f"PROTECTED PREVIEW BROWSER BLOCKED [{error.code}]", file=sys.stderr)
        return 1
    except PreflightBlocked as error:
        print(f"PROTECTED PREVIEW BROWSER BLOCKED [{error.code}]", file=sys.stderr)
        return 1
    except BrowserReadBlocked as error:
        print(f"PROTECTED PREVIEW BROWSER BLOCKED [{error.code}]", file=sys.stderr)
        return 1
    except Exception:
        # Never print exception details: Playwright exceptions can contain URLs.
        print("PROTECTED PREVIEW BROWSER BLOCKED [SAFE_FAILURE]", file=sys.stderr)
        return 1
    print("PROTECTED PREVIEW BROWSER READ PROBE PASS; no artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
