#!/usr/bin/env python3
"""Fail-closed high-confidence secret scan for tracked repository text files.

The scanner reports only path, line and rule id. Matched credential values are never
printed or stored in evidence output.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


@dataclass(frozen=True)
class Rule:
    rule_id: str
    pattern: re.Pattern[str]


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule_id: str


RULES: tuple[Rule, ...] = (
    Rule("private-key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----")),
    Rule("github-classic-token", re.compile(r"\bgh[opusr]_[A-Za-z0-9]{36,}\b")),
    Rule("github-fine-grained-token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{60,}\b")),
    Rule("aws-access-key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    Rule("stripe-live-secret", re.compile(r"\bsk_live_[0-9A-Za-z]{16,}\b")),
    Rule("slack-token", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{20,}\b")),
    Rule("openai-secret", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    Rule("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
)

ALLOWED_ENV_FILES = frozenset({".env.example"})


def tracked_paths() -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return [item.decode("utf-8") for item in completed.stdout.split(b"\0") if item]


def runtime_env_paths(paths: Iterable[str]) -> list[str]:
    blocked: list[str] = []
    for path in paths:
        name = Path(path).name
        if (name == ".env" or name.startswith(".env.")) and name not in ALLOWED_ENV_FILES:
            blocked.append(path)
    return sorted(blocked)


def scan_text(text: str, display_path: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for rule in RULES:
            if rule.pattern.search(line):
                findings.append(Finding(display_path, line_number, rule.rule_id))
    return findings


def scan_file(path: Path, display_path: str | None = None) -> list[Finding]:
    data = path.read_bytes()
    if b"\0" in data:
        return []
    text = data.decode("utf-8", errors="replace")
    return scan_text(text, display_path or path.as_posix())


def scan_repository(paths: Sequence[str]) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    scanned_text_files = 0
    for relative_path in paths:
        path = Path(relative_path)
        if not path.is_file():
            continue
        data = path.read_bytes()
        if b"\0" in data:
            continue
        scanned_text_files += 1
        findings.extend(scan_text(data.decode("utf-8", errors="replace"), relative_path))
    return findings, scanned_text_files


def describe_finding(finding: Finding) -> str:
    return f"{finding.path}:{finding.line}:{finding.rule_id}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--paths",
        nargs="*",
        help="Optional explicit files to scan. Defaults to all git-tracked files.",
    )
    args = parser.parse_args()

    paths = list(args.paths) if args.paths else tracked_paths()
    blocked_env = runtime_env_paths(paths)
    findings, scanned_text_files = scan_repository(paths)

    if blocked_env:
        print("Tracked runtime environment files are forbidden:", file=sys.stderr)
        for path in blocked_env:
            print(f"{path}:tracked-runtime-env", file=sys.stderr)

    if findings:
        print("High-confidence secret patterns detected (values intentionally redacted):", file=sys.stderr)
        for finding in findings:
            print(describe_finding(finding), file=sys.stderr)

    if blocked_env or findings:
        return 1

    print(
        f"Secret scan passed: {scanned_text_files} tracked text files; "
        "runtime .env tracking guard passed; no high-confidence credential patterns found."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
