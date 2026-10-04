---
name: setup-kit
description: Tailor the Claude Code starter kit to this repository right after installing it. Fills in CLAUDE.md, test and format settings, protected paths and permissions.
disable-model-invocation: true
---
The starter kit was just installed into this repo. Customize it so every piece reflects how this project actually works.

1. Explore first: package manifests, lockfiles, CI config, README, docs, test setup, migration folders, generated files, and `.env*` files (names only, never contents). Note whether it is a monorepo.
2. `CLAUDE.md`: replace every TODO with facts from this repo. Commands must be exact and real: confirm each one exists in a manifest, and run the cheap ones. Stay under 120 lines. If the repo already had a CLAUDE.md before the kit, keep everything the user wrote and only add what is missing.
3. `.claude/kit.conf`: by default the Stop hook runs the `test` script of the nearest package.json for each changed file. Set `KIT_TEST_CMD` only if that would be wrong or too slow, and explain why. Leave `KIT_FORMAT_CMD` empty if the project's Prettier or ruff should be used.
4. `.claude/protected-paths`: add this repo's real secret files, generated files (for example generated database types) and append-only folders. Remove default rules that do not apply.
5. `.claude/settings.json`: add allow rules for this repo's read-only and test commands (for example `Bash(npm --prefix web test:*)`). Never allow anything that deploys, pushes, sends messages, or writes to a database.
6. Run `bash .claude/hooks/selftest.sh` and confirm it passes.
7. Report what you changed, anything you were unsure about, and what the user should review. Do not commit.
