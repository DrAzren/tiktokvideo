"""Generate the talking-head-recut composition for 'Keadaan Dalam Wad Psikiatri'.

Cards live in the headroom band above the speaker (y 150-540 on 1080x1920);
captions go just below (y ~565-690) in the next stage. Every card element
lands on the word it illustrates — times are absolute seconds on the cut
timeline (edit/cut_words.json), with a small lead so the motion *lands* on
the spoken word.

Outputs: storyboard.json, public/cards/<id>.html, public/index.html
"""

import html
import json
from pathlib import Path

W = Path(__file__).parent
PUB = W / "public"
FPS = 30
DUR = json.loads((W / "metadata.json").read_text())["duration"]
LEAD = 0.12  # element starts this much before its word so it lands on it

TEAL, MINT, CREAM, INK, RED, MUTED = "#0E5E6F", "#5EEAD4", "#FFF8EE", "#0B1F2A", "#E5484D", "#6B7C85"

CHECK = '<svg viewBox="0 0 24 24" class="ico"><circle cx="12" cy="12" r="11" fill="%s"/><path d="M7 12.5l3.2 3.2L17.5 8.5" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>' % TEAL
CROSS = '<svg viewBox="0 0 24 24" class="ico"><circle cx="12" cy="12" r="11" fill="%s"/><path d="M8 8l8 8M16 8l-8 8" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/></svg>' % RED
DOT = '<svg viewBox="0 0 24 24" class="ico"><circle cx="12" cy="12" r="6" fill="%s"/></svg>' % MUTED
ARROW = '<svg viewBox="0 0 24 24" class="arr"><path d="M12 4v15M5.5 12.5L12 19l6.5-6.5" stroke="%s" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>' % TEAL


def _build_remap():
    """Card times were authored against authored_words.json. When the cut changes,
    re-map each authored time onto the current cut by sequence-aligning the two word
    lists and shifting by the matched word's displacement."""
    import difflib
    old = json.loads((W / "authored_words.json").read_text())
    new = json.loads((W.parent / "edit" / "cut_words.json").read_text())
    sm = difflib.SequenceMatcher(a=[w["text"] for w in old], b=[w["text"] for w in new], autojunk=False)
    pairs = [(old[i + k]["start"], new[j + k]["start"]) for i, j, n in sm.get_matching_blocks() for k in range(n)]

    def remap(t: float) -> float:
        prev = max((p for p in pairs if p[0] <= t), default=pairs[0])
        return t + (prev[1] - prev[0])
    return remap


REMAP = _build_remap()


def q(t: float) -> float:
    """Absolute authored time -> frame-quantized time on the current cut."""
    return round(round(min(REMAP(t), DUR) * FPS) / FPS, 4)


def qd(a: float, b: float) -> float:
    """Duration between two absolute authored times, on the current cut."""
    return round(q(b) - q(a), 4)


# ---- card spec -------------------------------------------------------------
# element: (kind, html, t_abs, anim)   anim in {"pop","slide","fade","strikeword","stamp","none"}
# pages:   [(t_in, [elements])] — pages crossfade inside one persistent panel


def chip(text, color=TEAL):
    return f'<span class="chip" style="background:{color}">{html.escape(text)}</span>'


def row(icon, text, cls="row"):
    return f'<div class="{cls}">{icon}<span>{text}</span></div>'


CARDS = [
    {"id": "c01-hook", "start": 0.0, "end": 8.35, "intent": "Hook — the patient's question", "pages": [
        (0.0, [
            ("kicker", chip("Soalan #1"), 0.15, "pop"),
            ("t1", '<div class="title sm">Macam mana keadaan dalam</div>', 0.3, "slide"),
            ("t2", f'<div class="title xl" style="color:{TEAL}">WAD PSIKIATRI?</div>', 3.85 - LEAD, "pop"),
            ("s1", '<div class="sub">Seram macam dalam filem?</div>', 5.8 - LEAD, "slide"),
        ]),
    ]},
    {"id": "c02-mitos", "start": 13.3, "end": 22.35, "intent": "Myths from films, struck out on 'tapi tidak sebenarnya'", "pages": [
        (13.3, [
            ("kicker", chip("Mitos · macam dalam filem", RED), 13.4, "pop"),
            ("lb", '<div class="label">Apa orang bayangkan</div>', 13.98 - LEAD, "fade"),
            ("m1", row(DOT, '<span class="strikeword">Gelap &amp; menakutkan</span>', "row big"), 16.47 - LEAD, "slide"),
            ("m2", row(DOT, '<span class="strikeword">Pesakit meracau-racau</span>', "row big"), 17.91 - LEAD, "slide"),
            ("m3", row(DOT, '<span class="strikeword">Diikat sepanjang masa</span>', "row big"), 19.86 - LEAD, "slide"),
            ("#c02-mitos-m1 .strikeword", None, 21.5, "strikeword"),
            ("#c02-mitos-m2 .strikeword", None, 21.62, "strikeword"),
            ("#c02-mitos-m3 .strikeword", None, 21.74, "strikeword"),
            ("st", '<div class="stamp">TIDAK BENAR</div>', 21.74, "stamp"),
        ]),
    ]},
    {"id": "c03-realiti", "start": 24.35, "end": 35.0, "intent": "Reality: a normal hospital ward, run by a team", "pages": [
        (24.35, [
            ("kicker", chip("Realiti di Malaysia"), 24.4, "pop"),
            ("t", '<div class="title">Salah satu wad di hospital</div>', 24.77 - LEAD, "slide"),
            ("s", '<div class="label">Dikendalikan oleh</div>', 26.45 - LEAD, "fade"),
            ("g1", '<div class="grid">'
                   '<span id="c03-p1" class="pill">Doktor psikiatri</span>'
                   '<span id="c03-p2" class="pill">Jururawat terlatih</span>'
                   '<span id="c03-p3" class="pill">Ahli psikologi</span>'
                   '<span id="c03-p4" class="pill">Kaunselor</span>'
                   '<span id="c03-p5" class="pill wide">Jurupulih cara kerja</span></div>', 26.45, "none"),
            ("#c03-p1", None, 27.81 - LEAD, "pop"),
            ("#c03-p2", None, 29.04 - LEAD, "pop"),
            ("#c03-p3", None, 30.61 - LEAD, "pop"),
            ("#c03-p4", None, 31.83 - LEAD, "pop"),
            ("#c03-p5", None, 33.02 - LEAD, "pop"),
        ]),
    ]},
    {"id": "c04-rutin", "start": 35.0, "end": 57.05, "intent": "Daily routine checklist, one tick per spoken item", "pages": [
        (35.0, [
            ("kicker", chip("Apa pesakit buat dalam wad?"), 35.1, "pop"),
            ("r1", row(CHECK, "Jumpa doktor setiap hari"), 36.44 - LEAD, "slide"),
            ("r2", row(CHECK, "Ambil ubat ikut jadual"), 40.98 - LEAD, "slide"),
            ("r3", row(CHECK, "Pemerhatian &amp; keselamatan dipantau"), 42.66 - LEAD, "slide"),
            ("r4", row(CHECK, "Terapi: cara kerja · senaman · kaunseling"), 46.14 - LEAD, "slide"),
            ("r5", row(CHECK, "Makan &amp; rehat ikut jadual"), 54.49 - LEAD, "slide"),
        ]),
    ]},
    {"id": "c05-tujuan", "start": 57.05, "end": 61.75, "intent": "Pull-quote: to stabilise, not to punish", "pages": [
        (57.05, [
            ("kicker", chip("Tujuan utama"), 57.15, "pop"),
            ("a", f'<div class="title xl" style="color:{TEAL}">MENSTABILKAN</div>', 58.75 - LEAD, "pop"),
            ("b", '<div class="title muted"><span class="strikeword">bukan menghukum</span></div>', 60.18 - LEAD, "slide"),
            ("#c05-tujuan-b .strikeword", None, 60.82 + 0.35, "strikeword"),
        ]),
    ]},
    {"id": "c06-soalan2", "start": 61.75, "end": 82.45, "intent": "Q2 — are all patients aggressive? No; the conditions they have", "pages": [
        (61.75, [
            ("kicker", chip("Soalan #2"), 61.85, "pop"),
            ("t", '<div class="title">Semua pesakit dalam wad agresif?</div>', 62.85 - LEAD, "slide"),
            ("st", '<div class="stamp teal">TIDAK</div>', 65.66 - LEAD, "stampflow"),
        ]),
        (67.75, [
            ("kicker2", chip("Mereka mungkin mengalami"), 67.85, "pop"),
            ("g", '<div class="grid">'
                  '<span id="c06-p1" class="pill">Kemurungan teruk</span>'
                  '<span id="c06-p2" class="pill">Anxiety melampau</span>'
                  '<span id="c06-p3" class="pill">Bipolar tidak stabil</span>'
                  '<span id="c06-p4" class="pill">Skizofrenia tidak stabil</span>'
                  '<span id="c06-p5" class="pill wide">Krisis emosi</span></div>', 67.75, "none"),
            ("#c06-p1", None, 68.97 - LEAD, "pop"),
            ("#c06-p2", None, 70.33 - LEAD, "pop"),
            ("#c06-p3", None, 71.75 - LEAD, "pop"),
            ("#c06-p4", None, 73.39 - LEAD, "pop"),
            ("#c06-p5", None, 75.49 - LEAD, "pop"),
        ]),
        (78.3, [
            ("q", '<div class="title">Ramai yang <span style="color:%s">pendiam</span> &amp; <span style="color:%s">takut</span></div>' % (TEAL, TEAL), 78.49 - LEAD, "slide"),
            ("s", '<div class="sub">— sedang berjuang dengan penyakit mereka</div>', 80.39 - LEAD, "slide"),
        ]),
    ]},
    {"id": "c07-soalan3", "start": 82.45, "end": 110.45, "intent": "Q3 — why are some patients restrained? Last resort, 3 conditions", "pages": [
        (82.45, [
            ("kicker", chip("Soalan #3"), 82.55, "pop"),
            ("t", '<div class="title">Kenapa ada pesakit kena ikat?</div>', 83.64 - LEAD, "slide"),
            ("st", '<div class="stamp">SALAH FAHAM</div>', 88.12 - LEAD, "stampflow"),
        ]),
        (89.95, [
            ("kicker2", chip("Physical restraint"), 90.05, "pop"),
            ("t2", '<div class="title"><span id="c07-t2a">Bukan rutin</span> <span id="c07-t2b" style="color:%s">— langkah terakhir</span></div>' % RED, 91.47 - LEAD, "none"),
            ("#c07-t2a", None, 91.47 - LEAD, "slide"),
            ("#c07-t2b", None, 94.71 - LEAD, "fade"),
            ("n1", row('<span class="num">1</span>', "Berisiko cederakan diri sendiri"), 96.88 - LEAD, "slide"),
            ("n2", row('<span class="num">2</span>', "Berisiko cederakan orang lain"), 99.06 - LEAD, "slide"),
            ("n3", row('<span class="num">3</span>', "Cara lain tidak berjaya menenangkan"), 101.26 - LEAD, "slide"),
        ]),
        (104.3, [
            ("kicker3", chip("Bila pesakit stabil"), 104.4, "pop"),
            ("t3", '<div class="title">Dihentikan <span style="color:%s">secepat mungkin</span></div>' % TEAL, 106.89 - LEAD, "slide"),
            ("s3", '<div class="sub">Ikut prosedur &amp; pemantauan yang ketat</div>', 108.27 - LEAD, "slide"),
        ]),
    ]},
    {"id": "c08-pulih", "start": 111.55, "end": 125.7, "intent": "Admission is not the end — patients go home and back to life", "pages": [
        (111.55, [
            ("kicker", chip("Masuk wad psikiatri"), 111.81 - LEAD, "pop"),
            ("a", row(CROSS, "Bukan bermaksud hidup berakhir", "row big"), 112.91 - LEAD, "slide"),
            ("b", row(CROSS, "Bukan bermaksud anda gila", "row big"), 114.81 - LEAD, "slide"),
        ]),
        (116.55, [
            ("kicker2", chip("Realiti"), 116.65, "pop"),
            ("tl", '<div class="steps">'
                   '<span id="c08-s1" class="step">Beberapa hari</span><span id="c08-a1" class="sep">→</span>'
                   '<span id="c08-s2" class="step">minggu</span><span id="c08-a2" class="sep">→</span>'
                   '<span id="c08-s3" class="step hi">Keluar</span></div>', 116.55, "none"),
            ("#c08-s1", None, 118.62 - LEAD, "pop"),
            ("#c08-a1", None, 119.4, "fade"),
            ("#c08-s2", None, 119.58 - LEAD, "pop"),
            ("#c08-a2", None, 120.1, "fade"),
            ("#c08-s3", None, 120.26 - LEAD, "pop"),
            ("k1", row(CHECK, "Kembali bekerja"), 122.36 - LEAD, "slide"),
            ("k2", row(CHECK, "Kembali belajar"), 123.16 - LEAD, "slide"),
            ("k3", row(CHECK, "Kembali hidup seperti biasa"), 123.94 - LEAD, "slide"),
        ]),
    ]},
    {"id": "c09-selamat", "start": 125.7, "end": 136.45, "intent": "Not a place of punishment — a safe place to rest, stabilise, begin healing", "pages": [
        (125.7, [
            ("kicker", chip("Wad psikiatri"), 125.8, "pop"),
            ("a", '<div class="title muted"><span class="strikeword">Tempat hukuman</span></div>', 126.43 - LEAD, "slide"),
            ("#c09-selamat-a .strikeword", None, 127.2, "strikeword"),
            ("b", f'<div class="title xl" style="color:{TEAL}">TEMPAT SELAMAT</div>', 128.82 - LEAD, "pop"),
            ("g", '<div class="steps">'
                  '<span id="c09-s1" class="step">Berehat</span><span id="c09-a1" class="sep">·</span>'
                  '<span id="c09-s2" class="step">Distabilkan</span><span id="c09-a2" class="sep">·</span>'
                  '<span id="c09-s3" class="step hi">Mula sembuh</span></div>', 125.7, "none"),
            ("#c09-s1", None, 130.61 - LEAD, "pop"),
            ("#c09-a1", None, 131.1, "fade"),
            ("#c09-s2", None, 131.31 - LEAD, "pop"),
            ("#c09-a2", None, 133.9, "fade"),
            ("#c09-s3", None, 134.36 - LEAD, "pop"),
        ]),
    ]},
    {"id": "c10-cta", "start": 136.45, "end": DUR, "intent": "CTA — don't be afraid to get help; screening at the clinic; comment", "pages": [
        (136.45, [
            ("kicker", chip("Kesihatan mental"), 136.55, "pop"),
            ("t0", '<div class="title sm">Anda / orang tersayang sedang bergelut?</div>', 136.99 - LEAD, "slide"),
            ("t", '<div class="title">Jangan takut <span style="color:%s">dapatkan bantuan</span></div>' % TEAL, 140.33 - LEAD, "slide"),
        ]),
        (141.9, [
            ("kicker2", chip("Di klinik saya"), 141.99, "pop"),
            ("t2", '<div class="title">Saringan kesihatan mental</div>', 142.57 - LEAD, "slide"),
            ("s2", row(CHECK, "Bincang pilihan rawatan paling sesuai"), 145.62 - LEAD, "slide"),
        ]),
        (147.35, [
            ("t3", f'<div class="title xl" style="color:{TEAL}">Ada soalan?</div>', 147.47 - LEAD, "pop"),
            ("s3", f'<div class="sub strong">Komen di bawah {ARROW}</div>', 148.4 - LEAD, "slide"),
        ]),
    ]},
]

CARD_CSS = f"""
.card-host .card {{ position:relative; width:100%; height:100%; }}
.panel {{ position:absolute; left:60px; top:160px; width:960px; display:grid; background:{CREAM}; border-radius:34px;
  box-shadow:0 22px 60px rgba(8,22,30,.30), 0 2px 0 rgba(255,255,255,.6) inset; padding:30px 38px 34px;
  font-family:'Plus Jakarta Sans', sans-serif; color:{INK}; overflow:hidden; }}
.panel::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:12px; background:{TEAL}; }}
.page {{ grid-area:1/1; position:relative; }}  /* pages share one cell: panel sizes to the tallest page */
.page > * + * {{ margin-top:16px; }}
.chip {{ display:inline-block; color:#fff; font-weight:800; font-size:24px; letter-spacing:.07em; text-transform:uppercase;
  padding:9px 20px 8px; border-radius:999px; }}
.title {{ font-weight:800; font-size:58px; line-height:1.08; letter-spacing:-.015em; }}
.title.sm {{ font-size:44px; font-weight:700; }}
.title.xl {{ font-size:88px; letter-spacing:-.02em; line-height:1.0; }}
.title.muted {{ color:{MUTED}; font-size:50px; }}
.sub {{ font-weight:700; font-size:38px; color:{MUTED}; }}
.sub.strong {{ color:{INK}; display:flex; align-items:center; gap:14px; }}
.label {{ font-weight:700; font-size:28px; color:{MUTED}; text-transform:uppercase; letter-spacing:.06em; }}
.row {{ display:flex; align-items:center; gap:18px; font-weight:700; font-size:38px; line-height:1.15; }}
.row.big {{ font-size:44px; }}
.row + .row {{ margin-top:14px; }}
.ico {{ width:40px; height:40px; flex:none; }}
.arr {{ width:44px; height:44px; }}
.num {{ width:44px; height:44px; flex:none; border-radius:50%; background:{RED}; color:#fff; font-size:26px; font-weight:800;
  display:inline-flex; align-items:center; justify-content:center; }}
.grid {{ display:flex; flex-wrap:wrap; gap:14px; }}
.pill {{ display:inline-block; font-weight:700; font-size:34px; padding:12px 24px; border-radius:18px; background:#E3F4F1; color:{TEAL};
  border:2px solid rgba(14,94,111,.25); }}
.steps {{ display:flex; align-items:center; flex-wrap:wrap; gap:14px; font-weight:800; font-size:40px; }}
.step {{ display:inline-block; padding:10px 22px; border-radius:16px; background:#E3F4F1; color:{TEAL}; }}
.step.hi {{ background:{TEAL}; color:#fff; }}
.sep {{ color:{MUTED}; font-size:40px; font-weight:800; }}
.strikeword {{ background:linear-gradient({RED},{RED}) left 55%/0% 6px no-repeat; }}
.stampwrap {{ position:absolute; right:0; top:-10px; margin:0 !important; }}  /* sits in the (half-width) chip row */
.stampflow {{ transform-origin:left center; padding-top:6px; }}
.stamp {{ display:inline-block; transform:rotate(-6deg); border:6px solid {RED}; color:{RED}; border-radius:14px;
  font-weight:800; font-size:46px; letter-spacing:.04em; padding:6px 18px 2px; background:rgba(255,248,238,.92); }}
.stamp.teal {{ border-color:{TEAL}; color:{TEAL}; font-size:72px; }}
"""


STAMPWRAP = {"stamp": ' class="stampwrap"', "stampflow": ' class="stampflow"'}


def card_fragment(card) -> str:
    cid = card["id"]
    pages = []
    for p, (t_in, els) in enumerate(card["pages"]):
        inner = "".join(
            f'<div id="{cid}-{key}"{STAMPWRAP.get(anim, "")} data-anim="{anim}" '
            f'data-anim-at="{qd(card["start"], t)}">{frag}</div>'
            for key, frag, t, anim in els if frag is not None)
        pages.append(f'<div class="page" id="{cid}-page{p}">{inner}</div>')
    return (f'<div class="card" data-card-id="{cid}"><div class="root">'
            f'<div class="panel" id="{cid}-panel">{"".join(pages)}</div>'
            f'</div></div>')


def timeline_js(card) -> list[str]:
    cid, s, e = card["id"], card["start"], card["end"]
    host = f'.card-host[data-card-id="{cid}"]'
    panel = f"#{cid}-panel"
    js = [f"// {cid}: {card['intent']}",
          f'tl.set(\'{host}\', {{visibility:"visible", opacity:1}}, {q(s)});',
          f"tl.fromTo('{panel}', {{opacity:0, y:-36, scale:0.97}}, {{opacity:1, y:0, scale:1, duration:0.45, ease:'power3.out'}}, {q(s)});"]
    pages = card["pages"]
    for p, (t_in, els) in enumerate(pages):
        pg = f"#{cid}-page{p}"
        if p == 0:
            js.append(f"tl.set('{pg}', {{opacity:1}}, {q(s)});")
        else:
            prev = f"#{cid}-page{p - 1}"
            js.append(f"tl.to('{prev}', {{opacity:0, y:-14, duration:0.28, ease:'power2.in'}}, {q(t_in - 0.28)});")
            js.append(f"tl.fromTo('{pg}', {{opacity:0, y:14}}, {{opacity:1, y:0, duration:0.32, ease:'power3.out'}}, {q(t_in)});")
        for key, frag, t, anim in els:
            sel = f"#{cid}-{key}" if not key.startswith("#") else key
            T = q(max(t, s + 0.05))
            if anim == "pop":
                js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.34, ease:'back.out(1.8)'}}, {T});")
            elif anim == "slide":
                js.append(f"tl.fromTo('{sel}', {{opacity:0, x:-44}}, {{opacity:1, x:0, duration:0.38, ease:'power3.out'}}, {T});")
            elif anim == "fade":
                js.append(f"tl.fromTo('{sel}', {{opacity:0}}, {{opacity:1, duration:0.3, ease:'power2.out'}}, {T});")
            elif anim == "strikeword":
                js.append(f"tl.fromTo('{sel}', {{backgroundSize:'0% 6px'}}, {{backgroundSize:'100% 6px', duration:0.35, ease:'power2.inOut'}}, {T});")
            elif anim in ("stamp", "stampflow"):
                js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:1.9}}, {{opacity:1, scale:1, duration:0.26, ease:'power4.out'}}, {T});")
        # rows / pills that were struck in c02 dim after the strike
    if cid == "c02-mitos":
        js.append(f"tl.to('#{cid}-m1, #{cid}-m2, #{cid}-m3', {{opacity:0.45, duration:0.3, ease:'power2.out'}}, {q(21.9)});")
    js.append(f"tl.to('{panel}', {{opacity:0, y:-24, duration:0.3, ease:'power2.in'}}, {q(e - 0.3)});")
    js.append(f'tl.set(\'{host}\', {{visibility:"hidden"}}, {q(e)});')
    return js


def main() -> None:
    (PUB / "cards").mkdir(parents=True, exist_ok=True)
    storyboard = {
        "schemaVersion": 3,
        "composition": {"fps": FPS, "width": 1080, "height": 1920, "durationSeconds": DUR,
                        "layout": "portrait", "themeId": "custom-teal", "seed": 7},
        "videoTrack": {"sourcePath": "input-video.mp4", "startSec": 0, "endSec": DUR,
                       "bounds": {"x": 0, "y": 0, "width": 1080, "height": 1920}},
        "subtitles": {"enabled": False},
        "cards": [{"id": c["id"], "intent": c["intent"], "startSec": c["start"], "endSec": c["end"],
                   "accentIndex": i % 5, "zone": "video-overlay",
                   "contentHints": {"pages": len(c["pages"])}} for i, c in enumerate(CARDS)],
    }
    (W / "storyboard.json").write_text(json.dumps(storyboard, indent=2, ensure_ascii=False))

    hosts, js = [], []
    for c in CARDS:
        frag = card_fragment(c)
        (PUB / "cards" / f"{c['id']}.html").write_text(frag)
        hosts.append(f'<div id="card-{c["id"]}" class="card-host clip" data-card-id="{c["id"]}" data-start="{q(c["start"])}" '
                     f'data-duration="{qd(c["start"], c["end"])}" data-track-index="2" '
                     f'style="left:0;top:0;width:1080px;height:1920px;visibility:hidden;">{frag}</div>')
        js += timeline_js(c)

    fonts = "".join(
        f'@font-face{{font-family:"Plus Jakarta Sans";src:url("fonts/PlusJakartaSans-{w}.woff2") format("woff2");'
        f'font-weight:{w};font-style:normal;font-display:block;}}' for w in (500, 700, 800))
    page = f"""<!doctype html>
<html lang="ms">
<head>
<meta charset="utf-8" />
<style>
{fonts}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; padding:0; width:100%; height:100%; overflow:hidden; background:#000;
  font-family:"Plus Jakarta Sans", sans-serif; }}
#stage {{ position:relative; width:1080px; height:1920px; overflow:hidden; }}
.video-wrapper {{ position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden; }}
.video-wrapper video {{ width:100%; height:100%; object-fit:cover; }}
.card-host {{ position:absolute; pointer-events:none; overflow:hidden; }}
.page {{ opacity:0; }}
{CARD_CSS}
</style>
</head>
<body>
<div id="stage" data-composition-id="talking-head-recut" data-start="0" data-duration="{DUR}" data-fps="{FPS}" data-width="1080" data-height="1920">
  <div class="video-wrapper" id="video-wrap">
    <video id="bg-video" src="input-video.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="1"></video>
  </div>
  <audio id="source-audio" src="input-video.mp4" data-start="0" data-duration="{DUR}" data-track-index="10" data-volume="1"></audio>
  {chr(10).join(hosts)}
  <script src="vendor/gsap.min.js"></script>
  <script>
  (function () {{
    const tl = window.gsap.timeline({{ paused: true }});
    {(chr(10) + '    ').join(js)}
    window.__timelines = window.__timelines || {{}};
    window.__timelines["talking-head-recut"] = tl;
  }})();
  </script>
</div>
</body>
</html>
"""
    (PUB / "index.html").write_text(page)
    print(f"{len(CARDS)} cards, {sum(len(c['pages']) for c in CARDS)} pages, {len(js)} timeline statements")


if __name__ == "__main__":
    main()
