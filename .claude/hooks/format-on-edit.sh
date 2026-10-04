#!/usr/bin/env bash
# PostToolUse hook for Edit, Write and MultiEdit: formats the file Claude just changed.
# Uses KIT_FORMAT_CMD from .claude/kit.conf when set, otherwise the project's own
# Prettier (nearest node_modules/.bin/prettier) or ruff for Python files.
# Never blocks: a formatter failure is not worth interrupting Claude for.
set -u
here=$(cd "$(dirname "$0")" && pwd)
# shellcheck source=lib.sh
. "$here/lib.sh"
kit_load_conf

command -v jq >/dev/null 2>&1 || exit 0
file=$(jq -r '.tool_input.file_path // empty')
[ -z "$file" ] && exit 0
abs=$(kit_abspath "$file")
[ -f "$abs" ] || exit 0
# Only format files inside this project.
case "$abs" in "$(kit_root)"/*) ;; *) exit 0 ;; esac

if [ -n "${KIT_FORMAT_CMD:-}" ]; then
  quoted=$(printf '%q' "$abs")
  cmd=${KIT_FORMAT_CMD//\{file\}/$quoted}
  (cd "$(kit_root)" && eval "$cmd") >/dev/null 2>&1
  exit 0
fi

case "$abs" in
  *.py)
    command -v ruff >/dev/null 2>&1 && ruff format --quiet "$abs" >/dev/null 2>&1
    ;;
  *)
    if dir=$(kit_nearest "$(dirname "$abs")" node_modules/.bin/prettier); then
      (cd "$dir" && ./node_modules/.bin/prettier --write --ignore-unknown --log-level silent "$abs") >/dev/null 2>&1
    fi
    ;;
esac
exit 0
