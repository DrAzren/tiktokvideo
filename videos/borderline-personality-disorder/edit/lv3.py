"""Unprompted faster-whisper large-v3 pass (no vocabulary/filler prompt — a prompt biases it).
Second opinion on wording and on what each short burst between words is.
Usage: lv3.py <audio> <out.json> [--clip START END]"""
import json
import sys

from faster_whisper import WhisperModel

src, dest = sys.argv[1], sys.argv[2]
kw = {}
if "--clip" in sys.argv:
    i = sys.argv.index("--clip")
    kw["clip_timestamps"] = [float(sys.argv[i + 1]), float(sys.argv[i + 2])]
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
segs, _ = m.transcribe(src, language="ms", word_timestamps=True, vad_filter=False,
                       condition_on_previous_text=False, **kw)
out = [{"start": s.start, "end": s.end, "text": s.text,
        "words": [{"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3),
                   "p": round(w.probability, 3)} for w in s.words]} for s in segs]
json.dump(out, open(dest, "w"), indent=1, ensure_ascii=False)
for s in out:
    print(f"[{s['start']:7.2f}-{s['end']:7.2f}] {s['text']}")
