"""Envelope plots at EVERY cut edge in edl.json (pause shrinks and filler cuts too), with aligned words.
Green bar = the side that is kept. Output: verify/edges_<n>.png"""
import json
from pathlib import Path

import matplotlib
import numpy as np
matplotlib.use("Agg")
import matplotlib.pyplot as plt

E = Path(__file__).parent
db = np.load(E / "env_db.npy")
al = json.load(open(E / "aligned.json"))
words = sorted((w for v in al.values() for w in v["words"]), key=lambda w: w["start"])
rs = json.load(open(E / "edl.json"))["ranges"]
edges = []
for i, r in enumerate(rs):
    edges.append((i, "IN", r["start"]))
    edges.append((i, "OUT", r["end"]))
cols, per = 6, 24
for part in range(0, len(edges), per):
    chunk = edges[part:part + per]
    rows = (len(chunk) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(30, rows * 2.3))
    for ax, (i, kind, t) in zip(axes.flat, chunk):
        lo, hi = t - 0.6, t + 0.6
        idx = np.arange(int(max(0, lo) * 100), int(min(len(db) / 100, hi) * 100))
        ax.fill_between(idx / 100, -70, db[idx], color="#6aa9ff")
        for w in words:
            if w["end"] > lo and w["start"] < hi:
                c = "#bbbbbb" if w["text"] == "*" else "#ffcc66"
                ax.axvspan(max(w["start"], lo), min(w["end"], hi), color=c, alpha=0.3)
                ax.text((max(w["start"], lo) + min(w["end"], hi)) / 2, -4, w["text"], ha="center", fontsize=8)
        ax.axvline(t, color="red", lw=1.6)
        ax.axvspan(*((t, hi) if kind == "IN" else (lo, t)), ymin=0, ymax=0.07, color="green")
        ax.set_xlim(lo, hi); ax.set_ylim(-70, 0); ax.set_title(f"r{i} {kind} @ {t:.2f}", fontsize=10)
        ax.tick_params(labelsize=7)
    for ax in list(axes.flat)[len(chunk):]:
        ax.axis("off")
    fig.tight_layout(); fig.savefig(E / f"verify/edges_{part // per}.png", dpi=55)
print(len(edges), "edges")
