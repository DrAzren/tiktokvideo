"""9:16 TikTok layer for the wad-psikiatri video: header, chapter chips and word-highlight captions as one ASS file.

Layout (1080x1920): header 170-440, the 16:9 film as a 1080x608 band at y 470-1078, captions centred on
x=490 (clear of TikTok's right-hand buttons), nothing below y 1430 (caption/UI zone).
Run: ../../../.venv/bin/python make_ass.py   (reads ../doc/build_wad.py for words, punctuation and emphasis sets)
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "doc"))
import build_wad as bw  # noqa: E402  (module level only loads words/maps; main() is not run)

OFF = bw.OFF
BAND_Y = 470
CAP_X, CAP_Y = 490, 1250
MAXL = 20                     # chars per caption line at 62 px
YEL, WHITE, GOLD, TEAL = "&H1FD2FF&", "&HFFFFFF&", "&H41A4D9&", "&HBEC85C&"

CHAPTERS = [  # (anchor phrase, label)
    (None, "BAYANGKAN TAHUN 1911"),
    ("Ramai orang ingat", "ABAD KE-19 · PULAU PINANG & TAIPING"),
    ("Kemudian pada tahun", "1911 · TANJUNG RAMBUTAN"),
    ("Pada tahun 1928", "1928 → 1970-AN · NAMA BERTUKAR"),
    ("Tapi persoalannya", "KEHIDUPAN PESAKIT ZAMAN DULU"),
    ("mulalah satu perubahan", "1950-AN · UBAT ANTIPSIKOTIK"),
    ("Pada tahun 1958", "1958 · WAD DI HOSPITAL UMUM"),
    ("Sekarang kalau kita", "HARI INI · BETUL KE MENAKUTKAN?"),
    ("sebagai doktor psikiatri", "PENGALAMAN DOKTOR PSIKIATRI"),
    ("Saya juga ada tulis", "BUKU · DR, SAYA BOLEH SEMBUH KE?"),
]


def ts(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t // 60 % 60):02d}:{t % 60:05.2f}"


def core(w):
    return re.sub(r"[^\w-]", "", w)


def colour(text):
    c = core(text)
    if c in bw.EMPH_GOLD or c.rstrip(".") in bw.EMPH_GOLD:
        return GOLD
    if c.lower() in bw.EMPH_TEAL:
        return TEAL
    return WHITE


def chunks():
    """Caption chunks: <= 2 lines of MAXL chars, ending at sentence/clause ends or pauses; when a chunk overflows,
    back off to the last word that a new phrase starts with (dan, di, yang, ...) so phrases are not split."""
    out, cur = [], []
    W = bw.WORDS
    for k, w in enumerate(W):
        if cur and sum(len(x["text"]) + 1 for x in cur) + len(w["text"]) > 2 * MAXL - 2:
            cut = next((i for i in range(len(cur) - 1, 1, -1) if bw.nk(cur[i]["text"]) in bw.BREAK_BEFORE
                        or cur[i - 1]["text"].endswith(",")), len(cur))
            out.append(cur[:cut])
            cur = cur[cut:]
        cur.append(w)
        n = sum(len(x["text"]) + 1 for x in cur) - 1
        nxt = W[k + 1] if k + 1 < len(W) else None
        gap = nxt["start"] - w["end"] if nxt else 9
        end = re.search(r"[.?!]$", w["text"]) and w["text"] != "Dr."
        soft = w["text"].endswith(",") or gap > 0.3
        if not nxt or end or (soft and n >= 14):
            out.append(cur)
            cur = []
    out = [c for c in out if c]
    merged = []      # fold a lone trailing word ("lagi") back into its phrase when it still fits on two lines
    for c in out:
        if (merged and len(c) == 1 and not re.search(r"[.?!]$", merged[-1][-1]["text"])
                and sum(len(x["text"]) + 1 for x in merged[-1] + c) - 1 <= 2 * MAXL + 2):
            merged[-1] = merged[-1] + c
        else:
            merged.append(c)
    return merged


def lines(ch):
    """Split a chunk into 1-2 balanced lines (never splitting a KEEP pair)."""
    n = sum(len(x["text"]) + 1 for x in ch) - 1
    if n <= MAXL or len(ch) == 1:
        return [ch]
    best = None
    for c in range(1, len(ch)):
        a = sum(len(x["text"]) + 1 for x in ch[:c]) - 1
        b = n - a - 1
        cost = abs(a - b) + (40 if (bw.nk(ch[c - 1]["text"]), bw.nk(ch[c]["text"])) in bw.KEEP else 0)
        cost += max(0, max(a, b) - MAXL) * 6
        if best is None or cost < best[0]:
            best = (cost, c)
    return [ch[:best[1]], ch[best[1]:]]


def main():
    ev = []
    dur = bw.DUR
    # header (whole video)
    ev.append(f"Dialogue: 1,{ts(0)},{ts(dur)},Brand,,0,0,0,,{{\\an5\\pos(540,196)}}B O R A K   J I W A")
    ev.append(f"Dialogue: 1,{ts(0)},{ts(dur)},Title,,0,0,0,,{{\\an5\\pos(540,268)}}SEJARAH WAD PSIKIATRI")
    ev.append(f"Dialogue: 1,{ts(0)},{ts(dur)},Title,,0,0,0,,{{\\an5\\pos(540,334)}}DI MALAYSIA")
    ev.append(f"Dialogue: 1,{ts(0)},{ts(dur)},Note,,0,0,0,,{{\\an7\\pos(40,{BAND_Y + 608 + 14})}}Visual sejarah: dramatisasi dijana AI")
    # chapter chips
    t0s = [OFF - 1.0 if p is None else bw.T(p) - 0.15 for p, _ in CHAPTERS]
    end_card = bw.WORDS[-1]["end"] + OFF + 0.3
    for k, (_, lab) in enumerate(CHAPTERS):
        a = t0s[k]
        b = t0s[k + 1] - 0.05 if k + 1 < len(CHAPTERS) else end_card
        ev.append(f"Dialogue: 2,{ts(a)},{ts(b)},Chip,,0,0,0,,{{\\an5\\pos(540,410)\\fad(250,200)}}{lab}")
    # captions: one event per active word
    segs = chunks()
    prev_last = None
    for k, ch in enumerate(segs):
        a = ch[0]["start"] + OFF - 0.06
        b = ch[-1]["end"] + OFF + 0.3
        if k + 1 < len(segs):
            b = min(b, segs[k + 1][0]["start"] + OFF - 0.06)
        ls = lines(ch)
        flat = [w for l in ls for w in l]
        cap = prev_last is None or re.search(r"[.?!]$", prev_last["text"]) is not None
        prev_last = ch[-1]

        def word_txt(w):
            t = w["text"]
            if w is ch[-1] and not t.endswith("?"):
                t = t.rstrip(".,:")
            if w is ch[0] and cap:
                t = t[0].upper() + t[1:]
            return t

        for j, w in enumerate(flat):
            s = a if j == 0 else w["start"] + OFF - 0.03
            e = b if j == len(flat) - 1 else flat[j + 1]["start"] + OFF - 0.03
            if e <= s:
                continue
            parts = []
            for l in ls:
                parts.append(" ".join(("{\\c" + (YEL if x is w else colour(x["text"])) + "}" + word_txt(x)) for x in l))
            fade = "\\fad(90,0)" if j == 0 else ""
            ev.append(f"Dialogue: 3,{ts(s)},{ts(e)},Cap,,0,0,0,,{{\\an5\\pos({CAP_X},{CAP_Y}){fade}}}" + "\\N".join(parts))
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Brand,Plus Jakarta Sans ExtraBold,30,&H00BEC85C,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Title,Cinzel SemiBold,62,&H00D8EBF4,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,1,0,1,0,3,5,0,0,0,1
Style: Chip,Plus Jakarta Sans,34,&H0041A4D9,&H00FFFFFF,&H40554F0E,&H00000000,-1,0,0,0,100,100,1,0,3,14,0,5,0,0,0,1
Style: Note,Plus Jakarta Sans Medium,22,&H66D8EBF4,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Cap,Plus Jakarta Sans ExtraBold,62,&H00FFFFFF,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,0,0,1,5,3,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    (HERE / "captions.ass").write_text(head + "\n".join(ev) + "\n")
    print(f"{len(segs)} caption chunks, {len(ev)} events, chapters at " + ", ".join(f"{t:.1f}" for t in t0s))


if __name__ == "__main__":
    main()
