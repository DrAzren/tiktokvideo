"""large-v3 (no prompt) over the CUT audio → captions_src/large_v3_cut.json. Only its punctuation is used
(author_captions.py attaches clause ends to our forced-aligned words); its timestamps are ignored."""
import json
from pathlib import Path

import soundfile as sf
from faster_whisper import WhisperModel

C = Path(__file__).parent
a, sr = sf.read(C / "cut_audio.wav", dtype="float32")
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
segs, _ = m.transcribe(a, language="ms", word_timestamps=True, vad_filter=False, condition_on_previous_text=False, beam_size=5)
out = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
        "words": [{"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)} for w in s.words]} for s in segs]
(C / "large_v3_cut.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
for s in out:
    print(f'[{s["start"]:6.2f}-{s["end"]:6.2f}] {s["text"]}')
