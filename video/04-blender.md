# 04 · 3D with Blender, driven by code

Blender is the strongest free 3D tool, and everything in it is reachable from Python. That makes it the natural 3D engine for Claude: it can build a scene, light it, animate a camera and render it without anyone opening the app.

## Three ways Claude works with Blender

| Mode | How | Best for |
|---|---|---|
| **Scripts, headless** | `blender -b -P scene.py -- args` | Repeatable shots, batch renders, CI, overnight jobs. The demo uses this |
| **Scripts, in the app** | Paste into Blender's Text Editor, press Run | Seeing the result instantly while tuning |
| **Live control over MCP** | Claude sends commands to the running Blender | Exploring: "make the tower taller", "show me from the lake" |

Rule: explore over MCP, then **write what you settled on into a script**. A script can be re-run, reviewed and versioned; a sequence of MCP clicks cannot.

## Headless rendering

```bash
blender -b -P blender_scene.py -- --out renders/S02 --seconds 7.4 --camera orbit --engine CYCLES_GPU
```

- `-b` runs without a window. `-P` runs a Python file. Arguments after `--` go to your script.
- On a Mac, the binary is `/Applications/Blender.app/Contents/MacOS/Blender`. The demo's `make.py` finds it for you.
- Start scripts with `bpy.ops.wm.read_factory_settings(use_empty=True)` so nothing from your own startup file leaks into the render.

## Building a scene from data

Look at `demo/blender_scene.py`. Its shape is the shape of most good scene scripts:

1. **Units first.** Metric, scale 1.0, model at real size. The tower is 1,609 m because the documented height is one mile. Real units make lenses, light and depth of field behave realistically.
2. **Geometry from numbers.** `tapered_prism()` builds the massing from dimensions. For a documentary, the numbers come from your research notes, and the code is the audit trail: anyone can see which dimension produced which shape.
3. **Materials from a few functions.** Principled BSDF for most surfaces. Procedural textures (the demo's lit windows use a brick texture as a window grid) cost nothing to store and never look tiled.
4. **A world, then one key light.** The physical sky texture plus one sun lamp. Two light sources that both draw a sun disc give two reflections in water: the demo hit exactly this.
5. **Camera last**, with eased motion (below).

## Camera moves that look professional

| Do | Why |
|---|---|
| Ease in and out (smoothstep) | Real cameras have mass; linear moves look robotic |
| Move slowly | 30 to 40 degrees of orbit over 7 seconds reads as "cinematic" at 24 fps |
| Use a target (Track To constraint) | The subject stays framed while the camera travels |
| Real focal lengths: 24 to 35 mm wide, 50 neutral, 85 to 200 mm compressed | Lens choice sets the mood as much as the move |
| Keep the camera outside geometry | Check the first and last frame of every move before rendering the middle |

## Lighting for drama

The demo's first frame was technically correct and visually dead: midday haze, flat front light. Three changes fixed it, and they apply to almost any architecture shot:

1. **Low sun, behind the subject.** It separates the building from the sky and makes the edges glow.
2. **Darker sky and ground** than feels natural. Contrast is what reads on a phone screen.
3. **Practical lights in the scene**: lit windows, glowing floor bands. They tell the eye the scale and the time of day.

Use the **AgX** view transform (Blender's default). It handles bright skies and dark cities in one frame without clipping.

## Cycles or EEVEE on an M4 Air

| | Cycles | EEVEE |
|---|---|---|
| What it is | Path tracer: physically accurate light | Real-time renderer: game-engine speed |
| Speed on M4 (estimate, not measured here) | Seconds to tens of seconds per 1080p frame, depending on samples and scene | Around a second per frame or less |
| Use for | Hero shots, anything with glass, water, sunsets | Previews, graphics-like 3D, long shots |
| GPU | `--engine CYCLES_GPU` uses Metal | Always GPU |

Practical recipe: render previews in EEVEE or at low samples, final shots in Cycles with **16 to 64 samples plus the denoiser**. Render at 960x540 and upscale (the demo does this) when time matters more than the last bit of sharpness. The MacBook Air has no fan, so long renders slow down as it heats up. Render in short batches, or overnight on a hard surface.

## Blender MCP: live control

`blender-mcp` (MIT; the package is now named `mcp-for-blender`) has two parts: an add-on inside Blender that listens for commands, and an MCP server Claude talks to.

```bash
uvx mcp-for-blender install-addon        # installs the Blender add-on
claude mcp add blender uvx mcp-for-blender
```

Then in Blender, open the sidebar (N), find the BlenderMCP tab, and click Connect. Claude can now inspect the scene, run Python inside Blender and take viewport screenshots.

Two cautions. It runs arbitrary Python inside Blender, so save your file before a session. It also sends anonymous usage telemetry by default; set `DISABLE_TELEMETRY=true` in the server's environment if you don't want that.

## Useful prompts

- "Build a massing model of [building] from the dimensions in research.md. Real units, one object per part, named `SM_<Project>_<Part>`."
- "Render frames 1 and the last frame of every camera move at 480x270 and show me a grid."
- "This frame looks flat. Relight it for dusk with the sun behind the tower, then show me before and after."
- "Turn what we just did over MCP into a script I can re-run."
