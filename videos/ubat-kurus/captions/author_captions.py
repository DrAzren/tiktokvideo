"""Author project/cinematic.json for the `loud` caption identity.

Layout: graphics cards own the car-roof headroom (y 150-560). Captions run as ONE line on
the chest band (plane top 68% = y1306, below the chin even at the 1.07 punch-in; bottom
~75%, clear of TikTok's bottom ~20% UI) and stop at 84% width, left of the action buttons.
Lines flip TikTok style. No hero: every caption is in front of the subject (no matte).

Line grouping: 1-3 words, <= MAX_CHARS, break at pauses >= PAUSE and at large-v3's sentence /
clause marks; a line that would be on screen < MIN_ON is merged when it fits.
"""

import difflib
import json
import re
from pathlib import Path

C = Path(__file__).parent
P = C / "project"
words = json.loads((P / "transcript.json").read_text())["words"]
LV3 = C.parent / "edit" / "verify" / "cut_lv3_final.json"   # large-v3 on the final cut (punctuation)

MAX_WORDS, MAX_CHARS, PAUSE, MIN_ON = 3, 18, 0.28, 0.5
FIT = 21   # merges of flashing lines may reach this (0.046h Anton: 21 chars fit the 80%-wide band)
GLUE = {("berat", "badan"), ("selera", "makan"), ("kesan", "sampingan"), ("jangka", "panjang"),
        ("jabatan", "psikiatri"), ("take", "care"), ("masalah", "mood"), ("masalah", "anxiety"),
        ("berhenti", "merokok"), ("ruang", "komen"), ("setengah", "orang"), ("ubat", "sawan"),
        ("turun", "berat"), ("naik", "balik"), ("widely", "used"), ("rasa", "kenyang"),
        ("rasa", "semput"), ("kurang", "craving"), ("dos", "yang"), ("yang", "tinggi"),
        ("doktor", "azren"), ("sejenis", "antidepressant"), ("merawat", "kemurungan")}


def _punct_marks():
    norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())
    lv3 = []
    for w in json.loads(LV3.read_text()):   # whisper splits reduplications: "masing" + "-masing." -> rejoin
        t = w["text"]
        if lv3 and t.startswith("-"):
            lv3[-1] += t
        else:
            lv3.append(t)
    # our joined reduplications ("ubat-ubat") are one token; large-v3 writes them the same way
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
# sentence ends large-v3 spells differently (rupopion / topiramid / fluozetin / mata-mata), so difflib can't match them
for _i, _w in enumerate(words):
    if _w["text"] in ("bupropion", "topiramate", "fluoxetine", "semata-mata"):
        MARKS[_i] = "."
for _i, _w in enumerate(words):
    _w["idx"] = _i


def punct_break(prev, strong_only=False):
    m = MARKS.get(prev["idx"])
    return m == "." if strong_only else m is not None


BODY_CSS = ("font-size: calc(0.046*var(--h)); text-transform: uppercase; letter-spacing: 0.01em; "
            "-webkit-text-stroke: 3px rgba(0,0,0,0.55); paint-order: stroke fill; "
            "text-shadow: 0 4px 0 rgba(0,0,0,0.35), 0 8px 26px rgba(0,0,0,0.55);")


def text(ln):
    return " ".join(x["text"] for x in ln)


FUNC = {"di", "dan", "yang", "untuk", "dengan", "ni", "ada", "pada", "nak", "sebab", "kalau", "akan", "boleh",
        "adalah", "the", "and", "for", "saya", "kena", "tu"}


def group(ws):
    """Optimal line breaks (DP over the word sequence), minimising:
      inf   line > FIT chars, or a sentence end ('.') inside a line
      big   line on screen < MIN_ON (it flashes); mild cost when > 2.4s
      +8    breaking a GLUE phrase; +3 ending a line on a function word; +1 any other break
       0    breaking at a clause mark or a pause >= PAUSE
    A line is shown from its first word until the next line's first word (start-to-start - 0.10)."""
    n = len(ws)
    INF = float("inf")

    def line_cost(i, j):          # words i..j-1 form one line
        ln = ws[i:j]
        if len(text(ln)) > FIT and j - i > 1:
            return INF
        if j - i > 4:
            return INF
        if any(MARKS.get(w["idx"]) == "." for w in ln[:-1]):
            return INF
        nxt = ws[j]["start"] if j < n else ws[j - 1]["end"] + 0.9
        on = nxt - ws[i]["start"] - 0.10
        c = 0.0
        if on < MIN_ON:
            c += 40 + 200 * (MIN_ON - on)
        elif on > 2.4:
            c += 2 * (on - 2.4)
        if j < n:                 # the break after this line
            a, b = ws[j - 1], ws[j]
            if MARKS.get(a["idx"]) or b["start"] - a["end"] >= PAUSE:
                pass
            elif (a["text"], b["text"]) in GLUE:
                c += 8
            elif a["text"] in FUNC:
                c += 3
            else:
                c += 1
        return c + 0.5            # per-line cost: prefer fuller lines

    best = [INF] * (n + 1)
    nxt_cut = [n] * (n + 1)
    best[n] = 0.0
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, min(n, i + 4) + 1):
            c = line_cost(i, j)
            if c + best[j] < best[i]:
                best[i], nxt_cut[i] = c + best[j], j
    lines, i = [], 0
    while i < n:
        lines.append(ws[i:nxt_cut[i]])
        i = nxt_cut[i]
    return lines


lines = group(words)
for ln in lines:
    assert len(text(ln)) <= max(FIT, max(len(w["text"]) for w in ln)), text(ln)
blocks = [{"plane": "narr", "flip": True, "lines": [{"words": [w["text"] for w in ln], "css": BODY_CSS}]}
          for ln in lines]

cin = {
    "dna": "loud",
    "width": 1080, "height": 1920, "fps": 30,
    "planes": {
        "narr": "top: 68%; left: 4%; width: 80%; height: 7%;",
        "hero": None,
    },
    "blocks": blocks,
    "tones": {"default": "soft"},
}
(P / "cinematic.json").write_text(json.dumps(cin, indent=1, ensure_ascii=False))
print(f"{len(blocks)} caption lines")
short = []
for i, ln in enumerate(lines):
    nxt = lines[i + 1][0]["start"] if i + 1 < len(lines) else ln[-1]["end"] + 0.9
    if nxt - ln[0]["start"] - 0.1 < MIN_ON:
        short.append((text(ln), round(nxt - ln[0]["start"] - 0.1, 2)))
print("short lines:", short)
print(" | ".join(text(ln) for ln in lines))
