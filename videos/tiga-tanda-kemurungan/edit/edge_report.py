"""Envelope plots (template: ward-psikiatri) around the segment-boundary cut edges (reason-tagged ranges), with aligned words."""
import json
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
E = Path(__file__).parent
db = np.load(E/"env_db.npy")
al = json.load(open(E/"aligned.json"))
words = sorted((w for v in al.values() for w in v["words"]), key=lambda w: w["start"])
rs = json.load(open(E/"edl.json"))["ranges"]
# segment starts = first range, or range after a reason-tagged one; segment ends = reason-tagged
edges = []
for i, r in enumerate(rs):
    if i == 0 or "reason" in rs[i-1]: edges.append((i, "IN", r["start"]))
    if "reason" in r: edges.append((i, "OUT", r["end"]))
cols = 5
for part in range(0, len(edges), 20):
    chunk = edges[part:part+20]
    rows = (len(chunk)+cols-1)//cols
    fig, axes = plt.subplots(rows, cols, figsize=(25, rows*2.3))
    for ax, (i, kind, t) in zip(axes.flat, chunk):
        lo, hi = t-0.7, t+0.7
        idx = np.arange(int(max(0,lo)*100), int(min(len(db)/100,hi)*100))
        ax.fill_between(idx/100, -70, db[idx], color="#6aa9ff")
        for w in words:
            if w["end"] > lo and w["start"] < hi:
                c = "#bbbbbb" if w["text"] == "*" else "#ffcc66"
                ax.axvspan(max(w["start"],lo), min(w["end"],hi), color=c, alpha=0.3)
                ax.text((max(w["start"],lo)+min(w["end"],hi))/2, -4, w["text"], ha="center", fontsize=8)
        ax.axvline(t, color="red", lw=1.6)
        keep = (t, hi) if kind=="IN" else (lo, t)
        ax.axvspan(*keep, ymin=0, ymax=0.07, color="green")
        ax.set_xlim(lo, hi); ax.set_ylim(-70, 0); ax.set_title(f"r{i} {kind} @ {t:.2f}", fontsize=10)
        ax.tick_params(labelsize=7)
    for ax in list(axes.flat)[len(chunk):]: ax.axis("off")
    fig.tight_layout(); fig.savefig(E/f"verify/edges_{part//20}.png", dpi=62)
print(len(edges), "edges")
