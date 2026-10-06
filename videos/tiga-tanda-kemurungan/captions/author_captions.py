"""Author project/cinematic.json for the `loud` caption identity.
Template: videos/ward-psikiatri/captions/author_captions.py.

Layout (hair top measured on the cut, edit/hair_top.json): graphics cards own y 125-360;
captions run ONE Anton line just above the head and flip line by line, TikTok style:
  - "narr": y ~370-460 (hair top is 460-530 through the body of the video)
  - "high": y ~300-390 for the hook (0-6s, hair at ~405-420, hook card ends at y ~275) and the
            closing CTA from "kalau perlukan bantuan" (he leans in: hair rises to ~420-445)
Both planes span x 6%-82%: clear of TikTok's right-hand action buttons (right ~15%).
One apex: "KEMURUNGAN" (the hook's answer, 0:07.1) slams in BEHIND the head in the cards' teal
while no card is on screen; its block carries the rest of that sentence ("yang ramai orang tak
perasan") so the hero holds through the card-free gap instead of flashing for 0.6s.

Line grouping: lines never cross a sentence/clause start (SENT_START + large-v3 sentence ends); inside a
sentence an optimal break (DP) keeps lines <= FIT chars and avoids orphans, split phrases and flashes.
"""

import difflib
import json
import re
from pathlib import Path

C = Path(__file__).parent
P = C / "project"
words = json.loads((P / "transcript.json").read_text())["words"]

MAX_WORDS, MIN_ON = 4, 0.62
FIT = 21   # characters that fit one Anton line at 0.044h across the 76%-wide plane (~35px/char → 820px)
GLUE = {("tanda-tanda", "ni"), ("skip", "breakfast"), ("bangun", "lewat"), ("main", "game"), ("tengok", "drama"),
        ("makan", "kat"), ("kat", "luar"), ("mood", "swing"), ("tengah", "hari"), ("naik", "turun"),
        ("brain", "fog"), ("cepat", "marah"), ("letih", "fizikal"), ("dalam", "kepala"), ("kesihatan", "mental"),
        ("kesihatan", "fizikal"), ("sama", "penting"), ("di", "Nilai"), ("doktor", "Azren"), ("di", "bio"),
        ("take", "care"), ("susah", "fokus"), ("mudah", "lupa"), ("nombor", "satu"), ("nombor", "tiga"),
        ("nombor", "enam"), ("yang", "kedua"), ("yang", "keempat"), ("yang", "kelima"), ("paling", "common"),
        ("tak", "stabil"), ("bangun", "pagi"), ("hilang", "minat"), ("sepanjang", "masa"), ("diri", "sendiri"),
        ("tiga", "kali"), ("tak", "ada"), ("tak", "boleh"), ("rasa", "penat"), ("rasa", "kosong"), ("rasa", "berat"), ("tak", "perasan"), ("lari", "daripada")}
HIGH_FROM = "kalau perlukan bantuan"   # closing CTA rides the raised plane (he leans in at the end)


def _punct_marks():
    """Clause/sentence ends from large-v3's punctuated transcript of the cut, attached to OUR words
    by sequence-aligning the two word lists (its timestamps drift; its text doesn't)."""
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


def punct_break(prev, strong_only=False):
    m = MARKS.get(prev["idx"])
    return m == "." if strong_only else m is not None


BODY_CSS = ("font-size: calc(0.044*var(--h)); text-transform: uppercase; letter-spacing: 0.01em; "
            "-webkit-text-stroke: 3px rgba(0,0,0,0.55); paint-order: stroke fill; "
            "text-shadow: 0 4px 0 rgba(0,0,0,0.35), 0 8px 26px rgba(0,0,0,0.55);")
HERO_CSS = "font-size: calc(0.11*var(--h)); text-transform: uppercase; color: #0E5E6F !important;"


def text(ln):
    return " ".join(x["text"] for x in ln)


# sentence / clause starts: a caption line never runs across one (spoken thought units)
SENT_START = ["yang nombor tiga", "nombor satu", "bukan selalu", "skip breakfast sebab tak", "bukan sebab", "tapi badan",
              "minda rasa", "nak bangun", "yang kedua", "benda yang dulu", "tapi sekarang", "kalau dulu", "sekarang ni", "yang ni yang",
              "hilang minat", "nombor tiga bila", "bila bangun", "benda pertama", "bukan nak", "kadang-kadang", "nak cari",
              "disebabkan", "yang keempat", "kejap pagi", "tengah hari", "malam rasa", "emosi naik", "tanpa sebab",
              "yang kelima", "baca satu", "otak jadi", "atau kita", "nombor enam", "letih tapi", "letih dalam",
              "benda kecil", "kalau tanda-tanda", "jangan biarkan", "kesihatan mental ni", "kalau anda", "anda boleh",
              "kita buat", "saya akan", "dan kita", "apa yang sesuai", "kalau perlukan", "untuk mendapatkan",
              "bersama saya", "boleh klik", "apa persoalan", "take care"]


def sentences(ws):
    starts = set()
    for ph in SENT_START:
        toks = ph.split()
        for i in range(len(ws) - len(toks) + 1):
            if [w["text"] for w in ws[i:i + len(toks)]] == toks:
                starts.add(i)
    for i in range(1, len(ws)):
        if punct_break(ws[i - 1], strong_only=True):
            starts.add(i)
    cuts = sorted(starts | {0}) + [len(ws)]
    return [ws[a:b] for a, b in zip(cuts, cuts[1:]) if b > a]


def line_cost(ln, nxt):
    """Cost of one caption line: every line costs 1; short orphans, split phrases, pauses inside a
    line and lines too brief to read cost more. Over-wide lines are impossible."""
    t = text(ln)
    if len(t) > FIT and len(ln) > 1:
        return None
    c = 1.0
    if len(ln) == 1 and len(t) < 8:
        c += 3
    if any(b["start"] - a["end"] >= 0.35 for a, b in zip(ln, ln[1:])):
        c += 4
    if nxt is not None and (ln[-1]["text"], nxt["text"]) in GLUE:
        c += 4
    on = (nxt["start"] if nxt is not None else ln[-1]["end"] + 0.9) - ln[0]["start"] - 0.10
    if on < MIN_ON:
        c += 8 * (MIN_ON - on) / MIN_ON + 2
    return c


def group(ws):
    """Optimal line breaks (DP) inside each sentence."""
    lines = []
    for sent in sentences(ws):
        n = len(sent)
        best = [0.0] + [float("inf")] * n
        back = [0] * (n + 1)
        for j in range(1, n + 1):
            for i in range(max(0, j - MAX_WORDS - 1), j):
                nxt = sent[j] if j < n else None
                c = line_cost(sent[i:j], nxt)
                if c is not None and best[i] + c < best[j]:
                    best[j], back[j] = best[i] + c, i
        out, j = [], n
        while j > 0:
            out.append(sent[back[j]:j])
            j = back[j]
        lines += out[::-1]
    for ln in lines:
        assert len(text(ln)) <= FIT or len(ln) == 1, text(ln)
    return lines


hero_i = next(i for i, w in enumerate(words) if w["text"] == "kemurungan")
assert [w["text"] for w in words[hero_i - 3:hero_i]] == ["ini", "mungkin", "tanda"], words[hero_i - 3:hero_i]
tail_end = next(i for i in range(hero_i, len(words)) if words[i]["text"] == "perasan")

# hook lines hand-broken (<=18 chars, each on screen >= 0.5s)
HOOK = ["kalau tiga", "tanda-tanda", "yang saya sebut ni", "ada pada anda", "ini mungkin bukan", "penat yang biasa"]
hook_words = [w["text"] for w in words[:hero_i - 3]]
assert " ".join(HOOK).split() == hook_words, (" ".join(HOOK), hook_words)
blocks = [{"plane": "high", "flip": True, "lines": [{"words": ln.split(), "css": BODY_CSS}]} for ln in HOOK]

hero_block = {"plane": "high", "flip": True, "lines": [
    {"words": ["ini", "mungkin", "tanda"], "css": BODY_CSS},
    {"words": ["kemurungan"], "hero": True, "css": HERO_CSS},
    {"words": [w["text"] for w in words[hero_i + 1:tail_end + 1]], "css": BODY_CSS},
]}
assert hero_block["lines"][2]["words"] == ["yang", "ramai", "orang", "tak", "perasan"], hero_block["lines"][2]
blocks.append(hero_block)

hi = next(i for i in range(len(words)) if " ".join(w["text"] for w in words[i:i + len(HIGH_FROM.split())]) == HIGH_FROM)
for ln in group(words[tail_end + 1:hi]):
    blocks.append({"plane": "narr", "flip": True, "lines": [{"words": [w["text"] for w in ln], "css": BODY_CSS}]})
for ln in group(words[hi:]):
    blocks.append({"plane": "high", "flip": True, "lines": [{"words": [w["text"] for w in ln], "css": BODY_CSS}]})

cin = {
    "dna": "loud",
    "width": 1080, "height": 1920, "fps": 30,
    "planes": {
        "narr": "top: 19.3%; left: 6%; width: 76%; height: 4.8%;",
        "high": "top: 15.6%; left: 6%; width: 76%; height: 4.8%;",
        "hero": None,
    },
    "blocks": blocks,
    "tones": {"default": "soft", "hero": "impact"},
}
(P / "cinematic.json").write_text(json.dumps(cin, indent=1, ensure_ascii=False))
n_lines = sum(len(b["lines"]) for b in blocks)
print(f"{len(blocks)} blocks, {n_lines} lines, hero block = {len(hero_block['lines'])} lines")
for b in blocks:
    print(f"{b['plane']:4} | " + " | ".join(" ".join(l["words"]) for l in b["lines"]))
