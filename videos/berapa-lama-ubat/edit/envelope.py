"""Energy envelope of the demucs vocal stem (vocals16k.wav; the source has CapCut music baked in) for edge snapping: RMS dBFS, 20ms window, 10ms hop -> env_db.npy (100 frames/s)."""
from pathlib import Path

import numpy as np
import soundfile as sf

E = Path(__file__).parent
a, sr = sf.read(E / "vocals16k.wav", dtype="float32")
hop, win = sr // 100, sr // 50
pad = np.pad(a, (win // 2, win))
n = len(a) // hop
frames = np.lib.stride_tricks.sliding_window_view(pad, win)[::hop][:n]
db = 20 * np.log10(np.sqrt((frames ** 2).mean(axis=1)) + 1e-6)
np.save(E / "env_db.npy", db.astype(np.float32))
print(f"{n} frames; p10={np.percentile(db, 10):.1f} p50={np.percentile(db, 50):.1f} p90={np.percentile(db, 90):.1f} dBFS")
