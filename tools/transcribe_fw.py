"""Word-level transcription with faster-whisper → Scribe-shaped JSON.

Multilingual fallback when no ELEVENLABS_API_KEY is set (hyperframes' whisper
only ships English models + large-v3). An initial prompt full of fillers nudges
Whisper to keep "emm/err/uh" instead of normalizing them away.

Usage:
    python tools/transcribe_fw.py <audio_or_video> --edit-dir <edit> --name <stem> [--language ms] [--model medium]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from faster_whisper import WhisperModel

FILLER_PROMPT = {
    "ms": "Emm, err, ah, jadi, macam, kan, eh... Okay, so, emm, macam tu lah.",
    "en": "Umm, uh, like, you know, I mean... so, uh, yeah.",
}


def _load(path: Path):
    """16 kHz mono WAV → float32 array (bypasses PyAV, whose 15+ API breaks faster-whisper's
    decode_audio: "open() got an unexpected keyword argument 'metadata_errors'"). Other inputs
    are passed through as paths."""
    if path.suffix.lower() == ".wav":
        import soundfile as sf
        a, sr = sf.read(path, dtype="float32")
        if sr == 16000:
            return a if a.ndim == 1 else a.mean(axis=1)
    return str(path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--edit-dir", type=Path, required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--language", default=None)
    ap.add_argument("--model", default="medium")
    args = ap.parse_args()

    dest = args.edit_dir / "transcripts" / f"{args.name}.json"
    if dest.exists():
        print(f"cached: {dest}")
        return

    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        _load(args.input),
        language=args.language,
        word_timestamps=True,
        vad_filter=False,
        condition_on_previous_text=False,
        initial_prompt=FILLER_PROMPT.get(args.language or "", None),
    )
    words: list[dict] = []
    prev_end = None
    for seg in segments:
        for w in seg.words or []:
            text = w.word.strip()
            if not text:
                continue
            if prev_end is not None and w.start > prev_end:
                words.append({"type": "spacing", "text": " ", "start": prev_end, "end": w.start})
            words.append({"type": "word", "text": text, "start": round(w.start, 3),
                          "end": round(w.end, 3), "speaker_id": "speaker_0",
                          "logprob": round(w.probability, 3)})
            prev_end = w.end
        print(f"[{seg.start:7.2f}-{seg.end:7.2f}] {seg.text.strip()}", flush=True)

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({
        "language_code": info.language, "language_probability": info.language_probability,
        "text": " ".join(w["text"] for w in words if w["type"] == "word"),
        "words": words, "source": f"faster-whisper-{args.model}",
    }, indent=2, ensure_ascii=False))
    print(f"wrote {dest} (lang={info.language} p={info.language_probability:.2f})")


if __name__ == "__main__":
    main()
