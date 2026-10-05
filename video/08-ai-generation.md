# 08 · Free AI imagery and video

Paid generators (Kling, Veo, Runway, image models sold through resellers) are the easy path, and the one this course avoids. You can do the same work with open models on free GPUs. It is slower and the ceiling is lower, so use it where it earns its place.

## First, ask whether you need it

For documentaries about real things, the strongest visuals are usually not generated:

1. **Archive and public domain**: NASA, the Library of Congress, the Internet Archive, Wikimedia Commons (check each file's licence), national archives.
2. **Built in code**: Blender reconstructions and HTML or Manim graphics are exact, controllable and yours.
3. **Free stock**: Pexels and Pixabay for atmosphere (cities, weather, crowds).
4. **Generated**: for the shots none of the above can supply, such as a 1920s harbour, a mood, or an illustrative vignette.

When you do generate, **label it on screen** ("Illustration" or "AI illustration") and never present it as archival footage. That is an honesty rule, and YouTube's altered-content disclosure rules also apply to realistic synthetic media.

## The free models you may use commercially

| Model | Licence | Makes | GPU memory needed |
|---|---|---|---|
| **FLUX.1 [schnell]** | Apache-2.0 | Images, 1 to 4 steps, fast | About 24 GB at full precision; roughly 12 to 16 GB with 8-bit builds, less with 4-bit |
| **Wan 2.1 T2V 1.3B** | Apache-2.0 | Short video clips | About 8 GB |
| **Wan 2.2 TI2V 5B** | Apache-2.0 | 720p clips from text or an image | 24 GB, with offloading |
| **LTX-2** | Free under $10M annual revenue | Video, fast | Varies by variant |
| **Real-ESRGAN** | BSD-3 | 2x or 4x upscaling | Small |
| **RIFE** | MIT | In-between frames (24 to 48 fps, smooth slow motion) | Small |

Not FLUX.1 [dev] (non-commercial), and not HunyuanVideo if you or your audience are in the EU, UK or South Korea (lesson 02).

## Where to run them for free

Your MacBook Air can run FLUX schnell slowly (minutes per image) using Apple-Silicon builds such as `mflux`. It cannot realistically run video models: 16 GB shared memory is not enough, and there is no NVIDIA GPU.

**Kaggle notebooks** are the practical free GPU. A free, phone-verified account gets roughly 30 GPU-hours a week (an NVIDIA T4 or P100; check Kaggle's current quota). The workflow:

1. Claude writes a notebook: install the model, load your prompts from a file, generate, save to `/kaggle/working/`.
2. You upload it to kaggle.com, switch the accelerator to GPU, and run it.
3. Download the outputs, or save them as a Kaggle dataset.

Kaggle's GPUs have 16 GB each. That fits FLUX schnell in 8-bit and Wan 2.1 1.3B comfortably. Wan 2.2 5B officially wants 24 GB, so on Kaggle it needs community quantized builds (GGUF/FP8 via ComfyUI); I haven't tested those here, so treat them as an experiment.

Google Colab's free tier also offers GPUs, but availability is not guaranteed. Neither service is meant for unattended production at scale; batch your generation into one session a week.

Claude can't run Kaggle for you from a cloud session; you press Run. Everything else (prompts, code, file naming, picking the best takes from a contact sheet) it can do.

## Getting usable shots

| Do | Why |
|---|---|
| Generate a still first (FLUX), then animate it (Wan image-to-video) | Far more control than text-to-video |
| Keep a fixed style suffix on every prompt ("cinematic, desaturated, slight grain, no text, no logos, no identifiable people") | Shots match each other and your 3D renders |
| Make 4 to 8 seeds per shot, then have Claude pick from a contact sheet | Most takes fail; choosing is the real work |
| Keep clips short (3 to 6 s) and cut on motion | Open models drift in longer clips |
| Upscale with Real-ESRGAN, add the same grain as your other shots | Hides the "generated" sheen |
| Never upscale archive scans with AI | It invents detail in historical documents |

## The trade-off

Code-built shots (Blender, graphics) cost time once and then cost nothing per episode. Generated shots cost GPU time every episode and can't be precisely edited. Channels that look expensive usually lean on the first and use the second sparingly.
