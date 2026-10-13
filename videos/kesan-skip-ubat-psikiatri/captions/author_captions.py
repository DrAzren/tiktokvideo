"""Author project/cinematic.json for the `loud` caption identity.
Template: videos/ubat-psikiatri-olanzapine/captions/author_captions.py.

Layout: the speaker sits high in a car (hair top y ~490-560), so graphics cards own y 130-372 and the
captions run in a one-line plane just above the hair (y ~390-500), flipping line by line, TikTok style.
One apex: "BERHENTI" (the patient's question in the hook, 0:02.4) slams in BEHIND the head, teal, while
no card or insert is on screen; its lockup carries "saya nak" above it and "ubat sendiri" as the tail.

Line grouping: 1-3 words, <= MAX_CHARS, break at pauses >= PAUSE; a line that would be on screen
< MIN_ON is merged forward when it fits.
"""

import json
from pathlib import Path

C = Path(__file__).parent
P = C / "project"
words = json.loads((P / "transcript.json").read_text())["words"]

MAX_WORDS, MAX_CHARS, PAUSE, MIN_ON = 3, 21, 0.28, 0.62
FIT = 24   # Anton at 0.046h: 24-char lines measure 830-965px in Chromium vs the 994px plane (every line width-checked)
# forced breaks (prev, word) at clause ends large-v3 left unpunctuated
FORCE_BREAK = {("sikit", "saya"), ("sendiri", "takpe"), ("doktor", "assalamualaikum"), ("psikiatri", "jom"),
               ("sekejap", "apa"), ("doktor", "yang"), ("relapse", "gejala"), ("semula", "ubat"), ("kita", "bila"),
               ("semula", "contohnya"), ("balik", "rasa"), ("balik", "yang"), ("penarikan", "bukan"),
               ("mengejut", "boleh"), ("serabut", "yang"), ("rawatan", "setiap"), ("balik", "lambat"),
               ("bawah", "kadang-kadang"), ("lagi", "saya"), ("baik", "di"), ("Nilai", "kami"), ("one-on-one", "boleh"),
               ("tidur", "nak"), ("diagnosis", "boleh"), ("Nilai", "kalau"), ("tidak", "atau"), ("pasti", "boleh"),
               ("mental", "take"), ("Azren", "doktor")}
# fixed phrases that must never be split across two caption lines
GLUE = {("mood", "swing"), ("withdrawal", "symptom"), ("reset", "button"), ("second", "opinion"), ("take", "care"),
        ("kesihatan", "mental"), ("ubat", "psikiatri"), ("tak", "stabil"), ("masuk", "wad"), ("pening", "kepala"),
        ("gangguan", "tidur"), ("emosi", "huru-hara"), ("proses", "rawatan"), ("tak", "efektif"), ("berita", "baik"),
        ("di", "Nilai"), ("masalah", "tidur"), ("start", "rawatan"), ("tentukan", "diagnosis"), ("tak", "pasti"),
        ("doktor", "Azren"), ("risiko", "relapse"), ("rasa", "loya"), ("dulu", "lagi"), ("gejala", "berulang"),
        ("gejala", "penarikan"), ("rasa", "cemas"), ("ubat", "sendiri"), ("sihat", "sikit"), ("isu", "kemurungan"), ("mulakan", "rawatan"), ("teruskan", "rawatan"), ("stop", "start")}


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
HERO_WORD_T = 2.41          # "berhenti" in "saya nak berhenti ubat sendiri" (cut timeline)
HERO_BLOCK_END = 3.9        # lockup = kicker + hero + one tail line; ends before "takpe ke doktor" (3.96s)


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
    return rebreak(no_orphans(lines, on_time, text))


# hand re-breaks where the automatic split cuts a phrase awkwardly or leaves a line flashing:
# consecutive auto lines (as text) -> the same words re-partitioned
REBREAK = {
    ("ubat psikiatri ni", "macam pelindung", "untuk kita"): ["ubat psikiatri ni macam", "pelindung untuk kita"],
    ("rasa cemas semakin", "menjadi-jadi atau", "sampai tahap boleh", "masuk wad balik"):
        ["rasa cemas", "semakin menjadi-jadi", "atau sampai tahap", "boleh masuk wad balik"],
    ("servis konsultasi dan", "juga saringan"): ["servis konsultasi", "dan juga saringan"],
    ("boleh datang klinik", "saya di Nilai"): ["boleh datang", "klinik saya di Nilai"],
    ("kalau anda tengah", "keliru patut", "teruskan rawatan"): ["kalau anda tengah keliru", "patut teruskan rawatan"],
}


def rebreak(lines):
    out, i = [], 0
    while i < len(lines):
        for key, new in REBREAK.items():
            span = lines[i:i + len(key)]
            if tuple(" ".join(w["text"] for w in ln) for ln in span) == key:
                flat = [w for ln in span for w in ln]
                assert " ".join(w["text"] for w in flat) == " ".join(new), (key, new)
                k = 0
                for t in new:
                    n = len(t.split())
                    out.append(flat[k:k + n])
                    k += n
                i += len(key)
                break
        else:
            out.append(lines[i])
            i += 1
    return out


def no_orphans(lines, on_time, text):
    """User rule: no orphan word alone on a line, no line under 0.5 s where it can be avoided.
    A short single word (< 12 chars) merges into a neighbour when it fits; otherwise it borrows the
    previous line's last word (shifting one more word up a line when the previous line has only two).
    Then a line on screen < 0.5 s borrows the previous line's last word (it starts earlier)."""
    def strong(a, b):
        return punct_break(a, b, strong_only=True) or (a["text"], b["text"]) in FORCE_BREAK

    def glued(a, b):
        return (a["text"], b["text"]) in GLUE

    changed = True
    while changed:
        changed = False
        for i, ln in enumerate(lines):
            if len(ln) != 1 or len(ln[0]["text"]) >= 12:
                continue
            p = lines[i - 1] if i > 0 else None
            n = lines[i + 1] if i + 1 < len(lines) else None
            if p and len(text(p + ln)) <= FIT and not strong(p[-1], ln[0]):
                lines[i - 1:i + 1] = [p + ln]
            elif n and len(text(ln + n)) <= FIT and not strong(ln[0], n[0]):
                lines[i:i + 2] = [ln + n]
            elif p and len(p) >= 3 and not glued(p[-2], p[-1]) and not strong(p[-1], ln[0]):
                lines[i] = [p.pop()] + ln
            elif p and len(p) == 2 and i > 1 and len(text(lines[i - 2] + p[:1])) <= FIT \
                    and not strong(lines[i - 2][-1], p[0]) and not strong(p[-1], ln[0]):
                lines[i - 2].append(p.pop(0))
                lines[i] = [p.pop()] + ln
                del lines[i - 1]
            else:
                continue
            changed = True
            break
    for i in range(1, len(lines)):
        p, ln = lines[i - 1], lines[i]
        if on_time(i, lines) < 0.5 and len(p) >= 3 and not glued(p[-2], p[-1]) and not strong(p[-1], ln[0]) \
                and len(text(p[-1:] + ln)) <= FIT:
            lines[i] = [p.pop()] + ln
    return lines


hero_i = min(range(len(words)), key=lambda i: abs(words[i]["start"] - HERO_WORD_T))
assert words[hero_i]["text"] == "berhenti" and words[hero_i - 1]["text"] == "nak", words[hero_i]
end_i = max(i for i, w in enumerate(words) if w["start"] < HERO_BLOCK_END)

# the patient's opening line, before the hero lockup
blocks = [{"plane": "narr", "flip": True, "lines": [{"words": [w["text"] for w in ln], "css": BODY_CSS}]}
          for ln in group(words[:hero_i - 2])]
hero_block = {"plane": "narr", "flip": True, "lines": [
    {"words": ["saya", "nak"], "css": BODY_CSS},
    {"words": ["berhenti"], "hero": True, "css": HERO_CSS},
]}
assert [w["text"] for w in words[hero_i - 2:hero_i]] == ["saya", "nak"]
tail = [w["text"] for w in words[hero_i + 1:end_i + 1]]
assert tail == ["ubat", "sendiri"], tail
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
for b in blocks:
    print(" | ".join(" ".join(l["words"]) for l in b["lines"]))
