#!/usr/bin/env sh
set -eu

php artisan migrate --force --no-interaction
php artisan config:clear

if [ "${PREVIEW_SEED_FIXTURES:-true}" = "true" ]; then
  php artisan songchart:fixture:import-artist --no-interaction
  php artisan songchart:fixture:import-release --no-interaction
fi
