#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! docker info >/dev/null 2>&1; then
  echo "Docker is not ready yet. Run bash scripts/codespaces_doctor.sh if this persists." >&2
  exit 0
fi

app_id="$(docker compose ps -q app 2>/dev/null || true)"
if [[ -n "$app_id" ]] && [[ "$(docker inspect -f '{{.State.Running}}' "$app_id" 2>/dev/null || true)" == "true" ]] && curl --fail --silent http://127.0.0.1:8000/up >/dev/null 2>&1; then
  echo "SongChart app is already healthy on port 8000."
  exit 0
fi

echo "Restoring SongChart local runtime after Codespace start..."
if ! bash scripts/design_review.sh; then
  echo "Automatic runtime restore did not complete. Codespace remains usable; run bash scripts/codespaces_doctor.sh." >&2
fi

exit 0
