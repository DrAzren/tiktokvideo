"""Author project/cinematic.json for the `loud` caption identity.

Layout: graphics cards own y 150-450 (over the teal header band); captions run in a one-line
plane just above the hair (y ~453-580) and flip line by line, TikTok style. One apex:
"BIPOLAR" (the hook's answer: "sebelumnya nak tahu mania, kita kena tahu bipolar", 0:06.4) slams in
teal BEHIND the head while no card or insert is on screen (graphics/inserts.py HERO).

Line grouping: 1-3 words, <= MAX_CHARS, break at pauses >= PAUSE and at large-v3's punctuation;
a line that would be on screen < MIN_ON is merged forward when it fits.
"""

import difflib
import json
import re
from pathlib import Path

C = Path(__file__).parent
P = C / "project"
words = json.loads((C / "transcript.json").read_text())["words"]

MAX_WORDS, MAX_CHARS, PAUSE, MIN_ON = 3, 19, 0.28, 0.78
FIT = 21   # characters that fit one Anton line at 0.046h across the plane — merges never exceed it
FORCE_BREAK = set()
# fixed phrases that must never be split across two caption lines
GLUE = {("salah", "faham"), ("gangguan", "mania"), ("gangguan", "personaliti"), ("gangguan", "bipolar"),
        ("penyakit", "mental"), ("perubahan", "mood"), ("fasa", "tinggi"), ("fasa", "mania"), ("fasa", "rendah"),
        ("satu", "minggu"), ("penuh", "semangat"), ("banyak", "bercakap"), ("nak", "stop"), ("banyak", "aktiviti"),
        ("kesan", "negatif"), ("terlalu", "aktif"), ("kurang", "tidur"), ("banyak", "projek"), ("banyak", "tenaga"),
        ("dua", "tiga"), ("tiga", "jam"), ("satu", "hari"), ("sangat", "laju"), ("banyak", "idea"), ("masuk", "akal"),
        ("cepat", "marah"), ("kelakuan", "agresif"), ("pakai", "baju"), ("pakai", "kasut"), ("panjat", "gunung"),
        ("puteri", "gunung"), ("gunung", "ledang"), ("pergi", "kerja"), ("kualiti", "hidup"), ("take", "care"),
        ("di", "ruang"), ("ruang", "komen"), ("pengeluaran", "wang"), ("tidak", "terkawal"), ("kurang", "dari"),
        ("tak", "panggil"), ("lebih", "banyak"), ("individu", "cenderung"), ("ubat-ubatan", "untuk")}


# clause/sentence ends: large-v3's punctuated transcript of the same cut, attached to OUR words by
# sequence-aligning the two word lists (its timestamps drift; its text doesn't)
def _punct_marks():
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
            "-webkit-text-stroke: 3px rgba(0,0,0,0.55); paint-order: stroke fill; "
            "text-shadow: 0 4px 0 rgba(0,0,0,0.35), 0 8px 26px rgba(0,0,0,0.55);")
HERO_CSS = "font-size: calc(0.11*var(--h)); text-transform: uppercase; color: #0E5E6F !important;"
HERO_WORD_T = 6.36          # "bipolar" in "kita kena tahu bipolar" (cut timeline)


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
                lines.append(cur[:-1])     # move the phrase's first word down to join its partner
                cur = cur[-1:]
            elif not glued and (len(cur) >= MAX_WORDS or chars > MAX_CHARS or gap >= PAUSE
                                or punct_break(cur[-1], w)):
                lines.append(cur)
                cur = []
        cur.append(w)
    if cur:
        lines.append(cur)

    # merge lines that would flash. The compiler shows a line from its first word -0.18s until the
    # next line's first word -0.28s, so start-to-start must be >= MIN_ON + 0.10.
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
                    and not punct_break(lines[i][-1], lines[i + 1][0], strong_only=True):
                lines[i:i + 2] = [lines[i] + lines[i + 1]]
            elif i > 0 and len(text(lines[i - 1] + lines[i])) <= FIT \
                    and not punct_break(lines[i - 1][-1], lines[i][0], strong_only=True):
                lines[i - 1:i + 1] = [lines[i - 1] + lines[i]]
            else:
                continue
            changed = True
            break
    return lines


hero_i = min(range(len(words)), key=lambda i: abs(words[i]["start"] - HERO_WORD_T))
assert [w["text"] for w in words[hero_i - 3:hero_i + 1]] == ["kita", "kena", "tahu", "bipolar"], words[hero_i]


def block(ln):
    return {"plane": "narr", "flip": True, "lines": [{"words": [w["text"] for w in ln], "css": BODY_CSS}]}


# hand-broken lines where he speaks fast (auto-grouping left 0.3-0.6s flashes); each entry is the
# exact spoken words, one string per caption line
PINNED = [
    ["ramai yang salah faham", "yang ingat gangguan", "mania ni seperti", "gangguan personaliti", "atau identiti yang",
     "berubah-ubah", "sebelumnya nak tahu mania"],
    ["fasa tinggi atau", "kita panggil sebagai", "fasa mania", "dan juga fasa rendah", "kita panggil sebagai", "depression"],
    ["kurang dari satu minggu"],
    ["orang yang mengalami", "mania akan ada mood", "yang berlebihan"],
    ["orang yang ada bipolar", "akan jadi", "lebih banyak bercakap", "susah nak stop", "percakapan kalau kita",
     "berbual dengan dia", "kita nampak dia"],
    ["tengok orang yang ada", "dalam fasa mania", "tidur dalam dua tiga", "jam je satu hari"],
    ["yang melibatkan risiko", "dan kesukaran untuk", "menumpukan perhatian", "pada sesuatu"],
    ["ada yang saya jumpa", "dia tak pergi kerja", "sebab dia kata", "dia pergi panjat gunung"],
    ["sebab nak cari", "puteri gunung ledang", "di sana sampai tahap", "macam tu sekali"],
    ["penting untuk saya", "ingatkan bahawa", "gangguan bipolar", "memerlukan rawatan", "yang sesuai seperti",
     "terapi dan juga", "mungkin ubat-ubatan", "untuk membantu", "menguruskan gejala"],
    ["kalau ada apa-apa soalan", "boleh tanya di ruang komen", "take care"],
]


def lines_for(ws):
    """group() the free stretches; PINNED phrases keep their hand breaks."""
    toks = [w["text"] for w in ws]
    spans = []
    for spec in PINNED:
        flat = " ".join(spec).split()
        hits = [i for i in range(len(toks) - len(flat) + 1) if toks[i:i + len(flat)] == flat]
        if hits:
            spans.append((hits[0], hits[0] + len(flat), spec))
    spans.sort()
    out, i = [], 0
    for a, b, spec in spans:
        out += group(ws[i:a]) if a > i else []
        k = a
        for ln in spec:
            n = len(ln.split())
            out.append(ws[k:k + n])
            k += n
        i = b
    return out + (group(ws[i:]) if i < len(ws) else [])


used = [spec for spec in PINNED if " ".join(" ".join(spec).split()) in " ".join(w["text"] for w in words)]
assert len(used) == len(PINNED), [spec for spec in PINNED if spec not in used]

blocks = [block(ln) for ln in lines_for(words[:hero_i - 3])]
hero_block = {"plane": "narr", "flip": True, "lines": [
    {"words": ["kita", "kena", "tahu"], "css": BODY_CSS},
    {"words": ["bipolar"], "hero": True, "css": HERO_CSS},
    {"words": ["gangguan", "bipolar", "ni"], "css": BODY_CSS},   # tail: holds the hero ~1.3s (patch_apex.py)
]}
blocks.append(hero_block)
assert [w["text"] for w in words[hero_i + 1:hero_i + 4]] == ["gangguan", "bipolar", "ni"]
blocks += [block(ln) for ln in lines_for(words[hero_i + 4:])]

cin = {
    "dna": "loud",
    "width": 1080, "height": 1920, "fps": 30,
    "planes": {
        # one Anton line just above the hair, clear of the cards (end y450) and TikTok's top UI
        "narr": "top: 23.6%; left: 4%; width: 92%; height: 6.6%;",
        "hero": None,
    },
    "blocks": blocks,
    "tones": {"default": "soft", "hero": "impact"},
}
P.mkdir(exist_ok=True)
(P / "cinematic.json").write_text(json.dumps(cin, indent=1, ensure_ascii=False))
n_lines = sum(len(b["lines"]) for b in blocks)
longest = max((" ".join(l["words"]) for b in blocks for l in b["lines"] if not l.get("hero")), key=len)
print(f"{len(blocks)} blocks, {n_lines} lines; longest line {len(longest)} chars: {longest!r}")
for b in blocks[:14]:
    print(" | ".join(" ".join(l["words"]) for l in b["lines"]))
