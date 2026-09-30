"""10ms RMS energy envelope (dB) of audio.wav -> env_db.npy (used by build_edl.py / edge_report.py)."""
from pathlib import Path

import numpy as np
import soundfile as sf

E = Path(__file__).parent
x, sr = sf.read(E / "audio.wav", dtype="float32")
hop = sr // 100
n = len(x) // hop
db = 20 * np.log10(np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1)) + 1e-9)
np.save(E / "env_db.npy", db.astype(np.float32))
print(f"{n} frames, floor p5={np.percentile(db, 5):.1f} dB, median={np.median(db):.1f} dB")
