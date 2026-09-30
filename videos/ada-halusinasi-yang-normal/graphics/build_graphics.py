"""Generate the talking-head-recut composition for 'Ada Halusinasi Yang Normal'.

Layout (1080x1920): the framing has little headroom (hair at y~280), so the picture is shifted
down SHIFT px under a deep-teal header band, its top edge feathered into the band. Cards live
in y 150-450 over the band; captions go just below (y ~460-575, next stage), just above the
hair; the chin lands at ~y1510, clear of TikTok's bottom UI.

Every card element lands on the word it illustrates: times are phrase anchors on the cut
(inserts.T over edit/cut_words.json), with a small lead so the motion *lands* on the word.
Cards that would still be up when a full-screen insert starts leave behind it.

Outputs: storyboard.json, public/cards/<id>.html, public/index.html
"""

import html
import json
from pathlib import Path

from inserts import ICON, LEAD, T
from inserts import build as build_inserts

W = Path(__file__).parent
PUB = W / "public"
FPS = 30
DUR = json.loads((W / "metadata.json").read_text())["duration"]
SHIFT = 320

TEAL, DEEP, MINT, CREAM, INK, RED, MUTED = "#0E5E6F", "#08323C", "#5EEAD4", "#FFF8EE", "#0B1F2A", "#E5484D", "#6B7C85"

CHECK = '<svg viewBox="0 0 24 24" class="ico"><circle cx="12" cy="12" r="11" fill="%s"/><path d="M7 12.5l3.2 3.2L17.5 8.5" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>' % TEAL
ARROW = '<svg viewBox="0 0 24 24" class="arr"><path d="M12 4v15M5.5 12.5L12 19l6.5-6.5" stroke="%s" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>' % TEAL


def ico(name):
    """A line icon from inserts.ICON on a small teal disc, sized for card rows."""
    return (f'<span class="cdisc"><svg viewBox="0 0 48 48"><g stroke="#fff" stroke-width="3.6" stroke-linecap="round" '
            f'stroke-linejoin="round" fill="none">{ICON[name]}</g></svg></span>')


def q(t: float) -> float:
    return round(round(min(max(t, 0.0), DUR) * FPS) / FPS, 4)


def chip(text, color=TEAL):
    return f'<span class="chip" style="background:{color}">{html.escape(text)}</span>'


def row(icon, text, cls="row"):
    return f'<div class="{cls}">{icon}<span>{text}</span></div>'


def teal(t):
    return f'<span style="color:{TEAL}">{t}</span>'


def at(phrase, after=0.0):
    return T(phrase, after) - LEAD


# element: (key, html, t_abs, anim)   anim in {"pop","slide","fade","strikeword","stamp","none"}
# pages:   [(t_in, [elements])] — pages crossfade inside one persistent panel
CARDS = [
    {"id": "c01-hook", "start": 0.0, "end": 14.0, "intent": "Hook — have you experienced these?", "pages": [
        (0.0, [
            ("kicker", chip("Pernah alami?"), 0.0, "pop"),
            ("r1", row(ico("ear"), "Suara panggil nama anda"), 0.0, "slide"),
            ("r2", row(ico("speech"), "Bisikan negatif yang jelas"), at("berbisik"), "slide"),
            ("r3", row(ico("person"), "Bayang hitam lalu"), at("nampak"), "slide"),
        ]),
    ]},
    {"id": "c02-soalan", "start": T("tapi adakah"), "end": T("definisi") - 0.15, "intent": "The question", "pages": [
        (T("tapi adakah"), [
            ("kicker", chip("Soalan"), T("tapi adakah") + 0.02, "pop"),
            ("q1", '<div class="title sm">Adakah halusinasi…</div>', at("adakah"), "fade"),
            ("t", f'<div class="title">hanya berlaku pada {teal("pesakit mental?")}</div>', at("hanya berlaku"), "slide"),
        ]),
    ]},
    {"id": "c03-definisi", "start": T("definisi") - 0.15, "end": 29.0, "intent": "Definition", "pages": [
        (T("definisi") - 0.15, [
            ("kicker", chip("Definisi"), T("definisi") - 0.1, "pop"),
            ("t0", '<div class="title sm">Halusinasi bermaksud</div>', at("halusinasi bermaksud"), "slide"),
            ("t", f'<div class="title xl" style="color:{TEAL}">Persepsi deria</div>', at("persepsi"), "pop"),
        ]),
        (T("tanpa rangsangan") - 0.3, [
            ("t2", f'<div class="title">tanpa {teal("rangsangan sebenar")}</div>', at("tanpa rangsangan"), "slide"),
            ("s2", '<div class="sub en">“without any external stimulation”</div>', at("without"), "fade"),
        ]),
    ]},
    {"id": "c04-mitos", "start": T("halusinasi ini bukannya") - 0.15, "end": 41.0, "intent": "Myth: only mental patients — NOT TRUE", "pages": [
        (T("halusinasi ini bukannya") - 0.15, [
            ("kicker", chip("Mitos", RED), T("halusinasi ini bukannya") - 0.1, "pop"),
            ("t", '<div class="title"><span class="strikeword">Hanya pesakit mental</span></div>', T("halusinasi ini bukannya"), "slide"),
            ("st", '<div class="stamp">TIDAK BENAR</div>', at("bukannya"), "stamp"),
            ("#c04-mitos-t .strikeword", None, T("bukannya") + 0.15, "strikeword"),
            ("s", '<div class="sub">cth: skizofrenia &amp; gangguan mental lain</div>', at("skizofrenia"), "fade"),
        ]),
    ]},
    {"id": "c05-contoh1", "start": T("contoh yang pertama") - 0.1, "end": 55.0, "intent": "Example 1: hypnagogic", "pages": [
        (T("contoh yang pertama") - 0.1, [
            ("kicker", chip("Contoh #1"), T("contoh yang pertama"), "pop"),
            ("t0", '<div class="title sm">Halusinasi sebelum tidur</div>', at("halusinasi yang kita panggil"), "slide"),
            ("t", f'<div class="title xl" style="color:{TEAL}">Hypnagogic</div>', at("hypnagogic"), "pop"),
            ("g", '<div class="steps">'
                  '<span id="c05-s1" class="step">Bayangan</span><span id="c05-a1" class="sep">·</span>'
                  '<span id="c05-s2" class="step">Suara</span><span id="c05-a2" class="sep">→</span>'
                  '<span id="c05-s3" class="step hi">Sebelum tidur</span></div>', at("bayangan"), "none"),
            ("#c05-s1", None, at("bayangan"), "pop"),
            ("#c05-a1", None, at("atau suara"), "fade"),
            ("#c05-s2", None, at("suara yang muncul"), "pop"),
            ("#c05-a2", None, at("sebelum kita tidur") - 0.1, "fade"),
            ("#c05-s3", None, at("sebelum kita tidur"), "pop"),
        ]),
    ]},
    {"id": "c06-normal", "start": T("buka mata", end=True) + 0.1, "end": 60.0, "intent": "That's normal, not a sign of illness", "pages": [
        (T("buka mata", end=True) + 0.1, [
            ("kicker", chip("Realiti"), T("buka mata", end=True) + 0.15, "pop"),
            ("a", row(CHECK, f"Itu {teal('normal')}", "row big"), at("itu normal"), "slide"),
            ("b", row(CHECK, "Tak semestinya tanda penyakit", "row big"), at("tak semestinya"), "slide"),
        ]),
    ]},
    {"id": "c07-contoh3", "start": T("ada juga halusinasi yang berlaku akibat") - 0.1, "end": 70.0, "intent": "Example 3: sleep deprivation", "pages": [
        (T("ada juga halusinasi yang berlaku akibat") - 0.1, [
            ("kicker", chip("Contoh #3"), T("ada juga halusinasi yang berlaku akibat"), "pop"),
            ("t", f'<div class="title">Akibat {teal("kurang tidur")}</div>', at("akibat seorang"), "slide"),
        ]),
    ]},
    {"id": "c08-overload", "start": T("otak boleh jadi") - 0.1, "end": 79.0, "intent": "The brain overloads and creates images/sounds", "pages": [
        (T("otak boleh jadi") - 0.1, [
            ("kicker", chip("Otak overload"), T("otak boleh jadi"), "pop"),
            ("t", f'<div class="title">Cipta {teal("imej &amp; bunyi")}</div>', at("mencipta"), "slide"),
            ("s", '<div class="sub">yang sebenarnya tak wujud</div>', at("tak wujud pun", after=76.0), "fade"),
        ]),
    ]},
    {"id": "c09-bantuan", "start": T("jangan takut untuk") - 0.35, "end": T("kesimpulannya") - 0.1, "intent": "Don't be afraid to get help", "pages": [
        (T("jangan takut untuk") - 0.35, [
            ("kicker", chip("Ingat"), T("jangan takut untuk") - 0.3, "pop"),
            ("t", f'<div class="title">Jangan takut {teal("dapatkan bantuan")}</div>', at("jangan takut untuk"), "slide"),
        ]),
    ]},
    {"id": "c10-kesimpulan", "start": T("kesimpulannya") - 0.1, "end": 103.0, "intent": "Conclusion", "pages": [
        (T("kesimpulannya") - 0.1, [
            ("kicker", chip("Kesimpulan"), T("kesimpulannya"), "pop"),
            ("t", f'<div class="title">Tak semua {teal("halusinasi")}</div>', at("tak semua"), "slide"),
            ("s", '<div class="title muted">tanda sakit mental</div>', at("tanda sakit"), "slide"),
        ]),
    ]},
    {"id": "c11-cta", "start": T("jangan lupa follow") - 0.2, "end": DUR, "intent": "CTA — follow, comment", "pages": [
        (T("jangan lupa follow") - 0.2, [
            ("kicker", chip("Follow"), T("jangan lupa follow") - 0.1, "pop"),
            ("t", f'<div class="title">Lebih banyak ilmu {teal("kesihatan mental")}</div>', at("lebih banyak"), "slide"),
        ]),
        (T("apa apa soalan") - 0.15, [
            ("t3", f'<div class="title xl" style="color:{TEAL}">Ada soalan?</div>', at("apa apa soalan"), "pop"),
            ("s3", f'<div class="sub strong">Komen di bawah {ARROW}</div>', at("di ruang komen"), "slide"),
        ]),
    ]},
]

CARD_CSS = f"""
.card-host .card {{ position:relative; width:100%; height:100%; }}
.panel {{ position:absolute; left:60px; top:150px; width:960px; display:grid; background:{CREAM}; border-radius:34px;
  box-shadow:0 22px 60px rgba(4,18,24,.40), 0 2px 0 rgba(255,255,255,.6) inset; padding:28px 36px 30px;
  font-family:'Plus Jakarta Sans', sans-serif; color:{INK}; overflow:hidden; }}
.panel::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:12px; background:{TEAL}; }}
.page {{ grid-area:1/1; position:relative; align-self:start; }}
.page > * + * {{ margin-top:12px; }}
.chip {{ display:inline-block; color:#fff; font-weight:800; font-size:30px; letter-spacing:.07em; text-transform:uppercase;
  padding:8px 20px 7px; border-radius:999px; }}
.title {{ font-weight:800; font-size:54px; line-height:1.08; letter-spacing:-.015em; }}
.title.sm {{ font-size:40px; font-weight:700; color:#33434B; }}
.title.xl {{ font-size:80px; letter-spacing:-.02em; line-height:1.0; }}
.title.muted {{ color:{MUTED}; font-size:46px; }}
.sub {{ font-weight:700; font-size:36px; color:#44525A; }}
.sub.en {{ font-style:italic; font-weight:500; color:{TEAL}; }}
.sub.strong {{ color:{INK}; display:flex; align-items:center; gap:14px; font-size:40px; }}
.row {{ display:flex; align-items:center; gap:18px; font-weight:700; font-size:38px; line-height:1.15; }}
.row.big {{ font-size:44px; }}
.row + .row {{ margin-top:10px; }}
.ico {{ width:42px; height:42px; flex:none; }}
.cdisc {{ width:46px; height:46px; flex:none; border-radius:50%; background:{TEAL}; display:inline-flex; align-items:center; justify-content:center; }}
.cdisc svg {{ width:30px; height:30px; }}
.arr {{ width:44px; height:44px; }}
.steps {{ display:flex; align-items:center; flex-wrap:wrap; gap:12px; font-weight:800; font-size:38px; }}
.step {{ display:inline-block; padding:8px 20px; border-radius:16px; background:#E3F4F1; color:{TEAL}; }}
.step.hi {{ background:{TEAL}; color:#fff; }}
.sep {{ color:{MUTED}; font-size:38px; font-weight:800; }}
.strikeword {{ background:linear-gradient({RED},{RED}) left 55%/0% 6px no-repeat; }}
.stampwrap {{ position:absolute; right:0; top:-12px; margin:0 !important; }}
.stamp {{ display:inline-block; transform:rotate(-6deg); border:6px solid {RED}; color:{RED}; border-radius:14px;
  font-weight:800; font-size:34px; letter-spacing:.04em; padding:4px 14px 0; background:rgba(255,248,238,.94); }}
"""


STAMPWRAP = ' class="stampwrap"'
HEIGHTS_FILE = W / "page_heights.json"      # written by measure_pages.cjs (real browser layout)
HEIGHTS = json.loads(HEIGHTS_FILE.read_text()) if HEIGHTS_FILE.exists() else {}
PANEL_PAD = 58                              # panel padding top + bottom


def height_events(card):
    """(time, panel height, page) steps: the panel grows as each top-level element lands and resizes
    on page changes, so it never shows empty space for content that hasn't been spoken yet."""
    ev = []
    for p, (t_in, els) in enumerate(card["pages"]):
        hs = HEIGHTS.get(f"{card['id']}-page{p}")
        if not hs:
            continue
        run = 0
        for k, (key, frag, t, anim) in enumerate(e for e in els if e[1] is not None):
            run = max(run, hs[k])            # absolutely-positioned stamps measure short: keep the max
            ev.append((max(t, t_in, card["start"]), run + PANEL_PAD, p))
    ev.sort()
    out = []
    for t, h, p in ev:
        if out and out[-1][2] == p and t - out[-1][0] < 0.05:
            out[-1] = (out[-1][0], max(h, out[-1][1]), p)
        else:
            out.append((t, h, p))
    return out


def card_fragment(card) -> str:
    cid = card["id"]
    pages = []
    for p, (t_in, els) in enumerate(card["pages"]):
        inner = "".join(
            f'<div id="{cid}-{key}"{STAMPWRAP if anim == "stamp" else ""} data-anim="{anim}">{frag}</div>'
            for key, frag, t, anim in els if frag is not None)
        pages.append(f'<div class="page" id="{cid}-page{p}">{inner}</div>')
    return (f'<div class="card" data-card-id="{cid}"><div class="root">'
            f'<div class="panel" id="{cid}-panel">{"".join(pages)}</div></div></div>')


INSERTS, INS_HOSTS, INS_JS, INS_CSS = build_inserts()


def card_end(card) -> float:
    """A card still up when a full-screen insert starts leaves behind it (never flashes back after)."""
    e = q(card["end"])
    for x in INSERTS:
        if q(card["start"]) < x["start"] and x["start"] + 0.3 < e:
            return round(x["start"] + 0.35, 4)
    return e


def timeline_js(card) -> list[str]:
    cid, s = card["id"], card["start"]
    host = f'.card-host[data-card-id="{cid}"]'
    panel = f"#{cid}-panel"
    js = [f"// {cid}: {card['intent']}", f'tl.set(\'{host}\', {{visibility:"visible", opacity:1}}, {q(s)});']
    if s <= 0.001:   # the hook is on screen at frame 0 (first frame = thumbnail / first impression)
        js.append(f"tl.set('{panel}', {{opacity:1, y:0, scale:1}}, 0);")
    else:
        js.append(f"tl.fromTo('{panel}', {{opacity:0, y:-36, scale:0.97}}, {{opacity:1, y:0, scale:1, duration:0.45, ease:'power3.out'}}, {q(s)});")
    hev = height_events(card)
    if hev:
        js.append(f"tl.set('{panel}', {{height:{hev[0][1]}}}, {q(s) if s > 0.001 else 0});")
        prev_p = hev[0][2]
        for t, h, p in hev[1:]:
            if p != prev_p:   # page change: resize with the crossfade
                js.append(f"tl.to('{panel}', {{height:{h}, duration:0.36, ease:'power2.inOut'}}, {q(t - 0.3)});")
            else:
                js.append(f"tl.to('{panel}', {{height:{h}, duration:0.34, ease:'power3.out'}}, {q(max(t - 0.04, s))});")
            prev_p = p
    for p, (t_in, els) in enumerate(card["pages"]):
        pg = f"#{cid}-page{p}"
        if p == 0:
            js.append(f"tl.set('{pg}', {{opacity:1}}, {q(s)});")
        else:
            js.append(f"tl.to('#{cid}-page{p - 1}', {{opacity:0, y:-14, duration:0.28, ease:'power2.in'}}, {q(t_in - 0.28)});")
            js.append(f"tl.fromTo('{pg}', {{opacity:0, y:14}}, {{opacity:1, y:0, duration:0.32, ease:'power3.out'}}, {q(t_in)});")
        for key, frag, t, anim in els:
            sel = f"#{cid}-{key}" if not key.startswith("#") else key
            T_ = q(max(t, s + 0.05))
            if t <= 0.001:
                js.append(f"tl.set('{sel}', {{opacity:1}}, 0);")
            elif anim == "pop":
                js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.34, ease:'back.out(1.8)'}}, {T_});")
            elif anim == "slide":
                js.append(f"tl.fromTo('{sel}', {{opacity:0, x:-44}}, {{opacity:1, x:0, duration:0.38, ease:'power3.out'}}, {T_});")
            elif anim == "fade":
                js.append(f"tl.fromTo('{sel}', {{opacity:0}}, {{opacity:1, duration:0.3, ease:'power2.out'}}, {T_});")
            elif anim == "strikeword":
                js.append(f"tl.fromTo('{sel}', {{backgroundSize:'0% 6px'}}, {{backgroundSize:'100% 6px', duration:0.35, ease:'power2.inOut'}}, {T_});")
            elif anim == "stamp":
                js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:1.9}}, {{opacity:1, scale:1, duration:0.26, ease:'power4.out'}}, {T_});")
    E = card_end(card)
    js.append(f"tl.to('{panel}', {{opacity:0, y:-24, duration:0.3, ease:'power2.in'}}, {round(E - 0.3, 4)});")
    js.append(f'tl.set(\'{host}\', {{visibility:"hidden"}}, {E});')
    return js


def main() -> None:
    (PUB / "cards").mkdir(parents=True, exist_ok=True)
    for a, b in zip(CARDS, CARDS[1:]):   # one card at a time
        assert card_end(a) <= q(b["start"]) + 0.05, (a["id"], card_end(a), b["id"], q(b["start"]))
    storyboard = {
        "schemaVersion": 3,
        "composition": {"fps": FPS, "width": 1080, "height": 1920, "durationSeconds": DUR,
                        "layout": "portrait", "themeId": "custom-teal", "seed": 7},
        "videoTrack": {"sourcePath": "input-video.mp4", "startSec": 0, "endSec": DUR,
                       "bounds": {"x": 0, "y": SHIFT, "width": 1080, "height": 1920}},
        "subtitles": {"enabled": False},
        "cards": [{"id": c["id"], "intent": c["intent"], "startSec": q(c["start"]), "endSec": card_end(c),
                   "zone": "headroom", "contentHints": {"pages": len(c["pages"])}} for c in CARDS],
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
        f'@font-face{{font-family:"Plus Jakarta Sans";src:url("fonts/PlusJakartaSans-{w}.woff2") format("woff2");'
        f'font-weight:{w};font-style:normal;font-display:block;}}' for w in (500, 700, 800))
    page = f"""<!doctype html>
<html lang="ms">
<head>
<meta charset="utf-8" />
<style>
{fonts}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; padding:0; width:100%; height:100%; overflow:hidden; background:{DEEP};
  font-family:"Plus Jakarta Sans", sans-serif; }}
#stage {{ position:relative; width:1080px; height:1920px; overflow:hidden; background:{DEEP}; }}
/* header band: the picture sits {SHIFT}px lower; its top edge fades into the band */
#band {{ position:absolute; left:0; top:0; width:1080px; height:{SHIFT + 140}px;
  background:radial-gradient(90% 120% at 78% 0%, #13707F 0%, rgba(19,112,127,0) 60%), linear-gradient(180deg, #05222A 0%, {DEEP} 45%, #0C5160 100%); }}
.video-wrapper {{ position:absolute; left:0; top:{SHIFT}px; width:1080px; height:1920px; overflow:hidden;
  -webkit-mask-image:linear-gradient(180deg, rgba(0,0,0,0) 0px, #000 120px); mask-image:linear-gradient(180deg, rgba(0,0,0,0) 0px, #000 120px); }}
.video-wrapper video {{ width:100%; height:100%; object-fit:cover; }}
.card-host {{ position:absolute; pointer-events:none; overflow:hidden; }}
.page {{ opacity:0; }}
{CARD_CSS}
{INS_CSS}
</style>
</head>
<body>
<div id="stage" data-composition-id="talking-head-recut" data-start="0" data-duration="{DUR}" data-fps="{FPS}" data-width="1080" data-height="1920">
  <div id="band"></div>
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
        print(f"  {c['id']:15s} {q(c['start']):7.2f} - {card_end(c):7.2f}")
    for x in INSERTS:
        print(f"  {x['id']:15s} {x['start']:7.2f} - {x['end']:7.2f}  ({x['kind']})")


if __name__ == "__main__":
    main()
