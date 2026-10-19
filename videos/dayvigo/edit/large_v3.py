"""Unprompted faster-whisper large-v3 pass (a vocabulary prompt biases wording; this one doesn't).
Used to settle wording disputes and to classify short bursts (breath vs. real word)."""
import json
import sys
from pathlib import Path

import soundfile as sf
from faster_whisper import WhisperModel

src, dest = Path(sys.argv[1]), Path(sys.argv[2])
model = WhisperModel("large-v3", device="cpu", compute_type="int8")
segs, info = model.transcribe(sf.read(src, dtype="float32")[0], language="ms", word_timestamps=True, vad_filter=False,
                              condition_on_previous_text=False)
words = []
for s in segs:
    print(f"[{s.start:7.2f}-{s.end:7.2f}] {s.text.strip()}", flush=True)
    words += [{"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3),
               "p": round(w.probability, 3)} for w in s.words or [] if w.word.strip()]
dest.write_text(json.dumps({"language": info.language, "words": words}, indent=1, ensure_ascii=False))
print("wrote", dest)
