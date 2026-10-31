"""Generate the talking-head-recut composition for '3 Ubat Psikiatri Kuruskan Badan'.

Same visual system as videos/ward-psikiatri (teal / cream / mint, Plus Jakarta Sans), so the
channel reads as one series.

Layout (1080x1920, measured on the cut at 5s / 70s): hair top ~y500 (y~470 at the 1.07 punch-in),
eyebrows ~y800, chin ~y1230. Cards live in the car-roof headroom (y 150 to <= 560: they may
cover the top of the hair, never the face). Captions go on the chest band (~y1270-1500) in
the next stage. The bottom ~20% is TikTok UI.

Every time is anchored to a phrase in edit/cut_words.json (T()), so the graphics re-time
themselves when the cut changes. Each element lands on its spoken word (LEAD before it).

Full-screen inserts (picture only; the voice keeps running, captions land on top later):
  b1  Higgsfield Seedance 2.5 clip (pharmacy blister pack), "Ilustrasi AI" tag
  m1  fluoxetine weight curve: dips early in treatment, climbs back long-term, PERLU MONITOR
  m2  "JANGAN pilih ubat sebab nak KURUS semata-mata"

Outputs: storyboard.json, public/cards/<id>.html, public/index.html
"""

import html
import json
from pathlib import Path

W = Path(__file__).parent
PUB = W / "public"
FPS = 30
DUR = json.loads((W / "metadata.json").read_text())["duration"]
WORDS = json.loads((W.parent / "edit" / "cut_words.json").read_text())
LEAD = 0.12  # element starts this much before its word so it lands on it

TEAL, DEEP, MINT, CREAM, INK, RED, MUTED, AMBER = ("#0E5E6F", "#08323C", "#5EEAD4", "#FFF8EE", "#0B1F2A",
                                                   "#E5484D", "#6B7C85", "#E9A23B")


def T(phrase: str, after: float = 0.0, end: bool = False) -> float:
    """Start (or end) time of the first occurrence of `phrase` at/after `after` on the cut."""
    toks = phrase.split()
    for i in range(len(WORDS) - len(toks) + 1):
        if WORDS[i]["start"] >= after and [w["text"] for w in WORDS[i:i + len(toks)]] == toks:
            return WORDS[i + len(toks) - 1]["end"] if end else WORDS[i]["start"]
    raise KeyError(phrase)


def q(t: float) -> float:
    return round(round(min(max(t, 0.0), DUR) * FPS) / FPS, 4)


def svg(body: str, fill: str, cls: str = "ico") -> str:
    return (f'<svg viewBox="0 0 24 24" class="{cls}"><circle cx="12" cy="12" r="11" fill="{fill}"/>'
            f'<g stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>')


CHECK = svg('<path d="M7 12.5l3.2 3.2L17.5 8.5"/>', TEAL)
DOWN = svg('<path d="M12 6.5v11M7.5 13l4.5 4.5 4.5-4.5"/>', TEAL)
UP = svg('<path d="M12 17.5v-11M7.5 11l4.5-4.5 4.5 4.5"/>', RED)
WARN = svg('<path d="M12 6.8v6.4"/><circle cx="12" cy="16.9" r=".6" fill="#fff"/>', AMBER)
DOT = '<svg viewBox="0 0 24 24" class="ico"><circle cx="12" cy="12" r="6" fill="%s"/></svg>' % MUTED
PERSON = svg('<circle cx="12" cy="9" r="3"/><path d="M6.5 18c.8-3 3-4.5 5.5-4.5s4.7 1.5 5.5 4.5"/>', TEAL)
ARROW = ('<svg viewBox="0 0 24 24" class="arr"><path d="M12 4v15M5.5 12.5L12 19l6.5-6.5" stroke="%s" stroke-width="3" '
         'fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>' % TEAL)


def chip(text, color=TEAL):
    return f'<span class="chip" style="background:{color}">{html.escape(text)}</span>'


def row(icon, text, cls="row"):
    return f'<div class="{cls}">{icon}<span>{text}</span></div>'


# Cards that end during an insert exit BEHIND it (0.35s overlap): intentional layering, so the card
# hosts carry data-layout-allow-occlusion.

# ---- full-screen inserts ------------------------------------------------------------------
def build_inserts():
    I = []
    s = T("ubat ubat yang sering")
    I.append({"id": "b1-pil", "kind": "video", "src": "broll/pills.mp4",
              "start": q(s - 0.1), "end": q(T("penurunan berat badan", end=True) + 0.12)})

    # m1: fluoxetine and weight over time
    s = T("kadang kadang boleh buat")
    down_end = T("rawatan tu")              # the dip is drawn over "turun berat badan masa awal-awal rawatan"
    up0, up1 = T("jangka panjang"), T("sedikit lah", end=True)
    mon = T("kena monitor")
    I.append({"id": "m1-kurva", "kind": "mg", "start": q(s - 0.1), "end": q(T("yang penting") + 0.5), "body": f"""
      <div class="head"><div class="mg-chip" id="m1-c">Fluoxetine &amp; berat badan</div>
        <div class="mg-title" id="m1-t">Awal rawatan <span class="mint">vs</span><br/>jangka panjang</div></div>
      <svg class="chart" viewBox="0 0 920 560" style="left:80px; top:600px; width:920px; height:560px">
        <line x1="20" y1="170" x2="900" y2="170" stroke="rgba(255,248,238,.45)" stroke-width="4" stroke-dasharray="14 14" id="m1-base"/>
        <path id="m1-curve" pathLength="100" d="M20 170 C130 170 210 390 340 400 C450 408 520 360 600 270 C690 170 790 128 900 118"
          stroke="{MINT}" stroke-width="12" stroke-linecap="round" fill="none"/>
        <circle id="m1-dot1" cx="340" cy="400" r="20" fill="{MINT}" stroke="{DEEP}" stroke-width="7"/>
        <circle id="m1-dot2" cx="900" cy="118" r="20" fill="{RED}" stroke="{DEEP}" stroke-width="7"/>
        <line x1="20" y1="540" x2="900" y2="540" stroke="rgba(255,248,238,.35)" stroke-width="4"/>
      </svg>
      <div class="axis" id="m1-ax" style="left:96px; top:574px">Berat asal</div>
      <div class="tag-dn" id="m1-l1" style="left:80px; top:1030px">{DOWN.replace('class="ico"', 'class="ico lg"')}<span>Awal rawatan:<br/>berat turun</span></div>
      <div class="note" id="m1-n1" style="left:96px; top:1168px">hilang selera makan</div>
      <div class="tag-up" id="m1-l2" style="left:560px; top:1030px">{UP.replace('class="ico"', 'class="ico lg"')}<span>Jangka panjang:<br/>boleh naik balik</span></div>
      <div class="stamp-lg mint-stamp" id="m1-st" style="left:300px; top:470px">PERLU MONITOR</div>""",
              "anims": [("#m1-c", s - 0.08, "pop"), ("#m1-t", s - 0.02, "rise"), ("#m1-base", s + 0.2, "fade"),
                        ("#m1-ax", s + 0.25, "fade"),
                        ("#m1-curve", T("turun berat badan", after=s) - 0.3, ("draw", 100, 45, down_end - T("turun berat badan", after=s) + 0.3)),
                        ("#m1-dot1", T("awal awal", after=s) - LEAD, "pop"),
                        ("#m1-l1", T("awal awal", after=s) - LEAD, "rise"),
                        ("#m1-n1", T("hilang selera", after=s) - LEAD, "fade"),
                        ("#m1-curve", up0 - 0.1, ("draw", 45, 0, up1 - up0)),
                        ("#m1-l2", T("naik balik", after=s) - LEAD, "rise"),
                        ("#m1-dot2", T("naik balik", after=s) + 0.3, "pop"),
                        ("#m1-st", mon - LEAD, "stamp")]})

    # m2: the line the whole video builds to
    s = T("jangan pilih ubat")
    I.append({"id": "m2-jangan", "kind": "mg", "start": q(s - 0.1), "end": q(T("berbincang") - 0.02), "body": f"""
      <div class="center">
        <div class="mg-chip red" id="m2-c">Ingat</div>
        <div class="huge" id="m2-a">JANGAN</div>
        <div class="mg-sub big" id="m2-b">pilih ubat sebab nak</div>
        <div class="huge mint" id="m2-d">KURUS</div>
        <div class="mg-sub big" id="m2-e">semata-mata</div>
      </div>""",
              "anims": [("#m2-c", s - 0.1, "pop"), ("#m2-a", s - LEAD + 0.02, "stamp"),
                        ("#m2-b", T("pilih ubat", after=s) - LEAD, "rise"),
                        ("#m2-d", T("kurus", after=s) - LEAD, "stamp"),
                        ("#m2-e", T("semata mata", after=s) - LEAD, "rise")]})

    I.sort(key=lambda x: x["start"])
    for a, b in zip(I, I[1:]):
        assert b["start"] >= a["end"] - 0.01, (a["id"], b["id"])
    for x in I:
        assert x["end"] - x["start"] >= 1.8, (x["id"], x["end"] - x["start"])
    return I


INSERTS = build_inserts()


def ins(iid):
    return next(x for x in INSERTS if x["id"] == iid)


# ---- cards ------------------------------------------------------------------------------
# element: (key, html, t_abs, anim)   anim in {"pop","slide","fade","stamp","none"}
# pages:   [(t_in, [elements])] — pages crossfade inside one persistent panel
L = LEAD
CARDS = [
    {"id": "c01-hook", "start": 0.0, "end": ins("b1-pil")["start"] + 0.35, "intent": "Hook: the topic, on screen from frame 0", "pages": [
        (0.0, [
            ("kicker", chip("Ubat psikiatri"), 0.0, "pop"),
            ("t1", '<div class="title sm">3 ubat yang dikaitkan dengan</div>', 0.0, "slide"),
            ("t2", f'<div class="title xl hook" style="color:{TEAL}">PENURUNAN<br/>BERAT BADAN</div>', 0.0, "pop"),
            ("who", row(PERSON, "Dr Azren · Doktor, Jabatan Psikiatri", "row who"), T("doktor") - L, "slide"),
        ]),
    ]},
    {"id": "c02-bupropion", "start": ins("b1-pil")["end"] - 0.05, "end": T("yang kedua") - 0.1, "intent": "Drug 1: bupropion", "pages": [
        (ins("b1-pil")["end"] - 0.05, [
            ("kicker", chip("Ubat #1"), ins("b1-pil")["end"], "pop"),
            ("t", f'<div class="title xl" style="color:{TEAL}">BUPROPION</div>', T("bupropion") - L, "pop"),
            ("s", '<div class="sub">Sejenis antidepresan</div>', T("sejenis antidepressant") - L, "slide"),
            ("r", row(DOWN, "Boleh kurangkan selera makan", "row big"), T("kurangkan selera") - L, "slide"),
        ]),
        (T("biasanya") - 0.1, [
            ("kicker2", chip("Biasanya digunakan untuk"), T("biasanya"), "pop"),
            ("r1", row(CHECK, "Merawat kemurungan", "row big"), T("merawat kemurungan") - L, "slide"),
            ("r2", row(CHECK, "Bantu berhenti merokok", "row big"), T("berhenti merokok") - L, "slide"),
        ]),
        (T("tapi ingat") - 0.1, [
            ("kicker3", chip("Tapi ingat", RED), T("tapi ingat"), "pop"),
            ("t3", '<div class="title">Bukan semua orang turun berat</div>', T("bukan semua") - L, "slide"),
            ("s3", '<div class="sub">Bergantung pada badan masing-masing</div>', T("bergantung") - L, "slide"),
        ]),
    ]},
    {"id": "c03-topiramate", "start": T("yang kedua") - 0.1, "end": T("yang ketiga") - 0.12, "intent": "Drug 2: topiramate", "pages": [
        (T("yang kedua") - 0.1, [
            ("kicker", chip("Ubat #2"), T("yang kedua"), "pop"),
            ("t", f'<div class="title xl" style="color:{TEAL}">TOPIRAMATE</div>', T("topiramid") - L, "pop"),
            ("s", '<div class="sub">Asalnya ubat sawan</div>', T("asalnya") - L, "slide"),
            ("r", row(DOT, "Kadang-kadang untuk masalah mood", "row"), T("kadang kadang guna") - L, "slide"),
        ]),
        (T("dia boleh turunkan") - 0.1, [
            ("kicker2", chip("Kesan pada berat badan"), T("dia boleh turunkan"), "pop"),
            ("r1", row(DOWN, "Turunkan berat badan", "row big"), T("turunkan berat") - L, "slide"),
            ("r2", row(CHECK, "Cepat rasa kenyang", "row big"), T("kenyang") - L, "slide"),
            ("r3", row(CHECK, "Kurang craving", "row big"), T("kurang craving") - L, "slide"),
        ]),
        (T("tapi kesan sampingan") - 0.1, [
            ("kicker3", chip("Kesan sampingan", RED), T("kesan sampingan"), "pop"),
            ("t3", '<div class="title">Lebih banyak sikit</div>', T("banyak sikit") - L, "slide"),
            ("w3", row(WARN, "Senang rasa semput — dos tinggi", "row big"), T("semput") - L, "slide"),
        ]),
    ]},
    {"id": "c04-fluoxetine", "start": T("yang ketiga") - 0.1, "end": ins("m1-kurva")["start"] + 0.35, "intent": "Drug 3: fluoxetine", "pages": [
        (T("yang ketiga") - 0.1, [
            ("kicker", chip("Ubat #3"), T("yang ketiga"), "pop"),
            ("t", f'<div class="title xl" style="color:{TEAL}">FLUOXETINE</div>', T("fluoxetine") - L, "pop"),
            ("s", '<div class="sub">SSRI yang paling biasa digunakan</div>', T("ssri") - L, "slide"),
            ("g", '<div class="grid"><span id="c04-p1" class="pill">Antidepresan</span>'
                  '<span id="c04-p2" class="pill">Anxiety</span></div>', T("ssri"), "none"),
            ("#c04-p1", None, T("antidepressant", after=46) - L, "pop"),
            ("#c04-p2", None, T("anxiety") - L, "pop"),
        ]),
    ]},
    {"id": "c05-penting", "start": ins("m1-kurva")["end"] - 0.05, "end": ins("m2-jangan")["start"] + 0.35, "intent": "Takeaway: every drug acts differently", "pages": [
        (ins("m1-kurva")["end"] - 0.05, [
            ("kicker", chip("Yang penting"), ins("m1-kurva")["end"], "pop"),
            ("t", f'<div class="title">Setiap ubat, kesan berbeza <span style="color:{TEAL}">untuk setiap orang</span></div>',
             T("setiap ubat") - L, "slide"),
        ]),
        (T("mungkin ketiga") - 0.1, [
            ("kicker2", chip("Ketiga-tiga ubat"), T("mungkin ketiga"), "pop"),
            ("g", '<div class="steps">'
                  '<span id="c05-s1" class="step">Bupropion</span>'
                  '<span id="c05-s2" class="step">Topiramate</span>'
                  '<span id="c05-s3" class="step">Fluoxetine</span></div>', T("mungkin ketiga"), "none"),
            ("#c05-s1", None, T("ketiga tiga") - L, "pop"),
            ("#c05-s2", None, T("tiga ubat") - L, "pop"),
            ("#c05-s3", None, T("ubat yang saya") - L, "pop"),
            ("r", row(UP, f'Setengah orang: berat boleh <b style="color:{RED}">naik</b>', "row big"), T("kenaikan berat") - L, "slide"),
        ]),
    ]},
    {"id": "c06-cta", "start": ins("m2-jangan")["end"] - 0.05, "end": DUR, "intent": "CTA: talk to your doctor; questions in the comments", "pages": [
        (ins("m2-jangan")["end"] - 0.05, [
            ("kicker", chip("Sentiasa"), ins("m2-jangan")["end"], "pop"),
            ("t", f'<div class="title">Bincang dengan <span style="color:{TEAL}">doktor</span></div>', T("berbincang") - L, "slide"),
            ("s", '<div class="sub">Rawatan paling sesuai untuk anda</div>', T("rawatan yang paling") - L, "slide"),
        ]),
        (T("apa apa soalan") - 0.1, [
            ("t3", f'<div class="title xl" style="color:{TEAL}">Ada soalan?</div>', T("apa apa soalan") - L, "pop"),
            ("s3", f'<div class="sub strong">Tanya di ruang komen {ARROW}</div>', T("tanya") - L, "slide"),
            ("d3", '<div class="disc-note">Info pendidikan · bukan nasihat perubatan</div>', T("komen") - 0.3, "fade"),
        ]),
    ]},
]


def tighten(cards, min_gap=0.6, lead=0.3):
    """No empty shells: a chip may not sit alone. If a page's kicker comes > min_gap before its
    first content, move the kicker (and the page / card entrance) to just before that content."""
    for c in cards:
        for p, (t_in, els) in enumerate(c["pages"]):
            kick = [i for i, e in enumerate(els) if e[0].startswith("kicker")]
            content = [e[2] for e in els if not e[0].startswith("kicker") and e[3] != "none"]
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
PANEL_PAD = 64
PANEL_TOP, PANEL_MAX_BOTTOM = 150, 560      # may cover the top of the hair, never the face


def page_h(cid, p):
    h = HEIGHTS.get(f"{cid}-page{p}")
    return None if h is None else h + PANEL_PAD


CSS = f"""
.card-host .card {{ position:relative; width:100%; height:100%; }}
.panel {{ position:absolute; left:60px; top:{PANEL_TOP}px; width:960px; display:grid; background:{CREAM}; border-radius:34px;
  box-shadow:0 22px 60px rgba(8,22,30,.30), 0 2px 0 rgba(255,255,255,.6) inset; padding:30px 38px 34px;
  font-family:'Plus Jakarta Sans', sans-serif; color:{INK}; overflow:hidden; }}
.panel::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:12px; background:{TEAL}; }}
.page {{ grid-area:1/1; position:relative; align-self:start; }}
.page > * + * {{ margin-top:14px; }}
.chip {{ display:inline-block; color:#fff; font-weight:800; font-size:30px; letter-spacing:.07em; text-transform:uppercase;
  padding:9px 20px 8px; border-radius:999px; }}
.title {{ font-weight:800; font-size:58px; line-height:1.08; letter-spacing:-.015em; }}
.title.sm {{ font-size:44px; font-weight:700; }}
.title.xl {{ font-size:84px; letter-spacing:-.02em; line-height:1.0; }}
.title.xl.hook {{ font-size:74px; }}
.sub {{ font-weight:700; font-size:38px; color:#44525A; }}
.sub.strong {{ color:{INK}; display:flex; align-items:center; gap:14px; }}
.row {{ display:flex; align-items:center; gap:18px; font-weight:700; font-size:38px; line-height:1.15; }}
.row.big {{ font-size:44px; }}
.row.who {{ font-size:32px; color:#44525A; }}
.row + .row {{ margin-top:11px; }}
.ico {{ width:44px; height:44px; flex:none; }}
.ico.lg {{ width:64px; height:64px; }}
.arr {{ width:44px; height:44px; }}
.grid {{ display:flex; flex-wrap:wrap; gap:14px; }}
.pill {{ display:inline-block; font-weight:700; font-size:36px; padding:12px 26px; border-radius:18px; background:#E3F4F1; color:{TEAL};
  border:2px solid rgba(14,94,111,.25); }}
.steps {{ display:flex; align-items:center; flex-wrap:wrap; gap:14px; font-weight:800; font-size:38px; }}
.step {{ display:inline-block; padding:10px 22px; border-radius:16px; background:{TEAL}; color:#fff; }}
.disc-note {{ font-weight:600; font-size:28px; color:{MUTED}; letter-spacing:.02em; }}

.ins {{ position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden; pointer-events:none; }}
.ins-in {{ position:absolute; inset:0; overflow:hidden; background:#000; }}
.ins-in video {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
.vid-shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.28) 0%, rgba(0,0,0,0) 16%,
  rgba(0,0,0,0) 60%, rgba(0,0,0,.30) 70%, rgba(0,0,0,.30) 80%, rgba(0,0,0,0) 90%); }}
.ai-tag {{ position:absolute; left:48px; top:160px; font:700 28px 'Plus Jakarta Sans'; letter-spacing:.08em; text-transform:uppercase;
  color:rgba(255,255,255,.92); background:rgba(0,0,0,.38); padding:7px 14px 6px; border-radius:10px; }}
.mg {{ position:absolute; inset:0; background:radial-gradient(120% 80% at 80% 10%, {TEAL} 0%, {DEEP} 62%, #051E25 100%);
  font-family:'Plus Jakarta Sans', sans-serif; color:{CREAM}; }}
.mg .mint {{ color:{MINT}; }}
.head {{ position:absolute; left:80px; top:160px; width:920px; }}
.mg-chip {{ display:inline-block; font-weight:800; font-size:30px; letter-spacing:.08em; text-transform:uppercase;
  padding:10px 22px 9px; border-radius:999px; background:{MINT}; color:{DEEP}; }}
.mg-chip.red {{ background:{RED}; color:#fff; }}
.mg-title {{ font-weight:800; font-size:76px; line-height:1.04; letter-spacing:-.02em; margin-top:22px; }}
.mg-sub {{ font-weight:700; font-size:44px; color:rgba(255,248,238,.82); margin-top:22px; }}
.mg-sub.big {{ font-size:60px; margin-top:10px; }}
.chart {{ position:absolute; overflow:visible; }}
#m1-curve {{ stroke-dasharray:100; stroke-dashoffset:100; }}
.axis {{ position:absolute; font-weight:700; font-size:30px; color:rgba(255,248,238,.7); letter-spacing:.04em; text-transform:uppercase; }}
.tag-dn, .tag-up {{ position:absolute; display:flex; align-items:center; gap:18px; padding:16px 26px 16px 18px; border-radius:24px;
  background:{CREAM}; color:{INK}; font-weight:800; font-size:38px; line-height:1.12; box-shadow:0 14px 34px rgba(0,0,0,.28); }}
.note {{ position:absolute; font-weight:700; font-size:36px; color:rgba(255,248,238,.85); font-style:italic; }}
.stamp-lg {{ position:absolute; display:inline-block; transform:rotate(-6deg); border:8px solid {RED}; color:{RED}; border-radius:18px;
  font-weight:800; font-size:70px; letter-spacing:.04em; padding:8px 26px 2px; background:rgba(255,248,238,.95); }}
.stamp-lg.mint-stamp {{ border-color:{AMBER}; color:#9A5B00; }}
.center {{ position:absolute; left:0; right:0; top:330px; text-align:center; }}
.huge {{ font-weight:800; font-size:190px; line-height:.98; letter-spacing:-.03em; margin-top:26px; }}
.huge.mint {{ color:{MINT}; font-size:210px; }}
"""

STAMPWRAP = {"stamp": ' class="stampflow"'}


def card_fragment(card) -> str:
    cid = card["id"]
    pages = []
    for p, (t_in, els) in enumerate(card["pages"]):
        inner = "".join(f'<div id="{cid}-{key}" data-anim="{anim}">{frag}</div>'
                        for key, frag, t, anim in els if frag is not None)
        pages.append(f'<div class="page" id="{cid}-page{p}">{inner}</div>')
    return (f'<div class="card" data-card-id="{cid}"><div class="root">'
            f'<div class="panel" id="{cid}-panel">{"".join(pages)}</div></div></div>')


def card_end(card) -> float:
    return q(card["end"])


def timeline_js(card) -> list[str]:
    cid, s = card["id"], card["start"]
    host = f'.card-host[data-card-id="{cid}"]'
    panel = f"#{cid}-panel"
    js = [f"// {cid}: {card['intent']}", f'tl.set(\'{host}\', {{visibility:"visible", opacity:1}}, {q(s)});']
    if s <= 0.001:   # the hook is fully on screen at frame 0 (thumbnail / first impression)
        js.append(f"tl.set('{panel}', {{opacity:1, y:0, scale:1}}, 0);")
    else:
        js.append(f"tl.fromTo('{panel}', {{opacity:0, y:-36, scale:0.97}}, {{opacity:1, y:0, scale:1, duration:0.45, ease:'power3.out'}}, {q(s)});")
    if page_h(cid, 0):
        js.append(f"tl.set('{panel}', {{height:{page_h(cid, 0)}}}, {q(s)});")
    for p, (t_in, els) in enumerate(card["pages"]):
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
            T_ = q(max(t, s + 0.05))
            if t <= 0.001:
                js.append(f"tl.set('{sel}', {{opacity:1}}, 0);")
            elif anim == "pop":
                js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.34, ease:'back.out(1.8)'}}, {T_});")
            elif anim == "slide":
                js.append(f"tl.fromTo('{sel}', {{opacity:0, x:-44}}, {{opacity:1, x:0, duration:0.38, ease:'power3.out'}}, {T_});")
            elif anim == "fade":
                js.append(f"tl.fromTo('{sel}', {{opacity:0}}, {{opacity:1, duration:0.3, ease:'power2.out'}}, {T_});")
    E = card_end(card)
    if E < DUR:
        js.append(f"tl.to('{panel}', {{opacity:0, y:-24, duration:0.3, ease:'power2.in'}}, {round(E - 0.3, 4)});")
        js.append(f'tl.set(\'{host}\', {{visibility:"hidden"}}, {E});')
    return js


def inserts_html_js():
    hosts, js = [], []
    for z, x in enumerate(INSERTS):
        iid, st, en = x["id"], x["start"], x["end"]
        inner = f"#{iid}-in"   # animate the inner wrapper: the framework owns the clip element's visibility
        if x["kind"] == "video":
            body = (f'<video id="{iid}-v" class="clip" src="{x["src"]}" muted playsinline data-start="{st}" '
                    f'data-duration="{round(en - st, 4)}" data-track-index="{7 + z}" data-layout-allow-occlusion></video>'
                    f'<div class="vid-shade"></div><div class="ai-tag">Ilustrasi AI</div>')
        else:
            body = f'<div class="mg">{x["body"]}</div>'
        if x["kind"] == "video":   # time the video, never its wrapper too (lint video_nested_in_timed_element)
            hosts.append(f'<div id="ins-{iid}" class="ins" style="z-index:{20 + z}">'
                         f'<div class="ins-in" id="{iid}-in" style="opacity:0">{body}</div></div>')
        else:
            hosts.append(f'<div id="ins-{iid}" class="ins clip" data-start="{st}" data-duration="{round(en - st, 4)}" '
                         f'data-track-index="{4 + z}" style="z-index:{20 + z}"><div class="ins-in" id="{iid}-in">{body}</div></div>')
        js.append(f"// insert {iid} ({x['kind']}) {st:.2f}-{en:.2f}s")
        if x["kind"] == "video":
            js.append(f"tl.fromTo('{inner}', {{opacity:0, scale:1.06}}, {{opacity:1, scale:1, duration:0.32, ease:'power2.out'}}, {st});")
        else:
            js.append(f"tl.fromTo('{inner}', {{clipPath:'inset(100% 0% 0% 0%)'}}, {{clipPath:'inset(0% 0% 0% 0%)', duration:0.42, ease:'power3.inOut'}}, {st});")
            for sel, t, kind in x["anims"]:
                t = round(max(t, st + 0.12), 3)
                if kind == "pop":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:0.6, transformOrigin:'50% 50%'}}, {{opacity:1, scale:1, duration:0.34, ease:'back.out(1.8)'}}, {t});")
                elif kind == "rise":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.42, ease:'power3.out'}}, {t});")
                elif kind == "fade":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0}}, {{opacity:1, duration:0.3, ease:'power2.out'}}, {t});")
                elif kind == "stamp":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:1.9}}, {{opacity:1, scale:1, duration:0.26, ease:'power4.out'}}, {t});")
                elif isinstance(kind, tuple) and kind[0] == "draw":
                    _, a, b, d = kind
                    js.append(f"tl.fromTo('{sel}', {{strokeDashoffset:{a}}}, {{strokeDashoffset:{b}, duration:{round(d, 3)}, ease:'power1.inOut', immediateRender:false}}, {t});")
        if en < DUR:
            js.append(f"tl.to('{inner}', {{opacity:0, duration:0.24, ease:'power2.in'}}, {round(en - 0.24, 3)});")
            if x["kind"] == "video":   # untimed wrapper: make sure it is fully gone after its slot
                js.append(f"tl.set('{inner}', {{opacity:0}}, {en});")
    return hosts, js


def main() -> None:
    (PUB / "cards").mkdir(parents=True, exist_ok=True)
    storyboard = {
        "schemaVersion": 3,
        "composition": {"fps": FPS, "width": 1080, "height": 1920, "durationSeconds": DUR,
                        "layout": "portrait", "themeId": "custom-teal", "seed": 7},
        "videoTrack": {"sourcePath": "input-video.mp4", "startSec": 0, "endSec": DUR,
                       "bounds": {"x": 0, "y": 0, "width": 1080, "height": 1920}},
        "subtitles": {"enabled": False},
        "cards": [{"id": c["id"], "intent": c["intent"], "startSec": q(c["start"]), "endSec": card_end(c),
                   "zone": "video-overlay", "contentHints": {"pages": len(c["pages"])}} for c in CARDS],
        "inserts": [{"id": x["id"], "kind": x["kind"], "startSec": x["start"], "endSec": x["end"]} for x in INSERTS],
    }
    (W / "storyboard.json").write_text(json.dumps(storyboard, indent=2, ensure_ascii=False))

    hosts, js = [], []
    for c in CARDS:
        frag = card_fragment(c)
        (PUB / "cards" / f"{c['id']}.html").write_text(frag)
        hosts.append(f'<div id="card-{c["id"]}" class="card-host clip" data-card-id="{c["id"]}" data-start="{q(c["start"])}" '
                     f'data-duration="{round(card_end(c) - q(c["start"]), 4)}" data-track-index="2" data-layout-allow-occlusion '
                     f'style="left:0;top:0;width:1080px;height:1920px;visibility:hidden;">{frag}</div>')
        js += timeline_js(c)
    ins_hosts, ins_js = inserts_html_js()

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
{CSS}
</style>
</head>
<body>
<div id="stage" data-composition-id="talking-head-recut" data-start="0" data-duration="{DUR}" data-fps="{FPS}" data-width="1080" data-height="1920">
  <div class="video-wrapper" id="video-wrap">
    <video id="bg-video" src="input-video.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="1"></video>
  </div>
  <audio id="source-audio" src="input-video.mp4" data-start="0" data-duration="{DUR}" data-track-index="10" data-volume="1"></audio>
  {chr(10).join(hosts)}
  {chr(10).join(ins_hosts)}
  <script src="vendor/gsap.min.js"></script>
  <script>
  (function () {{
    const tl = window.gsap.timeline({{ paused: true }});
    {(chr(10) + '    ').join(js + ins_js)}
    window.__timelines = window.__timelines || {{}};
    window.__timelines["talking-head-recut"] = tl;
  }})();
  </script>
</div>
</body>
</html>
"""
    (PUB / "index.html").write_text(page)
    # every page must fit above the face (heights from the last measure_pages.cjs run: re-measure after edits)
    for c in CARDS:
        for p in range(len(c["pages"])):
            h = page_h(c["id"], p)
            if h is not None:
                assert PANEL_TOP + h <= PANEL_MAX_BOTTOM, f"{c['id']} page{p}: panel bottom {PANEL_TOP + h} > {PANEL_MAX_BOTTOM}"
    print(f"{len(CARDS)} cards, {sum(len(c['pages']) for c in CARDS)} pages, {len(INSERTS)} inserts, "
          f"{len(js) + len(ins_js)} timeline statements")
    for c in CARDS:
        print(f"  {c['id']:16s} {q(c['start']):6.2f}-{card_end(c):6.2f}")
    for x in INSERTS:
        print(f"  {x['id']:16s} {x['start']:6.2f}-{x['end']:6.2f}  ({x['kind']})")


if __name__ == "__main__":
    main()
