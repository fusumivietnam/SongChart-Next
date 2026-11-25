#!/usr/bin/env bash
# Best-effort Git status on VS Code folder open. Never update checked-out files.
set -u
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR" || exit 0

if ! command -v git >/dev/null 2>&1 || ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "SongChart Git: workspace is not a Git checkout."
  exit 0
fi

branch="$(git branch --show-current 2>/dev/null || true)"
echo "SongChart Git: branch ${branch:-detached HEAD}"
if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
  echo "SongChart Git: local changes exist; they will not be modified."
fi

# Bounded remote check: never block the independent Docker startup task.
if ! command -v timeout >/dev/null 2>&1; then
  echo "SongChart Git: timeout unavailable; skipping remote check."
  exit 0
fi
if ! timeout 12s git -c credential.interactive=never -c core.askPass=/bin/false fetch --no-tags --quiet origin main </dev/null; then
  echo "SongChart Git: fetch unavailable or timed out; working tree unchanged."
  exit 0
fi

if [[ "$branch" != "main" ]]; then
  echo "SongChart Git: current branch is not main. origin/main fetched; no sync performed."
  exit 0
fi

counts="$(git rev-list --left-right --count HEAD...refs/remotes/origin/main 2>/dev/null || true)"
if [[ -z "$counts" ]]; then
  echo "SongChart Git: cannot compare with origin/main; no sync performed."
  exit 0
fi
read -r ahead behind <<< "$counts"
if (( behind > 0 )); then
  echo "SongChart Git: main is behind origin/main by $behind commit(s); ahead by $ahead. Review before manually running git pull --ff-only."
elif (( ahead > 0 )); then
  echo "SongChart Git: local main is ahead of origin/main by $ahead commit(s); inspect before pushing."
else
  echo "SongChart Git: main is up to date with origin/main."
fi
