"""Turn narration timings into an edit plan: how long each shot lasts and where it starts.

    python plan.py <work_dir>

Reads episode.json and <work_dir>/words.json, writes <work_dir>/plan.json. Shots are timed
to the voice: a short lead-in before each line, a beat after it, a longer hold on the
last shot. Change the pacing here, not in the render or edit scripts.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEAD = 0.4  # seconds of picture before the narrator speaks
TAIL = 0.8  # breathing room after each line
END_HOLD = 2.0  # final shot holds longer so the video doesn't end on the last word


def main(work: Path) -> None:
    episode = json.loads((HERE / "episode.json").read_text())
    words = json.loads((work / "words.json").read_text())
    fps = episode["fps"]
    t = 0.0
    shots = []
    for i, shot in enumerate(episode["shots"]):
        vo = words[shot["id"]]["duration"]
        tail = END_HOLD if i == len(episode["shots"]) - 1 else TAIL
        frames = round((LEAD + vo + tail) * fps)  # whole frames, so audio and picture never drift
        shots.append({**shot, "start": round(t, 3), "frames": frames, "seconds": frames / fps, "vo_offset": LEAD})
        t += frames / fps
    (work / "plan.json").write_text(json.dumps({"fps": fps, "total_seconds": round(t, 3), "shots": shots}, indent=2))
    for s in shots:
        print(f"{s['id']}  {s['visual']:8}  start {s['start']:6.2f}s  {s['seconds']:5.2f}s  ({s['frames']} frames)")
    print(f"total {t:.2f}s")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
