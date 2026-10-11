#!/usr/bin/env bash
set -euo pipefail

BASE_URL=${1:-}
if [[ -z "$BASE_URL" ]]; then
  echo "usage: $0 https://songchart.example" >&2
  exit 2
fi
BASE_URL=${BASE_URL%/}

check() {
  local path=$1
  local expected=$2
  local code
  code=$(curl --fail-with-body --silent --show-error --location --max-time 15 --output /tmp/songchart-smoke-body --write-out '%{http_code}' "$BASE_URL$path")
  if [[ "$code" != "$expected" ]]; then
    echo "smoke failed: $path returned $code, expected $expected" >&2
    exit 1
  fi
}

check /health 200
check / 200
check /search 200

if ! grep -q '"status":"ok"' /tmp/songchart-smoke-body 2>/dev/null; then
  # /tmp body now belongs to /search, so query health separately without logging body.
  health=$(curl --fail --silent --show-error --max-time 15 "$BASE_URL/health")
  [[ "$health" == *'"status":"ok"'* ]] || { echo "health body is not ok" >&2; exit 1; }
fi

rm -f /tmp/songchart-smoke-body
printf 'production smoke passed for %s\n' "$BASE_URL"
