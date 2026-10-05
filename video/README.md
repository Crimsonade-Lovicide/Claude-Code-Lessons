# Programmatic video with Claude Code

A course in making high-quality YouTube video with code, free tools only: no credits, no subscriptions, no resellers. Every technique here is used by the working demo in [`demo/`](demo/), which renders a finished 1080p video from a JSON script with one command.

Written for a MacBook Air M4 with 16 GB of memory (notes for other machines where it matters). Licences and versions were checked against primary sources in October 2026; they change, so recheck anything you build a business on.

## The lessons

| # | Lesson | You will be able to |
|---|---|---|
| 01 | [What Claude can and can't do with video](01-capabilities.md) | Decide what to hand to Claude and what to keep for yourself |
| 02 | [The free toolbox](02-toolbox.md) | Install everything on a Mac, and know which "free" tools you may not use on a monetized channel |
| 03 | [Anatomy of a video pipeline](03-pipeline.md) | Run the demo end to end and understand every stage |
| 04 | [3D with Blender, driven by code](04-blender.md) | Build, light and animate scenes from Python, and control Blender live through MCP |
| 05 | [Voice, music and sound](05-sound.md) | Get broadcast-quality narration and a legal score for free, and mix to YouTube's loudness |
| 06 | [Motion graphics in code](06-motion-graphics.md) | Make titles, charts and maps with HTML, HyperFrames, Remotion or Manim |
| 07 | [Unreal Engine 5](07-unreal.md) | Know when Unreal is worth it on your machine, and how Claude drives it |
| 08 | [Free AI imagery and video](08-ai-generation.md) | Generate illustrations and clips on free GPUs, legally, and label them honestly |
| 09 | [What "top-notch" means](09-quality.md) | Hold a professional quality bar, with automated checks and frame-by-frame review |
| 10 | [A Claude Code setup for a video channel](10-claude-code-setup.md) | Run one or more channels from a repo with skills, hooks, subagents and free uploading |

Start with 01 and 03. The others stand alone; read them when you reach that part of production.

## The demo in one minute

```bash
cd video/demo
python make.py ../work --preview   # 2 to 3 frames per shot, about a minute: check the look
python make.py ../work --gpu       # every frame, mixed, captioned, checked
open ../work/final.mp4
```

Setup is in [lesson 02](02-toolbox.md#install-on-a-mac). What it makes: a 28-second teaser about Frank Lloyd Wright's mile-high "Illinois" tower (1956, never built), with narration, a title card, a 3D dusk flyover of a massing model, a to-scale height comparison, a score, captions, and a mix at YouTube's -14 LUFS. Total spend: nothing.
