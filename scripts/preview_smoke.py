#!/usr/bin/env python3
"""Smoke-test a protected SongChart Preview deployment without leaking bodies/secrets."""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable


ROUTES = (
    ("health", "/health", "health"),
    ("home", "/", "html"),
    ("search", "/search?q=Signals", "html"),
    ("artist", "/artists/01m4xhg00fj3qgdbn34j43731a/aster-echo", "html"),
    ("release", "/releases/01m4xhg22zj51ctppzfqxe07y1/signals-at-dawn", "html"),
    ("recording", "/recordings/01m4xhg3et77xdjfkhwxedg1qm/signals-at-dawn", "html"),
    ("corrections", "/corrections", "html"),
)


@dataclass(frozen=True)
class Result:
    name: str
    path: str
    status: int
    attempts: int


def build_opener() -> urllib.request.OpenerDirector:
    jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def authenticate_share_url(opener: urllib.request.OpenerDirector, share_url: str) -> str:
    request = urllib.request.Request(share_url, headers={"User-Agent": "SongChart-Preview-Smoke/1"})
    with opener.open(request, timeout=20) as response:
        final = urllib.parse.urlsplit(response.geturl())
    if final.scheme != "https" or not final.netloc:
        raise RuntimeError("share URL did not resolve to an HTTPS deployment origin")
    return urllib.parse.urlunsplit((final.scheme, final.netloc, "", "", ""))


def _request(
    opener: urllib.request.OpenerDirector,
    url: str,
    *,
    attempts: int,
    sleep: Callable[[float], None],
) -> tuple[int, object, bytes, int, str]:
    for attempt in range(1, attempts + 1):
        request = urllib.request.Request(url, headers={"User-Agent": "SongChart-Preview-Smoke/1"})
        try:
            with opener.open(request, timeout=20) as response:
                return response.status, response.headers, response.read(), attempt, response.geturl()
        except urllib.error.HTTPError as error:
            if error.code != 503 or attempt == attempts:
                raise RuntimeError(f"HTTP {error.code} for {urllib.parse.urlsplit(url).path or '/'}") from None
            retry_after = error.headers.get("Retry-After", "2")
            try:
                delay = max(0.0, min(float(retry_after), 5.0))
            except ValueError:
                delay = 2.0
            sleep(delay)
    raise RuntimeError("preview request retry loop exhausted")


def run_smoke(
    base_url: str,
    *,
    opener: urllib.request.OpenerDirector | None = None,
    attempts: int = 8,
    sleep: Callable[[float], None] = time.sleep,
) -> list[Result]:
    origin = base_url.rstrip("/")
    parsed = urllib.parse.urlsplit(origin)
    if parsed.scheme != "https" and parsed.hostname not in {"127.0.0.1", "localhost"}:
        raise RuntimeError("preview base URL must use HTTPS")

    client = opener or build_opener()
    results: list[Result] = []

    for name, path, kind in ROUTES:
        url = origin + path
        status, headers, body, used_attempts, final_url = _request(
            client, url, attempts=attempts, sleep=sleep
        )
        if status != 200:
            raise RuntimeError(f"{name} returned HTTP {status}")
        final = urllib.parse.urlsplit(final_url)
        if parsed.hostname not in {"127.0.0.1", "localhost"} and final.scheme != "https":
            raise RuntimeError(f"{name} redirected away from HTTPS")

        if kind == "health":
            try:
                payload = json.loads(body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                raise RuntimeError("health returned invalid JSON") from None
            if payload != {"status": "ok"}:
                raise RuntimeError("health did not report status=ok")
        else:
            robots = headers.get("X-Robots-Tag", "")
            if "noindex" not in robots.lower():
                raise RuntimeError(f"{name} is missing preview X-Robots-Tag: noindex")

        results.append(Result(name=name, path=path, status=status, attempts=used_attempts))

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a SongChart Vercel Preview deployment")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--base-url", help="Authenticated/unprotected HTTPS preview origin")
    source.add_argument("--share-url", help="Temporary Vercel share URL; never commit or log it")
    parser.add_argument("--attempts", type=int, default=8, help="Maximum attempts per route (default: 8)")
    args = parser.parse_args()

    if args.attempts < 1 or args.attempts > 30:
        parser.error("--attempts must be between 1 and 30")

    opener = build_opener()
    base_url = args.base_url
    if args.share_url:
        base_url = authenticate_share_url(opener, args.share_url)

    try:
        results = run_smoke(base_url or "", opener=opener, attempts=args.attempts)
    except (RuntimeError, urllib.error.URLError, TimeoutError) as error:
        print(f"PREVIEW FAIL: {error}")
        return 1

    print("PREVIEW PASS")
    for result in results:
        retry_note = f" attempts={result.attempts}" if result.attempts > 1 else ""
        print(f"- {result.name}: HTTP {result.status} {result.path}{retry_note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
