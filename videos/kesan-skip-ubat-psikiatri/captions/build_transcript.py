"""Caption transcript for the cut. Template: videos/ubat-psikiatri-olanzapine/captions/build_transcript.py.

Forced-aligned words (edit/cut_words.json) with the phonetic alignment spellings turned back into
display spellings: saikiatri->psikiatri, rilaps->relapse, mud swing->mood swing,
widdrowal simptom->withdrawal symptom, riset baten->reset button, wan on wan->one-on-one,
angzaieti->anxiety, sekan opinion->second opinion, tek ker->take care, azren->Azren, nilai->Nilai.
"gejala penaikan" is captioned "gejala penarikan" (the correct term; user-approved).
Reduplicated words are joined (tiba-tiba, simptom-simptom, kadang-kadang, menjadi-jadi, huru-hara).
Output: project/transcript.json {language_code, words:[{text,start,end,type}]} (embedded-captions format)
"""

import json
from pathlib import Path

C = Path(__file__).parent
words = json.loads((C.parent / "edit" / "cut_words.json").read_text())

FIX = {"saikiatri": "psikiatri", "rilaps": "relapse", "penaikan": "penarikan", "angzaieti": "anxiety",
       "azren": "Azren", "nilai": "Nilai"}
PAIRS = {("mud", "swing"): ["mood", "swing"], ("widdrowal", "simptom"): ["withdrawal", "symptom"],
         ("riset", "baten"): ["reset", "button"], ("sekan", "opinion"): ["second", "opinion"],
         ("tek", "ker"): ["take", "care"], ("menjadi", "jadi"): ["menjadi-jadi"], ("huru", "hara"): ["huru-hara"]}
REDUP = {"tiba", "simptom", "kadang"}

out, i = [], 0
while i < len(words):
    w, nxt = words[i], words[i + 1] if i + 1 < len(words) else None
    t = w["text"]
    if nxt and (t, nxt["text"]) in PAIRS:
        rep = PAIRS[(t, nxt["text"])]
        if len(rep) == 1:
            out.append({"text": rep[0], "start": w["start"], "end": nxt["end"]})
        else:
            out += [{"text": rep[0], "start": w["start"], "end": w["end"]},
                    {"text": rep[1], "start": nxt["start"], "end": nxt["end"]}]
        i += 2
        continue
    if t == "wan" and nxt and nxt["text"] == "on" and i + 2 < len(words) and words[i + 2]["text"] == "wan":
        out.append({"text": "one-on-one", "start": w["start"], "end": words[i + 2]["end"]})
        i += 3
        continue
    if t in REDUP and nxt and nxt["text"] == t:
        out.append({"text": f"{t}-{t}", "start": w["start"], "end": nxt["end"]})
        i += 2
        continue
    out.append({"text": FIX.get(t, t), "start": w["start"], "end": w["end"]})
    i += 1

for w in out:
    w["type"] = "word"
(C / "project").mkdir(exist_ok=True)
(C / "project" / "transcript.json").write_text(json.dumps({"language_code": "ms", "words": out}, indent=1, ensure_ascii=False))
(C / "transcript.json").write_text(json.dumps({"language_code": "ms", "words": out}, indent=1, ensure_ascii=False))
print(len(out), "caption words")
print(" ".join(w["text"] for w in out))
