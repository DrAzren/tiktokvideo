"""Unprompted faster-whisper large-v3 pass (wording check; a vocabulary prompt biases it)."""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel

E = Path(__file__).parent
out = E.parent / "captions_src" / "large_v3.json"
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(E / "audio.wav"), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                     check=True, capture_output=True).stdout
model = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=4)
segs, info = model.transcribe(np.frombuffer(pcm, np.float32), language="ms", word_timestamps=True,
                              vad_filter=False, condition_on_previous_text=False)
res = []
for s in segs:
    res.append({"start": s.start, "end": s.end, "text": s.text.strip(),
                "words": [{"text": w.word.strip(), "start": w.start, "end": w.end, "p": round(w.probability, 3)} for w in s.words]})
    print(f"[{s.start:7.2f}-{s.end:7.2f}] {s.text.strip()}", flush=True)
out.write_text(json.dumps(res, indent=2, ensure_ascii=False))
