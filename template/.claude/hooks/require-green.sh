#!/usr/bin/env bash
# Stop hook: Claude cannot finish a turn while the tests for what it changed are failing.
#
# Which tests run:
#   - KIT_TEST_CMD from .claude/kit.conf, if set (run from the project root), otherwise
#   - for each changed file, the nearest package.json with a real "test" script
#     (so monorepos test only the packages that changed), and pytest for Python projects.
# Skips when nothing changed, when only docs changed, and when the exact same working
# tree already passed. Exit 2 blocks the stop and sends the failure output to Claude.
set -u
here=$(cd "$(dirname "$0")" && pwd)
# shellcheck source=lib.sh
. "$here/lib.sh"
kit_load_conf

input=$(cat)
if command -v jq >/dev/null 2>&1; then
  # Claude is already continuing because of this hook. Let it stop to avoid a loop.
  [ "$(printf '%s' "$input" | jq -r '.stop_hook_active // false')" = "true" ] && exit 0
fi
[ "${KIT_STOP_GATE:-1}" = "0" ] && exit 0

root=$(kit_root)
cd "$root" || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

changed=$( { git diff --name-only HEAD 2>/dev/null; git ls-files --others --exclude-standard; } | sort -u)
code_changed=$(printf '%s\n' "$changed" | grep -Ev '(^$|\.(md|mdx|txt)$|^docs/)' || true)
[ -z "$code_changed" ] && exit 0

# Fingerprint of the working tree, so a turn that changed nothing reruns nothing.
fingerprint=$( {
  git diff HEAD --no-ext-diff 2>/dev/null
  git ls-files --others --exclude-standard -z | while IFS= read -r -d '' f; do
    printf '%s\n' "$f"
    git hash-object -- "$f" 2>/dev/null
  done
} | git hash-object --stdin)
state="$(git rev-parse --git-dir)/claude-kit-last-green"
[ -f "$state" ] && [ "$(cat "$state")" = "$fingerprint" ] && exit 0

# Build the list of checks as lines of "<dir><TAB><command>".
TAB=$'\t'
checks=""
skipped=""
if [ -n "${KIT_TEST_CMD:-}" ]; then
  checks="$root$TAB$KIT_TEST_CMD"
else
  dirs=""
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    start="$root/$(dirname "$f")"
    if d=$(kit_nearest "$start" package.json); then
      dirs="$dirs
node:$d"
    elif d=$(kit_nearest "$start" pyproject.toml) || d=$(kit_nearest "$start" pytest.ini); then
      dirs="$dirs
py:$d"
    fi
  done <<EOF
$code_changed
EOF
  while IFS= read -r entry; do
    case "$entry" in
      py:*)
        d=${entry#py:}
        command -v pytest >/dev/null 2>&1 && checks="$checks
$d${TAB}pytest -q -x"
        ;;
      node:*)
        d=${entry#node:}
        command -v jq >/dev/null 2>&1 || continue
        script=$(jq -r '.scripts.test // empty' "$d/package.json" 2>/dev/null)
        case "$script" in ''|*'no test specified'*) continue ;; esac
        if [ ! -d "$d/node_modules" ]; then
          skipped="$skipped $(kit_relpath "$d")"
          continue
        fi
        if kit_nearest "$d" bun.lockb >/dev/null; then runner="bun run test"
        elif kit_nearest "$d" yarn.lock >/dev/null; then runner="yarn test --silent"
        elif kit_nearest "$d" pnpm-lock.yaml >/dev/null; then runner="pnpm test --silent"
        else runner="npm test --silent"
        fi
        checks="$checks
$d$TAB$runner"
        ;;
    esac
  done <<EOF
$(printf '%s\n' "$dirs" | sort -u)
EOF
fi

# The useful part of a test log: the failures themselves, then the summary at the end.
# Plain "tail" is not enough because runners such as node --test print passing tests last.
failure_excerpt() {
  local hits
  hits=$(grep -E -A 12 '(^|[[:space:]])not ok |FAIL|AssertionError|Error:' "$1" | head -n 60)
  if [ -n "$hits" ]; then
    printf 'Failures:\n%s\n\nEnd of output:\n%s' "$hits" "$(tail -n 12 "$1")"
  else
    tail -n 40 "$1"
  fi
}

failed=0
report=""
log=$(mktemp)
while IFS="$TAB" read -r dir cmd; do
  [ -z "$dir" ] && continue
  # </dev/null: a test runner must not swallow the rest of this loop's input.
  if ! (cd "$dir" && eval "$cmd") </dev/null >"$log" 2>&1; then
    failed=1
    report="$report
--- $cmd (in $(kit_relpath "$dir")) ---
$(failure_excerpt "$log")"
  fi
done <<EOF
$checks
EOF
rm -f "$log"

if [ "$failed" = 1 ]; then
  {
    echo "Tests are failing for the code you changed. Fix them before finishing, or explain to the user why they cannot pass yet.$report"
  } >&2
  exit 2
fi

printf '%s' "$fingerprint" >"$state"
if [ -n "$skipped" ]; then
  printf '{"systemMessage":"Stop gate skipped tests in:%s (dependencies not installed)"}\n' "$skipped"
fi
exit 0
