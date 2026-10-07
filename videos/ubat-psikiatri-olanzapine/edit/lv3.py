"""large-v3 (faster-whisper) over the source with NO initial prompt (a vocabulary prompt biases it).
Used to fill segments medium skipped and to settle wording disputes. → transcripts/large_v3.json"""
import json
import sys
from pathlib import Path

import soundfile as sf
from faster_whisper import WhisperModel

E = Path(__file__).parent
a, sr = sf.read(E / "audio.wav", dtype="float32")
lo, hi = (float(sys.argv[1]), float(sys.argv[2])) if len(sys.argv) > 2 else (0, len(a) / sr)
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
segs, _ = m.transcribe(a[int(lo * sr):int(hi * sr)], language="ms", word_timestamps=True, vad_filter=False,
                       condition_on_previous_text=False, beam_size=5)
out = []
for s in segs:
    ws = [{"text": w.word.strip(), "start": round(lo + w.start, 3), "end": round(lo + w.end, 3), "p": round(w.probability, 3)} for w in s.words]
    out.append({"start": round(lo + s.start, 2), "end": round(lo + s.end, 2), "text": s.text.strip(), "words": ws})
    print(f"[{lo + s.start:7.2f}-{lo + s.end:7.2f}] {s.text.strip()}", flush=True)
name = "large_v3.json" if len(sys.argv) <= 2 else f"large_v3_{lo:g}_{hi:g}.json"
(E / "transcripts" / name).write_text(json.dumps(out, indent=1, ensure_ascii=False))
