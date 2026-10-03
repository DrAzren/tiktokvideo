"""Energy envelope of audio.wav in 10ms frames (dB re full scale) -> env_db.npy.
Used by build_edl.py to snap cut edges to where words really start/stop, and by
the edge plots.

This source carries continuous sub-100 Hz rumble (wind/HVAC/handling) under every pause,
so the envelope is measured on a 150 Hz-6 kHz band: only speech energy counts."""
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt

E = Path(__file__).parent
a, sr = sf.read(E / "audio.wav", dtype="float32")
a = sosfiltfilt(butter(4, [150, 6000], btype="band", fs=sr, output="sos"), a).astype(np.float32)
hop = sr // 100
n = len(a) // hop
frames = a[: n * hop].reshape(n, hop)
db = 10 * np.log10(np.mean(frames ** 2, axis=1) + 1e-10)
np.save(E / "env_db.npy", db.astype(np.float32))
print(f"{n} frames, median {np.median(db):.1f} dB, p10 {np.percentile(db, 10):.1f} dB, p90 {np.percentile(db, 90):.1f} dB")
