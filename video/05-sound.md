# 05 · Voice, music and sound

Viewers forgive rough pictures far more readily than bad sound. Get the audio right first.

## Narration

### Options, best first

| Option | Cost | Quality | When |
|---|---|---|---|
| **Your own voice**, recorded well | Free | Highest trust; personality no model has | Your main channel, if you're willing to be its voice |
| **Kokoro-82M** (Apache-2.0) | Free | Clean, natural, slightly even in emotion | Faceless channels, second channels, drafts |
| **Chatterbox** (MIT) | Free | Expressive; clones a voice from a short sample | Pickups in *your* voice without re-recording |

Kokoro voices worth auditioning for documentary work: `bm_george`, `bm_lewis`, `bm_daniel` (British male), `am_michael`, `am_adam` (American male), `bf_emma`, `af_heart` (female). Pick one per channel and never switch mid-episode: listeners notice a narrator change even when they can't say what changed.

### Directing a TTS voice

Text-to-speech reads punctuation, not intent, so you direct it through the text:

| Want | Write |
|---|---|
| A pause | A full stop, or split the line into two takes |
| Emphasis on a number | Spell it out: "five hundred and twenty-eight" |
| A name said right | Respell it in the TTS text only ("Oberth" as "Oh-bert"); the captions still use the script's spelling |
| Slower, weightier | `speed=0.9` to `0.95` (the demo uses 0.95) |
| A dramatic beat | End the take, leave silence in the edit (`TAIL` in `plan.py`) |

Check every take by transcribing it: if Whisper hears different words from the script, listen to that line.

### Recording yourself for free

A quiet room with soft furnishings, a USB mic 15 to 20 cm away and slightly off-axis, and Audacity or QuickTime. Then clean up in code:

```bash
ffmpeg -i raw.wav -af "highpass=f=80,afftdn=nf=-25,acompressor=threshold=-20dB:ratio=3:attack=5:release=100,loudnorm=I=-20:TP=-2" vo.wav
```

High-pass removes rumble, `afftdn` removes steady noise, the compressor evens out the level, and `loudnorm` sets the narration level.

## Music

| Source | Licence | Notes |
|---|---|---|
| **YouTube Audio Library** (YouTube Studio > Audio Library) | Free for YouTube, monetization OK | Safest choice for YouTube specifically. Some tracks require attribution in the description |
| **Pixabay Music** (website) | Pixabay Content License | Commercial OK. The Pixabay API serves images and video only, so download music from the site |
| **Free Music Archive / ccMixter** | Per track (CC) | Only use tracks marked CC BY or CC0. Avoid NC (non-commercial) and ND (no derivatives) |
| **ACE-Step 1.5** (MIT) | Free, commercial OK | A local music model that runs in under 4 GB of GPU memory. On an M4, expect it to be slow; Kaggle works too (lesson 08) |
| **Stable Audio Open** | Free under $1M annual revenue, registration required | Short clips and sound design rather than full songs |
| **Code** (`music.py`) | Yours | Drones, pulses and pads are easy to synthesize and never trigger a copyright claim |

Even with a valid licence, YouTube's Content ID can occasionally flag library music. Keep the licence or download page for every track in your episode folder, so a dispute takes two minutes.

## Sound effects

**freesound.org** (filter to CC0, which needs no attribution), **Pixabay sound effects**, and **Sonniss's free GDC game-audio bundles** (large, royalty-free). A whoosh on a cut, a low hit on a title, room tone under silence: these small touches separate professional edits from amateur ones.

## The mix

Targets used by the demo, and by most documentary channels:

| Stem | Level | Why |
|---|---|---|
| Narration | -20 LUFS | The anchor everything else is set against |
| Music | about -33 LUFS, ducked about 8 dB more under speech | Present, never competing |
| Voice-to-music gap | at least 15 dB during speech | Below this, phone speakers blur the words |
| Master | **-14 LUFS integrated, true peak -1 dBTP** | YouTube plays everything at about -14; louder is turned down, quieter sounds weak |

How `edit.py` does it:

```
narration ─ loudnorm -20 ─┬───────────────────────────┐
                          └─► (key) ┐                 ├─ amix ─ loudnorm -14 (two-pass) ─► master
music ───── loudnorm -33 ─► sidechaincompress ────────┘
```

**Two-pass loudnorm**: the first pass measures, the second applies the exact correction. One pass guesses and can miss by several LU.

`qa.py` then measures the result. The demo's numbers: master -14.0 LUFS, true peak -1.0 dBTP, music 20 dB under the voice.

## What Claude can and can't judge here

Claude can measure loudness, peaks, gaps, silence and sync, and read transcripts. It cannot hear tone, warmth, a strained read, or music that clashes with the mood. **Listen to the final mix once, on headphones and on a phone speaker.** That is your job in every episode.
