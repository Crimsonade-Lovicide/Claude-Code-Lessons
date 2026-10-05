# 06 · Motion graphics in code

Titles, maps, timelines, charts, quotes, lower thirds: in a documentary these carry the facts. Doing them in code gives you a consistent brand and exact numbers, and Claude can make them for you.

## The core trick

Write every animation as **a function of time**: given `t`, draw exactly what the frame at `t` should look like. Then render by stepping `t` frame by frame and capturing each image. Never use real-time playback or timers.

This gives you three things a timeline editor can't:

- **Determinism.** The same input gives the same video, every run.
- **Random access.** Render or check frame 137 alone.
- **Data in, video out.** Change a number in the script and the chart redraws itself.

The demo's `motion/stat.html` is about 60 lines. It reads two heights from `episode.json` and animates bars to scale, with counters and a half-height marker timed to the narration.

## Which tool

| Tool | Licence | Language | Best for | Watch out for |
|---|---|---|---|---|
| **Plain HTML + Playwright** (the demo) | Free | HTML/CSS/JS + Python | Cards, charts, lower thirds; zero extra installs | You write the frame loop yourself (about 40 lines) |
| **HyperFrames** (HeyGen) | Apache-2.0 | HTML/CSS + seekable animation | The same idea, productized: deterministic MP4 from HTML via a CLI | Young project. HeyGen's *hosted* render service is a separate, paid product |
| **Remotion** | Free for companies of up to 3 people | React | Complex, data-driven or templated video; large ecosystem | A fourth employee means a paid licence. A proposed change would count contractors too |
| **Motion Canvas** | MIT | TypeScript | Explainer animation with a visual editor | No stable release since Dec 2024 |
| **Revideo** | MIT | TypeScript | Motion Canvas with headless rendering and an API | Now maintained by the Midrender team |
| **Manim** (Community) | MIT | Python | Maths, diagrams, physics, anything 3Blue1Brown-like | Not for photographic or editorial looks |
| **Blender** | GPL | Python | 3D titles, globes, map flyovers, depth and real lighting | Slow to render |

**Recommendation for a documentary channel:** HTML (or HyperFrames) for editorial cards and lower thirds; Manim when the subject is physics or maths; Blender for anything that should feel physical (globes, terrain, a camera flying over a map). Stay with one per job, so the look stays consistent.

## HyperFrames with Claude Code

HyperFrames ships a Claude Code plugin, so Claude learns its conventions without you pasting docs:

```bash
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
```

It renders locally from a CLI and needs Node 22. HeyGen also offers a hosted MCP that renders in their cloud: that is the paid path, and it's disabled for CLI agents anyway. Use the local plugin.

## Remotion in one paragraph

A video is a React component, and `useCurrentFrame()` gives you `t`. `npx create-video@latest` scaffolds a project, `npx remotion studio` gives a live preview, `npx remotion render` writes the MP4. It is the most capable option for templated series (the same layout, new data each episode). Read the licence first: free for individuals and companies of up to three people.

## A brand system, once

Put your look in one place, so every card on every channel stays consistent. The demo's version is `motion/common.css`:

```css
:root {
  --bg: #0b0d10;  --ink: #f2ede4;  --muted: #8b8f98;  --gold: #c9a25c;
  --serif: "Instrument Serif", Georgia, serif;
  --mono: "IBM Plex Mono", Menlo, monospace;
}
```

For a second channel, copy the file and change the tokens: same pipeline, different identity. Use fonts under the SIL Open Font License (most of Google Fonts), and bundle them locally. The demo downloads them on first run and refuses to render if they're missing, because a silent fallback font is an easy mistake to ship.

## Motion rules that read as professional

| Rule | Demo example |
|---|---|
| Ease everything (smootherstep or similar) | `ease()` in `common.js` |
| Stagger related elements by 40 to 80 ms | The headline reveals letter by letter, 45 ms apart |
| Time reveals to the words that mention them | The "half a mile" line appears as the narrator says "half" |
| Add a slow push across the whole shot | `stagePush()`: 3.5% over the shot |
| Use subtle grain on flat graphics | Matches the grain on the 3D shots, so cuts don't jump |
| Hold finished frames long enough to read | About 1 second per 3 words on screen |
| Fade to black only where the story pauses | The title fades out before the first 3D shot |

## Checking graphics without watching

Render three frames per card (early, middle, end) and put them in a grid: `python motion.py work --preview`. Claude reads the grid and catches overlapping text, labels running together and bars that aren't to scale. The demo's first stat card had its two labels running into each other; the preview grid caught it before the full render.
