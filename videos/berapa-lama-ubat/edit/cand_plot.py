"""Spectrogram + envelope around every filler candidate (voiced sound no word covers), words overlaid."""
import json
import sys
from pathlib import Path

import matplotlib
import numpy as np
import soundfile as sf
matplotlib.use("Agg")
import matplotlib.pyplot as plt

E = Path(__file__).parent
db = np.load(E / "env_db.npy")
a, sr = sf.read(E / "vocals16k.wav", dtype="float32")
al = json.loads((E / "aligned.json").read_text())
ws = sorted((w for v in al.values() for w in v["words"]), key=lambda w: w["start"])
cands = json.loads(sys.argv[1]) if len(sys.argv) > 1 else None
if cands is None:
    cands = []
    for x, y in zip(ws, ws[1:]):
        lo, hi = int(x["end"] * 100) + 2, int(y["start"] * 100) - 2
        if hi - lo >= 8 and (db[lo:hi] > -28).sum() >= 8:
            cands.append([x["end"], y["start"]])
cols = 4
rows = (len(cands) + cols - 1) // cols
fig, axes = plt.subplots(rows * 2, cols, figsize=(26, rows * 4.2), gridspec_kw={"height_ratios": [3, 1] * rows})
for n, (s, e) in enumerate(cands):
    r, c = divmod(n, cols)
    ax, ax2 = axes[2 * r, c], axes[2 * r + 1, c]
    lo, hi = max(0, s - 0.6), e + 0.6
    seg = a[int(lo * sr):int(hi * sr)]
    ax.specgram(seg, NFFT=512, Fs=sr, noverlap=448, cmap="magma", vmin=-110, xextent=(lo, hi))
    ax.set_ylim(0, 4000)
    for w in ws:
        if w["end"] > lo and w["start"] < hi:
            ax.axvspan(max(w["start"], lo), min(w["end"], hi), ymin=0.9, ymax=1, color="#6cf" if w["text"] != "*" else "#999", alpha=.8)
            ax.text((max(w["start"], lo) + min(w["end"], hi)) / 2, 3700, w["text"], ha="center", fontsize=9, color="w")
    ax.axvline(s, color="lime", lw=1); ax.axvline(e, color="lime", lw=1)
    ax.set_title(f"#{n}  {s:.2f}-{e:.2f}", fontsize=11); ax.tick_params(labelsize=7)
    idx = np.arange(int(lo * 100), min(len(db), int(hi * 100)))
    ax2.fill_between(idx / 100, -60, db[idx], color="#6aa9ff"); ax2.set_xlim(lo, hi); ax2.set_ylim(-60, 0)
    ax2.axhline(-28, color="r", lw=.6); ax2.tick_params(labelsize=7)
for ax in axes.flat[2 * len(cands) if False else 0:]:
    pass
fig.tight_layout(); fig.savefig(E / "verify/candidates.png", dpi=48)
print(len(cands), "candidates"); print(json.dumps([[round(s, 2), round(e, 2)] for s, e in cands]))
