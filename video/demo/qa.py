"""Automatic quality checks on a finished video, plus a contact sheet for a visual review.

    python qa.py <work_dir>

Checks the things that most often go wrong and are tedious to catch by eye:
  - loudness: -14 LUFS integrated (+/- 1), true peak no higher than -1 dBTP
  - voice clarity: narration at least 15 dB louder than the ducked music
  - picture: no unintended black stretches or frozen frames
  - delivery: 1920x1080, 24 fps, H.264 + AAC, sensible bitrate, audio and video the same length
Writes <work_dir>/qa.json and <work_dir>/contact_sheet.png (one frame per second), which
Claude can open and critique like an editor. Exit code 1 if any check fails.
"""
import json
import re
import subprocess
import sys
from pathlib import Path


def ff(args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args], capture_output=True, text=True).stderr


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def loudness(path, extra=None):
    log = ff(["-i", str(path), *(extra or []), "-af", "ebur128=peak=true", "-f", "null", "-"])
    i = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", log)[-1])
    peak = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", log)[-1])
    return i, peak


def main(work: Path) -> None:
    final = work / "final.mp4"
    plan = json.loads((work / "plan.json").read_text())
    info = probe(final)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next(s for s in info["streams"] if s["codec_type"] == "audio")
    checks = []

    def check(name, ok, detail):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    check("resolution", (v["width"], v["height"]) == (1920, 1080), f"{v['width']}x{v['height']}")
    check("frame rate", v["r_frame_rate"] == f"{plan['fps']}/1", v["r_frame_rate"])
    check("codecs", v["codec_name"] == "h264" and a["codec_name"] == "aac", f"{v['codec_name']} + {a['codec_name']}")
    dv, da = float(v["duration"]), float(a["duration"])
    mbps = int(info["format"]["bit_rate"]) / 1e6
    check("bitrate", 6 <= mbps <= 25, f"{mbps:.1f} Mbps (6 to 25 for 1080p24 upload)")
    check("audio/video length", abs(dv - da) < 0.1, f"video {dv:.2f}s, audio {da:.2f}s")

    lufs, peak = loudness(final)
    check("integrated loudness", abs(lufs + 14) <= 1.0, f"{lufs:.1f} LUFS (target -14)")
    check("true peak", peak <= -0.9, f"{peak:.1f} dBTP (max -1)")

    # Narration is normalized to -20 LUFS in the mix; the ducked music stem should sit well below it.
    music_i, _ = loudness(work / "music_ducked.wav")
    gap = -20 - music_i
    check("voice over music", gap >= 15, f"narration -20 LUFS, music {music_i:.1f} LUFS: {gap:.1f} dB gap (min 15)")

    black = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", ff(["-i", str(final), "-vf", "blackdetect=d=0.6:pix_th=0.06", "-an", "-f", "null", "-"]))
    check("no long black", not black, f"{len(black)} stretch(es) of black over 0.6 s" + (f": {black}" if black else ""))
    # Shrink and blur first: film grain changes every frame and would hide a frozen shot.
    frozen = re.findall(r"freeze_start: ([\d.]+)", ff(["-i", str(final), "-vf", "scale=160:90,gblur=sigma=1.5,freezedetect=n=0.001:d=1.5", "-an", "-f", "null", "-"]))
    check("no frozen picture", not frozen, f"{len(frozen)} freeze(s) over 1.5 s" + (f" at {frozen}" if frozen else ""))

    cols = 6
    rows = max(1, -(-int(dv) // cols))
    ff(["-y", "-i", str(final), "-vf", f"fps=1,scale=480:-1,tile={cols}x{rows}:padding=6:color=black", "-frames:v", "1", str(work / "contact_sheet.png")])

    (work / "qa.json").write_text(json.dumps(checks, indent=2))
    for c in checks:
        print(f"{'PASS' if c['ok'] else 'FAIL'}  {c['check']:22} {c['detail']}")
    print(f"contact sheet: {work / 'contact_sheet.png'}")
    sys.exit(0 if all(c["ok"] for c in checks) else 1)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
