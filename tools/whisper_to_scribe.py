"""Convert a `hyperframes transcribe --json` word array into Scribe-shaped JSON.

Fallback for when no ELEVENLABS_API_KEY is available. The output lands in
<edit>/transcripts/<stem>.json so video-use's pack_transcripts.py and
render.py (--build-subtitles) work unchanged.

Caveat: Whisper tends to drop or normalize fillers ("um", "uh"), so filler
removal is weaker than with Scribe. Silence gaps are still preserved, so
dead-air trimming works fine.

Usage:
    python tools/whisper_to_scribe.py <transcript.json> --edit-dir <edit> --name <source_stem>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def convert(words: list[dict]) -> dict:
    out: list[dict] = []
    prev_end: float | None = None
    for w in words:
        text = (w.get("text") or w.get("word") or "").strip()
        start, end = w.get("start"), w.get("end")
        if not text or start is None or end is None:
            continue
        if prev_end is not None and start > prev_end:
            out.append({"type": "spacing", "text": " ", "start": prev_end, "end": start})
        out.append({"type": "word", "text": text, "start": start, "end": end, "speaker_id": "speaker_0"})
        prev_end = end
    return {"text": " ".join(w["text"] for w in out if w["type"] == "word"), "words": out, "source": "whisper"}


def main() -> None:
    ap = argparse.ArgumentParser(description="hyperframes/Whisper word array -> Scribe JSON")
    ap.add_argument("transcript", type=Path)
    ap.add_argument("--edit-dir", type=Path, required=True)
    ap.add_argument("--name", required=True, help="Source video stem (matches the EDL source key)")
    args = ap.parse_args()

    data = json.loads(args.transcript.read_text())
    words = data if isinstance(data, list) else data.get("words", [])
    dest = args.edit_dir / "transcripts" / f"{args.name}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(convert(words), indent=2))
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
