"""Render the 2D motion-graphics shots (title card, stat card) from HTML, frame by frame.

    python motion.py <work_dir> [--preview]

--preview renders three frames per shot (early, middle, end) into <work_dir>/preview/
so a design can be checked in seconds before rendering every frame.

Each page in motion/ exposes setup(data) and render(t, duration). This script opens the
page in headless Chromium, sets the time for every frame, and saves a screenshot, so the
animation is exact and repeatable: the same idea HyperFrames and Remotion are built on.
Writes <work_dir>/render/<shot>/0001.png, ...
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
FONTS = HERE / "models" / "fonts"
FONT_CSS = "https://fonts.googleapis.com/css2?family=Instrument+Serif&family=IBM+Plex+Mono:wght@400;600&display=swap"
PAGES = {"title": "title.html", "stat": "stat.html"}


def fetch_fonts() -> None:
    """Download the two free (SIL Open Font License) fonts once into models/fonts."""
    css_path = FONTS / "fonts.css"
    if css_path.exists() and css_path.stat().st_size > 0:
        return
    FONTS.mkdir(parents=True, exist_ok=True)
    # A minimal user agent gets one complete TTF per weight instead of many unicode subsets.
    req = urllib.request.Request(FONT_CSS, headers={"User-Agent": "Mozilla/5.0"})
    css = urllib.request.urlopen(req).read().decode()
    blocks = re.findall(r"@font-face \{.*?\}", css, re.S)
    out = []
    for block in blocks:
        url = re.search(r"url\((https://[^)]+)\)", block).group(1)
        name = url.rsplit("/", 1)[1]
        (FONTS / name).write_bytes(urllib.request.urlopen(url).read())
        out.append(block.replace(url, name))
    if not out:
        raise SystemExit("No fonts downloaded; the page would silently fall back to a default font.")
    css_path.write_text("\n".join(out))


def main(work: Path, preview: bool = False) -> None:
    fetch_fonts()
    plan = json.loads((work / "plan.json").read_text())
    fps = plan["fps"]
    with sync_playwright() as pw:
        # CHROMIUM_PATH lets you use an existing browser; otherwise run `playwright install chromium`.
        browser = pw.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        for shot in plan["shots"]:
            if shot["visual"] not in PAGES:
                continue
            out = work / ("preview" if preview else "render") / shot["id"]
            out.mkdir(parents=True, exist_ok=True)
            n = shot["frames"]
            frames = [int(n * 0.2), n // 2, n - 15] if preview else range(n)
            page.goto((HERE / "motion" / PAGES[shot["visual"]]).as_uri())
            page.evaluate("document.fonts.ready")
            page.evaluate("d => setup(d)", shot)
            for f in frames:
                page.evaluate("([t, d]) => render(t, d)", [f / fps, shot["seconds"]])
                page.screenshot(path=str(out / f"{f + 1:04d}.png"))
            print(f"motion {shot['id']}  {len(frames)} frames")
        browser.close()


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve(), preview="--preview" in sys.argv)
