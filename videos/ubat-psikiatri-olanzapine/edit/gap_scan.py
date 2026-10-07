"""Find voiced sounds hiding between aligned words (the "mmm"/"eee"/drawn vowels a pause-shrink misses).

For every gap >= 0.08s between consecutive aligned words (and every '*' token), measure how much
of it is voiced: 40ms frames, normalized autocorrelation peak in the 80-400 Hz pitch range > 0.45
with energy above the local noise floor + 8 dB. Prints candidates and writes verify/gaps.png
(envelope + words around each candidate) so every one is eyeballed before it goes on the list.
"""

import json
from pathlib import Path

import matplotlib
import numpy as np
import soundfile as sf

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

E = Path(__file__).parent
a, sr = sf.read(E / "audio.wav", dtype="float32")
db = np.load(E / "env_db.npy")
al = json.loads((E / "aligned.json").read_text())
words = sorted(({"iid": k, "i": i, **w} for k, v in al.items() for i, w in enumerate(v["words"])),
               key=lambda w: w["start"])
FLOOR = float(np.percentile(db, 8))


def voiced(t0: float, t1: float) -> tuple[float, float]:
    """(fraction of 10ms frames voiced, voiced seconds) in [t0, t1)."""
    n, v = 0, 0
    for t in np.arange(t0, t1 - 0.04, 0.01):
        x = a[int(t * sr):int((t + 0.04) * sr)]
        x = x - x.mean()
        e = float(np.dot(x, x))
        n += 1
        if e < 1e-9 or db[min(len(db) - 1, int(t * 100) + 2)] < FLOOR + 8:
            continue
        ac = np.correlate(x, x, "full")[len(x) - 1:]
        lo, hi = int(sr / 400), int(sr / 80)
        if ac[lo:hi].max() / e > 0.45:
            v += 1
    return (v / n if n else 0.0), v * 0.01


cands = []
for w, nx in zip(words, words[1:]):
    if w["iid"] != nx["iid"]:
        continue
    if w["text"] == "*":
        g0, g1, kind = w["start"], w["end"], "star"
    elif nx["text"] != "*" and nx["start"] - w["end"] >= 0.08:
        g0, g1, kind = w["end"] + 0.02, nx["start"] - 0.02, "gap"
    else:
        continue
    frac, sec = voiced(g0, g1)
    if sec >= 0.06:
        prev = next((x for x in reversed(words[:words.index(w) + (0 if kind == "star" else 1)]) if x["text"] != "*"), None)
        cands.append({"after": f'{prev["iid"]}:{prev["i"]} {prev["text"]}' if prev else "-",
                      "before": nx["text"], "t0": round(g0, 2), "t1": round(g1, 2), "voiced_s": round(sec, 2),
                      "frac": round(frac, 2), "kind": kind})

for c in cands:
    print(f'{c["t0"]:7.2f}-{c["t1"]:7.2f} {c["kind"]:4s} voiced {c["voiced_s"]:.2f}s ({c["frac"]:.0%})  after "{c["after"]}" before "{c["before"]}"')
(E / "gap_candidates.json").write_text(json.dumps(cands, indent=1, ensure_ascii=False))

cols = 5
rows = max(1, (len(cands) + cols - 1) // cols)
fig, axes = plt.subplots(rows, cols, figsize=(25, rows * 2.3), squeeze=False)
for ax, c in zip(axes.flat, cands):
    lo, hi = c["t0"] - 0.6, c["t1"] + 0.6
    idx = np.arange(int(max(0, lo) * 100), int(min(len(db) / 100, hi) * 100))
    ax.fill_between(idx / 100, -70, db[idx], color="#6aa9ff")
    for w in words:
        if w["end"] > lo and w["start"] < hi:
            col = "#bbbbbb" if w["text"] == "*" else "#ffcc66"
            ax.axvspan(max(w["start"], lo), min(w["end"], hi), color=col, alpha=0.3)
            ax.text((max(w["start"], lo) + min(w["end"], hi)) / 2, -4, w["text"], ha="center", fontsize=8)
    ax.axvspan(c["t0"], c["t1"], ymin=0, ymax=0.07, color="red")
    ax.set_xlim(lo, hi)
    ax.set_ylim(-70, 0)
    ax.set_title(f'{c["t0"]:.2f} {c["kind"]} {c["voiced_s"]}s', fontsize=10)
for ax in list(axes.flat)[len(cands):]:
    ax.axis("off")
fig.tight_layout()
fig.savefig(E / "verify" / "gaps.png", dpi=55)
