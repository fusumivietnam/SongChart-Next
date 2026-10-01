#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ACTION="${1:-start}"
PORT="${FOUNDATION_PREVIEW_PORT:-8000}"
CONTAINER="${FOUNDATION_PREVIEW_CONTAINER:-songchart-foundation-preview}"
COMPOSER_VOLUME="${FOUNDATION_PREVIEW_COMPOSER_VOLUME:-songchart-foundation-preview-composer}"
NODE_VOLUME="${FOUNDATION_PREVIEW_NODE_VOLUME:-songchart-foundation-preview-node}"
DOCKERFILE_HASH="$(sha256sum Dockerfile | cut -c1-12)"
PREFERRED_TOOLCHAIN_IMAGE="${FOUNDATION_PREVIEW_TOOLCHAIN_IMAGE:-songchart-next:foundation-toolchain-${DOCKERFILE_HASH}}"
FALLBACK_IMAGES="${FOUNDATION_PREVIEW_FALLBACK_IMAGES:-songchart-next-app:latest songchart-next:foundation-preview songchart-next:foundation-visual}"
SELECTED_TOOLCHAIN_IMAGE=""

preview_url() {
  if [[ -n "${CODESPACE_NAME:-}" && -n "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]]; then
    printf 'https://%s-%s.%s\n' "$CODESPACE_NAME" "$PORT" "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN"
  else
    printf 'http://127.0.0.1:%s\n' "$PORT"
  fi
}

source_revision() {
  git rev-parse HEAD
}

warn_if_dirty() {
  local dirty=0

  git diff --quiet --ignore-submodules -- || dirty=1
  git diff --cached --quiet --ignore-submodules -- || dirty=1

  if [[ "$dirty" -eq 0 ]]; then
    if git ls-files --others --exclude-standard 2>/dev/null | head -n 1 | grep -q .; then
      dirty=1
    fi
  fi

  if [[ "$dirty" -ne 0 ]]; then
    echo "WARNING: working tree has changes; preview reflects the current workspace, not only commit $(source_revision)." >&2
  fi
}

toolchain_is_compatible() {
  local image="$1"

  docker image inspect "$image" >/dev/null 2>&1 || return 1

  docker run --rm "$image" sh -ec '
    php -r '\''foreach (["pdo_pgsql","pdo_sqlite","intl","mbstring","zip","Zend OPcache"] as $ext) { if (!extension_loaded($ext)) { fwrite(STDERR, "Missing PHP extension: $ext\\n"); exit(1); } }'\''
    composer --version >/dev/null
    node --version | grep -Eq "^v22\\."
    test "$(pnpm --version)" = "10.17.1"
  ' >/dev/null 2>&1
}

select_existing_toolchain() {
  local image

  if toolchain_is_compatible "$PREFERRED_TOOLCHAIN_IMAGE"; then
    SELECTED_TOOLCHAIN_IMAGE="$PREFERRED_TOOLCHAIN_IMAGE"
    echo "Using cached Foundation toolchain: $SELECTED_TOOLCHAIN_IMAGE"
    return 0
  fi

  for image in $FALLBACK_IMAGES; do
    if toolchain_is_compatible "$image"; then
      SELECTED_TOOLCHAIN_IMAGE="$image"
      echo "Using compatible existing local toolchain image: $SELECTED_TOOLCHAIN_IMAGE"
      return 0
    fi
  done

  return 1
}

build_preferred_toolchain() {
  local context_dir
  context_dir="$(mktemp -d)"
  cp Dockerfile "$context_dir/Dockerfile"

  echo "No compatible local toolchain image was found."
  echo "Building cached Foundation toolchain from a Dockerfile-only context..."

  if docker build --target php-toolchain --tag "$PREFERRED_TOOLCHAIN_IMAGE" "$context_dir"; then
    rm -rf "$context_dir"

    if toolchain_is_compatible "$PREFERRED_TOOLCHAIN_IMAGE"; then
      SELECTED_TOOLCHAIN_IMAGE="$PREFERRED_TOOLCHAIN_IMAGE"
      return 0
    fi

    echo "Built toolchain image failed compatibility verification." >&2
    return 1
  fi

  rm -rf "$context_dir"
  return 1
}

ensure_toolchain_image() {
  if select_existing_toolchain; then
    return 0
  fi

  if build_preferred_toolchain; then
    return 0
  fi

  cat >&2 <<'EOF'
Foundation preview could not obtain a compatible local toolchain.
The preview deliberately does not prune Docker caches, delete volumes, or mutate the Docker daemon.
If Docker's local content store is damaged, an existing compatible SongChart development image is used automatically when available.
EOF
  return 1
}

ensure_dependency_volumes() {
  docker volume create "$COMPOSER_VOLUME" >/dev/null
  docker volume create "$NODE_VOLUME" >/dev/null
}

build_workspace() {
  echo "Installing locked dependencies and building static assets..."
  docker run --rm \
    -v "$ROOT_DIR:/var/www/html" \
    -v "$COMPOSER_VOLUME:/var/www/html/vendor" \
    -v "$NODE_VOLUME:/var/www/html/node_modules" \
    -w /var/www/html \
    "$SELECTED_TOOLCHAIN_IMAGE" \
    sh -ec '
      composer install --prefer-dist --no-interaction --no-progress
      CI=true pnpm install --frozen-lockfile
      rm -f public/hot
      pnpm run build
      pnpm run types:check
    '
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

start_server() {
  docker rm -f "$CONTAINER" >/dev/null 2>&1 || true

  docker run -d \
    --name "$CONTAINER" \
    -p "127.0.0.1:${PORT}:8000" \
    -e APP_ENV=local \
    -e APP_DEBUG=false \
    -e APP_URL="http://127.0.0.1:${PORT}" \
    -e APP_KEY=base64:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= \
    -e DB_CONNECTION=sqlite \
    -e DB_DATABASE=:memory: \
    -e SESSION_DRIVER=array \
    -e CACHE_STORE=array \
    -v "$ROOT_DIR:/var/www/html" \
    -v "$COMPOSER_VOLUME:/var/www/html/vendor" \
    -v "$NODE_VOLUME:/var/www/html/node_modules" \
    -w /var/www/html \
    "$SELECTED_TOOLCHAIN_IMAGE" \
    php artisan serve --host=0.0.0.0 --port=8000 >/dev/null

  if ! wait_for_preview; then
    echo "Foundation preview failed to become healthy." >&2
    exit 1
  fi
}

start_preview() {
  warn_if_dirty
  ensure_toolchain_image
  ensure_dependency_volumes
  build_workspace
  start_server

  echo "Foundation preview is ready."
  echo "Revision: $(source_revision)"
  echo "Toolchain: $SELECTED_TOOLCHAIN_IMAGE"
  echo "URL: $(preview_url)"
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
    echo "Foundation preview container stopped. Dedicated dependency caches and all database volumes were preserved."
    ;;
  status)
    if docker ps --filter "name=^/${CONTAINER}$" --filter status=running --format '{{.Names}}' | grep -qx "$CONTAINER"; then
      echo "running"
      echo "Revision: $(source_revision)"
      echo "URL: $(preview_url)"
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
