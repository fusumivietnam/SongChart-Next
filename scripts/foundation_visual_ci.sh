#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ACTION="${1:-start}"
PORT="${FOUNDATION_VISUAL_PORT:-8000}"
IMAGE="${FOUNDATION_VISUAL_IMAGE:-songchart-next:foundation-visual}"
CONTAINER="${FOUNDATION_VISUAL_CONTAINER:-foundation-visual}"

wait_for_server() {
  for attempt in {1..30}; do
    if curl --fail --silent "http://127.0.0.1:${PORT}/up" >/dev/null; then
      return 0
    fi
    sleep 1
  done

  docker logs "$CONTAINER" || true
  return 1
}

start_ci_server() {
  docker build --target frontend-build --tag "$IMAGE" .

  docker rm -f "$CONTAINER" >/dev/null 2>&1 || true

  docker run -d     --name "$CONTAINER"     -p "127.0.0.1:${PORT}:8000"     -e APP_ENV=local     -e APP_DEBUG=false     -e APP_URL="http://127.0.0.1:${PORT}"     -e APP_KEY=base64:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=     -e DB_CONNECTION=sqlite     -e DB_DATABASE=:memory:     -e SESSION_DRIVER=array     -e CACHE_STORE=array     "$IMAGE"     php artisan serve --host=0.0.0.0 --port=8000 >/dev/null

  wait_for_server
}

case "$ACTION" in
  start)
    start_ci_server
    ;;
  stop)
    docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
    ;;
  *)
    echo "Usage: bash scripts/foundation_visual_ci.sh [start|stop]" >&2
    exit 2
    ;;
esac
