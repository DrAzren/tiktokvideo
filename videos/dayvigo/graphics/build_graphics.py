"""Generate the HyperFrames composition for 'Ubat Psikiatri Dayvigo' (education only, no promo).

One composition over the cut talking head (edit/cut.mp4 → public/input-video.mp4), picture only
(audio is mixed separately in audio/). Layers, bottom → top:
  video → hero word (z5, matted behind the subject in assemble.sh) → paper cards in the headroom
  (z10) → full-screen inserts: AI B-roll video + paper motion graphics (z20+) → captions (z100)

Every time is anchored to a spoken word in edit/cut_words.json (exact cut-timeline times mapped
through the EDL), so the whole build re-times itself when the cut changes.

Layout (1080x1920, face measured on the source): head top ≈ y420 (y400 at the 1.1 punch-in),
chin ≈ y1245 → cards live in the headroom y150-410; captions run one line in y1290-1420, below
the chin and above TikTok's bottom UI (bottom 20%), centred in x140-940 (clear of the right 15%).

Motion (motion-doctrine): one current, LEFT. Everything enters from the right mid-flight
(power4.out) and leaves to the left (power4.in); paper scenes enter with a torn-paper pull.
No idle loops: B-roll carries its own camera move plus a slow push; MG scenes are staged reveals,
each element landing on its word (LEAD before the word onset). Stillness before the hero.

Outputs: public/index.html, sfx_cues.json (every animation's sound, same clock), plan.md
(timecoded motion-graphics + sound-design plan), storyboard.json.
"""

import html
import json
import random
import subprocess
from pathlib import Path

W = Path(__file__).parent
PUB = W / "public"
EDIT = W.parent / "edit"
FPS = 30
_nb = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                               "stream=nb_read_packets", "-of", "csv=p=0", str(EDIT / "cut.mp4")], text=True)
DUR = round(int(_nb.strip()) / FPS, 4)
# the aligner leaves a zero-length "ke" where "pengsan ke apa" was cut: not in the audio
WORDS = [w for w in json.loads((EDIT / "cut_words.json").read_text())
         if not (w["text"] == "ke" and w["end"] - w["start"] < 0.04)]
LEAD = 0.12

NAVY, TEAL, CREAM, ORANGE, WHITE = "#101C2C", "#18A9A2", "#F5F0E8", "#F5AA55", "#FFFFFF"
DEEP_TEAL, MARKER, MUTED, PAPER2 = "#0D6B67", "#E8643A", "#5E6B78", "#FBE7C6"


def T(phrase: str, after: float = 0.0, end: bool = False) -> float:
    """Start (or end) of the first occurrence of `phrase` at/after `after` on the cut timeline."""
    toks = phrase.split()
    for i in range(len(WORDS) - len(toks) + 1):
        if WORDS[i]["start"] >= after - 1e-6 and [w["text"] for w in WORDS[i:i + len(toks)]] == toks:
            return WORDS[i + len(toks) - 1]["end"] if end else WORDS[i]["start"]
    raise KeyError(phrase)


def fq(t: float) -> float:
    return round(round(t * FPS) / FPS, 4)


SFX: list[dict] = []
PLAN: list[tuple[float, str, str]] = []


def sfx(kind: str, t: float, gain: float = 0.0, dur: float | None = None) -> None:
    c = {"t": round(max(0.0, t), 3), "kind": kind, "gain": gain}
    if dur:
        c["dur"] = round(dur, 3)
    SFX.append(c)


def plan(t: float, what: str, sound: str = "") -> None:
    PLAN.append((round(t, 2), what, sound))


# ---------------------------------------------------------------- shared visual bits
def noise_bg(opacity: float = 0.09, seed: int = 3) -> str:
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'>"
           f"<feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' seed='{seed}'/>"
           f"<feColorMatrix values='0 0 0 0 .25  0 0 0 0 .2  0 0 0 0 .15  0 0 0 {opacity} 0'/></filter>"
           f"<rect width='300' height='300' filter='url(%23n)'/></svg>")
    return 'url("data:image/svg+xml;utf8,' + svg.replace('"', "'") + '")'


def torn(seed: int, edge: str = "bottom", amp: int = 9, n: int = 34) -> str:
    """clip-path polygon with one torn edge (deterministic)."""
    r = random.Random(seed)
    pts = [(i / n * 100, r.uniform(0, amp)) for i in range(n + 1)]
    if edge == "bottom":
        body = ["0% 0%", "100% 0%"] + [f"{x:.2f}% calc(100% - {y:.1f}px)" for x, y in reversed(pts)]
    elif edge == "left":
        body = ["100% 0%", "100% 100%"] + [f"{y:.1f}px {x:.2f}%" for x, y in reversed(pts)]
    else:  # right
        body = ["0% 0%"] + [f"calc(100% - {y:.1f}px) {x:.2f}%" for x, y in pts] + ["0% 100%"]
    return "polygon(" + ", ".join(body) + ")"


ICONS = {
    "check": '<path d="M9 25l9 9L39 13"/>',
    "cross": '<path d="M12 12l24 24M36 12L12 36"/>',
    "warn": '<path d="M24 6L44 41H4z"/><path d="M24 19v10M24 35v.5"/>',
    "moon": '<path d="M33 30A15 15 0 0 1 18 9a15 15 0 1 0 15 21z"/>',
    "dot": '<circle cx="24" cy="24" r="5" fill="currentColor"/>',
    "glass": '<path d="M14 6h20l-2 16a8 8 0 0 1-16 0zM24 30v11M17 42h14"/>',
    "doc": '<path d="M12 5h17l8 8v30H12z"/><path d="M18 22h13M18 29h13M18 36h8"/>',
    "arrow": '<path d="M24 6v34M12 29l12 12 12-12"/>',
}


def icon(name: str, cls: str = "ico", color: str = "currentColor") -> str:
    return (f'<svg viewBox="0 0 48 48" class="{cls}"><g stroke="{color}" stroke-width="4.2" stroke-linecap="round" '
            f'stroke-linejoin="round" fill="none">{ICONS[name]}</g></svg>')


def esc(s: str) -> str:
    return html.escape(s)


# ================================================================== CARDS (headroom)
# element: (key, html, t_abs, anim) — anim: in | pop | fade | hl | draw | stamp | none
# pages:   [(t_in, [elements])]; a new page pushes the old one out to the LEFT (the current)
def chip(text, color=TEAL, ico=None):
    i = icon(ico, "chip-ico", "#fff") if ico else ""
    return f'<span class="chip" style="background:{color}">{i}{esc(text)}</span>'


def title(text, cls=""):
    return f'<div class="title {cls}">{text}</div>'


def row(ic, text, color=TEAL):
    return f'<div class="row"><span class="disc" style="background:{color}">{icon(ic, "dico", "#fff")}</span><span>{text}</span></div>'


def underline_svg(uid, width=520):
    return (f'<svg class="uline" viewBox="0 0 {width} 24" style="width:{width}px"><path id="{uid}" pathLength="1" '
            f'd="M4 16 C {width * .3:.0f} 7, {width * .62:.0f} 21, {width - 6} 11" /></svg>')


CARDS = []


def card(cid, start, end, pages, intent):
    CARDS.append({"id": cid, "start": fq(start), "end": fq(end), "pages": pages, "intent": intent})


# --- c01: "Pernah tak dengar ubat nama dia Dayvigo? Apa itu Dayvigo? ... ubat tidur generasi baru"
t_day = T("devigo")
card("c01-dayvigo", T("pernah tak dengar") - 0.25, T("dia bukan di") - 0.05, [
    (T("pernah tak dengar") - 0.25, [
        ("k", chip("Ubat psikiatri", TEAL, "moon"), T("pernah tak dengar") - 0.2, "pop"),
        ("t", title('Pernah dengar <span class="serif teal">Dayvigo</span>?'), t_day - 0.45, "in"),
        ("n", '<div class="hand">lemborexant · ubat preskripsi</div>', t_day + 0.35, "fade"),
    ]),
    (T("apa itu devigo") - 0.1, [
        ("k2", chip("Apa itu Dayvigo?", NAVY), T("apa itu devigo") - 0.05, "pop"),
        ("t2", title('Ubat tidur <span class="hl">generasi baru</span>'), T("ubat tidur generasi") - LEAD, "in"),
        (".c01-dayvigo-p1 .hl", None, T("generasi baru") + 0.05, "hl"),
    ]),
], "What Dayvigo is — a new-generation sleep medicine")
plan(T("devigo"), "Card: torn-paper strip 'Pernah dengar Dayvigo?' + handwritten 'lemborexant · ubat preskripsi'", "paper slide, chip pop")

# --- c02: "Ubat ni adalah daripada kumpulan orexin reseptor antagonis"
s = T("ubat ni adalah daripada")
card("c02-orexin", s - 0.2, T("bahasa senang") - 0.12, [
    (s - 0.2, [
        ("k", chip("Kumpulan ubat"), T("kumpulan") - 0.15, "pop"),
        ("w1", title('<span class="serif">Orexin</span>', "inl"), T("orexin") - LEAD, "in"),
        ("w2", title('<span class="serif">Receptor</span>', "inl"), T("reseptor") - LEAD, "in"),
        ("w3", title('<span class="serif teal">Antagonist</span>', "inl"), T("antagonis") - LEAD, "in"),
    ]),
], "Drug class, word by word")
plan(T("orexin"), "Card: 'Orexin / Receptor / Antagonist' lands word by word", "3 text ticks")

# --- c03: "Bahasa senang dia, ubat ni function dia untuk"
s = T("bahasa senang")
card("c03-senang", s - 0.1, T("dia untuk switch") + 0.05, [
    (s - 0.1, [("n", '<div class="hand big">Bahasa senang…</div>', s - 0.05, "in")]),
], "Plain-language setup for the switch metaphor")

# --- c04: kicker above the INSOMNIA hero: "Antara fungsi utama ... untuk rawat insomnia"
s = T("antara fungsi utama")
card("c04-fungsi", s - 0.1, T("untuk kes susah") + 0.05, [
    (s - 0.1, [
        ("k", chip("Fungsi utama"), T("fungsi utama") - 0.1, "pop"),
        ("t", title("Untuk merawat…", "sm"), T("rawat") - LEAD, "in"),
    ]),
], "Kicker for the hero word")

# --- c05: "Kelebihan Dayvigo ni tidur rasa lebih natural"
s = T("kelebihan")
card("c05-kelebihan", s - 0.15, T("kurang ketagihan") - 0.05, [
    (s - 0.15, [
        ("k", chip("Kelebihan", TEAL, "check"), s - 0.1, "pop"),
        ("r", row("check", "Tidur rasa lebih <b>natural</b>"), T("tidur rasa lebih") - LEAD, "in"),
    ]),
], "Benefit 1")

# --- c06: "Tapi setiap ubat pun ada kesan sampingan. Contohnya,"
s = T("tapi setiap ubat")
card("c06-kesan", s - 0.12, T("contohnya ubat ni") + 0.45, [
    (s - 0.12, [
        ("k", chip("Kesan sampingan", MARKER, "warn"), T("kesan sampingan") - 0.15, "pop"),
        ("t", title('Setiap ubat ada <span class="hl o">kesan sampingan</span>', "sm"), s - 0.05, "in"),
        (".c06-kesan-p0 .hl", None, T("kesan sampingan") + 0.1, "hl"),
    ]),
], "Side effects exist for every medicine")

# --- c07: "boleh menyebabkan mimpi pelik-pelik, rasa lemah sementara. Tapi ni ringan je dan dikawal ..."
s = T("boleh menyebabkan mimpi")
card("c07-mimpi", s - 0.2, T("devigo ni bukan") - 0.15, [
    (s - 0.2, [
        ("k", chip("Kesan sampingan", MARKER, "warn"), s - 0.15, "pop"),
        ("r1", row("dot", "Mimpi pelik-pelik", MARKER), T("mimpi") - LEAD, "in"),
        ("r2", row("dot", "Rasa lemah sementara", MARKER), T("rasa lemah") - LEAD, "in"),
    ]),
    (T("tapi ni ringan") - 0.1, [
        ("st", '<div class="stamp teal">RINGAN</div>', T("ringan") - 0.06, "stamp"),
        ("s", '<div class="sub">&amp; dikawal dengan dos yang sesuai</div>', T("dikawal") - LEAD, "in"),
    ]),
], "Side effects 2-3, then 'mild, dose-controlled'")

# --- c08: "Perlu ambil ikut arahan doktor dan elakkan alkohol kalau ambil ubat ni"
s = T("perlu ambil ikut")
card("c08-arahan", s - 0.15, T("kalau insomnia dah") - 0.12, [
    (s - 0.15, [
        ("k", chip("Penting", NAVY, "warn"), s - 0.1, "pop"),
        ("r1", row("check", "Ambil ikut <b>arahan doktor</b>"), T("ikut arahan") - LEAD, "in"),
        ("r2", row("cross", "Elakkan <b>alkohol</b>", MARKER), T("elakkan alkohol") - LEAD, "in"),
    ]),
], "Safety: follow the doctor, avoid alcohol")

# --- c09: "Kalau insomnia dah lama sangat sampai kacau emosi, kerja, kesihatan"
s = T("kalau insomnia dah")
pills = ('<div class="pills"><span class="pill" id="c09-p1">Emosi</span><span class="pill" id="c09-p2">Kerja</span>'
         '<span class="pill" id="c09-p3">Kesihatan</span></div>')
card("c09-lama", s - 0.12, T("jangan tunggu") - 0.2, [
    (s - 0.12, [
        ("t", title('Insomnia <span class="hl o">berpanjangan</span>?', "sm"), s - 0.06, "in"),
        (".c09-lama-p0 .hl", None, T("lama sangat") + 0.05, "hl"),
        ("g", pills, s, "none"),
        ("#c09-p1", None, T("emosi") - LEAD, "pop"),
        ("#c09-p2", None, T("kerja", after=T("emosi")) - LEAD, "pop"),
        ("#c09-p3", None, T("kesihatan", after=T("emosi")) - LEAD, "pop"),
    ]),
], "Long-standing insomnia disrupting emotion / work / health")

# --- c10: name + comment prompt (no clinic promo, no end card)
s = T("doktor azren")
card("c10-soalan", s - 0.2, DUR, [
    (s - 0.2, [
        ("n", '<div class="name">Dr Azren <span class="bar"></span> <span class="ntag">Spread Positivity</span></div>', s - 0.15, "in"),
    ]),
    (T("apa apa soalan") - 0.12, [
        ("t", title('Ada soalan? <span class="teal">Komen di bawah</span>', "sm"), T("apa apa soalan") - 0.08, "in"),
        ("d", '<div class="disc-note">Video pendidikan · bukan nasihat perubatan peribadi</div>', T("boleh tanya") - 0.1, "fade"),
    ]),
], "Speaker name, then comment prompt + education disclaimer")


# ================================================================== INSERTS (full screen)
INSERTS = []


def insert(iid, kind, start, end, body, anims, **kw):
    INSERTS.append({"id": iid, "kind": kind, "start": fq(start), "end": fq(end), "body": body, "anims": anims, **kw})


def sticky(sid, text, x, y, w=560, color=CREAM, hand=False, rot=-3):
    cls = "sticky hand-note" if hand else "sticky"
    return (f'<div class="{cls}" id="{sid}" data-rot="{rot}" style="left:{x}px; top:{y}px; width:{w}px; background-color:{color}">'
            f'<span class="tape"></span>{text}</div>')


def kin(kid, text, cls=""):
    return f'<div class="kin {cls}" id="{kid}">{text}</div>'


# --- B1 hook: 3 a.m., awake. Kinetic hook replaces captions until the cut to the face.
H_END = T("pernah tak", after=6) - 0.06
hook_pages = [
    ("h1", kin("h1", "BADAN PENAT,"), 0.0),
    ("h2", kin("h2", 'MATA DAH <span class="o">TERPEJAM-PEJAM</span>'), T("mata") - LEAD),
    ("h3", kin("h3", "TAPI OTAK…"), T("tapi otak") - LEAD),
    ("h4", kin("h4", '<span class="huge o">STILL BUSY</span>'), T("still busy") - LEAD),
    ("h5", kin("h5", "PUSING-PUSING"), T("pusing") - LEAD),
    ("h6", kin("h6", f'{icon("moon", "kin-ico", ORANGE)}PUKUL <span class="o">3</span> PAGI'), T("pukul tiga") - LEAD),
]
insert("b1-3am", "broll", 0.0, H_END, "".join(k for _, k, _ in hook_pages),
       [(f"#{k}", t, "page") for k, _, t in hook_pages], src="b1_3am.mp4", push=(1.0, 1.07), amb="amb_night", hook=True)
plan(0.0, "B-roll (AI, Kling): Malay man awake 3 a.m., terrace-house bedroom, ceiling fan; kinetic hook words page by page",
     "sub drop at 0, night ambience (crickets + fan), text whooshes, impact on STILL BUSY, clock tick on PUKUL 3 PAGI")

# --- MG1: not a benzodiazepine (alprazolam, clonazepam), not a knock-out pill
s = T("dia bukan di")
e = T("ubat ni adalah daripada") - 0.12
mg1 = f"""
  <div class="sheet">
    <div class="mg-head"><span class="chip" style="background:{NAVY}" id="m1-k">Kelas ubat</span></div>
    <div class="mg-title" id="m1-t">Bukan <span class="serif o2">benzodiazepin</span></div>
    <div class="index i1" id="m1-a"><span class="tape"></span><div class="lab">contoh</div><div class="drug">Alprazolam</div></div>
    <div class="index i2" id="m1-b"><span class="tape"></span><div class="lab">contoh</div><div class="drug">Clonazepam</div></div>
    <svg class="xmark" viewBox="0 0 900 520"><path id="m1-x1" pathLength="1" d="M70 60 C 300 210, 560 330, 840 470"/>
      <path id="m1-x2" pathLength="1" d="M820 50 C 600 190, 330 340, 80 480"/></svg>
    <div class="note" id="m1-n">bukan ubat untuk buat kita “pengsan”</div>
  </div>"""
insert("m1-benzo", "mg", s - 0.15, e, mg1, [
    ("#m1-k", s - 0.05, "pop"), ("#m1-t", T("bawah kelas") - LEAD, "rise"),
    ("#m1-a", T("alprazolam" if False else "aprazolam") - LEAD, "slap"), ("#m1-b", T("klonazepam") - LEAD, "slap"),
    ("#m1-x1", T("dia bukan ubat") - 0.05, ("draw", 0.32)), ("#m1-x2", T("dia bukan ubat") + 0.22, ("draw", 0.32)),
    ("#m1-n", T("pengsan") - LEAD, "rise"),
])
plan(s, "MG paper: 'Bukan benzodiazepin' — index cards Alprazolam / Clonazepam slapped on, marker X scribbled, note 'bukan ubat pengsan'",
     "paper tear in, 2 card slaps, marker scribble, pen note")

# --- B2: switch off — the click lands on "off" (clip press ≈1.7s), the light dies on "jaga"
t_off = T("off")
b2s = t_off - 1.7
insert("b2-switch", "broll", b2s, T("dalam otak kita") - 0.06,
       kin("s1", '<span class="huge">SWITCH OFF</span>', "low") + kin("s2", '<span class="hand-o">butang “jaga”</span>', "low2"),
       [("#s1", t_off - 0.3, "page"), ("#s2", T("butang jaga") - LEAD, "rise")], src="b2_switch.mp4", push=(1.0, 1.05),
       clicks=[t_off])
plan(b2s, "B-roll (AI): hand switches off a hallway light — click on 'off'; 'SWITCH OFF' + handwritten 'butang jaga'", "switch click on 'off', whoosh in")

# --- MG2: inside the head, the wake switch sits at OFF — it doesn't force sleep
s = T("dalam otak kita")
e = T("antara fungsi utama") - 0.1
head = ('<svg class="head" viewBox="0 0 400 480"><path id="m2-hp" pathLength="1" d="M150 470 L150 402 C112 392 84 364 72 326 '
        'C44 312 40 280 60 258 C40 206 52 124 112 74 C172 24 272 24 322 74 C370 122 380 192 362 242 C376 266 386 286 370 300 '
        'C360 306 350 306 346 312 C351 332 346 350 330 356 C336 372 326 386 300 386 C290 402 270 408 248 402 L248 470"/></svg>')
mg2 = f"""
  <div class="night">
    {head}
    <div class="toggle" id="m2-tg"><span class="tg-lab">JAGA</span><span class="tg-track" id="m2-tr"><span class="tg-knob" id="m2-kn"></span></span>
      <span class="tg-state" id="m2-st">OFF</span></div>
    <div class="m2-txt" id="m2-a">Tak <span class="strike" id="m2-sk">paksa</span> tidur</div>
    <div class="m2-sub" id="m2-b">matikan isyarat “jaga” — badan tidur sendiri</div>
  </div>"""
insert("m2-head", "mg", s - 0.1, e, mg2, [
    ("#m2-hp", s - 0.1, ("draw", 0.55)), ("#m2-tg", T("otak kita") - 0.05, "pop"), ("#m2-kn", T("kita", after=s) + 0.1, "knob"),
    ("#m2-a", T("tak paksa") - LEAD, "rise"), ("#m2-sk", T("paksa") + 0.25, "strike"), ("#m2-b", T("tidur pun") - 0.05, "fade"),
])
plan(s, "MG night: head outline draws, 'JAGA' toggle flips OFF, 'Tak paksa tidur' with 'paksa' struck", "click on toggle, marker strike")

# --- HERO (behind the subject; matte composited in assemble.sh)
HERO_T = T("insomnia") - 0.1
HERO_END = T("untuk kes susah") + 0.3
plan(HERO_T, "HERO: 'INSOMNIA' slams in BEHIND the head (subject matte), kicker card above", "riser into low impact")

# --- B3: can't sleep — three sticky notes on the words
s = HERO_END
e = T("terutamanya insomnia") - 0.1
b3 = (sticky("n31", "Susah nak tidur", 70, 250, 560, CREAM, rot=-4)
      + sticky("n32", "Mudah terjaga waktu malam", 330, 480, 640, PAPER2, rot=3)
      + sticky("n33", "Tidur tak lena", 120, 730, 520, CREAM, rot=-2))
insert("b3-condo", "broll", s, e, b3, [("#n31", T("susah nak tidur") - LEAD, "slap"), ("#n32", T("mudah terjaga") - LEAD, "slap"),
                                       ("#n33", T("tidur tak lena") - LEAD, "slap")], src="b3_toss_condo.mp4", push=(1.0, 1.06),
       amb="amb_night")
plan(s, "B-roll (AI): Chinese Malaysian woman restless in a KL condo at night; 3 sticky notes slap on", "night ambience, 3 paper slaps")

# --- B4: anxiety + overthinking
s = e
e = T("kelebihan") - 0.15
b4 = (kin("a0", '<span class="hand-o">terutamanya insomnia berkait dengan</span>', "top")
      + kin("a1", '<span class="box">ANXIETY</span>', "mid1") + kin("a2", '<span class="box o">OVERTHINKING</span>', "mid2"))
insert("b4-office", "broll", s, e, b4, [("#a0", T("insomnia yang berkait") - LEAD, "rise"), ("#a1", T("anxiety") - LEAD, "slam"),
                                        ("#a2", T("overthinking") - LEAD, "slam")], src="b4_overthink_office.mp4", push=(1.0, 1.06),
       amb="amb_office")
plan(s, "B-roll (AI): Indian Malaysian man in a late KL office, temples in hands; ANXIETY / OVERTHINKING slam in", "office hum, 2 bass hits")

# --- MG3: lower addiction risk vs benzodiazepines — a balance tips (no numbers, qualitative)
s = T("kurang ketagihan") - 0.15
e = T("dia kurang hangover") - 0.1
mg3 = f"""
  <div class="sheet">
    <div class="mg-head"><span class="chip" style="background:{TEAL}" id="m3-k">Kelebihan</span></div>
    <div class="mg-title" id="m3-t">Risiko <span class="serif">ketagihan</span></div>
    <div class="scale">
      <div class="post"></div>
      <div class="beam-wrap" id="m3-beam"><div class="beam"></div>
        <div class="pan l"><div class="tag t1" id="m3-d">Dayvigo</div></div>
        <div class="pan r"><div class="tag t2" id="m3-bz">Benzodiazepin</div></div></div>
    </div>
    <div class="m3-lab" id="m3-lo">Dayvigo: risiko <b>lebih rendah</b></div>
    <div class="note small" id="m3-n">berbanding ubat benzodiazepin</div>
  </div>"""
insert("m3-scale", "mg", s, e, mg3, [
    ("#m3-k", s + 0.05, "pop"), ("#m3-t", T("ketagihan") - LEAD, "rise"), ("#m3-d", T("ketagihan") + 0.15, "drop"),
    ("#m3-n", T("berbanding") - LEAD, "fade"), ("#m3-bz", T("benzodiazepin", after=s) - LEAD, "drop"),
    ("#m3-beam", T("benzodiazepin", after=s) + 0.12, "tip"), ("#m3-lo", T("benzodiazepin", after=s) + 0.2, "rise"),
])
plan(s, "MG paper: balance scale — 'Dayvigo' and 'Benzodiazepin' weights drop in, beam tips: 'risiko ketagihan lebih rendah' (qualitative, as spoken)",
     "paper tear in, 2 weight thuds, beam creak, pop")

# --- B5: morning — less hangover, stays asleep longer
s = e
e = T("tapi setiap ubat") - 0.15
b5 = (sticky("n51", "Kurang <i>hangover</i> waktu pagi", 90, 260, 620, CREAM, rot=-3)
      + sticky("n52", "Kekalkan tidur lebih lama", 300, 520, 640, PAPER2, rot=2))
insert("b5-morning", "broll", s, e, b5, [("#n51", T("kurang hangover") - LEAD, "slap"), ("#n52", T("kekalkan tidur") - LEAD, "slap")],
       src="b5_morning.mp4", push=(1.0, 1.05), amb="amb_morning")
plan(s, "B-roll (AI): Malay man wakes refreshed, opens curtains to warm light; 2 sticky notes", "morning birds, 2 slaps")

# --- B7: daytime drowsiness, especially early on
s = T("ubat ni boleh menyebabkan mengantuk") - 0.1
e = T("boleh menyebabkan mimpi") - 0.25
b7 = (sticky("n71", "Mengantuk pada siang hari", 70, 200, 780, CREAM, rot=-3)
      + sticky("n72", "terutamanya awal pengambilan ubat", 110, 330, 870, PAPER2, hand=True, rot=2))
insert("b7-drowsy", "broll", s, e, b7, [("#n71", T("mengantuk pada siang") - LEAD, "slap"), ("#n72", T("awal pengambilan") - LEAD, "slap")],
       src="b7_tired_work.mp4", push=(1.0, 1.06), amb="amb_office")
plan(s, "B-roll (AI): man yawning at his office desk; sticky 'Mengantuk pada siang hari' + handwritten 'terutamanya awal pengambilan'", "office hum, 2 slaps")

# --- MG4: not for everyone
s = T("devigo ni bukan") - 0.12
e = T("masih perlu jaga") - 0.2
mg4 = f"""
  <div class="night">
    <div class="m4-big"><span id="m4-w1">Bukan</span> <span id="m4-w2">untuk</span></div>
    <div class="m4-big o"><span id="m4-w3">semua orang</span></div>
    <svg class="m4-ul" viewBox="0 0 760 40"><path id="m4-u" pathLength="1" d="M8 26 C 200 10, 480 36, 750 14"/></svg>
    <div class="m2-sub m4-sub" id="m4-s">Tak sesuai kalau…</div>
  </div>"""
insert("m4-bukan", "mg", s, e, mg4, [("#m4-w1", T("bukan untuk semua") - LEAD, "rise"), ("#m4-w2", T("untuk semua") - LEAD, "rise"),
                                     ("#m4-w3", T("semua orang") - LEAD, "slam"), ("#m4-u", T("orang", after=s) + 0.1, ("draw", 0.4)),
                                     ("#m4-s", T("tak sesuai kalau") - LEAD, "rise")])
plan(s, "MG night: 'Bukan untuk SEMUA ORANG' word by word, orange marker underline, 'Tak sesuai kalau…'", "paper tear in, low impact, marker swipe")

# --- B6: night shift
s = e
e = T("perlu ambil ikut") - 0.18
b6 = (sticky("n61", "Masih perlu berjaga malam", 80, 190, 640, CREAM, rot=-3)
      + sticky("n62", "Kerja shift malam", 400, 360, 520, PAPER2, rot=3)
      + '<div class="stamp-lg" id="n63">TAK SESUAI</div>')
insert("b6-nurse", "broll", s, e, b6, [("#n61", T("masih perlu jaga") - LEAD, "slap"), ("#n62", T("kerja shift") - LEAD, "slap"),
                                       ("#n63", T("tak sesuai", after=T("shift")) - 0.05, "stamp")],
       src="b6_nightshift_nurse.mp4", push=(1.0, 1.05), amb="amb_ward")
plan(s, "B-roll (AI): Malay nurse on night shift at a ward station; stickies + 'TAK SESUAI' stamp", "ward hum, 2 slaps, stamp thud")

# --- MG5: don't wait
s = T("jangan tunggu") - 0.15
e = T("tidur yang terganggu") - 0.1
mg5 = f"""
  <div class="night">
    <div class="m5-stamp" id="m5-s">JANGAN TUNGGU LAGI</div>
  </div>"""
insert("m5-jangan", "mg", s, e, mg5, [("#m5-s", T("jangan tunggu") - 0.02, "stamp")])
plan(s, "MG: 'JANGAN TUNGGU LAGI' rubber stamp slam", "paper tear in, stamp impact")

# --- B8: professional assessment
s = T("boleh buat penilaian") - 0.12
e = T("ataupun boleh buat") - 0.1
b8 = (sticky("n81", "Penilaian profesional kesihatan mental", 70, 200, 700, CREAM, rot=-2)
      + sticky("n82", "Cari punca sebenar", 380, 360, 640, PAPER2, rot=3))
insert("b8-consult", "broll", s, e, b8, [("#n81", T("penilaian daripada") - LEAD, "slap"), ("#n82", T("cari punca") - LEAD, "slap")],
       src="b8_consult.mp4", push=(1.0, 1.05), amb="amb_clinic")
plan(s, "B-roll (AI): supportive consultation in a Malaysian clinic (over-the-shoulder, doctor unidentifiable); 2 stickies", "soft room tone, 2 slaps, hopeful swell")

INSERTS.sort(key=lambda x: x["start"])
for a, b in zip(INSERTS, INSERTS[1:]):
    assert a["end"] <= b["start"] + 0.35, (a["id"], b["id"], a["end"], b["start"])
for x in INSERTS:
    assert x["end"] - x["start"] >= 1.0, (x["id"], x["end"] - x["start"])
    assert x["end"] <= HERO_T - 0.4 or x["start"] >= fq(HERO_END) - 0.001, x["id"]  # hero window stays on the face


# ================================================================== CAPTIONS
FIX = {"devigo": "Dayvigo", "aprazolam": "alprazolam", "klonazepam": "clonazepam", "tiga": "3", "azren": "Azren",
       "nilai": "Nilai", "doktor": "doktor"}
KEY = {"dayvigo", "benzodiazepin", "alprazolam", "clonazepam", "orexin", "insomnia", "anxiety", "overthinking", "ketagihan",
       "hangover", "sampingan", "mengantuk", "mimpi", "lemah", "alkohol", "shift", "jangan", "tunggu", "profesional", "natural",
       "busy", "switch", "off", "jaga", "ringan", "doktor", "rosak", "3", "generasi", "antagonis"}
GLUE = {("kesan", "sampingan"), ("kesihatan", "mental"), ("waktu", "malam"), ("waktu", "pagi"), ("siang", "hari"),
        ("shift", "malam"), ("switch", "off"), ("butang", "jaga"), ("arahan", "doktor"), ("take", "care"), ("doktor", "Azren"),
        ("di", "Nilai"), ("hangover", "effect"), ("punca", "sebenar"), ("jangan", "tunggu"), ("generasi", "baru"),
        ("semua", "orang"), ("tak", "sesuai"), ("tak", "lena"), ("lebih", "lama"), ("lebih", "natural"), ("ubat", "tidur"),
        ("rasa", "lemah"), ("dos", "yang"), ("otak", "kita"), ("insomnia", "yang")}


def caption_words():
    out = []
    for i, w in enumerate(WORDS):
        t = FIX.get(w["text"], w["text"])
        prev = out[-1]["text"] if out else ""
        if t == "tekeh":
            m = round((w["start"] + w["end"]) / 2, 3)
            out += [{"text": "take", "start": w["start"], "end": m}, {"text": "care", "start": m, "end": w["end"]}]
            continue
        if out and ((prev, t) in (("terpejam", "pejam"),) or (t in ("pusing", "pelik", "apa") and prev == t)):
            out[-1]["text"] += "-" + t
            out[-1]["end"] = w["end"]
            continue
        out.append({"text": t, "start": w["start"], "end": w["end"]})
    return out


CW = caption_words()


def _punct():
    """Sentence/clause ends from the two Whisper passes (their text is punctuated; their times drift),
    attached to OUR caption words by sequence-aligning the word lists."""
    import difflib
    import re
    norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())
    mine = [norm(w["text"].split("-")[0]) for w in CW]
    marks = {}
    for src in (EDIT / "transcripts" / "dayvigo.json", W.parent / "captions_src" / "large_v3.json"):
        ws = [w["text"] for w in json.loads(src.read_text())["words"] if w.get("type", "word") == "word"]
        toks = [(norm(p), t) for t in ws for p in t.replace("-", " ").split()]
        sm = difflib.SequenceMatcher(a=mine, b=[n for n, _ in toks], autojunk=False)
        for i, j, n in sm.get_matching_blocks():
            for k in range(n):
                end = toks[j + k][1].rstrip()[-1:]
                if end in ".?!":
                    marks[i + k] = "."
                elif end == "," and marks.get(i + k) != ".":
                    marks[i + k] = ","
    return marks


MARKS = _punct()
for _i, _w in enumerate(CW):
    _w["mark"] = MARKS.get(_i)
MAX_CHARS, MAX_WORDS, PAUSE = 17, 3, 0.3


# sentence starts on this cut (hand-listed from the transcript, like the ward project's hook lines):
# a caption line never runs across one
STARTS = ["pernah tak dengar", "apa itu", "devigo ni adalah", "dia bukan di", "dia bukan ubat", "ubat ni adalah daripada",
          "bahasa senang", "dia tak paksa", "antara fungsi", "untuk kes", "mudah terjaga", "tidur tak lena", "terutamanya insomnia",
          "kelebihan", "kurang ketagihan", "dia kurang", "dan boleh kekalkan", "tapi setiap", "contohnya ubat", "terutamanya pada awal",
          "boleh menyebabkan mimpi", "rasa lemah", "tapi ni ringan", "devigo ni bukan", "tak sesuai kalau", "contohnya kena",
          "tak sesuai perlu", "perlu ambil", "dan elakkan", "kalau insomnia", "jangan tunggu", "tidur yang terganggu",
          "boleh buat penilaian", "untuk cari", "ataupun boleh", "bersama saya", "di klinik", "apa apa soalan", "tekeh"]


def _start_idx():
    idx = set()
    raw = [w["text"] for w in WORDS]
    for ph in STARTS:
        toks = ph.split()
        hits = [i for i in range(len(raw) - len(toks) + 1) if raw[i:i + len(toks)] == toks]
        assert hits, ph
        idx.update(hits)
    # WORDS index -> CW index (CW joins reduplications and splits "take care")
    m, j = {}, 0
    for i, w in enumerate(WORDS):
        while j < len(CW) and not (abs(CW[j]["start"] - w["start"]) < 1e-6 or CW[j]["start"] <= w["start"] < CW[j]["end"] - 1e-6):
            j += 1
        m[i] = j
    return {m[i] for i in idx}


START_CW = _start_idx()
for _i, _w in enumerate(CW):
    _w["sent"] = _i in START_CW


def group(ws):
    lines, cur = [], []
    for w in ws:
        if cur:
            gap = w["start"] - cur[-1]["end"]
            chars = len(" ".join(x["text"] for x in cur + [w]))
            glued = (cur[-1]["text"], w["text"]) in GLUE and gap < 0.4
            if w["sent"] or cur[-1].get("mark") == ".":
                lines.append(cur)
                cur = []
            elif glued and (len(cur) >= MAX_WORDS or chars > MAX_CHARS) and len(cur) >= 2:
                lines.append(cur[:-1])
                cur = cur[-1:]
            elif not glued and (len(cur) >= MAX_WORDS or chars > MAX_CHARS or gap >= PAUSE
                                or (cur[-1].get("mark") == "," and len(cur) >= 2)):
                lines.append(cur)
                cur = []
        cur.append(w)
    if cur:
        lines.append(cur)

    def text(ln):
        return " ".join(x["text"] for x in ln)

    def on(i):
        nxt = lines[i + 1][0]["start"] if i + 1 < len(lines) else lines[i][-1]["end"] + 0.5
        return nxt - lines[i][0]["start"]

    changed = True
    while changed:   # merge lines that would flash (< 0.55s) into a neighbour in the same sentence
        changed = False
        for i in range(len(lines)):
            if on(i) >= 0.55:
                continue
            if i + 1 < len(lines) and not lines[i + 1][0]["sent"] and len(text(lines[i] + lines[i + 1])) <= MAX_CHARS + 4:
                lines[i:i + 2] = [lines[i] + lines[i + 1]]
            elif i > 0 and not lines[i][0]["sent"] and len(text(lines[i - 1] + lines[i])) <= MAX_CHARS + 4:
                lines[i - 1:i + 1] = [lines[i - 1] + lines[i]]
            else:
                continue
            changed = True
            break
    return lines


CAP_FROM = H_END            # the kinetic hook IS the caption before this
LINES = [ln for ln in group([w for w in CW if w["start"] >= CAP_FROM - 0.05])]
# the hero word is its own caption: drop the caption line(s) inside the hero window
# (only the line holding the hero word; the next line waits until the hero has cleared)
LINES = [ln for ln in LINES if not any(HERO_T - 0.05 <= w["start"] < HERO_T + 0.3 for w in ln)]
CAP_HOLD = {id(ln): HERO_END for ln in LINES if HERO_T <= ln[0]["start"] < HERO_END}


# ================================================================== HTML / JS
JS: list[str] = []


def js(line: str) -> None:
    JS.append(line)


def enter_r(sel, t, dist=110, dur=0.38):
    js(f"tl.fromTo('{sel}', {{x:{dist}, opacity:0}}, {{x:0, opacity:1, duration:{dur}, ease:'power4.out'}}, {fq(t)});")


def exit_l(sel, t, dist=110, dur=0.26):
    js(f"tl.to('{sel}', {{x:-{dist}, opacity:0, duration:{dur}, ease:'power4.in'}}, {fq(t)});")


def anim(sel, t, kind, rot=0):
    t = fq(t)
    if kind == "pop":
        js(f"tl.fromTo('{sel}', {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.3, ease:'back.out(1.6)'}}, {t});")
    elif kind == "in":
        enter_r(sel, t, 90, 0.36)
    elif kind == "fade":
        js(f"tl.fromTo('{sel}', {{opacity:0}}, {{opacity:1, duration:0.3, ease:'power2.out'}}, {t});")
    elif kind == "rise":
        js(f"tl.fromTo('{sel}', {{opacity:0, y:46}}, {{opacity:1, y:0, duration:0.4, ease:'power3.out'}}, {t});")
    elif kind == "hl":
        js(f"tl.fromTo('{sel}', {{backgroundSize:'0% 42%'}}, {{backgroundSize:'100% 42%', duration:0.4, ease:'power2.inOut'}}, {t});")
    elif kind == "strike":
        js(f"tl.fromTo('{sel}', {{backgroundSize:'0% 7px'}}, {{backgroundSize:'100% 7px', duration:0.3, ease:'power2.inOut'}}, {t});")
    elif kind == "stamp":
        js(f"tl.fromTo('{sel}', {{opacity:0, scale:2.0, rotation:{rot - 8}}}, {{opacity:1, scale:1, rotation:{rot - 6}, duration:0.24, ease:'power4.out'}}, {t});")
    elif kind == "slap":
        js(f"tl.fromTo('{sel}', {{opacity:0, scale:1.35, rotation:{rot + 9}}}, {{opacity:1, scale:1, rotation:{rot}, duration:0.26, ease:'power4.out'}}, {t});")
    elif kind == "slam":
        js(f"tl.fromTo('{sel}', {{opacity:0, scale:1.6}}, {{opacity:1, scale:1, duration:0.22, ease:'power4.out'}}, {t});")
    elif kind == "drop":
        js(f"tl.fromTo('{sel}', {{opacity:0, y:-160}}, {{opacity:1, y:0, duration:0.32, ease:'power3.in'}}, {t});")
    elif kind == "tip":
        js(f"tl.fromTo('{sel}', {{rotation:0}}, {{rotation:9, duration:0.7, ease:'back.out(1.4)'}}, {t});")
    elif kind == "knob":
        js(f"tl.fromTo('{sel}', {{x:0}}, {{x:-58, duration:0.22, ease:'power3.inOut'}}, {t});")
        js(f"tl.fromTo('#m2-tr', {{backgroundColor:'{ORANGE}'}}, {{backgroundColor:'#34465C', duration:0.22, ease:'power2.inOut'}}, {t});")
        js(f"tl.fromTo('#m2-st', {{opacity:0}}, {{opacity:1, duration:0.2}}, {fq(t + 0.12)});")
    elif isinstance(kind, tuple) and kind[0] == "draw":
        js(f"tl.fromTo('{sel}', {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:{kind[1]}, ease:'power2.inOut'}}, {t});")


SFX_FOR = {"pop": ("pop", -4), "in": ("paper_slide", -6), "fade": None, "rise": ("tick", -8), "hl": ("marker", -6),
           "strike": ("marker", -4), "stamp": ("stamp", 0), "slap": ("slap", -2), "slam": ("impact", -3), "drop": ("thud", -3),
           "tip": ("creak", -8), "knob": ("click", -2), "page": ("whoosh_text", -6)}


def sfx_for(kind, t, idx=0):
    k = kind[0] if isinstance(kind, tuple) else kind
    if k == "draw":
        sfx("scribble", t, -5, kind[1])
        return
    m = SFX_FOR.get(k)
    if m:
        sfx(m[0], t, m[1])


# ---------------- cards
CARD_HOSTS = []
for c in CARDS:
    cid = c["id"]
    pages_html = []
    for p, (t_in, els) in enumerate(c["pages"]):
        inner = "".join(f'<div id="{cid}-{key}" class="el">{frag}</div>' for key, frag, t, a in els if frag is not None)
        pages_html.append(f'<div class="page {cid}-p{p}" id="{cid}-page{p}">{inner}</div>')
    seed = sum(map(ord, cid))
    CARD_HOSTS.append(
        f'<div class="card-host clip" id="host-{cid}" data-start="{c["start"]}" data-duration="{round(c["end"] - c["start"], 4)}" '
        f'data-track-index="3"><div class="paper-card" id="{cid}-panel" style="clip-path:{torn(seed)}">'
        f'<span class="tape tl"></span>{"".join(pages_html)}</div></div>')
    js(f"// card {cid}: {c['intent']}")
    panel = f"#{cid}-panel"
    enter_r(panel, c["start"], 130, 0.42)
    sfx("paper_slide", c["start"], -5)
    for p, (t_in, els) in enumerate(c["pages"]):
        pg = f"#{cid}-page{p}"
        if p == 0:
            js(f"tl.set('{pg}', {{opacity:1}}, {c['start']});")
        else:
            exit_l(f"#{cid}-page{p - 1}", t_in - 0.22, 70, 0.22)
            js(f"tl.fromTo('{pg}', {{opacity:0, x:70}}, {{opacity:1, x:0, duration:0.32, ease:'power4.out'}}, {fq(t_in)});")
            sfx("swish", t_in - 0.15, -9)
        for key, frag, t, a in els:
            sel = f"#{cid}-{key}" if not key.startswith((".", "#")) else key
            if a == "none":
                continue
            t = max(t, c["start"] + 0.08)
            anim(sel, t, a)
            if a != "in" or t > c["start"] + 0.2:
                sfx_for(a, t)
    if c["end"] < DUR - 0.05:
        exit_l(panel, c["end"] - 0.26, 130, 0.26)

# ---------------- hero
HERO_HTML = (f'<div class="hero-host clip" id="hero-host" data-start="{fq(HERO_T)}" data-duration="{round(fq(HERO_END) - fq(HERO_T), 4)}" '
             f'data-track-index="2"><div class="hero" id="hero-word">INSOMNIA</div></div>')
js("// hero: INSOMNIA behind the subject (stillness 0.35s after the kicker lands, then the slam)")
js(f"tl.fromTo('#hero-word', {{opacity:0, scale:1.22}}, {{opacity:1, scale:1, duration:0.28, ease:'power4.out'}}, {fq(HERO_T)});")
sfx("riser", HERO_T - 0.7, -10, 0.7)
sfx("impact", HERO_T + 0.02, 0)

# ---------------- inserts
INS_HOSTS = []
for z, x in enumerate(INSERTS):
    iid, st, en = x["id"], x["start"], x["end"]
    if x["kind"] == "broll":
        media = (f'<video class="bv" id="{iid}-v" src="broll/{x["src"]}" muted playsinline data-start="{st}" '
                 f'data-duration="{round(en - st, 4)}" data-track-index="{6 + z % 2}"></video>')
        over = (f'<div class="ov clip" id="{iid}-ov" data-start="{st}" data-duration="{round(en - st, 4)}" data-track-index="8">'
                f'<div class="shade{" hook" if x.get("hook") else ""}"></div><div class="ai-tag">Ilustrasi AI</div>{x["body"]}</div>')
        INS_HOSTS.append(f'<div class="ins" id="{iid}-in" style="z-index:{20 + z}"><div class="bvwrap" id="{iid}-cam">{media}</div>{over}</div>')
    else:
        INS_HOSTS.append(f'<div class="ins clip" id="ins-{iid}" data-start="{st}" data-duration="{round(en - st, 4)}" data-track-index="{6 + z % 2}" '
                         f'style="z-index:{20 + z}"><div class="ins-in" id="{iid}-in"><div class="tear" id="{iid}-tear" '
                         f'style="clip-path:{torn(z + 40, "left", 14, 40)}"></div><div class="mg" id="{iid}-mg">{x["body"]}</div></div></div>')
    js(f"// insert {iid} ({x['kind']}) {st:.2f}-{en:.2f}s")
    host = f"#{iid}-in"
    if x["kind"] == "broll":
        if st <= 0.001:   # the hook is fully on screen at frame 0 (first frame = thumbnail)
            js(f"tl.set('{host}', {{opacity:1, x:0}}, 0);")
            sfx("drop", 0.0, -2)
        else:
            js(f"tl.set('{host}', {{opacity:0}}, 0);")
            js(f"tl.fromTo('{host}', {{x:150, opacity:0, filter:'blur(16px)'}}, {{x:0, opacity:1, filter:'blur(0px)', duration:0.36, ease:'power4.out'}}, {st});")
            sfx("whoosh", st - 0.12, -5)
        p0, p1 = x["push"]
        js(f"tl.fromTo('#{iid}-cam', {{scale:{p0}}}, {{scale:{p1}, duration:{round(en - st, 3)}, ease:'sine.inOut'}}, {st});")
        js(f"tl.to('{host}', {{x:-150, opacity:0, filter:'blur(16px)', duration:0.28, ease:'power4.in'}}, {fq(en - 0.28)});")
        js(f"tl.set('{host}', {{opacity:0}}, {fq(en)});")
        sfx("whoosh_soft", en - 0.25, -10)
        if x.get("amb"):
            sfx(x["amb"], st, -16, en - st)
        for t in x.get("clicks", []):
            sfx("click", t, 0)
    else:
        js(f"tl.fromTo('{host}', {{clipPath:'inset(0% 0% 0% 100%)'}}, {{clipPath:'inset(0% 0% 0% 0%)', duration:0.46, ease:'power3.inOut'}}, {st});")
        js(f"tl.fromTo('#{iid}-tear', {{x:1080}}, {{x:-90, duration:0.46, ease:'power3.inOut'}}, {st});")
        js(f"tl.to('{host}', {{x:-150, opacity:0, filter:'blur(14px)', duration:0.28, ease:'power4.in'}}, {fq(en - 0.28)});")
        sfx("paper_tear", st - 0.05, -3)
        sfx("whoosh_soft", en - 0.25, -10)
    # inner animations
    pages = [a for a in x["anims"] if a[2] == "page"]
    for i, (sel, t, kind) in enumerate(x["anims"]):
        t = max(t, st + (0.0 if st <= 0.001 else 0.1))
        if kind == "page":
            nxt = next((p[1] for p in pages if p[1] > t), None)
            if t <= 0.001:
                js(f"tl.set('{sel}', {{opacity:1, x:0}}, 0);")
            else:
                js(f"tl.fromTo('{sel}', {{opacity:0, x:120}}, {{opacity:1, x:0, duration:0.3, ease:'power4.out'}}, {fq(t)});")
                sfx("whoosh_text", t - 0.05, -7)
            if nxt is not None:
                js(f"tl.to('{sel}', {{opacity:0, x:-120, duration:0.2, ease:'power4.in'}}, {fq(nxt - 0.18)});")
            continue
        rot = 0
        if kind in ("slap",) and sel.startswith("#n"):
            rot = {"n31": -4, "n32": 3, "n33": -2, "n51": -3, "n52": 2, "n61": -3, "n62": 3, "n71": -3, "n72": 2, "n81": -2, "n82": 3}.get(sel[1:], 0)
        if kind in ("slap", "stamp") and sel.startswith("#m1-"):
            rot = {"#m1-a": -5, "#m1-b": 4}.get(sel, 0)
        anim(sel, t, kind, rot)
        sfx_for(kind, t)
# hook accents
sfx("impact", T("still busy") - LEAD + 0.02, -4)
sfx("clock", T("pukul tiga") - LEAD + 0.05, -6)

# ---------------- captions
CAP_HTML = []
for li, ln in enumerate(LINES):
    t0 = max(ln[0]["start"] - 0.08, CAP_HOLD.get(id(ln), 0.0))
    nxt = LINES[li + 1][0]["start"] - 0.1 if li + 1 < len(LINES) else DUR
    t1 = min(nxt, ln[-1]["end"] + 0.45)
    if t1 - t0 < 0.3:
        t1 = t0 + 0.3
    spans = "".join(f'<span class="w{" key" if w["text"].lower() in KEY else ""}" id="cw{li}-{k}">{esc(w["text"])}</span> '
                    for k, w in enumerate(ln))
    CAP_HTML.append(f'<div class="cap clip" id="cap{li}" data-start="{fq(t0)}" data-duration="{round(fq(t1) - fq(t0), 4)}" '
                    f'data-track-index="12"><div class="cap-in" id="capi{li}">{spans.strip()}</div></div>')
    js(f"tl.fromTo('#capi{li}', {{opacity:0, y:16, scale:0.94}}, {{opacity:1, y:0, scale:1, duration:0.16, ease:'power3.out'}}, {fq(t0)});")
    for k, w in enumerate(ln):
        js(f"tl.set('#cw{li}-{k}', {{className:'w{' key' if w['text'].lower() in KEY else ''} on'}}, {fq(w['start'] - 0.02)});")

FONTS = "".join([
    *(f'@font-face{{font-family:"Plus Jakarta Sans";src:url("fonts/PlusJakartaSans-{w}.woff2") format("woff2");font-weight:{w};font-display:block;}}'
      for w in (500, 700, 800)),
    '@font-face{font-family:"Anton";src:url("fonts/Anton-400.woff2") format("woff2");font-weight:400;font-display:block;}',
    '@font-face{font-family:"DM Serif Display";src:url("fonts/DMSerifDisplay-400.woff2") format("woff2");font-weight:400;font-display:block;}',
    '@font-face{font-family:"Caveat";src:url("fonts/Caveat-700-latin.woff2") format("woff2");font-weight:700;font-display:block;}',
])

CSS = f"""
{FONTS}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; padding:0; width:100%; height:100%; overflow:hidden; background:{NAVY}; font-family:"Plus Jakarta Sans", sans-serif; }}
#stage {{ position:relative; width:100%; height:100%; overflow:hidden; background:{NAVY}; }}
#bg-video {{ position:absolute; left:0; top:0; width:1080px; height:1920px; object-fit:cover; }}
.serif {{ font-family:"DM Serif Display", serif; font-weight:400; letter-spacing:0; }}
.teal {{ color:{TEAL}; }} .o {{ color:{ORANGE}; }} .o2 {{ color:{MARKER}; }}
.tape {{ position:absolute; width:120px; height:34px; background:rgba(255,255,255,.55); box-shadow:0 1px 3px rgba(0,0,0,.12);
  top:-14px; left:50%; margin-left:-60px; }}
.tape.tl {{ left:34px; margin-left:0; top:-4px; width:110px; height:30px; background:rgba(245,170,85,.55); }}
.hand {{ font-family:"Caveat", cursive; font-weight:700; font-size:40px; color:{MARKER}; }}
.hand.big {{ font-size:66px; color:{NAVY}; }}

/* ---- cards (headroom) */
.card-host {{ position:absolute; left:0; top:0; width:1080px; height:1920px; pointer-events:none; z-index:10; }}
.paper-card {{ position:absolute; left:56px; top:150px; width:968px; display:grid; padding:30px 40px 40px;
  background-color:{CREAM}; background-image:{noise_bg()}; color:{NAVY}; box-shadow:0 18px 40px rgba(6,14,24,.35); }}
.page {{ grid-area:1/1; opacity:0; align-self:start; }}
.page > .el + .el {{ margin-top:12px; }}
.chip {{ display:inline-flex; align-items:center; gap:10px; color:#fff; font-weight:800; font-size:27px; letter-spacing:.08em;
  text-transform:uppercase; padding:9px 20px 8px; border-radius:999px; }}
.chip-ico {{ width:28px; height:28px; }}
.title {{ font-weight:800; font-size:56px; line-height:1.08; letter-spacing:-.015em; }}
.title .serif {{ font-size:66px; }}
.title.sm {{ font-size:48px; }}
.title.inl {{ display:inline-block; margin-right:16px; }}
.el.inl-wrap {{ display:inline-block; }}
#c02-orexin-w1, #c02-orexin-w2, #c02-orexin-w3 {{ display:inline-block; margin-right:14px; margin-top:12px; }}
.sub {{ font-weight:700; font-size:38px; color:#3E4B59; }}
.hl {{ background:linear-gradient({ORANGE}, {ORANGE}) left 88%/0% 42% no-repeat; padding:0 4px; }}
.hl.o {{ color:{NAVY}; }}
.row {{ display:flex; align-items:center; gap:18px; font-weight:700; font-size:42px; line-height:1.12; }}
.disc {{ width:52px; height:52px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; flex:none; }}
.dico {{ width:32px; height:32px; }}
.pills {{ display:flex; gap:14px; flex-wrap:wrap; }}
.pill {{ display:inline-block; font-weight:800; font-size:38px; padding:10px 24px; border-radius:16px; background:{NAVY}; color:{CREAM}; }}
.stamp {{ display:inline-block; border:7px solid {MARKER}; color:{MARKER}; border-radius:14px; font-weight:800; font-size:62px;
  letter-spacing:.06em; padding:4px 22px 0; font-family:"Anton", sans-serif; }}
.stamp.teal {{ border-color:{TEAL}; color:{TEAL}; }}
.name {{ font-weight:800; font-size:52px; display:flex; align-items:center; gap:18px; }}
.name .bar {{ width:6px; height:46px; background:{TEAL}; display:inline-block; }}
.name .ntag {{ font-family:"Caveat", cursive; font-weight:700; font-size:52px; color:{TEAL}; }}
#c07-mimpi-st {{ display:inline-block; }}  /* rotate the stamp, not a 968px-wide row */
#c07-mimpi-s {{ margin-top:18px; }}
.disc-note {{ font-weight:600; font-size:26px; color:#5A6672; letter-spacing:.02em; }}

/* ---- hero */
.hero-host {{ position:absolute; left:0; top:0; width:1080px; height:1920px; z-index:5; pointer-events:none; }}
.hero {{ position:absolute; left:0; top:380px; width:1080px; text-align:center; font-family:"Anton", sans-serif; font-size:262px;
  line-height:1; letter-spacing:.01em; color:{TEAL}; text-shadow:0 10px 30px rgba(6,14,24,.35); }}

/* ---- inserts */
.ins {{ position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden; pointer-events:none; }}
.ins-in {{ position:absolute; inset:0; overflow:hidden; }}
.bvwrap {{ position:absolute; inset:0; transform-origin:50% 42%; }}
.bv {{ position:absolute; left:0; top:0; width:1080px; height:1920px; object-fit:cover; }}
.ov {{ position:absolute; inset:0; }}
.shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(8,16,28,.55) 0%, rgba(8,16,28,.12) 30%,
  rgba(8,16,28,0) 52%, rgba(8,16,28,.32) 66%, rgba(8,16,28,.38) 76%, rgba(8,16,28,0) 88%); }}
.shade.hook {{ background:linear-gradient(180deg, rgba(8,16,28,.70) 0%, rgba(8,16,28,.45) 42%, rgba(8,16,28,.10) 62%, rgba(8,16,28,.35) 100%); }}
.ai-tag {{ position:absolute; left:48px; top:156px; font:700 22px "Plus Jakarta Sans"; letter-spacing:.1em; text-transform:uppercase;
  color:rgba(255,255,255,.88); background:rgba(0,0,0,.36); padding:6px 13px 5px; border-radius:9px; }}
.kin {{ position:absolute; left:60px; width:960px; top:470px; text-align:center; font-family:"Anton", sans-serif; font-size:118px; line-height:1.02;
  color:{CREAM}; text-shadow:0 6px 24px rgba(0,0,0,.45); opacity:0; }}
.kin .huge {{ font-size:168px; }}
.kin.low {{ top:330px; }} .kin.low2 {{ top:560px; }}
.kin.top {{ top:260px; }} .kin.mid1 {{ top:440px; }} .kin.mid2 {{ top:620px; }}
.kin-ico {{ width:104px; height:104px; vertical-align:-10px; margin-right:18px; }}
.hand-o {{ font-family:"Caveat", cursive; font-weight:700; font-size:84px; color:{ORANGE}; }}
.kin.top .hand-o {{ font-size:62px; color:{CREAM}; }}
.box {{ display:inline-block; background:{CREAM}; color:{NAVY}; padding:6px 30px 0; font-size:128px; }}
.box.o {{ background:{ORANGE}; color:{NAVY}; }}
.sticky {{ position:absolute; padding:34px 34px 30px; font-weight:800; font-size:50px; line-height:1.1; color:{NAVY};
  background-image:{noise_bg(0.07, 7)}; box-shadow:0 16px 34px rgba(0,0,0,.38); opacity:0; }}
.sticky.hand-note {{ font-family:"Caveat", cursive; font-weight:700; font-size:54px; color:{MARKER}; }}
.stamp-lg {{ position:absolute; left:190px; top:1060px; width:700px; text-align:center; border:10px solid {MARKER}; color:{MARKER};
  background:rgba(245,240,232,.92); border-radius:18px; font-family:"Anton", sans-serif; font-size:118px; letter-spacing:.06em;
  padding:6px 0 0; opacity:0; }}

/* ---- motion-graphic scenes */
.tear {{ position:absolute; top:0; left:0; width:90px; height:1920px; z-index:3; background-color:{CREAM};
  background-image:{noise_bg(0.12, 5)}; box-shadow:-8px 0 18px rgba(0,0,0,.25); }}
.mg {{ position:absolute; inset:0; }}
.sheet {{ position:absolute; inset:0; background-color:{CREAM}; background-image:{noise_bg(0.10, 9)}; color:{NAVY}; }}
.night {{ position:absolute; inset:0; background:radial-gradient(110% 70% at 70% 18%, #1C3550 0%, {NAVY} 60%, #0A121D 100%); color:{CREAM}; }}
.mg-head {{ position:absolute; left:80px; top:180px; }}
.mg-title {{ position:absolute; left:80px; top:262px; width:920px; font-weight:800; font-size:78px; line-height:1.05; letter-spacing:-.02em; }}
.mg-title .serif {{ font-size:96px; }}
.index {{ position:absolute; width:440px; height:250px; padding:34px 34px; background:#FFFDF8; box-shadow:0 16px 30px rgba(10,20,30,.22);
  border-top:10px solid {TEAL}; opacity:0; }}
.index.i1 {{ left:70px; top:520px; }} .index.i2 {{ left:560px; top:600px; }}
.index .lab {{ font-weight:700; font-size:26px; letter-spacing:.12em; text-transform:uppercase; color:#7A8794; }}
.index .drug {{ font-family:"DM Serif Display", serif; font-size:70px; margin-top:16px; }}
.xmark {{ position:absolute; left:90px; top:470px; width:900px; height:520px; }}
.xmark path {{ fill:none; stroke:{MARKER}; stroke-width:22; stroke-linecap:round; stroke-dasharray:1; stroke-dashoffset:1; opacity:.92; }}
.note {{ position:absolute; left:110px; top:1040px; width:860px; font-family:"Caveat", cursive; font-weight:700; font-size:72px; color:{MARKER}; }}
.note.small {{ top:1056px; font-size:58px; color:#5A6672; }}
.head {{ position:absolute; left:290px; top:300px; width:500px; height:600px; }}
.head path {{ fill:none; stroke:{CREAM}; stroke-width:7; stroke-linecap:round; stroke-linejoin:round; stroke-dasharray:1; stroke-dashoffset:1; }}
.toggle {{ position:absolute; left:372px; top:470px; display:flex; align-items:center; gap:16px; opacity:0; }}
.tg-lab {{ font-weight:800; font-size:34px; letter-spacing:.12em; color:{CREAM}; }}
.tg-track {{ position:relative; width:126px; height:66px; border-radius:40px; background:{ORANGE}; display:inline-block; }}
.tg-knob {{ position:absolute; left:64px; top:6px; width:54px; height:54px; border-radius:50%; background:#fff; box-shadow:0 3px 8px rgba(0,0,0,.3); }}
.tg-state {{ font-weight:800; font-size:34px; color:{TEAL}; opacity:0; }}
.m2-txt {{ position:absolute; left:80px; top:940px; width:920px; text-align:center; font-family:"DM Serif Display", serif; font-size:104px; opacity:0; }}
.strike {{ background:linear-gradient({MARKER}, {MARKER}) left 56%/0% 7px no-repeat; }}
.m2-sub {{ position:absolute; left:80px; top:1090px; width:920px; text-align:center; font-weight:700; font-size:42px; color:rgba(245,240,232,.82); opacity:0; }}
.scale {{ position:absolute; left:90px; top:470px; width:900px; height:560px; }}
.post {{ position:absolute; left:440px; top:120px; width:20px; height:420px; background:{NAVY}; border-radius:8px; }}
.beam-wrap {{ position:absolute; left:40px; top:100px; width:820px; height:40px; transform-origin:50% 50%; }}
.beam {{ position:absolute; left:0; top:12px; width:820px; height:16px; background:{NAVY}; border-radius:8px; }}
.pan {{ position:absolute; top:28px; width:300px; height:150px; border-left:4px solid {NAVY}; border-right:4px solid {NAVY}; }}
.pan.l {{ left:-20px; }} .pan.r {{ left:540px; }}
.tag {{ position:absolute; left:-20px; bottom:-40px; width:340px; padding:22px 0 18px; text-align:center; font-weight:800; font-size:40px;
  border-radius:16px; color:#fff; opacity:0; }}
.tag.t1 {{ background:{TEAL}; }} .tag.t2 {{ background:{MARKER}; padding:58px 0 54px; bottom:-76px; }}
.m3-lab {{ position:absolute; left:80px; top:1150px; width:920px; text-align:center; font-weight:700; font-size:54px; opacity:0; }}
.m3-lab b {{ background:linear-gradient({ORANGE},{ORANGE}) left 88%/100% 42% no-repeat; }}
.m4-big {{ position:relative; top:420px; text-align:center; font-family:"DM Serif Display", serif; font-size:140px; line-height:1.05; }}
.m4-big span {{ display:inline-block; opacity:0; }}
.m4-ul {{ position:absolute; left:160px; top:720px; width:760px; height:40px; }}
.m4-ul path {{ fill:none; stroke:{ORANGE}; stroke-width:12; stroke-linecap:round; stroke-dasharray:1; stroke-dashoffset:1; }}
.m4-sub {{ top:860px; font-size:56px; }}
.m5-stamp {{ position:absolute; left:110px; top:560px; width:860px; text-align:center; border:14px solid {ORANGE}; color:{ORANGE};
  border-radius:24px; font-family:"Anton", sans-serif; font-size:136px; line-height:1.08; padding:26px 20px 14px; opacity:0; }}

/* ---- captions */
.cap {{ position:absolute; left:140px; top:1292px; width:800px; height:140px; z-index:100; pointer-events:none; }}
.cap-in {{ width:100%; text-align:center; font-weight:800; font-size:64px; line-height:1.06; text-transform:uppercase; letter-spacing:.005em;
  color:rgba(255,255,255,.55); -webkit-text-stroke:2px rgba(16,28,44,.55); paint-order:stroke fill;
  text-shadow:0 4px 0 rgba(16,28,44,.45), 0 10px 26px rgba(0,0,0,.55); }}
.cap-in .w.on {{ color:#fff; }}
.cap-in .w.key.on {{ color:{ORANGE}; }}
"""

# the switch-off frame: the B-roll's light dies ~1.4s after the press, i.e. on "jaga"


def build_html() -> str:
    hosts = "\n  ".join(CARD_HOSTS + [HERO_HTML] + INS_HOSTS + CAP_HTML)
    body_js = "\n    ".join(JS)
    return f"""<!doctype html>
<html lang="ms">
<head>
<meta charset="utf-8" />
<style>{CSS}</style>
</head>
<body>
<div id="stage" data-composition-id="dayvigo" data-start="0" data-duration="{DUR}" data-fps="{FPS}" data-width="1080" data-height="1920">
  <video id="bg-video" src="input-video.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="1"></video>
  {hosts}
  <script src="vendor/gsap.min.js"></script>
  <script>
  (function () {{
    const tl = window.gsap.timeline({{ paused: true }});
    {body_js}
    window.__timelines["dayvigo"] = tl;
  }})();
  </script>
</div>
</body>
</html>
"""


def main() -> None:
    (PUB / "index.html").write_text(build_html())
    SFX.sort(key=lambda c: c["t"])
    (W / "sfx_cues.json").write_text(json.dumps({"duration": DUR, "cues": SFX}, indent=1))
    sb = {"duration": DUR, "hero": {"word": "INSOMNIA", "start": fq(HERO_T), "end": fq(HERO_END)},
          "cards": [{"id": c["id"], "start": c["start"], "end": c["end"], "intent": c["intent"]} for c in CARDS],
          "inserts": [{"id": x["id"], "kind": x["kind"], "start": x["start"], "end": x["end"], "src": x.get("src")} for x in INSERTS],
          "caption_lines": len(LINES)}
    (W / "storyboard.json").write_text(json.dumps(sb, indent=1))
    md = ["# Dayvigo — timecoded motion-graphics & sound-design plan", "",
          "Times are on the final cut (mm:ss.s). Generated by build_graphics.py from the word-level transcript.", "",
          "| Time | Visual | Sound |", "|---|---|---|"]
    for t, what, snd in sorted(PLAN):
        md.append(f"| {int(t // 60)}:{t % 60:04.1f} | {what} | {snd} |")
    for c in CARDS:
        md.append(f"| {int(c['start'] // 60)}:{c['start'] % 60:04.1f} | Card `{c['id']}`: {c['intent']} | paper slide in, pops/ticks per element |")
    md.sort(key=lambda r: r if not r.startswith("| ") or r.startswith("| Time") else "| " + r[2:].split(" |")[0].zfill(7) + r)
    (W / "plan.md").write_text("\n".join(md) + "\n")
    th = DUR - sum(x["end"] - x["start"] for x in INSERTS)
    print(f"DUR {DUR}s | {len(CARDS)} cards | {len(INSERTS)} inserts | {len(LINES)} caption lines | {len(SFX)} sfx cues | "
          f"talking head on screen {th:.1f}s ({th / DUR:.0%}), b-roll {sum(x['end'] - x['start'] for x in INSERTS if x['kind'] == 'broll'):.1f}s, "
          f"mg {sum(x['end'] - x['start'] for x in INSERTS if x['kind'] == 'mg'):.1f}s")


if __name__ == "__main__":
    main()
