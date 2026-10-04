#!/usr/bin/env bash
# PreToolUse hook for Edit, Write, MultiEdit and NotebookEdit.
# Blocks changes to anything listed in .claude/protected-paths.
# Exit 2 blocks the tool call and sends stderr to Claude.
set -u
here=$(cd "$(dirname "$0")" && pwd)
# shellcheck source=lib.sh
. "$here/lib.sh"

if ! command -v jq >/dev/null 2>&1; then
  echo "protect-paths: jq is not installed, so protected paths cannot be checked and edits are blocked. Ask the user to install jq (brew install jq, or apt install jq)." >&2
  exit 2
fi

input=$(cat)
file=$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty')
[ -z "$file" ] && exit 0

list="$(kit_root)/.claude/protected-paths"
[ -f "$list" ] || exit 0

abs=$(kit_abspath "$file")
rel=$(kit_relpath "$abs")

if kit_is_protected "$rel" "$abs" "$list"; then
  echo "Blocked: $rel is protected by .claude/protected-paths (rule: $KIT_MATCH). Do not work around this with another tool. Tell the user what change you need and why, and let them make it." >&2
  exit 2
fi
exit 0
