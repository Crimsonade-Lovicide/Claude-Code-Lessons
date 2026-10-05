"""A placeholder score synthesized in code: a slow, dark pad with a low pulse.

    python music.py <work_dir>

Writes <work_dir>/music.wav, exactly as long as the edit. It is copyright-free because it
is generated here, but it is a placeholder: for real episodes use a properly licensed
track (see lesson 05). The point is that the edit never waits on music, and the mix
can be tested from day one.
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

RATE = 48000
# D minor progression: Dm9, Bbmaj7, Fmaj7/A, Csus2. Frequencies in Hz.
CHORDS = [
    [73.42, 146.83, 174.61, 220.00, 261.63, 329.63],
    [58.27, 116.54, 146.83, 174.61, 220.00, 293.66],
    [55.00, 110.00, 130.81, 174.61, 220.00, 261.63],
    [65.41, 130.81, 146.83, 196.00, 261.63, 293.66],
]


def pad(freqs, seconds, rng):
    t = np.arange(int(seconds * RATE)) / RATE
    out = np.zeros_like(t)
    for f in freqs:
        for detune in (-0.12, 0.0, 0.12):  # three slightly detuned voices per note: a chorus-like width
            phase = rng.uniform(0, 2 * np.pi)
            out += np.sin(2 * np.pi * (f + detune) * t + phase) / (1 + f / 220)
    swell = np.minimum(1, t / 2.5) * np.minimum(1, (seconds - t) / 2.5)  # slow attack and release
    return out * swell


def main(work: Path) -> None:
    plan = json.loads((work / "plan.json").read_text())
    total = plan["total_seconds"]
    rng = np.random.default_rng(1956)
    chord_len = 7.0
    n = int(total * RATE)
    music = np.zeros(n)
    start = 0.0
    i = 0
    while start < total:
        seg = pad(CHORDS[i % len(CHORDS)], chord_len + 2.5, rng)  # overlap chords for smooth changes
        a = int(start * RATE)
        b = min(n, a + len(seg))
        music[a:b] += seg[: b - a]
        start += chord_len
        i += 1
    # A soft low pulse, like a heartbeat under the pad, every 1.5 s.
    t = np.arange(n) / RATE
    pulse = np.sin(2 * np.pi * 41.2 * t) * np.exp(-((t % 1.5) * 6.0))
    music += 0.6 * pulse * np.minimum(1, t / 4)
    fade = np.minimum(1, (total - t) / 3.0)  # fade out over the final three seconds
    music *= np.clip(fade, 0, 1)
    music /= np.max(np.abs(music)) * 1.12
    stereo = np.stack([music, np.roll(music, 480)], axis=1)  # 10 ms offset for a little width
    sf.write(work / "music.wav", stereo, RATE)
    print(f"music  {total:.2f}s")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
