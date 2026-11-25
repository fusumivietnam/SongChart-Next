#!/usr/bin/env bash
# SongChart Next: local WSL/Docker Desktop port preflight and safe Compose startup.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

port="${SONGCHART_HTTP_PORT:-8000}"
if [[ ! "$port" =~ ^[0-9]+$ ]] || (( 10#$port < 1 || 10#$port > 65535 )); then
  echo "Invalid SONGCHART_HTTP_PORT; expected 1..65535." >&2
  exit 2
fi
port="$((10#$port))"

echo "SongChart development startup"
echo "Revision: $(git rev-parse --short HEAD)"
echo "Host URL: http://127.0.0.1:${port}"

command -v docker >/dev/null || { echo "Docker CLI unavailable." >&2; exit 1; }
docker info --format 'Docker daemon: {{.Name}} ({{.OperatingSystem}})' || {
  echo "Docker daemon unavailable; check Docker Desktop and WSL integration." >&2
  exit 1
}

# Checking the host before Compose avoids the opaque /forwards/expose 500
# when VS Code or another Windows process owns the loopback listener.
if [[ -n "${WSL_DISTRO_NAME:-}" ]] && command -v powershell.exe >/dev/null 2>&1; then
  win_listener="$(powershell.exe -NoProfile -NonInteractive -Command "Get-NetTCPConnection -LocalPort ${port} -State Listen -ErrorAction SilentlyContinue | ForEach-Object { \$p = Get-Process -Id \$_.OwningProcess -ErrorAction SilentlyContinue; if (\$p) { Write-Output ('PID=' + \$p.Id + ' Process=' + \$p.ProcessName) } }" 2>/dev/null | tr -d '\r' || true)"
  if [[ -n "$win_listener" ]]; then
    echo "Windows already listens on port ${port}:" >&2
    printf '%s\n' "$win_listener" >&2
    echo "Check VS Code Ports/other windows and stop stale forwarding; no process was terminated." >&2
    exit 3
  fi
fi

if command -v ss >/dev/null 2>&1; then
  linux_listener="$(ss -H -ltn "sport = :${port}" 2>/dev/null || true)"
  if [[ -n "$linux_listener" ]]; then
    echo "A Linux listener is already using host port ${port}; inspect 'ss -ltnp'." >&2
    exit 3
  fi
fi

docker compose config --quiet
if ! docker compose up -d --wait db app; then
  echo "Compose startup failed. If /forwards/expose returned 500 on a free port, diagnose Docker Desktop networking; do not reset the database." >&2
  exit 1
fi

docker compose ps
echo "Checking loopback HTTP on ${port}..."
bash scripts/codespaces_public_read.sh
echo "Ready: http://127.0.0.1:${port}"
