"""Envelope + voicing + aligned words for arbitrary windows: plot_windows.py out.png t1 t2 ... (±0.9s each)."""
import json
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

E = Path(__file__).parent
db, v = np.load(E / "env_db.npy"), np.load(E / "voicing.npy")
al = json.loads((E / "aligned.json").read_text())
words = sorted((w for x in al.values() for w in x["words"]), key=lambda w: w["start"])
out, ts = sys.argv[1], [float(t) for t in sys.argv[2:]]
cols = 3
rows = (len(ts) + cols - 1) // cols
fig, axes = plt.subplots(rows, cols, figsize=(24, rows * 2.6), squeeze=False)
for ax, t in zip(axes.flat, ts):
    HW = float(__import__("os").environ.get("HW", 0.9))
    lo, hi = t - HW, t + HW
    idx = np.arange(int(max(0, lo) * 100), int(min(len(v) / 100, hi) * 100))
    ax.fill_between(idx / 100, -70, db[idx], color="#6aa9ff")
    vo = (v[idx, 0] > 0.6) & (db[idx] > -26)
    ax.fill_between(idx / 100, -70, -70 + 12 * vo, color="orange")
    for w in words:
        if w["end"] > lo and w["start"] < hi:
            c = "#bbbbbb" if w["text"] == "*" else "#ffcc66"
            ax.axvspan(max(w["start"], lo), min(w["end"], hi), color=c, alpha=0.3)
            ax.text((max(w["start"], lo) + min(w["end"], hi)) / 2, -4, w["text"], ha="center", fontsize=8)
    ax.set_xlim(lo, hi); ax.set_ylim(-70, 0); ax.set_title(f"@ {t:.2f}", fontsize=10)
    ax.set_xticks(np.arange(round(lo, 1), hi, 0.1)); ax.tick_params(labelsize=6); ax.grid(alpha=.3)
for ax in list(axes.flat)[len(ts):]:
    ax.axis("off")
fig.tight_layout(); fig.savefig(out, dpi=62)
