#!/usr/bin/env sh
set -eu

if [ -n "${VERCEL_URL:-}" ]; then
  export APP_URL="https://${VERCEL_URL}"
fi

if [ -z "${APP_KEY:-}" ]; then
  echo "APP_KEY is required for preview runtime" >&2
  exit 1
fi

if [ -z "${DB_URL:-}" ]; then
  echo "DB_URL is required for preview runtime" >&2
  exit 1
fi

php artisan migrate --force --no-interaction
php artisan config:clear

exec php artisan serve --host=0.0.0.0 --port="${PORT:-3000}"
