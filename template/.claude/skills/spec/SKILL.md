---
name: spec
description: Interview the user and write an implementation spec before any code is written. Use for new features or any change touching several files.
disable-model-invocation: true
argument-hint: "<feature idea>"
---
Feature idea: $ARGUMENTS

1. Read enough of the codebase to ask informed questions: the modules involved, the data model, and existing patterns to follow. If that means more than a handful of files, use the Explore subagent so this conversation stays small.
2. Interview the user one question at a time, most important first. Cover the goal and who it is for, scope and non-goals, data model changes, edge cases and failure modes, security and privacy, and how we will know it works. Give your recommended answer with each question so the user can simply agree. Stop when the remaining unknowns are minor.
3. Write the spec to `docs/specs/<kebab-case-name>.md` with these sections: Problem, Goals, Non-goals, Design (files to change and why), Data model, Edge cases, Test plan, Rollout, Open questions.
4. Do not write implementation code. Finish by telling the user to run `/clear` and then say: "Implement docs/specs/<name>.md step by step. Run the tests after each step."
