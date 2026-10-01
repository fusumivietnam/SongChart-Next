#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p .codespaces/logs
LOG_FILE=".codespaces/logs/post-create-$(date -u +%Y%m%dT%H%M%SZ).log"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "SongChart Codespaces post-create bootstrap"
echo "Repository: $ROOT_DIR"
echo "Revision: $(git rev-parse HEAD 2>/dev/null || echo unknown)"

docker_ready=0
for attempt in $(seq 1 30); do
  if docker info >/dev/null 2>&1; then
    docker_ready=1
    break
  fi
  sleep 2
done

if [[ "$docker_ready" -ne 1 ]]; then
  echo "Docker is not ready after 60 seconds. Codespace remains usable; run bash scripts/codespaces_doctor.sh for diagnostics." >&2
  exit 0
fi

if bash scripts/design_review.sh; then
  git rev-parse HEAD > .codespaces/last-ready-sha
  echo "SongChart Codespaces bootstrap completed."
else
  echo "Application bootstrap did not complete. Codespace remains usable; run bash scripts/codespaces_doctor.sh and retry bash scripts/design_review.sh." >&2
fi

exit 0
