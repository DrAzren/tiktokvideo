"""Map forced-aligned source words through edl.json onto the cut timeline.

The EDL is a pure time remap (frame-aligned ranges, same as tools/render_edl.py),
so every kept word's output time is exact — no re-transcription needed.
Output: cut_words.json  [{text, start, end, beat}]  ('*' noise tokens dropped)
"""

import json
from fractions import Fraction
from pathlib import Path

E = Path(__file__).parent
FPS = Fraction(30)

edl = json.loads((E / "edl.json").read_text())
al = json.loads((E / "aligned.json").read_text())
from build_edl import WORD_FIX  # aligner fixes (e.g. "marah" stretched over a half-said "yang")

words = sorted(({**w, **WORD_FIX.get((k, i), {})} for k, v in al.items() for i, w in enumerate(v["words"])
                if w["text"] != "*"), key=lambda w: w["start"])

out, t = [], 0.0
for r in edl["ranges"]:
    s = float(Fraction(round(r["start"] * FPS)) / FPS)
    e = float(Fraction(round(r["end"] * FPS)) / FPS)
    for w in words:
        mid = (w["start"] + w["end"]) / 2
        if s <= mid < e:
            out.append({"text": w["text"], "start": round(max(s, w["start"]) - s + t, 3),
                        "end": round(min(e, w["end"]) - s + t, 3), "beat": r["beat"]})
    t += e - s

(E / "cut_words.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(f"{len(out)} words over {t:.2f}s")
line, t0 = [], None
for w in out:
    if t0 is None:
        t0 = w["start"]
    line.append(w["text"])
    if len(line) == 12:
        print(f"{t0:7.2f} {' '.join(line)}")
        line, t0 = [], None
if line:
    print(f"{t0:7.2f} {' '.join(line)}")
