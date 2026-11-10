"""Caption transcript for the cut: forced-aligned words (edit/cut_words.json) → project/transcript.json
({language_code, words:[{text,start,end,type}]}, embedded-captions format).

- drop aligner slivers of cut fillers ("ha"/"uh") and '*' noise tokens that map_words keeps at range edges
- join reduplications into one word (berhati-hati, kadang-kadang, betul-betul, apa-apa)
- fused sentence-final "lah" stays on its word (bipolarlah, doktorlah) — it is spoken that way
- "seratus peratus" → one token "100%" (start of seratus, end of peratus); "sepuluh" → "10"
- spelling: the aligner works on lowercase romanisation; captions are uppercase anyway
"""

import json
from pathlib import Path

C = Path(__file__).parent
words = [w for w in json.loads((C.parent / "edit" / "cut_words.json").read_text()) if w["text"] not in ("*", "ha", "uh")]

REDUP = {"berhati": "hati", "kadang": "kadang", "betul": "betul", "apa": "apa"}
out = []
i = 0
while i < len(words):
    w = dict(text=words[i]["text"], start=words[i]["start"], end=words[i]["end"])
    nxt = words[i + 1] if i + 1 < len(words) else None
    if nxt and REDUP.get(w["text"]) == nxt["text"]:
        w = {"text": f"{w['text']}-{nxt['text']}", "start": w["start"], "end": nxt["end"]}
        i += 2
    elif nxt and w["text"] == "seratus" and nxt["text"] == "peratus":
        w = {"text": "100%", "start": w["start"], "end": nxt["end"]}
        i += 2
    elif nxt and nxt["text"] == "lah" and w["text"] in ("bipolar", "doktor"):
        w = {"text": w["text"] + "lah", "start": w["start"], "end": nxt["end"]}
        i += 2
    else:
        i += 1
    if w["text"] == "sepuluh":   # numerals read faster on screen ("10 UBAT"), and the hero renders verbatim
        w["text"] = "10"
    out.append(w)

for w in out:
    w["type"] = "word"
P = C / "project"
P.mkdir(exist_ok=True)
(P / "transcript.json").write_text(json.dumps({"language_code": "ms", "words": out}, indent=1, ensure_ascii=False))
print(len(out), "caption words")
print(" ".join(w["text"] for w in out))
