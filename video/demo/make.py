"""Run the whole pipeline: voice, plan, graphics, 3D, music, edit, QA.

    python make.py <work_dir> [--preview] [--gpu] [--samples 16] [--only voice,plan,...]

--preview  renders 2 frames per 3D shot and 3 per graphics shot instead of every frame,
           so a full pass takes a minute or two. Check the frames, then run without it.
--gpu      renders Blender on the GPU (Metal on Apple Silicon).
--only     runs just the named stages, in pipeline order.

Blender is found from $BLENDER, then the macOS app, then `blender` on PATH.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGES = ["voice", "plan", "motion", "blender", "music", "edit", "qa"]


def blender_path() -> str:
    for candidate in (os.environ.get("BLENDER"), "/Applications/Blender.app/Contents/MacOS/Blender", shutil.which("blender")):
        if candidate and Path(candidate).exists():
            return candidate
    sys.exit("Blender not found. Install it (brew install --cask blender) or set BLENDER=/path/to/blender.")


def py(script, *args):
    subprocess.run([sys.executable, str(HERE / script), *args], check=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("work")
    p.add_argument("--preview", action="store_true")
    p.add_argument("--gpu", action="store_true")
    p.add_argument("--samples", type=int, default=16)
    p.add_argument("--only", default=",".join(STAGES))
    a = p.parse_args()
    work = Path(a.work).resolve()
    work.mkdir(parents=True, exist_ok=True)
    only = [s for s in STAGES if s in a.only.split(",")]

    for stage in only:
        print(f"\n== {stage}")
        if stage == "voice":
            py("voice.py", str(work))
        elif stage == "plan":
            py("plan.py", str(work))
        elif stage == "motion":
            py("motion.py", str(work), *(["--preview"] if a.preview else []))
        elif stage == "blender":
            plan = json.loads((work / "plan.json").read_text())
            for shot in plan["shots"]:
                if shot["visual"] != "blender":
                    continue
                out = work / ("preview" if a.preview else "render") / shot["id"]
                cmd = [blender_path(), "-b", "-P", str(HERE / "blender_scene.py"), "--",
                       "--out", str(out), "--seconds", str(shot["seconds"]), "--camera", shot["camera"],
                       "--samples", str(a.samples), "--engine", "CYCLES_GPU" if a.gpu else "CYCLES"]
                if a.preview:
                    cmd += ["--frames", f"1,{shot['frames']}"]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
                print(f"blender {shot['id']} -> {out}")
        elif stage == "music":
            py("music.py", str(work))
        elif stage in ("edit", "qa"):
            if a.preview:
                print("skipped in --preview (needs every frame)")
                continue
            if stage == "edit":
                py("edit.py", str(work))
            else:
                subprocess.run([sys.executable, str(HERE / "qa.py"), str(work)])  # report even on failure


if __name__ == "__main__":
    main()
