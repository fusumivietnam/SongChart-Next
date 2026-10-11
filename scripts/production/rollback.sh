#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=${1:-}
PREVIOUS_APP_IMAGE=${2:-}
PREVIOUS_WEB_IMAGE=${3:-}

if [[ -z "$ENV_FILE" || ! -f "$ENV_FILE" || -z "$PREVIOUS_APP_IMAGE" || -z "$PREVIOUS_WEB_IMAGE" ]]; then
  echo "usage: $0 /path/to/production.env <previous-app-image@digest> <previous-web-image@digest>" >&2
  exit 2
fi

case "$PREVIOUS_APP_IMAGE" in
  *@sha256:*) ;;
  *) echo "previous app image must be an immutable digest reference" >&2; exit 3 ;;
esac
case "$PREVIOUS_WEB_IMAGE" in
  *@sha256:*) ;;
  *) echo "previous web image must be an immutable digest reference" >&2; exit 3 ;;
esac

export APP_IMAGE="$PREVIOUS_APP_IMAGE"
export WEB_IMAGE="$PREVIOUS_WEB_IMAGE"
COMPOSE=(docker compose --env-file "$ENV_FILE" -f compose.production.yaml)

"${COMPOSE[@]}" pull app web
"${COMPOSE[@]}" up -d --no-deps app web
"${COMPOSE[@]}" ps

APP_URL=$(awk -F= '$1=="APP_URL" {print substr($0, index($0,"=")+1)}' "$ENV_FILE" | tail -n1)
bash scripts/production/smoke.sh "$APP_URL"

cat <<'EOF'
Application/web image rollback completed.
Database schema was NOT rolled back. If the release changed schema incompatibly, stop and use the release-specific forward-fix/recovery plan; never run destructive migration rollback automatically.
EOF
