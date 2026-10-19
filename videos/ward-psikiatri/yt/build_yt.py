"""16:9 YouTube version of 'Keadaan Dalam Wad Psikiatri' (1920x1080 @ 30).

The vertical talking head is matted (speaker_alpha.webm, transparent background), so it can
stand on any background and move around the frame:
  L  speaker left,  graphics panel right
  R  speaker right, graphics panel left
  C  speaker centre (slightly smaller), graphics on both sides
The layout alternates through the video; the speaker glides between positions.
Each chapter gets its own background scene (studio teal, the horror corridor during the myths,
a bright ward, warm daylight for recovery...). The "TIDAK" hero sits between the background
and the speaker, so it reads as behind his head with no extra matte pass.
Full-screen inserts (Higgsfield Seedance B-roll videos + motion-graphic cards) cover everything
except the captions, which stay on top (one karaoke line, bottom band).

All times are anchored to phrases in edit/cut_words.json.
Outputs public/index.html.  Run: ../../../.venv/bin/python build_yt.py
"""

import difflib
import html
import json
import re
from pathlib import Path

Y = Path(__file__).parent
P = Y / "public"
WORDS = json.loads((Y.parent / "edit" / "cut_words.json").read_text())
CAPW = json.loads((Y.parent / "captions" / "transcript.json").read_text())["words"]
FPS, W, H = 30, 1920, 1080
DUR = 142.833
import os
SPEAKER = os.environ.get("SPEAKER", "speaker_alpha.webm")   # SPEAKER=speaker_preview.mp4 for layout checks before the matte exists
LEAD = 0.12
TEAL, DEEP, MINT, CREAM, INK, RED, MUTED = "#0E5E6F", "#08323C", "#5EEAD4", "#FFF8EE", "#0B1F2A", "#E5484D", "#6B7C85"


def T(phrase: str, after: float = 0.0, end: bool = False) -> float:
    toks = phrase.split()
    for i in range(len(WORDS) - len(toks) + 1):
        if WORDS[i]["start"] >= after and [w["text"] for w in WORDS[i:i + len(toks)]] == toks:
            return WORDS[i + len(toks) - 1]["end"] if end else WORDS[i]["start"]
    raise KeyError(phrase)


def fq(t: float) -> float:
    return round(round(t * FPS) / FPS, 4)


# ---------------------------------------------------------------- icons (white strokes, 48 grid)
ICON = {
    "rain": '<path d="M15 27a8 8 0 0 1 1.5-15.8A10 10 0 0 1 35 14a7 7 0 0 1-1 13.9H15z"/><path d="M17 32l-2 6M25 32l-2 6M33 32l-2 6"/>',
    "pulse": '<path d="M5 25h9l4-10 6 20 5-14 3 4h11"/>',
    "wave": '<path d="M5 24c4-12 9-12 13 0s9 12 13 0 9-12 12-4"/>',
    "scatter": '<circle cx="24" cy="24" r="14" stroke-dasharray="5 5"/><circle cx="24" cy="24" r="3" fill="#fff"/>',
    "bolt": '<path d="M27 5L12 27h11l-3 16 16-23H25z"/>',
    "steth": '<path d="M12 6v12a8 8 0 0 0 16 0V6"/><path d="M20 26v6a8 8 0 0 0 16 0v-4"/><circle cx="36" cy="25" r="3"/>',
    "cross": '<rect x="8" y="8" width="32" height="32" rx="8"/><path d="M24 16v16M16 24h16"/>',
    "brain": '<path d="M18 10a6 6 0 0 0-6 6 6 6 0 0 0-4 10 6 6 0 0 0 6 8 6 6 0 0 0 10 2V12a6 6 0 0 0-6-2z"/><path d="M30 10a6 6 0 0 1 6 6 6 6 0 0 1 4 10 6 6 0 0 1-6 8 6 6 0 0 1-10 2"/>',
    "chat": '<path d="M8 12h22v14H16l-6 5v-5H8z"/><path d="M34 18h6v14h-2v5l-6-5H22v-2"/>',
    "puzzle": '<path d="M10 14h8a4 4 0 1 1 8 0h8v8a4 4 0 1 0 0 8v8H26a4 4 0 1 0-8 0h-8V30a4 4 0 1 1 0-8z"/>',
    "check": '<path d="M12 25l8 8 16-17"/>',
    "x": '<path d="M14 14l20 20M34 14L14 34"/>',
    "pill": '<rect x="6" y="17" width="36" height="14" rx="7" transform="rotate(-35 24 24)"/><path d="M19 17l10 14"/>',
    "eye": '<path d="M4 24s7-12 20-12 20 12 20 12-7 12-20 12S4 24 4 24z"/><circle cx="24" cy="24" r="5"/>',
    "shield": '<path d="M24 5l15 6v11c0 10-7 17-15 21C16 39 9 32 9 22V11z"/><path d="M17 23l5 5 9-10"/>',
    "meal": '<path d="M14 6v14a4 4 0 0 0 8 0V6M18 6v36M32 6c-4 0-6 6-6 12s2 8 6 8v16"/>',
    "home": '<path d="M7 22L24 8l17 14"/><path d="M12 19v21h24V19"/><path d="M20 40V28h8v12"/>',
    "talk": '<path d="M6 10h36v22H20l-10 8v-8H6z"/><path d="M14 19h20M14 25h12"/>',
}


def icon(name, cls="ico"):
    return (f'<svg viewBox="0 0 48 48" class="{cls}"><g stroke="#fff" stroke-width="3.4" stroke-linecap="round" '
            f'stroke-linejoin="round" fill="none">{ICON[name]}</g></svg>')


def chip(text, color=TEAL, fg="#fff"):
    return f'<span class="chip" style="background:{color};color:{fg}">{html.escape(text)}</span>'


def row(ic, text, color=TEAL, cls="row"):
    return f'<div class="{cls}"><span class="disc" style="background:{color}">{icon(ic)}</span><span>{text}</span></div>'


# ---------------------------------------------------------------- timeline spec
B = {}  # named anchor times
B["hook_broll"] = fq(T("macam dalam filem filem") - 0.08)
B["matte_lo"] = 7.87
B["ext"] = fq(T("jauh berbeza") - 0.1)
B["myth"] = fq(T("ramai orang bayangkan") - 0.15)
B["m1"] = fq(T("tapi tidak sebenarnya") - 0.1)
B["ward"] = fq(T("adalah salah satu wad") - 0.1)
B["team"] = fq(T("di hospital", end=True) + 0.08)
B["apa"] = fq(T("apa pesakit buat") - 0.25)
B["consult"] = fq(T("jumpa dengan doktor") - 0.12)
B["rutin"] = fq(T("mengikut keperluan", end=True) + 0.1)
B["therapy"] = fq(T("aktiviti terapi") - 0.1)
B["terapi"] = fq(T("senaman ringan", end=True) + 0.08)
B["tujuan"] = fq(T("tujuan utama") - 0.1)
B["q2"] = fq(T("datang pula soalan") - 0.1)
B["q2c"] = fq(T("pesakit dalam wad psikiatri ini") - 0.05)
B["keadaan"] = fq(T("mereka mungkin mengalami") - 0.12)
B["quiet"] = fq(T("ramai yang pendiam") - 0.1)
B["q3"] = fq(T("ada juga yang tanya") - 0.1)
B["restraint"] = fq(T("yang paling biasalah", end=True) + 0.1)
B["ladder"] = fq(T("pertama berisiko") - 0.3)
B["stabil"] = fq(T("apabila pesakit sudah stabil") - 0.12)
B["bukan"] = fq(T("yang penting masuk") - 0.12)
B["pulih"] = fq(T("selepas beberapa hari") - 0.1)
B["return"] = fq(T("mereka kembali bekerja") - 0.06)
B["hukum"] = fq(T("seperti biasa", end=True) + 0.1)
B["safe"] = fq(T("tempat yang selamat") - 0.1)
B["selamat"] = fq(T("berehat distabilkan", end=True) + 0.08)
B["support"] = fq(T("jadi kalau anda") - 0.1)
B["cta"] = fq(T("kesihatan mental jangan", end=True) - 0.25)
B["rawatan"] = fq(T("kita bincang") - 0.12)
B["end"] = fq(T("apa-apa soalan") - 0.12) if any(w["text"] == "apa-apa" for w in WORDS) else fq(T("soalan minta") - 0.25)

# full-screen inserts: (id, kind, start, end, src/body)
FS = [
    ("f-asylum", "broll", B["hook_broll"], B["matte_lo"], "v01_asylum"),
    ("f-ext", "broll", B["ext"], B["myth"], "v02_hospital"),
    ("f-filem", "mg", B["m1"], B["ward"] + 0.3, None),
    ("f-ward", "broll", B["ward"], B["team"], "v03_ward"),
    ("f-consult", "broll", B["consult"], B["rutin"], "v04_consult"),
    ("f-therapy", "broll", B["therapy"], B["terapi"], "v06_therapy"),
    ("f-tujuan", "mg", B["tujuan"], B["q2"] + 0.3, None),
    ("f-q2", "mg", B["q2"], B["q2c"], None),
    ("f-quiet", "broll", B["quiet"], B["q3"] + 0.3, "v07_quiet"),
    ("f-q3", "mg", B["q3"], B["restraint"], None),
    ("f-pulih", "mg", B["pulih"], B["return"] + 0.3, None),
    ("f-return", "broll", B["return"], B["hukum"], "v08_return"),
    ("f-safe", "broll", B["safe"], B["selamat"], "v09_saferoom"),
    ("f-support", "broll", B["support"], B["cta"], "v10_support"),
]

# speaker layout keyframes (layout holds until the next one; FS inserts cover it meanwhile)
LAYOUT = [(0, "C"), (B["myth"], "L"), (B["team"], "R"), (B["apa"], "L"), (B["terapi"], "R"),
          (B["q2c"], "C"), (B["keadaan"], "L"), (B["restraint"], "R"), (B["ladder"], "C"),
          (B["stabil"], "L"), (B["bukan"], "R"), (B["hukum"], "L"), (B["cta"], "C"),
          (B["rawatan"], "R"), (B["end"], "C")]

# background scenes
SCENES = [(0, "studio"), (B["myth"], "asylum"), (B["team"], "ward"), (B["q2c"], "studio2"),
          (B["restraint"], "deep"), (B["bukan"], "return"), (B["selamat"], "saferoom")]

# ---------------------------------------------------------------- panels
# each: id, start, end, slots {side: html}, anims [(selector, t, kind)]
PANELS = []


def panel(pid, start, end, slots, anims):
    PANELS.append({"id": pid, "start": fq(start), "end": fq(end), "slots": slots, "anims": anims})


panel("p-hook", 0, B["hook_broll"] + 0.3, {
    "left": f'{chip("Soalan pesakit")}<div class="title" id="ph-a">Macam mana keadaan dalam</div>',
    "right": f'<div class="title xl teal" id="ph-b">WAD<br/>PSIKIATRI?</div><div class="sub" id="ph-c">Seram macam dalam filem?</div>'},
    [("#ph-c", T("dalam filem filem") - LEAD, "slide")])

s = B["myth"]
panel("p-mitos", s, B["m1"] + 0.3, {"main": f'''
    {chip("Mitos", RED)}<div class="label" id="pm-l">Apa orang bayangkan</div>
    <div class="row big" id="pm-1"><span class="disc" style="background:{MUTED}">{icon("eye")}</span><span class="strike">Gelap &amp; menakutkan</span></div>
    <div class="row big" id="pm-2"><span class="disc" style="background:{MUTED}">{icon("bolt")}</span><span class="strike">Pesakit meracau-racau</span></div>
    <div class="row big" id="pm-3"><span class="disc" style="background:{MUTED}">{icon("x")}</span><span class="strike">Diikat sepanjang masa</span></div>'''},
    [("#pm-l", T("ramai orang bayangkan"), "fade"), ("#pm-1", T("gelap") - LEAD, "slide"),
     ("#pm-2", T("meracau") - LEAD, "slide"), ("#pm-3", T("kena ikat sepanjang") - LEAD, "slide"),
     ("#pm-1 .strike", T("tapi tidak") - 0.25, "strike"), ("#pm-2 .strike", T("tapi tidak") - 0.15, "strike"),
     ("#pm-3 .strike", T("tapi tidak") - 0.05, "strike")])

s = B["team"]
roles = [("steth", "Doktor psikiatri", "doktor psikiatri jururawat"), ("cross", "Jururawat terlatih", "jururawat terlatih"),
         ("brain", "Ahli psikologi", "ahli psikologi"), ("chat", "Kaunselor", "kaunselor"),
         ("puzzle", "Jurupulih cara kerja", "terapi jurupulih")]
tiles = "".join(f'<div class="tile" id="pt-{i}"><span class="disc lg">{icon(ic)}</span><span>{t}</span></div>'
                for i, (ic, t, _) in enumerate(roles))
panel("p-team", s, B["apa"] + 0.3, {"main": f'''
    {chip("Realiti di Malaysia")}<div class="title">Satu pasukan pakar</div>
    <div class="tiles">{tiles}<div class="tile more" id="pt-5"><span>+ lain-lain lagi</span></div></div>'''},
    [(f"#pt-{i}", T(w, after=s) - LEAD, "pop") for i, (_, _, w) in enumerate(roles)]
    + [("#pt-5", T("lain-lain lagi", after=s) - LEAD if any(x["text"] == "lain-lain" for x in WORDS) else T("lain lain lagi", after=s) - LEAD, "pop")])

s = B["apa"]
panel("p-apa", s, B["consult"] + 0.3, {"main": f'''
    {chip("Rutin harian")}<div class="title xl" id="pa-t">Apa pesakit buat<br/>dalam wad?</div>'''},
    [("#pa-t", T("apa pesakit buat") - LEAD, "slide")])

s = B["rutin"]
panel("p-rutin", s, B["therapy"] + 0.3, {"main": f'''
    {chip("Setiap hari")}<div class="medslot" id="pr-med">MEDVIDEO</div>
    {row("steth", "Jumpa doktor setiap hari")}
    <div id="pr-2">{row("pill", "Ambil ubat ikut jadual")}</div>
    <div id="pr-3">{row("eye", "Pemerhatian rapi")}</div>
    <div id="pr-4">{row("shield", "Keselamatan dipantau")}</div>'''},
    [("#pr-2", T("mengambil ubat") - LEAD, "slide"), ("#pr-3", T("pemerhatian rapi") - LEAD, "slide"),
     ("#pr-4", T("keselamatan akan") - LEAD, "slide")])

s = B["terapi"]
panel("p-terapi", s, B["tujuan"] + 0.3, {"main": f'''
    {chip("Aktiviti terapi")}
    <div class="pills"><span class="pill2">Terapi cara kerja</span><span class="pill2">Senaman ringan</span>
      <span class="pill2" id="pp-3">Sesi kaunseling</span></div>
    <div class="sub" id="pp-s">Ikut hospital &amp; keadaan pesakit</div>
    <div class="hr"></div>
    <div id="pp-m">{row("meal", "Makan &amp; rehat ikut jadual", RED)}</div>'''},
    [("#pp-3", T("sesi kaunseling") - LEAD, "pop"), ("#pp-s", T("bergantung pada") - LEAD, "fade"),
     ("#pp-m", T("makan dan rehat") - LEAD, "slide")])

s = B["q2c"]
panel("p-q2c", s, B["keadaan"] + 0.3, {
    "left": f'{chip("Soalan #2")}<div class="title">Semua pesakit agresif?</div>',
    "right": f'<div class="stamp teal" id="pq-s">TIDAK</div>'}, [])

s = B["keadaan"]
conds = [("rain", "Kemurungan teruk", "kemurungan"), ("pulse", "Anxiety melampau", "anxiety"),
         ("wave", "Bipolar tidak stabil", "bipolar"), ("scatter", "Skizofrenia tidak stabil", "skizofrenia"),
         ("bolt", "Krisis emosi", "krisis emosi")]
crow = "".join(f'<div id="pk-{i}">{row(ic, t)}</div>' for i, (ic, t, _) in enumerate(conds))
panel("p-keadaan", s, B["quiet"] + 0.3, {"main": f'''
    {chip("Mereka mungkin mengalami")}{crow}
    <div class="sub" id="pk-s">— perlukan pemantauan, bukan hukuman</div>'''},
    [(f"#pk-{i}", T(w, after=s) - LEAD, "slide") for i, (_, _, w) in enumerate(conds)]
    + [("#pk-s", T("yang memerlukan pemantauan") - LEAD, "fade")])

s = B["restraint"]
panel("p-restraint", s, B["ladder"] + 0.3, {"main": f'''
    {chip("Physical restraint", RED)}
    <div class="title xl" id="px-a">Bukan rutin</div>
    <div class="title xl red" id="px-b">Langkah terakhir</div>'''},
    [("#px-a", T("bukanlah rutin") - LEAD, "slide"), ("#px-b", T("langkah terakhir") - LEAD, "pop")])

s = B["ladder"]
panel("p-ladder", s, B["stabil"] + 0.3, {
    "left": f'''{chip("Hanya bila", RED)}
      <div class="rung" id="pl-1"><span class="num">1</span><span>Berisiko cederakan diri sendiri</span></div>
      <div class="rung" id="pl-2"><span class="num">2</span><span>Berisiko cederakan orang lain</span></div>''',
    "right": f'''<div class="rung" id="pl-3"><span class="num">3</span><span>Cara lain tidak berjaya menenangkan</span></div>
      <div class="lastbox" id="pl-4">Baru restraint<br/><b>— langkah terakhir</b></div>'''},
    [("#pl-1", T("pertama berisiko") - LEAD, "slide"), ("#pl-2", T("kedua berisiko") - LEAD, "slide"),
     ("#pl-3", T("semua cara lain") - LEAD, "slide"), ("#pl-4", T("tidak berjaya", after=s) - LEAD, "stamp")])

s = B["stabil"]
panel("p-stabil", s, B["bukan"] + 0.3, {"main": f'''
    {chip("Bila pesakit stabil")}
    <div class="title xl" id="ps-t">Dihentikan <span class="teal">secepat mungkin</span></div>
    <div id="ps-s">{row("shield", "Ikut prosedur &amp; pemantauan ketat")}</div>'''},
    [("#ps-t", T("akan dihentikan") - LEAD, "slide"), ("#ps-s", T("ikut prosedur") - LEAD, "slide")])

s = B["bukan"]
panel("p-bukan", s, B["pulih"] + 0.3, {"main": f'''
    {chip("Masuk wad psikiatri")}
    <div id="pb-1">{row("x", "Bukan bermaksud hidup berakhir", RED, "row big")}</div>
    <div id="pb-2">{row("x", "Bukan bermaksud anda gila", RED, "row big")}</div>
    <div class="title teal" id="pb-3">Ramai pesakit pulih &amp; keluar semula</div>'''},
    [("#pb-1", T("bukan bermaksud hidup") - LEAD, "slide"), ("#pb-2", T("bukan bermaksud anda") - LEAD, "slide"),
     ("#pb-3", T("ramai pesakit masuk") - LEAD, "fade")])

s = B["hukum"]
panel("p-hukum", s, B["safe"] + 0.3, {"main": f'''
    {chip("Wad psikiatri")}
    <div class="title xl muted"><span class="strike" id="pu-s">Tempat hukuman</span></div>'''},
    [("#pu-s", T("bukan tempat hukum") + 0.3, "strike")])

s = B["selamat"]
panel("p-selamat", s, B["support"] + 0.3, {"main": f'''
    <div class="title xxl teal">TEMPAT<br/>SELAMAT</div>
    <div class="steps"><span class="step">Berehat</span><span class="sep">·</span><span class="step">Distabilkan</span>
      <span class="sep">·</span><span class="step hi" id="pl-h">Mula sembuh</span></div>'''},
    [("#pl-h", T("memulakan proses") - LEAD, "pop")])

s = B["cta"]
panel("p-cta", s, B["rawatan"] + 0.3, {
    "left": f'{chip("Kesihatan mental")}<div class="title" id="pc-a">Jangan takut <span class="teal">dapatkan bantuan</span></div>',
    "right": f'{chip("Di klinik saya")}<div class="title" id="pc-b">Saringan &amp; konsultasi</div>'},
    [("#pc-a", T("jangan takut untuk") - LEAD, "slide"), ("#pc-b", T("boleh datang buat") - LEAD, "slide")])

s = B["rawatan"]
panel("p-rawatan", s, B["end"] + 0.3, {"main": f'''
    {chip("Kita bincang dahulu")}
    <div class="title xl">Pilihan rawatan <span class="teal">paling sesuai</span> untuk anda</div>'''}, [])

s = B["end"]
panel("p-end", s, DUR, {
    "left": f'<div class="title xxl teal">Ada<br/>soalan?</div>',
    "right": f'<div class="title">Komen di bawah</div><div class="arrowdown">↓</div><div class="subpill">Subscribe untuk info kesihatan mental</div>'},
    [])

# ---------------------------------------------------------------- full-screen motion graphics bodies
MG = {}
s = B["m1"]
MG["f-filem"] = (f'''
  <div class="hh left"><img src="broll/asylum_still.jpg" class="hh-img grim"/><div class="hh-shade"></div>
    <div class="fs-chip red" style="left:90px;top:110px">Dalam filem</div>
    <div class="fs-stamp" id="fm-x">TIDAK BENAR</div></div>
  <div class="hh right"><div class="fs-chip" style="left:90px;top:110px" id="fm-c">Realiti</div>
    <div class="fs-title" style="left:90px;top:200px" id="fm-t">Wad psikiatri<br/><span class="mint">di Malaysia</span></div>
    <div class="fs-sub" style="left:90px;top:450px" id="fm-s">= wad di hospital biasa</div></div>
  <div class="vseam" id="fm-seam"></div>''',
    [("#fm-seam", s, "growy"), ("#fm-x", T("tidak", after=s) - LEAD, "stamp"), ("#fm-c", T("di malaysia", after=s) - 0.3, "pop"),
     ("#fm-t", T("di malaysia", after=s) - LEAD, "rise"), ("#fm-s", T("wad psikiatri adalah", after=s) - LEAD, "rise")])

s = B["tujuan"]
MG["f-tujuan"] = (f'''
  <div class="center-col">
    <div class="fs-chip static" id="ft-c">Tujuan utama</div>
    <div class="big-line" id="ft-a"><span class="bdisc" style="background:{MINT}">{icon("check", "ico-xl")}</span><span class="mint">MENSTABILKAN</span></div>
    <div class="big-line muted2" id="ft-b"><span class="bdisc" style="background:{RED}">{icon("x", "ico-xl")}</span><span class="strike2" id="ft-s">bukan menghukum</span></div>
  </div>''',
    [("#ft-c", s + 0.05, "pop"), ("#ft-a", T("menstabilkan") - LEAD, "rise"), ("#ft-b", T("bukan untuk menghukum") - LEAD, "rise"),
     ("#ft-s", T("menghukum") + 0.3, "strike2")])

for key, num, q, stamp, word in (("f-q2", "Soalan #2", "Adakah semua pesakit dalam wad <span class='mint'>agresif?</span>", "TIDAK", "jawapannya tidak"),
                                 ("f-q3", "Soalan #3", "Kenapa ada pesakit sampai <span class='mint'>kena ikat?</span>", "SALAH FAHAM", "salah faham")):
    s = B["q2" if key == "f-q2" else "q3"]
    k = key[2:]
    MG[key] = (f'''
  <div class="chap-num" id="{k}-n">{num}</div>
  <div class="chap-q" id="{k}-q">{q}</div>
  <div class="fs-stamp chap" id="{k}-s">{stamp}</div>''',
        [(f"#{k}-n", s + 0.1, "rise"), (f"#{k}-q", s + 0.35, "rise"),
         (f"#{k}-s", T(word, after=s) + (0.25 if stamp == "TIDAK" else 0.0) - LEAD, "stamp")])

s = B["pulih"]
nodes = [("Beberapa hari", "beberapa hari"), ("Beberapa minggu", "beberapa minggu"),
         ("Keluar semula", "keluar semula"), ("Sambung rawatan", "sambung rawatan")]
nh = "".join(f'<div class="hnode{" hi" if i == 2 else ""}" id="fp-{i}" style="left:{200 + i * 460}px"><span class="hdot"></span>'
             f'<span class="hlabel">{t}</span></div>' for i, (t, _) in enumerate(nodes))
MG["f-pulih"] = (f'''
  <div class="fs-chip" style="left:120px;top:110px" id="fp-c">Realiti</div>
  <div class="fs-title" style="left:120px;top:190px" id="fp-t">Masuk wad <span class="mint">bukan</span> pengakhiran</div>
  <svg class="hrail" viewBox="0 0 1500 20" style="left:230px;top:546px;width:1500px;height:20px">
    <path id="fp-rail" d="M10 10H1490" stroke="{MINT}" stroke-width="8" stroke-linecap="round" fill="none"/></svg>
  {nh}''',
    [("#fp-c", s, "pop"), ("#fp-t", s + 0.05, "rise"), ("#fp-rail", s + 0.15, ("draw", T("sambung rawatan", after=s) - s))]
    + [(f"#fp-{i}", T(w, after=s) - LEAD, "rise") for i, (_, w) in enumerate(nodes)])

# ---------------------------------------------------------------- captions (one line, karaoke)
HERO = (8.6, 10.4)          # caption-free: the hero lockup says it


def punct_marks():
    lv3 = [w["text"] for seg in json.loads((Y.parent / "captions_src" / "large_v3_v4.json").read_text()) for w in seg["words"]]
    norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())
    sm = difflib.SequenceMatcher(a=[norm(w["text"]) for w in CAPW], b=[norm(t) for t in lv3], autojunk=False)
    marks = {}
    for i, j, n in sm.get_matching_blocks():
        for k in range(n):
            e = lv3[j + k].rstrip()[-1:]
            if e in ".?!,":
                marks[i + k] = e
    return marks


def cap_lines():
    marks = punct_marks()
    lines, cur = [], []
    for i, w in enumerate(CAPW):
        if cur:
            gap = w["start"] - cur[-1][1]["end"]
            chars = len(" ".join(x["text"] for _, x in cur + [(i, w)]))
            if chars > 30 or len(cur) >= 5 or gap >= 0.3 or cur[-1][0] in marks:
                lines.append(cur)
                cur = []
        cur.append((i, w))
    lines.append(cur)
    out = []
    for n, ln in enumerate(lines):
        t0 = ln[0][1]["start"] - 0.08
        t1 = min(lines[n + 1][0][1]["start"] - 0.04, ln[-1][1]["end"] + 0.7) if n + 1 < len(lines) else ln[-1][1]["end"] + 0.8
        if t0 < HERO[1] and t1 > HERO[0]:
            continue
        out.append((fq(max(t0, 0)), fq(t1), [w for _, w in ln]))
    return out


# ---------------------------------------------------------------- geometry
VID_W, VID_H, VID_TOP = 900, 1600, -430
FACE_X = 486              # face centre inside the 900px-wide video
POS = {"C": (0, 0.84), "L": (-430, 1.0), "R": (430, 1.0)}       # x shift of the face from frame centre, scale
SLOT = {"L": {"main": (1000, 860)}, "R": {"main": (80, 860)}, "C": {"left": (40, 540), "right": (1340, 540)}}


SPLIT_F = 2790   # the matte was produced in two runs: frames 0-2789 and 2790-end


def speaker_clips():
    if SPEAKER != "speaker_alpha.webm":       # single preview source
        return (f'<video id="spkv" class="clip spkv" src="{SPEAKER}" muted playsinline data-start="0" '
                f'data-duration="{DUR}" data-track-index="1"></video>')
    t = round(SPLIT_F / FPS, 4)
    return (f'<video id="spkv" class="clip spkv" src="speaker_a.webm" muted playsinline data-start="0" data-duration="{t}" data-track-index="1"></video>'
            f'<video id="spkv2" class="clip spkv" src="speaker_b.webm" muted playsinline data-start="{t}" '
            f'data-duration="{round(DUR - t, 4)}" data-track-index="2"></video>')


def layout_at(t):
    cur = LAYOUT[0][1]
    for t0, l in LAYOUT:
        if t0 <= t + 1e-6:
            cur = l
    return cur


# ---------------------------------------------------------------- html / js
def build():
    js, body = [], []
    # background scenes
    scene_html = {
        "studio": f'<div class="scene" id="sc-studio" style="background:radial-gradient(120% 90% at 30% 20%, {TEAL} 0%, {DEEP} 60%, #041920 100%)">'
                  f'<div class="blob" id="blob1"></div><div class="blob b2" id="blob2"></div></div>',
        "studio2": f'<div class="scene" id="sc-studio2" style="background:radial-gradient(110% 90% at 75% 15%, #11707F 0%, {DEEP} 58%, #031419 100%)">'
                   f'<div class="grid"></div></div>',
        "deep": f'<div class="scene" id="sc-deep" style="background:radial-gradient(90% 80% at 50% 30%, #2A1F2B 0%, #0D1A21 60%, #05090C 100%)">'
                f'<div class="redglow"></div></div>',
        "asylum": '<div class="scene" id="sc-asylum"><img class="bgimg" src="bg/asylum.jpg"/><div class="vign"></div></div>',
        "ward": '<div class="scene" id="sc-ward"><img class="bgimg" src="bg/ward.jpg"/><div class="wash"></div></div>',
        "return": '<div class="scene" id="sc-return"><img class="bgimg" src="bg/return.jpg"/><div class="wash warm"></div></div>',
        "saferoom": '<div class="scene" id="sc-saferoom"><img class="bgimg" src="bg/saferoom.jpg"/><div class="wash"></div></div>',
    }
    for _, sc in SCENES:
        body.append(scene_html[sc])
    for n, (t0, sc) in enumerate(SCENES):
        t1 = SCENES[n + 1][0] if n + 1 < len(SCENES) else DUR
        if n == 0:
            js.append(f"tl.set('#sc-{sc}', {{opacity:1}}, 0);")
        else:
            js.append(f"tl.fromTo('#sc-{sc}', {{opacity:0}}, {{opacity:1, duration:0.7, ease:'power2.inOut'}}, {fq(t0 - 0.35)});")
            js.append(f"tl.set('#sc-{SCENES[n - 1][1]}', {{opacity:0}}, {fq(t0 + 0.4)});")
        if sc in ("asylum", "ward", "return", "saferoom"):
            js.append(f"tl.fromTo('#sc-{sc} .bgimg', {{scale:1.04}}, {{scale:1.14, duration:{round(t1 - t0 + 0.8, 2)}, ease:'sine.inOut'}}, {fq(max(0, t0 - 0.4))});")
    js.append("tl.fromTo('#blob1', {x:-80, y:0}, {x:260, y:120, duration:14, ease:'sine.inOut'}, 0);")
    js.append("tl.fromTo('#blob2', {x:120, y:60}, {x:-220, y:-80, duration:14, ease:'sine.inOut'}, 0);")

    # hero lockup behind the speaker
    t_tidak = T("sebenarnya tidak") + 0.0
    t_hero = T("tidak", after=t_tidak + 0.05)
    body.append('<div id="hero"><div id="hero-k">SEBENARNYA,</div><div id="hero-w">TIDAK</div></div>')
    js.append(f"tl.fromTo('#hero-k', {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.3, ease:'power3.out'}}, {fq(t_tidak - 0.1)});")
    js.append(f"tl.fromTo('#hero-w', {{opacity:0, scale:1.6}}, {{opacity:1, scale:1, duration:0.32, ease:'power4.out'}}, {fq(t_hero - 0.08)});")
    js.append(f"tl.to('#hero', {{opacity:0, duration:0.3, ease:'power2.in'}}, {fq(HERO[1] - 0.15)});")

    # speaker
    body.append(f'''<div id="spk"><div id="spkmove"><div id="spot"></div>
      {speaker_clips()}
    </div></div>''')
    x0, s0 = POS[LAYOUT[0][1]]
    js.append(f"tl.set('#spkmove', {{x:{x0}, scale:{s0}}}, 0);")
    for t0, l in LAYOUT[1:]:
        x, sc = POS[l]
        js.append(f"tl.to('#spkmove', {{x:{x}, scale:{sc}, duration:0.7, ease:'power3.inOut'}}, {fq(t0 - 0.35)});")

    # panels
    for p in PANELS:
        lay = layout_at(p["start"] + 0.05)
        slots = SLOT[lay]
        inner = []
        for side, frag in p["slots"].items():
            if side not in slots:
                raise ValueError(f"{p['id']}: slot {side} not in layout {lay}")
            x, w = slots[side]
            if "MEDVIDEO" in frag:   # a media clip inside the panel (the framework drives its playback)
                frag = frag.replace("MEDVIDEO", f'<video id="medv" class="clip" src="broll/v05_meds.mp4" muted playsinline '
                                    f'data-start="{p["start"]}" data-duration="{round(min(5.0, p["end"] - p["start"]), 3)}" data-track-index="3"></video>')
            inner.append(f'<div class="ypanel {side}" id="{p["id"]}-{side}" style="left:{x}px;width:{w}px">{frag}</div>')
        body.append(f'<div class="phost" id="{p["id"]}">{"".join(inner)}</div>')
        st, en = p["start"], p["end"]
        dx = {"main": 70 if lay == "L" else -70, "left": -60, "right": 60}
        js.append(f"// panel {p['id']} {lay} {st}-{en}")
        js.append(f"tl.set('#{p['id']}', {{opacity:1}}, {st});")
        for side in p["slots"]:
            sel = f"#{p['id']}-{side}"
            js.append(f"tl.fromTo('{sel}', {{opacity:0, x:{dx[side]}}}, {{opacity:1, x:0, duration:0.5, ease:'power3.out'}}, {fq(st + 0.15)});")
            js.append(f"tl.to('{sel}', {{opacity:0, x:{dx[side] // 2}, duration:0.3, ease:'power2.in'}}, {fq(en - 0.3)});")
        js.append(f"tl.set('#{p['id']}', {{opacity:0}}, {en});")
        for sel, t, kind in p["anims"]:
            js += anim(sel, max(fq(t), fq(st + 0.2)), kind)

    # full-screen inserts
    for z, (fid, kind, st, en, src) in enumerate(FS):
        st, en = fq(st), fq(en)
        if kind == "broll":
            body.append(f'<div class="fs" id="{fid}" style="z-index:{30 + z}"><div class="fs-in" id="{fid}-in">'
                        f'<video class="clip fsv" id="{fid}-v" src="broll/{src}.mp4" muted playsinline data-start="{st}" '
                        f'data-duration="{round(en - st, 3)}" data-track-index="{4 + z % 2}"></video>'
                        f'<div class="fs-shade"></div><div class="ai-tag">Ilustrasi AI · Higgsfield</div></div></div>')
            js.append(f"tl.set('#{fid}', {{opacity:1}}, {st});")
            js.append(f"tl.fromTo('#{fid}-in', {{opacity:0, scale:1.06}}, {{opacity:1, scale:1, duration:0.35, ease:'power2.out'}}, {st});")
            js.append(f"tl.fromTo('#{fid}-v', {{scale:1.0}}, {{scale:1.07, duration:{round(en - st, 3)}, ease:'sine.inOut'}}, {st});")
        else:
            bod, anims = MG[fid]
            body.append(f'<div class="fs" id="{fid}" style="z-index:{30 + z}"><div class="fs-in mgbg" id="{fid}-in">{bod}</div></div>')
            js.append(f"tl.set('#{fid}', {{opacity:1}}, {st});")
            js.append(f"tl.fromTo('#{fid}-in', {{clipPath:'inset(0% 100% 0% 0%)'}}, {{clipPath:'inset(0% 0% 0% 0%)', duration:0.45, ease:'power3.inOut'}}, {st});")
            for sel, t, k in anims:
                js += anim(sel, max(fq(t), fq(st + 0.15)), k)
        js.append(f"tl.to('#{fid}-in', {{opacity:0, duration:0.25, ease:'power2.in'}}, {fq(en - 0.25)});")
        js.append(f"tl.set('#{fid}', {{opacity:0}}, {en});")

    # captions
    caps = cap_lines()
    for n, (t0, t1, ws) in enumerate(caps):
        spans = "".join(f'<span class="cw" id="c{n}w{k}">{html.escape(w["text"])}</span> ' for k, w in enumerate(ws))
        body.append(f'<div class="cap" id="c{n}">{spans.strip()}</div>')
        js.append(f"tl.fromTo('#c{n}', {{opacity:0, y:18, scale:0.96}}, {{opacity:1, y:0, scale:1, duration:0.16, ease:'power3.out'}}, {t0});")
        js.append(f"tl.set('#c{n}', {{opacity:0}}, {t1});")
        for k, w in enumerate(ws):
            js.append(f"tl.set('#c{n}w{k}', {{color:'{MINT}'}}, {fq(w['start'])});")
            js.append(f"tl.set('#c{n}w{k}', {{color:'#ffffff'}}, {fq(w['end'] + 0.05)});")
    return body, js, len(caps)


def anim(sel, t, kind):
    if kind == "pop":
        return [f"tl.fromTo('{sel}', {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.34, ease:'back.out(1.8)'}}, {t});"]
    if kind == "slide":
        return [f"tl.fromTo('{sel}', {{opacity:0, x:-50}}, {{opacity:1, x:0, duration:0.4, ease:'power3.out'}}, {t});"]
    if kind == "rise":
        return [f"tl.fromTo('{sel}', {{opacity:0, y:46}}, {{opacity:1, y:0, duration:0.45, ease:'power3.out'}}, {t});"]
    if kind == "fade":
        return [f"tl.fromTo('{sel}', {{opacity:0}}, {{opacity:1, duration:0.35, ease:'power2.out'}}, {t});"]
    if kind == "stamp":
        return [f"tl.fromTo('{sel}', {{opacity:0, scale:1.9}}, {{opacity:1, scale:1, duration:0.26, ease:'power4.out'}}, {t});"]
    if kind == "strike":
        return [f"tl.fromTo('{sel}', {{backgroundSize:'0% 7px'}}, {{backgroundSize:'100% 7px', duration:0.35, ease:'power2.inOut'}}, {t});"]
    if kind == "strike2":
        return [f"tl.fromTo('{sel}', {{backgroundSize:'0% 10px'}}, {{backgroundSize:'100% 10px', duration:0.4, ease:'power2.inOut'}}, {t});"]
    if kind == "growy":
        return [f"tl.fromTo('{sel}', {{scaleY:0}}, {{scaleY:1, duration:0.5, ease:'power3.inOut'}}, {t});"]
    if isinstance(kind, tuple) and kind[0] == "draw":
        return [f"tl.fromTo('{sel}', {{strokeDashoffset:1500}}, {{strokeDashoffset:0, duration:{round(kind[1], 3)}, ease:'power1.inOut'}}, {t});"]
    raise ValueError(kind)


CSS = f"""
@font-face{{font-family:"PJS";src:url("fonts/PlusJakartaSans-500.woff2") format("woff2");font-weight:500;font-display:block}}
@font-face{{font-family:"PJS";src:url("fonts/PlusJakartaSans-700.woff2") format("woff2");font-weight:700;font-display:block}}
@font-face{{font-family:"PJS";src:url("fonts/PlusJakartaSans-800.woff2") format("woff2");font-weight:800;font-display:block}}
@font-face{{font-family:"Anton";src:url("fonts/Anton.woff2") format("woff2");font-weight:400;font-display:block}}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; padding:0; width:{W}px; height:{H}px; overflow:hidden; background:#041920; font-family:"PJS", sans-serif; }}
#stage {{ position:relative; width:{W}px; height:{H}px; overflow:hidden; background:#041920; }}
.scene {{ position:absolute; inset:0; opacity:0; overflow:hidden; z-index:1; }}
.bgimg {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
.vign {{ position:absolute; inset:0; background:radial-gradient(80% 80% at 50% 45%, rgba(0,0,0,0) 30%, rgba(0,0,0,.65) 100%); }}
.wash {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(8,50,60,.18), rgba(8,50,60,.42)); }}
.wash.warm {{ background:linear-gradient(180deg, rgba(60,30,0,.10), rgba(40,20,0,.38)); }}
.blob {{ position:absolute; width:900px; height:900px; border-radius:50%; left:900px; top:-200px;
  background:radial-gradient(circle, rgba(94,234,212,.28) 0%, rgba(94,234,212,0) 65%); }}
.blob.b2 {{ left:-150px; top:380px; background:radial-gradient(circle, rgba(255,248,238,.14) 0%, rgba(255,248,238,0) 65%); }}
.grid {{ position:absolute; inset:0; background-image:linear-gradient(rgba(94,234,212,.07) 2px, transparent 2px),
  linear-gradient(90deg, rgba(94,234,212,.07) 2px, transparent 2px); background-size:80px 80px; }}
.redglow {{ position:absolute; width:1100px; height:1100px; left:410px; top:-300px; border-radius:50%;
  background:radial-gradient(circle, rgba(229,72,77,.22) 0%, rgba(229,72,77,0) 62%); }}
#hero {{ position:absolute; inset:0; z-index:2; text-align:center; font-family:"Anton"; pointer-events:none; }}
#hero-k {{ position:absolute; left:0; right:0; top:70px; font-size:84px; color:{CREAM}; letter-spacing:.04em; opacity:0; }}
#hero-w {{ position:absolute; left:0; right:0; top:150px; font-size:520px; line-height:1; color:{MINT}; letter-spacing:.02em;
  text-shadow:0 20px 60px rgba(0,0,0,.35); opacity:0; }}
#spk {{ position:absolute; inset:0; z-index:3; pointer-events:none; }}
#spkmove {{ position:absolute; inset:0; transform-origin:960px 570px; filter:drop-shadow(0 30px 50px rgba(0,0,0,.45)); }}
#spot {{ position:absolute; left:{960 - 520}px; top:{570 - 520}px; width:1040px; height:1040px; border-radius:50%;
  background:radial-gradient(circle, rgba(255,248,238,.20) 0%, rgba(255,248,238,0) 62%); }}
.spkv {{ -webkit-mask-image:linear-gradient(90deg, transparent 0, #000 110px, #000 calc(100% - 110px), transparent 100%);
  mask-image:linear-gradient(90deg, transparent 0, #000 110px, #000 calc(100% - 110px), transparent 100%); }}
.spkv {{ position:absolute; left:{960 - FACE_X}px; top:{VID_TOP}px; width:{VID_W}px; height:{VID_H}px; }}
.phost {{ position:absolute; inset:0; z-index:4; opacity:0; pointer-events:none; }}
.ypanel {{ position:absolute; top:50%; transform:translateY(-58%); background:rgba(255,248,238,.97); border-radius:36px;
  padding:44px 50px 48px; color:{INK}; box-shadow:0 30px 80px rgba(3,20,25,.40), 0 2px 0 rgba(255,255,255,.7) inset; }}
.ypanel::before {{ content:""; position:absolute; left:0; top:36px; bottom:36px; width:12px; border-radius:0 8px 8px 0; background:{TEAL}; }}
.ypanel > * + * {{ margin-top:18px; }}
.chip {{ display:inline-block; font-weight:800; font-size:28px; letter-spacing:.08em; text-transform:uppercase; padding:10px 22px 9px; border-radius:999px; }}
.title {{ font-weight:800; font-size:58px; line-height:1.08; letter-spacing:-.015em; }}
.title.xl {{ font-size:72px; line-height:1.04; letter-spacing:-.02em; }}
.title.xxl {{ font-size:112px; line-height:.98; letter-spacing:-.03em; }}
.title.muted {{ color:{MUTED}; }}
.teal {{ color:{TEAL}; }} .red {{ color:{RED}; }} .mint {{ color:{MINT}; }}
.sub {{ font-weight:700; font-size:36px; color:#44525A; }}
.label {{ font-weight:700; font-size:30px; color:#44525A; text-transform:uppercase; letter-spacing:.06em; }}
.row {{ display:flex; align-items:center; gap:22px; font-weight:700; font-size:40px; line-height:1.15; }}
.row.big {{ font-size:46px; }}
.disc {{ width:70px; height:70px; flex:none; border-radius:50%; background:{TEAL}; display:inline-flex; align-items:center; justify-content:center; }}
.disc.lg {{ width:84px; height:84px; }}
.ico {{ width:42px; height:42px; }}
.tiles {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
.tile {{ display:flex; align-items:center; gap:18px; background:#E3F4F1; border-radius:22px; padding:16px 20px; font-weight:800; font-size:32px; color:{DEEP}; }}
.tile.more {{ justify-content:center; background:transparent; border:3px dashed rgba(14,94,111,.35); color:{TEAL}; }}
.pills {{ display:flex; flex-wrap:wrap; gap:14px; }}
.pill2 {{ font-weight:800; font-size:36px; padding:14px 26px; border-radius:18px; background:#E3F4F1; color:{TEAL}; }}
.hr {{ height:3px; background:rgba(14,94,111,.15); border-radius:2px; }}
.strike {{ background:linear-gradient({RED},{RED}) left 55%/0% 7px no-repeat; }}
.stamp {{ display:inline-block; transform:rotate(-6deg); border:8px solid {RED}; color:{RED}; border-radius:18px; font-weight:800;
  font-size:96px; letter-spacing:.04em; padding:6px 28px 2px; background:rgba(255,248,238,.95); }}
.stamp.teal {{ border-color:{TEAL}; color:{TEAL}; }}
.ypanel.right:has(.stamp) {{ background:transparent; box-shadow:none; }}
.ypanel.right:has(.stamp)::before {{ display:none; }}
.rung {{ display:flex; align-items:center; gap:20px; background:#fff; border-radius:22px; padding:18px 22px; font-weight:800; font-size:34px;
  line-height:1.12; box-shadow:0 8px 20px rgba(0,0,0,.08); }}
.num {{ width:58px; height:58px; flex:none; border-radius:50%; background:{RED}; color:#fff; font-size:32px; display:inline-flex; align-items:center; justify-content:center; }}
.lastbox {{ border:6px solid {RED}; border-radius:22px; padding:18px 24px; font-weight:800; font-size:40px; color:{RED}; text-align:center; }}
.lastbox b {{ color:{INK}; }}
.steps {{ display:flex; flex-wrap:wrap; align-items:center; gap:14px; font-weight:800; font-size:40px; }}
.step {{ padding:12px 24px; border-radius:16px; background:#E3F4F1; color:{TEAL}; }}
.step.hi {{ background:{TEAL}; color:#fff; }}
.sep {{ color:{MUTED}; }}
.arrowdown {{ font-size:110px; font-weight:800; color:{TEAL}; line-height:1; }}
.subpill {{ display:inline-block; background:{RED}; color:#fff; font-weight:800; font-size:30px; padding:14px 26px; border-radius:16px; }}
.medslot {{ width:772px; height:300px; border-radius:22px; background:#0B1F2A; overflow:hidden; }}
#medv {{ width:100%; height:100%; object-fit:cover; }}
.fs {{ position:absolute; inset:0; opacity:0; pointer-events:none; }}
.fs-in {{ position:absolute; inset:0; overflow:hidden; }}
.fsv {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
.fs-shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,0) 70%, rgba(0,0,0,.45) 100%); }}
.ai-tag {{ position:absolute; left:48px; top:44px; font:700 24px "PJS"; letter-spacing:.08em; text-transform:uppercase; color:rgba(255,255,255,.92);
  background:rgba(0,0,0,.38); padding:8px 16px 7px; border-radius:10px; }}
.mgbg {{ background:radial-gradient(110% 90% at 80% 10%, {TEAL} 0%, {DEEP} 60%, #041920 100%); color:{CREAM}; }}
.fs-chip {{ position:absolute; display:inline-block; font-weight:800; font-size:32px; letter-spacing:.08em; text-transform:uppercase;
  padding:12px 26px 11px; border-radius:999px; background:{MINT}; color:{DEEP}; }}
.fs-chip.red {{ background:{RED}; color:#fff; }}
.fs-chip.static {{ position:static; }}
.fs-title {{ position:absolute; font-weight:800; font-size:96px; line-height:1.02; letter-spacing:-.025em; }}
.fs-sub {{ position:absolute; font-weight:700; font-size:52px; color:rgba(255,248,238,.85); }}
.hh {{ position:absolute; top:0; width:960px; height:1080px; overflow:hidden; }}
.hh.left {{ left:0; }} .hh.right {{ left:960px; background:radial-gradient(120% 90% at 10% 0%, {TEAL} 0%, {DEEP} 70%); }}
.hh-img {{ position:absolute; left:0; top:-420px; width:960px; height:1707px; object-fit:cover; }}
.grim {{ filter:grayscale(1) contrast(1.15) brightness(.7); }}
.hh-shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.35), rgba(0,0,0,.15) 40%, rgba(0,0,0,.55)); }}
.fs-stamp {{ position:absolute; left:0; right:0; margin:auto; top:470px; width:max-content; transform:rotate(-7deg); border:10px solid {RED};
  color:{RED}; border-radius:22px; font-weight:800; font-size:110px; letter-spacing:.04em; padding:8px 34px 2px; background:rgba(255,248,238,.94); }}
.fs-stamp.chap {{ top:640px; }}
.vseam {{ position:absolute; left:954px; top:0; width:12px; height:1080px; background:{CREAM}; transform-origin:center top; }}
.center-col {{ position:absolute; left:0; right:0; top:170px; display:flex; flex-direction:column; align-items:center; gap:46px; }}
.big-line {{ display:flex; align-items:center; gap:36px; font-weight:800; font-size:140px; letter-spacing:-.03em; line-height:1; }}
.big-line.muted2 {{ font-size:96px; color:rgba(255,248,238,.6); }}
.bdisc {{ width:130px; height:130px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; flex:none; }}
.ico-xl {{ width:80px; height:80px; }}
.strike2 {{ background:linear-gradient({RED},{RED}) left 55%/0% 10px no-repeat; }}
.chap-num {{ position:absolute; left:0; right:0; top:170px; text-align:center; font-family:"Anton"; font-size:120px; letter-spacing:.06em; color:{MINT}; }}
.chap-q {{ position:absolute; left:160px; right:160px; top:340px; text-align:center; font-weight:800; font-size:92px; line-height:1.05; letter-spacing:-.02em; }}
.hrail {{ position:absolute; }}
.hrail path {{ stroke-dasharray:1500; }}
.hnode {{ position:absolute; top:500px; width:420px; margin-left:-180px; display:flex; flex-direction:column; align-items:center; gap:26px; }}
.hdot {{ width:96px; height:96px; border-radius:50%; background:{DEEP}; border:12px solid {MINT}; }}
.hnode.hi .hdot {{ background:{MINT}; }}
.hlabel {{ font-weight:800; font-size:46px; padding:14px 28px; border-radius:22px; background:{CREAM}; color:{INK}; white-space:nowrap; }}
.hnode.hi .hlabel {{ background:{MINT}; color:{DEEP}; }}
.cap {{ position:absolute; left:0; right:0; top:930px; z-index:100; text-align:center; font-family:"Anton"; font-size:66px; line-height:1.1;
  text-transform:uppercase; letter-spacing:.015em; color:#fff; opacity:0; pointer-events:none;
  -webkit-text-stroke:5px rgba(0,0,0,.6); paint-order:stroke fill; text-shadow:0 5px 0 rgba(0,0,0,.35), 0 10px 30px rgba(0,0,0,.55); }}
"""


def main():
    body, js, ncap = build()
    page = f"""<!doctype html>
<html lang="ms"><head><meta charset="utf-8" />
<style>{CSS}</style></head>
<body>
<div id="stage" data-composition-id="ward-yt" data-start="0" data-duration="{DUR}" data-fps="{FPS}" data-width="{W}" data-height="{H}">
  {chr(10).join(body)}
  <audio id="voice" src="voice.wav" data-start="0" data-duration="{DUR}" data-track-index="10" data-volume="1"></audio>
  <script src="vendor/gsap.min.js"></script>
  <script>
  (function () {{
    const tl = window.gsap.timeline({{ paused: true }});
    {(chr(10) + '    ').join(js)}
    window.__timelines = window.__timelines || {{}};
    window.__timelines["ward-yt"] = tl;
  }})();
  </script>
</div>
</body></html>
"""
    (P / "index.html").write_text(page)
    print(f"{len(PANELS)} panels, {len(FS)} full-screen inserts, {ncap} caption lines, {len(js)} timeline statements")
    for k, v in B.items():
        print(f"  {k:10s} {v:7.2f}")


if __name__ == "__main__":
    main()
