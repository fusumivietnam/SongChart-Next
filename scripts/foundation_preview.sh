#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ACTION="${1:-start}"
PORT="${FOUNDATION_PREVIEW_PORT:-8000}"
IMAGE="${FOUNDATION_PREVIEW_IMAGE:-songchart-next:foundation-preview}"
CONTAINER="${FOUNDATION_PREVIEW_CONTAINER:-songchart-foundation-preview}"

preview_url() {
  if [[ -n "${CODESPACE_NAME:-}" && -n "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]]; then
    printf 'https://%s-%s.%s\n' "$CODESPACE_NAME" "$PORT" "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN"
  else
    printf 'http://127.0.0.1:%s\n' "$PORT"
  fi
}

wait_for_preview() {
  for attempt in {1..30}; do
    if curl --fail --silent "http://127.0.0.1:${PORT}/up" >/dev/null; then
      return 0
    fi
    sleep 1
  done

  docker logs "$CONTAINER" || true
  return 1
}

start_preview() {
  docker build --target frontend-build --tag "$IMAGE" .

  docker rm -f "$CONTAINER" >/dev/null 2>&1 || true

  docker run -d     --name "$CONTAINER"     -p "127.0.0.1:${PORT}:8000"     -e APP_ENV=local     -e APP_DEBUG=false     -e APP_URL="http://127.0.0.1:${PORT}"     -e APP_KEY=base64:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=     -e DB_CONNECTION=sqlite     -e DB_DATABASE=:memory:     -e SESSION_DRIVER=array     -e CACHE_STORE=array     "$IMAGE"     php artisan serve --host=0.0.0.0 --port=8000 >/dev/null

  if ! wait_for_preview; then
    echo "Foundation preview failed to become healthy." >&2
    exit 1
  fi

  echo "Foundation preview is ready:"
  preview_url
  echo "Routes:"
  echo "  /_design/foundation/artist"
  echo "  /_design/foundation/artist-long"
  echo "  /_design/foundation/search"
  echo "  /_design/foundation/search-empty"
  echo "  /_design/foundation/search-error"
}

case "$ACTION" in
  start)
    start_preview
    ;;
  stop)
    docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
    echo "Foundation preview container stopped. Named development volumes were not touched."
    ;;
  status)
    if docker ps --filter "name=^/${CONTAINER}$" --filter status=running --format '{{.Names}}' | grep -qx "$CONTAINER"; then
      echo "running"
      preview_url
    else
      echo "stopped"
      exit 1
    fi
    ;;
  url)
    preview_url
    ;;
  *)
    echo "Usage: bash scripts/foundation_preview.sh [start|stop|status|url]" >&2
    exit 2
    ;;
esac
