#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 scripts/verify_project_os.py
bash -n scripts/design_review.sh
bash -n scripts/codespaces_doctor.sh
bash -n .devcontainer/prebuild.sh
bash -n .devcontainer/post-create.sh
bash -n .devcontainer/post-start.sh
bash -n .devcontainer/install-understand-anything.sh

echo "Codespaces prebuild contract checks passed."
