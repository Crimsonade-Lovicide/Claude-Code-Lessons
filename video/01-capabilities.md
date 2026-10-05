# 01 · What Claude can and can't do with video

Know this before anything else: it decides how you split the work. These are facts about Claude Code as of October 2026, from building the demo in this folder.

## The core fact

**Claude does not generate video.** It has no camera and no video model. What it does is write and run the programs that make video: Blender, FFmpeg, a headless browser, text-to-speech models, Unreal Engine. That turns out to be a strength. Code is exact, repeatable, editable line by line, and free. A clip from a paid generator is none of those.

## What Claude can do

| Capability | How | Notes |
|---|---|---|
| Write the whole production pipeline | Python, shell, JavaScript, Blender's `bpy`, Unreal's Python API | The demo's 7 stages were written this way |
| Run renders unattended | `blender -b` (no window), FFmpeg, headless Chromium | Runs on your Mac, in CI, or in a cloud session |
| **See still frames** | Opens a PNG and describes what is in it | Used throughout the demo to catch a black shot, flat lighting, and unreadable windows |
| Critique like an editor | Compares frames against a brief: composition, contrast, legibility, consistency | As good as your brief is specific |
| Check sound by numbers | Loudness (LUFS), true peak, voice-to-music gap, silence | Via FFmpeg's `ebur128` and `loudnorm` |
| Understand speech | Transcribes narration with Whisper and gets word timings | That is how cuts and captions sync to the voice |
| Drive Blender or Unreal live | MCP servers that connect Claude to the running app | Lesson 04 and 07 |
| Write the words | Research, script, shot list, titles, descriptions, chapters | Fact-check anything it states (lesson 09) |
| Publish | YouTube Data API: upload, captions, thumbnail, chapters | Free quota (lesson 10) |

## What Claude cannot do

| Limit | Consequence | Workaround |
|---|---|---|
| **Cannot watch motion.** It sees single frames, not playback | Judder, bad pacing, awkward easing get past it | Contact sheets and frame pairs catch most problems; you watch the final cut once, every time |
| **Cannot hear.** It reads numbers and transcripts, not tone | It can't tell a flat read from a great one, or music that fights the mood | You listen to narration takes and music choices |
| No GPU in cloud sessions | Cloud renders are CPU-only (the demo's 3D shots took about 9 s per frame) | Run Claude Code on your Mac for GPU work, or use a free cloud GPU (lesson 08) |
| Can't click through apps that have no API | DaVinci Resolve's free version has no scripting at all since 21.1 | Do the edit in code (the demo does), or edit by hand |
| Taste is borrowed | It knows principles, not your channel's voice | Write your rules into `CLAUDE.md` (lesson 10) and correct it once |
| Facts can be wrong | Confident errors in dates, numbers, names | Source every claim (lesson 09) |

## How to split the work

Rule of thumb: **Claude does everything measurable and repeatable. You do everything that needs eyes on motion or ears on sound.**

| Claude | You |
|---|---|
| Research drafts and sourcing | Final call on every fact |
| Script drafts and tightening | The story and the opinion |
| Shot list timed to the narration | Approving the look from preview frames |
| All rendering, editing, mixing, captions | Watching the cut once, listening once |
| Automated QA and frame review | Choosing music and the voice |
| Uploading, metadata, chapters | Thumbnail choice, title choice |

## Two ways to run it

| | Claude Code on your Mac | Claude Code in the cloud (claude.ai/code) |
|---|---|---|
| GPU | Yes: Apple M4 through Metal | No |
| Blender and Unreal MCP | Yes: the apps are on your machine | No |
| Good for | 3D renders, anything interactive | Writing code, edits, QA, long CPU jobs while your laptop is closed |
| Files | Stay on your disk | Must be committed or uploaded; the container is temporary |

Most channels end up using both: the cloud for scripting, editing and checks, the Mac for anything that needs the GPU or a live app.
