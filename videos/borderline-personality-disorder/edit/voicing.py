"""Frame-level voicing (10ms hop, 40ms window) -> voicing.npy  [periodicity 0..1, f0 Hz].
Normalised autocorrelation peak in the 75-400 Hz lag range on 80 Hz-high-passed audio.
A run of strongly periodic, loud frames that lies OUTSIDE every aligned word is a
voiced hesitation ("aaa", "eee", "mmm"), which pause-shrinking never catches."""
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt

E = Path(__file__).parent
a, sr = sf.read(E / "audio.wav", dtype="float32")
a = sosfiltfilt(butter(4, 80, btype="high", fs=sr, output="sos"), a).astype(np.float32)
hop, win = sr // 100, int(0.04 * sr)
lo, hi = sr // 400, sr // 75
n = (len(a) - win) // hop
out = np.zeros((n, 2), np.float32)
for i in range(n):
    x = a[i * hop:i * hop + win]
    x = x - x.mean()
    e = float(np.dot(x, x))
    if e < 1e-6:
        continue
    f = np.fft.rfft(x, 2 * win)
    ac = np.fft.irfft(f * np.conj(f))[:win]
    ac /= ac[0]
    k = lo + int(np.argmax(ac[lo:hi]))
    out[i] = (ac[k], sr / k)
np.save(E / "voicing.npy", out)
print(n, "frames; periodic>0.6:", f"{(out[:, 0] > 0.6).mean():.0%}")
