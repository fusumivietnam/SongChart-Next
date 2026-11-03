#!/usr/bin/env bash
# Opt-in, read-only localhost UX reconnaissance. Not a protected Preview verifier.
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo 'Usage: scripts/agent_browser_pilot.sh http://127.0.0.1:8000[/approved-route]' >&2
  exit 2
fi

url="$1"
# Do not let the browser visit external origins, credentials, query payloads or fragments.
if ! python3 - "$url" <<'PY'
import sys
from urllib.parse import urlsplit

try:
    url = urlsplit(sys.argv[1])
    assert url.scheme == "http"
    assert url.hostname in {"localhost", "127.0.0.1"}
    assert url.port is not None and 1 <= url.port <= 65535
    assert not (url.username or url.password or url.query or url.fragment)
    assert url.path in {"", "/", "/search", "/corrections", "/about", "/privacy", "/terms", "/disclaimer", "/support"}
except (AssertionError, ValueError):
    sys.exit("Refusing non-local or unapproved URL; use local fixture routes only")
PY
then
  exit 2
fi

browser="${AGENT_BROWSER_BIN:-agent-browser}"
if ! command -v "$browser" >/dev/null 2>&1; then
  echo 'Install the opt-in agent-browser CLI (version 0.41.1); see docs/operations/AGENT_BROWSER_PILOT.md' >&2
  exit 2
fi

# The CLI enforces this policy for browser subresource loads and redirects too.
# Explicitly override any broader inherited allowance from an operator shell.
export AGENT_BROWSER_ALLOWED_DOMAINS='localhost,127.0.0.1'
session="songchart-local-pilot-$$"
cleanup() { "$browser" --session "$session" close >/dev/null 2>&1 || true; }
trap cleanup EXIT

for viewport in '390 844' '1440 1024'; do
  read -r width height <<< "$viewport"
  echo "=== LOCAL pilot viewport ${width}x${height}; no assertion or acceptance claim ==="
  "$browser" --session "$session" set viewport "$width" "$height"
  "$browser" --session "$session" open "$url"
  "$browser" --session "$session" snapshot -i
done

echo 'Pilot finished. Review the interactive snapshots manually; no protected Preview acceptance was performed.'
