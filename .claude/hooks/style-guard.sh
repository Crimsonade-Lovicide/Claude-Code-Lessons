#!/usr/bin/env bash
# PostToolUse hook for Edit, Write and MultiEdit.
# Checks only the text Claude just wrote against .claude/banned-patterns.
# Exit 2 sends stderr back to Claude so it fixes the text right away.
set -u
here=$(cd "$(dirname "$0")" && pwd)
# shellcheck source=lib.sh
. "$here/lib.sh"

command -v jq >/dev/null 2>&1 || exit 0

list="$(kit_root)/.claude/banned-patterns"
[ -f "$list" ] || exit 0

input=$(cat)
file=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')
rel=$(kit_relpath "$(kit_abspath "$file")")
# Rules files have to contain the banned text, so never check them.
case "$rel" in banned-patterns|*/banned-patterns) exit 0 ;; esac

text=$(printf '%s' "$input" | jq -r '
  [ .tool_input.content, .tool_input.new_string, ((.tool_input.edits // []) | .[].new_string) ]
  | map(select(. != null)) | join("\n")')
[ -z "$text" ] && exit 0

problems=""
while IFS= read -r raw || [ -n "$raw" ]; do
  line=$(kit_trim "$raw")
  case "$line" in ''|'#'*) continue ;; esac
  # Format: <extended regex> :: <message for Claude>
  pattern=$(kit_trim "${line%% :: *}")
  message=$(kit_trim "${line#* :: }")
  [ "$message" = "$line" ] && message="matches banned pattern: $pattern"
  if hits=$(printf '%s\n' "$text" | grep -E -- "$pattern" | head -n 5) && [ -n "$hits" ]; then
    problems="$problems
- $message
$(printf '%s\n' "$hits" | sed 's/^/    > /')"
  fi
done < "$list"

if [ -n "$problems" ]; then
  {
    echo "Style rules from .claude/banned-patterns were broken in ${rel:-the text you just wrote}:$problems"
    echo "Fix these lines now, before continuing."
  } >&2
  exit 2
fi
exit 0
