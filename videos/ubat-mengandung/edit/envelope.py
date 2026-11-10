"""10 ms RMS energy envelope (dBFS) of edit/audio.wav -> env_db.npy (one value per 10 ms).

build_edl.py snaps cut edges to this; also prints the silence islands (speech runs separated by
>= GAP s below QUIET dB) that align.py uses as its island list.
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

E = Path(__file__).parent
QUIET, GAP = -40.0, 0.30

a, sr = sf.read(E / "audio.wav", dtype="float32")
hop = sr // 100
n = len(a) // hop
rms = np.sqrt(np.mean(a[: n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
db = 20 * np.log10(rms)
np.save(E / "env_db.npy", db.astype(np.float32))

if "--islands" in sys.argv:
    loud = db > QUIET
    isl, i = [], 0
    while i < n:
        if loud[i]:
            j = i
            while j < n and (loud[j] or (j + int(GAP * 100) < n and loud[j:j + int(GAP * 100)].any())):
                j += 1
            isl.append((i / 100, j / 100))
            i = j
        else:
            i += 1
    for k, (s, e) in enumerate(isl):
        print(f"{k:3d} {s:7.2f} {e:7.2f} {e - s:5.2f}")
print(f"{n} frames, {n / 100:.1f}s, median {np.median(db):.1f} dB")
