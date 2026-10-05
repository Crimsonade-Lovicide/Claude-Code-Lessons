# Session log: how this repo was built

A plain-English record of everything Claude did in the Claude Code session that produced this repo, in order, including the work on other repositories. Written October 4, 2026.

## The short version

| What | Where it is now | Status |
|---|---|---|
| The Claude Code guide | `lessons/field-manual.html` in this repo | Done |
| The starter kit | `template/`, `user/`, `install.sh`, `tests/` in this repo | Done, tested, merged |
| This repo using the kit on itself | `.claude/` and `CLAUDE.md` at the root of this repo | Added in pull request #2 |
| The video course and demo pipeline | `video/` | Added in pull request #3 |
| A trial install in KAY 2.0 | Closed pull request #18 in the private KAY repo, plus one leftover branch | Stopped at the owner's request. KAY's main code and live app were never changed. |

## What the starter kit is, in plain terms

When Claude Code works inside a project, it reads a few special files from that project. Those files act as house rules and safety guards. The kit is a ready-made set of them:

| Rule | What it does |
|---|---|
| Project notes (`CLAUDE.md`) | Claude reads this at the start of every session: what the project is, how to test it, what never to do. |
| Protected files | Claude is blocked from editing files you list, such as password files (`.env`) or old database migrations. |
| Banned text | If Claude writes something you banned (an em dash by default), it is made to fix it immediately. |
| Auto-formatting | After Claude edits a file, the project's formatter tidies it. |
| Tests before "done" | When Claude tries to finish, the tests for what it changed run. If they fail, it has to keep fixing. |
| Ask before risky actions | Uploading code or deploying always asks first. Running tests does not. |
| `/spec`, `/ship`, `/catchup`, `/setup-kit` | Shortcut commands: plan before coding, wrap up and propose a change, summarize where a project stands, tailor the kit to a new project. |
| Reviewer | A second Claude that only reads and critiques changes and cannot edit anything. |

Rules like "don't edit password files" are enforced by small scripts (called hooks) that Claude Code runs automatically. That makes them guarantees, unlike a written instruction, which the model usually but not always follows.

## Timeline

### 1. The guide
- Asked to teach advanced Claude Code use, Claude had a helper agent check current Claude Code features against the official documentation. Some of what the helper reported looked wrong or invented, so Claude left those parts out.
- Claude wrote the guide as a web page and published it as a private claude.ai artifact. A copy is in this repo at `lessons/field-manual.html`.

### 2. Building the kit
- Asked to set up a real starter kit, Claude first opened KAY 2.0 to read its existing setup. KAY turned out to already have a project notes file and six of its own skills.
- The owner then asked for a fresh repo instead, so Claude stopped working in KAY and built the kit as a standalone project.
- Claude tried to create a new GitHub repository and was refused (GitHub returned "403, not accessible"). It built and tested the kit locally in the meantime.
- Testing done before anything was uploaded:
  - A 30-case self-test that feeds each hook the same data Claude Code sends it.
  - Shellcheck (a linter for shell scripts), JSON validity, and a check for em dashes across every file.
  - A full run under bash 3.2, which Claude compiled from source because macOS still ships that old version.
  - A trial on a **local, throwaway copy** of KAY 2.0 inside Claude's own sandbox. It confirmed the kit tests only the part of a project that changed, and blocks protected files. This copy was never uploaded anywhere.
  - The trial exposed one weakness: when tests failed, the report Claude received showed passing tests instead of the failure. This was fixed before upload.

### 3. This repo
- The owner created Claude-Code-Lessons. Claude made one small first commit on `main` (a one-line README) so there was something to propose changes against.
- Pull request #1 added the kit and the guide. Automated checks passed on Linux and on macOS. On the owner's instruction, Claude merged it.

### 4. KAY 2.0 (stopped)
After the merge, the owner said "merge it and install the kit." Claude read "install" as installing into KAY, which it had earlier offered as the next step. That was a misunderstanding.
- Claude created a separate branch in the private KAY repo, named `claude/beautiful-lamport-i1544i`, and added the kit tailored to KAY. A branch is a separate draft copy; the live app does not run from it.
- Claude opened draft pull request #18 to propose the change for review.
- Vercel automatically built a **preview** of the site from that branch, at its own separate link. The live site was not affected.
- The owner said KAY is live and must not be touched. Claude closed pull request #18 and stopped watching it.
- Claude started to delete the leftover branch; the owner stopped that action, so the branch still exists. It is inert. Per the owner's instruction, KAY is being left exactly as it is.
- **To see every line Claude wrote for KAY:** open the closed pull request #18 in the KAY repo and look at its "Files changed" tab. Those files are not copied here because this repo is public and they describe the internal layout of a live product.

### 5. This repo using the kit on itself (pull request #2)
The kit's rule files sit in `template/`, which is a box of parts for other projects. Claude does not follow rules stored there. Pull request #2 copies them into the places Claude actually reads (`.claude/` and `CLAUDE.md` at the root), adjusted for this repo:
- "Tests before done" runs this repo's own test suite.
- Claude may not edit `.claude/hooks/` directly, because those files must stay identical to `template/`. A new test fails if the two ever differ.
- The default rules about lockfiles, database migrations, Supabase and Vercel are removed, since this repo has none of those.

The same pull request fixes one small bug the self-install exposed: the em dash rule flagged the copy of its own rules file stored in `template/`. That copy is now exempt, and a new test covers it, bringing the self-test to 31 cases.

### 6. The video course (pull request #3)
Asked to teach programmatic video with free tools only, Claude:
- Had a research agent check the licences of about 25 free tools against their primary sources. Five popular options turned out to be unusable for free on a monetized channel.
- Built and ran a working pipeline in its cloud sandbox: Kokoro narration, Whisper timings, HTML motion graphics, a Blender scene, a synthesized score, an FFmpeg edit and mix, and automated QA. It rendered a finished 28-second video.
- Reviewed its own frames at each step and fixed what it found: flat lighting, a camera inside a building, misheard captions, a frozen-frame check fooled by grain, a colliding label, and a 51 Mbps export.
- Wrote ten lessons in `video/`, each tied to the demo code.

## Things the owner may still want to do
- **Install the personal files on your own computer.** These are your cross-project preferences and a desktop notification for when Claude needs you. Claude cannot reach your machine from its cloud sandbox. Run: `git clone https://github.com/Crimsonade-Lovicide/Claude-Code-Lessons && cd Claude-Code-Lessons && ./install.sh --user`
- **Decide about the leftover KAY branch.** Deleting `claude/beautiful-lamport-i1544i` in KAY would not affect the live app. Leaving it does no harm either.
