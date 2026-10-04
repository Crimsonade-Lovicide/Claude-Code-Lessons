#!/usr/bin/env bash
# Self-test for the starter-kit hooks. Builds a throwaway git repo with its own
# fixture config, feeds each hook the JSON Claude Code would send, and checks the
# exit codes. Safe to run anywhere: it never touches the current repo.
#   bash .claude/hooks/selftest.sh
set -u
hooks=$(cd "$(dirname "$0")" && pwd)
pass=0
fail=0

if ! command -v jq >/dev/null 2>&1; then
  echo "selftest: jq is required by the hooks. Install it first (brew install jq, or apt install jq)."
  exit 1
fi

proj=$(mktemp -d)
trap 'rm -rf "$proj"' EXIT
out="$proj/.out"
err="$proj/.err"
EM=$(printf '\342\200\224') # the em dash, built from bytes so this file stays free of it

# run <hook> <json> [VAR=value ...]   sets $code, stdout in $out, stderr in $err
run() {
  local hook=$1 json=$2
  shift 2
  printf '%s' "$json" | env CLAUDE_PROJECT_DIR="$proj" "$@" bash "$hooks/$hook" >"$out" 2>"$err"
  code=$?
}

# expect <name> <expected exit code> [text that stderr or stdout must contain]
expect() {
  local name=$1 want=$2 needle=${3:-}
  if [ "$code" = "$want" ] && { [ -z "$needle" ] || grep -qF -- "$needle" "$out" "$err"; }; then
    pass=$((pass + 1))
    printf '  ok    %s\n' "$name"
  else
    fail=$((fail + 1))
    printf '  FAIL  %s (exit %s, wanted %s)\n' "$name" "$code" "$want"
    sed 's/^/        /' "$err" "$out" | head -n 20
  fi
}

edit_json() { jq -cn --arg f "$1" --arg s "${2:-x}" '{tool_name:"Edit",tool_input:{file_path:$f,old_string:"a",new_string:$s}}'; }
write_json() { jq -cn --arg f "$1" --arg c "${2:-x}" '{tool_name:"Write",tool_input:{file_path:$f,content:$c}}'; }

# Fixture project.
(
  cd "$proj" || exit 1
  git init -q
  git config user.email selftest@example.com
  git config user.name selftest
  mkdir -p .claude supabase/migrations web/node_modules/.bin src
  cat >.claude/protected-paths <<'EOF'
.env
.env.*
!.env.example
existing:supabase/migrations/*
EOF
  printf '%s\n' "$EM :: No em dashes." "console\.log\( :: Use the logger." >.claude/banned-patterns
  echo "select 1;" >supabase/migrations/0001_init.sql
  printf '{"name":"web","scripts":{"test":"node test.js"}}\n' >web/package.json
  printf 'const fs=require("fs");fs.appendFileSync("runs","x");if(fs.existsSync("FAIL"))process.exit(1);\n' >web/test.js
  printf 'runs\n.out\n.err\nnode_modules\n' >.gitignore
  # shellcheck disable=SC2016 # $a and $f belong to the fake prettier script
  printf '#!/bin/sh\nfor a; do f=$a; done\necho formatted >"$f.formatted"\n' >web/node_modules/.bin/prettier
  chmod +x web/node_modules/.bin/prettier
  echo "# readme" >README.md
  git add -A && git commit -qm init
)

echo "protect-paths"
run protect-paths.sh "$(edit_json "$proj/.env")"
expect "blocks .env" 2 "protected"
run protect-paths.sh "$(write_json "$proj/web/.env.local")"
expect "blocks nested .env.local by file name" 2
run protect-paths.sh "$(write_json "$proj/web/.env.example")"
expect "allows .env.example (exception rule)" 0
run protect-paths.sh "$(edit_json "$proj/supabase/migrations/0001_init.sql")"
expect "blocks editing an existing migration" 2
run protect-paths.sh "$(write_json "$proj/supabase/migrations/0002_new.sql")"
expect "allows creating a new migration" 0
run protect-paths.sh "$(edit_json "$proj/src/app.ts")"
expect "allows ordinary source files" 0
run protect-paths.sh "$(edit_json ".env")"
expect "handles relative paths" 2
run protect-paths.sh '{"tool_name":"Edit","tool_input":{}}'
expect "ignores input without a path" 0

echo "style-guard"
run style-guard.sh "$(write_json "$proj/src/a.ts" "const a = 1 $EM oops")"
expect "flags an em dash in new content" 2 "No em dashes"
run style-guard.sh "$(edit_json "$proj/src/a.ts" "console.log(x)")"
expect "flags a custom pattern in an edit" 2 "Use the logger"
run style-guard.sh "$(jq -cn --arg f "$proj/src/a.ts" --arg bad "bad $EM here" '{tool_name:"MultiEdit",tool_input:{file_path:$f,edits:[{old_string:"a",new_string:"fine"},{old_string:"b",new_string:$bad}]}}')"
expect "checks every edit in a MultiEdit" 2
run style-guard.sh "$(edit_json "$proj/src/a.ts" "clean text, no problems")"
expect "passes clean text" 0
run style-guard.sh "$(edit_json "$proj/.claude/banned-patterns" "$EM :: rule")"
expect "never flags the rules file itself" 0
run style-guard.sh "$(edit_json "$proj/template/.claude/banned-patterns" "$EM :: rule")"
expect "never flags a copy of the rules file elsewhere" 0

echo "format-on-edit"
echo "x" >"$proj/web/page.tsx"
run format-on-edit.sh "$(edit_json "$proj/web/page.tsx")"
if [ "$code" = 0 ] && [ -f "$proj/web/page.tsx.formatted" ]; then code=0; else code=1; fi
expect "runs the project's own Prettier on the edited file" 0
run format-on-edit.sh "$(edit_json "$proj/src/missing.ts")"
expect "ignores files that do not exist" 0

echo "require-green"
(cd "$proj" && git add -A && git commit -qm "format fixtures")
stop='{"hook_event_name":"Stop","stop_hook_active":false}'
run require-green.sh "$stop"
expect "skips when nothing changed" 0
echo "more" >>"$proj/README.md"
run require-green.sh "$stop"
expect "skips docs-only changes" 0
[ ! -f "$proj/web/runs" ] && code=0 || code=1
expect "did not run tests for docs-only changes" 0
echo "export const x = 1" >"$proj/web/lib.ts"
run require-green.sh "$stop"
expect "passes when the changed package's tests pass" 0
run require-green.sh "$stop"
expect "second stop with no new changes" 0
[ "$(cat "$proj/web/runs" 2>/dev/null)" = "x" ] && code=0 || code=1
expect "reuses the cached green result instead of rerunning" 0
touch "$proj/web/FAIL"
run require-green.sh "$stop"
expect "blocks when tests fail" 2 "Tests are failing"
run require-green.sh '{"hook_event_name":"Stop","stop_hook_active":true}'
expect "lets Claude stop on the retry (no infinite loop)" 0
run require-green.sh "$stop" KIT_STOP_GATE=0
expect "can be turned off with KIT_STOP_GATE=0" 0
printf 'KIT_STOP_GATE=0\n' >"$proj/.claude/kit.conf"
run require-green.sh "$stop"
expect "can be turned off in kit.conf" 0
printf 'KIT_TEST_CMD="echo custom-ran >custom.log"\n' >"$proj/.claude/kit.conf"
run require-green.sh "$stop"
[ "$code" = 0 ] && grep -q custom-ran "$proj/custom.log" 2>/dev/null && code=0 || code=1
expect "uses KIT_TEST_CMD when set" 0
rm -f "$proj/.claude/kit.conf" "$proj/web/FAIL" "$proj/custom.log"
mv "$proj/web/node_modules" "$proj/web/nm"
echo "export const y = 2" >>"$proj/web/lib.ts"
run require-green.sh "$stop"
expect "skips packages without installed dependencies and says so" 0 "dependencies not installed"
mv "$proj/web/nm" "$proj/web/node_modules"

echo "session-start"
run session-start.sh '{"hook_event_name":"SessionStart"}' CLAUDE_CODE_REMOTE=
[ "$code" = 0 ] && [ ! -s "$out" ] && code=0 || code=1
expect "does nothing outside cloud sessions" 0
shim="$proj/.shim"
mkdir -p "$shim"
printf '#!/bin/sh\nmkdir -p node_modules\necho "$*" >node_modules/.installed\n' >"$shim/npm"
chmod +x "$shim/npm"
mv "$proj/web/node_modules" "$proj/web/nm"
echo '{}' >"$proj/web/package-lock.json"
run session-start.sh '{"hook_event_name":"SessionStart"}' CLAUDE_CODE_REMOTE=true PATH="$shim:$PATH"
expect "installs missing dependencies in cloud sessions" 0 "installed dependencies in: web"
grep -q "^ci" "$proj/web/node_modules/.installed" 2>/dev/null && code=0 || code=1
expect "uses npm ci for package-lock projects" 0

echo
echo "selftest: $pass passed, $fail failed"
[ "$fail" = 0 ]
