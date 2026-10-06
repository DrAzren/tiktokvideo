"""Energy envelope of edit/audio.wav: RMS in dB per 10ms frame → env_db.npy (read by build_edl.py).

Also prints silence islands (speech runs separated by >= GAP s below QUIET_DB) as a first map
of the take, so the alignment islands in align.py can be drawn around them.
"""

from pathlib import Path

import numpy as np
import soundfile as sf

E = Path(__file__).parent
QUIET_DB, GAP = -40.0, 0.30

a, sr = sf.read(E / "audio.wav", dtype="float32")
hop = sr // 100
n = len(a) // hop
fr = a[: n * hop].reshape(n, hop)
db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
np.save(E / "env_db.npy", db.astype(np.float32))
print(f"{n} frames ({n / 100:.2f}s), peak {db.max():.1f} dB, median {np.median(db):.1f} dB")

loud = db > QUIET_DB
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
    print(f"S{k:02d} {s:7.2f}-{e:7.2f} ({e - s:5.2f}s)")
