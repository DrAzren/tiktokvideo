"""YouTube closed captions (Malay) for final_youtube.mp4 → captions_ms.srt.

Words + times: captions/transcript.json (verified, aligned to the cut; the YouTube render keeps the
cut's timeline). Punctuation + sentence case: large-v3's transcript of the same cut, attached by
sequence alignment. Cues ≤ 42 chars, ≤ 5 s, broken at sentence/clause ends.
"""
import difflib
import json
import re
from pathlib import Path

V = Path(__file__).resolve().parents[2]
words = json.loads((V / "captions" / "transcript.json").read_text())["words"]
lv3 = [w["text"] for s in json.loads((V / "captions_src" / "large_v3_v4.json").read_text()) for w in s["words"]]
norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())
sm = difflib.SequenceMatcher(a=[norm(w["text"]) for w in words], b=[norm(t) for t in lv3], autojunk=False)
mark = {}
for i, j, n in sm.get_matching_blocks():
    for k in range(n):
        e = lv3[j + k].rstrip()[-1:]
        if e in ".?!,":
            mark[i + k] = e
mark[len(words) - 1] = "."
# large-v3 dropped the hook's tag question "…wad psikiatri, ya?" — put the question mark on "ya"
for i in range(len(words) - 1):
    if words[i]["text"] == "psikiatri" and words[i + 1]["text"] == "ya":
        mark[i], mark[i + 1] = ",", "?"
        break
PROPER = {"malaysia": "Malaysia", "physical": "physical", "skizofrenia": "skizofrenia"}

cues, cur, cap_next = [], [], True
for i, w in enumerate(words):
    t = PROPER.get(w["text"], w["text"])
    if i > 0 and words[i - 1]["text"] == "saya" and t == "doktor":   # the patient's quoted question
        t = "Doktor"
    if cap_next:
        t = t[:1].upper() + t[1:]
    t += mark.get(i, "")
    cap_next = mark.get(i) in (".", "?", "!")
    cur.append((t, w))
    text = " ".join(x for x, _ in cur)
    nxt = words[i + 1] if i + 1 < len(words) else None
    end_here = (nxt is None or mark.get(i) in (".", "?", "!") or (mark.get(i) == "," and len(text) > 24 and mark.get(i + 1) not in (".", "?", "!"))
                or len(text + " " + nxt["text"]) > 50 or nxt["start"] - cur[0][1]["start"] > 5.0
                or nxt["start"] - w["end"] > 0.6)
    if end_here:
        cues.append((cur[0][1]["start"], w["end"], text))
        cur = []

def ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

out = []
for n, (a, b, text) in enumerate(cues):
    nxt = cues[n + 1][0] if n + 1 < len(cues) else b + 1
    b = min(max(b + 0.25, a + 0.8), nxt - 0.02)
    out.append(f"{n + 1}\n{ts(a)} --> {ts(b)}\n{text}\n")
(Path(__file__).parent / "captions_ms.srt").write_text("\n".join(out), encoding="utf-8")
print(len(cues), "cues")
