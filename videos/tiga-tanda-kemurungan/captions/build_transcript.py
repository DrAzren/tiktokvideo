"""Caption transcript for the cut: forced-aligned words (edit/cut_words.json) mapped through the EDL.
Template: videos/ward-psikiatri/captions/build_transcript.py.

Fixes:
  - anhidonia -> anhedonia (the aligner's phonetic spelling; the clinical term is anhedonia)
  - the 60ms aligner token "dah" kept at the "minda | rasa" cut edge is dropped (large-v3 on the
    cut hears "minda rasa kosong")
  - reduplicated words joined: tanda-tanda, apa-apa, lepak-lepak, kadang-kadang
  - azren -> Azren, nilai -> Nilai (proper nouns; captions are uppercase anyway)
Output: project/transcript.json {language_code, words:[{text,start,end,type}]} (embedded-captions format)
"""

import json
from pathlib import Path

C = Path(__file__).parent
words = json.loads((C.parent / "edit" / "cut_words.json").read_text())

FIX = {"anhidonia": "anhedonia", "azren": "Azren", "nilai": "Nilai"}
REDUP = {"tanda", "apa", "lepak", "kadang"}

out = []
for i, w in enumerate(words):
    t = FIX.get(w["text"], w["text"])
    prev = words[i - 1]["text"] if i else ""
    nxt = words[i + 1]["text"] if i + 1 < len(words) else ""
    if t == "dah" and prev == "minda" and nxt == "rasa":
        continue
    if out and t in REDUP and out[-1]["text"] == t and w["start"] - out[-1]["end"] < 0.25:
        out[-1]["text"] += "-" + t
        out[-1]["end"] = w["end"]
        continue
    out.append({"text": t, "start": w["start"], "end": w["end"]})

for w in out:
    w["type"] = "word"
(C / "project").mkdir(exist_ok=True)
(C / "project" / "transcript.json").write_text(json.dumps({"language_code": "ms", "words": out}, indent=1, ensure_ascii=False))
print(len(out), "caption words")
print(" ".join(w["text"] for w in out))
