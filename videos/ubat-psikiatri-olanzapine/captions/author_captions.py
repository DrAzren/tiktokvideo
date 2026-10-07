"""Author project/cinematic.json for the `loud` caption identity.
Template: videos/ward-psikiatri/captions/author_captions.py.

Layout: the speaker sits high in a car (hair top y ~460-520), so graphics cards own y 130-372 and the
captions run in a one-line plane just above the hair (y ~390-480), flipping line by line, TikTok style.
One apex: "OLANZAPINE" (the hook's answer, 0:01.8) slams in BEHIND the head, teal, while no card or
insert is on screen; its lockup carries "nama ubat" above it and "jom saya terangkan" as the tail.

Line grouping: 1-3 words, <= MAX_CHARS, break at pauses >= PAUSE; a line that would be on screen
< MIN_ON is merged forward when it fits.
"""

import json
from pathlib import Path

C = Path(__file__).parent
P = C / "project"
words = json.loads((P / "transcript.json").read_text())["words"]

MAX_WORDS, MAX_CHARS, PAUSE, MIN_ON = 3, 21, 0.28, 0.62
FIT = 23   # Anton at 0.046h fits ~24 chars across the 92% plane; merges (to stop a line flashing) never exceed 23
# forced breaks (prev, word) at clause ends large-v3 left unpunctuated
FORCE_BREAK = {("sendiri", "jangan"), ("up", "kalau"), ("psikiatri", "tapi"), ("mental", "di"), ("badan", "kalau"),
               ("penting", "kita"), ("komen", "take")}
# fixed phrases that must never be split across two caption lines
GLUE = {("kesan", "sampingan"), ("berat", "badan"), ("tekanan", "darah"), ("side", "effect"), ("nafsu", "makan"),
        ("kesihatan", "mental"), ("give", "up"), ("tidak", "dinafikan"), ("gangguan", "psikosis"),
        ("khidmat", "nasihat"), ("take", "care"), ("ubat", "olanzapine"), ("ubat", "psikiatri"),
        ("kembali", "senyap"), ("lebih", "tenang"), ("hilang", "nafsu"), ("stabilkan", "mood"),
        ("jangan", "stop"), ("jangan", "give"), ("di", "bio"), ("buat", "appointment"), ("di", "Nilai"),
        ("apa-apa", "soalan"), ("naik", "drastik"), ("ubat", "ni"), ("yang", "lain"), ("naik", "pelan-pelan"), ("start", "rawatan")}


# clause/sentence ends: large-v3's punctuated transcript of the same cut, attached to OUR
# words by sequence-aligning the two word lists (its timestamps drift; its text doesn't)
def _punct_marks():
    import difflib
    import re
    lv3 = [w["text"] for seg in json.loads((C.parent / "captions_src" / "large_v3_cut.json").read_text())
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


BODY_CSS = ("font-size: calc(0.046*var(--h)); text-transform: uppercase; letter-spacing: 0.01em; "
            "-webkit-text-stroke: 3px rgba(0,0,0,0.6); paint-order: stroke fill; "
            "text-shadow: 0 4px 0 rgba(0,0,0,0.38), 0 8px 26px rgba(0,0,0,0.6);")
HERO_CSS = "font-size: calc(0.115*var(--h)); text-transform: uppercase; color: #0E5E6F !important;"
HERO_WORD_T = 1.76          # "olanzapine" in "pernah dengar nama ubat olanzapine?" (cut timeline)
HERO_BLOCK_END = 3.4        # lockup = kicker + hero + one tail line; ends before MG1 (3.68s)


def group(ws):
    lines, cur = [], []
    for i, w in enumerate(ws):
        if cur:
            gap = w["start"] - cur[-1]["end"]
            chars = len(" ".join(x["text"] for x in cur + [w]))
            if (cur[-1]["text"], w["text"]) in FORCE_BREAK:
                lines.append(cur)
                cur = [w]
                continue
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

    # rebalance first: a line that would flash borrows the next line's first word when it fits
    # (e.g. "ubat ini / sangat bagus untuk" -> "ubat ini sangat / bagus untuk"), unless that breaks a GLUE pair
    for i in range(len(lines) - 1):
        while on_time(i, lines) < MIN_ON and len(lines[i + 1]) > 1 \
                and len(text(lines[i] + lines[i + 1][:1])) <= FIT \
                and (lines[i + 1][0]["text"], lines[i + 1][1]["text"]) not in GLUE \
                and (lines[i][-1]["text"], lines[i + 1][0]["text"]) not in FORCE_BREAK \
                and not punct_break(lines[i][-1], lines[i + 1][0], strong_only=True):
            lines[i].append(lines[i + 1].pop(0))

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
    return lines


hero_i = min(range(len(words)), key=lambda i: abs(words[i]["start"] - HERO_WORD_T))
assert words[hero_i]["text"] == "olanzapine" and words[hero_i - 1]["text"] == "ubat", words[hero_i]
end_i = max(i for i, w in enumerate(words) if w["start"] < HERO_BLOCK_END)

blocks = [{"plane": "narr", "flip": True, "lines": [{"words": ["pernah", "dengar"], "css": BODY_CSS}]}]
assert [w["text"] for w in words[:hero_i - 2]] == ["pernah", "dengar"]
hero_block = {"plane": "narr", "flip": True, "lines": [
    {"words": ["nama", "ubat"], "css": BODY_CSS},
    {"words": ["olanzapine"], "hero": True, "css": HERO_CSS},
]}
tail = [w["text"] for w in words[hero_i + 1:end_i + 1]]
assert tail == ["jom", "saya", "terangkan"], tail
hero_block["lines"].append({"words": tail, "css": BODY_CSS})
blocks.append(hero_block)

for ln in group(words[end_i + 1:]):
    blocks.append({"plane": "narr", "flip": True, "lines": [{"words": [w["text"] for w in ln], "css": BODY_CSS}]})

cin = {
    "dna": "loud",
    "width": 1080, "height": 1920, "fps": 30,
    "planes": {
        # one Anton line just above the hair, clear of the cards (end <= y372) and TikTok's top UI
        "narr": "top: 20.4%; left: 4%; width: 92%; height: 5.6%;",
        "hero": None,
    },
    "blocks": blocks,
    "tones": {"default": "soft", "hero": "impact"},
}
(P / "cinematic.json").write_text(json.dumps(cin, indent=1, ensure_ascii=False))
n_lines = sum(len(b["lines"]) for b in blocks)
print(f"{len(blocks)} blocks, {n_lines} lines, hero block = {len(hero_block['lines'])} lines")
long = [" ".join(l["words"]) for b in blocks for l in b["lines"] if len(" ".join(l["words"])) > FIT and not l.get("hero")]
print("lines over FIT:", long)
for b in blocks[:12]:
    print(" | ".join(" ".join(l["words"]) for l in b["lines"]))
