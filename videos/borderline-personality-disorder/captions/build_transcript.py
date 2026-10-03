"""Caption transcript for the cut: forced-aligned words (edit/cut_words.json), with the
aligner's phonetic spellings mapped back to how they are written:
  mudi->moody, mud swing->mood swing, eksplen->explain, bipidi->BPD, wasap->WhatsApp,
  perfek->perfect, hepi->happy, syoping->shopping, self harm->self-harm, tek ker->take care,
  nilai->Nilai (the town: "klinik saya di Nilai"), insyaallah->InsyaAllah.
Reduplicated words are joined (tanda-tanda, tiba-tiba, sangat-sangat, gejala-gejala, apa-apa).
Output: transcript.json {language_code, words:[{text,start,end,type}]} (embedded-captions format)
"""

import json
from pathlib import Path

C = Path(__file__).parent
words = json.loads((C.parent / "edit" / "cut_words.json").read_text())

FIX = {"mudi": "moody", "eksplen": "explain", "bipidi": "BPD", "wasap": "WhatsApp", "perfek": "perfect",
       "hepi": "happy", "syoping": "shopping", "nilai": "Nilai", "insyaallah": "InsyaAllah"}
PAIRS = {("mud", "swing"): ["mood", "swing"], ("self", "harm"): ["self-harm"], ("tek", "ker"): ["take", "care"]}
REDUP = {"tanda", "tiba", "sangat", "gejala", "apa"}

out, i = [], 0
while i < len(words):
    w = words[i]
    nxt = words[i + 1] if i + 1 < len(words) else None
    if nxt and (w["text"], nxt["text"]) in PAIRS:
        rep = PAIRS[(w["text"], nxt["text"])]
        if len(rep) == 1:
            out.append({"text": rep[0], "start": w["start"], "end": nxt["end"]})
        else:
            out += [{"text": rep[0], "start": w["start"], "end": w["end"]},
                    {"text": rep[1], "start": nxt["start"], "end": nxt["end"]}]
        i += 2
        continue
    t = FIX.get(w["text"], w["text"])
    if out and t in REDUP and out[-1]["text"] == t and w["start"] - out[-1]["end"] < 0.3:
        out[-1]["text"] += "-" + t
        out[-1]["end"] = w["end"]
    else:
        out.append({"text": t, "start": w["start"], "end": w["end"]})
    i += 1

for w in out:
    w["type"] = "word"
(C / "transcript.json").write_text(json.dumps({"language_code": "ms", "words": out}, indent=1, ensure_ascii=False))
print(len(out), "caption words")
print(" ".join(w["text"] for w in out))
