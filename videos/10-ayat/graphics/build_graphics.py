"""'10 Ayat Dilarang Cakap' — the full 1080x1920 composition (HyperFrames).

Layers, back to front:
  1  studio background (the user's image, softened for depth of field) — zooms less than the speaker
  2  behind-the-head type: the "10 AYAT" hook slam and each statement's big numeral
  3  the speaker (speaker.webm: RVM-matted, graded, transparent) — punch-ins 1.0/1.15/1.30 at cuts
  4  headroom cards: "0N / 10" counter, the harmful line word-synced (red strike when the
     explanation starts), then the supportive takeaway in gold/ivory
  5  full-screen inserts: Higgsfield B-roll (5 clips, "Ilustrasi AI" tag) and motion-graphic cards
  6  captions (Malay, word-highlighted, max 2 lines, clear of the face and the TikTok UI)
Every time is anchored to a phrase in edit/cut_words.json, so a new cut re-times everything.
Also writes sfx_cues.json (every transition / reveal) for audio/build_audio.py.

Run: ../../../.venv/bin/python build_graphics.py
"""

import html
import json
from fractions import Fraction
from pathlib import Path

G = Path(__file__).parent
P = G / "public"
ROOT = G.parent
WORDS = json.loads((ROOT / "edit" / "cut_words.json").read_text())
EDL = json.loads((ROOT / "edit" / "edl.json").read_text())
FPS, W, H = 30, 1080, 1920
DUR = round(sum(float((Fraction(round(r["end"] * FPS)) - Fraction(round(r["start"] * FPS))) / FPS) for r in EDL["ranges"])
            + EDL["tail_hold"], 4)
LEAD = 0.10
GOLD, GOLD2, IVORY, NAVY, CHAR, GREEN, RED = "#E9B44C", "#F6D58E", "#FFF5E4", "#0E1A2B", "#17181C", "#7FA36B", "#E5484D"
FOCUS = (540, 768)            # punch-in origin: the face, in frame px (EDL punch_focus 0.5/0.4)
SFX = []                      # (t, kind, gain_db)


def T(phrase: str, after: float = 0.0, end: bool = False) -> float:
    toks = phrase.split()
    for i in range(len(WORDS) - len(toks) + 1):
        if WORDS[i]["start"] >= after - 1e-6 and [w["text"] for w in WORDS[i:i + len(toks)]] == toks:
            return WORDS[i + len(toks) - 1]["end"] if end else WORDS[i]["start"]
    raise KeyError(phrase)


def fq(t: float) -> float:
    return round(round(t * FPS) / FPS, 4)


def sfx(t, kind, gain=0.0):
    SFX.append({"t": round(t, 3), "kind": kind, "gain_db": gain})


# ---------------------------------------------------------------- range starts on the output timeline
CUTS, acc = [], 0.0
for r in EDL["ranges"]:
    s, e = Fraction(round(r["start"] * FPS)) / FPS, Fraction(round(r["end"] * FPS)) / FPS
    CUTS.append((round(acc, 4), r["punch"]))
    acc += float(e - s)

# ---------------------------------------------------------------- the ten statements
# open: words that announce it; quote: the harmful line as displayed (word-synced to the phrase);
# strike: where the explanation starts; support: [(anchor phrase, html)] takeaways in gold/ivory
STMT = [
    dict(open="satu", qp="kau ni terlalu fikir banyak sangat",
         quote="Kau ni terlalu fikir banyak sangat.", strike="masalah mental ni",
         support=[("bukan semata mata", "Bukan semata-mata <em>overthinking</em>")]),
    dict(open="yang kedua", qp="ramai lagi orang lain yang lagi teruk daripada kau",
         quote="Ramai lagi orang lain yang lagi teruk daripada kau.", strike="ini boleh buatkan",
         support=[("sedangkan semua orang", "Semua orang ada <em>cabaran</em> masing-masing")]),
    dict(open="yang ketiga", qp="kau ni manja sangat sebab tu boleh jadi sampai macam ni",
         quote="Kau ni manja sangat, sebab tu boleh jadi sampai macam ni.", strike="ni pun boleh",
         support=[("perasaan malu", "Menambah rasa <em>malu</em>"), ("rasa bersalah", "&amp; rasa <em>bersalah</em>")]),
    dict(open="yang keempat", qp="kau ni doa je lebih sikit nanti baik lah tu",
         quote="Kau ni doa je lebih sikit, nanti baik+lah tu.", strike="betul doa tu",
         support=[("doa tu penting", "Doa tu <em>penting</em>"), ("tapi kesihatan mental juga", "tapi perlukan <em>rawatan</em>")]),
    dict(open="yang kelima", qp="kau ni dah gila eh",
         quote="Kau ni dah gila eh.", strike="yang ni stigma",
         support=[("stigma macam ni", "<em>Stigma</em> yang menyakitkan")]),
    dict(open="yang keenam", qp="kau ambik je cuti nanti okey lah tu",
         quote="Kau ambik je cuti, nanti okey+lah tu.", strike="okey rehat penting",
         support=[("rehat penting", "Rehat <em>penting</em>"), ("tapi ini bukan semudah", "tapi bukan <em>semudah</em> itu")]),
    dict(open="yang ketujuh", qp="semua ni ada dalam kepala je",
         quote="Semua ni ada dalam kepala je.", strike="kesihatan mental ni dia",
         support=[("bukanlah benda yang", "Bukan <em>main-main</em>"), ("bukanlah rekaan", "Bukan <em>rekaan</em>"),
                  ("menjejaskan fungsi harian", "Menjejaskan <em>fungsi harian</em>")]),
    dict(open="yang ke lapan", qp="jangan tunjuk sangat lah nanti orang fikir kau lemah",
         quote="Jangan tunjuk sangat+lah. Nanti orang fikir kau lemah.", strike="sebenarnya kita",
         support=[]),
    dict(open="yang ke sembilan", qp="kau kena lah kuat sikit",
         quote="Kau kena+lah kuat sikit.", strike="orang yang ada masalah",
         support=[("dah kuat sebenarnya", "Mereka <em>dah kuat</em> sebenarnya")]),
    dict(open="yang ke sepuluh", qp="kau ni macam cari perhatian je",
         quote="Kau ni macam cari perhatian je.", strike="sebenarnya mereka ni",
         support=[("sedang cari bantuan", "Mereka sedang cari <em>bantuan</em>")]),
]
t_prev = 0.0
for i, s in enumerate(STMT):
    s["n"] = i + 1
    s["t_open"] = T(s["open"], after=t_prev)
    s["t_q0"] = T(s["qp"], after=s["t_open"])
    s["t_q1"] = T(s["qp"], after=s["t_open"], end=True)
    s["t_strike"] = T(s["strike"], after=s["t_q1"])
    s["sup"] = [(T(p, after=s["t_strike"] - 0.01), h) for p, h in s["support"]]
    nq = len(s["qp"].split())
    s["qwords"] = WORDS[[k for k, w in enumerate(WORDS) if abs(w["start"] - s["t_q0"]) < 1e-6][0]:][:nq]
    t_prev = s["t_strike"]
for i, s in enumerate(STMT):
    s["t_end"] = STMT[i + 1]["t_open"] - 0.12 if i + 1 < len(STMT) else T("kesimpulan dia") - 0.1

B = {}
B["end_open"] = T("kesimpulan dia")
B["quote_mg"] = T("saya ada di sini")
B["cukup"] = T("itu pun dah cukup")
B["cta"] = T("kalau ada apa apa soalan")
B["takecare"] = T("take care", end=True)
B["endcard"] = fq(B["takecare"] + 0.15)

# ---------------------------------------------------------------- full-screen inserts
# (id, kind, start, end, src or mg-key, tag/label)
FS = [
    ("f-brain", "mg", T("melibatkan perubahan") - 0.08, T("otak", end=True) + 0.25, "brain", None),
    ("f-valid", "broll", T("ini boleh buatkan") - 0.05, T("sedangkan semua") - 0.08, "a_window", "Rasa perasaan dia tak valid"),
    ("f-pro", "broll", T("kesihatan mental juga") - 0.08, T("profesional", end=True) + 0.25, "c_clinic", "Rawatan &amp; sokongan profesional"),
    ("f-stigma", "broll", T("sebab ni bukan gurauan") - 0.08, T("kesihatan mental", after=T("untuk orang yang ada")) + 0.6, "b_words", "Ini bukan gurauan"),
    ("f-proses", "mg", T("dia memerlukan") - 0.08, T("mental ni", after=T("dia memerlukan"), end=True) + 0.2, "proses", None),
    ("f-pendam", "mg", T("kita menggalakkan") - 0.08, T("keadaan", after=T("kita menggalakkan"), end=True) + 0.25, "pendam", None),
    ("f-juang", "broll", T("sebab mereka masih") - 0.08, T("kehidupan mereka", end=True) + 0.25, "d_morning", "Masih berjuang setiap hari"),
    ("f-empati", "broll", T("kita ni yang patut") - 0.08, T("judge mereka", end=True) + 0.25, "e_support", "Tunjuk empati"),
    ("f-quote", "mg", B["quote_mg"] - 0.25, T("perlukan saya", after=B["quote_mg"], end=True) + 0.35, "quote", None),
    ("f-besar", "broll", B["cukup"] - 0.05, T("mental ni", after=B["cukup"], end=True) + 0.15, "e_support_tight", "Itu pun dah cukup besar"),
    ("f-end", "mg", B["endcard"], DUR, "endcard", None),
]
FS = [(i, k, fq(a), fq(b), s, l) for i, k, a, b, s, l in FS]
# no caption on top of the quote card and end card (they say it), nor during the hook
NOCAP = [(0.0, STMT[0]["t_open"] - 0.05)] + [(fq(s["t_q0"] - 0.1), fq(s["t_q1"] + 0.15)) for s in STMT] \
    + [(a, b) for i, k, a, b, s, l in FS if s in ("quote", "endcard")]


def covered(t0, t1):
    """True when [t0, t1] overlaps a full-screen insert."""
    return any(a < t1 and b > t0 for _, _, a, b, _, _ in FS)


# ---------------------------------------------------------------- captions
FIX = {"kesehatan": "kesihatan", "satu": "Satu,", "okey": "okey", "judge": "<i>judge</i>",
       "overthinking": "<i>overthinking</i>", "take": "Take"}
MERGE = [("semata", "mata", "semata-mata"), ("masing", "masing", "masing-masing"), ("main", "main", "main-main"),
         ("apa", "apa", "apa-apa"), ("okey", "lah", "okeylah"), ("baik", "lah", "baiklah"), ("kena", "lah", "kenalah"),
         ("sangat", "lah", "sangatlah"), ("lagi", "lah", "lagilah"), ("ke", "lapan", "kelapan"),
         ("ke", "sembilan", "kesembilan"), ("ke", "sepuluh", "kesepuluh")]
REPL = {("tanya", "orang"): "dalam"}   # "boleh tanya orang komen" -> what he says: "dalam komen" (user-confirmed)
# sentence ends (cut-timeline phrases whose last word closes a sentence / clause)
STOPS = ["mental", "sangat", "otak", "kau", "valid", "masing", "ni", "tu", "profesional", "eh", "menyakitkan",
         "gurauan", "penting", "sembuh", "je", "rekaan", "seseorang", "lemah", "mereka", "keadaan", "sikit",
         "bantuan", "dia", "sekadar", "saya", "soalan", "komen", "care"]


def cap_words():
    out, i = [], 0
    while i < len(WORDS):
        w = dict(WORDS[i])
        if i + 1 < len(WORDS):
            n = WORDS[i + 1]
            for a, b, m in MERGE:
                if w["text"] == a and n["text"] == b and n["start"] - w["end"] < 0.25:
                    w = {"text": m, "start": w["start"], "end": n["end"]}
                    i += 1
                    break
        if i > 0 and (WORDS[i - 1]["text"], WORDS[i]["text"]) in REPL:
            w["text"] = REPL[(WORDS[i - 1]["text"], WORDS[i]["text"])]
        w["text"] = FIX.get(w["text"], w["text"])
        out.append(w)
        i += 1
    return out


def cap_groups():
    ws = [w for w in cap_words()]
    groups, cur = [], []
    for k, w in enumerate(ws):
        if cur:
            gap = w["start"] - cur[-1]["end"]
            chars = len(" ".join(x["text"] for x in cur + [w]))
            if w["text"] == "Take" or chars > 34 or len(cur) >= 6 or gap > 0.35 or (len(cur) >= 3 and cur[-1]["text"].rstrip(",") in STOPS and gap > 0.12):
                groups.append(cur)
                cur = []
        cur.append(w)
    groups.append(cur)
    out = []
    for n, g in enumerate(groups):
        t0 = g[0]["start"] - 0.06
        t1 = min(groups[n + 1][0]["start"] - 0.06, g[-1]["end"] + 0.6) if n + 1 < len(groups) else g[-1]["end"] + 0.6
        # trim against caption-free windows
        for a, b in NOCAP:
            if t0 >= a and t1 <= b:
                t0 = t1 = None
                break
            if t0 < a < t1 and t1 <= b:
                t1 = a
            if a <= t0 < b < t1:
                t0 = b
        if t0 is None or t1 - t0 < 0.3:
            continue
        g2 = [w for w in g if w["end"] > t0 and w["start"] < t1]
        if g2:
            out.append((fq(t0), fq(t1), g2))
    return out


# ---------------------------------------------------------------- quote card entrances (10 different)
ENTER = ["rise", "blurslide", "type", "pop", "slam", "wipe", "track", "split", "drop", "flip"]


def word_anim(kind, sel, t, k):
    e = "power3.out"
    if kind == "rise":
        return f"tl.fromTo('{sel}', {{opacity:0, y:46}}, {{opacity:1, y:0, duration:0.32, ease:'{e}'}}, {t});"
    if kind == "blurslide":
        return f"tl.fromTo('{sel}', {{opacity:0, x:-60, filter:'blur(12px)'}}, {{opacity:1, x:0, filter:'blur(0px)', duration:0.34, ease:'power4.out'}}, {t});"
    if kind == "type":
        return f"tl.fromTo('{sel}', {{opacity:0}}, {{opacity:1, duration:0.06, ease:'none'}}, {t});"
    if kind == "pop":
        return f"tl.fromTo('{sel}', {{opacity:0, scale:0.4}}, {{opacity:1, scale:1, duration:0.32, ease:'back.out(2.2)'}}, {t});"
    if kind == "slam":
        return f"tl.fromTo('{sel}', {{opacity:0, scale:1.9}}, {{opacity:1, scale:1, duration:0.24, ease:'power4.out'}}, {t});"
    if kind == "wipe":
        return f"tl.fromTo('{sel}', {{clipPath:'inset(0% 100% 0% 0%)'}}, {{clipPath:'inset(0% 0% 0% 0%)', duration:0.3, ease:'power2.out'}}, {t});"
    if kind == "track":     # tracking-in look with transforms only (letterSpacing snaps under frame capture)
        return f"tl.fromTo('{sel}', {{opacity:0, scaleX:1.7, x:{40 + 25 * k}}}, {{opacity:1, scaleX:1, x:0, duration:0.4, ease:'power3.out'}}, {t});"
    if kind == "split":
        d = -80 if k % 2 == 0 else 80
        return f"tl.fromTo('{sel}', {{opacity:0, x:{d}}}, {{opacity:1, x:0, duration:0.34, ease:'{e}'}}, {t});"
    if kind == "drop":
        return f"tl.fromTo('{sel}', {{opacity:0, y:-70}}, {{opacity:1, y:0, duration:0.42, ease:'bounce.out'}}, {t});"
    if kind == "flip":
        return f"tl.fromTo('{sel}', {{opacity:0, rotationX:-95}}, {{opacity:1, rotationX:0, duration:0.4, ease:'power3.out'}}, {t});"
    raise ValueError(kind)


# ---------------------------------------------------------------- motion-graphic bodies
def mg_body(key, st, en):
    """(html, [js]) for a full-screen motion graphic starting at st."""
    js = []
    if key == "brain":
        t1, t2 = T("perubahan kimia"), T("di dalam otak")
        nodes = [(250, 820), (430, 690), (620, 760), (800, 650), (330, 1010), (540, 930), (760, 880), (470, 1150), (680, 1100), (860, 1020)]
        edges = [(0, 1), (1, 2), (2, 3), (0, 4), (1, 5), (2, 5), (3, 6), (4, 5), (5, 6), (4, 7), (5, 8), (6, 9), (7, 8), (8, 9), (2, 6)]
        lines = "".join(f'<line class="nl" x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[b][0]}" y2="{nodes[b][1]}"/>' for a, b in edges)
        dots = "".join(f'<circle class="nd" id="bn{i}" cx="{x}" cy="{y}" r="16"/>' for i, (x, y) in enumerate(nodes))
        sparks = "".join(f'<circle class="sp" id="bs{k}" r="9" cx="{nodes[a][0]}" cy="{nodes[a][1]}"/>' for k, (a, b) in enumerate(edges[:8]))
        h = f'''<div class="mg-bg navy"></div><div class="glow g1"></div>
        <div class="mg-chip" id="br-c">01 / 10 · Realiti</div>
        <div class="mg-h" id="br-h">Perubahan <span class="gold">kimia</span></div>
        <div class="mg-h2" id="br-h2">di dalam otak</div>
        <svg class="net" viewBox="0 0 1080 1920">{lines}{dots}{sparks}</svg>'''
        js += [f"tl.fromTo('#br-c', {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:0.35, ease:'power3.out'}}, {fq(st + 0.1)});",
               f"tl.fromTo('#br-h', {{opacity:0, y:50}}, {{opacity:1, y:0, duration:0.45, ease:'power3.out'}}, {fq(t1 - LEAD)});",
               f"tl.fromTo('#br-h2', {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.4, ease:'power3.out'}}, {fq(t2 - LEAD)});",
               f"tl.fromTo('#f-brain .nl', {{strokeDashoffset:400}}, {{strokeDashoffset:0, duration:1.2, stagger:0.05, ease:'power2.out'}}, {fq(st + 0.15)});",
               f"tl.fromTo('#f-brain .nd', {{scale:0, transformOrigin:'50% 50%'}}, {{scale:1, duration:0.35, stagger:0.06, ease:'back.out(2)'}}, {fq(st + 0.2)});"]
        for k, (a, b) in enumerate(edges[:8]):
            x0, y0, x1, y1 = *nodes[a], *nodes[b]
            js.append(f"tl.fromTo('#bs{k}', {{attr:{{cx:{x0}, cy:{y0}}}, opacity:0}}, {{attr:{{cx:{x1}, cy:{y1}}}, opacity:1, duration:0.7, ease:'power1.inOut'}}, {fq(t1 + 0.08 * k)});")
            js.append(f"tl.to('#bs{k}', {{opacity:0, duration:0.2, ease:'power1.in'}}, {fq(t1 + 0.08 * k + 0.7)});")
        sfx(t1 - LEAD, "pop", -4)
        return h, js
    if key == "proses":
        t1, t2, t3 = T("satu proses"), T("untuk pemulihan"), T("masalah kesihatan", after=T("untuk pemulihan"))
        steps = [("Cuti", "rehat"), ("Rawatan", "&amp; sokongan"), ("Pemulihan", "ambil masa")]
        nodes = "".join(f'<div class="pnode" id="pn{i}" style="top:{820 + i * 250}px"><span class="pdot">{i + 1}</span>'
                        f'<span class="plab"><b>{a}</b><small>{b}</small></span></div>' for i, (a, b) in enumerate(steps))
        h = f'''<div class="mg-bg navy"></div><div class="glow g2"></div>
        <div class="mg-chip" id="pr-c">06 / 10 · Realiti</div>
        <div class="mg-h" id="pr-h">Satu <span class="gold">proses</span></div>
        <div class="mg-h2" id="pr-h2">untuk pemulihan</div>
        <svg class="prail" viewBox="0 0 40 760"><path id="pr-rail" d="M20 10V750"/></svg>{nodes}'''
        js += [f"tl.fromTo('#pr-c', {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:0.35, ease:'power3.out'}}, {fq(st + 0.1)});",
               f"tl.fromTo('#pr-h', {{opacity:0, y:50}}, {{opacity:1, y:0, duration:0.45, ease:'power3.out'}}, {fq(t1 - LEAD)});",
               f"tl.fromTo('#pr-h2', {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.4, ease:'power3.out'}}, {fq(t2 - LEAD)});",
               f"tl.fromTo('#pr-rail', {{strokeDashoffset:760}}, {{strokeDashoffset:0, duration:{round(t3 - t2 + 0.6, 2)}, ease:'power2.inOut'}}, {fq(t2)});"]
        for i, tt in enumerate((t2 - 0.05, t2 + 0.55, t3)):
            js.append(f"tl.fromTo('#pn{i}', {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:0.4, ease:'power3.out'}}, {fq(tt)});")
            sfx(tt, "click", -6)
        return h, js
    if key == "pendam":
        t1, t2, t3 = T("pendam perasaan"), T("memperburukkan"), T("keadaan", after=T("memperburukkan"))
        h = f'''<div class="mg-bg char"></div><div class="glow g3"></div>
        <div class="mg-chip" id="pd-c">08 / 10 · Realiti</div>
        <div class="mg-h" id="pd-h">Pendam <span class="gold">perasaan</span></div>
        <div class="vessel"><div class="fill" id="pd-f"></div><div class="vlabel" id="pd-l">tekanan</div></div>
        <div class="mg-h3" id="pd-w">memperburukkan<br/><span class="red">keadaan</span></div>'''
        js += [f"tl.fromTo('#pd-c', {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:0.35, ease:'power3.out'}}, {fq(st + 0.1)});",
               f"tl.fromTo('#pd-h', {{opacity:0, y:50}}, {{opacity:1, y:0, duration:0.45, ease:'power3.out'}}, {fq(t1 - LEAD)});",
               f"tl.fromTo('#pd-f', {{scaleY:0.08}}, {{scaleY:0.92, duration:{round(t3 - t1, 2)}, ease:'power2.in'}}, {fq(t1)});",
               f"tl.fromTo('#pd-l', {{opacity:0}}, {{opacity:1, duration:0.3, ease:'power2.out'}}, {fq(t1 + 0.4)});",
               f"tl.fromTo('#pd-w', {{opacity:0, scale:1.4}}, {{opacity:1, scale:1, duration:0.3, ease:'power4.out'}}, {fq(t2 - LEAD)});",
               f"tl.fromTo('.vessel', {{x:0}}, {{x:6, duration:0.06, repeat:5, yoyo:true, ease:'power1.inOut'}}, {fq(t3)});"]
        sfx(t1 - 0.4, "riser", -8)
        sfx(t2 - LEAD, "impact", -6)
        return h, js
    if key == "quote":
        q0, q1 = T("saya ada di sini"), T("perlukan saya", after=T("saya ada di sini"), end=True)
        qw = [w for w in WORDS if q0 - 0.01 <= w["start"] and w["end"] <= q1 + 0.01]
        spans = "".join(f'<span class="qw" id="qq{k}">{html.escape(w["text"].capitalize() if k == 0 else w["text"])}</span> '
                        for k, w in enumerate(qw))
        h = f'''<div class="mg-bg warm"></div><div class="glow g4"></div>
        <div class="mg-chip" id="qt-c">Kesimpulan</div>
        <div class="qmark">&ldquo;</div>
        <div class="qtext">{spans.strip()}.&rdquo;</div>
        <div class="qsub" id="qt-s">Cukuplah sekadar itu.</div>'''
        js.append(f"tl.fromTo('#qt-c', {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:0.35, ease:'power3.out'}}, {fq(st + 0.05)});")
        js.append(f"tl.fromTo('#f-quote .qmark', {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.5, ease:'power3.out'}}, {fq(st + 0.1)});")
        for k, w in enumerate(qw):
            js.append(f"tl.fromTo('#qq{k}', {{opacity:0.12, y:14}}, {{opacity:1, y:0, duration:0.22, ease:'power2.out'}}, {fq(w['start'] - 0.04)});")
        js.append(f"tl.set('#qt-s', {{opacity:0}}, {fq(st)});")
        return h.replace('<div class="qsub" id="qt-s">Cukuplah sekadar itu.</div>', ""), js
    if key == "endcard":
        h = f'''<video class="clip fsv" id="end-v" src="broll/b_words_slow.mp4" muted playsinline data-start="{st}"
              data-duration="{round(en - st, 3)}" data-track-index="6"></video>
        <div class="endshade"></div>
        <div class="end-l1" id="en-1">Kata-Kata Kita</div>
        <div class="end-l2" id="en-2">Ada <span class="gold">Kesan.</span></div>
        <div class="end-rule" id="en-r"></div>
        <div class="end-brand" id="en-b">Dr Azren <span class="bar">|</span> Spread Positivity</div>
        <div class="ai-tag">Ilustrasi AI</div>'''
        js += [f"tl.fromTo('#en-1', {{opacity:0, y:40, scaleX:1.25, filter:'blur(10px)'}}, {{opacity:1, y:0, scaleX:1, filter:'blur(0px)', duration:0.7, ease:'power3.out'}}, {fq(st + 0.2)});",
               f"tl.fromTo('#en-2', {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.6, ease:'power3.out'}}, {fq(st + 0.6)});",
               f"tl.fromTo('#en-r', {{scaleX:0}}, {{scaleX:1, duration:0.6, ease:'power3.inOut'}}, {fq(st + 1.2)});",
               f"tl.fromTo('#en-b', {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.5, ease:'power3.out'}}, {fq(st + 1.4)});",
               f"tl.to('#f-end-in', {{opacity:0, duration:0.45, ease:'power2.in'}}, {fq(DUR - 0.5)});"]
        sfx(st + 0.6, "swell", -6)
        sfx(st + 1.4, "pop", -10)
        return h, js
    raise KeyError(key)


# ---------------------------------------------------------------- build
def build():
    body, js = [], []
    # 1 background + speaker punch-ins (background moves a quarter as much: parallax)
    body.append('<div id="bgwrap"><img id="bg" src="studio_soft.jpg"/><div id="bgwarm"></div></div>')
    body.append('<div id="hero"><div id="h10">10 AYAT</div></div>')
    body.append('<div id="nums">' + "".join(f'<div class="bignum" id="bn-{s["n"]}">{s["n"]:02d}</div>' for s in STMT) + '</div>')
    body.append(f'<div id="spk"><video id="spkv" class="clip" src="speaker.webm" muted playsinline data-start="0" '
                f'data-duration="{DUR}" data-track-index="1"></video><div id="spkshade"></div></div>')

    # punch levels: the hook opens on the close-up; a punch never pushes the head into a visible card
    cards_on = [(s["t_q0"] - 0.3, s["t_end"]) for s in STMT] + [(B["end_open"] - 0.2, B["endcard"])]
    for k, (t0, p) in enumerate(CUTS):
        t1 = CUTS[k + 1][0] if k + 1 < len(CUTS) else DUR
        if k == 0:
            p = 1.30
        elif any(a < t1 and b > t0 for a, b in cards_on):
            p = min(p, 1.15)
        js.append(f"tl.set('#spk', {{scale:{p}}}, {fq(t0)});")
        js.append(f"tl.set('#bgwrap', {{scale:{round(1.02 + (p - 1) * 0.25, 4)}}}, {fq(t0)});")
        if k:
            sfx(t0, "tick", -22)          # barely-there air on each jump cut

    # 2 hook: "10 AYAT" slams in behind the head, then the front line + subline
    t_s, t_a = T("sepuluh"), T("ayat")
    js += [f"tl.fromTo('#h10', {{opacity:0, scale:1.8, y:-40}}, {{opacity:1, scale:1, y:0, duration:0.38, ease:'power4.out'}}, {fq(max(0.0, t_s - 0.05))});",
           f"tl.to('#h10', {{opacity:0, y:-60, duration:0.35, ease:'power2.in'}}, {fq(STMT[0]['t_open'] - 0.3)});"]
    sfx(max(0.0, t_s - 0.05), "impact", -3)
    body.append('''<div id="hookfront"><div id="hk1">JANGAN <span class="red">SESEKALI</span> CAKAP!</div>
      <div id="hk2">Kepada Orang Yang Ada Masalah Mental</div></div>''')
    t_hk1, t_hk2 = T("tak patut kita cakap") - 0.1, T("pada orang yang") - 0.1
    js += [f"tl.fromTo('#hk1', {{opacity:0, scale:1.5}}, {{opacity:1, scale:1, duration:0.28, ease:'power4.out'}}, {fq(t_hk1)});",
           f"tl.fromTo('#hk2', {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.4, ease:'power3.out'}}, {fq(t_hk2)});",
           f"tl.to('#hookfront', {{opacity:0, y:-40, duration:0.3, ease:'power2.in'}}, {fq(STMT[0]['t_open'] - 0.25)});"]
    sfx(t_hk1, "whoosh", -6)
    sfx(t_hk2, "pop", -12)

    # 3 statements
    for s in STMT:
        n, kind = s["n"], ENTER[s["n"] - 1]
        # big numeral behind the head from "Yang ke-N" to the quote, then it hands over to the chip
        js.append(f"tl.fromTo('#bn-{n}', {{opacity:0, scale:1.5}}, {{opacity:1, scale:1, duration:0.3, ease:'power4.out'}}, {fq(s['t_open'] - 0.05)});")
        js.append(f"tl.to('#bn-{n}', {{opacity:0, scale:0.7, y:-120, duration:0.35, ease:'power3.in'}}, {fq(max(s['t_q0'], s['t_open'] + 0.5) - 0.1)});")
        sfx(s["t_open"] - 0.05, "impact" if n in (5, 10) else "boom", -8)
        # a display word may join spoken tokens ("baik+lah" -> "baiklah"); it lands on the first one
        disp = s["quote"].split()
        words = "".join(f'<span class="qw" id="q{n}w{k}">{html.escape(t.replace("+", ""))}</span> '
                        for k, t in enumerate(disp))
        sup = "".join(f'<div class="sup" id="s{n}-{k}">{h}</div>' for k, (_, h) in enumerate(s["sup"]))
        body.append(f'''<div class="card" id="cd{n}"><div class="chip" id="ch{n}"><b>{n:02d}</b> / 10</div>
          <div class="quote" id="qt{n}"><span class="qin">{words.strip()}</span><span class="strk" id="sk{n}"></span></div>
          <div class="sups" id="sp{n}">{sup}</div></div>''')
        q0 = fq(s["t_q0"] - 0.25)
        js.append(f"tl.set('#cd{n}', {{opacity:1}}, {q0});")
        js.append(f"tl.fromTo('#ch{n}', {{opacity:0, y:-24}}, {{opacity:1, y:0, duration:0.3, ease:'power3.out'}}, {q0});")
        js.append(f"tl.fromTo('#qt{n}', {{opacity:0}}, {{opacity:1, duration:0.2, ease:'power2.out'}}, {q0});")
        sfx(q0, "whoosh", -9)
        if sum(t.count("+") + 1 for t in disp) != len(s["qwords"]):
            raise ValueError(f"S{n}: quote covers {sum(t.count('+') + 1 for t in disp)} tokens, phrase has {len(s['qwords'])}")
        j = 0
        for k, t in enumerate(disp):
            js.append(word_anim(kind, f"#q{n}w{k}", fq(s["qwords"][j]["start"] - 0.06), k))
            j += t.count("+") + 1
        # the strike: red line through, text desaturates, a soft impact
        ts = fq(s["t_strike"] - 0.05)
        js.append(f"tl.fromTo('#sk{n}', {{scaleX:0}}, {{scaleX:1, duration:0.35, ease:'power3.inOut'}}, {ts});")
        js.append(f"tl.to('#qt{n} .qin', {{color:'rgba(255,245,228,.55)', duration:0.3, ease:'power2.out'}}, {ts});")
        sfx(ts, "strike", -6)
        if s["sup"]:
            first = fq(s["sup"][0][0] - LEAD)
            qout = fq(max(first - 0.25, ts + 0.6))
            js.append(f"tl.to('#qt{n}', {{opacity:0, y:-30, scale:0.92, duration:0.3, ease:'power2.in'}}, {qout});")
            for k, (t, _) in enumerate(s["sup"]):
                tt = fq(max(t - LEAD, qout + 0.3 + 0.1 * k))   # never on top of the leaving quote
                js.append(f"tl.fromTo('#s{n}-{k}', {{opacity:0, y:40, rotationX:-50}}, {{opacity:1, y:0, rotationX:0, duration:0.45, ease:'power3.out'}}, {tt});")
                sfx(tt, "pop", -10)
        js.append(f"tl.to('#cd{n}', {{opacity:0, y:-20, duration:0.25, ease:'power2.in'}}, {fq(s['t_end'] - 0.25)});")
        js.append(f"tl.set('#cd{n}', {{opacity:0}}, {fq(s['t_end'])});")

    # 4 conclusion + CTA cards
    t_ke, t_kal = B["end_open"], T("kalau kita tak tahu")
    body.append(f'''<div class="card" id="cdK"><div class="chip gold">Kesimpulan</div>
      <div class="sup big" id="kK1">Kalau tak tahu nak cakap <em>apa</em>…</div></div>''')
    js += [f"tl.set('#cdK', {{opacity:1}}, {fq(t_ke - 0.15)});",
           f"tl.fromTo('#cdK .chip', {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.35, ease:'back.out(2)'}}, {fq(t_ke - 0.15)});",
           f"tl.fromTo('#kK1', {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.4, ease:'power3.out'}}, {fq(t_kal - LEAD)});",
           f"tl.set('#cdK', {{opacity:0}}, {fq(B['quote_mg'] - 0.2)});"]
    sfx(t_ke - 0.15, "swell", -10)
    body.append('''<div class="card" id="cdC"><div class="chip">Ada soalan?</div>
      <div class="sup big" id="kC1">Tanya dalam <em>komen</em> &#8595;</div></div>''')
    js += [f"tl.set('#cdC', {{opacity:1}}, {fq(B['cta'] - 0.15)});",
           f"tl.fromTo('#cdC .chip', {{opacity:0, y:-20}}, {{opacity:1, y:0, duration:0.3, ease:'power3.out'}}, {fq(B['cta'] - 0.15)});",
           f"tl.fromTo('#kC1', {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.35, ease:'power3.out'}}, {fq(T('boleh tanya') - LEAD)});",
           f"tl.to('#cdC', {{opacity:0, duration:0.25, ease:'power2.in'}}, {fq(B['endcard'] - 0.1)});"]
    sfx(B["cta"] - 0.15, "pop", -10)

    # 5 full-screen inserts (alternate entrances: zoom-through, wipe up, iris)
    for z, (fid, kind, st, en, src, label) in enumerate(FS):
        entry = ["zoom", "wipe", "iris"][z % 3]
        if kind == "broll":
            lab = f'<div class="fs-label" id="{fid}-l">{label}</div>' if label else ""
            body.append(f'<div class="fs" id="{fid}" style="z-index:{30 + z}"><div class="fs-in" id="{fid}-in">'
                        f'<video class="clip fsv" id="{fid}-v" src="broll/{src}.mp4" muted playsinline data-start="{st}" '
                        f'data-duration="{round(min(en - st, 5.0), 3)}" data-track-index="{4 + z % 2}"></video>'
                        f'<div class="fs-shade"></div>{lab}<div class="ai-tag">Ilustrasi AI</div></div></div>')
            js.append(f"tl.fromTo('#{fid}-v', {{scale:1.0}}, {{scale:1.08, duration:{round(en - st, 3)}, ease:'sine.inOut'}}, {st});")
            if label:
                js.append(f"tl.fromTo('#{fid}-l', {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.4, ease:'power3.out'}}, {fq(st + 0.35)});")
        else:
            hb, mjs = mg_body(src, st, en)
            body.append(f'<div class="fs" id="{fid}" style="z-index:{30 + z}"><div class="fs-in" id="{fid}-in">{hb}</div></div>')
            js += mjs
        js.append(f"tl.set('#{fid}', {{opacity:1}}, {st});")
        if entry == "zoom":
            js.append(f"tl.fromTo('#{fid}-in', {{opacity:0, scale:1.25, filter:'blur(18px)'}}, {{opacity:1, scale:1, filter:'blur(0px)', duration:0.4, ease:'power4.out'}}, {st});")
        elif entry == "wipe":
            js.append(f"tl.fromTo('#{fid}-in', {{clipPath:'inset(100% 0% 0% 0%)'}}, {{clipPath:'inset(0% 0% 0% 0%)', duration:0.42, ease:'power3.inOut'}}, {st});")
        else:
            js.append(f"tl.fromTo('#{fid}-in', {{clipPath:'circle(0% at 50% 40%)'}}, {{clipPath:'circle(150% at 50% 40%)', duration:0.5, ease:'power3.inOut'}}, {st});")
            js.append(f"tl.set('#{fid}-in', {{clipPath:'none'}}, {fq(st + 0.5)});")
        sfx(st, "whoosh" if entry != "iris" else "swell", -7)
        if fid != "f-end":
            js.append(f"tl.to('#{fid}-in', {{opacity:0, scale:0.96, duration:0.25, ease:'power2.in'}}, {fq(en - 0.25)});")
            js.append(f"tl.set('#{fid}', {{opacity:0}}, {en});")
            sfx(en - 0.25, "air", -14)

    # 6 captions (ivory, active word gold)
    caps = cap_groups()
    for n, (t0, t1, ws) in enumerate(caps):
        spans = "".join(f'<span class="cw" id="c{n}w{k}">{w["text"]}</span> ' for k, w in enumerate(ws))
        body.append(f'<div class="cap" id="c{n}"><div class="capin">{spans.strip()}</div></div>')
        js.append(f"tl.fromTo('#c{n}', {{opacity:0, y:16}}, {{opacity:1, y:0, duration:0.14, ease:'power3.out'}}, {t0});")
        js.append(f"tl.set('#c{n}', {{opacity:0}}, {t1});")
        for k, w in enumerate(ws):
            js.append(f"tl.set('#c{n}w{k}', {{color:'{GOLD}'}}, {fq(max(t0, w['start'] - 0.02))});")
            js.append(f"tl.set('#c{n}w{k}', {{color:'{IVORY}'}}, {fq(w['end'] + 0.04)});")
    return body, js, len(caps)


CSS = f"""
@font-face{{font-family:"PJS";src:url("fonts/PlusJakartaSans-800.woff2") format("woff2");font-weight:200 800;font-display:block}}
@font-face{{font-family:"Anton";src:url("fonts/Anton-400.woff2") format("woff2");font-weight:400;font-display:block}}
@font-face{{font-family:"Playfair";src:url("fonts/PlayfairDisplay-600i.woff2") format("woff2");font-weight:600;font-style:italic;font-display:block}}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; padding:0; width:{W}px; height:{H}px; overflow:hidden; background:{NAVY}; font-family:"PJS", sans-serif; }}
#stage {{ position:relative; width:{W}px; height:{H}px; overflow:hidden; background:{NAVY}; }}
#bgwrap {{ position:absolute; inset:0; z-index:1; transform-origin:{FOCUS[0]}px {FOCUS[1]}px; }}
#bg {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
#bgwarm {{ position:absolute; inset:0; background:radial-gradient(90% 60% at 50% 38%, rgba(255,190,110,.10) 0%, rgba(14,26,43,0) 55%),
  linear-gradient(180deg, rgba(14,26,43,.30) 0%, rgba(14,26,43,0) 22%, rgba(14,26,43,0) 70%, rgba(14,26,43,.45) 100%); }}
#hero {{ position:absolute; inset:0; z-index:2; pointer-events:none; }}
#h10 {{ position:absolute; left:0; right:0; top:120px; text-align:center; font-family:"Anton"; font-size:330px; line-height:1;
  color:{GOLD}; letter-spacing:.01em; opacity:0;
  text-shadow:0 3px 0 #C99633, 0 6px 0 #A87A26, 0 10px 0 #8A6320, 0 28px 60px rgba(0,0,0,.55); }}
#nums {{ position:absolute; inset:0; z-index:2; pointer-events:none; }}
.bignum {{ position:absolute; left:0; right:0; top:60px; text-align:center; font-family:"Anton"; font-size:420px; line-height:1; opacity:0;
  color:rgba(233,180,76,.92); text-shadow:0 4px 0 #B88A30, 0 9px 0 #8A6320, 0 30px 70px rgba(0,0,0,.5); }}
#spk {{ position:absolute; inset:0; z-index:3; transform-origin:{FOCUS[0]}px {FOCUS[1]}px; }}
#spkv {{ position:absolute; left:0; top:0; width:{W}px; height:{H}px; filter:drop-shadow(0 24px 40px rgba(0,0,0,.45)); }}
#spkshade {{ position:absolute; left:0; right:0; bottom:0; height:520px; background:linear-gradient(180deg, rgba(14,26,43,0), rgba(14,26,43,.38)); }}
#hookfront {{ position:absolute; left:50px; right:50px; top:1250px; z-index:6; text-align:center; pointer-events:none; }}
#hk1 {{ font-family:"Anton"; font-size:104px; line-height:1; color:{IVORY}; letter-spacing:.01em; opacity:0;
  text-shadow:0 4px 0 rgba(0,0,0,.35), 0 14px 34px rgba(0,0,0,.6); }}
#hk2 {{ margin-top:22px; display:inline-block; font-weight:800; font-size:40px; color:{NAVY}; background:{GOLD}; padding:12px 26px 11px; border-radius:14px; opacity:0; }}
.red {{ color:{RED}; }} .gold {{ color:{GOLD}; }}
.card {{ position:absolute; left:56px; right:56px; top:96px; z-index:5; opacity:0; pointer-events:none; perspective:900px; }}
.chip {{ display:inline-block; font-weight:800; font-size:34px; letter-spacing:.08em; color:{IVORY}; background:rgba(14,26,43,.78);
  border:2px solid rgba(233,180,76,.75); padding:10px 22px 9px; border-radius:999px; }}
.chip b {{ color:{GOLD}; }}
.chip.gold {{ background:{GOLD}; color:{NAVY}; border-color:{GOLD}; }}
.quote {{ position:relative; margin-top:18px; padding:26px 32px 30px; border-radius:30px; background:rgba(14,26,43,.66);
  backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px); border:2px solid rgba(229,72,77,.55);
  box-shadow:0 24px 60px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.12); }}
.qin {{ display:block; font-weight:800; font-size:72px; line-height:1.12; letter-spacing:-.015em; color:{IVORY}; transform-style:preserve-3d; }}
.qin .qw {{ display:inline-block; }}
.quote::before {{ content:"✕"; position:absolute; right:22px; top:-26px; width:56px; height:56px; border-radius:50%; background:{RED};
  color:#fff; font-size:30px; font-weight:800; display:flex; align-items:center; justify-content:center; }}
.strk {{ position:absolute; left:26px; right:26px; top:50%; height:9px; margin-top:-4px; background:{RED}; border-radius:6px;
  transform:scaleX(0) rotate(-2deg); transform-origin:left center; box-shadow:0 0 18px rgba(229,72,77,.6); }}
.sups {{ position:absolute; left:0; right:0; top:84px; perspective:900px; }}
.sup {{ font-weight:800; font-size:64px; line-height:1.08; letter-spacing:-.02em; color:{IVORY}; opacity:0; margin-top:10px;
  text-shadow:0 3px 0 rgba(0,0,0,.25), 0 12px 30px rgba(0,0,0,.55); transform-origin:50% 100%; }}
.sup em, .sup.big em {{ font-style:normal; color:{GOLD}; text-shadow:0 3px 0 #8A6320, 0 12px 30px rgba(0,0,0,.55); }}
.sup.big {{ font-size:66px; margin-top:20px; }}
.fs {{ position:absolute; inset:0; opacity:0; pointer-events:none; }}
.fs-in {{ position:absolute; inset:0; overflow:hidden; }}
.fsv {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
.fs-shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(14,26,43,.45) 0%, rgba(14,26,43,0) 26%, rgba(14,26,43,0) 60%, rgba(14,26,43,.55) 100%); }}
.fs-label {{ position:absolute; left:56px; right:56px; top:150px; font-weight:800; font-size:64px; line-height:1.08; color:{IVORY};
  letter-spacing:-.02em; text-shadow:0 4px 0 rgba(0,0,0,.3), 0 14px 34px rgba(0,0,0,.7); opacity:0; }}
.ai-tag {{ position:absolute; left:56px; top:84px; font:700 22px "PJS"; letter-spacing:.1em; text-transform:uppercase; color:rgba(255,245,228,.9);
  background:rgba(14,26,43,.5); padding:7px 14px 6px; border-radius:8px; }}
.mg-bg {{ position:absolute; inset:0; }}
.mg-bg.navy {{ background:radial-gradient(110% 80% at 30% 15%, #1C3352 0%, {NAVY} 55%, #070D16 100%); }}
.mg-bg.char {{ background:radial-gradient(110% 80% at 70% 20%, #2A2B31 0%, {CHAR} 60%, #0B0B0D 100%); }}
.mg-bg.warm {{ background:radial-gradient(110% 80% at 50% 30%, #3B2A16 0%, #1B1612 55%, #0C0A08 100%); }}
.glow {{ position:absolute; border-radius:50%; }}
.glow.g1 {{ width:1100px; height:1100px; left:-10px; top:420px; background:radial-gradient(circle, rgba(233,180,76,.20), rgba(233,180,76,0) 62%); }}
.glow.g2 {{ width:1000px; height:1000px; left:200px; top:700px; background:radial-gradient(circle, rgba(127,163,107,.22), rgba(127,163,107,0) 62%); }}
.glow.g3 {{ width:1100px; height:1100px; left:-10px; top:600px; background:radial-gradient(circle, rgba(229,72,77,.16), rgba(229,72,77,0) 62%); }}
.glow.g4 {{ width:1200px; height:1200px; left:-60px; top:300px; background:radial-gradient(circle, rgba(233,180,76,.24), rgba(233,180,76,0) 60%); }}
.mg-chip {{ position:absolute; left:70px; top:150px; font-weight:800; font-size:34px; letter-spacing:.08em; color:{NAVY}; background:{GOLD};
  padding:10px 22px 9px; border-radius:999px; }}
.mg-h {{ position:absolute; left:70px; right:60px; top:240px; font-family:"Anton"; font-size:150px; line-height:1; color:{IVORY};
  text-shadow:0 4px 0 rgba(0,0,0,.3), 0 18px 40px rgba(0,0,0,.5); }}
.mg-h2 {{ position:absolute; left:74px; right:60px; top:410px; font-weight:800; font-size:70px; color:rgba(255,245,228,.82); }}
.mg-h3 {{ position:absolute; left:70px; right:60px; top:1350px; font-family:"Anton"; font-size:120px; line-height:1; color:{IVORY}; text-align:right; }}
.net {{ position:absolute; inset:0; width:{W}px; height:{H}px; }}
.nl {{ stroke:rgba(233,180,76,.55); stroke-width:4; stroke-dasharray:400; }}
.nd {{ fill:{GOLD}; filter:drop-shadow(0 0 14px rgba(233,180,76,.9)); }}
.sp {{ fill:#FFF0C8; filter:drop-shadow(0 0 12px #fff); opacity:0; }}
.prail {{ position:absolute; left:120px; top:780px; width:40px; height:760px; overflow:visible; }}
.prail path {{ stroke:{GREEN}; stroke-width:10; stroke-linecap:round; fill:none; stroke-dasharray:760; }}
.pnode {{ position:absolute; left:92px; display:flex; align-items:center; gap:34px; opacity:0; }}
.pdot {{ width:96px; height:96px; border-radius:50%; background:{NAVY}; border:8px solid {GREEN}; color:{IVORY}; font-family:"Anton"; font-size:50px;
  display:flex; align-items:center; justify-content:center; }}
.plab {{ display:flex; flex-direction:column; background:rgba(255,245,228,.95); color:{NAVY}; padding:16px 30px 18px; border-radius:24px; }}
.plab b {{ font-size:58px; line-height:1.05; }} .plab small {{ font-size:34px; font-weight:700; color:#5B6573; }}
.vessel {{ position:absolute; left:340px; top:560px; width:400px; height:720px; border:10px solid rgba(255,245,228,.85); border-radius:60px 60px 80px 80px; overflow:hidden; }}
.fill {{ position:absolute; left:0; right:0; bottom:0; height:100%; transform-origin:50% 100%;
  background:linear-gradient(0deg, {RED} 0%, #F07A4A 55%, {GOLD} 100%); opacity:.9; }}
.vlabel {{ position:absolute; left:0; right:0; bottom:40px; text-align:center; font-weight:800; font-size:44px; color:#fff; letter-spacing:.12em; text-transform:uppercase; opacity:0; }}
.qmark {{ position:absolute; left:60px; top:330px; font-family:"Playfair"; font-style:italic; font-size:420px; line-height:1; color:{GOLD}; opacity:0; }}
.qtext {{ position:absolute; left:80px; right:80px; top:640px; font-family:"Playfair"; font-style:italic; font-weight:600; font-size:96px; line-height:1.14; color:{IVORY}; }}
.qtext .qw {{ display:inline-block; }}
.endshade {{ position:absolute; inset:0; background:radial-gradient(90% 70% at 50% 45%, rgba(14,26,43,.55), rgba(7,13,22,.92)); }}
.end-l1 {{ position:absolute; left:0; right:0; top:700px; text-align:center; font-family:"Anton"; font-size:120px; line-height:1; color:{IVORY}; opacity:0; }}
.end-l2 {{ position:absolute; left:0; right:0; top:840px; text-align:center; font-family:"Anton"; font-size:150px; line-height:1; color:{IVORY}; opacity:0;
  text-shadow:0 4px 0 rgba(0,0,0,.3), 0 18px 40px rgba(0,0,0,.6); }}
.end-rule {{ position:absolute; left:390px; width:300px; top:1040px; height:6px; border-radius:3px; background:{GOLD}; transform:scaleX(0); }}
.end-brand {{ position:absolute; left:0; right:0; top:1090px; text-align:center; font-weight:800; font-size:48px; color:{IVORY}; letter-spacing:.02em; opacity:0; }}
.end-brand .bar {{ color:{GOLD}; padding:0 10px; }}
.cap {{ position:absolute; left:64px; width:850px; bottom:430px; z-index:100; text-align:center; opacity:0; pointer-events:none; }}
.capin {{ display:inline-block; text-wrap:balance; font-weight:800; font-size:62px; line-height:1.14; letter-spacing:-.01em; color:{IVORY};
  -webkit-text-stroke:3px rgba(14,26,43,.55); paint-order:stroke fill;
  text-shadow:0 4px 0 rgba(0,0,0,.30), 0 10px 28px rgba(0,0,0,.65); }}
.capin i {{ font-style:italic; }}
"""


def main():
    body, js, ncap = build()
    page = f"""<!doctype html>
<html lang="ms"><head><meta charset="utf-8" />
<style>{CSS}</style></head>
<body>
<div id="stage" data-composition-id="ayat10" data-start="0" data-duration="{DUR}" data-fps="{FPS}" data-width="{W}" data-height="{H}">
  {chr(10).join(body)}
  <script src="vendor/gsap.min.js"></script>
  <script>
  (function () {{
    const tl = window.gsap.timeline({{ paused: true }});
    {(chr(10) + '    ').join(js)}
    window.__timelines = window.__timelines || {{}};
    window.__timelines["ayat10"] = tl;
  }})();
  </script>
</div>
</body></html>
"""
    (P / "index.html").write_text(page)
    (G / "sfx_cues.json").write_text(json.dumps(sorted(SFX, key=lambda c: c["t"]), indent=1))
    print(f"DUR {DUR}s · {len(STMT)} statements · {len(FS)} inserts · {ncap} caption groups · {len(SFX)} sfx cues · {len(js)} timeline statements")
    for s in STMT:
        print(f"  S{s['n']:02d} open {s['t_open']:6.2f} quote {s['t_q0']:6.2f}-{s['t_q1']:6.2f} strike {s['t_strike']:6.2f} end {s['t_end']:6.2f}")
    for f in FS:
        print(f"  {f[0]:9s} {f[1]:5s} {f[2]:7.2f}-{f[3]:7.2f} ({f[3] - f[2]:.2f}s)")


if __name__ == "__main__":
    main()
