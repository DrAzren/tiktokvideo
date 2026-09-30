"""Unprompted faster-whisper large-v3 pass (no vocabulary/filler prompt, which biases it) with
punctuation — second opinion on wording and on short ambiguous bursts. -> transcripts/large_v3.json"""
import json
from pathlib import Path

from faster_whisper import WhisperModel

E = Path(__file__).parent
model = WhisperModel("large-v3", device="cpu", compute_type="int8")
segs, info = model.transcribe(str(E / "audio.wav"), language="ms", word_timestamps=True,
                              vad_filter=False, condition_on_previous_text=False)
out = []
for s in segs:
    out.append({"start": s.start, "end": s.end, "text": s.text.strip(),
                "words": [{"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3),
                           "p": round(w.probability, 3)} for w in s.words or []]})
    print(f"[{s.start:7.2f}-{s.end:7.2f}] {s.text.strip()}", flush=True)
(E / "transcripts" / "large_v3.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
