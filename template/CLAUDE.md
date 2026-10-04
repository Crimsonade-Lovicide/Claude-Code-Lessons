# CLAUDE.md

<!-- Loaded into every Claude Code session, so every line costs context on every turn.
     Keep it under about 120 lines. Run /setup-kit to fill this in from the repo.
     When Claude repeats a mistake, add one line here that would have prevented it. -->

## What this is
TODO: one or two sentences. What the product does and who it is for.

## Repo map
TODO: top-level folders and what lives in each.

## Commands
TODO: exact commands. Claude runs these verbatim.
- Install:
- Dev server:
- All tests:
- One test file:
- Typecheck:
- Lint:

## Rules
TODO: conventions Claude cannot infer from the code. For example:
- Never edit an applied migration. Add a new one.
- All database access goes through one module. Name it here.

## Gotchas
TODO: things that cost you time. Generated files, required local services, flaky setup steps.

## Ask before
- Changing the database schema, auth, billing, or anything compliance-related.
- Adding a dependency.
- Deleting files you did not create in this session.

## Done means verified
Before saying a task is done, run the relevant tests and typecheck and report the results. A Stop hook blocks finishing while tests for changed code fail. If something could not be verified, say so plainly.

## Kit
This repo uses the Claude Code starter kit: hooks in `.claude/hooks/`, settings in `.claude/kit.conf`, protected paths in `.claude/protected-paths`, banned text in `.claude/banned-patterns`. Skills: /spec, /ship, /catchup, /setup-kit. Subagent: reviewer.
