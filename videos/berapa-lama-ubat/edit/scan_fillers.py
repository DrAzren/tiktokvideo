"""Filler scan: voiced energy in the vocal stem that no aligned word covers, plus words whose
duration is far beyond their letter count (drawn-out vowels). Prints candidates for the
strategy list; nothing here cuts anything."""
import json
from pathlib import Path

import numpy as np

E = Path(__file__).parent
db = np.load(E / "env_db.npy")
al = json.loads((E / "aligned.json").read_text())
ws = sorted((dict(w, iid=k, i=i) for k, v in al.items() for i, w in enumerate(v["words"])), key=lambda w: w["start"])
VOICED = -28.0
print("== uncovered voiced stretches (>=0.10s above %.0f dB) ==" % VOICED)
for a, b in zip(ws, ws[1:]):
    lo, hi = int(a["end"] * 100) + 2, int(b["start"] * 100) - 2   # CTC edges run ~20ms tight
    if hi - lo < 10:
        continue
    v = db[lo:hi] > VOICED
    n = int(v.sum())
    if n >= 10:
        print(f"{a['end']:6.2f}-{b['start']:6.2f} gap={b['start']-a['end']:.2f}s voiced={n/100:.2f}s peak={db[lo:hi].max():5.1f}dB  "
              f"[{a['iid']}#{a['i']} {a['text']}] … [{b['iid']}#{b['i']} {b['text']}]")
print("== long words (duration per letter) ==")
for w in ws:
    d = w["end"] - w["start"]
    if d / max(len(w["text"]), 1) > 0.11 and d > 0.35:
        print(f"{w['start']:6.2f}-{w['end']:6.2f} {w['text']:15s} {d:.2f}s score={w['score']}")
print("== low-score words ==")
for w in ws:
    if w["score"] < 0.35:
        print(f"{w['start']:6.2f}-{w['end']:6.2f} {w['iid']}#{w['i']} {w['text']:15s} score={w['score']}")
