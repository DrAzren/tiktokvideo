"""Caption transcript for the cut: forced-aligned words (edit/cut_words.json), verified by an
unprompted large-v3 pass on the cut (captions_src/large_v3_cut.json reads back the approved script).
Reduplicated words are joined (betul-betul, suka-suka, perlahan-lahan, apa-apa).
Output: transcript.json + project/transcript.json {language_code, words:[{text,start,end,type}]}
"""

import json
from pathlib import Path

C = Path(__file__).parent
words = json.loads((C.parent / "edit" / "cut_words.json").read_text())
PAIRS = {("betul", "betul"), ("suka", "suka"), ("perlahan", "lahan"), ("apa", "apa")}

out = []
for w in words:
    t = w["text"]
    if out and (out[-1]["text"], t) in PAIRS:
        out[-1]["text"] += "-" + t
        out[-1]["end"] = w["end"]
        continue
    out.append({"text": t, "start": w["start"], "end": w["end"]})
for w in out:
    w["type"] = "word"
doc = json.dumps({"language_code": "ms", "words": out}, indent=1, ensure_ascii=False)
(C / "transcript.json").write_text(doc)
(C / "project" / "transcript.json").write_text(doc)
print(len(out), "caption words")
print(" ".join(w["text"] for w in out))
