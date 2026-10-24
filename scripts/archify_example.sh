#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXAMPLE_COMMIT="600162d4b0bc531485d8df685c42745cb13baca6"
EXAMPLE_JSON="docs/architecture/examples/archify-public-read.architecture.json"
EXAMPLE_OUTPUT=".archify/examples/songchart-public-read.html"
ARCHIFY_BIN="${ARCHIFY_BIN:-$HOME/.agents/skills/archify/bin/archify.mjs}"

cd "$PROJECT_ROOT"
if ! git cat-file -e "$EXAMPLE_COMMIT^{commit}" 2>/dev/null; then
  echo "The sample is pinned to $EXAMPLE_COMMIT but the revision is missing locally." >&2
  echo "Fetch that commit's history or use a checkout containing the pinned source." >&2
  exit 1
fi

if [[ ! -f "$ARCHIFY_BIN" ]]; then
  echo "Archify not installed: run bash .devcontainer/install-archify.sh first." >&2
  exit 1
fi

mkdir -p .archify/examples
ARCHIFY_UPDATE_CHECK_DISABLED=1 node "$ARCHIFY_BIN" finalize architecture "$EXAMPLE_JSON" "$EXAMPLE_OUTPUT" \
  --repo-root "$PROJECT_ROOT" --quality showcase --json
