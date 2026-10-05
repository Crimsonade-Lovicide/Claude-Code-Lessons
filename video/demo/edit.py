"""Assemble picture and sound into the finished video with FFmpeg.

    python edit.py <work_dir>

Reads plan.json, render/<shot>/####.png, vo/<shot>.wav, words.json and music.wav.
Writes <work_dir>/final.mp4 and final.srt.

Mix targets (the same ones used on a real documentary channel):
  narration    -20 LUFS
  music        about -33 LUFS, ducked a further ~8 dB while the narrator speaks
  master       -14 LUFS integrated, true peak no higher than -1 dBTP (YouTube's playback level)
"""
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONT = next((HERE / "models" / "fonts").glob("-F6q*.ttf"), None)  # IBM Plex Mono SemiBold


def run(cmd):
    subprocess.run(cmd, check=True)


def picture(work: Path, plan: dict) -> Path:
    """One clip per shot at 1920x1080, then a lossless-enough concat."""
    fps = plan["fps"]
    clips = []
    for shot in plan["shots"]:
        src = work / "render" / shot["id"] / "%04d.png"
        out = work / "clips" / f"{shot['id']}.mp4"
        out.parent.mkdir(exist_ok=True)
        vf = ["scale=1920:1080:flags=lanczos", "format=yuv420p"]
        if shot["visual"] == "blender":
            # Match the 2D cards: a little grain, a gentle vignette, and the honesty label.
            vf[1:1] = ["noise=alls=5:allf=t", "vignette=PI/5"]
            if shot.get("label") and FONT:
                label = shot["label"].replace(":", r"\:")
                vf.insert(-1, f"drawtext=fontfile='{FONT}':text='{label}':x=80:y=h-110:fontsize=26:"
                              "fontcolor=0xF2EDE4@0.85:borderw=0:shadowcolor=black@0.6:shadowx=2:shadowy=2")
            # Fade in from black, since the previous card fades out to black.
            vf.insert(-1, "fade=t=in:st=0:d=0.5")
        run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(fps), "-i", str(src),
             "-frames:v", str(shot["frames"]), "-vf", ",".join(vf),
             "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-r", str(fps), str(out)])
        clips.append(out)
    listing = work / "clips" / "list.txt"
    listing.write_text("".join(f"file '{c}'\n" for c in clips))
    out = work / "picture.mp4"
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(out)])
    return out


def narration(work: Path, plan: dict) -> Path:
    """Place each line at its shot's start plus lead-in, on one 48 kHz track."""
    inputs, filters = [], []
    for i, shot in enumerate(plan["shots"]):
        inputs += ["-i", str(work / "vo" / f"{shot['id']}.wav")]
        ms = int(round((shot["start"] + shot["vo_offset"]) * 1000))
        filters.append(f"[{i}]aresample=48000,adelay={ms}|{ms}[v{i}]")
    mix = "".join(f"[v{i}]" for i in range(len(plan["shots"])))
    filters.append(f"{mix}amix=inputs={len(plan['shots'])}:normalize=0,apad,atrim=0:{plan['total_seconds']}[vo]")
    out = work / "vo_track.wav"
    run(["ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", "[vo]", str(out)])
    return out


def measure(path: Path, filters: str) -> dict:
    """First loudnorm pass: measure, so the second pass can hit the target exactly."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", filters + ":print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stderr[r.stderr.rindex("{"):])


def mix(work: Path, vo: Path, plan: dict) -> Path:
    # Narration and music each normalized on their own, then music ducked under the voice.
    graph = (
        "[0]loudnorm=I=-20:TP=-2:LRA=11,aformat=channel_layouts=stereo,asplit=2[vo][key];"
        "[1]loudnorm=I=-33:TP=-6:LRA=11[mus];"
        "[mus][key]sidechaincompress=threshold=0.02:ratio=6:attack=40:release=600:makeup=1,asplit=2[duck][duckstem];"
        "[vo][duck]amix=inputs=2:normalize=0[pre]"
    )
    pre = work / "premaster.wav"
    # Also keep the ducked music on its own, so QA can measure the voice-to-music gap.
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(vo), "-i", str(work / "music.wav"),
         "-filter_complex", graph, "-map", "[pre]", "-ar", "48000", str(pre),
         "-map", "[duckstem]", "-ar", "48000", str(work / "music_ducked.wav")])
    target = "loudnorm=I=-14:TP=-1:LRA=11"
    m = measure(pre, target)
    second = (f"{target}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
              f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    out = work / "master.wav"
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(pre), "-af", second, "-ar", "48000", str(out)])
    return out


def script_words(script: str, heard: list) -> list:
    """Caption text comes from the script; only the timing comes from Whisper.

    Whisper mishears names ("Wright" -> "right") and rewrites numbers ("five hundred and
    twenty-eight" -> "528"). Align the two word lists, keep Whisper's times where words
    match, and spread the time of any mismatched stretch evenly over the script's words.
    """
    norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())
    said = script.split()
    matcher = difflib.SequenceMatcher(a=[norm(w) for w in said], b=[norm(w["word"]) for w in heard], autojunk=False)
    out = []
    for op, a0, a1, b0, b1 in matcher.get_opcodes():
        if op == "equal":
            out += [{"word": said[a0 + k], "start": heard[b0 + k]["start"], "end": heard[b0 + k]["end"]} for k in range(a1 - a0)]
            continue
        if a1 == a0:
            continue  # Whisper heard words the script doesn't have: drop them
        start = heard[b0]["start"] if b1 > b0 else (out[-1]["end"] if out else 0.0)
        end = heard[b1 - 1]["end"] if b1 > b0 else (heard[b0]["start"] if b0 < len(heard) else start + 0.3 * (a1 - a0))
        step = (end - start) / (a1 - a0)
        out += [{"word": said[a0 + k], "start": start + k * step, "end": start + (k + 1) * step} for k in range(a1 - a0)]
    return out


def captions(work: Path, plan: dict) -> Path:
    """SRT from the word timings: lines of up to 7 words, never across a shot change."""
    words = json.loads((work / "words.json").read_text())

    def ts(sec):
        ms = int(round(sec * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

    cues = []
    for shot in plan["shots"]:
        offset = shot["start"] + shot["vo_offset"]
        ws = script_words(shot["narration"], words[shot["id"]]["words"])
        for i in range(0, len(ws), 7):
            chunk = ws[i:i + 7]
            text = re.sub(r"\s+([,.!?])", r"\1", " ".join(w["word"] for w in chunk))
            cues.append((offset + chunk[0]["start"], offset + chunk[-1]["end"], text))
    srt = "".join(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n" for i, (a, b, t) in enumerate(cues, 1))
    out = work / "final.srt"
    out.write_text(srt)
    return out


def main(work: Path) -> None:
    plan = json.loads((work / "plan.json").read_text())
    pic = picture(work, plan)
    master = mix(work, narration(work, plan), plan)
    srt = captions(work, plan)
    final = work / "final.mp4"
    # Delivery encode. The working clips are near-lossless (crf 14) and grain makes them huge;
    # copying them through gave about 50 Mbps. YouTube re-encodes anyway: 10 to 20 Mbps is plenty.
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(pic), "-i", str(master),
         "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
         "-maxrate", "20M", "-bufsize", "40M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
         "-shortest", "-movflags", "+faststart", str(final)])
    print(f"wrote {final}\nwrote {srt}")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
