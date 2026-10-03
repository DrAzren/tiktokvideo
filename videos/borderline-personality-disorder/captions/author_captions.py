"""Author project/cinematic.json for the `loud` caption identity.

Template: videos/ward-psikiatri/captions/author_captions.py.
Layout: graphics cards own the headroom band (y 118-320); captions run in a
one-line plane just above the hair (y ~334-420, hair top ~430) and flip line by
line, TikTok style. The plane spans x 4%-85%: centred on the face (x ~0.45) and
clear of TikTok's right-hand buttons. One apex: "BPD" ("tanda-tanda utama BPD",
0:09.1, the answer to the hook's "Betul ke?") slams in BEHIND the head in the
card-free window; its block carries kicker + tail so the hero holds ~2.5s.

Line grouping: 1-3 words, <= MAX_CHARS, break at pauses >= PAUSE; a line that
would be on screen < MIN_ON is merged forward when it fits.
"""

import json
from pathlib import Path

C = Path(__file__).parent
P = C / "project"
words = json.loads((P / "transcript.json").read_text())["words"]

MAX_WORDS, MAX_CHARS, PAUSE, MIN_ON = 3, 20, 0.28, 0.62
FIT = 21   # characters that fit one Anton line at 0.042h across the plane (~880px) — merges never exceed it
# forced breaks (prev, word): the patient's quoted question starts at "doktor"
FORCE_BREAK = {("ke", "jom"), ("panik", "yang"), ("stabil", "sekejap"), ("cepat", "contohnya"), ("Nilai", "sama")}
# fixed phrases that must never be split across two caption lines
GLUE = {("borderline", "personality"), ("personality", "disorder"), ("mood", "swing"), ("betul", "ke"),
        ("tak", "stabil"), ("naik", "turun"), ("turun", "naik"), ("orang", "tu"), ("tengah", "hari"),
        ("rasa", "kosong"), ("tingkah", "laku"), ("kesihatan", "mental"), ("take", "care"),
        ("ruang", "komen"), ("di", "Nilai"), ("yang", "kedua"), ("yang", "ketiga"), ("yang", "keempat"),
        ("yang", "kelima"), ("nombor", "enam"), ("benda", "kecil"), ("tak", "difahami"), ("self-harm", "bila"),
        ("bila", "stres"), ("kecil", "je"), ("memang", "ada"), ("sama", "ada")}

# clause/sentence ends: large-v3's punctuated transcript of the same cut, attached to OUR
# words by sequence-aligning the two word lists (its timestamps drift; its text doesn't)
def _punct_marks():
    import difflib
    import re
    # large-v3 drops punctuation after ~0:31 but still splits sentences into segments: a segment's
    # last word counts as a sentence end
    segs = json.loads((C.parent / "captions_src" / "large_v3_cut.json").read_text())
    lv3 = [w["text"] + ("." if k == len(seg["words"]) - 1 and w["text"].rstrip()[-1:] not in ".?!," else "")
           for seg in segs for k, w in enumerate(seg["words"])]
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


BODY_CSS = ("font-size: calc(0.042*var(--h)); text-transform: uppercase; letter-spacing: 0.01em; "
            "-webkit-text-stroke: 3px rgba(0,0,0,0.55); paint-order: stroke fill; "
            "text-shadow: 0 4px 0 rgba(0,0,0,0.35), 0 8px 26px rgba(0,0,0,0.55);")
HERO_CSS = "font-size: calc(0.16*var(--h)); text-transform: uppercase; color: #0E5E6F !important;"
HERO_WORD_T = 9.07          # "BPD" in "tanda-tanda utama BPD" (cut timeline)
HERO_BLOCK_END = 10.3       # lockup = kicker + hero + one tail line ("supaya kita lebih")


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
    out = lines
    return out


hero_i = min(range(len(words)), key=lambda i: abs(words[i]["start"] - HERO_WORD_T))
assert words[hero_i]["text"] == "BPD" and words[hero_i - 1]["text"] == "utama", words[hero_i]
end_i = max(i for i, w in enumerate(words) if w["start"] < HERO_BLOCK_END)

# hook lines hand-broken (<=21 chars, each on screen >= 0.5s, the question "betul ke" on its own)
HOOK = ["orang kata borderline", "personality disorder", "ni sekadar moody je", "mood swing", "betul ke",
        "jom saya explain", "tunjukkan"]
hook_words = [w["text"] for w in words[:hero_i - 2]]
assert " ".join(HOOK).split() == hook_words, (" ".join(HOOK), hook_words)
blocks = []
for ln in HOOK:
    blocks.append({"plane": "narr", "flip": True, "lines": [{"words": ln.split(), "css": BODY_CSS}]})
for ln in []:
    blocks.append({"plane": "narr", "flip": True, "lines": [{"words": [w["text"] for w in ln], "css": BODY_CSS}]})

hero_block = {"plane": "narr", "flip": True, "lines": [
    {"words": ["tanda-tanda", "utama"], "css": BODY_CSS},
    {"words": ["BPD"], "hero": True, "css": HERO_CSS},
]}
tail = [w["text"] for w in words[hero_i + 1:end_i + 1]]
assert tail == ["supaya", "kita", "lebih"], tail
hero_block["lines"].append({"words": tail, "css": BODY_CSS})
blocks.append(hero_block)

for ln in group(words[end_i + 1:]):
    blocks.append({"plane": "narr", "flip": True, "lines": [{"words": [w["text"] for w in ln], "css": BODY_CSS}]})

cin = {
    "dna": "loud",
    "width": 1080, "height": 1920, "fps": 30,
    "planes": {
        # one Anton line just above the hair (~y430), below the cards (end ~y320), clear of the right-hand buttons
        "narr": "top: 17.4%; left: 4%; width: 81%; height: 4.6%;",
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
