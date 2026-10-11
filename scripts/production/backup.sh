#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=${1:-}
if [[ -z "$ENV_FILE" || ! -f "$ENV_FILE" ]]; then
  echo "usage: $0 /path/to/production.env" >&2
  exit 2
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

: "${BACKUP_DIR:?BACKUP_DIR is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${POSTGRES_USER:?POSTGRES_USER is required}"

mkdir -p "$BACKUP_DIR"
umask 077
stamp=$(date -u +%Y%m%dT%H%M%SZ)
out="$BACKUP_DIR/songchart-${stamp}.dump"

COMPOSE=(docker compose --env-file "$ENV_FILE" -f compose.production.yaml)
"${COMPOSE[@]}" exec -T db pg_dump --format=custom --no-owner --no-acl --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" > "$out"

test -s "$out"
sha256sum "$out" > "$out.sha256"

printf 'local backup staged: %s\n' "$out"
printf 'OFF-HOST COPY REQUIRED: transfer %s and %s.sha256 to independent storage, verify checksum there, then record the remote object/version in release evidence.\n' "$out" "$out"

# Exit 3 intentionally: a local VPS dump is not considered a completed backup.
# The release operator must perform and record the off-host copy before continuing G5.
exit 3
