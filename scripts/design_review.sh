#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PORT="${DESIGN_REVIEW_PORT:-8000}"
LEGACY_PREVIEW_CONTAINER="${DESIGN_REVIEW_LEGACY_CONTAINER:-songchart-foundation-preview}"

review_url() {
  if [[ -n "${CODESPACE_NAME:-}" && -n "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]]; then
    printf 'https://%s-%s.%s\n' "$CODESPACE_NAME" "$PORT" "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN"
  else
    printf 'http://127.0.0.1:%s\n' "$PORT"
  fi
}

cleanup_legacy_preview() {
  if docker container inspect "$LEGACY_PREVIEW_CONTAINER" >/dev/null 2>&1; then
    echo "Removing superseded Foundation preview container: $LEGACY_PREVIEW_CONTAINER"
    docker rm -f "$LEGACY_PREVIEW_CONTAINER" >/dev/null
  fi
}

ensure_app_running() {
  local app_id
  app_id="$(docker compose ps -q app 2>/dev/null || true)"

  if [[ -n "$app_id" ]] && [[ "$(docker inspect -f '{{.State.Running}}' "$app_id" 2>/dev/null || true)" == "true" ]]; then
    return 0
  fi

  echo "SongChart app service is not running; starting the approved local Compose stack..."
  docker compose up -d --wait db app
}

build_static_assets() {
  echo "Building Design Authority review assets in the existing app service..."
  docker compose exec -T app sh -ec '
    test -f vendor/autoload.php || composer install --prefer-dist --no-interaction --no-progress
    CI=true pnpm install --frozen-lockfile
    rm -f public/hot
    pnpm run build
    pnpm run types:check
  '
}

verify_routes() {
  local route
  for route in     /_design/foundation/artist     /_design/foundation/artist-long     /_design/foundation/search     /_design/foundation/search-empty     /_design/foundation/search-error
  do
    curl --fail --silent --show-error "http://127.0.0.1:${PORT}${route}" >/dev/null
  done
}

verify_proxy_assets() {
  if [[ -z "${CODESPACE_NAME:-}" || -z "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]]; then
    return 0
  fi

  local forwarded_host html
  forwarded_host="${CODESPACE_NAME}-${PORT}.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
  html="$(curl --fail --silent --show-error     -H "Host: 127.0.0.1:${PORT}"     -H "X-Forwarded-Host: ${forwarded_host}"     -H "X-Forwarded-Proto: https"     -H "X-Forwarded-Port: 443"     "http://127.0.0.1:${PORT}/_design/foundation/artist")"

  grep -q "https://${forwarded_host}/build/assets/" <<< "$html"
  ! grep -q "http://127.0.0.1:${PORT}/build/assets/" <<< "$html"
}

main() {
  cleanup_legacy_preview
  ensure_app_running
  build_static_assets
  verify_routes
  verify_proxy_assets

  local base
  base="$(review_url)"

  echo
  echo "Design Authority review is ready."
  echo "Revision: $(git rev-parse HEAD)"
  echo "Base URL: $base"
  echo "Routes:"
  echo "  $base/_design/foundation/artist"
  echo "  $base/_design/foundation/artist-long"
  echo "  $base/_design/foundation/search"
  echo "  $base/_design/foundation/search-empty"
  echo "  $base/_design/foundation/search-error"
  echo
  echo "No preview container, extra port binding, preview volume, or Docker image build was created."
}

main "$@"
