"""Author project/cinematic.json for the `loud` caption identity ('10 Ubat Psikiatri').

Layout for this framing (head high: hair ~y420, chin ~y1280-1310 with punch-ins): the graphic
cards own the headroom band (y 140-376), so captions run in a one-line plane on the CHEST
(y ~1335-1470) — clear of the face and of TikTok's bottom ~20% UI (y > 1536). One apex:
"10 UBAT" (the opening words, 0:00) behind the head while no card is on screen; its block carries
"psikiatri yang perlu" so the hero holds until the full-screen hook graphic covers the frame (2.13s).

Line grouping (same rules as videos/ward-psikiatri/captions/author_captions.py): 1-4 words,
<= MAX_CHARS, break at pauses >= PAUSE and at clause ends (from large-v3's punctuation);
fixed phrases never split; a line on screen < MIN_ON is merged into a neighbour when it fits.
"""

import difflib
import json
import re
from pathlib import Path

C = Path(__file__).parent
P = C / "project"
words = json.loads((P / "transcript.json").read_text())["words"]

MAX_WORDS, MAX_CHARS, PAUSE, MIN_ON = 4, 22, 0.28, 0.75
FIT = 22   # Anton at 0.047h: 22 uppercase chars ~ 900px of the 994px plane
FORCE_BREAK = {("pregnant", "assalamualaikum"), ("psikiatri", "kalau"), ("baby", "ubat")}
GLUE = {("sodium", "valproate"), ("panic", "attack"), ("neural", "tube"), ("tube", "defect"), ("cleft", "lip"),
        ("cleft", "palate"), ("baby", "floppy"), ("floppy", "syndrome"), ("withdrawal", "effect"), ("mood", "stabilizer"),
        ("muscle", "relaxant"), ("side", "effect"), ("doktor", "psikiatri"), ("doktor", "azren"), ("ubat", "psikiatri"),
        ("sistem", "saraf"), ("jantung", "bayi"), ("tengah", "pregnant"), ("apa-apa", "soalan"), ("ruangan", "komen"),
        ("pemantauan", "rapi"), ("100%", "tak"), ("tak", "boleh"), ("metabolik", "effect"), ("yang", "pertama"),
        ("yang", "kedua"), ("yang", "ketiga"), ("yang", "keempat"), ("yang", "kelima"), ("yang", "keenam"),
        ("yang", "ketujuh"), ("yang", "kelapan"), ("yang", "kesembilan"), ("yang", "kesepuluh"), ("berat", "bayi")}


def _punct_marks():
    lv3 = [w["text"] for w in json.loads((C.parent / "captions_src" / "large_v3.json").read_text())]
    norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())
    sm = difflib.SequenceMatcher(a=[norm(w["text"]) for w in words], b=[norm(t) for t in lv3], autojunk=False)
    marks = {}
    for i, j, n in sm.get_matching_blocks():
        for k in range(n):
            end = lv3[j + k].rstrip()[-1:]
            if end in ".?!":
                marks[i + k] = "."
            elif end == ",":
                marks[i + k] = ","
    return marks


MARKS = _punct_marks()
for _i, _w in enumerate(words):
    _w["idx"] = _i


def punct_break(prev, w, strong_only=False):
    m = MARKS.get(prev["idx"])
    return m == "." if strong_only else m is not None


BODY_CSS = ("font-size: calc(0.047*var(--h)); text-transform: uppercase; letter-spacing: 0.01em; "
            "-webkit-text-stroke: 3px rgba(0,0,0,0.55); paint-order: stroke fill; "
            "text-shadow: 0 4px 0 rgba(0,0,0,0.35), 0 8px 26px rgba(0,0,0,0.55);")
HERO_CSS = "font-size: calc(0.13*var(--h)); text-transform: uppercase; color: #0E5E6F !important;"


def group(ws):
    lines, cur = [], []
    for w in ws:
        if cur:
            gap = w["start"] - cur[-1]["end"]
            chars = len(" ".join(x["text"] for x in cur + [w]))
            if (cur[-1]["text"], w["text"]) in FORCE_BREAK:
                lines.append(cur)
                cur = [w]
                continue
            glued = (cur[-1]["text"], w["text"]) in GLUE and gap < 0.45
            if glued and (len(cur) >= MAX_WORDS or chars > MAX_CHARS) and len(cur) >= 2:
                lines.append(cur[:-1])
                cur = cur[-1:]
            elif not glued and (len(cur) >= MAX_WORDS or chars > MAX_CHARS or gap >= PAUSE or punct_break(cur[-1], w)):
                lines.append(cur)
                cur = []
        cur.append(w)
    if cur:
        lines.append(cur)

    def on_time(i, ls):
        nxt = ls[i + 1][0]["start"] if i + 1 < len(ls) else ls[i][-1]["end"] + 0.9
        return nxt - ls[i][0]["start"] - 0.10

    def text(ln):
        return " ".join(x["text"] for x in ln)

    changed = True
    while changed:
        changed = False
        for i in range(len(lines)):
            if on_time(i, lines) >= MIN_ON:
                continue
            if i + 1 < len(lines) and len(text(lines[i] + lines[i + 1])) <= FIT \
                    and not punct_break(lines[i][-1], lines[i + 1][0], strong_only=True) \
                    and (lines[i][-1]["text"], lines[i + 1][0]["text"]) not in FORCE_BREAK:
                lines[i:i + 2] = [lines[i] + lines[i + 1]]
            elif i > 0 and len(text(lines[i - 1] + lines[i])) <= FIT \
                    and not punct_break(lines[i - 1][-1], lines[i][0], strong_only=True) \
                    and (lines[i - 1][-1]["text"], lines[i][0]["text"]) not in FORCE_BREAK:
                lines[i - 1:i + 1] = [lines[i - 1] + lines[i]]
            else:
                continue
            changed = True
            break
    # rebalance: a still-short line borrows the previous line's last word ("digunakan untuk sawan | juga"
    # -> "digunakan untuk | sawan juga") when that keeps both lines inside FIT and splits no glued phrase
    for i in range(1, len(lines)):
        prev, cur = lines[i - 1], lines[i]
        if on_time(i, lines) >= MIN_ON or len(prev) < 2:
            continue
        mv = prev[-1]
        if (prev[-2]["text"], mv["text"]) in GLUE or len(text([mv] + cur)) > FIT:
            continue
        lines[i - 1], lines[i] = prev[:-1], [mv] + cur
    return lines


assert [w["text"] for w in words[:5]] == ["10", "ubat", "psikiatri", "yang", "perlu"], words[:5]
hero_block = {"plane": "narr", "flip": True, "lines": [
    {"words": ["10", "ubat"], "hero": True, "css": HERO_CSS},
    {"words": ["psikiatri", "yang", "perlu"], "css": BODY_CSS},
]}
blocks = [hero_block]
for ln in group(words[5:]):
    blocks.append({"plane": "narr", "flip": True, "lines": [{"words": [w["text"] for w in ln], "css": BODY_CSS}]})

cin = {
    "dna": "loud",
    "width": 1080, "height": 1920, "fps": 30,
    "planes": {
        # one Anton line on the chest: under the chin (~y1310 at the deepest punch-in), above TikTok's UI
        "narr": "top: 69.6%; left: 4%; width: 92%; height: 7%;",
        "hero": None,
    },
    "blocks": blocks,
    "tones": {"default": "soft", "hero": "impact"},
}
(P / "cinematic.json").write_text(json.dumps(cin, indent=1, ensure_ascii=False))
lens = [len(" ".join(l["words"])) for b in blocks[1:] for l in b["lines"]]
print(f"{len(blocks)} blocks; longest line {max(lens)} chars")
for b in blocks[:10]:
    print(" | ".join(" ".join(l["words"]) for l in b["lines"]))
