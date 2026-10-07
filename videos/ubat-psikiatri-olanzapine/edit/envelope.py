"""Energy envelope of edit/audio.wav at 100 fps (20 ms RMS window, 10 ms hop) in dBFS → env_db.npy.
build_edl.py snaps cut edges to it; islands.txt lists speech islands (runs above -40 dB, gaps >= 0.35 s)."""
from pathlib import Path

import numpy as np
import soundfile as sf

E = Path(__file__).parent
a, sr = sf.read(E / "audio.wav", dtype="float32")
hop, win = sr // 100, sr // 50
n = len(a) // hop
pad = np.pad(a, (win // 2, win))
rms = np.array([np.sqrt(np.mean(pad[i * hop:i * hop + win] ** 2) + 1e-12) for i in range(n)])
db = 20 * np.log10(rms + 1e-9)
np.save(E / "env_db.npy", db.astype(np.float32))

loud = db > -40
isl, i = [], 0
while i < n:
    if loud[i]:
        j = i
        while j < n and (loud[j] or np.any(loud[j:j + 35])):
            j += 1
        isl.append((i / 100, j / 100))
        i = j
    else:
        i += 1
with open(E / "islands.txt", "w") as f:
    for k, (s, e) in enumerate(isl):
        f.write(f"{k:3d} {s:7.2f} {e:7.2f} {e - s:5.2f}\n")
print(f"{n / 100:.1f}s, {len(isl)} islands; median level {np.median(db):.1f} dB, p95 {np.percentile(db, 95):.1f} dB")
