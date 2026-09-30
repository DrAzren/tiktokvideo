"""Caption transcript for the cut: forced-aligned words (edit/cut_words.json), which are exact on the
cut timeline (mapped through the EDL, not re-transcribed).
  - reduplications joined: bayang-bayang, apa-apa (x3)
  - wording settled by alignment scoring: "di ruang komen" (vs "diorang"), "take care" (said "tekeh");
    "persepsi deria" kept (the correct term; deria/diri inconclusive by scoring)
Output: transcript.json {language_code, words:[{text,start,end,type}]} (embedded-captions format)
"""

import json
from pathlib import Path

C = Path(__file__).parent
words = json.loads((C.parent / "edit" / "cut_words.json").read_text())

out = []
for w in words:
    t = w["text"]
    if out and t in ("bayang", "apa") and out[-1]["text"] == t:
        out[-1]["text"] += "-" + t
        out[-1]["end"] = w["end"]
        continue
    out.append({"text": t, "start": w["start"], "end": w["end"], "type": "word"})

(C / "transcript.json").write_text(json.dumps({"language_code": "ms", "words": out}, indent=1, ensure_ascii=False))
print(len(out), "caption words")
print(" ".join(w["text"] for w in out))
