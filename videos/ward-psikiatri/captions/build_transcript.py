"""Caption transcript for the cut: forced-aligned words (edit/cut_words.json) with the
wording disputes settled by alignment scoring against the cut audio:
  ini->ni (x2), ketatlah->ketat, restrain->restraint, tekeh->take care; 'penyakit' kept where the speaker
  slipped to 'pesakit' (meaning-preserving fix, flagged to the user).
Reduplicated words are joined (meracau-racau, filem-filem, lain-lain, apa-apa).
Output: transcript.json {language_code, words:[{text,start,end,type}]} (embedded-captions format)
"""

import json
from pathlib import Path

C = Path(__file__).parent
words = json.loads((C.parent / "edit" / "cut_words.json").read_text())

# (index-free) contextual fixes: (prev_word, word) -> replacement
FIX_AFTER = {("psikiatri", "ini"): "ni"}
FIX = {"ketatlah": "ketat", "restrain": "restraint"}

out = []
for i, w in enumerate(words):
    t = w["text"]
    prev = words[i - 1]["text"] if i else ""
    t = FIX_AFTER.get((prev, t), FIX.get(t, t))
    if t == "apa" and prev == "bantuan":  # aligner put the first "apa" of "apa-apa" before 229.45; not in the audio
        continue
    if t == "apa" and i + 1 < len(words) and words[i + 1]["text"] == "soalan":  # its first half was dropped above
        t = "apa-apa"
    if t == "tekeh":  # "take care": split the aligned span
        mid = round((w["start"] + w["end"]) / 2, 3)
        out += [{"text": "take", "start": w["start"], "end": mid}, {"text": "care", "start": mid, "end": w["end"]}]
        continue
    if out and t in ("racau", "filem", "lain", "apa") and out[-1]["text"].split("-")[0] == ("me" + t if t == "racau" else t):
        out[-1]["text"] += "-" + t
        out[-1]["end"] = w["end"]
        continue
    out.append({"text": t, "start": w["start"], "end": w["end"]})

for w in out:
    w["type"] = "word"
(C / "transcript.json").write_text(json.dumps({"language_code": "ms", "words": out}, indent=1, ensure_ascii=False))
print(len(out), "caption words")
print(" ".join(w["text"] for w in out))
