#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXAMPLE_COMMIT="cc31819fd074ec7d5f1e4d1b79cfdcbbf2c7e673"
EXAMPLE_JSON="docs/architecture/examples/archify-catalog-core.erd.json"
EXAMPLE_OUTPUT=".archify/examples/songchart-catalog-core.html"
ARCHIFY_BIN="${ARCHIFY_BIN:-$HOME/.agents/skills/archify/bin/archify.mjs}"

cd "$PROJECT_ROOT"
if ! git cat-file -e "$EXAMPLE_COMMIT^{commit}" 2>/dev/null; then
  echo "The catalog sample is pinned to $EXAMPLE_COMMIT but the revision is missing locally." >&2
  exit 1
fi

if [[ ! -f "$ARCHIFY_BIN" ]]; then
  echo "Archify not installed: run bash .devcontainer/install-archify.sh first." >&2
  exit 1
fi

mkdir -p .archify/examples
ARCHIFY_UPDATE_CHECK_DISABLED=1 node "$ARCHIFY_BIN" finalize erd "$EXAMPLE_JSON" "$EXAMPLE_OUTPUT" \
  --repo-root "$PROJECT_ROOT" --quality standard --json
