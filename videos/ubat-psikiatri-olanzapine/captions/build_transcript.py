"""Caption transcript for the cut. Template: videos/ward-psikiatri/captions/build_transcript.py.

Forced-aligned words (edit/cut_words.json) with the phonetic alignment spellings turned back into
display spellings, and the wording disputes settled by large-v3 on the cut (captions_src/large_v3_cut.json):
  olanzapin->olanzapine, dilusi->delusi, the first "komen" ("paling common")->common,
  said efek->side effect, giv ap->give up, wan on wan->one-on-one, di em->DM, apointmen->appointment,
  tek ker->take care; "ada soalan" -> "ada apa-apa soalan" (large-v3 hears "apa-apa" twice; the noisy
  aligner span of "ada" is split for it).
A 60 ms remnant of the dropped "itu" (seseorang itu jadi) is removed.
Reduplicated words are joined (kadang-kadang, pelan-pelan, penyakit-penyakit, awal-awal).
Output: project/transcript.json {language_code, words:[{text,start,end,type}]} (embedded-captions format)
"""

import json
from pathlib import Path

C = Path(__file__).parent
words = json.loads((C.parent / "edit" / "cut_words.json").read_text())

FIX = {"olanzapin": "olanzapine", "dilusi": "delusi", "apointmen": "appointment", "nilai": "Nilai"}
PAIRS = {("said", "efek"): ["side", "effect"], ("giv", "ap"): ["give", "up"], ("di", "em"): ["DM"],
         ("tek", "ker"): ["take", "care"]}
REDUP = {"kadang", "pelan", "penyakit", "awal"}

out, i, seen_komen = [], 0, False
while i < len(words):
    w, nxt = words[i], words[i + 1] if i + 1 < len(words) else None
    t = w["text"]
    if t == "itu" and w["end"] - w["start"] < 0.1:          # remnant of the dropped "seseorang itu jadi"
        i += 1
        continue
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
    if t == "komen" and not seen_komen:                     # "paling common lah"
        seen_komen = True
        t = "common"
    if t in REDUP and nxt and nxt["text"] == t:
        out.append({"text": f"{t}-{t}", "start": w["start"], "end": nxt["end"]})
        i += 2
        continue
    if t == "ada" and nxt and nxt["text"] == "soalan":      # "ada apa-apa soalan"
        mid = round((w["start"] + nxt["start"]) / 2, 3)
        out += [{"text": "ada", "start": w["start"], "end": mid}, {"text": "apa-apa", "start": mid, "end": nxt["start"]}]
        i += 1
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
