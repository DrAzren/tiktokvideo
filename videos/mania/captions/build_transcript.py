"""Caption transcript for the cut: forced-aligned words (edit/cut_words.json), which are exact on the
cut timeline (mapped through the EDL, not re-transcribed).
  - reduplications joined: berubah-ubah, gejala-gejala, hari-hari, sekurang-kurangnya, lain-lain,
    ubat-ubatan, apa-apa
  - wording settled by alignment scoring (edit/align.py VARIANTS): "sebelumnya nak tahu",
    "di ruang komen" (vs "diorang"), "Puteri Gunung Ledang" (the legend; "putih" scored 0.01 higher)
Output: transcript.json {language_code, words:[{text,start,end,type}]} (embedded-captions format)
"""

import json
from pathlib import Path

C = Path(__file__).parent
words = json.loads((C.parent / "edit" / "cut_words.json").read_text())
JOIN = {("berubah", "ubah"), ("gejala", "gejala"), ("hari", "hari"), ("sekurang", "kurangnya"),
        ("lain", "lain"), ("ubat", "ubatan"), ("apa", "apa")}

out = []
for w in words:
    t = w["text"]
    if out and (out[-1]["text"], t) in JOIN:
        out[-1]["text"] += "-" + t
        out[-1]["end"] = w["end"]
        continue
    out.append({"text": t, "start": w["start"], "end": w["end"], "type": "word"})

(C / "transcript.json").write_text(json.dumps({"language_code": "ms", "words": out}, indent=1, ensure_ascii=False))
print(len(out), "caption words")
print(" ".join(w["text"] for w in out))
