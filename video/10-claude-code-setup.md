# 10 · A Claude Code setup for a video channel

Lessons 03 to 09 give you the tools. This lesson turns them into a system: a repo that knows your channel, so each episode starts from "make episode 12" rather than from a blank prompt. It uses the starter kit from this repo's root (`install.sh`), extended for video.

## Repo layout

```
my-channel/
├── CLAUDE.md                 # the channel bible: voice, look, rules, commands
├── brand/                    # one folder per channel: tokens.css, fonts/, voice.json, intro/outro
│   ├── main/
│   └── second/
├── pipeline/                 # the demo's scripts, grown up: voice, plan, motion, blender, edit, qa
├── episodes/
│   └── 012-mile-high/
│       ├── research.md       # every claim with its source and a confidence tag
│       ├── script.md         # narration, with [S##] shot markers
│       ├── episode.json      # generated from script.md: what the pipeline reads
│       └── youtube.md        # title options, description, chapters, tags
└── .claude/                  # skills, agents, hooks, settings (below)
```

**Media stays out of git.** Renders, audio and footage go in a folder that isn't under version control (or cloud storage), referenced by path. Git holds only what's needed to *recreate* the video.

## CLAUDE.md: the channel bible

Keep it under about 120 lines. What earns a line:

```markdown
## Channel
Documentary channel: projects that were designed but never built. 8 to 12 min, 24 fps, 1080p.
Narrator: Kokoro bm_george, speed 0.95. Never switch voices inside an episode.

## Look
Tokens in brand/main/tokens.css. Dusk palette, gold accent, grain on everything.
Reconstructions labeled on screen. AI footage labeled "Illustration", never passed off as archive.

## Commands
- Preview: python pipeline/make.py work/012 --preview
- Final:   python pipeline/make.py work/012 --gpu
- QA only: python pipeline/qa.py work/012

## Rules
- Every number in script.md must trace to research.md with a source.
- Time picture to the voice: never stretch audio to fit picture.
- Mix: narration -20 LUFS, music -33 ducked, master -14 LUFS / -1 dBTP.
- Free tools only. Check the licence before adding any model or asset source.
```

## Skills: one per production step

Each is a folder in `.claude/skills/` with a `SKILL.md`. Invoke them as `/new-episode`, `/preview` and so on.

| Skill | What it does |
|---|---|
| `/new-episode <slug>` | Copies the episode template, starts `research.md` with a claims table |
| `/script` | Drafts or tightens `script.md` from `research.md`; refuses to add untagged facts |
| `/build` | Generates `episode.json` from the script and shot list |
| `/preview` | Runs `make.py --preview`, builds a frame grid, reviews it against `CLAUDE.md` |
| `/render` | Full render, then QA; reports failures with timestamps |
| `/package` | Writes titles, description, chapters (from the plan's shot times) and tags into `youtube.md` |
| `/publish` | Uploads as **private** with captions and a thumbnail; you flip it to public |

A minimal example, `.claude/skills/preview/SKILL.md`:

```markdown
---
name: preview
description: Render preview frames for the current episode and review them against the channel look.
disable-model-invocation: true
argument-hint: "<episode folder>"
allowed-tools: Bash(python pipeline/make.py:*), Bash(ffmpeg:*)
---
1. Run `python pipeline/make.py work/$ARGUMENTS --preview`.
2. Tile the preview frames into one grid image with ffmpeg and open it.
3. Review against "Look" in CLAUDE.md. For each problem: shot id, what is wrong, the fix.
4. Fix only scene or graphics code. Re-run the preview for the shots you changed. Stop after 2 rounds and report.
```

## Subagents: separate eyes

| Agent | Tools | Job |
|---|---|---|
| `fact-checker` | Read, WebSearch, WebFetch | Checks every claim in `script.md` against its source; flags anything untagged or unsupported |
| `retention-editor` | Read | Reads the script as a viewer: hook strength, dead stretches, act-break questions |
| `frame-critic` | Read | Reviews contact sheets against the look, without having built the shots, so it isn't biased toward them |

A reviewer that didn't make the work catches more. That is the whole point of a subagent here.

## Hooks: guarantees

| Hook | Event | Effect |
|---|---|---|
| QA gate | `Stop` | If `final.mp4` changed this turn and `qa.py` fails, Claude can't call the render done |
| Protect sources | `PreToolUse` on Edit/Write | Blocks edits to `research/sources/` (scans, PDFs) and to delivered episodes |
| No em dashes, banned phrases | `PostToolUse` | The starter kit's style guard, applied to scripts and on-screen text |

The starter kit already has the protect and style hooks; add the QA gate the same way as its test gate (`require-green.sh`), with `qa.py` as the command.

## MCP servers for a video repo

| Server | Why |
|---|---|
| Blender MCP | Live scene work (lesson 04) |
| Unreal MCP (5.8, experimental) | Live Unreal work (lesson 07) |
| Playwright MCP | Preview HTML graphics in a real browser |

Connect only what this repo uses. Every server adds tools to Claude's context.

## Publishing for free

The **YouTube Data API v3** costs nothing. Since June 2026 uploads have their own quota: **100 uploads a day**, at 1 unit each. Two catches:

1. Create OAuth credentials in Google Cloud (Desktop app type) and authorize once. Keep the token file out of git.
2. **Uploads from an API project that hasn't been verified by YouTube are forced to private** until the project passes an audit. That is fine for "upload private, then publish by hand", which is the safer workflow anyway.

A sketch of the upload (`pip install google-api-python-client google-auth-oauthlib`). Untested here, because it needs your Google account:

```python
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

creds = InstalledAppFlow.from_client_secrets_file(
    "client_secret.json", ["https://www.googleapis.com/auth/youtube.upload"]).run_local_server(port=0)
yt = build("youtube", "v3", credentials=creds)
video = yt.videos().insert(
    part="snippet,status",
    body={"snippet": {"title": TITLE, "description": DESCRIPTION, "categoryId": "27"},  # 27 = Education
          "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False}},
    media_body=MediaFileUpload("final.mp4", chunksize=-1, resumable=True)).execute()
yt.captions().insert(part="snippet", body={"snippet": {"videoId": video["id"], "language": "en", "name": "English"}},
                     media_body=MediaFileUpload("final.srt")).execute()
```

Thumbnails go through `yt.thumbnails().set(...)`. Your channel must be verified for custom thumbnails, which is a one-time phone check in YouTube Studio.

## Running two channels

Same pipeline, different brand folder. The demo doesn't have a `--brand` flag yet; adding one is a small first project to do with Claude:

```bash
python pipeline/make.py work/main-012   --brand brand/main
python pipeline/make.py work/second-004 --brand brand/second
```

Each brand folder holds its tokens, fonts, voice settings, intro and outro, and its own `CHANNEL.md` (tone, audience, format). `CLAUDE.md` points to them. One pipeline to improve, two identities to keep distinct. Keep the two channels' voices different enough that a viewer of both wouldn't confuse them.

## A weekly rhythm

| Day | You | Claude |
|---|---|---|
| 1 | Pick the topic | Research draft with sources; you verify the key facts |
| 2 | Approve the script | Script draft, retention and fact-check passes |
| 3 | Approve preview frames | Narration, plan, preview renders, frame review |
| 4 | Overnight render on the Mac | Full render, QA, fixes |
| 5 | Watch once, listen once, pick the thumbnail and title | Package, upload private |

Shorts come from the same assets: a vertical (9:16) crop of the strongest 30 to 50 seconds, word-by-word captions spelled from the script, and its own hook.
