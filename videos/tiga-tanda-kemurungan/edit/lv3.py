"""Unprompted faster-whisper large-v3 pass (Malay) — wording checks only.

A vocabulary/filler prompt biases Whisper, so this pass gets none; it settles what a
short burst actually is and gives punctuation for caption line breaks. Timestamps are
NOT used for cutting (forced alignment does that).

Usage: python lv3.py <audio.wav> <out.json>
"""

import json
import sys

from faster_whisper import WhisperModel

src, dst = sys.argv[1], sys.argv[2]
model = WhisperModel("large-v3", device="cpu", compute_type="int8")
segs, info = model.transcribe(src, language="ms", word_timestamps=True, beam_size=5,
                              vad_filter=False, condition_on_previous_text=False)
out = []
for s in segs:
    out.append({"start": s.start, "end": s.end, "text": s.text,
                "words": [{"text": w.word, "start": w.start, "end": w.end, "p": round(w.probability, 3)} for w in s.words]})
    print(f"{s.start:7.2f} {s.text}", flush=True)
json.dump(out, open(dst, "w"), ensure_ascii=False, indent=1)
