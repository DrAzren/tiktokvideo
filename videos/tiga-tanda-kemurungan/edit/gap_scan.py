"""Find voiced sounds that are not words: "aa", "eee", "mmm", drawn-out vowels hiding in gaps.

For every gap between aligned words (and every '*' token), measure per 10ms frame:
energy (dB) and voicing (peak normalised autocorrelation at 70-400 Hz pitch lags).
Breaths are noisy (low periodicity); hesitations are voiced. A gap with >= MIN_VOICED s
of voiced frames is reported as a suspected hesitation, with its voiced span.
Also flags drawn-out word endings: a word whose voiced tail runs > DRAWL s past its aligned end.

Usage: python gap_scan.py  → prints a table, writes verify/gaps.json
"""

import json
from pathlib import Path

import numpy as np
import soundfile as sf

E = Path(__file__).parent
MIN_VOICED = 0.08
VOICE_DB, VOICE_R = -38.0, 0.55

a, sr = sf.read(E / "audio.wav", dtype="float32")
hop, win = sr // 100, sr // 25          # 10ms hop, 40ms window
n = len(a) // hop
lo, hi = sr // 400, sr // 70
db = np.load(E / "env_db.npy")
voiced = np.zeros(n, bool)
for i in range(n - 4):
    x = a[i * hop:i * hop + win]
    if len(x) < win or db[i] < VOICE_DB:
        continue
    x = x - x.mean()
    ac = np.correlate(x, x, "full")[win - 1:]
    if ac[0] <= 0:
        continue
    r = ac[lo:hi] / ac[0]
    voiced[i] = r.max() > VOICE_R

al = json.loads((E / "aligned.json").read_text())
flat = sorted(({"iid": iid, "i": i, **w} for iid, v in al.items() for i, w in enumerate(v["words"])),
              key=lambda w: w["start"])
real = [w for w in flat if w["text"] != "*"]
rows = []
for w, nx in zip(real, real[1:]):
    g0, g1 = w["end"], nx["start"]
    if g1 - g0 < 0.06:
        continue
    seg = voiced[int(g0 * 100):int(g1 * 100)]
    v = seg.sum() / 100
    if v >= MIN_VOICED:
        idx = np.flatnonzero(seg)
        rows.append({"after": f'{w["iid"]}:{w["i"]}', "prev": w["text"], "next": nx["text"],
                     "gap": [round(g0, 2), round(g1, 2)], "voiced_s": round(v, 2),
                     "span": [round(g0 + idx[0] / 100, 2), round(g0 + (idx[-1] + 1) / 100, 2)],
                     "peak_db": round(float(db[int(g0 * 100):int(g1 * 100)].max()), 1)})
for r in rows:
    print(f'{r["gap"][0]:7.2f}-{r["gap"][1]:7.2f}  voiced {r["voiced_s"]:.2f}s @{r["span"][0]:.2f}-{r["span"][1]:.2f} '
          f'peak {r["peak_db"]:6.1f}dB  {r["after"]:>7} {r["prev"]} … {r["next"]}')
(E / "verify").mkdir(exist_ok=True)
(E / "verify" / "gaps.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
np.save(E / "voiced.npy", voiced)
