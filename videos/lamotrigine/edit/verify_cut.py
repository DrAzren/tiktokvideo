"""Unprompted large-v3 pass over edit/cut.mp4: every kept word should be heard, no removed word should be."""
import subprocess
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

E = Path(__file__).parent
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(E / "cut.mp4"), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                     check=True, capture_output=True).stdout
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
segs, _ = m.transcribe(np.frombuffer(pcm, np.float32), language="ms", word_timestamps=True, condition_on_previous_text=False)
for s in segs:
    print(f"[{s.start:6.2f}-{s.end:6.2f}] " + " ".join(w.word.strip() + (f"({w.probability:.2f})" if w.probability < 0.5 else "")
                                                for w in s.words), flush=True)
print("DONE")
