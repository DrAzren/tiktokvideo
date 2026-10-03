"""Hesitation scan: voiced runs between aligned words + words held far longer than their letters need.
voiced frame = periodicity > 0.6 and band energy > -26 dB (the rumble floor sits ~-30 dB).
CTC word ends run ~0.1s early, so a gap is only scanned from end+0.10 to next start-0.03."""
import json
from pathlib import Path

import numpy as np

E = Path(__file__).parent
db, v = np.load(E / "env_db.npy"), np.load(E / "voicing.npy")
al = json.loads((E / "aligned.json").read_text())
words = sorted(({"iid": k, "i": i, **w} for k, x in al.items() for i, w in enumerate(x["words"])), key=lambda w: w["start"])
voiced = (v[:len(db), 0] > 0.6) & (db[:len(v)] > -26)


def runs(lo, hi):
    i0, i1 = int(lo * 100), int(hi * 100)
    seg = voiced[i0:i1]
    out, s = [], None
    for k, x in enumerate(np.append(seg, False)):
        if x and s is None:
            s = k
        elif not x and s is not None:
            if k - s >= 8:
                out.append(((i0 + s) / 100, (i0 + k) / 100))
            s = None
    return out


for a, b in zip(words, words[1:]):
    if a["iid"] != b["iid"]:
        continue
    r = runs(a["end"] + 0.10, b["start"] - 0.03)
    gap = b["start"] - a["end"]
    if r:
        tot = sum(e - s for s, e in r)
        f0 = np.median(v[int(r[0][0] * 100):int(r[0][1] * 100), 1])
        print(f"GAP  {a['iid']}:{a['i']:>3} {a['text']:>14} | {b['text']:<14} gap {gap:.2f}s voiced {tot:.2f}s "
              f"{' '.join(f'{s:.2f}-{e:.2f}' for s, e in r)} f0~{f0:.0f}")
for w in words:
    d = w["end"] - w["start"]
    expect = 0.075 * len(w["text"]) + 0.12
    if d > expect + 0.25:
        print(f"LONG {w['iid']}:{w['i']:>3} {w['text']:>14} {w['start']:.2f}-{w['end']:.2f} ({d:.2f}s, expect ~{expect:.2f})")
