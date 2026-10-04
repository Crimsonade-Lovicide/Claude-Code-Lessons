---
name: ship
description: Verify, review, commit, push and open a draft PR for the current work. Use when the user says ship it, wrap up, or open a PR.
disable-model-invocation: true
argument-hint: "[notes for the PR]"
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git branch:*), Bash(git switch:*), Bash(git add:*), Bash(git commit:*), Bash(gh pr create:*)
---
## Current state
- Branch: !`git branch --show-current`
- Status: !`git status --short`
- Diff size: !`git diff --stat HEAD`

## Steps
1. If the branch is `main` or `master`, create a branch named after the change (`feat/...`, `fix/...`, `chore/...`) and tell the user its name.
2. Run the checks listed under "Commands" in CLAUDE.md (typecheck, lint, tests) for every package you touched. Fix failures and rerun. If the same failure survives 3 rounds, stop and report it instead of guessing.
3. Ask the `reviewer` subagent to review the diff. Fix every high-severity finding. List the rest in the PR body under "Follow-ups".
4. Stage only the files that belong to this change. Never stage `.env` files, secrets, or unrelated edits. Commit with a conventional commit message (`feat: ...`, `fix: ...`).
5. Push with `git push -u origin HEAD`. The user will be asked to approve this.
6. Open a draft PR with `gh pr create --draft`. Body sections: Summary, Why, How it was verified (the exact commands and their results), Follow-ups. If `gh` is unavailable, give the user the branch name and compare URL instead.
7. Reply with the PR link and one line on anything left for the user.

Notes from the user: $ARGUMENTS
