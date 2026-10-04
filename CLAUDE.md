# CLAUDE.md

<!-- Loaded into every Claude Code session. Keep it short: every line costs context on every turn. -->

## What this is
A public repo that teaches advanced Claude Code use. Two halves: `lessons/field-manual.html` (the guide) and a starter kit people install into their own repos with `install.sh`. This repo also runs the kit on itself, so it is the first real user of every change.

## Repo map
- `template/` what `install.sh` copies into a target repo: `CLAUDE.md` and `.claude/` (hooks, skills, reviewer agent, settings, config files).
- `user/` personal files for `~/.claude`, installed with `--user`.
- `tests/run.sh` the kit's test suite. `template/.claude/hooks/selftest.sh` is the hook self-test it calls.
- `lessons/` the field manual, a standalone HTML page.
- `.claude/` this repo's own installed copy of the kit, tailored for this repo.
- `SESSION-LOG.md` a plain-English record of how this repo was built.

## Commands
- All tests: `bash tests/run.sh` (about 3s; syntax, shellcheck, JSON, frontmatter, no em dashes, hook self-test, installer)
- Hook self-test only: `bash template/.claude/hooks/selftest.sh`
- Sync this repo's hooks after changing the template: `cp template/.claude/hooks/*.sh .claude/hooks/`

## Rules
- Change hooks in `template/.claude/hooks/`, never in `.claude/hooks/` (that copy is protected). Sync afterwards; a test fails if the copies differ.
- Hooks must run on bash 3.2 (macOS). No associative arrays, `mapfile`, `${var,,}`, or `|&`. CI runs the suite on macOS with the system bash.
- Every hook behavior change gets a case in `selftest.sh`.
- `install.sh` must never overwrite an existing file.
- No em dashes anywhere. The only exceptions are the `banned-patterns` rules files, which must contain the character.
- This repo is public. Never add details from private projects (names of internal files, folder layouts, commands, credentials).

## Ask before
- Changing what `install.sh` writes into other people's repos, or the default permission rules in `template/.claude/settings.json`.
- Adding a dependency beyond bash, git and jq.

## Done means verified
Run `bash tests/run.sh` and report the result. The Stop hook runs it too and blocks finishing while it fails.
