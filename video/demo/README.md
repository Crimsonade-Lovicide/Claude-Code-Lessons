# Demo: The Mile-High Tower

A 28-second documentary teaser, made from [`episode.json`](episode.json) with free tools only. It is the worked example for every lesson in [`../`](../README.md).

| Stage | Script | Tool | Output |
|---|---|---|---|
| Narration + word timings | `voice.py` | Kokoro, faster-whisper | `vo/*.wav`, `words.json` |
| Shot timing | `plan.py` | Python | `plan.json` |
| Title and stat cards | `motion.py`, `motion/*.html` | Headless Chromium | `render/S01/`, `render/S03/` |
| 3D shots | `blender_scene.py` | Blender 5.2, Cycles | `render/S02/`, `render/S04/` |
| Score (placeholder) | `music.py` | NumPy | `music.wav` |
| Edit, mix, captions | `edit.py` | FFmpeg | `final.mp4`, `final.srt` |
| Checks + contact sheet | `qa.py` | FFmpeg | `qa.json`, `contact_sheet.png` |
| All of the above | `make.py` | | |

## Run

Setup is in [lesson 02](../02-toolbox.md#install-on-a-mac). Then:

```bash
source .venv/bin/activate
python make.py ../work --preview    # a few frames per shot: check the look
python make.py ../work --gpu        # full render on the Mac's GPU (omit --gpu for CPU)
```

`work/` and `models/` are not in git: they hold generated media and downloaded models.

## Measured on a 4-core cloud CPU (no GPU)

| Stage | Time |
|---|---|
| Narration, 4 lines + Whisper | about 20 s |
| Title and stat cards, 315 frames | about 5 min |
| 3D, 348 frames at 960x540, 16 samples | about 9 s per frame |
| Edit, mix, captions, delivery encode | about 2.5 min |

On an M4 with `--gpu`, the 3D stage should be several times faster. Not measured here, because there's no Mac in this sandbox.

## Facts used in the script

| Claim | Status |
|---|---|
| Frank Lloyd Wright announced the Illinois in 1956 | Documented |
| One mile tall (1,609 m), 528 floors | Documented |
| Burj Khalifa, 828 m, tallest building standing (October 2026) | Documented |
| The tower's shape in the 3D shots | Massing study from published drawings: illustrative, labeled on screen |
