#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# This is a blocking Codespaces onCreate hook. Keep it limited to
# dependencies explicitly owned by the devcontainer configuration.
# Project governance verification belongs to GitHub CI and must not make
# a developer shell unrecoverable because an unrelated interpreter/tool
# is absent from the base image.

for cmd in bash git docker gh node corepack; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Codespaces devcontainer is missing required shell feature: $cmd" >&2
    exit 1
  fi
done

bash -n scripts/design_review.sh
bash -n scripts/codespaces_doctor.sh
bash -n .devcontainer/prebuild.sh
bash -n .devcontainer/post-create.sh
bash -n .devcontainer/post-start.sh
bash -n .devcontainer/install-understand-anything.sh

echo "Codespaces onCreate contract checks passed."
