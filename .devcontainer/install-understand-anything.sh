#!/usr/bin/env bash
set -euo pipefail

# Developer-only code intelligence tooling. This is not a SongChart runtime dependency.
UA_REPO_URL="https://github.com/Egonex-AI/Understand-Anything.git"
UA_COMMIT="b05cc3b20990afca537b4fc0a49b4d7fbdc65bb0"
UA_PNPM_VERSION="10.6.2"
UA_REPO_DIR="${UA_DIR:-$HOME/.understand-anything/repo}"
UA_PLUGIN_ROOT="$UA_REPO_DIR/understand-anything-plugin"
UA_SKILLS_DIR="$UA_PLUGIN_ROOT/skills"
AGENT_SKILLS_DIR="$HOME/.agents/skills"
PLUGIN_LINK="$HOME/.understand-anything-plugin"

for cmd in git node corepack; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Understand Anything bootstrap requires $cmd in the Codespaces developer shell." >&2
    exit 1
  fi
done

mkdir -p "$(dirname "$UA_REPO_DIR")"

if [[ ! -d "$UA_REPO_DIR/.git" ]]; then
  git clone --filter=blob:none --no-checkout "$UA_REPO_URL" "$UA_REPO_DIR"
else
  git -C "$UA_REPO_DIR" remote set-url origin "$UA_REPO_URL"
fi

git -C "$UA_REPO_DIR" fetch --depth=1 origin "$UA_COMMIT"
git -C "$UA_REPO_DIR" checkout --detach --force "$UA_COMMIT"

actual_commit="$(git -C "$UA_REPO_DIR" rev-parse HEAD)"
if [[ "$actual_commit" != "$UA_COMMIT" ]]; then
  echo "Understand Anything provenance mismatch: expected $UA_COMMIT, got $actual_commit" >&2
  exit 1
fi

corepack enable
corepack prepare "pnpm@$UA_PNPM_VERSION" --activate

(
  cd "$UA_REPO_DIR"
  pnpm install --frozen-lockfile
  pnpm --filter @understand-anything/core build
)

if [[ ! -d "$UA_SKILLS_DIR" ]]; then
  echo "Understand Anything skills directory not found at $UA_SKILLS_DIR" >&2
  exit 1
fi

mkdir -p "$AGENT_SKILLS_DIR"
for skill_dir in "$UA_SKILLS_DIR"/*/; do
  [[ -d "$skill_dir" ]] || continue
  skill="$(basename "$skill_dir")"
  target="$AGENT_SKILLS_DIR/$skill"
  if [[ -e "$target" && ! -L "$target" ]]; then
    echo "Refusing to replace non-symlink skill path: $target" >&2
    exit 1
  fi
  ln -sfn "$skill_dir" "$target"
done

if [[ -e "$PLUGIN_LINK" && ! -L "$PLUGIN_LINK" ]]; then
  echo "Refusing to replace non-symlink plugin path: $PLUGIN_LINK" >&2
  exit 1
fi
ln -sfn "$UA_PLUGIN_ROOT" "$PLUGIN_LINK"

echo "Understand Anything installed for Codex-compatible skill discovery."
echo "Upstream commit: $UA_COMMIT"
echo 'Invoke with $understand (Codex) or ask the agent to use the understand skill.'
echo "Generated .ua data is derived analysis and is not SongChart project authority."
