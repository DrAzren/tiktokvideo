"""Spectrograms (0-4 kHz) around each gap_scan.py candidate with >= 0.1 s voicing, aligned words on top.
A voiced hesitation ("eee"/"mmm") shows as flat, evenly spaced harmonics with no consonant bursts;
a breath is broadband noise with no harmonics. → verify/spectro.png"""
import json
from pathlib import Path

import matplotlib
import numpy as np
import soundfile as sf

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

E = Path(__file__).parent
a, sr = sf.read(E / "audio.wav", dtype="float32")
al = json.loads((E / "aligned.json").read_text())
words = sorted((w for v in al.values() for w in v["words"]), key=lambda w: w["start"])
cands = [c for c in json.loads((E / "gap_candidates.json").read_text()) if c["voiced_s"] >= 0.1]
cols = 4
rows = (len(cands) + cols - 1) // cols
fig, axes = plt.subplots(rows, cols, figsize=(24, rows * 3.0), squeeze=False)
for ax, c in zip(axes.flat, cands):
    lo, hi = max(0, c["t0"] - 0.5), c["t1"] + 0.5
    x = a[int(lo * sr):int(hi * sr)]
    ax.specgram(x, NFFT=512, Fs=sr, noverlap=448, cmap="magma", vmin=-110, vmax=-20, xextent=(lo, hi))
    ax.set_ylim(0, 4000)
    for w in words:
        if w["end"] > lo and w["start"] < hi:
            ax.axvline(w["start"], color="cyan", lw=0.8)
            ax.axvline(w["end"], color="cyan", lw=0.8, ls=":")
            ax.text((max(w["start"], lo) + min(w["end"], hi)) / 2, 3700, w["text"], color="white", ha="center", fontsize=9)
    ax.axvspan(c["t0"], c["t1"], ymin=0, ymax=0.04, color="lime")
    ax.set_title(f'{c["t0"]:.2f}-{c["t1"]:.2f} after "{c["after"].split()[-1]}" voiced {c["voiced_s"]}s', fontsize=10)
    ax.tick_params(labelsize=7)
for ax in list(axes.flat)[len(cands):]:
    ax.axis("off")
fig.tight_layout()
fig.savefig(E / "verify" / "spectro.png", dpi=50)
print(len(cands), "spectrograms")
