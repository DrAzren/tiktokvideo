"""Unprompted large-v3 on the rendered cut: (1) proof that no removed filler is still audible,
(2) punctuation for the caption line breaks. -> captions_src/large_v3_cut.json"""
import json
from pathlib import Path

from faster_whisper import WhisperModel

C = Path(__file__).parent
segs, _ = WhisperModel("large-v3", device="cpu", compute_type="int8").transcribe(
    str(C / "cut.wav"), language="ms", word_timestamps=True, vad_filter=False, condition_on_previous_text=False)
out = [{"start": s.start, "end": s.end, "text": s.text.strip(),
        "words": [{"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)} for w in s.words or []]}
       for s in segs]
(C / "large_v3_cut.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print("\n".join(f"[{s['start']:6.2f}] {s['text']}" for s in out))
