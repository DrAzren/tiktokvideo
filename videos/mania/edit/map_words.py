"""Map forced-aligned source words through edl.json onto the cut timeline.

The EDL is a pure time remap (frame-aligned ranges, same as tools/render_edl.py),
so every kept word's output time is exact — no re-transcription needed.
Output: cut_words.json  [{text, start, end}]  (words whose midpoint falls in a cut gap are gone)
"""

import json
from fractions import Fraction
from pathlib import Path

E = Path(__file__).parent
FPS = Fraction(30)

edl = json.loads((E / "edl.json").read_text())
words = json.loads((E / "aligned.json").read_text())["words"]

out, t = [], 0.0
for r in edl["ranges"]:
    s = float(Fraction(round(r["start"] * FPS)) / FPS)
    e = float(Fraction(round(r["end"] * FPS)) / FPS)
    for w in words:
        mid = (w["start"] + w["end"]) / 2
        if s <= mid < e:
            out.append({"text": w["text"], "start": round(max(s, w["start"]) - s + t, 3),
                        "end": round(min(e, w["end"]) - s + t, 3), "src": w["start"]})
    t += e - s

(E / "cut_words.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(f"{len(out)} words over {t:.2f}s (+{edl.get('tail_hold', 0)}s hold)")
for k in range(0, len(out), 12):
    print(f"{out[k]['start']:7.2f} {' '.join(w['text'] for w in out[k:k + 12])}")
