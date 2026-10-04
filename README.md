# Claude Code Lessons

A tested Claude Code setup you can drop into any repository. It covers the layers that separate an expert setup from a default one: short always-on memory, procedures on demand, a fresh-eyes reviewer, guarantees enforced by hooks, and permission rules that cut prompts without opening holes.

Built for TypeScript and Node monorepos (Next.js, Supabase, `node --test`), with Python support where it is cheap.

## Lessons

[`lessons/field-manual.html`](lessons/field-manual.html) is the guide this kit implements: the mental model (context, authority, guarantees, concurrency), each layer with examples and a drill, the anti-patterns, and a four-week path. Download it and open it in a browser. The starter kit below is the hands-on half: install it, then work through the drills with it.

## Install

```bash
git clone https://github.com/Crimsonade-Lovicide/Claude-Code-Lessons
cd Claude-Code-Lessons
./install.sh ~/code/my-project          # project kit
./install.sh ~/code/my-project --user   # plus personal files in ~/.claude
```

Then, in the target repo:

1. `bash .claude/hooks/selftest.sh` (31 checks, a few seconds)
2. Open Claude Code there and run `/setup-kit`. Claude reads the repo, fills in `CLAUDE.md`, and tunes test commands, protected paths and permissions.
3. Review the diff and commit `.claude/` and `CLAUDE.md` so every session (yours, cloud, CI) gets the same setup.

The installer never overwrites a file. Anything that already exists (an existing `CLAUDE.md`, for example) is listed so you can merge it by hand or ask Claude to.

Requires `jq` (`brew install jq`). macOS 15 and later ship it.

## What you get

| Piece | Where | What it does |
|---|---|---|
| Project memory | `CLAUDE.md` | Template for the always-on context: commands, rules, gotchas, what to ask before doing. |
| Protected paths | `hooks/protect-paths.sh` + `.claude/protected-paths` | Blocks edits to secrets, lockfiles and applied migrations *before* they happen. Supports exceptions (`!.env.example`) and append-only folders (`existing:supabase/migrations/*` allows new migrations, blocks editing old ones). |
| Style guard | `hooks/style-guard.sh` + `.claude/banned-patterns` | Checks only the text Claude just wrote against regex rules and makes it fix violations immediately. Ships with a no-em-dash rule. |
| Formatter | `hooks/format-on-edit.sh` | Runs the project's own Prettier (or ruff) on each edited file. Never blocks. |
| Stop gate | `hooks/require-green.sh` | Claude cannot end a turn while tests fail for what it changed. In monorepos it tests only the packages that changed. Skips docs-only changes, caches green results, and reports the actual failing assertions. |
| Cloud setup | `hooks/session-start.sh` | In Claude Code cloud sessions, installs dependencies for every lockfile so tests work from turn one. No-op locally. |
| `/spec` | skill | Interviews you one question at a time, then writes `docs/specs/<name>.md`. No code. |
| `/ship` | skill | Checks, reviewer pass, conventional commit, push (asks you), draft PR. |
| `/catchup` | skill | Rebuilds context in a fresh session from the branch, diff and specs. |
| `/setup-kit` | skill | Tailors the kit to the repo after install. |
| `reviewer` | subagent | Read-only skeptical reviewer that reports findings with `file:line`, a failure scenario and a fix. |
| Permissions | `.claude/settings.json` | Allows read-only git and test commands; asks before push, publish, deploy and database pushes; denies reading `.env` and key files. |
| Personal | `user/` (with `--user`) | `~/.claude/CLAUDE.md` with your cross-project preferences, and a desktop notification when Claude needs you. |

## The workflow it is built for

```
/spec add conflict checks to intake      # interview, then a written spec
/clear
Implement docs/specs/conflict-checks.md step by step. Run the tests after each step.
                                         # hooks format, guard and gate as Claude works
/ship                                    # verify, review, commit, draft PR
```

Next morning, in a fresh session: `/catchup`.

## Customize

| To change | Edit |
|---|---|
| What the Stop gate runs, or turn it off | `.claude/kit.conf` (`KIT_TEST_CMD`, `KIT_STOP_GATE=0`) |
| The formatter | `.claude/kit.conf` (`KIT_FORMAT_CMD="npx biome format --write {file}"`) |
| Files Claude may not touch | `.claude/protected-paths` |
| Text Claude may not write | `.claude/banned-patterns` (`<regex> :: <message>`) |
| Commands that never prompt | `permissions.allow` in `.claude/settings.json` (team) or `.claude/settings.local.json` (just you) |

Hooks run automatically with your user permissions. Read any hook before you add it, including these.

## Limits worth knowing

- Bash permission rules match command prefixes. They are not a security boundary: `deny` on `curl` does not stop `python -c ...`. Use `/sandbox` or a container for real isolation.
- `protect-paths` guards Claude's file-editing tools. It does not stop a shell command like `echo x > .env`; the `.env` deny rules and the ask rules cover the common cases.
- The Stop gate skips a package whose dependencies are not installed and says so, rather than blocking on a missing `node_modules`.
- Keep the gate fast. If your full suite takes minutes, point `KIT_TEST_CMD` at the unit tests and leave the rest to CI.

## Develop

This repo runs the kit on itself: see `.claude/` and `CLAUDE.md` at the root. Change hooks in `template/.claude/hooks/`, then sync them with `cp template/.claude/hooks/*.sh .claude/hooks/`. [SESSION-LOG.md](SESSION-LOG.md) records how this repo was built.

```bash
bash tests/run.sh   # syntax, shellcheck, JSON, frontmatter, house style, hook self-test, installer
```

CI runs the same script on Ubuntu and macOS. The macOS run matters: the hooks must work with the bash 3.2 that ships there.
