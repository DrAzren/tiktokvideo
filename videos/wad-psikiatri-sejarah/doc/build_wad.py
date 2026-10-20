"""'Sejarah Wad Psikiatri di Malaysia — Adakah Ia Menakutkan?' — 16:9, 24 fps HyperFrames composition.

The narrator is the user's own voice (edit/voice_cut.wav). Every shot, card and kinetic line is anchored to a
phrase in edit/cut_words.json, so re-cutting the voice re-times the picture.
Layers: shots (Kling clips, Ken-Burns stills, full-frame graphics) → vignette + grain → era bar, kinetic text,
lower thirds, tags → subtitles.
Run: ../../../.venv/bin/python build_wad.py   →  public/index.html
"""

import html
import itertools
import json
import re
from pathlib import Path

D = Path(__file__).parent
P = D / "public"
WORDS = json.loads((D.parent / "edit" / "cut_words.json").read_text())
# subtitle punctuation/capitalisation for stretches the speaker ran together (display only; timing unchanged)
PUNCT = {107: "dihantar?", 135: "Rambutan,", 271: "British.", 374: "Hospital", 375: "Bahagia", 377: "Kinta,", 386: "lah.", 401: "dulu?",
         410: "antipsikotik,", 418: "antidepressant,", 427: "stabilizer.", 441: "pun,", 447: "berbeza.", 699: "umum.",
         718: "lain,", 842: "manik,", 863: "diri.", 871: "lah,", 877: "je,", 882: "minggu,", 900: "psikiatri,", 901: "saya",
         922: "mental,", 923: "cepat-cepat", 962: "yang", 967: "dan", 978: "Kalau"}
for _w in WORDS:
    _w["text"] = PUNCT.get(_w["i"], _w["text"])
MAPS = json.loads((D / "maps.json").read_text())
FPS, W, H = 24, 1920, 1080
OFF = 1.5                                         # voice starts after a short cold open
END_HOLD = 6.0
DUR = round(WORDS[-1]["end"] + OFF + END_HOLD, 3)

INK, NAVY, TEAL, TEAL_L, GOLD, CREAM, PARCH, SEPIA, RED = ("#0B1418", "#0A1A2F", "#0E4F55", "#5CC8BE", "#D9A441",
                                                           "#F4EBD8", "#E9DCC0", "#3B2A1A", "#B3352B")


def fq(t):
    return round(round(t * FPS) / FPS, 4)


def nk(s):
    return re.sub(r"[^\w-]", "", s.lower())


def T(phrase, end=False, after=0.0):
    toks = [nk(t) for t in phrase.split()]
    for i in range(len(WORDS) - len(toks) + 1):
        if WORDS[i]["start"] + OFF >= after and [nk(w["text"]) for w in WORDS[i:i + len(toks)]] == toks:
            return round((WORDS[i + len(toks) - 1]["end"] if end else WORDS[i]["start"]) + OFF, 3)
    raise KeyError(phrase)


js, body = [], []
_CUR = [0.0]


def TT(phrase, end=False, after=None):
    """Like T, but searches forward from the previous overlay anchor (overlays are authored in time order)."""
    t = T(phrase, end=end, after=_CUR[0] if after is None else after)
    _CUR[0] = max(_CUR[0], t - 2.0)
    return t


def A(sel, t, frm, to, dur, ease="power3.out", ir=True):
    extra = "" if ir else ", immediateRender:false"
    js.append(f"tl.fromTo('{sel}', {json.dumps(frm)}, {{...{json.dumps(to)}, duration:{round(dur, 3)}, ease:'{ease}'{extra}}}, {fq(t)});")


def TO(sel, t, to, dur, ease="power2.in"):
    js.append(f"tl.to('{sel}', {{...{json.dumps(to)}, duration:{round(dur, 3)}, ease:'{ease}'}}, {fq(t)});")


def SET(sel, t, props):
    js.append(f"tl.set('{sel}', {json.dumps(props)}, {fq(t)});")


def esc(s):
    return html.escape(s)


# ------------------------------------------------------------------ shot list (anchored to the narration)
KB = {"in": ({"scale": 1.0, "xPercent": 0}, {"scale": 1.09, "xPercent": 0}),
      "out": ({"scale": 1.12, "xPercent": 0}, {"scale": 1.02, "xPercent": 0}),
      "left": ({"scale": 1.1, "xPercent": 2.5}, {"scale": 1.1, "xPercent": -2.5}),
      "right": ({"scale": 1.1, "xPercent": -2.5}, {"scale": 1.1, "xPercent": 2.5}),
      "up": ({"scale": 1.12, "yPercent": 2.5}, {"scale": 1.12, "yPercent": -2.0})}

SHOTS = [  # (id, kind, src, start-anchor, transition-in, ken-burns / options)
    ("k1", "v", "k1_kampung_rain", 0.0, "black", None),
    ("s01", "s", "03_ipoh_1911", T("Waktu tu tak"), "cut", "right"),
    ("s02", "s", "02_mother_son", T("Tiba-tiba"), "cut", "in"),
    ("s03", "s", "06_alone_steps", T("Dia bercakap"), "cut", "out"),
    ("s04", "s", "04_villagers", T("Keluarga tak tahu"), "cut", "left"),
    ("s05", "s", "05_incense", T("Ada yang kata dia kena rasuk"), "cut", "in"),
    ("g01", "g", "fact", T("Tapi sebenarnya dia mungkin"), "fade", None),
    ("s06", "s", "18_empty_ward", T("Pada masa itu pilihan"), "cut", "in"),
    ("g02", "g", "title", T("Jadi ke mana"), "fade", None),
    ("g03", "g", "mappen", T("Ramai orang ingat"), "ink", None),
    ("s07", "s", "32_register", T("tapi sebenarnya sejarah penjagaan"), "cut", "in"),
    ("s08", "s", "09_early_asylum", T("Seawal abad"), "cut", "right"),
    ("s09", "s", "07_penang_1880", T("di kawasan seperti"), "cut", "left"),
    ("s10", "s", "08_taiping_1890", T("dan juga Taiping"), "cut", "in"),
    ("g04", "g", "conditions", T("Penyakit seperti skizofrenia"), "tear", None),
    ("s11", "s", "11_attendant", T("Rawatan pun waktu"), "cut", "in"),
    ("s12", "s", "13_ward_ext", T("Dalam sesetengah keadaan"), "cut", "left"),
    ("e01", "v", "e1_15_room", T("Bayangkan seseorang"), "cut", None),
    ("e02", "v", "e1_14_corridor", T("Dia takut"), "cut", None),
    ("s13", "s", "18_empty_ward", T("Tapi belum ada rawatan"), "cut", "out"),
    ("k2", "v", "k2_tanjung_rambutan", T("Kemudian pada tahun"), "ink", None),
    ("s14", "s", "12_tanjung_rambutan", T("semasa zaman pemerintahan"), "cut", "in"),
    ("g05", "g", "asylum", T("nama asal adalah"), "tear", None),
    ("s15", "s", "10_desk_ledger", T("Tapi pada waktu itu istilah"), "cut", "right"),
    ("g06", "g", "wards", T("Menariknya institusi"), "fade", None),
    ("s16", "s", "14_female_ward", T("Bayangkan institusi yang"), "cut", "in"),
    ("s17", "s", "33_veranda", T("akhirnya menjadi"), "cut", "left"),
    ("g07", "g", "names", T("Pada tahun 1928"), "tear", None),
    ("s18", "s", "16_feeding", T("macam mana kehidupan"), "cut", "in"),
    ("g08", "g", "meds", T("sekarang kalau pesakit"), "ink", None),
    ("e03", "v", "e1_13_asylum_ext", T("Di seluruh dunia"), "cut", None),
    ("e04", "v", "e1_16_garden", T("Pesakit mungkin tinggal"), "cut", None),
    ("s19", "s", "16_feeding", T("Ada yang memerlukan bantuan"), "cut", "out"),
    ("s20", "s", "17_garden_work", T("aktiviti rutin"), "cut", "right"),
    ("g09", "g", "imperfect", T("Namun pendekatan psikiatri"), "tear", None),
    ("s21", "s", "13_ward_ext", T("Dan penting untuk kita faham"), "cut", "out"),
    ("s22", "s", "33_veranda", T("Kita tak boleh anggap"), "cut", "right"),
    ("e05", "v", "e1_11_brain_morph", T("dan satu perkara yang penting"), "cut", None),
    ("e06", "v", "e1_17_lab", T("mulalah satu perubahan"), "ink", None),
    ("e07", "v", "e1_18_glassware", T("Sekitar tahun 1950-an"), "cut", None),
    ("s23", "s", "19_dispensary", T("Ini merupakan salah"), "cut", "in"),
    ("s24", "s", "10_desk_ledger", T("Sebelum tu doktor"), "cut", "left"),
    ("e08", "v", "e1_19_neurons", T("Dengan adanya ubat"), "cut", None),
    ("g10", "g", "grow", T("Pada masa yang sama"), "fade", None),
    ("g11", "g", "balance", T("Rawatan masih mempunyai"), "cut", None),
    ("s25", "s", "22_corridor_1960", T("dan perkembangan inilah"), "cut", "in"),
    ("s26", "s", "20_penang_gh_1958", T("pada tahun 1958"), "ink", "right"),
    ("s27", "s", "21_ward_1958", T("wad psikiatri dibuka"), "cut", "in"),
    ("g12", "g", "general", T("benda ni penting"), "tear", None),
    ("g13", "g", "depts", T("sama macam pesakit"), "cut", None),
    ("g14", "g", "mapmy", T("Ramai yang mengalami penyakit mental juga"), "fade", None),
    ("s28", "s", "31_horror_set", T("Sekarang kalau kita tengok"), "ink", "in"),
    ("k3", "v", "k3_modern_ward", T("kat dalam wad"), "cut", None),
    ("s29", "s", "24_doctor_nurse", T("Mereka diberikan ubat"), "cut", "in"),
    ("s30", "s", "25_mdt", T("Ada pesakit yang menjalani"), "cut", "left"),
    ("g15", "g", "reasons", T("Ada juga yang masuk"), "fade", None),
    ("g16", "g", "stay", T("tempoh kemasukan"), "cut", None),
    ("s31", "s", "28_family_visit", T("sebagai doktor psikiatri"), "ink", "in"),
    ("s32", "s", "26_ot", T("rawatan yang sesuai boleh"), "cut", "right"),
    ("e09", "v", "e1_21_family", T("Kalau anda ataupun"), "cut", None),
    ("s33", "s", "29_clinic_room", T("Boleh bawa datang"), "cut", "in"),
    ("g17", "g", "book", T("Saya juga ada tulis"), "fade", None),
    ("k4", "v", "k4_kinta_sunrise", T("kalau anda pernah"), "ink", None),
    ("g18", "g", "end", round(WORDS[-1]["end"] + OFF + 0.5, 3), "fade", None),
]
def _dur(f):
    import subprocess
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                capture_output=True, text=True).stdout)


SRCDUR = {f.stem: round(_dur(f) - 0.04, 3) for f in (P / "broll").glob("*.mp4")}
AI_KINDS = {"v", "s"}
WIN = {"cut": (-0.25, 0.05), "ink": (-0.5, 0.35), "tear": (-0.5, 0.3), "fade": (-0.4, 0.6), "black": (0, 0)}


# ------------------------------------------------------------------ graphics
def bg(kind):
    return {"dark": '<div class="bgdark"></div><div class="tex" style="opacity:.10;mix-blend-mode:screen"></div><div class="vg"></div>',
            "paper": '<div class="tex"></div><div class="vgw"></div>',
            "navy": '<div class="bgnavy"></div><div class="grid"></div><div class="vg"></div>',
            "teal": '<div class="bgteal"></div><div class="vg"></div>',
            "slate": '<div class="bgslate"></div><div class="tex" style="opacity:.14;mix-blend-mode:multiply"></div><div class="vg"></div>'}[kind]


def chars(text, cls="ch"):
    return "".join(f'<span class="{cls}">{esc(c) if c != " " else "&nbsp;"}</span>' for c in text)


G = {}  # gfx id -> (html, anim(t0, t1, sid))


def gfx(name):
    def deco(fn):
        G[name] = fn
        return fn
    return deco


@gfx("fact")
def g_fact(t0, t1, sid):
    h = bg("dark") + f"""<div class="fk" id="{sid}-k">Sebenarnya…</div>
<div class="fbig" id="{sid}-b">PENYAKIT MENTAL</div><div class="fsub" id="{sid}-s">yang serius — bukan sekadar “rasuk”</div>"""
    def an():
        A(f"#{sid}-k", t0 + 0.2, {"opacity": 0, "y": 12}, {"opacity": 1, "y": 0}, 0.5)
        A(f"#{sid}-b", T("penyakit mental yang serius") - 0.1, {"opacity": 0, "scale": 1.15}, {"opacity": 1, "scale": 1}, 0.7)
        A(f"#{sid}-s", T("serius", after=t0) - 0.05, {"opacity": 0, "y": 14}, {"opacity": 1, "y": 0}, 0.5)
    return h, an


@gfx("title")
def g_title(t0, t1, sid):
    h = bg("dark") + f"""<div class="ttl" id="{sid}-t">{chars("SEJARAH WAD PSIKIATRI")}</div>
<div class="ttl2" id="{sid}-t2">{chars("DI MALAYSIA")}</div>
<div class="ttl-sub" id="{sid}-s">Adakah ia menakutkan?</div>
<svg class="ttl-line" viewBox="0 0 1200 40"><path id="{sid}-p" d="M10 20 L1190 20" stroke="{GOLD}" stroke-width="2" fill="none" stroke-dasharray="1200"/>
{''.join(f'<circle id="{sid}-d{i}" cx="{10 + i * 236}" cy="20" r="6" fill="{GOLD}"/>' for i in range(6))}</svg>"""
    def an():
        js.append(f"tl.fromTo('#{sid}-t .ch', {{opacity:0, y:14, scale:1.25}}, {{opacity:1, y:0, scale:1, duration:1.0, ease:'power3.out', stagger:0.03}}, {fq(t0 + 0.3)});")
        js.append(f"tl.fromTo('#{sid}-t2 .ch', {{opacity:0, y:14, scale:1.25}}, {{opacity:1, y:0, scale:1, duration:1.0, ease:'power3.out', stagger:0.04}}, {fq(t0 + 1.0)});")
        A(f"#{sid}-s", t0 + 1.8, {"opacity": 0, "y": 16}, {"opacity": 1, "y": 0}, 0.8)
        js.append(f"tl.fromTo('#{sid}-p', {{strokeDashoffset:1200}}, {{strokeDashoffset:0, duration:1.6, ease:'power2.inOut'}}, {fq(t0 + 1.6)});")
        for i in range(6):
            A(f"#{sid}-d{i}", t0 + 1.7 + i * 0.25, {"opacity": 0, "scale": 0, "transformOrigin": "50% 50%"}, {"opacity": 1, "scale": 1}, 0.35, "back.out(2)")
    return h, an


def map_pins(prefix, which, names, labels=None):
    sz = MAPS[which]["size"]
    out = []
    for i, n in enumerate(names):
        x, y = MAPS[which]["pins"][n]
        lab = (labels or {}).get(n, n)
        out.append(f'<div class="pin" id="{prefix}-p{i}" style="left:{x - 14}px;top:{y - 14}px"><span class="pdot"></span>'
                   f'<span class="plab">{esc(lab)}</span></div>' if lab else
                   f'<div class="pin dot" id="{prefix}-p{i}" style="left:{x - 9}px;top:{y - 9}px"><span class="pdot"></span></div>')
    return sz, "".join(out)


@gfx("mappen")
def g_mappen(t0, t1, sid):
    sz, pins = map_pins(sid, "pen", ["Tanjung Rambutan", "Pulau Pinang", "Taiping"],
                        {"Tanjung Rambutan": "Tanjung Rambutan, Perak", "Pulau Pinang": "Pulau Pinang", "Taiping": "Taiping"})
    h = bg("paper") + f"""<div class="mapwrap" id="{sid}-m" style="width:{sz[0]}px;height:{sz[1]}px;left:{(W - sz[0]) // 2 + 120}px;top:{(H - sz[1]) // 2 + 20}px">
<img src="img/map_pen.svg" style="width:100%;height:100%"/>{pins}</div>
<div class="mph" id="{sid}-h">Tanah Melayu</div><div class="mcredit">Peta: Natural Earth</div>"""
    def an():
        A(f"#{sid}-m", t0, {"scale": 1.0, "transformOrigin": "40% 40%"}, {"scale": 1.12}, t1 - t0 + 0.5, "sine.inOut")
        A(f"#{sid}-h", t0 + 0.2, {"opacity": 0, "x": -20}, {"opacity": 1, "x": 0}, 0.6)
        A(f"#{sid}-p0", T("Tanjung Rambutan") - 0.1, {"opacity": 0, "scale": 0.3}, {"opacity": 1, "scale": 1}, 0.5, "back.out(2)")
    return h, an


@gfx("conditions")
def g_conditions(t0, t1, sid):
    names = ["Skizofrenia", "Bipolar", "Kemurungan"]
    cards = "".join(f'<div class="ccard" id="{sid}-c{i}"><div class="cq">?</div><div class="cn">{n}</div></div>' for i, n in enumerate(names))
    h = bg("paper") + f"""<div class="chd" id="{sid}-h">Ilmu pada zaman itu masih terhad</div><div class="crow">{cards}</div>
<div class="cfoot" id="{sid}-f">Belum difahami sepenuhnya</div>"""
    def an():
        A(f"#{sid}-h", t0 + 0.15, {"opacity": 0, "y": -12}, {"opacity": 1, "y": 0}, 0.6)
        for i, n in enumerate(names):
            A(f"#{sid}-c{i}", T(n.lower(), after=t0 - 0.5) - 0.15, {"opacity": 0, "y": 30}, {"opacity": 1, "y": 0}, 0.5)
        A(f"#{sid}-f", T("belum difahami") - 0.1, {"opacity": 0, "y": 10}, {"opacity": 1, "y": 0}, 0.5)
    return h, an


@gfx("asylum")
def g_asylum(t0, t1, sid):
    h = bg("paper") + f"""<div class="ak" id="{sid}-k">Nama asal · 1911</div>
<div class="aname"><span id="{sid}-w0">FEDERAL</span> <span class="lun" id="{sid}-w1">LUNATIC<i class="strike" id="{sid}-x"></i></span> <span id="{sid}-w2">ASYLUM</span></div>
<div class="aplace" id="{sid}-pl">Tanjung Rambutan, Perak</div>
<div class="anote" id="{sid}-n">“Lunatic” — istilah rasmi zaman itu, kini dianggap menghina</div>"""
    def an():
        A(f"#{sid}-k", t0 + 0.15, {"opacity": 0}, {"opacity": 1}, 0.5)
        for i, w in enumerate(["Federal", "Lunatic", "Asylum"]):
            A(f"#{sid}-w{i}", T(w, after=t0 - 1) - 0.05, {"opacity": 0, "y": 20}, {"opacity": 1, "y": 0}, 0.5)
        A(f"#{sid}-pl", T("Asylum", after=t0 - 1) + 0.4, {"opacity": 0}, {"opacity": 1}, 0.6)
        A(f"#{sid}-w1", T("perkataan lunatik"), {"color": SEPIA}, {"color": RED}, 0.4, "power2.out")
        A(f"#{sid}-x", T("penghinaan") - 0.1, {"scaleX": 0, "transformOrigin": "0% 50%"}, {"scaleX": 1}, 0.45, "power3.inOut")
        A(f"#{sid}-n", T("penghinaan") + 0.2, {"opacity": 0, "y": 12}, {"opacity": 1, "y": 0}, 0.5)
    return h, an


@gfx("wards")
def g_wards(t0, t1, sid):
    blocks = "".join(f'<div class="wb m" id="{sid}-b{i}"><div class="roof"></div><div class="wl">Wad Lelaki</div></div>' for i in range(3))
    blocks += f'<div class="wb f" id="{sid}-b3"><div class="roof"></div><div class="wl">Wad Perempuan</div></div>'
    h = bg("paper") + f"""<div class="wk" id="{sid}-k">Peringkat awal · 1911</div><div class="wrow">{blocks}</div>
<div class="wsum" id="{sid}-s"><b>3</b> wad lelaki &nbsp;·&nbsp; <b>1</b> wad perempuan</div>"""
    def an():
        A(f"#{sid}-k", t0 + 0.1, {"opacity": 0}, {"opacity": 1}, 0.5)
        tm = T("tiga wad lelaki")
        for i in range(3):
            A(f"#{sid}-b{i}", tm - 0.1 + i * 0.18, {"opacity": 0, "y": 40}, {"opacity": 1, "y": 0}, 0.5, "back.out(1.5)")
        A(f"#{sid}-b3", T("satu wad perempuan") - 0.1, {"opacity": 0, "y": 40}, {"opacity": 1, "y": 0}, 0.5, "back.out(1.5)")
        A(f"#{sid}-s", T("satu wad perempuan") + 0.5, {"opacity": 0, "y": 10}, {"opacity": 1, "y": 0}, 0.5)
    return h, an


@gfx("names")
def g_names(t0, t1, sid):
    rows = [("1911", "Federal Lunatic Asylum"), ("1928", "Central Mental Hospital"), ("1970-an", "Hospital Bahagia Ulu Kinta")]
    r = "".join(f'<div class="nrow" id="{sid}-r{i}"><div class="ny">{y}</div><div class="ndot"></div><div class="nn">{n}</div></div>' for i, (y, n) in enumerate(rows))
    h = bg("slate") + f"""<div class="nhd" id="{sid}-h">Satu institusi, tiga nama</div><div class="nrail" id="{sid}-l"></div>{r}"""
    def an():
        A(f"#{sid}-h", t0 + 0.1, {"opacity": 0, "y": -10}, {"opacity": 1, "y": 0}, 0.5)
        A(f"#{sid}-l", t0 + 0.2, {"scaleY": 0, "transformOrigin": "50% 0%"}, {"scaleY": 1}, 2.0, "power2.inOut")
        A(f"#{sid}-r0", t0 + 0.3, {"opacity": 0, "x": -30}, {"opacity": 1, "x": 0}, 0.5)
        A(f"#{sid}-r1", T("Central Mental") - 0.2, {"opacity": 0, "x": -30}, {"opacity": 1, "x": 0}, 0.5)
        A(f"#{sid}-r2", T("hospital bahagia") - 0.2, {"opacity": 0, "x": -30}, {"opacity": 1, "x": 0}, 0.5)
        A(f"#{sid}-r0, #{sid}-r1", T("hospital bahagia") - 0.2, {"opacity": 1}, {"opacity": 0.45}, 0.5, "power2.out", ir=False)
    return h, an


@gfx("meds")
def g_meds(t0, t1, sid):
    rows = [("Skizofrenia", "Antipsikotik", "skizofrenia"), ("Kemurungan", "Antidepresan", "kemurungan"), ("Bipolar", "Penstabil mood", "bipolar")]
    r = "".join(f'<div class="mrow" id="{sid}-r{i}"><div class="mc">{c}</div><div class="marr">→</div><div class="mm" id="{sid}-m{i}">{m}<i class="strike" id="{sid}-x{i}"></i></div></div>'
                for i, (c, m, _) in enumerate(rows))
    h = bg("teal") + f"""<div class="mhd" id="{sid}-h">Hari ini</div><div class="mhd sep" id="{sid}-h2">1911</div><div class="mgrid">{r}</div>
<div class="mnone" id="{sid}-n">Ubat-ubat ini belum wujud</div><div class="sepia" id="{sid}-sp"></div>"""
    def an():
        A(f"#{sid}-h", t0 + 0.1, {"opacity": 0, "y": -10}, {"opacity": 1, "y": 0}, 0.5)
        for i, (_, _, key) in enumerate(rows):
            A(f"#{sid}-r{i}", T(key, after=t0 - 0.5) - 0.15, {"opacity": 0, "x": -30}, {"opacity": 1, "x": 0}, 0.5)
        tb = T("pada zaman 1911")
        A(f"#{sid}-sp", tb, {"opacity": 0}, {"opacity": 1}, 0.8, "power2.inOut")
        A(f"#{sid}-h", tb, {"opacity": 1}, {"opacity": 0}, 0.3, "power2.in", ir=False)
        A(f"#{sid}-h2", tb + 0.2, {"opacity": 0, "y": -10}, {"opacity": 1, "y": 0}, 0.5)
        for i in range(3):
            A(f"#{sid}-x{i}", tb + 0.9 + i * 0.2, {"scaleX": 0, "transformOrigin": "0% 50%"}, {"scaleX": 1}, 0.4, "power3.inOut")
        A(f"#{sid}-n", tb + 1.6, {"opacity": 0, "y": 12}, {"opacity": 1, "y": 0}, 0.5)
    return h, an


@gfx("imperfect")
def g_imperfect(t0, t1, sid):
    h = bg("paper") + f"""<div class="ihd" id="{sid}-h">Tidak semuanya sempurna</div>
<div class="isub" id="{sid}-s">Ada kaedah rawatan lama yang kemudiannya ditinggalkan kerana:</div>
<div class="irow"><div class="ichip" id="{sid}-c0">Bukti keberkesanan lemah</div><div class="ichip" id="{sid}-c1">Risiko tinggi</div></div>"""
    def an():
        A(f"#{sid}-h", t0 + 0.15, {"opacity": 0, "y": 14}, {"opacity": 1, "y": 0}, 0.6)
        A(f"#{sid}-s", T("Ada kaedah rawatan") - 0.1, {"opacity": 0}, {"opacity": 1}, 0.5)
        A(f"#{sid}-c0", T("bukti keberkesanan") - 0.1, {"opacity": 0, "y": 20}, {"opacity": 1, "y": 0}, 0.5)
        A(f"#{sid}-c1", T("risiko yang tinggi") - 0.1, {"opacity": 0, "y": 20}, {"opacity": 1, "y": 0}, 0.5)
    return h, an


@gfx("grow")
def g_grow(t0, t1, sid):
    items = [("Antipsikotik", "1950-an"), ("Antidepresan", ""), ("Rawatan lain", "")]
    r = "".join(f'<div class="gi" id="{sid}-i{i}"><div class="gn">{n}</div><div class="gy">{y}</div></div>'
                + (f'<div class="ga" id="{sid}-a{i}">→</div>' if i < 2 else "") for i, (n, y) in enumerate(items))
    h = bg("navy") + f"""<div class="ghd" id="{sid}-h">Pilihan rawatan semakin berkembang</div><div class="grow">{r}</div>"""
    def an():
        A(f"#{sid}-h", t0 + 0.1, {"opacity": 0, "y": -10}, {"opacity": 1, "y": 0}, 0.5)
        A(f"#{sid}-i0", t0 + 0.3, {"opacity": 0, "y": 20}, {"opacity": 1, "y": 0}, 0.5)
        for i, key in ((1, "ubat antidepressant"), (2, "rawatan psikiatri yang lain")):
            A(f"#{sid}-a{i - 1}", T(key, after=t0 - 0.5) - 0.3, {"opacity": 0, "x": -10}, {"opacity": 1, "x": 0}, 0.3)
            A(f"#{sid}-i{i}", T(key, after=t0 - 0.5) - 0.15, {"opacity": 0, "y": 20}, {"opacity": 1, "y": 0}, 0.5)
    return h, an


@gfx("balance")
def g_balance(t0, t1, sid):
    h = bg("navy") + f"""<div class="bcol l" id="{sid}-l"><div class="bt">Risiko &amp; kesan sampingan</div><div class="bbar amber" id="{sid}-bl"></div><div class="bnote">masih wujud</div></div>
<div class="bcol r" id="{sid}-r"><div class="bt">Pilihan untuk membantu pesakit</div><div class="bbar teal" id="{sid}-br"></div><div class="bnote">semakin berkembang</div></div>"""
    def an():
        A(f"#{sid}-l", t0 + 0.1, {"opacity": 0, "y": 20}, {"opacity": 1, "y": 0}, 0.5)
        A(f"#{sid}-bl", t0 + 0.3, {"scaleX": 0, "transformOrigin": "0% 50%"}, {"scaleX": 0.45}, 0.9, "power2.out")
        tp = T("tapi pilihan untuk bantu")
        A(f"#{sid}-r", tp - 0.1, {"opacity": 0, "y": 20}, {"opacity": 1, "y": 0}, 0.5)
        A(f"#{sid}-br", tp + 0.1, {"scaleX": 0, "transformOrigin": "0% 50%"}, {"scaleX": 1}, 1.6, "power2.out")
    return h, an


@gfx("general")
def g_general(t0, t1, sid):
    h = bg("paper") + f"""<div class="gcol l" id="{sid}-l"><div class="gk">Sebelum</div><div class="bld solo"><div class="bl-roof"></div><div class="bl-body">Hospital khusus</div></div>
<div class="gd">terpisah daripada perkhidmatan perubatan lain</div></div>
<div class="gcol r" id="{sid}-r"><div class="gk">Mulai 1958</div><div class="bld big"><div class="bl-roof"></div><div class="bl-body">Hospital umum<span class="wing" id="{sid}-w">Wad psikiatri</span></div></div>
<div class="gd">lebih dekat dengan sistem penjagaan kesihatan biasa</div></div>"""
    def an():
        A(f"#{sid}-l", t0 + 0.1, {"opacity": 0, "x": -30}, {"opacity": 1, "x": 0}, 0.6)
        tr = T("tapi apabila wad")
        A(f"#{sid}-r", tr - 0.1, {"opacity": 0, "x": 30}, {"opacity": 1, "x": 0}, 0.6)
        A(f"#{sid}-w", tr + 0.6, {"opacity": 0, "scale": 0.6}, {"opacity": 1, "scale": 1}, 0.5, "back.out(1.8)")
        A(f"#{sid}-l", tr, {"opacity": 1}, {"opacity": 0.45}, 0.5, "power2.out", ir=False)
    return h, an


@gfx("depts")
def g_depts(t0, t1, sid):
    ds = [("Jantung", "jantung"), ("Buah pinggang", "buah pinggang"), ("Penyakit lain", "penyakit lain"), ("Kesihatan mental", "Ramai yang mengalami")]
    c = "".join(f'<div class="dchip{" hi" if i == 3 else ""}" id="{sid}-d{i}">{n}</div>' for i, (n, _) in enumerate(ds))
    h = bg("navy") + f"""<div class="dhd" id="{sid}-h">Hospital Umum</div><div class="drow">{c}</div>"""
    def an():
        A(f"#{sid}-h", t0 + 0.1, {"opacity": 0, "y": -10}, {"opacity": 1, "y": 0}, 0.5)
        for i, (_, key) in enumerate(ds[:3]):
            A(f"#{sid}-d{i}", T(key, after=t0 - 0.5) - 0.1, {"opacity": 0, "y": 20}, {"opacity": 1, "y": 0}, 0.45)
        A(f"#{sid}-d3", min(t1 - 0.8, T("penyakit lain", after=t0 - 0.5) + 0.6), {"opacity": 0, "scale": 0.7}, {"opacity": 1, "scale": 1}, 0.5, "back.out(1.8)")
    return h, an


@gfx("mapmy")
def g_mapmy(t0, t1, sid):
    names = list(MAPS["my"]["pins"])
    sz, pins = map_pins(sid, "my", names, {n: "" for n in names})
    h = bg("navy") + f"""<div class="mapwrap my" id="{sid}-m" style="width:{sz[0]}px;height:{sz[1]}px;left:{(W - sz[0]) // 2}px;top:{(H - sz[1]) // 2 + 40}px">
<img src="img/map_my.svg" style="width:100%;height:100%"/>{pins}</div>
<div class="myhd" id="{sid}-h">Perkhidmatan psikiatri berkembang ke hospital seluruh Malaysia</div><div class="mcredit l">Ilustrasi · Peta: Natural Earth</div>"""
    def an():
        A(f"#{sid}-h", t0 + 0.2, {"opacity": 0, "y": -10}, {"opacity": 1, "y": 0}, 0.6)
        for i in range(len(names)):
            A(f"#{sid}-p{i}", t0 + 0.8 + i * 0.28, {"opacity": 0, "scale": 0.2}, {"opacity": 1, "scale": 1}, 0.4, "back.out(2.2)")
    return h, an


@gfx("reasons")
def g_reasons(t0, t1, sid):
    rs = [("Kemurungan yang teruk", "kemurungan yang teruk"), ("Mania (full-blown)", "full blown"),
          ("Psikosis — tak mampu jaga keselamatan diri", "mengalami psikotik"), ("Risiko mencederakan diri", "risiko mencederakan")]
    li = "".join(f'<div class="ri" id="{sid}-i{i}"><span class="rd"></span>{n}</div>' for i, (n, _) in enumerate(rs))
    h = f"""<div class="kb"><img class="shotimg" src="img/23_modern_ward.jpg" style="filter:brightness(.45) saturate(.8)"/></div><div class="vg"></div>
<div class="rhd" id="{sid}-h">Antara sebab kemasukan ke wad</div><div class="rlist">{li}</div>"""
    def an():
        A(f"#{sid}-h", t0 + 0.1, {"opacity": 0, "y": -10}, {"opacity": 1, "y": 0}, 0.5)
        for i, (_, key) in enumerate(rs):
            A(f"#{sid}-i{i}", T(key, after=t0 - 0.5) - 0.15, {"opacity": 0, "x": -30}, {"opacity": 1, "x": 0}, 0.5)
    return h, an


@gfx("stay")
def g_stay(t0, t1, sid):
    bars = [("Beberapa hari", 0.22, "beberapa hari"), ("Beberapa minggu", 0.55, "beberapa minggu"), ("Lebih lama", 0.95, "penjagaan yang lebih lama")]
    b = "".join(f'<div class="srow" id="{sid}-r{i}"><div class="sl">{n}</div><div class="sbar"><i id="{sid}-b{i}"></i></div></div>' for i, (n, _, _) in enumerate(bars))
    h = f"""<div class="kb"><img class="shotimg" src="img/27_patient_room.jpg" style="filter:brightness(.42) saturate(.85)"/></div><div class="vg"></div>
<div class="shd" id="{sid}-h">Tempoh kemasukan berbeza mengikut keadaan pesakit</div><div class="sbox">{b}</div>"""
    def an():
        A(f"#{sid}-h", t0 + 0.1, {"opacity": 0, "y": -10}, {"opacity": 1, "y": 0}, 0.5)
        for i, (_, frac, key) in enumerate(bars):
            tt = T(key, after=t0 - 0.5) - 0.15
            A(f"#{sid}-r{i}", tt, {"opacity": 0}, {"opacity": 1}, 0.35)
            A(f"#{sid}-b{i}", tt, {"scaleX": 0, "transformOrigin": "0% 50%"}, {"scaleX": frac}, 0.9, "power2.out")
    return h, an


@gfx("book")
def g_book(t0, t1, sid):
    pages = "".join(f'<i style="top:{4 + k * 4}px"></i>' for k in range(12))
    h = bg("teal") + f"""<div class="bkstage"><div class="bshadow" id="{sid}-sh"></div>
<div class="book3d" id="{sid}-bk"><div class="bf bfront"><img src="img/book_cover.jpg"/><div class="bsheen" id="{sid}-sn"></div></div>
<div class="bf bback"></div><div class="bf bspine3"><span>DR, SAYA BOLEH SEMBUH KE?</span><b>DR AZREN</b></div>
<div class="bf bpages"></div><div class="bf btop">{pages}</div><div class="bf bbot"></div></div></div>
<div class="btxt" id="{sid}-t"><div class="bk1">Buku oleh Dr. Azren</div><div class="bk2">“Dr, Saya Boleh Sembuh Ke?”</div>
<div class="bk3">Manual Survival Kesihatan Mental — menjawab persoalan &amp; menangkis mitos</div><div class="bk4">Terbitan White Coat Books</div></div>"""
    def an():
        A(f"#{sid}-bk", t0 + 0.1, {"opacity": 0, "rotationY": 68, "rotationX": 8, "y": 60, "z": -300},
          {"opacity": 1, "rotationY": 28, "rotationX": 4, "y": 0, "z": 0}, 1.4, "power3.out")
        A(f"#{sid}-sh", t0 + 0.1, {"opacity": 0, "scaleX": 0.5}, {"opacity": 1, "scaleX": 1}, 1.4, "power3.out")
        A(f"#{sid}-bk", t0 + 1.5, {"rotationY": 28, "rotationX": 4}, {"rotationY": 14, "rotationX": 2}, t1 - t0 - 1.5, "sine.inOut", ir=False)
        A(f"#{sid}-sn", t0 + 1.2, {"x": -700}, {"x": 900}, 1.6, "power2.inOut")
        A(f"#{sid}-t", t0 + 0.6, {"opacity": 0, "x": 30}, {"opacity": 1, "x": 0}, 0.8)
    return h, an


@gfx("end")
def g_end(t0, t1, sid):
    h = bg("teal") + f"""<div class="e1" id="{sid}-a">SEJARAH WAD PSIKIATRI DI MALAYSIA</div>
<div class="e2" id="{sid}-b">Rawatan berubah — maruah pesakit tetap dijaga</div>
<div class="brand" id="{sid}-c"><span class="bl"></span><span>BORAK JIWA</span><span class="bl"></span></div>
<div class="ep" id="{sid}-d">Dr. Azren · Klinik Nissa</div>"""
    def an():
        A(f"#{sid}-a", t0 + 0.3, {"opacity": 0, "y": 24}, {"opacity": 1, "y": 0}, 0.8)
        A(f"#{sid}-b", t0 + 1.2, {"opacity": 0, "y": 14}, {"opacity": 1, "y": 0}, 0.7)
        A(f"#{sid}-c", t0 + 2.0, {"opacity": 0, "scale": 1.15}, {"opacity": 1, "scale": 1}, 0.9)
        A(f"#{sid}-d", t0 + 2.6, {"opacity": 0}, {"opacity": 1}, 0.6)
    return h, an


def tear_path():
    import random
    r = random.Random(5)
    pts, y = [(0, 0)], 0
    while y < 1080:
        y += r.randint(18, 42)
        pts.append((r.randint(18, 52), min(y, 1080)))
    pts.append((0, 1080))
    return "M" + " L".join(f"{x} {y}" for x, y in pts) + " Z"


def build_shots():
    anims = []
    for z, (sid, kind, src, t0, mode, opt) in enumerate(SHOTS):
        nxt = SHOTS[z + 1] if z + 1 < len(SHOTS) else None
        t0 = fq(t0)
        hold = fq(nxt[3] + WIN[nxt[4]][1] + 0.05) if nxt else DUR
        if kind == "v":
            sd = SRCDUR[src]
            need = hold - t0
            if need > sd + 0.05:
                print(f"!! {sid} {src}: slot {need:.2f}s > footage {sd:.2f}s")
            inner = (f'<div class="kb" id="{sid}-kb"><video class="clip shotv" id="{sid}-v" src="broll/{src}.mp4" muted playsinline '
                     f'data-start="{t0}" data-duration="{round(min(sd, need + 0.04), 3)}" data-track-index="{1 + z % 2}"></video></div>')
            A(f"#{sid}-kb", t0, {"scale": 1.0}, {"scale": 1.035}, hold - t0, "sine.inOut")
        elif kind == "s":
            inner = f'<div class="kb" id="{sid}-kb"><img class="shotimg" src="img/{src}.jpg" /></div>'
            a, b = KB[opt]
            A(f"#{sid}-kb", t0, a, b, hold - t0 + 0.3, "sine.inOut")
        else:
            h, an = G[src](t0, hold, sid)
            inner = f'<div class="gfx" id="{sid}-g">{h}</div>'
            anims.append(an)
        body.append(f'<div class="shot" id="{sid}" style="z-index:{10 + z}"><div class="shin{" inkm" if mode == "ink" else ""}" id="{sid}-in">{inner}</div></div>')
        a, b = WIN[mode]
        SET(f"#{sid}", t0 + a - 0.05, {"opacity": 1})
        if mode == "cut":
            A(f"#{sid}-in", t0 + a, {"opacity": 0}, {"opacity": 1}, b - a, "power1.inOut")
        elif mode == "black":
            A(f"#{sid}-in", 0, {"opacity": 0}, {"opacity": 1}, 1.4, "power2.out")
        elif mode == "fade":
            A(f"#{sid}-in", t0 + a, {"opacity": 0}, {"opacity": 1}, b - a, "power2.inOut")
        elif mode == "ink":
            js.append(f"tl.fromTo('#{sid}-in', {{'--r':'0%'}}, {{'--r':'140%', duration:{b - a}, ease:'power2.inOut'}}, {fq(t0 + a)});")
        elif mode == "tear":
            body.append(f'<div class="tear" id="{sid}-tear" style="z-index:{10 + z}"><svg viewBox="0 0 60 1080" preserveAspectRatio="none">'
                        f'<path d="{tear_path()}" fill="{PARCH}"/></svg></div>')
            js.append(f"tl.fromTo('#{sid}-in', {{clipPath:'inset(0% 100% 0% 0%)'}}, {{clipPath:'inset(0% 0% 0% 0%)', duration:{b - a}, ease:'power3.inOut'}}, {fq(t0 + a)});")
            js.append(f"tl.fromTo('#{sid}-tear', {{x:-40, opacity:1}}, {{x:1940, duration:{b - a}, ease:'power3.inOut'}}, {fq(t0 + a)});")
            SET(f"#{sid}-tear", t0 + b + 0.02, {"opacity": 0})
        SET(f"#{sid}", hold, {"opacity": 0})
    for an in anims:
        an()


# ------------------------------------------------------------------ overlays
def shot_end(sid):
    i = [s[0] for s in SHOTS].index(sid)
    return SHOTS[i + 1][3] if i + 1 < len(SHOTS) else DUR


def kin(id_, cls, text, t, t_out, style=""):
    body.append(f'<div class="{cls}" id="{id_}" style="{style}">{text}</div>')
    A(f"#{id_}", t, {"opacity": 0, "y": 18}, {"opacity": 1, "y": 0}, 0.6)
    TO(f"#{id_}", t_out - 0.45, {"opacity": 0}, 0.4)


def chips(id_, items, t_out, style="", cls="tx"):
    body.append(f'<div class="{cls}" id="{id_}" style="{style}">' + "".join(
        f'<div class="txi" id="{id_}{i}"><span class="txd"></span>{esc(n)}</div>' for i, (n, _) in enumerate(items)) + "</div>")
    for i, (_, t) in enumerate(items):
        A(f"#{id_}{i}", t - 0.1, {"opacity": 0, "x": -24}, {"opacity": 1, "x": 0}, 0.45)
    TO(f"#{id_}", t_out - 0.45, {"opacity": 0}, 0.4)


ERA = ["ABAD KE-19", "1911", "1928", "1950-an", "1958", "1970-an", "HARI INI"]


def overlays():
    # era bar (chronological rail; the active node lights up at each chapter)
    x0, x1, y = 460, 1460, 72
    xs = [round(x0 + (x1 - x0) * i / (len(ERA) - 1)) for i in range(len(ERA))]
    parts = [f'<div class="tlrail" style="left:{x0}px;top:{y}px;width:{x1 - x0}px"></div>',
             f'<div class="tlprog" id="et-prog" style="left:{x0}px;top:{y}px;width:{x1 - x0}px"></div>']
    for i, (lab, x) in enumerate(zip(ERA, xs)):
        parts.append(f'<div class="tlnode" id="et-n{i}" style="left:{x - 8}px;top:{y - 7}px;width:16px;height:16px"></div>')
        parts.append(f'<div class="tllab" id="et-l{i}" style="left:{x - 200}px;top:{y + 18}px;font-size:19px">{lab}</div>')
    body.append('<div class="era" id="et">' + "".join(parts) + "</div>")
    apps = [(T("Seawal abad"), 0), (T("Kemudian pada tahun"), 1), (T("Sekitar tahun 1950-an"), 3), (T("pada tahun 1958"), 4),
            (T("kita masuk ke zaman"), 6)]
    prev = 0.0
    for k, (t, node) in enumerate(apps):
        frac = node / (len(ERA) - 1)
        A("#et", t - 0.1, {"opacity": 0}, {"opacity": 1}, 0.5, "power2.out", ir=(k == 0))
        A("#et-prog", t + 0.2, {"scaleX": prev, "transformOrigin": "0% 50%"}, {"scaleX": frac}, 1.0, "power2.inOut", ir=(k == 0))
        for i in range(len(ERA)):
            cur = i == node
            js.append(f"tl.set('#et-n{i}', {{backgroundColor:'{GOLD if i <= node else 'rgba(244,235,216,.35)'}', scale:{1.4 if cur else 1}}}, {fq(t + 0.2 + (0.6 if cur else 0))});")
            js.append(f"tl.set('#et-l{i}', {{opacity:{1 if cur else 0.45}, color:'{GOLD if cur else CREAM}'}}, {fq(t + 0.2 + (0.6 if cur else 0))});")
        TO("#et", t + 3.6, {"opacity": 0}, 0.5)
        prev = frac

    # 1911 cold open
    t = TT("Bayangkan anda hidup")
    body.append('<div class="yr" id="k-1911a">1911</div>')
    A("#k-1911a", TT("1911.") - 0.1, {"opacity": 0, "scale": 1.2}, {"opacity": 1, "scale": 1}, 0.8)
    TO("#k-1911a", shot_end("k1") - 0.4, {"opacity": 0}, 0.4)
    chips("c-1911", [("Tiada telefon pintar", TT("smartphone")), ("Tiada internet", TT("Tak ada internet")),
                     ("Malaysia belum merdeka", TT("belum merdeka"))], shot_end("s01"))
    chips("c-sym", [("Bercakap seorang diri", TT("bercakap seorang")), ("Mendengar suara", TT("dengar suara")),
                    ("Ketawa sendiri", TT("dia ketawa")), ("Ketakutan · paranoid", TT("jadi ketakutan"))], shot_end("s03"),
          style="left:auto;right:110px")
    chips("c-myth", [("“Kena rasuk?”", TT("kena rasuk")), ("“Kena gangguan?”", TT("kena gangguan")), ("Ditakuti", TT("takut nak dekat"))],
          shot_end("s05"), cls="tx myth")
    kin("k-terhad", "humane", "Pilihan rawatan sangat terhad", TT("pilihan rawatan memang") + 0.2, shot_end("s06"))
    # 19th century
    kin("k-abad", "chap", "ABAD KE-19", TT("Seawal abad") + 0.1, shot_end("s08"))
    kin("k-abad2", "place", "Rekaan semula · kemudahan awal di Tanah Melayu", TT("Seawal abad") + 0.6, shot_end("s08"))
    kin("k-pen", "placebig", "Pulau Pinang", TT("Pulau Pinang") - 0.1, shot_end("s09"))
    kin("k-tai", "placebig", "Taiping, Perak", TT("Taiping") - 0.1, TT("Tapi pada zaman tu") + 1.2)
    chips("c-care", [("Penjagaan", TT("penjagaan,")), ("Keselamatan", TT("keselamatan")), ("Pengawasan", TT("pengawasan"))], shot_end("s11"))
    kin("k-jauh", "humane", "Ditempatkan jauh daripada masyarakat", TT("ditempatkan jauh") + 0.1, shot_end("s12"))
    chips("c-hal", [("Halusinasi", TT("halusinasi")), ("Delusi", TT("dilusi"))], shot_end("e01"), style="left:auto;right:110px")
    kin("k-modern0", "humane", "Belum ada rawatan moden", TT("belum ada rawatan") + 0.2, shot_end("s13"))
    # 1911 Tanjung Rambutan
    t11 = TT("Kemudian pada tahun")
    body.append('<div class="yr" id="k-1911b">1911</div><div class="place2" id="k-tr">Tanjung Rambutan, Perak · zaman pentadbiran British</div>')
    A("#k-1911b", TT("1911", after=t11 - 0.5) - 0.1, {"opacity": 0, "scale": 1.2}, {"opacity": 1, "scale": 1}, 0.8)
    A("#k-tr", TT("Tanjung Rambutan", after=t11) - 0.1, {"opacity": 0, "y": 12}, {"opacity": 1, "y": 0}, 0.6)
    TO("#k-1911b, #k-tr", shot_end("k2") - 0.4, {"opacity": 0}, 0.4)
    kin("k-pent", "humane", "Istilah dalam sistem perubatan & pentadbiran", TT("istilah tersebut") + 0.2, shot_end("s15"))
    kin("k-famous", "humane", "Hospital psikiatri paling terkenal dalam sejarah Malaysia", TT("paling terkenal") - 0.3, shot_end("s17"))
    kin("k-life", "humane", "Kehidupan pesakit pada zaman dulu?", TT("macam mana kehidupan") + 0.2, shot_end("s18"))
    kin("k-world", "placebig", "Di seluruh dunia: pendekatan berasaskan institusi", TT("Di seluruh dunia"), shot_end("e03"), style="font-size:44px")
    kin("k-long", "humane", "Tinggal untuk tempoh yang panjang", TT("tempoh masa yang panjang") - 0.6, shot_end("e04"))
    chips("c-daily", [("Makan", TT("makan,")), ("Mandi", TT("mandi,")), ("Kehidupan harian", TT("menguruskan kehidupan"))], shot_end("s19"))
    kin("k-work", "humane", "Aktiviti rutin & pekerjaan sebagai sebahagian penjagaan", TT("aktiviti rutin"), shot_end("s20"))
    kin("k-diff", "humane", "Amalan berbeza mengikut hospital & zaman", TT("amalan rawatan berbeza") - 0.2, shot_end("s21"))
    kin("k-same", "humane", "Pengalaman setiap pesakit tidak sama", TT("Kita tak boleh anggap") + 0.3, shot_end("s22"))
    # 1950s
    t5 = TT("Sekitar tahun 1950-an")
    body.append('<div class="yr" id="k-1950">1950-an</div><div class="drug" id="k-cpz">CHLORPROMAZINE</div>'
                '<div class="drug2" id="k-cpz2">Antara ubat antipsikotik terawal</div>')
    A("#k-1950", t5 + 0.3, {"opacity": 0, "scale": 1.2}, {"opacity": 1, "scale": 1}, 0.8)
    A("#k-cpz", TT("chlorpromazine") - 0.1, {"opacity": 0, "scale": 1.18}, {"opacity": 1, "scale": 1}, 0.7)
    A("#k-cpz2", TT("chlorpromazine") + 0.4, {"opacity": 0}, {"opacity": 1}, 0.4)
    TO("#k-1950, #k-cpz, #k-cpz2", shot_end("e07") - 0.35, {"opacity": 0}, 0.3)
    kin("k-turn", "humane", "Titik perubahan penting dalam rawatan psikiatri", TT("titik perubahan") - 0.2, shot_end("s23"))
    kin("k-before", "humane", "Sebelum itu: pilihan sangat terhad untuk mengawal psikosis", TT("Sebelum tu doktor") + 0.2, shot_end("s24"))
    chips("c-psy", [("Halusinasi", TT("mengawal halusinasi") + 0.4), ("Delusi", TT("dilusi dan juga")), ("Gangguan pemikiran", TT("gangguan pemikiran"))],
          shot_end("e08"), style="left:auto;right:110px")
    # 1958
    t58 = TT("pada tahun 1958")
    body.append('<div class="yr" id="k-1958">1958</div>')
    A("#k-1958", t58 + 0.4, {"opacity": 0, "scale": 1.2}, {"opacity": 1, "scale": 1}, 0.8)
    TO("#k-1958", shot_end("s26") - 0.35, {"opacity": 0}, 0.3)
    body.append(f"""<div class="l3" id="l3-pg"><div class="l3rule"></div><div class="l3n" style="font-size:52px">HOSPITAL PULAU PINANG</div>
<div class="l3m">1958 · Wad psikiatri pertama di hospital umum</div></div>""")
    A("#l3-pg", TT("wad psikiatri dibuka") + 0.2, {"opacity": 0, "x": -30}, {"opacity": 1, "x": 0}, 0.6)
    TO("#l3-pg", shot_end("s27") - 0.4, {"opacity": 0, "x": -20}, 0.35)
    # modern: myth vs reality
    body.append('<div class="stamp2" id="k-mitos">MITOS · FILEM SERAM</div><div class="real" id="k-real">REALITI · WAD PSIKIATRI HARI INI</div>')
    A("#k-mitos", TT("filem-filem seram") - 0.1, {"opacity": 0, "scale": 2.0, "rotation": -12}, {"opacity": 1, "scale": 1, "rotation": -7}, 0.3, "power4.in")
    TO("#k-mitos", shot_end("s28") - 0.3, {"opacity": 0}, 0.25)
    A("#k-real", TT("kat dalam wad") + 0.1, {"opacity": 0, "y": 14}, {"opacity": 1, "y": 0}, 0.5)
    TO("#k-real", shot_end("k3") - 0.4, {"opacity": 0}, 0.3)
    chips("c-ward", [("Dinilai oleh doktor", TT("dinilai oleh doktor")), ("Dipantau jururawat", TT("dipantau oleh"))], shot_end("k3"),
          style="left:auto;right:110px;top:300px")
    kin("k-meds", "humane", "Ubat diberi mengikut keperluan", TT("diberikan ubat") + 0.1, shot_end("s29"))
    chips("c-mdt", [("Terapi", TT("menjalani terapi")), ("Aktiviti pemulihan", TT("aktiviti pemulihan")), ("Penilaian", TT("penilaian,")),
                    ("Pasukan pelbagai disiplin", TT("multidisciplinary"))], shot_end("s30"))
    # CTA
    kin("k-change", "humane", "Rawatan yang sesuai boleh mengubah kehidupan", TT("boleh mengubah") - 0.3, shot_end("s32"))
    kin("k-help", "humane", "Dapatkan bantuan profesional kesihatan mental", TT("Cepat-cepat dapatkan") - 0.1, shot_end("e09"))
    body.append(f"""<div class="l3" id="l3-dr"><div class="l3rule"></div><div class="l3n" style="font-size:58px">DR. AZREN</div>
<div class="l3m">Klinik Nissa</div><div class="l3chip" id="l3-dr-c" style="opacity:1">Saringan &amp; konsultasi</div></div>""")
    A("#l3-dr", TT("Boleh bawa datang") + 0.2, {"opacity": 0, "x": -30}, {"opacity": 1, "x": 0}, 0.6)
    TO("#l3-dr", shot_end("s33") - 0.4, {"opacity": 0, "x": -20}, 0.35)
    kin("k-cmt", "cmt", "Pernah dimasukkan ke wad psikiatri? Kongsikan pengalaman anda di ruangan komen", TT("kongsikan pengalaman") - 0.6,
        shot_end("k4") + 0.3)

    # honesty tags
    ai = [(s[3], shot_end(s[0])) for s in SHOTS if s[1] in AI_KINDS]
    body.append('<div class="tag" id="tag-ai">Dramatisasi · visual dijana AI</div>')
    on, first = False, True
    for k, (a, b) in enumerate(ai):
        if not on:
            A("#tag-ai", a + 0.3, {"opacity": 0}, {"opacity": 0.6}, 0.4, "power1.out", ir=first)
            first, on = False, True
        nxt = ai[k + 1][0] if k + 1 < len(ai) else None
        if nxt is None or nxt > b + 0.2:
            TO("#tag-ai", b - 0.3, {"opacity": 0}, 0.3, "power1.in")
            on = False


# ------------------------------------------------------------------ subtitles
EMPH_GOLD = {"1911", "1911.", "1928", "1958", "1950-an", "1970-an", "ke-19", "Tanjung", "Rambutan", "Pulau", "Pinang", "Taiping",
             "Federal", "Lunatic", "Asylum", "Central", "Mental", "Hospital", "bahagia", "Ulu", "Kinta", "Azren", "Klinik", "Nissa"}
EMPH_TEAL = {"skizofrenia", "bipolar", "kemurungan", "antipsikotik", "antidepressant", "chlorpromazine", "halusinasi", "dilusi",
             "psikiatri", "bantuan", "terapi", "pemulihan"}
KEEP = {("tanjung", "rambutan"), ("pulau", "pinang"), ("ulu", "kinta"), ("bahagia", "ulu"), ("federal", "lunatic"), ("lunatic", "asylum"),
        ("central", "mental"), ("mental", "hospital"), ("kesihatan", "mental"), ("penyakit", "mental"), ("gangguan", "mental"),
        ("wad", "psikiatri"), ("hospital", "psikiatri"), ("tahun", "1911"), ("tahun", "1958"), ("tahun", "1928"), ("dr", "azren"),
        ("klinik", "nissa"), ("white", "coat"), ("coat", "books"), ("hospital", "umum"), ("rawatan", "psikiatri"), ("ubat", "antipsikotik")}


def split_balanced(ws, maxc=46):
    L = sum(len(w["text"]) + 1 for w in ws) - 1
    if L <= maxc + 4:
        return [ws]
    best = None
    for k in range(2, 7):
        if len(ws) < k:
            break
        if L / k > maxc + 4:
            continue
        for cuts in itertools.combinations(range(1, len(ws)), k - 1):
            parts = [ws[i:j] for i, j in zip((0,) + cuts, cuts + (len(ws),))]
            lens = [sum(len(w["text"]) + 1 for w in p_) - 1 for p_ in parts]
            if max(lens) > maxc + 4:
                continue
            cost = sum((x - L / k) ** 2 for x in lens) + 350 * k
            cost -= sum(400 for p_ in parts[:-1] if p_[-1]["text"].endswith(","))
            cost += sum(900 for p_ in parts if len(p_) == 1)
            cost += sum(5000 for c in cuts if (nk(ws[c - 1]["text"]), nk(ws[c]["text"])) in KEEP)
            cost -= sum(250 for c in cuts if ws[c]["start"] - ws[c - 1]["end"] > 0.18)       # prefer breaking at pauses
            if best is None or cost < best[0]:
                best = (cost, parts)
        if best and k >= 3 and len(ws) > 22:
            break
    return best[1] if best else [ws]


def sentences():
    out, cur = [], []
    for w in WORDS:
        cur.append(w)
        if (re.search(r"[.?!]$", w["text"]) and w["text"] != "Dr.") or (len(cur) > 24 and cur[-1]["text"].endswith(",")):
            out.append(cur)
            cur = []
        elif len(cur) > 1 and w["start"] - cur[-2]["end"] > 0.38 and len(cur) > 6:
            out.append(cur[:-1])
            cur = [w]
    if cur:
        out.append(cur)
    return out


BREAK_BEFORE = {"dan", "tapi", "kalau", "sekarang", "kita", "nama", "untuk", "ada", "di", "pada", "sebagai", "mungkin", "tempoh", "benda",
                "sama", "ramai", "kat", "yang"}


def prechunk(ws, maxc=92):
    """Greedy chunks of <= maxc chars, cut before a conjunction/preposition when possible."""
    out, cur = [], []
    for w in ws:
        if cur and sum(len(x["text"]) + 1 for x in cur) + len(w["text"]) > maxc:
            # back off to the last good break point in the second half of the chunk
            cut = next((i for i in range(len(cur) - 1, len(cur) // 2, -1) if nk(cur[i]["text"]) in BREAK_BEFORE
                        or cur[i - 1]["text"].endswith(",")), len(cur))
            out.append(cur[:cut])
            cur = cur[cut:]
        cur.append(w)
    if cur:
        out.append(cur)
    return out


def subtitles():
    segs = []
    for s in sentences():
        for c in prechunk(s):
            segs += split_balanced(c)
    for k, s in enumerate(segs):
        a = s[0]["start"] + OFF - 0.08
        b = s[-1]["end"] + OFF + 0.35
        if k + 1 < len(segs):
            b = min(b, segs[k + 1][0]["start"] + OFF - 0.1)
        txt = []
        for w in s:
            core = re.sub(r"[^\w-]", "", w["text"])
            cls = "g" if core in EMPH_GOLD or core.rstrip(".") in EMPH_GOLD else ("t" if core.lower() in EMPH_TEAL else "")
            word = esc(w["text"].rstrip(".,:") if w is s[-1] and not w["text"].endswith("?") else w["text"])
            if w is s[0] and (k == 0 or re.search(r"[.?!]$", segs[k - 1][-1]["text"])):
                word = word[0].upper() + word[1:]
            txt.append(f'<span class="{cls}">{word}</span>' if cls else word)
        body.append(f'<div class="sub" id="sub{k}"><span class="subin">{" ".join(txt)}</span></div>')
        A(f"#sub{k}", a, {"opacity": 0, "y": 6}, {"opacity": 1, "y": 0}, 0.14, "power2.out")
        TO(f"#sub{k}", b - 0.1, {"opacity": 0}, 0.1, "power1.in")
        SET(f"#sub{k}", b, {"opacity": 0})
    return segs


CSS = (Path(__file__).parent / "style.css").read_text()


def main():
    build_shots()
    overlays()
    body.append('<div class="vig"></div><div class="grain" id="grain"></div>')
    js.append(f"tl.fromTo('#grain', {{backgroundPosition:'0px 0px'}}, {{backgroundPosition:'-9300px -6100px', duration:{DUR}, ease:'steps({int(DUR * 12)})'}}, 0);")
    segs = subtitles()
    page = f"""<!doctype html>
<html lang="ms"><head><meta charset="utf-8" />
<style>{CSS}</style></head>
<body>
<div id="stage" data-composition-id="wad-psikiatri" data-start="0" data-duration="{DUR}" data-fps="{FPS}" data-width="{W}" data-height="{H}">
  {chr(10).join(body)}
  <audio id="mix" src="audio/mix.wav" data-start="0" data-duration="{DUR}" data-track-index="10" data-volume="1"></audio>
  <script src="vendor/gsap.min.js"></script>
  <script>
  (function () {{
    const tl = window.gsap.timeline({{ paused: true }});
    {(chr(10) + '    ').join(js)}
    window.__timelines["wad-psikiatri"] = tl;
  }})();
  </script>
</div>
</body></html>
"""
    (P / "index.html").write_text(page)
    srt = []
    for k, s in enumerate(segs):
        a = s[0]["start"] + OFF - 0.08
        b = s[-1]["end"] + OFF + 0.35
        if k + 1 < len(segs):
            b = min(b, segs[k + 1][0]["start"] + OFF - 0.1)
        ts = lambda t: f"{int(t // 3600):02d}:{int(t // 60 % 60):02d}:{int(t % 60):02d},{int(round(t * 1000)) % 1000:03d}"
        srt.append(f"{k + 1}\n{ts(a)} --> {ts(b)}\n{' '.join(w['text'] for w in s)}\n")
    (D.parent / "sejarah-wad-psikiatri_ms.srt").write_text("\n".join(srt))
    (D / "timeline.json").write_text(json.dumps({"fps": FPS, "duration": DUR, "voice_offset": OFF,
                                                 "shots": [{"id": s[0], "kind": s[1], "src": s[2], "t0": s[3], "in": s[4]} for s in SHOTS]}, indent=1))
    print(f"{len(SHOTS)} shots, {len(segs)} subtitle lines, {len(js)} timeline statements, duration {DUR:.2f}s")


if __name__ == "__main__":
    main()
