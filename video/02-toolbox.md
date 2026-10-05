# 02 · The free toolbox

Everything below costs nothing to use on a monetized channel run by a company of one to three people. "Free" is not enough on its own: several popular models are free to download but forbid commercial use, and a monetized YouTube channel is commercial. Those are listed separately at the end.

Licences checked against primary sources (licence files, model cards, EULAs) in October 2026.

## The stack, layer by layer

| Layer | Use | Licence | Why this one |
|---|---|---|---|
| Glue | **Python 3.12**, **Node 22** | Free | Every other tool has a Python or JS interface |
| Video engine | **FFmpeg** | LGPL/GPL | Cuts, scaling, mixing, loudness, encoding, analysis. The one tool every pipeline needs |
| 3D | **Blender 5.2 LTS** | GPL (your renders are yours) | Full Python API, headless rendering, Metal GPU on M-series Macs |
| 3D, real-time | **Unreal Engine 5.8** | Free for linear content (video) under $1M annual revenue | Photoreal lighting; heavy on a laptop (lesson 07) |
| 2D graphics | **HTML + headless Chromium** (demo), **HyperFrames** (Apache-2.0), **Remotion** (free up to 3 employees), **Manim** (MIT) | as listed | Lesson 06 compares them |
| Narration | **Kokoro-82M** (Apache-2.0 weights) via `kokoro-onnx` (MIT) | Free, commercial OK | Natural voices, runs fast on a laptop CPU |
| Voice cloning | **Chatterbox** (MIT) | Free, commercial OK | Clone your own voice for pickups. Outputs carry an inaudible watermark |
| Speech to text | **faster-whisper** (MIT) | Free | Word timings for cuts and captions |
| Music generation | **ACE-Step 1.5** (MIT) | Free, commercial OK | Local music model; or use a licensed library (lesson 05) |
| Stock footage | **Pexels**, **Pixabay** | Free, commercial OK | Free APIs; no recognizable brands or logos from Pixabay |
| Public domain | NASA, Library of Congress, Internet Archive, Wikimedia Commons (check each file) | Varies, often PD | Ideal for documentaries about history and engineering |
| AI images | **FLUX.1 [schnell]** (Apache-2.0) | Free, commercial OK | Not the [dev] model: see below |
| AI video | **Wan 2.1 / 2.2** (Apache-2.0), **LTX-2** (free under $10M revenue) | as listed | Needs a big GPU: run on Kaggle for free (lesson 08) |
| Upscale / slow-mo | **Real-ESRGAN** (BSD), **RIFE** (MIT) | Free | Upscale renders, interpolate frames |
| Background removal | **rembg** (MIT) with `-m birefnet-general` | Free | The default model needs a paid licence for commercial use |
| Screen capture | **OBS Studio** (GPL), scriptable over its built-in websocket | Free | Tutorials and software demos |
| Manual editing | **DaVinci Resolve** free, **Kdenlive** (GPL) | Free | Resolve free has no scripting since 21.1; Kdenlive's MLT engine is scriptable |
| Uploading | **YouTube Data API v3** | Free quota | 100 uploads a day (lesson 10) |

## Install on a Mac

One-time setup on an Apple Silicon Mac (M1 to M4). Paste into Terminal one block at a time.

**1. Package manager and command-line tools**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install ffmpeg espeak-ng python@3.12 node uv git
brew install --cask blender     # Blender 5.2 LTS
```

`espeak-ng` turns text into phonemes for the Kokoro voice. `uv` runs MCP servers.

**2. Claude Code**: follow the current install instructions at code.claude.com/docs (they change; do not trust an old copy).

**3. Python environment for the demo**

```bash
cd video/demo
python3.12 -m venv .venv
source .venv/bin/activate
pip install kokoro-onnx soundfile faster-whisper playwright numpy
playwright install chromium
```

**4. Voice model** (about 350 MB, once)

```bash
mkdir -p models
curl -L -o models/kokoro-v1.0.onnx https://huggingface.co/fastrtc/kokoro-onnx/resolve/main/kokoro-v1.0.onnx
curl -L -o models/voices-v1.0.bin  https://huggingface.co/fastrtc/kokoro-onnx/resolve/main/voices-v1.0.bin
```

The Whisper model and the fonts download themselves on first run.

**5. Check it**

```bash
python make.py ../work --preview
```

**Optional apps**

| App | Install | When |
|---|---|---|
| Blender MCP | `uvx mcp-for-blender install-addon`, then `claude mcp add blender uvx mcp-for-blender` | To let Claude drive Blender live (lesson 04) |
| HyperFrames | `claude plugin marketplace add heygen-com/hyperframes` then `claude plugin install hyperframes@hyperframes` | HTML motion graphics with a Claude Code plugin (lesson 06) |
| Unreal Engine 5.8 | Epic Games Launcher (free account) | Lesson 07 first; it is a big install |
| OBS Studio | `brew install --cask obs` | Screen recordings |
| DaVinci Resolve | blackmagicdesign.com (free version) | Hand edits, colour work |

## What you can't use for free on a monetized channel

| Tool | Problem | Use instead |
|---|---|---|
| **Coqui XTTS-v2** | Licence allows non-commercial use of the model *and its outputs*; Coqui shut down, so there is no one to buy a licence from | Kokoro, Chatterbox |
| **F5-TTS** | Code is MIT, but the released weights are CC-BY-NC (non-commercial) | Kokoro, Chatterbox |
| **MusicGen** | Weights are CC-BY-NC | ACE-Step, a licensed library |
| **FLUX.1 [dev]** | The model may only be used for non-commercial purposes | FLUX.1 [schnell] |
| **Piper voices, some of them** | Engine is GPL and fine, but each voice has its own licence; some (for example `en_US-ryan`) are non-commercial | Check the voice's model card, or use Kokoro |
| **rembg default model** | `bria-rmbg` needs a paid agreement for commercial use | `rembg -m birefnet-general` |
| **DaVinci Resolve free, for automation** | No scripting at all since 21.1 | Do the edit in FFmpeg (the demo), or Kdenlive/MLT |
| **HunyuanVideo** | Licence does not apply in the EU, UK and South Korea, including viewing outputs there | Wan 2.2 |

## Paid tools this replaces

| Paid | Free replacement here | Honest trade-off |
|---|---|---|
| ElevenLabs narration | Kokoro, or your own recorded voice | ElevenLabs is more expressive. Your own voice beats both for trust |
| ElevenLabs music and SFX | ACE-Step, the YouTube Audio Library, freesound (CC0 filter) | More searching, less "type a prompt" |
| Image and video generators (Kling, GPT Image via resellers) | FLUX schnell and Wan 2.2 on a free Kaggle GPU | Slower, fewer clips per week, lower ceiling. Code-built visuals often look better anyway |
| After Effects | HTML/HyperFrames/Remotion, Manim, Blender | Code first instead of drag and drop; far easier to automate |

## Staying current

Licences change. Remotion has a proposed change that would count contractors toward its three-person limit; Resolve removed scripting from its free version in a point release. Before you build a channel on a tool, open its licence file and read the commercial-use clause yourself. Ask Claude to fetch and summarize it, then read the clause it quotes.
