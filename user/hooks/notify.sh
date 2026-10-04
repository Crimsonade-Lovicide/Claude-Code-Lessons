#!/usr/bin/env bash
# Notification hook: a desktop notification when Claude Code needs your input.
# Installed to ~/.claude/hooks/notify.sh by ./install.sh --user.
msg="Claude Code needs your attention"
if command -v jq >/dev/null 2>&1; then
  m=$(jq -r '.message // empty' 2>/dev/null)
  [ -n "$m" ] && msg=$m
fi
if command -v osascript >/dev/null 2>&1; then
  osascript -e "display notification \"${msg//\"/}\" with title \"Claude Code\"" >/dev/null 2>&1
elif command -v notify-send >/dev/null 2>&1; then
  notify-send "Claude Code" "$msg" >/dev/null 2>&1
else
  printf '\a'
fi
exit 0
