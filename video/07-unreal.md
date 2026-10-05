# 07 · Unreal Engine 5

Unreal gives you real-time photoreal lighting (Lumen), effectively unlimited geometry (Nanite), huge free asset libraries (Fab, including the Quixel Megascans), and MetaHuman people. It is also a 100+ GB install that wants a strong GPU. Decide whether you need it before installing it.

## Is it free?

For video, yes. Under Epic's EULA, **linear content** (rendered video, film, YouTube) owes no royalty; the 5% royalty applies to games. A company with more than **$1M in annual gross revenue** that doesn't make games needs paid Unreal Subscription seats. *(Checked October 2026 from Epic's published terms as quoted by Epic; the EULA page itself was not directly readable, so confirm before you pass $1M.)*

## Will it run on a MacBook Air M4?

It runs: Unreal supports Apple Silicon. My assessment, not a benchmark: on a fanless Air with 16 GB shared between the CPU, the GPU and the OS, expect a slow editor on large scenes, long shader compiles, and thermal slowdown during renders. Small, focused scenes (one building, a sky, a camera move) are workable. City-scale scenes with Megascans and MetaHumans are not a good fit for this machine.

| Situation | Use |
|---|---|
| Massing models, skies, architectural flyovers | **Blender** (lesson 04): lighter, scriptable from the command line, and fine on the M4 |
| Photoreal environments, foliage, people, very large scenes | **Unreal**, ideally on a desktop with a dedicated GPU |
| You have both | Model in Blender, export FBX, light and render in Unreal: a common pipeline |

## How Claude drives Unreal

### Python editor scripting (stable)

Enable the **Python Editor Script Plugin**. Then any editor action can be scripted: import FBX files, create material instances, place actors, build Sequencer shots, queue renders. Run scripts from Tools > Execute Python Script, or from the command line. Claude writes these the same way it writes Blender scripts; the `unreal` module is documented in the editor's Python API reference.

### Unreal MCP (new, experimental)

Unreal 5.8 ships an **official MCP plugin** (`ModelContextProtocol`, marked experimental). It serves MCP on `http://127.0.0.1:8000/mcp` while the editor runs. In the editor's console, run:

```
ModelContextProtocol.GenerateClientConfig ClaudeCode
```

to generate the configuration for Claude Code. Community alternatives (all MIT), mostly for 5.5 to 5.7: `chongdashu/unreal-mcp`, `flopperam/unreal-engine-mcp`, `ChiR24/Unreal_mcp`.

As with Blender: explore over MCP, then commit what works to a Python script.

### Rendering from the command line

**Movie Render Queue** (and the node-based **Movie Render Graph**, production-ready in 5.8) can render a Level Sequence without opening the editor UI:

```bash
UnrealEditor-Cmd MyProject.uproject /Game/Maps/Main -game \
  -LevelSequence="/Game/Cinematics/SEQ_Flyover" \
  -MoviePipelineConfig="/Game/Cinematics/MRQ_Final" \
  -windowed -resx=1280 -resy=720 -log
```

*(Syntax from Epic's documentation as indexed in October 2026; the page itself returned empty when checked, so confirm against your engine version.)* On a Mac the binary lives inside `UnrealEditor.app/Contents/MacOS/`. Render to an **image sequence (PNG or EXR)**, not straight to video, then assemble and grade with FFmpeg exactly as in the demo's `edit.py`.

## Settings for cinematic output

| Setting | Value | Why |
|---|---|---|
| Frame rate | 24 fps everywhere: Sequencer, render, edit | Mixing rates causes judder and drift |
| Anti-aliasing | Temporal sample count 8 or more in Movie Render Queue | Removes shimmer on thin edges such as windows and wires |
| Warm-up frames | 30 or more | Lumen and motion blur need frames to settle; the first frames are otherwise wrong |
| Output | PNG/EXR sequence | Survives crashes; any frame can be re-rendered |
| Camera | Cine Camera Actor with real focal lengths and filmback | The same lens language as lesson 04 |

## Honest recommendation for this machine

Make Blender your main engine on the M4 Air. Learn Unreal on one small project (one building, one sky, one 10-second move) to see whether its look justifies its weight for your channel. If it does, the upgrade that matters is a desktop with an NVIDIA GPU, not a bigger laptop.
