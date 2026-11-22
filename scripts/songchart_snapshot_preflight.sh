#!/usr/bin/env bash
# MusicBrainz #174: metadata-only integrity preflight. No archive, database, or API writes.
set -euo pipefail

SNAPSHOT=20261118-001001
BASE="https://data.metabrainz.org/pub/musicbrainz/data/json-dumps/${SNAPSHOT}"
FPR=D5E63B4BDCCE195642948684B8FC2375C777580F
WORKDIR="${HOME}/songchart-data/${SNAPSHOT}"

for tool in curl gpg awk grep mktemp; do
  command -v "$tool" >/dev/null || { echo "Missing required command: $tool" >&2; exit 1; }
done

mkdir -p "$WORKDIR"
cd "$WORKDIR"

for file in SHA256SUMS SHA256SUMS.asc recording.tar.xz.asc; do
  curl --fail --silent --show-error --location --retry 2 \
    --connect-timeout 15 --max-time 90 --output "${file}.part" "$BASE/$file"
  mv -- "${file}.part" "$file"
done

GNUPGHOME="$(mktemp -d)"
chmod 700 "$GNUPGHOME"
export GNUPGHOME
trap 'rm -rf -- "$GNUPGHOME"' EXIT

if ! gpg --batch --keyserver hkps://keyserver.ubuntu.com --recv-keys "$FPR"; then
  echo "Could not fetch signing key; do not bypass verification." >&2
  exit 1
fi

if ! gpg --batch --with-colons --fingerprint "$FPR" \
  | awk -F: '$1=="fpr" {print $10}' | grep -Fxq "$FPR"; then
  echo "Signing key fingerprint mismatch." >&2
  exit 1
fi

if ! gpg --batch --verify SHA256SUMS.asc SHA256SUMS; then
  echo "SHA256SUMS signature verification failed. Stop." >&2
  exit 1
fi

awk '$2=="recording.tar.xz" || $2=="*recording.tar.xz" {
  n++; print; if (length($1)!=64 || $1 ~ /[^[:xdigit:]]/) bad=1
} END {exit (n==1 && !bad)?0:1}' SHA256SUMS || {
  echo "Missing, duplicate or invalid recording archive checksum." >&2
  exit 1
}

echo "PASS: signed SHA256 manifest verified. Archive was NOT downloaded or verified."
