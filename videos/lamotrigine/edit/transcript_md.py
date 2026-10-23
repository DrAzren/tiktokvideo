"""Timecoded source transcript (corrected wording) with each word marked kept or cut by edl.json."""
import json
from pathlib import Path

E = Path(__file__).parent
al = json.loads((E / "aligned.json").read_text())
edl = json.loads((E / "edl.json").read_text())
# display spelling for medical / English terms (alignment uses plain lowercase tokens)
SPELL = {"lamotrigine": "Lamotrigine", "steven": "Stevens-", "johnson": "Johnson", "azren": "Azren",
         "nilai": "Nilai", "doktor": "doktor", "litium": "litium", "*": "[—]"}


def kept(w):
    mid = (w["start"] + w["end"]) / 2
    return any(r["start"] <= mid < r["end"] for r in edl["ranges"])


lines = ["# Ubat Psikiatri Lamotrigine: source transcript", "",
         "Source timecodes. Corrected wording (MMS forced alignment, checked against Whisper medium + large-v3).",
         "~~Struck~~ = cut in the current EDL.", ""]
for iid, v in al.items():
    t = v["words"][0]["start"]
    out = []
    for w in v["words"]:
        s = SPELL.get(w["text"], w["text"])
        out.append(s if kept(w) else f"~~{s}~~")
    txt = " ".join(out).replace("Stevens- Johnson", "Stevens-Johnson").replace("~~ ~~", " ")
    lines.append(f"**{int(t // 60)}:{t % 60:04.1f}** · {txt}  ")
(E.parent / "transcript_source.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
