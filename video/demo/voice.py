"""Narration with Kokoro (free, local, Apache-2.0 weights), then word timings with faster-whisper.

    python voice.py <work_dir>

Writes <work_dir>/vo/<shot>.wav (24 kHz mono) and <work_dir>/words.json:
{ "S01": {"duration": 3.9, "words": [{"word": "In", "start": 0.12, "end": 0.2}, ...]}, ... }

Every later step (cuts, captions, animation timing) reads words.json, so the edit is
timed to the voice instead of the other way round.
"""
import ctypes.util
import json
import os
import sys
from pathlib import Path

import espeakng_loader
import soundfile as sf
from faster_whisper import WhisperModel
from kokoro_onnx import EspeakConfig, Kokoro

HERE = Path(__file__).resolve().parent
MODELS = HERE / "models"


def espeak_config() -> EspeakConfig:
    """Find espeak-ng, which Kokoro uses to turn text into phonemes.

    Prefers a system install (macOS: `brew install espeak-ng`, Linux: `apt install espeak-ng`)
    because some builds of the bundled copy look for their data at a path that only existed
    on the machine that built them. Override with ESPEAK_LIB and ESPEAK_DATA if needed.
    """
    lib = os.environ.get("ESPEAK_LIB") or ctypes.util.find_library("espeak-ng")
    if lib:
        candidates = [
            os.environ.get("ESPEAK_DATA"),
            "/opt/homebrew/share/espeak-ng-data",  # Homebrew on Apple Silicon
            "/usr/local/share/espeak-ng-data",
            "/usr/lib/x86_64-linux-gnu/espeak-ng-data",
            "/usr/lib/aarch64-linux-gnu/espeak-ng-data",
            "/usr/share/espeak-ng-data",
        ]
        data = next((c for c in candidates if c and Path(c, "phontab").exists()), None)
        if data:
            return EspeakConfig(lib_path=lib, data_path=data)
    return EspeakConfig(lib_path=espeakng_loader.get_library_path(), data_path=espeakng_loader.get_data_path())


def main(work: Path) -> None:
    episode = json.loads((HERE / "episode.json").read_text())
    (work / "vo").mkdir(parents=True, exist_ok=True)

    tts = Kokoro(str(MODELS / "kokoro-v1.0.onnx"), str(MODELS / "voices-v1.0.bin"), espeak_config=espeak_config())
    for shot in episode["shots"]:
        samples, rate = tts.create(
            shot["narration"],
            voice=episode["voice"],
            speed=episode["voice_speed"],
            lang=episode["voice_lang"],
        )
        sf.write(work / "vo" / f"{shot['id']}.wav", samples, rate)
        print(f"voice  {shot['id']}  {len(samples) / rate:.2f}s")

    whisper = WhisperModel("base.en", device="cpu", compute_type="int8", download_root=str(MODELS / "whisper"))
    timings = {}
    for shot in episode["shots"]:
        wav = work / "vo" / f"{shot['id']}.wav"
        segments, _ = whisper.transcribe(str(wav), word_timestamps=True, language="en")
        words = [
            {"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)}
            for seg in segments
            for w in seg.words
        ]
        timings[shot["id"]] = {"duration": round(sf.info(str(wav)).duration, 3), "words": words}
        heard = " ".join(w["word"] for w in words)
        print(f"heard  {shot['id']}  {heard}")
    (work / "words.json").write_text(json.dumps(timings, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
