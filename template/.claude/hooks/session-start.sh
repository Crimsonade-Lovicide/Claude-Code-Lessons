#!/usr/bin/env bash
# SessionStart hook: in Claude Code cloud sessions (fresh containers), install
# dependencies so tests, linters and the Stop gate work from the first turn.
# Does nothing on your own machine. Output on stdout is added to Claude's context.
set -u
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0

here=$(cd "$(dirname "$0")" && pwd)
# shellcheck source=lib.sh
. "$here/lib.sh"
root=$(kit_root)
cd "$root" || exit 0

installed=""
failed=""
log=$(mktemp)
while IFS= read -r lock; do
  [ -z "$lock" ] && continue
  dir=$(dirname "$lock")
  [ -d "$dir/node_modules" ] && continue
  case "$lock" in
    *package-lock.json) cmd="npm ci --no-audit --no-fund" ;;
    *pnpm-lock.yaml) cmd="pnpm install --frozen-lockfile" ;;
    *yarn.lock) cmd="yarn install --frozen-lockfile" ;;
    *bun.lockb) cmd="bun install" ;;
  esac
  if (cd "$dir" && eval "$cmd") </dev/null >"$log" 2>&1; then
    installed="$installed ${dir#./}"
  else
    failed="$failed ${dir#./}"
  fi
done <<EOF
$(find . -maxdepth 3 -not -path '*/node_modules/*' \
    \( -name package-lock.json -o -name pnpm-lock.yaml -o -name yarn.lock -o -name bun.lockb \) | sort)
EOF

if [ -f requirements.txt ] && command -v pip >/dev/null 2>&1; then
  if pip install -q -r requirements.txt >"$log" 2>&1; then
    installed="$installed requirements.txt"
  else
    failed="$failed requirements.txt"
  fi
fi
rm -f "$log"

[ -n "$installed" ] && echo "starter-kit: installed dependencies in:$installed"
[ -n "$failed" ] && echo "starter-kit: dependency install FAILED in:$failed. Tests there may not run until this is fixed."
exit 0
