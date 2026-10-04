# Personal preferences (every project)

<!-- Installed to ~/.claude/CLAUDE.md by ./install.sh --user. Applies to every repo you open.
     Project CLAUDE.md files add to this. Edit to taste. -->

## Writing
- No em dashes anywhere: code comments, commit messages, UI copy, docs. Use periods, commas, colons or parentheses.
- Plain, direct language. No hype, filler or sign-off summaries.

## Working style
- For changes touching more than about 3 files, or any data model, propose a plan before editing.
- Ask before changing database schemas, auth, billing, or anything compliance-related.
- When you finish, say what you verified and how. If you could not run something, say so.
- If a request is ambiguous in a way that changes the result, ask one focused question.

## Code
- TypeScript strict. Avoid `any` except at untyped vendor boundaries, and isolate it there.
- Small, conventional commits.
- Never commit secrets or `.env` files.
