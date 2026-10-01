#!/usr/bin/env bash
set +e

echo "== SongChart Codespaces doctor =="
echo "UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "PWD: $PWD"
echo "CODESPACE_NAME: ${CODESPACE_NAME:-not-set}"
echo

echo "-- Git --"
git rev-parse --short HEAD 2>&1
git status --short --untracked-files=normal 2>&1 | head -100
echo

echo "-- Disk --"
df -h / /workspaces 2>&1
echo

echo "-- Docker --"
docker version 2>&1
docker info 2>&1 | sed -n '1,80p'
docker compose version 2>&1
echo

echo "-- Compose --"
docker compose ps 2>&1
echo

echo "-- App health --"
curl -fsS http://127.0.0.1:8000/up 2>&1
echo
echo

echo "-- GitHub CLI --"
gh auth status 2>&1
echo

if [[ -n "${CODESPACE_NAME:-}" ]]; then
  echo "Creation log command:"
  echo "  gh codespace logs -c ${CODESPACE_NAME}"
fi
