#!/usr/bin/env bash
# Tests for the kit itself: syntax, JSON, skill frontmatter, house style,
# the hook self-test, and the installer. Run from anywhere: bash tests/run.sh
set -u
kit=$(cd "$(dirname "$0")/.." && pwd)
cd "$kit" || exit 1
status=0
step() { printf '\n== %s\n' "$1"; }
bad() { echo "  FAIL  $1"; status=1; }

step "shell syntax"
for f in install.sh tests/*.sh template/.claude/hooks/*.sh user/hooks/*.sh; do
  bash -n "$f" || bad "$f"
done
if command -v shellcheck >/dev/null 2>&1; then
  shellcheck -x -e SC1091 install.sh tests/*.sh template/.claude/hooks/*.sh user/hooks/*.sh || bad "shellcheck"
else
  echo "  (shellcheck not installed, skipped)"
fi

step "JSON files"
for f in template/.claude/settings.json user/settings.json; do
  jq empty "$f" || bad "$f"
done
# Every hook command in settings.json must point at a script that exists and is executable.
# shellcheck disable=SC2016 # the sed pattern matches a literal $CLAUDE_PROJECT_DIR
for cmd in $(jq -r '.hooks[][].hooks[].command' template/.claude/settings.json | sed 's/"\$CLAUDE_PROJECT_DIR"\///'); do
  [ -x "template/$cmd" ] || bad "settings.json references missing or non-executable $cmd"
done

step "video demo: Python syntax and episode JSON"
for f in video/demo/*.py; do
  python3 -m py_compile "$f" 2>/dev/null || bad "$f does not compile"
done
jq empty video/demo/episode.json || bad "video/demo/episode.json"
find video/demo -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null

step "skill and agent frontmatter"
for f in template/.claude/skills/*/SKILL.md template/.claude/agents/*.md; do
  head -n 1 "$f" | grep -qx -- '---' || bad "$f does not start with frontmatter"
  awk 'NR>1 && /^---$/ {exit} {print}' "$f" | grep -q '^name: ' || bad "$f has no name"
  awk 'NR>1 && /^---$/ {exit} {print}' "$f" | grep -q '^description: ' || bad "$f has no description"
done
for d in template/.claude/skills/*/; do
  name=$(basename "$d")
  grep -q "^name: $name\$" "$d/SKILL.md" || bad "skill folder $name does not match its name field"
done

step "no em dashes (outside the banned-patterns rules)"
if hits=$(grep -rn "$(printf '\342\200\224')" --exclude=banned-patterns --exclude-dir=.git . ) && [ -n "$hits" ]; then
  echo "$hits"
  bad "em dashes found"
fi

step "this repo's installed hooks match the template"
for f in template/.claude/hooks/*.sh; do
  cmp -s "$f" ".claude/hooks/$(basename "$f")" || bad ".claude/hooks/$(basename "$f") differs from $f (run: cp template/.claude/hooks/*.sh .claude/hooks/)"
done

step "hook self-test"
bash template/.claude/hooks/selftest.sh || bad "selftest"

step "installer"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
git -C "$tmp" init -q
bash install.sh "$tmp" >"$tmp/.log" 2>&1 || bad "install exited non-zero"
for f in CLAUDE.md .claude/settings.json .claude/hooks/require-green.sh .claude/skills/ship/SKILL.md .claude/agents/reviewer.md; do
  [ -e "$tmp/$f" ] || bad "install did not create $f"
done
[ -x "$tmp/.claude/hooks/protect-paths.sh" ] || bad "hooks are not executable after install"
echo "my notes" >"$tmp/CLAUDE.md"
bash install.sh "$tmp" >"$tmp/.log2" 2>&1
[ "$(cat "$tmp/CLAUDE.md")" = "my notes" ] || bad "install overwrote an existing file"
grep -q "Skipped" "$tmp/.log2" || bad "install did not report skipped files"
HOME="$tmp/home" bash install.sh --user >/dev/null 2>&1 || bad "install --user failed"
[ -x "$tmp/home/.claude/hooks/notify.sh" ] || bad "install --user did not install notify.sh"
(cd "$tmp" && bash .claude/hooks/selftest.sh >/dev/null) || bad "selftest fails from an installed copy"

echo
if [ "$status" = 0 ]; then echo "all kit tests passed"; else echo "kit tests FAILED"; fi
exit $status
