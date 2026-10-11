#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=${1:-}
if [[ -z "$ENV_FILE" || ! -f "$ENV_FILE" ]]; then
  echo "usage: $0 /path/to/production.env" >&2
  exit 2
fi

COMPOSE=(docker compose --env-file "$ENV_FILE" -f compose.production.yaml)

"${COMPOSE[@]}" config >/dev/null
"${COMPOSE[@]}" pull
"${COMPOSE[@]}" up -d db
"${COMPOSE[@]}" run --rm app php artisan migrate --force
"${COMPOSE[@]}" up -d app web
"${COMPOSE[@]}" ps

APP_URL=$(awk -F= '$1=="APP_URL" {print substr($0, index($0,"=")+1)}' "$ENV_FILE" | tail -n1)
if [[ -z "$APP_URL" ]]; then
  echo "APP_URL is missing from environment contract" >&2
  exit 3
fi

scripts/production/smoke.sh "$APP_URL"
