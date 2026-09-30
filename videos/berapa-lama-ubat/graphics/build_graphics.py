"""Generate the talking-head-recut composition for 'Berapa Lama Makan Ubat Psikiatri'.

Template: videos/ward-psikiatri/graphics/build_graphics.py. This framing has much less headroom
(hair top y~470-520 after the caption crop), so cards are compact — chip + one line per page —
in y 140-350; captions go just below (y ~360-480) in the next stage. Every card element
lands on the word it illustrates — times are absolute seconds on the cut
timeline (edit/cut_words.json), with a small lead so the motion *lands* on
the spoken word.

Outputs: storyboard.json, public/cards/<id>.html, public/index.html
"""

import html
import json
from pathlib import Path

from inserts import build as build_inserts

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
    if t == DUR:   # "until the end" is not an authored word time: never remap it
        return DUR
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
    {"id": "c01-hook", "start": 0.0, "end": 4.12, "intent": "Hook — the patient's two questions", "pages": [
        (0.0, [
            ("kicker", chip("Soalan #1"), 0.0, "pop"),
            ("t1", '<div class="title">Berapa lama kena <span style="color:%s">makan ubat?</span></div>' % TEAL, 0.0, "slide"),
        ]),
        (2.02, [
            ("kicker2", chip("Soalan #2"), 2.09 - LEAD, "pop"),
            ("t2", f'<div class="title xl" style="color:{TEAL}">SEUMUR HIDUP?</div>', 3.36 - LEAD, "pop"),
        ]),
    ]},
    # 4.1-8.85: no card — "Jom kita kupas", then the BERGANTUNG hero sits behind the head in the headroom
    {"id": "c02-kenapa", "start": 16.55, "end": 17.62, "intent": "Soalan #3 — why can it take longer?", "pages": [
        (16.55, [
            ("kicker", chip("Soalan #3"), 16.6, "pop"),
            ("t", '<div class="title">Kenapa <span style="color:%s">lama?</span></div>' % TEAL, 16.63 - LEAD, "slide"),
        ]),
    ]},
    {"id": "c03-sebelum", "start": 20.1, "end": 21.72, "intent": "Stable first, then stop", "pages": [
        (20.1, [
            ("r", row(CHECK, 'Stabil dulu, <span style="color:%s">baru berhenti</span>' % TEAL, "row big"), 20.11 - LEAD, "slide"),
        ]),
    ]},
    {"id": "c04-kronik", "start": 25.62, "end": 30.4, "intent": "Chronic illness: bipolar, schizophrenia", "pages": [
        (25.62, [
            ("t", '<div class="title sm">Penyakit mental <span style="color:%s">kronik</span></div>' % TEAL, 27.31 - LEAD, "slide"),
            ("g", '<div class="steps">'
                  '<span id="c04-s1" class="step">Bipolar</span>'
                  '<span id="c04-s2" class="step">Skizofrenia</span>'
                  '<span id="c04-s3" class="step hi">Jangka panjang</span></div>', 25.62, "none"),
            ("#c04-s1", None, 28.66 - LEAD, "pop"),
            ("#c04-s2", None, 29.42 - LEAD, "pop"),
            ("#c04-s3", None, 30.20 - LEAD, "pop"),
        ]),
    ]},
    {"id": "c05-penting", "start": 39.8, "end": 42.72, "intent": "Most important: never stop on your own", "pages": [
        (39.8, [
            ("kicker", chip("Paling penting", RED), 40.12 - LEAD, "pop"),
            ("t", row(CROSS, 'Jangan stop ubat <span style="color:%s">suka-suka</span>' % RED, "row big"), 41.59 - LEAD, "slide"),
        ]),
    ]},
    {"id": "c06-mitos", "start": 50.2, "end": 55.8, "intent": "Myth: medication = a life sentence. Reality: a chance to heal", "pages": [
        (50.2, [
            ("kicker", chip("Mitos", RED), 50.31 - LEAD, "pop"),
            ("a", '<div class="title muted"><span class="strikeword">Hukuman seumur hidup</span></div>', 51.37 - LEAD, "slide"),
            ("#c06-mitos-a .strikeword", None, 52.13, "strikeword"),
            ("st", '<div class="stamp">TIDAK BENAR</div>', 52.57 - LEAD, "stamp"),
        ]),
        (53.84, [
            ("kicker2", chip("Realiti"), 53.87 - LEAD, "pop"),
            ("b", '<div class="title">Peluang untuk <span style="color:%s">sembuh</span></div>' % TEAL, 54.37 - LEAD, "pop"),
        ]),
    ]},
    {"id": "c07-cta", "start": 58.3, "end": DUR, "intent": "CTA — ask in the comments", "pages": [
        (58.3, [
            ("t3", f'<div class="title xl" style="color:{TEAL}">Ada soalan?</div>', 58.84 - LEAD, "pop"),
            ("s3", f'<div class="sub strong">Tanya di komen {ARROW}</div>', 59.80 - LEAD, "slide"),
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
PANEL_PAD = 50                              # panel padding top+bottom
PANEL_TOP, PANEL_MAX_BOTTOM = 140, 352      # keep clear of the caption line (~y360)


def page_h(cid, p):
    h = HEIGHTS.get(f"{cid}-page{p}")
    return None if h is None else h + PANEL_PAD


CARD_CSS = f"""
.card-host .card {{ position:relative; width:100%; height:100%; }}
.panel {{ position:absolute; left:60px; top:140px; width:960px; display:grid; background:{CREAM}; border-radius:34px;
  box-shadow:0 22px 60px rgba(8,22,30,.30), 0 2px 0 rgba(255,255,255,.6) inset; padding:24px 36px 26px;
  font-family:'Plus Jakarta Sans', sans-serif; color:{INK}; overflow:hidden; }}
.panel::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:12px; background:{TEAL}; }}
.page {{ grid-area:1/1; position:relative; align-self:start; }}  /* pages share one cell; panel height set per page */
.page > * + * {{ margin-top:12px; }}
.chip {{ display:inline-block; color:#fff; font-weight:800; font-size:30px; letter-spacing:.07em; text-transform:uppercase;
  padding:9px 20px 8px; border-radius:999px; }}
.title {{ font-weight:800; font-size:58px; line-height:1.08; letter-spacing:-.015em; }}
.title.sm {{ font-size:44px; font-weight:700; }}
.title.xl {{ font-size:84px; letter-spacing:-.02em; line-height:1.0; }}
.title.muted {{ color:{MUTED}; font-size:50px; }}
.sub {{ font-weight:700; font-size:38px; color:#44525A; }}
.sub.strong {{ color:{INK}; display:flex; align-items:center; gap:14px; }}
.label {{ font-weight:700; font-size:32px; color:#44525A; text-transform:uppercase; letter-spacing:.06em; }}
.row {{ display:flex; align-items:center; gap:18px; font-weight:700; font-size:38px; line-height:1.15; }}
.row.big {{ font-size:44px; }}
.row + .row {{ margin-top:11px; }}
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
.stampwrap {{ position:absolute; right:4px; top:-6px; margin:0 !important; }}  /* sits in the (half-width) chip row */
.stampflow {{ transform-origin:left center; padding-top:6px; }}
.stamp {{ display:inline-block; transform:rotate(-6deg); border:6px solid {RED}; color:{RED}; border-radius:14px;
  font-weight:800; font-size:40px; letter-spacing:.04em; padding:4px 16px 0; background:rgba(255,248,238,.92); }}
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
        # only for a card already on screen when the insert starts (a card that starts after it is untouched)
        if q(card["start"]) < x["start"] and x["start"] + 0.3 < e <= x["end"] + 1.0:
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
