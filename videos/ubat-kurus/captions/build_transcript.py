"""Caption transcript for the cut: forced-aligned words (edit/cut_words.json) with display fixes:
  azrin -> azren (the speaker's name: Dr Azren), topiramid -> topiramate (drug name as spelled),
  reduplications joined (ubat-ubat, kadang-kadang, masing-masing, awal-awal, berbeza-beza,
  ketiga-tiga, semata-mata, apa-apa).
Output: project/transcript.json {language_code, words:[{text,start,end,type}]} (embedded-captions format)
"""

import json
from pathlib import Path

C = Path(__file__).parent
words = json.loads((C.parent / "edit" / "cut_words.json").read_text())

FIX = {"azrin": "azren", "topiramid": "topiramate"}
REDUP = {("ubat", "ubat"), ("kadang", "kadang"), ("masing", "masing"), ("awal", "awal"),
         ("berbeza", "beza"), ("ketiga", "tiga"), ("semata", "mata"), ("apa", "apa")}

out = []
for w in words:
    t = FIX.get(w["text"], w["text"])
    if out and (out[-1]["text"].split("-")[0], t) in REDUP and "-" not in out[-1]["text"] \
            and w["start"] - out[-1]["end"] < 0.25:
        out[-1]["text"] += "-" + t
        out[-1]["end"] = w["end"]
        continue
    out.append({"text": t, "start": w["start"], "end": w["end"]})

for w in out:
    w["type"] = "word"
(C / "project").mkdir(exist_ok=True)
(C / "project" / "transcript.json").write_text(
    json.dumps({"language_code": "ms", "words": out}, indent=1, ensure_ascii=False))
print(len(out), "caption words")
print(" ".join(w["text"] for w in out))
