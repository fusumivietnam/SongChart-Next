#!/usr/bin/env bash
set -euo pipefail

# Opt-in, developer-only Archify installer. Never run from Codespaces bootstrap.
ARCHIFY_REPO_URL="https://github.com/tt-a1i/archify.git"
ARCHIFY_COMMIT="208acba8d412335185b2056fedf54b3405df43fb" # v3.2.0
ARCHIFY_CHECKOUT="${ARCHIFY_CHECKOUT:-$HOME/.archify-tool/repo}"
ARCHIFY_AGENT_SKILLS="${ARCHIFY_AGENT_SKILLS:-$HOME/.agents/skills}"
ARCHIFY_TARGET="$ARCHIFY_AGENT_SKILLS/archify"

for command_name in git node; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Archify requires $command_name in the developer shell." >&2
    exit 1
  fi
done

node_major="$(node -p 'process.versions.node.split(".")[0]')"
if [[ ! "$node_major" =~ ^[0-9]+$ ]] || (( node_major < 22 )); then
  echo "Archify requires Node.js 22+ in the developer shell." >&2
  exit 1
fi

if [[ -e "$ARCHIFY_CHECKOUT" && ! -d "$ARCHIFY_CHECKOUT/.git" ]]; then
  echo "Refusing to overwrite an existing non-Git Archify checkout: $ARCHIFY_CHECKOUT" >&2
  exit 1
fi

if [[ ! -d "$ARCHIFY_CHECKOUT/.git" ]]; then
  mkdir -p "$(dirname "$ARCHIFY_CHECKOUT")"
  git clone --filter=blob:none --no-checkout "$ARCHIFY_REPO_URL" "$ARCHIFY_CHECKOUT"
  git -C "$ARCHIFY_CHECKOUT" fetch --depth=1 origin "$ARCHIFY_COMMIT"
  git -C "$ARCHIFY_CHECKOUT" checkout --detach "$ARCHIFY_COMMIT"
fi

actual_commit="$(git -C "$ARCHIFY_CHECKOUT" rev-parse HEAD)"
if [[ "$actual_commit" != "$ARCHIFY_COMMIT" ]]; then
  echo "Archify checkout is not the approved commit; refusing to replace existing work." >&2
  exit 1
fi
if [[ -n "$(git -C "$ARCHIFY_CHECKOUT" status --porcelain)" ]]; then
  echo "Archify checkout has local changes; refusing to install a dirty skill." >&2
  exit 1
fi

skill_source="$ARCHIFY_CHECKOUT/archify"
if [[ ! -f "$skill_source/SKILL.md" || ! -f "$skill_source/bin/archify.mjs" ]]; then
  echo "Pinned Archify checkout does not contain the expected skill and renderer." >&2
  exit 1
fi

mkdir -p "$ARCHIFY_AGENT_SKILLS"
if [[ -L "$ARCHIFY_TARGET" ]]; then
  if [[ "$(readlink -f "$ARCHIFY_TARGET")" != "$(readlink -f "$skill_source")" ]]; then
    echo "Archify skill already points elsewhere; resolve manually: $ARCHIFY_TARGET" >&2
    exit 1
  fi
elif [[ -e "$ARCHIFY_TARGET" ]]; then
  echo "Archify skill destination already exists; refusing to overwrite: $ARCHIFY_TARGET" >&2
  exit 1
else
  ln -s "$skill_source" "$ARCHIFY_TARGET"
fi

echo "Archify developer skill ready at commit $actual_commit"
echo "Run: node \"$ARCHIFY_TARGET/bin/archify.mjs\" --help"
echo "Optional update checks: set ARCHIFY_UPDATE_CHECK_DISABLED=1 when running Archify."
