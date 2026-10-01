"""Unprompted large-v3 on short windows (ambiguous bursts / long gaps) + energy runs inside each.
usage: burst_check.py t0-t1 [t0-t1 ...]"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

E = Path(__file__).parent
x, sr = sf.read(E / "audio.wav", dtype="float32")
db = np.load(E / "env_db.npy")
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
for arg in sys.argv[1:]:
    a, b = map(float, arg.split("-"))
    runs, cur = [], None
    for i in range(int(a * 100), int(b * 100)):
        on = db[i] > -30
        if on and cur is None:
            cur = i
        if not on and cur is not None:
            if i - cur >= 5:
                runs.append(f"{cur / 100:.2f}-{i / 100:.2f}")
            cur = None
    segs, _ = m.transcribe(x[int(a * sr):int(b * sr)], language="ms", word_timestamps=True, vad_filter=False,
                           condition_on_previous_text=False)
    ws = [f"{w.word.strip()}@{a + w.start:.2f}" for s in segs for w in (s.words or [])]
    print(f"[{a}-{b}] energy>-30dB runs: {' '.join(runs)}\n    lv3: {' '.join(ws)}")
