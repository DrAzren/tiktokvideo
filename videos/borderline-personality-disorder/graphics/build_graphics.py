"""Generate the talking-head-recut composition for 'Borderline Personality Disorder'.

Template: videos/ward-psikiatri/graphics/build_graphics.py. The headroom here is tight (hair top
at y ~420-500 of 1920), so each card is ONE compact page: a chip + one headline (+ one short
line), in a cream panel at y 118-~320. Captions run in a one-line band just below it (y ~334-420)
in the next stage. Every element lands on the word it illustrates: times are phrase anchors on
the cut (edit/cut_words.json via inserts.T), so cards re-time themselves when the cut changes.

Outputs: storyboard.json, public/cards/<id>.html, public/index.html
"""

import html
import json
from pathlib import Path

from inserts import HERO, T
from inserts import build as build_inserts

W = Path(__file__).parent
PUB = W / "public"
FPS = 30
DUR = json.loads((W / "metadata.json").read_text())["duration"]
LEAD = 0.12  # element starts this much before its word so it lands on it

TEAL, MINT, CREAM, INK, RED, MUTED = "#0E5E6F", "#5EEAD4", "#FFF8EE", "#0B1F2A", "#E5484D", "#6B7C85"

CHECK = '<svg viewBox="0 0 24 24" class="ico"><circle cx="12" cy="12" r="11" fill="%s"/><path d="M7 12.5l3.2 3.2L17.5 8.5" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>' % TEAL
CROSSR = '<svg viewBox="0 0 24 24" class="ico"><circle cx="12" cy="12" r="11" fill="%s"/><path d="M8 8l8 8M16 8l-8 8" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/></svg>' % RED
ARROW = '<svg viewBox="0 0 24 24" class="arr"><path d="M12 4v15M5.5 12.5L12 19l6.5-6.5" stroke="%s" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>' % TEAL


def q(t: float) -> float:
    """Absolute cut time -> frame-quantized time."""
    return round(round(min(t, DUR) * FPS) / FPS, 4)


def qd(a: float, b: float) -> float:
    return round(q(b) - q(a), 4)


def w(phrase, after=0.0, end=False):
    """Word time minus LEAD (element lands on the word)."""
    return T(phrase, after, end) - (0 if end else LEAD)


# ---- card spec -------------------------------------------------------------
# element: (kind, html, t_abs, anim)   anim in {"pop","slide","fade","strikeword","stamp","none"}
# pages:   [(t_in, [elements])] — pages crossfade inside one persistent panel


def chip(text, color=TEAL):
    return f'<span class="chip" style="background:{color}">{html.escape(text)}</span>'


def row(icon, text, cls="row"):
    return f'<div class="{cls}">{icon}<span>{text}</span></div>'


CARDS = [
    # hook: on screen from frame 0 (thumbnail); hidden behind the window B-roll; the stamp answers "Betul ke?"
    {"id": "c01-hook", "start": 0.0, "end": T("tunjukkan") + 0.1, "intent": "Hook — the myth 'BPD is just moodiness'", "pages": [
        (0.0, [
            ("kicker", chip("Mitos", RED), 0.0, "pop"),
            ("t", f'<div class="title">BPD = sekadar <span style="color:{TEAL}">moody?</span></div>', 0.0, "slide"),
            ("st", '<div class="stamp">TIDAK BENAR</div>', w("ke", after=5.0), "stamp"),
        ]),
    ]},
    # (HERO window: no card while "BPD" slams in behind the head)
    {"id": "c02-realiti", "start": HERO[1], "end": T("pertama") - 0.05, "intent": "Reality: 6 main signs", "pages": [
        (HERO[1], [
            ("kicker", chip("Realiti"), HERO[1] + 0.05, "pop"),
            ("t", f'<div class="title"><span style="color:{TEAL}">6</span> tanda utama BPD</div>', HERO[1] + 0.12, "slide"),
        ]),
    ]},
    {"id": "c03-t1", "start": T("pertama") - 0.1, "end": T("contohnya kalau pasangan"), "intent": "Sign 1 — fear of abandonment", "pages": [
        (T("pertama") - 0.1, [
            ("kicker", chip("Tanda #1"), w("pertama"), "pop"),
            ("t", '<div class="title">Takut ditinggalkan</div>', w("takut ditinggalkan"), "slide"),
        ]),
    ]},
    {"id": "c04-t2", "start": T("yang kedua") - 0.1, "end": T("sekejap rasa orang tu perfek"), "intent": "Sign 2 — unstable relationships", "pages": [
        (T("yang kedua") - 0.1, [
            ("kicker", chip("Tanda #2"), w("kedua"), "pop"),
            ("t", '<div class="title">Hubungan tak stabil</div>', w("hubungan mereka"), "slide"),
        ]),
    ]},
    {"id": "c04b-t2", "start": T("mudah percaya", end=True) + 0.25, "end": T("yang ketiga") - 0.05, "intent": "Sign 2 — trust and hate both go to extremes", "pages": [
        (T("mudah percaya", end=True) + 0.25, [
            ("r1", row(CHECK, "Percaya — terlalu percaya"), T("mudah percaya", end=True) + 0.3, "slide"),
            ("r2", row(CROSSR, "Benci — benci <b>sangat-sangat</b>"), w("benci dengan"), "slide"),
        ]),
    ]},
    {"id": "c05-t3", "start": T("yang ketiga") - 0.1, "end": T("contohnya pagi"), "intent": "Sign 3 — unstable emotions", "pages": [
        (T("yang ketiga") - 0.1, [
            ("kicker", chip("Tanda #3"), w("ketiga"), "pop"),
            ("t", '<div class="title">Emosi tak stabil</div>', w("emosi tak stabil"), "slide"),
            ("s", '<div class="sub">Turun naik dengan cepat</div>', w("emosi turun naik"), "fade"),
        ]),
    ]},
    {"id": "c06-t4", "start": T("yang keempat") - 0.1, "end": T("walaupun dikelilingi"), "intent": "Sign 4 — chronic emptiness", "pages": [
        (T("yang keempat") - 0.1, [
            ("kicker", chip("Tanda #4"), w("keempat"), "pop"),
            ("t", '<div class="title">Rasa kosong berpanjangan</div>', w("rasa kosong yang"), "slide"),
        ]),
    ]},
    {"id": "c06b-t4", "start": T("tetapi jiwa") - 0.05, "end": T("yang kelima") - 0.05, "intent": "Sign 4 — empty even among people", "pages": [
        (T("tetapi jiwa") - 0.05, [
            ("t", f'<div class="title sm">Ramai orang di sekeliling,</div>', T("tetapi jiwa"), "slide"),
            ("s", f'<div class="title">jiwa tetap <span style="color:{TEAL}">kosong</span></div>', w("jiwa rasa kosong"), "slide"),
        ]),
    ]},
    {"id": "c07-t5", "start": T("yang kelima") - 0.1, "end": T("tiba tiba marah yang", after=T("kawal")), "intent": "Sign 5 — intense, hard-to-control anger", "pages": [
        (T("yang kelima") - 0.1, [
            ("kicker", chip("Tanda #5"), w("kelima"), "pop"),
            ("t", '<div class="title">Marah yang melampau</div>', w("kemarahan"), "slide"),
            ("s", '<div class="sub">Susah nak kawal</div>', w("susah nak kawal"), "fade"),
        ]),
    ]},
    {"id": "c07b-t5", "start": T("difahami", end=True) + 0.1, "end": T("nombor enam") - 0.05, "intent": "Sign 5 — even over small things", "pages": [
        (T("difahami", end=True) + 0.1, [
            ("t", f'<div class="title">…walaupun hal <span style="color:{TEAL}">kecil</span></div>', T("difahami", end=True) + 0.15, "slide"),
        ]),
    ]},
    {"id": "c08-t6", "start": T("nombor enam") - 0.1, "end": T("contohnya syoping"), "intent": "Sign 6 — impulsive behaviour", "pages": [
        (T("nombor enam") - 0.1, [
            ("kicker", chip("Tanda #6"), w("nombor enam"), "pop"),
            ("t", '<div class="title">Tingkah laku impulsif</div>', w("tingkah laku"), "slide"),
        ]),
    ]},
    {"id": "c09-gejala", "start": T("ini adalah gejala") - 0.05, "end": T("kalau anda nak") - 0.05, "intent": "These are symptoms, and treatment exists", "pages": [
        (T("ini adalah gejala") - 0.05, [
            ("kicker", chip("Realiti"), T("ini adalah gejala"), "pop"),
            ("t", '<div class="title">Ini gejala BPD</div>', w("gejala gejala"), "slide"),
            ("s", row(CHECK, "Rawatan memang ada", "row big"), w("rawatan untuk"), "slide"),
        ]),
    ]},
    {"id": "c10-klinik", "start": T("kalau anda nak") - 0.1, "end": T("anda boleh datang"), "intent": "Plug — consultation and screening at the clinic", "pages": [
        (T("kalau anda nak") - 0.1, [
            ("kicker", chip("Di klinik saya · Nilai"), w("kalau anda nak"), "pop"),
            ("t", '<div class="title sm">Konsultasi &amp; saringan<br/>kesihatan mental</div>', w("konsultasi"), "slide"),
        ]),
    ]},
    {"id": "c10b-klinik", "start": T("sama ada nak") + 0.05, "end": T("apa apa soalan") - 0.05, "intent": "Plug — what the clinic helps with", "pages": [
        (T("sama ada nak") + 0.05, [
            ("r1", row(CHECK, "Faham keadaan diri"), w("faham tentang"), "slide"),
            ("r2", row(CHECK, "Dapatkan rawatan sesuai"), w("dapatkan rawatan"), "slide"),
            ("r3", row(CHECK, f'<span style="color:{TEAL}">InsyaAllah kami boleh bantu</span>'), w("insyaallah"), "slide"),
        ]),
    ]},
    {"id": "c11-cta", "start": T("apa apa soalan") - 0.1, "end": DUR, "intent": "CTA — ask in the comments", "pages": [
        (T("apa apa soalan") - 0.1, [
            ("t", f'<div class="title xl" style="color:{TEAL}">Ada soalan?</div>', w("apa apa soalan"), "pop"),
            ("s", f'<div class="sub strong">Tanya di ruang komen {ARROW}</div>', w("ruang komen"), "slide"),
        ]),
    ]},
]

def tighten(cards, min_gap=0.6, lead=0.3):
    """No empty shells: a chip may not sit alone. If a page's kicker comes > min_gap before its
    first content, move the kicker (and the page / card entrance) to just before that content."""
    for c in cards:
        for p, (t_in, els) in enumerate(c["pages"]):
            kick = [i for i, e in enumerate(els) if e[0].startswith("kicker")]
            # a small label is not content: a chip + label alone still reads as an empty card
            content = [e[2] for e in els if not e[0].startswith(("kicker", "lb")) and e[3] != "none"]
            if not kick or not content:
                continue
            first = min(content)
            k = kick[0]
            if els[k][2] < first - min_gap:
                nk = round(first - lead, 3)
                els[k] = (els[k][0], els[k][1], nk, els[k][3])
                new_in = round(nk - 0.1, 3)
                if p == 0:
                    c["start"] = new_in
                c["pages"][p] = (new_in, els)


tighten(CARDS)

HEIGHTS_FILE = W / "page_heights.json"      # written by measure_pages.cjs (real browser layout)
HEIGHTS = json.loads(HEIGHTS_FILE.read_text()) if HEIGHTS_FILE.exists() else {}
PANEL_PAD = 64                              # panel padding top+bottom
PANEL_TOP, PANEL_MAX_BOTTOM = 118, 322      # keep clear of the caption line (~y334) and the hair (~y420)


def page_h(cid, p):
    h = HEIGHTS.get(f"{cid}-page{p}")
    return None if h is None else h + PANEL_PAD


CARD_CSS = f"""
.card-host .card {{ position:relative; width:100%; height:100%; }}
.panel {{ position:absolute; left:60px; top:118px; width:960px; display:grid; background:{CREAM}; border-radius:34px;
  box-shadow:0 22px 60px rgba(8,22,30,.30), 0 2px 0 rgba(255,255,255,.6) inset; padding:20px 34px 22px;
  font-family:'Plus Jakarta Sans', sans-serif; color:{INK}; overflow:hidden; }}
.panel::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:12px; background:{TEAL}; }}
.page {{ grid-area:1/1; position:relative; align-self:start; }}  /* pages share one cell; panel height set per page */
.page > * + * {{ margin-top:10px; }}
.chip {{ display:inline-block; color:#fff; font-weight:800; font-size:25px; letter-spacing:.07em; text-transform:uppercase;
  padding:7px 18px 6px; border-radius:999px; }}
.title {{ font-weight:800; font-size:54px; line-height:1.08; letter-spacing:-.015em; }}
.title.sm {{ font-size:42px; font-weight:700; line-height:1.12; }}
.title.xl {{ font-size:78px; letter-spacing:-.02em; line-height:1.0; }}
.title.muted {{ color:{MUTED}; font-size:50px; }}
.sub {{ font-weight:700; font-size:36px; color:#44525A; }}
.sub.strong {{ color:{INK}; display:flex; align-items:center; gap:14px; }}
.label {{ font-weight:700; font-size:32px; color:#44525A; text-transform:uppercase; letter-spacing:.06em; }}
.row {{ display:flex; align-items:center; gap:16px; font-weight:700; font-size:38px; line-height:1.15; }}
.row.big {{ font-size:40px; }}
.row + .row {{ margin-top:8px; }}
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
.stampwrap {{ position:absolute; right:0; top:-14px; margin:0 !important; }}  /* sits in the (half-width) chip row */
.stampflow {{ transform-origin:left center; padding-top:6px; }}
.stamp {{ display:inline-block; transform:rotate(-6deg); border:6px solid {RED}; color:{RED}; border-radius:14px;
  font-weight:800; font-size:40px; letter-spacing:.04em; padding:4px 16px 0px; background:rgba(255,248,238,.92); }}
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
    cid, s, e = card["id"], card["start"], card["end"]
    host = f'.card-host[data-card-id="{cid}"]'
    panel = f"#{cid}-panel"
    js = [f"// {cid}: {card['intent']}",
          f'tl.set(\'{host}\', {{visibility:"visible", opacity:1}}, {q(s)});']
    if s <= 0.001:   # the hook is fully on screen at frame 0 (first frame = thumbnail/first impression)
        js.append(f"tl.set('{panel}', {{opacity:1, y:0, scale:1}}, 0);")
    else:
        js.append(f"tl.fromTo('{panel}', {{opacity:0, y:-36, scale:0.97}}, {{opacity:1, y:0, scale:1, duration:0.45, ease:'power3.out'}}, {q(s)});")
    if page_h(cid, 0):
        js.append(f"tl.set('{panel}', {{height:{page_h(cid, 0)}}}, {q(s)});")
    pages = card["pages"]
    for p, (t_in, els) in enumerate(pages):
        pg = f"#{cid}-page{p}"
        if p == 0:
            js.append(f"tl.set('{pg}', {{opacity:1}}, {q(s)});")
        else:
            prev = f"#{cid}-page{p - 1}"
            js.append(f"tl.to('{prev}', {{opacity:0, y:-14, duration:0.28, ease:'power2.in'}}, {q(t_in - 0.28)});")
            js.append(f"tl.fromTo('{pg}', {{opacity:0, y:14}}, {{opacity:1, y:0, duration:0.32, ease:'power3.out'}}, {q(t_in)});")
            if page_h(cid, p):
                js.append(f"tl.to('{panel}', {{height:{page_h(cid, p)}, duration:0.4, ease:'power2.inOut'}}, {q(t_in - 0.2)});")
        for key, frag, t, anim in els:
            sel = f"#{cid}-{key}" if not key.startswith("#") else key
            T = q(max(t, s + 0.05))
            if t <= 0.001:
                js.append(f"tl.set('{sel}', {{opacity:1}}, 0);")
            elif anim == "pop":
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
    E = card_end(card)
    js.append(f"tl.to('{panel}', {{opacity:0, y:-24, duration:0.3, ease:'power2.in'}}, {round(E - 0.3, 4)});")
    js.append(f'tl.set(\'{host}\', {{visibility:"hidden"}}, {E});')
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
                     f'data-duration="{round(card_end(c) - q(c["start"]), 4)}" data-track-index="2" '
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
    print(f"{len(CARDS)} cards, {sum(len(c['pages']) for c in CARDS)} pages, {len(js)} timeline statements")


if __name__ == "__main__":
    main()
