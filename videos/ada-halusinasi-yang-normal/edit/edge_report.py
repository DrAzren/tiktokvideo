"""Envelope plots at every cut edge of edl.json, with aligned words (yellow) and '*' slots (grey).
Green bar = the side that is kept. -> verify/edges_<n>.png"""
import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

E = Path(__file__).parent
db = np.load(E / "env_db.npy")
al = json.loads((E / "aligned.json").read_text())
spans = [(w["start"], w["end"], w["text"]) for w in al["words"]] + [(s["start"], s["end"], "*") for s in al["stars"]]
rs = json.loads((E / "edl.json").read_text())["ranges"]
edges = []
for i, r in enumerate(rs):
    if i:
        edges.append((i, "IN", r["start"]))
    if i + 1 < len(rs):
        edges.append((i, "OUT", r["end"]))
cols, per = 6, 24
for part in range(0, len(edges), per):
    chunk = edges[part:part + per]
    rows = (len(chunk) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(30, rows * 2.4))
    for ax, (i, kind, t) in zip(axes.flat, chunk):
        lo, hi = t - 0.6, t + 0.6
        idx = np.arange(int(max(0, lo) * 100), int(min(len(db) / 100, hi) * 100))
        ax.fill_between(idx / 100, -75, db[idx], color="#6aa9ff")
        for s, e, txt in spans:
            if e > lo and s < hi:
                ax.axvspan(max(s, lo), min(e, hi), color="#bbbbbb" if txt == "*" else "#ffcc66", alpha=0.35)
                if txt != "*":
                    ax.text((max(s, lo) + min(e, hi)) / 2, -5, txt, ha="center", fontsize=8)
        ax.axvline(t, color="red", lw=1.6)
        ax.axvspan(*((t, hi) if kind == "IN" else (lo, t)), ymin=0, ymax=0.07, color="green")
        ax.set_xlim(lo, hi); ax.set_ylim(-75, 0); ax.set_title(f"r{i} {kind} @ {t:.2f}", fontsize=10)
        ax.tick_params(labelsize=7)
    for ax in list(axes.flat)[len(chunk):]:
        ax.axis("off")
    fig.tight_layout(); fig.savefig(E / f"verify/edges_{part // per}.png", dpi=58)
print(len(edges), "edges")
