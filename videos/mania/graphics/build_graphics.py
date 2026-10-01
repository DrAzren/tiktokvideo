"""Generate the talking-head-recut composition for 'Fasa Mania dalam Bipolar Mood Disorder'.

Layout (1080x1920), as videos/ada-halusinasi-yang-normal: hair at y~445 on the source (y~417 at
the 1.07 punch-in), so the picture is shifted down SHIFT px under a deep-teal header band, its
top edge feathered into the band. Cards live in y 150-450 over the band; captions go just below
(y ~460-575, next stage), just above the hair (~y600); the chin lands at ~y1450, clear of
TikTok's bottom UI. No card is up while the BIPOLAR hero is matted behind the head (HERO).

Every card element lands on the word it illustrates: times are phrase anchors on the cut
(inserts.T over edit/cut_words.json), with a small lead so the motion *lands* on the word.
Cards that would still be up when a full-screen insert starts leave behind it.

Outputs: storyboard.json, public/cards/<id>.html, public/index.html
"""

import html
import json
from pathlib import Path

from inserts import HERO, ICON, LEAD, T
from inserts import build as build_inserts

W = Path(__file__).parent
PUB = W / "public"
FPS = 30
DUR = json.loads((W / "metadata.json").read_text())["duration"]
SHIFT = 180

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
    {"id": "c01-mitos", "start": 0.0, "end": HERO[0] - 0.1, "intent": "Hook — the myth: mania = personality/identity disorder", "pages": [
        (0.0, [
            ("kicker", chip("Mitos", RED), 0.0, "pop"),
            ("q", '<div class="title sm">Ramai salah faham, mania ialah…</div>', 0.0, "fade"),
            ("r1", row(ico("person"), '<span class="strikeword">Gangguan personaliti</span>'), at("personaliti"), "slide"),
            ("r2", row(ico("swap"), '<span class="strikeword">Identiti berubah-ubah</span>'), at("identiti"), "slide"),
            ("st", '<div class="stamp">TIDAK BENAR</div>', T("berubah ubah", end=True) - 0.08, "stamp"),
            ("#c01-mitos-r1 .strikeword", None, T("berubah ubah") + 0.05, "strikeword"),
            ("#c01-mitos-r2 .strikeword", None, T("berubah ubah") + 0.2, "strikeword"),
        ]),
    ]},
    {"id": "c02-soalan1", "start": HERO[1], "end": 10.6, "intent": "Q1 — what is bipolar?", "pages": [
        (HERO[1], [
            ("kicker", chip("Soalan #1"), HERO[1] + 0.03, "pop"),
            ("t", f'<div class="title">Apa itu {teal("bipolar")}?</div>', HERO[1] + 0.08, "slide"),
            ("r1", row(CHECK, "Salah satu penyakit mental", "row big"), at("penyakit mental"), "slide"),
        ]),
    ]},
    {"id": "c03-soalan2", "start": T("fasa mania ada") + 0.05, "end": T("apa yang berlaku") - 0.1, "intent": "Q2 — how long? daily, >= 1 week", "pages": [
        (T("fasa mania ada") + 0.05, [
            ("kicker", chip("Soalan #2"), T("fasa mania ada") + 0.1, "pop"),
            ("t", '<div class="title">Berapa lama?</div>', T("fasa mania ada") + 0.15, "slide"),
            ("s", '<div class="sub">Gejala mesti berlaku hari-hari</div>', at("hari hari"), "fade"),
            ("g", '<div class="steps">' + "".join(f'<span id="c03-d{k}" class="step day">{d}</span>' for k, d in enumerate("ISRKJSA"))
                  + '<span id="c03-w" class="step hi">≥ 1 minggu</span></div>', at("sekurang kurangnya"), "none"),
            *[(f"#c03-d{k}", None, at("sekurang kurangnya") + 0.07 * k, "pop") for k in range(7)],
            ("#c03-w", None, at("satu minggu", after=21.9), "pop"),
        ]),
        (T("kurang dari") - 0.15, [
            ("t2", f'<div class="title">Kurang {teal("1 minggu")}?</div>', at("kurang dari"), "slide"),
            ("s2", '<div class="title muted">Bukan fasa mania</div>', at("kita tak panggil"), "slide"),
        ]),
    ]},
    {"id": "c04-soalan3", "start": T("apa yang berlaku") - 0.1, "end": T("orang yang ada bipolar") - 0.1, "intent": "Q3 — what happens in the mania phase?", "pages": [
        (T("apa yang berlaku") - 0.1, [
            ("kicker", chip("Soalan #3"), T("apa yang berlaku") - 0.1, "pop"),
            ("t", f'<div class="title">Apa berlaku dalam {teal("fasa mania")}?</div>', at("apa yang berlaku"), "slide"),
        ]),
        (T("mood yang berlebihan") - 0.3, [
            ("r1", row(ico("up"), "Mood berlebihan", "row big"), at("mood yang berlebihan"), "slide"),
            ("r2", row(ico("star"), "Gairah &amp; penuh semangat", "row big"), at("gairah"), "slide"),
        ]),
    ]},
    {"id": "c05-gejala1", "start": T("orang yang ada bipolar") - 0.1, "end": T("dalam fasa mania individu") - 0.1, "intent": "Symptoms: talkative, cheerful", "pages": [
        (T("orang yang ada bipolar") - 0.1, [
            ("kicker", chip("Gejala"), T("orang yang ada bipolar") - 0.05, "pop"),
            ("r1", row(ico("speech"), "Lebih banyak bercakap", "row big"), at("lebih banyak bercakap"), "slide"),
            ("r2", row(ico("speech2"), "Susah nak berhenti", "row big"), at("susah nak stop"), "slide"),
            ("r3", row(ico("sun"), "Ceria &amp; optimistik melampau", "row big"), at("ceria"), "slide"),
        ]),
    ]},
    {"id": "c06-gejala2", "start": T("dalam fasa mania individu") - 0.1, "end": 57.0, "intent": "Symptoms: more activity, no risk thinking, overactive, little sleep", "pages": [
        (T("dalam fasa mania individu") - 0.1, [
            ("kicker", chip("Gejala"), T("dalam fasa mania individu") - 0.05, "pop"),
            ("r1", row(ico("run"), "Lebih banyak aktiviti", "row big"), at("lebih banyak aktiviti"), "slide"),
            ("r2", row(ico("warn"), "Tak fikir risiko", "row big"), at("tak memikirkan"), "slide"),
        ]),
        (T("dan mereka boleh") - 0.1, [
            ("r3", row(ico("bolt"), "Terlalu aktif", "row big"), at("terlalu aktif"), "slide"),
            ("r4", row(ico("moon"), "Kurang tidur", "row big"), at("kurang tidur"), "slide"),
        ]),
    ]},
    {"id": "c07-tenaga", "start": T("mereka rasa") - 0.05, "end": 62.0, "intent": "Symptoms: lots of energy, less need for sleep", "pages": [
        (T("mereka rasa") - 0.05, [
            ("kicker", chip("Gejala"), T("mereka rasa"), "pop"),
            ("r1", row(ico("battery"), "Rasa banyak tenaga", "row big"), at("banyak tenaga"), "slide"),
            ("r2", row(ico("moon"), "Kurang perlu tidur", "row big"), at("keperluan tidur"), "slide"),
        ]),
    ]},
    {"id": "c08-risiko", "start": T("fasa mania ni boleh"), "end": 76.0, "intent": "Risk-taking that makes no sense", "pages": [
        (T("fasa mania ni boleh"), [
            ("kicker", chip("Risiko", RED), T("fasa mania ni boleh") + 0.05, "pop"),
            ("t", f'<div class="title">Ambil risiko {teal("tak masuk akal")}</div>', at("risiko yang tidak"), "slide"),
        ]),
    ]},
    {"id": "c09-kes", "start": T("ada yang saya jumpa"), "end": 89.0, "intent": "A real case from the clinic", "pages": [
        (T("ada yang saya jumpa"), [
            ("kicker", chip("Kes sebenar"), T("ada yang saya jumpa") + 0.05, "pop"),
            ("t", '<div class="title">Tak pergi kerja…</div>', at("tak pergi kerja"), "slide"),
        ]),
    ]},
    {"id": "c10-cta", "start": T("kalau ada") - 0.02, "end": DUR, "intent": "CTA — questions in the comments", "pages": [
        (T("kalau ada") - 0.02, [
            ("kicker", chip("Ada soalan?"), T("kalau ada"), "pop"),
            ("t", f'<div class="title xl" style="color:{TEAL}">Tanya di komen</div>', at("boleh tanya"), "pop"),
            ("s", '<div class="sub strong">Take care!</div>', at("take care"), "slide"),
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
.step.day {{ min-width:62px; padding:8px 0; text-align:center; font-size:34px; }}
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
    top = {}                                 # an element that lands early must not shrink the panel back
    for k, (t, h, p) in enumerate(ev):
        top[p] = max(top.get(p, 0), h)
        ev[k] = (t, top[p], p)
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
    for c in CARDS:                      # the matted hero window stays clear
        assert card_end(c) <= HERO[0] or q(c["start"]) >= HERO[1], c["id"]
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
