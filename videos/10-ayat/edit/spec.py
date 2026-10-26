"""Spectrogram + envelope + aligned words (+ EDL cuts: yellow=in, orange=out) for given windows: python spec.py out.png lo-hi lo-hi ..."""
import json, sys
import numpy as np, soundfile as sf, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
E = Path(__file__).parent
a, sr = sf.read(E / "audio.wav", dtype="float32")
db = np.load(E / "env_bp_db.npy")
al = json.loads((E / "aligned.json").read_text())
words = sorted((w for v in al.values() for w in v["words"]), key=lambda w: w["start"])
wins = [tuple(map(float, s.split("-"))) for s in sys.argv[2:]]
fig, axes = plt.subplots(len(wins), 1, figsize=(18, 3.2 * len(wins)), squeeze=False)
for ax, (lo, hi) in zip(axes[:, 0], wins):
    seg = a[int(lo * sr):int(hi * sr)]
    ax.specgram(seg, NFFT=512, Fs=sr, noverlap=384, cmap="magma", vmin=-120, xextent=(lo, hi))
    ax.set_ylim(0, 6000)
    idx = np.arange(int(lo * 100), int(hi * 100))
    ax2 = ax.twinx(); ax2.plot(idx / 100, db[idx], color="cyan", lw=1); ax2.set_ylim(-70, 0)
    for w in words:
        if w["end"] > lo and w["start"] < hi:
            ax.axvline(w["start"], color="lime", lw=.8); ax.axvline(w["end"], color="red", lw=.8, ls="--")
            ax.text((w["start"] + w["end"]) / 2, 5600, w["text"], ha="center", color="white", fontsize=9)
    if (E / "edl.json").exists():
        for r in json.loads((E / "edl.json").read_text())["ranges"]:
            for t, c in ((r["start"], "yellow"), (r["end"], "orange")):
                if lo < t < hi:
                    ax.axvline(t, color=c, lw=2.2)
    ax.set_xticks(np.arange(lo, hi, 0.1), minor=True); ax.grid(which="minor", axis="x", alpha=.2)
fig.tight_layout(); fig.savefig(sys.argv[1], dpi=60)
