# 03 · Anatomy of a video pipeline

A pipeline turns a script into a finished, checked video with one command. The demo in [`demo/`](demo/) is a complete small one. This lesson walks through it stage by stage. Run each stage yourself as you read.

## The one idea that matters most

**Time everything from the voice.** Record or generate the narration first, measure exactly when each word is spoken, then cut the picture, place the animations and write the captions from those measurements. The alternative, guessing durations and stretching audio to fit, is where most amateur pacing problems come from.

```
episode.json ─► voice ─► words.json ─► plan.json ─┬─► motion graphics ─┐
 (the script)   (TTS)    (Whisper)    (shot times) ├─► 3D renders ───────┼─► edit ─► final.mp4 ─► qa
                                                   └─► music ───────────┘   (mix,      + .srt
                                                                             captions)
```

Every arrow is a file on disk. Any stage can be re-run on its own, and Claude can inspect any intermediate file.

## The stages

### 1. The script: `episode.json`

One entry per shot: what is said, and what is seen. The visuals are *described as data* (`"visual": "blender"`, `"camera": "orbit"`), not as instructions in prose. That lets a program act on them and lets Claude edit them safely.

```json
{ "id": "S02", "visual": "blender", "camera": "orbit",
  "label": "MASSING STUDY · ILLUSTRATIVE",
  "narration": "He called it the Illinois. Five hundred and twenty-eight floors, reaching a full mile into the sky." }
```

For a full episode, keep your research and script in Markdown (with sources) and generate this file from them.

### 2. Voice: `voice.py`

Kokoro reads each shot's narration into its own WAV file; faster-whisper then transcribes each file with **word timestamps**. Measured on a 4-core CPU: 4 lines generated in about 19 seconds. Whisper's transcript doubles as a check: if it hears something different from the script, the voice probably mispronounced it.

One take per shot means you can re-record one line without touching the rest.

### 3. Plan: `plan.py`

Turns narration lengths into shot lengths: 0.4 s of picture before each line, 0.8 s after, 2 s on the final shot. Durations are rounded to **whole frames**, so sound and picture can never drift apart. Pacing lives in these three numbers and nowhere else.

### 4. Motion graphics: `motion.py` + `motion/*.html`

Title and stat cards are web pages. Each page exposes `render(t)`, which draws the card exactly as it should look at time `t`. The script opens the page in headless Chromium, calls `render` for every frame, and screenshots it. Because every frame is a pure function of time, renders are identical every run, and any frame can be checked on its own. Lesson 06 covers the frameworks that industrialize this idea.

### 5. 3D: `blender_scene.py`

Builds the whole scene in Python (tower, city, sky, camera move), then renders it headless. Lesson 04 goes deep.

### 6. Music: `music.py`

A placeholder score synthesized in code, exactly as long as the edit, so the mix can be built and tested on day one. Replace it with a licensed track for a real episode (lesson 05).

### 7. Edit: `edit.py`

FFmpeg does what an editor would:

| Step | How |
|---|---|
| Upscale 3D shots to 1080p, add matching grain and vignette, burn in the "illustrative" label | `scale`, `noise`, `vignette`, `drawtext` filters |
| Place each narration line at its shot's start plus lead-in | `adelay`, `amix` |
| Narration to -20 LUFS, music to -33 LUFS | `loudnorm` per stem |
| Duck the music while the narrator speaks | `sidechaincompress` keyed from the narration |
| Master to -14 LUFS, true peak -1 dBTP | Two-pass `loudnorm`: measure, then correct exactly |
| Captions | Script words aligned to Whisper's timings, so names are spelled right |

### 8. QA: `qa.py`

Measures what usually goes wrong: loudness, peaks, voice-to-music gap, black frames, frozen shots, resolution, frame rate, bitrate, sync. Then builds a contact sheet (one frame per second) for Claude or you to review. Lesson 09 explains each check.

## Run it

```bash
cd video/demo && source .venv/bin/activate
python make.py ../work --preview          # minutes: check the look first
python make.py ../work --gpu              # the real render
python make.py ../work --only edit,qa     # after changing only the edit or the mix
```

## What the build taught (so you don't learn it the slow way)

These all happened while building the demo, and each is now handled in the code:

1. **The first 3D frame was flat and washed out.** Sun behind the camera, sky too bright. Fixed by moving the light behind the subject and darkening the sky.
2. **A camera move started inside a building**, so the shot was pure black. Caught by rendering the first and last frame of every move before the full render (`--preview`).
3. **Film grain fooled the frozen-frame detector.** A shot that was secretly a still image passed, because grain changes every frame. The check now blurs and shrinks frames before comparing them.
4. **Whisper wrote "Frank Lloyd right".** Captions now take their spelling from the script and only their timing from Whisper.
5. **The font silently failed to download** and a fallback font would have shipped. The script now refuses to render without the real font.
6. **The first finished file was 180 MB for 28 seconds** (about 51 Mbps), because the near-lossless working clips were copied straight into the final file and film grain inflates them. Every check passed, because none looked at bitrate. The edit now does a proper delivery encode (13 Mbps, 46 MB), and QA checks the bitrate.
7. **A label collided with a number** on the height chart ("HALF A MILE" over "828 m"). Moving it left put it behind a bar. Found and fixed from the contact sheet, before anyone watched the video.

The pattern behind all seven: **make the cheap check before the expensive render, and make failures loud.**
