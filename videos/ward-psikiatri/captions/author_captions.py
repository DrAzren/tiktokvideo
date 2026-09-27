"""Author project/cinematic.json for the `loud` caption identity.

Layout: graphics cards own the headroom band (y 160-560); captions run in a
one-line plane just above the head (y ~565-690) and flip line by line, TikTok
style. One apex: "TIDAK" (the first answer, 0:08.8) slams in BEHIND the head
while no card is on screen; its block carries the rest of that sentence so the
hero holds through the card-free gap instead of flashing for 0.7s.

Line grouping: 1-3 words, <= MAX_CHARS, break at pauses >= PAUSE; a line that
would be on screen < MIN_ON is merged forward when it fits.
"""

import json
from pathlib import Path

C = Path(__file__).parent
P = C / "project"
words = json.loads((P / "transcript.json").read_text())["words"]

MAX_WORDS, MAX_CHARS, PAUSE, MIN_ON = 3, 19, 0.28, 0.62
# fixed phrases that must never be split across two caption lines
GLUE = {("wad", "psikiatri"), ("salah", "faham"), ("ke", "apa"), ("physical", "restraint"),
        ("kesihatan", "mental"), ("jurupulih", "kerja"), ("cara", "kerja"), ("lain-lain", "lagi"),
        ("langkah", "terakhir"), ("tidak", "stabil"), ("beberapa", "hari"), ("beberapa", "minggu"),
        ("diri", "sendiri"), ("orang", "lain"), ("secepat", "mungkin"), ("sepanjang", "masa"),
        ("take", "care"), ("doktor", "psikiatri"), ("ahli", "psikologi"), ("jururawat", "terlatih"),
        ("tidak", "berjaya"), ("krisis", "emosi"), ("proses", "sembuh"), ("orang", "tersayang")}

# clause/sentence ends: large-v3's punctuated transcript of the same cut, attached to OUR
# words by sequence-aligning the two word lists (its timestamps drift; its text doesn't)
def _punct_marks():
    import difflib
    import re
    lv3 = [w["text"] for seg in json.loads((C.parent / "captions_src" / "large_v3.json").read_text())
           for w in seg["words"]]
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


BODY_CSS = ("font-size: calc(0.05*var(--h)); text-transform: uppercase; letter-spacing: 0.01em; "
            "-webkit-text-stroke: 3px rgba(0,0,0,0.55); paint-order: stroke fill; "
            "text-shadow: 0 4px 0 rgba(0,0,0,0.35), 0 8px 26px rgba(0,0,0,0.55);")
HERO_CSS = "font-size: calc(0.16*var(--h)); text-transform: uppercase; color: #0F766E !important;"
HERO_WORD_T = 8.84          # "tidak" in "sebenarnya tidak" (cut timeline)
HERO_BLOCK_END = 10.3       # lockup = kicker + hero + one tail line; a longer tail runs over the mouth / TikTok UI


def group(ws):
    lines, cur = [], []
    for i, w in enumerate(ws):
        if cur:
            gap = w["start"] - cur[-1]["end"]
            chars = len(" ".join(x["text"] for x in cur + [w]))
            glued = (cur[-1]["text"], w["text"]) in GLUE and gap < 0.45
            if glued and (len(cur) >= MAX_WORDS or chars > MAX_CHARS) and len(cur) >= 2:
                lines.append(cur[:-1])     # move the phrase's first word down to join its partner
                cur = cur[-1:]
            elif not glued and (len(cur) >= MAX_WORDS or chars > MAX_CHARS or gap >= PAUSE
                                or punct_break(cur[-1], w)):
                lines.append(cur)
                cur = []
        cur.append(w)
    if cur:
        lines.append(cur)
    # merge lines that would flash. The compiler shows a line from its first word -0.18s
    # until the next line's first word -0.28s, so start-to-start must be >= MIN_ON + 0.10.
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
            if i + 1 < len(lines) and len(text(lines[i] + lines[i + 1])) <= 22 \
                    and not punct_break(lines[i][-1], lines[i + 1][0], strong_only=True):
                lines[i:i + 2] = [lines[i] + lines[i + 1]]
            elif i > 0 and len(text(lines[i - 1] + lines[i])) <= 25 \
                    and not punct_break(lines[i - 1][-1], lines[i][0], strong_only=True):
                lines[i - 1:i + 1] = [lines[i - 1] + lines[i]]
            else:
                continue
            changed = True
            break
    out = lines
    return out


hero_i = min(range(len(words)), key=lambda i: abs(words[i]["start"] - HERO_WORD_T))
assert words[hero_i]["text"] == "tidak" and words[hero_i - 1]["text"] == "sebenarnya", words[hero_i]
end_i = max(i for i, w in enumerate(words) if w["start"] < HERO_BLOCK_END)

blocks = []
for ln in group(words[:hero_i - 1]):
    blocks.append({"plane": "narr", "flip": True, "lines": [{"words": [w["text"] for w in ln], "css": BODY_CSS}]})

hero_block = {"plane": "narr", "flip": True, "lines": [
    {"words": ["sebenarnya"], "css": BODY_CSS},
    {"words": ["tidak"], "hero": True, "css": HERO_CSS},
]}
tail = [w["text"] for w in words[hero_i + 1:end_i + 1]]
assert tail == ["wad", "psikiatri", "malaysia"], tail
hero_block["lines"].append({"words": tail, "css": BODY_CSS})
blocks.append(hero_block)

for ln in group(words[end_i + 1:]):
    blocks.append({"plane": "narr", "flip": True, "lines": [{"words": [w["text"] for w in ln], "css": BODY_CSS}]})

cin = {
    "dna": "loud",
    "width": 1080, "height": 1920, "fps": 30,
    "planes": {
        # one Anton line just above the head, clear of the cards (end ~y560) and TikTok's top UI
        "narr": "top: 29.6%; left: 4%; width: 92%; height: 7%;",
        "hero": None,
    },
    "blocks": blocks,
    "tones": {"default": "soft", "hero": "impact"},
}
(P / "cinematic.json").write_text(json.dumps(cin, indent=1, ensure_ascii=False))
n_lines = sum(len(b["lines"]) for b in blocks)
print(f"{len(blocks)} blocks, {n_lines} lines, hero block = {len(hero_block['lines'])} lines")
for b in blocks[:8]:
    print(" | ".join(" ".join(l["words"]) for l in b["lines"]))
