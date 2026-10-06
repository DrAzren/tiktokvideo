"""Generate the talking-head-recut composition for 'Tiga Tanda Kemurungan Yang Anda Tak Perasan'.

Template: videos/ward-psikiatri/graphics/build_graphics.py. Differences:
  - the speaker's head sits higher (hair top ~y 460-530, ~y 405-420 in the hook), so cards live in
    a shallower band, y PANEL_TOP-PANEL_MAX_BOTTOM; captions run in one line just below (y ~370-460)
  - every element time is a phrase anchor on edit/cut_words.json (inserts.T), so cards re-time
    themselves when the cut changes — no authored_words remap needed
Each element lands on the word it illustrates (starts LEAD s early so the motion lands on it).

Outputs: storyboard.json, public/cards/<id>.html, public/index.html
"""

import html
import json
from pathlib import Path

from inserts import T, build as build_inserts, HERO_WINDOW

W = Path(__file__).parent
PUB = W / "public"
FPS = 30
DUR = json.loads((W / "metadata.json").read_text())["duration"]
LEAD = 0.12

TEAL, MINT, CREAM, INK, RED, MUTED = "#0E5E6F", "#5EEAD4", "#FFF8EE", "#0B1F2A", "#E5484D", "#6B7C85"

CHECK = '<svg viewBox="0 0 24 24" class="ico"><circle cx="12" cy="12" r="11" fill="%s"/><path d="M7 12.5l3.2 3.2L17.5 8.5" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>' % TEAL
CROSS = '<svg viewBox="0 0 24 24" class="ico"><circle cx="12" cy="12" r="11" fill="%s"/><path d="M8 8l8 8M16 8l-8 8" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/></svg>' % RED
ARROW = '<svg viewBox="0 0 24 24" class="arr"><path d="M12 4v15M5.5 12.5L12 19l6.5-6.5" stroke="%s" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>' % TEAL
STAR = '<svg viewBox="0 0 24 24" class="star"><path d="M12 2.8l2.8 5.8 6.3.9-4.6 4.4 1.1 6.3L12 17.2 6.4 20.2l1.1-6.3L2.9 9.5l6.3-.9z" fill="#F5B942"/></svg>'


def q(t: float) -> float:
    """Absolute time -> frame-quantized time on the cut."""
    return round(round(min(t, DUR) * FPS) / FPS, 4)


def qd(a: float, b: float) -> float:
    return round(q(b) - q(a), 4)


def chip(text, color=TEAL):
    return f'<span class="chip" style="background:{color}">{html.escape(text)}</span>'


def row(icon, text, cls="row"):
    return f'<div class="{cls}">{icon}<span>{text}</span></div>'


def w(phrase, after=0.0):
    """Element time for a word: LEAD before it is spoken."""
    return T(phrase, after) - LEAD


# ---- card spec -------------------------------------------------------------
# element: (key, html, t_abs, anim)   anim in {"pop","slide","fade","strikeword","stamp","stampflow","none"}
# pages:   [(t_in, [elements])] — pages crossfade inside one persistent panel
INS = {}   # filled in main(): insert id -> (start, end)


def cards():
    t3 = T("nombor tiga", 30)      # sign 3 starts (second "nombor tiga": the first is the hook teaser)
    plug = T("kalau anda rasa banyak")
    cta = T("kalau perlukan bantuan")
    return [
        {"id": "c01-hook", "start": 0.0, "end": T("ini mungkin tanda") - 0.25, "hook": True,
         "intent": "Hook — if 3 of these signs are in you, it may not be ordinary tiredness", "pages": [
            (0.0, [
                ("kicker", chip("6 tanda kemurungan"), 0.0, "pop"),
                ("t1", f'<div class="title">Ada <span style="color:{TEAL}">3</span> pada anda?</div>', 0.0, "pop"),
            ]),
            (T("ini mungkin bukan") - 0.1, [
                ("t2", f'<div class="title">Mungkin <span style="color:{RED}">bukan</span> penat biasa</div>', w("bukan penat"), "slide"),
            ]),
        ]},
        {"id": "c02-teaser", "start": T("yang nombor tiga paling") - 0.1, "end": T("nombor satu") - 0.05,
         "intent": "Teaser — sign #3 is the most common", "pages": [
            (T("yang nombor tiga paling") - 0.1, [
                ("kicker", chip("Tanda #3"), T("yang nombor tiga paling"), "pop"),
                ("t", f'<div class="title">{STAR}Paling <span style="color:{TEAL}">common</span></div>', w("paling common"), "slide"),
            ]),
        ]},
        {"id": "c03-tanda1", "start": T("nombor satu") - 0.05, "end": T("bukan selalu skip") + 0.35,
         "intent": "Sign 1 — waking late and skipping breakfast", "pages": [
            (T("nombor satu") - 0.05, [
                ("kicker", chip("Tanda #1"), T("nombor satu"), "pop"),
                ("t", '<div class="title"><span id="c03-a">Bangun lewat</span> <span id="c03-b">&amp; skip breakfast</span></div>', T("nombor satu"), "none"),
                ("#c03-a", None, w("bangun lewat"), "slide"),
                ("#c03-b", None, w("skip breakfast"), "fade"),
            ]),
        ]},
        {"id": "c04-tanda2", "start": T("yang kedua") - 0.05, "end": T("kalau dulu suka") + 0.35,
         "intent": "Sign 2 — what used to be fun now feels like nothing", "pages": [
            (T("yang kedua") - 0.05, [
                ("kicker", chip("Tanda #2"), T("yang kedua"), "pop"),
                ("t", f'<div class="title">Dulu <span style="color:{TEAL}">seronok</span>…</div>', w("seronok"), "slide"),
                ("s", '<div class="sub">sekarang tak rasa apa-apa</div>', w("tak rasa apa"), "fade"),
            ]),
        ]},
        {"id": "c05-anhedonia", "start": T("yang ni yang kita") - 0.1, "end": t3 - 0.1,
         "intent": "The term: anhedonia — losing interest in what used to bring joy", "pages": [
            (T("yang ni yang kita") - 0.1, [
                ("kicker", chip("Istilahnya"), T("yang ni yang kita"), "pop"),
                ("t", f'<div class="title xl" style="color:{TEAL}">ANHEDONIA</div>', w("anhidonia"), "pop"),
            ]),
            (T("hilang minat") - 0.15, [
                ("t2", '<div class="title">Hilang minat</div>', w("hilang minat"), "slide"),
                ("s2", '<div class="sub">pada benda yang dulu menggembirakan</div>', w("menggembirakan"), "fade"),
            ]),
        ]},
        {"id": "c06-tanda3", "start": t3 - 0.05, "end": T("yang keempat") - 0.1,
         "intent": "Sign 3 (most common) — the phone first thing; not to scroll, to escape", "pages": [
            (t3 - 0.05, [
                ("kicker", chip("Tanda #3"), t3, "pop"),
                ("t", f'<div class="title">Bangun → terus <span style="color:{TEAL}">telefon</span></div>', w("bila bangun pagi"), "slide"),
            ]),
            # (benda pertama ... telefon) is the b2-phone B-roll; the page flips underneath it
            (T("bukan nak scroll") - 0.2, [
                ("kicker2", chip("Mitos", RED), T("bukan nak scroll") - 0.15, "pop"),
                ("m", '<div class="title muted"><span class="strikeword">Nak scroll</span></div>', w("bukan nak scroll"), "slide"),
                ("#c06-tanda3-m .strikeword", None, T("scroll pun", 40, end=True) - 0.1, "strikeword"),
                ("st", '<div class="stamp">TIDAK BENAR</div>', T("scroll pun", 40, end=True) - 0.05, "stamp"),
            ]),
            # the myth page holds until "lari daripada" so its strike + stamp read for ~1s
            (T("lari daripada") - 0.3, [
                ("kicker3", chip("Realiti"), T("lari daripada") - 0.25, "pop"),
                ("r1", row(CHECK, "Lari daripada realiti"), w("lari daripada"), "slide"),
                ("r2", row(CHECK, "Cari distraction — mood tak stabil"), w("cari distraction"), "slide"),
            ]),
        ]},
        {"id": "c07-tanda4", "start": T("yang keempat") - 0.05, "end": T("kejap pagi") + 0.35,
         "intent": "Sign 4 — severe mood swings", "pages": [
            (T("yang keempat") - 0.05, [
                ("kicker", chip("Tanda #4"), T("yang keempat"), "pop"),
                ("t", f'<div class="title">Mood swing <span style="color:{RED}">teruk</span></div>', w("mood swing"), "slide"),
            ]),
        ]},
        {"id": "c08-emosi", "start": T("emosi naik") - 0.15, "end": T("yang kelima") - 0.1,
         "intent": "Emotions up and down for no clear reason", "pages": [
            (T("emosi naik") - 0.15, [
                ("t", f'<div class="title">Emosi <span style="color:{TEAL}">naik turun</span></div>', w("emosi naik"), "slide"),
                ("s", '<div class="sub">tanpa sebab yang jelas</div>', w("tanpa sebab"), "fade"),
            ]),
        ]},
        {"id": "c09-tanda5", "start": T("yang kelima") - 0.05, "end": T("atau kita panggil", 60) + 1.6,
         "intent": "Sign 5 — forgetful, can't focus: brain fog", "pages": [
            (T("yang kelima") - 0.05, [
                ("kicker", chip("Tanda #5"), T("yang kelima"), "pop"),
                ("t", '<div class="title"><span id="c09-a">Mudah lupa</span> <span id="c09-b">&amp; susah fokus</span></div>', T("yang kelima"), "none"),
                ("#c09-a", None, w("mudah lupa"), "slide"),
                ("#c09-b", None, w("susah fokus"), "fade"),
            ]),
            # (baca satu benda ... nak ingat) is the b3-fog B-roll
            (T("otak jadi serabut") - 0.15, [
                ("s2", '<div class="sub">Otak jadi serabut…</div>', w("otak jadi serabut"), "slide"),
                ("t2", f'<div class="title xl" style="color:{TEAL}">BRAIN FOG</div>', w("brain fog"), "pop"),
            ]),
        ]},
        {"id": "c10-tanda6", "start": T("nombor enam") - 0.05, "end": T("benda kecil pun") + 0.35,
         "intent": "Sign 6 — tired and irritable; tired in the head, not the body", "pages": [
            (T("nombor enam") - 0.05, [
                ("kicker", chip("Tanda #6"), T("nombor enam"), "pop"),
                ("t", '<div class="title"><span id="c10-a">Penat</span> <span id="c10-b">&amp; cepat marah</span></div>', T("nombor enam"), "none"),
                ("#c10-a", None, w("rasa penat"), "slide"),
                ("#c10-b", None, w("cepat marah"), "fade"),
            ]),
            (T("letih tapi bukan") - 0.15, [
                ("a", row(CROSS, '<span class="strikeword">Letih fizikal</span>', "row big"), w("bukan letih fizikal") + 0.3, "slide"),
                ("#c10-tanda6-a .strikeword", None, T("letih dalam kepala") - 0.2, "strikeword"),
                ("b", row(CHECK, f'Letih <span style="color:{TEAL}">dalam kepala</span>', "row big"), w("letih dalam kepala"), "slide"),
            ]),
        ]},
        {"id": "c11-sama", "start": T("kesihatan mental ni sama") - 0.15, "end": plug - 0.1,
         "intent": "Mental health matters as much as physical health", "pages": [
            (T("kesihatan mental ni sama") - 0.15, [
                ("kicker", chip("Ingat"), T("kesihatan mental ni sama") - 0.1, "pop"),
                ("t", f'<div class="title">Kesihatan mental <span style="color:{TEAL}">=</span> fizikal</div>', w("sama penting"), "slide"),
            ]),
        ]},
        {"id": "c12-klinik", "start": plug - 0.05, "end": T("saya akan buat penilaian") + 0.35,
         "intent": "Plug (moved from 0:49) — screening at the clinic in Nilai", "pages": [
            (plug - 0.05, [
                ("kicker", chip("Banyak tanda ni pada anda?"), plug, "pop"),
                ("t", f'<div class="title">Klinik Dr Azren, <span style="color:{TEAL}">Nilai</span></div>', w("datang ke klinik"), "slide"),
            ]),
            (T("kita buat konsultasi") - 0.15, [
                ("t2", '<div class="title">Konsultasi &amp; saringan</div>', w("konsultasi dan saringan"), "slide"),
                ("s2", '<div class="sub">kesihatan mental</div>', w("kesihatan mental saya"), "fade"),
            ]),
        ]},
        {"id": "c13-cta", "start": cta - 0.05, "end": DUR,
         "intent": "CTA — consultation with Dr Azren, link in bio, questions in the comments", "pages": [
            (cta - 0.05, [
                ("kicker", chip("Perlukan bantuan?"), cta, "pop"),
                ("t", '<div class="title">Konsultasi bersama <span style="color:%s">Dr Azren</span></div>' % TEAL, w("bersama saya doktor"), "slide"),
            ]),
            (T("boleh klik di bio") - 0.15, [
                ("t2", f'<div class="title xl" style="color:{TEAL}">Klik link di bio</div>', w("klik di bio"), "pop"),
            ]),
            (T("apa persoalan") - 0.15, [
                ("t3", '<div class="title">Ada soalan?</div>', w("apa persoalan"), "pop"),
                ("s3", f'<div class="sub strong">Komen di bawah {ARROW}</div>', w("komen"), "slide"),
            ]),
        ]},
    ]


# (no ward-style tighten(): every chip here is itself a spoken word — "Tanda #1" lands on "nombor satu")
CARDS = cards()

HEIGHTS_FILE = W / "page_heights.json"      # written by measure_pages.cjs (real browser layout)
HEIGHTS = json.loads(HEIGHTS_FILE.read_text()) if HEIGHTS_FILE.exists() else {}
PANEL_PAD = 56                              # panel padding top+bottom
PANEL_TOP, PANEL_MAX_BOTTOM = 125, 362      # caption line starts at y ~370
HOOK_TOP, HOOK_MAX_BOTTOM = 100, 296        # hook: hair at y ~405, caption line raised to y ~300


def page_h(cid, p):
    h = HEIGHTS.get(f"{cid}-page{p}")
    return None if h is None else h + PANEL_PAD


CARD_CSS = f"""
.card-host .card {{ position:relative; width:100%; height:100%; }}
.panel {{ position:absolute; left:60px; top:{PANEL_TOP}px; width:960px; display:grid; background:{CREAM}; border-radius:30px;
  box-shadow:0 20px 54px rgba(8,22,30,.32), 0 2px 0 rgba(255,255,255,.6) inset; padding:26px 36px 30px;
  font-family:'Plus Jakarta Sans', sans-serif; color:{INK}; overflow:hidden; }}
.panel.hook {{ top:{HOOK_TOP}px; }}
.panel::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:12px; background:{TEAL}; }}
.page {{ grid-area:1/1; position:relative; align-self:start; }}  /* pages share one cell; panel height set per page */
.page > * + * {{ margin-top:10px; }}
.chip {{ display:inline-block; color:#fff; font-weight:800; font-size:27px; letter-spacing:.07em; text-transform:uppercase;
  padding:8px 18px 7px; border-radius:999px; }}
.title {{ font-weight:800; font-size:56px; line-height:1.06; letter-spacing:-.015em; white-space:nowrap; }}
.title.xl {{ font-size:84px; letter-spacing:-.01em; line-height:1.0; }}
.title.muted {{ color:{MUTED}; font-size:54px; }}
.sub {{ font-weight:700; font-size:36px; color:#3C4A52; }}
.sub.strong {{ color:{INK}; display:flex; align-items:center; gap:14px; }}
.row {{ display:flex; align-items:center; gap:16px; font-weight:700; font-size:38px; line-height:1.12; }}
.row.big {{ font-size:46px; font-weight:800; }}
.row + .row {{ margin-top:8px; }}
.ico {{ width:42px; height:42px; flex:none; }}
.arr {{ width:44px; height:44px; }}
.star {{ width:52px; height:52px; vertical-align:-6px; margin-right:12px; }}
.strikeword {{ background:linear-gradient({RED},{RED}) left 55%/0% 6px no-repeat; }}
.stampwrap {{ position:absolute; right:0; top:-6px; margin:0 !important; }}
.stamp {{ display:inline-block; transform:rotate(-6deg); border:6px solid {RED}; color:{RED}; border-radius:14px;
  font-weight:800; font-size:44px; letter-spacing:.04em; padding:6px 18px 2px; background:rgba(255,248,238,.92); }}
"""

STAMPWRAP = {"stamp": ' class="stampwrap"'}


def card_fragment(card) -> str:
    cid = card["id"]
    pages = []
    for p, (t_in, els) in enumerate(card["pages"]):
        inner = "".join(
            f'<div id="{cid}-{key}"{STAMPWRAP.get(anim, "")} data-anim="{anim}" '
            f'data-anim-at="{qd(card["start"], t)}">{frag}</div>'
            for key, frag, t, anim in els if frag is not None)
        pages.append(f'<div class="page" id="{cid}-page{p}">{inner}</div>')
    hook = " hook" if card.get("hook") else ""
    return (f'<div class="card" data-card-id="{cid}"><div class="root">'
            f'<div class="panel{hook}" id="{cid}-panel">{"".join(pages)}</div>'
            f'</div></div>')


INSERTS, INS_HOSTS, INS_JS, INS_CSS = build_inserts()


def card_end(card) -> float:
    """A card that would exit during (or just after) a full-screen insert leaves behind it instead,
    so it never flashes back for a moment once the insert clears."""
    e = q(card["end"])
    for x in INSERTS:
        if x["start"] + 0.3 < e <= x["end"] + 1.0:
            return round(x["start"] + 0.35, 4)
    return e


def timeline_js(card) -> list[str]:
    cid, s = card["id"], card["start"]
    host = f'.card-host[data-card-id="{cid}"]'
    panel = f"#{cid}-panel"
    js = [f"// {cid}: {card['intent']}",
          f'tl.set(\'{host}\', {{visibility:"visible", opacity:1}}, {q(s)});']
    if s <= 0.001:   # the hook is fully on screen at frame 0 (first frame = thumbnail/first impression)
        js.append(f"tl.set('{panel}', {{opacity:1, y:0, scale:1}}, 0);")
    else:
        js.append(f"tl.fromTo('{panel}', {{opacity:0, y:-30, scale:0.97}}, {{opacity:1, y:0, scale:1, duration:0.42, ease:'power3.out'}}, {q(s)});")
    if page_h(cid, 0):
        js.append(f"tl.set('{panel}', {{height:{page_h(cid, 0)}}}, {q(s)});")
    for p, (t_in, els) in enumerate(card["pages"]):
        pg = f"#{cid}-page{p}"
        if p == 0:
            js.append(f"tl.set('{pg}', {{opacity:1}}, {q(s)});")
        else:
            prev = f"#{cid}-page{p - 1}"
            js.append(f"tl.to('{prev}', {{opacity:0, y:-12, duration:0.26, ease:'power2.in'}}, {q(t_in - 0.26)});")
            js.append(f"tl.fromTo('{pg}', {{opacity:0, y:12}}, {{opacity:1, y:0, duration:0.3, ease:'power3.out'}}, {q(t_in)});")
            if page_h(cid, p):
                js.append(f"tl.to('{panel}', {{height:{page_h(cid, p)}, duration:0.36, ease:'power2.inOut'}}, {q(t_in - 0.18)});")
        for key, frag, t, anim in els:
            sel = f"#{cid}-{key}" if not key.startswith("#") else key
            Tt = q(max(t, s + 0.05))
            if t <= 0.001:
                js.append(f"tl.set('{sel}', {{opacity:1}}, 0);")
            elif anim == "pop":
                js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.34, ease:'back.out(1.8)'}}, {Tt});")
            elif anim == "slide":
                js.append(f"tl.fromTo('{sel}', {{opacity:0, x:-44}}, {{opacity:1, x:0, duration:0.38, ease:'power3.out'}}, {Tt});")
            elif anim == "fade":
                js.append(f"tl.fromTo('{sel}', {{opacity:0}}, {{opacity:1, duration:0.3, ease:'power2.out'}}, {Tt});")
            elif anim == "strikeword":
                js.append(f"tl.fromTo('{sel}', {{backgroundSize:'0% 6px'}}, {{backgroundSize:'100% 6px', duration:0.35, ease:'power2.inOut'}}, {Tt});")
            elif anim == "stamp":
                js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:1.9}}, {{opacity:1, scale:1, duration:0.26, ease:'power4.out'}}, {Tt});")
    E = card_end(card)
    if E < DUR:
        js.append(f"tl.to('{panel}', {{opacity:0, y:-20, duration:0.28, ease:'power2.in'}}, {round(E - 0.28, 4)});")
        js.append(f'tl.set(\'{host}\', {{visibility:"hidden"}}, {E});')
    return js


def main() -> None:
    (PUB / "cards").mkdir(parents=True, exist_ok=True)
    # sanity: cards never overlap each other, never sit on the hero apex window
    for a, b in zip(CARDS, CARDS[1:]):
        assert card_end(a) <= q(b["start"]) + 0.01, (a["id"], card_end(a), b["id"], b["start"])
    for c in CARDS:
        assert card_end(c) <= HERO_WINDOW[0] + 0.3 or q(c["start"]) >= HERO_WINDOW[1] - 0.3, c["id"]
        for t_in, els in c["pages"]:
            for e in els:
                if e[3] != "none":
                    assert q(c["start"]) - 0.01 <= q(e[2]) <= card_end(c), (c["id"], e[0], e[2])
    for c in CARDS:
        top, bottom = (HOOK_TOP, HOOK_MAX_BOTTOM) if c.get("hook") else (PANEL_TOP, PANEL_MAX_BOTTOM)
        for p in range(len(c["pages"])):
            h = page_h(c["id"], p)
            assert h is None or top + h <= bottom, f"{c['id']} page {p}: panel {top}-{top + h} crosses y {bottom}"
    storyboard = {
        "schemaVersion": 3,
        "composition": {"fps": FPS, "width": 1080, "height": 1920, "durationSeconds": DUR,
                        "layout": "portrait", "themeId": "custom-teal", "seed": 7},
        "videoTrack": {"sourcePath": "input-video.mp4", "startSec": 0, "endSec": DUR,
                       "bounds": {"x": 0, "y": 0, "width": 1080, "height": 1920}},
        "subtitles": {"enabled": False},
        "cards": [{"id": c["id"], "intent": c["intent"], "startSec": round(c["start"], 3), "endSec": round(card_end(c), 3),
                   "accentIndex": i % 5, "zone": "video-overlay",
                   "contentHints": {"pages": len(c["pages"])}} for i, c in enumerate(CARDS)],
        "inserts": [{"id": x["id"], "kind": x["kind"], "startSec": x["start"], "endSec": x["end"]} for x in INSERTS],
    }
    (W / "storyboard.json").write_text(json.dumps(storyboard, indent=2, ensure_ascii=False))

    hosts, js = [], []
    for c in CARDS:
        frag = card_fragment(c)
        (PUB / "cards" / f"{c['id']}.html").write_text(frag)
        hosts.append(f'<div id="card-{c["id"]}" class="card-host clip" data-card-id="{c["id"]}" data-start="{q(c["start"])}" '
                     f'data-duration="{round(card_end(c) - q(c["start"]), 4)}" data-track-index="2" '
                     f'style="left:0;top:0;width:1080px;height:1920px;visibility:hidden;">{frag}</div>')
        js += timeline_js(c)

    fonts = "".join(
        f'@font-face{{font-family:"Plus Jakarta Sans";src:url("fonts/PlusJakartaSans-{wt}.woff2") format("woff2");'
        f'font-weight:{wt};font-style:normal;font-display:block;}}' for wt in (500, 700, 800))
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
{INS_CSS}
</style>
</head>
<body>
<div id="stage" data-composition-id="talking-head-recut" data-start="0" data-duration="{DUR}" data-fps="{FPS}" data-width="1080" data-height="1920">
  <div class="video-wrapper" id="video-wrap">
    <video id="bg-video" src="input-video.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="1"></video>
  </div>
  <audio id="source-audio" src="input-video.mp4" data-start="0" data-duration="{DUR}" data-track-index="10" data-volume="1"></audio>
  {chr(10).join(hosts)}
  {chr(10).join(INS_HOSTS)}
  <script src="vendor/gsap.min.js"></script>
  <script>
  (function () {{
    const tl = window.gsap.timeline({{ paused: true }});
    {(chr(10) + '    ').join(js + INS_JS)}
    window.__timelines = window.__timelines || {{}};
    window.__timelines["talking-head-recut"] = tl;
  }})();
  </script>
</div>
</body>
</html>
"""
    (PUB / "index.html").write_text(page)
    print(f"{len(CARDS)} cards, {sum(len(c['pages']) for c in CARDS)} pages, {len(INSERTS)} inserts, "
          f"{len(js) + len(INS_JS)} timeline statements")
    for c in CARDS:
        print(f"  {c['id']:14} {q(c['start']):6.2f}-{card_end(c):6.2f}")
    for x in INSERTS:
        print(f"  {x['id']:14} {x['start']:6.2f}-{x['end']:6.2f}  ({x['kind']})")


if __name__ == "__main__":
    main()
