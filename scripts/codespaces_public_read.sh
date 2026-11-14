#!/usr/bin/env bash
# Private local read-only smoke, using only the Bash/curl shell tools.
set -euo pipefail
origin='http://127.0.0.1:8000'
routes=('/' '/search?q=Signals' '/corrections' '/about' '/privacy' '/terms' '/disclaimer' '/support')
failed=0
health="$(curl --silent --max-time 5 --max-filesize 80 --write-out $'\n%{http_code}|%{content_type}' "$origin/health" 2>/dev/null)" || health=''
if [[ "$health" == $'{"status":"ok"}\n200|application/json' ]]; then
  echo 'CODESPACES READ 00: PASS'
else
  echo 'CODESPACES READ 00: FAIL'
  failed=1
fi
index=1
for path in "${routes[@]}"; do
  result="$(curl --silent --max-time 5 --output /dev/null --write-out '%{http_code}|%{content_type}' "$origin$path" 2>/dev/null)" || result=''
  if [[ "$result" == 200\|text/html* ]]; then
    printf 'CODESPACES READ %02d: PASS\n' "$index"
  else
    printf 'CODESPACES READ %02d: FAIL\n' "$index"
    failed=1
  fi
  index=$((index + 1))
done
if (( failed )); then
  echo 'CODESPACES PUBLIC READ SMOKE FAILED; inspect local Compose health.'
  exit 1
fi
echo 'CODESPACES PUBLIC READ SMOKE PASS; local read-only only, no browser or release acceptance.'
