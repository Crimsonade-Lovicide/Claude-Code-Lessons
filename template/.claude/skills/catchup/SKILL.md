---
name: catchup
description: Rebuild context at the start of a fresh session. Summarizes what this branch is doing, what is done, and what comes next.
disable-model-invocation: true
allowed-tools: Bash(git status:*), Bash(git log:*), Bash(git diff:*), Bash(git branch:*), Bash(git ls-files:*)
---
- Branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -15`
- Uncommitted changes: !`git status --short`
- Diff size: !`git diff --stat HEAD`
- Specs: !`git ls-files docs/specs`

Read the changed files and the spec that matches this branch, if there is one. Then tell me, in 15 lines or fewer:
1. What this branch is for.
2. What is done.
3. What is in progress or broken.
4. The next 3 steps, most important first.

Do not change any files.
