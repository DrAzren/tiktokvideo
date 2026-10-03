"""Full-screen inserts for 'Borderline Personality Disorder'.

Template: videos/ward-psikiatri/graphics/inserts.py. Picture-only cutaways over the talking
head; the voice keeps running underneath and the captions are composited on top in the next
stage. Two kinds:
  - broll:  AI stills (Canva, design DAHW6VWdB_E, public/broll/*.jpg) with a slow cubic Ken Burns
            move and an "Ilustrasi AI" tag. No faces; nothing graphic for a sensitive topic.
  - mg:     full-screen motion graphics, deep-teal ground, cream + mint type, icons, each element
            landing on its spoken word

Layout (1080x1920): the caption line runs at y ~334-420 on top of everything, so each motion
graphic keeps a short header ABOVE it (zone A, y 120-315) and its main graphic BELOW it
(zone B, y 470-1500). Nothing important in the bottom ~20% (TikTok UI) or the right ~15%.

Every time is anchored to a phrase in edit/cut_words.json, so inserts re-time themselves
when the cut changes.
"""

import json
from pathlib import Path

W = Path(__file__).parent
WORDS = json.loads((W.parent / "edit" / "cut_words.json").read_text())
FPS = 30
TEAL, DEEP, MINT, CREAM, INK, RED, MUTED = "#0E5E6F", "#08323C", "#5EEAD4", "#FFF8EE", "#0B1F2A", "#E5484D", "#6B7C85"
HERO = (7.9, 10.95)   # "BPD" apex window (matted from the talking head): inserts must stay clear


def T(phrase: str, after: float = 0.0, end: bool = False) -> float:
    """Start (or end) time of the first occurrence of `phrase` at/after `after` on the cut."""
    toks = phrase.split()
    for i in range(len(WORDS) - len(toks) + 1):
        if WORDS[i]["start"] >= after and [w["text"] for w in WORDS[i:i + len(toks)]] == toks:
            return WORDS[i + len(toks) - 1]["end"] if end else WORDS[i]["start"]
    raise KeyError(phrase)


def fq(t: float) -> float:
    return round(round(t * FPS) / FPS, 4)


LEAD = 0.12

# icons: white strokes (viewBox 0 0 48 48)
ICON = {
    "clock": '<circle cx="24" cy="24" r="17"/><path d="M24 14v11l7 5"/>',
    "eyeoff": '<path d="M5 24s7-12 19-12 19 12 19 12-7 12-19 12S5 24 5 24z"/><circle cx="24" cy="24" r="5"/><path d="M8 40L40 8"/>',
    "alert": '<path d="M24 6L44 40H4z"/><path d="M24 19v10M24 34v1"/>',
    "heart": '<path d="M24 40S7 30 7 18a9 9 0 0 1 17-4 9 9 0 0 1 17 4c0 12-17 22-17 22z"/>',
    "crack": '<path d="M24 40S7 30 7 18a9 9 0 0 1 17-4 9 9 0 0 1 17 4c0 12-17 22-17 22z"/><path d="M24 14l-4 8 6 4-4 8"/>',
    "sun": '<circle cx="24" cy="24" r="8"/><path d="M24 5v5M24 38v5M5 24h5M38 24h5M10.5 10.5l3.5 3.5M34 34l3.5 3.5M10.5 37.5L14 34M34 14l3.5-3.5"/>',
    "cloud": '<path d="M15 34a8 8 0 0 1 1.5-15.8A10 10 0 0 1 35 21a7 7 0 0 1-1 13.9H15z"/>',
    "moon": '<path d="M36 30A15 15 0 1 1 22 9a12 12 0 0 0 14 21z"/>',
    "bag": '<path d="M10 16h28l-2 26H12z"/><path d="M18 20v-6a6 6 0 0 1 12 0v6"/>',
    "bolt": '<path d="M27 5L12 27h11l-3 16 16-23H25z"/>',
    "care": '<path d="M24 34S12 27 12 19a6 6 0 0 1 12-2 6 6 0 0 1 12 2c0 8-12 15-12 15z"/><path d="M6 38c6 0 9-3 18-3s12 3 18 3"/>',
    "unlink": '<path d="M20 28l-6 6a6 6 0 0 1-8-8l6-6M28 20l6-6a6 6 0 0 1 8 8l-6 6"/><path d="M17 11l2 5M31 37l-2-5M11 17l5 2M37 31l-5-2"/>',
    "swap": '<path d="M8 16h30l-7-7M40 32H10l7 7"/>',
    "wave": '<path d="M5 24c4-12 9-12 13 0s9 12 13 0 9-12 12-4"/>',
    "empty": '<circle cx="24" cy="24" r="15" stroke-dasharray="5 5"/>',
    "flame": '<path d="M24 43c-8 0-13-5-13-12 0-8 8-12 8-20 5 3 7 7 7 11 2-2 3-4 3-7 5 4 8 10 8 16 0 7-5 12-13 12z"/>',
    "msg": '<path d="M8 10h32v22H20l-9 7v-7H8z"/>',
}


def icon(name: str, cls: str = "mg-ico") -> str:
    return (f'<svg viewBox="0 0 48 48" class="{cls}"><g stroke="#fff" stroke-width="3.2" stroke-linecap="round" '
            f'stroke-linejoin="round" fill="none">{ICON[name]}</g></svg>')


def head(iid: str, chip: str, title: str, red: bool = False) -> str:
    return (f'<div class="head"><div class="mg-chip{" red" if red else ""}" id="{iid}-c">{chip}</div>'
            f'<div class="mg-title" id="{iid}-t">{title}</div></div>')


def build():
    """Returns (inserts, html_hosts, js_lines, css)."""
    I = []

    # ---- B-roll ----------------------------------------------------------------
    def broll(iid, img, start, end, move):
        I.append({"id": iid, "kind": "broll", "start": fq(start), "end": fq(end), "img": img, "move": move})

    # "sekadar moody je, mood swing" — a quiet low moment, not a dramatic one
    broll("b1-window", "window", T("sekadar") - 0.08, T("betul ke") - 0.06, (1.03, 1.12, 0, -24))
    # "hubungan jadi naik turun, kalau dia percaya ... mudah percaya"
    broll("b2-apart", "apart", T("hubungan jadi") - 0.12, T("mudah percaya", end=True) + 0.25, (1.10, 1.02, 0, 18))
    # "walaupun dikelilingi dengan ramai orang"
    broll("b3-crowd", "crowd", T("walaupun dikelilingi") - 0.1, T("tetapi jiwa") - 0.02, (1.02, 1.10, 0, -20))
    # "tiba-tiba marah yang melampau bila rasa tak difahami"
    broll("b4-hands", "hands", T("tiba tiba marah yang", after=T("kawal")) - 0.1, T("difahami", end=True) + 0.12, (1.04, 1.13, -22, 0))
    # "anda boleh datang ke klinik saya di Nilai"
    broll("b6-clinic", "clinic", T("anda boleh datang") - 0.1, T("sama ada nak") + 0.05, (1.12, 1.03, 16, -8))

    # ---- motion graphics ---------------------------------------------------------
    # MG1 — Tanda #1: late reply -> feels ignored -> panic
    s = T("contohnya kalau pasangan")
    steps = [("clock", "Lambat balas", "lambat balas"), ("eyeoff", "Rasa diabaikan", "diabaikan"),
             ("alert", "Terus panik", "panik")]
    chain = "".join(
        f'<div class="crow{" hot" if i == 2 else ""}" id="m1-r{i}"><span class="disc{" red" if i == 2 else ""}" id="m1-d{i}">'
        f'{icon(ic)}</span><span>{txt}</span></div>' for i, (ic, txt, _) in enumerate(steps))
    I.append({"id": "m1-chat", "kind": "mg", "start": fq(s - 0.1), "end": fq(T("yang kedua") - 0.06), "body": f"""
      {head("m1", "Tanda #1", "Takut <span class='mint'>ditinggalkan</span>")}
      <div class="phone" id="m1-ph">
        <div class="ph-top">{icon("msg", "ph-ico")}<span>Pasangan</span><span class="ph-seen" id="m1-seen">dilihat 10:02</span></div>
        <div class="bubble me" id="m1-b1">Awak dah sampai? <span class="tick">✓✓</span></div>
        <div class="wait" id="m1-w"><span class="dots"><i></i><i></i><i></i></span> 2 jam tiada balasan…</div>
      </div>
      <div class="stack" style="top:1000px">{chain}</div>""",
        "anims": [("#m1-c", s - 0.08, "pop"), ("#m1-t", s - 0.04, "rise"), ("#m1-ph", s + 0.1, "rise"),
                  ("#m1-b1", T("pasangan", after=s) - LEAD, "pop"),
                  ("#m1-w", T("lambat balas", after=s) - LEAD, "fade"),
                  ("#m1-seen", T("lambat balas", after=s) + 0.2, "fade")]
        + [a for i, (_, _, w) in enumerate(steps)
           for a in ((f"#m1-r{i}", T(w, after=s) - LEAD, "slidein"), (f"#m1-d{i}", T(w, after=s) - LEAD + 0.06, "pop"))]})

    # MG2 — Tanda #2: idealise <-> devalue
    s = T("sekejap rasa orang tu perfek")
    I.append({"id": "m2-split", "kind": "mg", "start": fq(s - 0.1), "end": fq(T("jahat", after=s, end=True) + 0.55), "body": f"""
      {head("m2", "Tanda #2", "Hubungan <span class='mint'>tak stabil</span>")}
      <div class="pole up" id="m2-a"><div class="pole-k">Sekejap…</div>
        <div class="pole-w"><span class="disc big">{icon("heart")}</span><span id="m2-aw">PERFECT</span></div></div>
      <div class="flip" id="m2-x">{icon("swap", "flip-ico")}</div>
      <div class="pole down" id="m2-b"><div class="pole-k">Sekejap…</div>
        <div class="pole-w"><span class="disc big red">{icon("crack")}</span><span id="m2-bw">JAHAT</span></div></div>""",
        "anims": [("#m2-c", s - 0.08, "pop"), ("#m2-t", s - 0.04, "rise"),
                  ("#m2-a", s - LEAD, "rise"), ("#m2-aw", T("perfek", after=s) - LEAD, "stamp"),
                  ("#m2-x", T("sekejap", after=s + 0.5) - 0.2, "pop"),
                  ("#m2-b", T("sekejap", after=s + 0.5) - LEAD, "rise"), ("#m2-bw", T("jahat", after=s) - LEAD, "stamp")]})

    # MG3 — Tanda #3: one day of mood swings
    s = T("contohnya pagi")
    day = [("sun", "Pagi", "Happy", "pagi", "hepi"), ("cloud", "Tengah hari", "Kosong", "tengah hari", "kosong"),
           ("moon", "Malam", "Tiba-tiba marah", "malam", "marah")]
    nodes = "".join(
        f'<div class="node{" hot" if i == 2 else ""}" id="m3-n{i}" style="top:{560 + i * 300}px">'
        f'<span class="disc big{" red" if i == 2 else ""}">{icon(ic)}</span>'
        f'<span class="nwrap"><span class="nk">{k}</span><span class="nlabel" id="m3-l{i}">{v}</span></span></div>'
        for i, (ic, k, v, _, _) in enumerate(day))
    I.append({"id": "m3-day", "kind": "mg", "start": fq(s - 0.1), "end": fq(T("marah", after=s, end=True) + 0.4), "body": f"""
      {head("m3", "Tanda #3", "Emosi turun naik <span class='mint'>cepat</span>")}
      <svg class="rail" viewBox="0 0 40 640" style="left:112px; top:600px; width:40px; height:640px">
        <path id="m3-rail" d="M20 10V630" stroke="{MINT}" stroke-width="6" stroke-linecap="round" fill="none"/></svg>
      {nodes}""",
        "anims": [("#m3-c", s - 0.08, "pop"), ("#m3-t", s - 0.04, "rise"),
                  ("#m3-rail", s + 0.1, ("draw", T("malam", after=s) - s))]
        + [a for i, (_, _, _, w1, w2) in enumerate(day)
           for a in ((f"#m3-n{i}", T(w1, after=s) - LEAD, "slidein"), (f"#m3-l{i}", T(w2, after=s) - LEAD, "pop"))]})

    # MG4 — Tanda #6: impulsive behaviour (top half: AI still, bottom: the list)
    s = T("contohnya syoping")
    rows = [("bag", "Shopping berlebihan", "syoping"), ("bolt", "Ambil risiko berbahaya", "ambil risiko"),
            ("care", "Self-harm bila stres", "self harm")]
    lst = "".join(f'<div class="crow sm" id="m4-r{i}"><span class="disc{" red" if i == 2 else ""}" id="m4-d{i}">{icon(ic)}</span>'
                  f'<span>{txt}</span></div>' for i, (ic, txt, _) in enumerate(rows))
    I.append({"id": "m4-impulsif", "kind": "mg", "start": fq(s - 0.1), "end": fq(T("stres", after=s, end=True) + 0.5), "body": f"""
      <div class="half top"><img src="broll/shopping.jpg" class="half-img" id="m4-img"/><div class="half-shade"></div>
        <div class="ai-tag">Ilustrasi AI</div></div>
      <div class="half bot"><div class="mg-chip" id="m4-c">Tanda #6 · Impulsif</div>
        <div class="stack" style="top:150px">{lst}</div>
        <div class="help" id="m4-h">Ada fikiran mencederakan diri? Dapatkan bantuan segera — <b>Talian HEAL 15555</b></div></div>
      <div class="seam" id="m4-seam"></div>""",
        "anims": [("#m4-seam", s - 0.1, "grow"), ("#m4-c", s - 0.05, "pop"), ("#m4-img", s - 0.1, ("kb", 1.04, 1.12)),
                  ("#m4-h", T("self harm", after=s) + 0.3, "fade")]
        + [a for i, (_, _, w) in enumerate(rows)
           for a in ((f"#m4-r{i}", T(w, after=s) - LEAD, "slidein"), (f"#m4-d{i}", T(w, after=s) - LEAD + 0.06, "pop"))]})

    # MG5 — recap: the 6 signs are not "gila"
    s = T("kalau ada tanda tanda ni")
    six = [("unlink", "Takut ditinggalkan"), ("swap", "Hubungan tak stabil"), ("wave", "Emosi tak stabil"),
           ("empty", "Rasa kosong"), ("flame", "Marah melampau"), ("bolt", "Impulsif")]
    tiles = "".join(f'<div class="tile" id="m5-k{i}"><span class="disc">{icon(ic)}</span><span>{txt}</span></div>'
                    for i, (ic, txt) in enumerate(six))
    I.append({"id": "m5-recap", "kind": "mg", "start": fq(s - 0.1), "end": fq(T("ini adalah gejala") - 0.05), "body": f"""
      {head("m5", "6 tanda BPD", "Kalau ada tanda-tanda <span class='mint'>ini…</span>")}
      <div class="grid6" id="m5-g">{tiles}</div>
      <div class="bigx" id="m5-x"><div class="stamp-lg">BUKAN BERMAKNA<br/>ANDA GILA</div></div>""",
        "anims": [("#m5-c", s - 0.08, "pop"), ("#m5-t", s - 0.04, "rise")]
        + [(f"#m5-k{i}", s + 0.05 + i * 0.11, "pop") for i in range(6)]
        + [("#m5-g", T("bukanlah", after=s) - 0.2, ("dim", 0.35)),
           ("#m5-x", T("bukanlah", after=s) - LEAD, "stamp")]})

    I.sort(key=lambda x: x["start"])
    for a, b in zip(I, I[1:]):
        assert a["start"] < b["start"] and a["end"] <= b["end"], (a["id"], b["id"])
        assert b["start"] >= a["end"] - 0.5, f"{a['id']} / {b['id']} overlap by more than a crossfade"
    for x in I:
        d = x["end"] - x["start"]
        assert d >= 1.8, (x["id"], d)
        if x["kind"] == "broll":
            assert d <= 4.3, (x["id"], d)   # user: 2-4 s each
        # the "BPD" apex is matted from the talking head: inserts must stay clear of it
        assert x["end"] <= HERO[0] or x["start"] >= HERO[1], x["id"]

    hosts, js = [], []
    for z, x in enumerate(I):
        iid, st, en = x["id"], x["start"], x["end"]
        host = f"#{iid}-in"   # animate the inner wrapper: the framework owns the clip element's visibility
        if x["kind"] == "broll":
            body = (f'<img src="broll/{x["img"]}.jpg" class="kb" id="{iid}-img"/>'
                    f'<div class="cap-shade"></div><div class="ai-tag">Ilustrasi AI</div>')
        else:
            body = f'<div class="mg">{x["body"]}</div>'
        hosts.append(f'<div id="ins-{iid}" class="ins clip" data-start="{st}" data-duration="{round(en - st, 4)}" '
                     f'data-track-index="{5 + z % 2}" style="z-index:{20 + z}"><div class="ins-in" id="{iid}-in">{body}</div></div>')
        js.append(f"// insert {iid} ({x['kind']}) {st:.2f}-{en:.2f}s")
        if x["kind"] == "broll":
            s0, s1, dx, dy = x["move"]
            js.append(f"tl.fromTo('{host}', {{opacity:0, scale:1.05}}, {{opacity:1, scale:1, duration:0.3, ease:'power2.out'}}, {st});")
            js.append(f"tl.fromTo('#{iid}-img', {{scale:{s0}, x:0, y:0}}, {{scale:{s1}, x:{dx}, y:{dy}, "
                      f"duration:{round(en - st, 3)}, ease:'sine.inOut'}}, {st});")
        else:
            js.append(f"tl.fromTo('{host}', {{clipPath:'inset(100% 0% 0% 0%)'}}, {{clipPath:'inset(0% 0% 0% 0%)', duration:0.42, ease:'power3.inOut'}}, {st});")
            for sel, t, kind in x["anims"]:
                t = round(max(t, st + 0.12), 3)
                if kind == "pop":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.34, ease:'back.out(1.8)'}}, {t});")
                elif kind == "rise":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.42, ease:'power3.out'}}, {t});")
                elif kind == "slidein":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0, x:80}}, {{opacity:1, x:0, duration:0.4, ease:'power3.out'}}, {t});")
                elif kind == "fade":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0}}, {{opacity:1, duration:0.3, ease:'power2.out'}}, {t});")
                elif kind == "stamp":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:1.9}}, {{opacity:1, scale:1, duration:0.26, ease:'power4.out'}}, {t});")
                elif kind == "grow":
                    js.append(f"tl.fromTo('{sel}', {{scaleX:0}}, {{scaleX:1, duration:0.5, ease:'power3.inOut'}}, {t});")
                elif kind[0] == "draw":
                    js.append(f"tl.fromTo('{sel}', {{strokeDashoffset:720}}, {{strokeDashoffset:0, duration:{round(kind[1], 3)}, ease:'power1.inOut'}}, {t});")
                elif kind[0] == "dim":
                    js.append(f"tl.to('{sel}', {{opacity:{kind[1]}, duration:0.3, ease:'power2.out'}}, {t});")
                elif kind[0] == "kb":
                    js.append(f"tl.fromTo('{sel}', {{scale:{kind[1]}}}, {{scale:{kind[2]}, duration:{round(en - t, 3)}, ease:'sine.inOut'}}, {t});")
        js.append(f"tl.to('{host}', {{opacity:0, duration:0.24, ease:'power2.in'}}, {round(en - 0.24, 3)});")
    return I, hosts, js, CSS


CSS = f"""
.ins {{ position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden; pointer-events:none; }}
.ins-in {{ position:absolute; inset:0; overflow:hidden; }}
.kb {{ position:absolute; left:0; top:0; width:1080px; height:1920px; object-fit:cover; transform-origin:50% 45%; }}
/* darken behind the caption line (y ~334-420) so white captions read on bright stills */
.cap-shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.28) 0%, rgba(0,0,0,0) 10%,
  rgba(0,0,0,.34) 16%, rgba(0,0,0,.34) 23%, rgba(0,0,0,0) 30%); }}
.ai-tag {{ position:absolute; left:48px; top:140px; font:700 24px 'Plus Jakarta Sans'; letter-spacing:.08em; text-transform:uppercase;
  color:rgba(255,255,255,.92); background:rgba(0,0,0,.40); padding:7px 14px 6px; border-radius:10px; }}
.mg {{ position:absolute; inset:0; background:radial-gradient(120% 80% at 80% 10%, {TEAL} 0%, {DEEP} 62%, #051E25 100%);
  font-family:'Plus Jakarta Sans', sans-serif; color:{CREAM}; }}
.mg .mint {{ color:{MINT}; }}
.head {{ position:absolute; left:80px; top:128px; width:900px; }}
.mg-chip {{ display:inline-block; font-weight:800; font-size:28px; letter-spacing:.08em; text-transform:uppercase;
  padding:9px 20px 8px; border-radius:999px; background:{MINT}; color:{DEEP}; }}
.mg-chip.red {{ background:{RED}; color:#fff; }}
.mg-title {{ font-weight:800; font-size:64px; line-height:1.04; letter-spacing:-.02em; margin-top:16px; white-space:nowrap; }}
.stack {{ position:absolute; left:80px; width:880px; display:flex; flex-direction:column; gap:22px; }}
.crow {{ display:flex; align-items:center; gap:26px; height:124px; padding:0 30px; border-radius:26px; background:{CREAM};
  color:{INK}; font-weight:800; font-size:48px; box-shadow:0 14px 34px rgba(0,0,0,.28); }}
.crow.sm {{ height:112px; font-size:42px; }}
.crow.hot {{ background:#FFE9E7; }}
.disc {{ width:78px; height:78px; border-radius:50%; background:{TEAL}; display:inline-flex; align-items:center; justify-content:center; flex:none; }}
.disc.red {{ background:{RED}; }}
.disc.big {{ width:104px; height:104px; }}
.disc.big .mg-ico {{ width:64px; height:64px; }}
.mg-ico {{ width:50px; height:50px; }}
.rail {{ position:absolute; }}
.rail path {{ stroke-dasharray:720; }}
/* MG1 phone */
.phone {{ position:absolute; left:140px; top:500px; width:800px; height:440px; border-radius:40px; background:#0A2A33;
  border:3px solid rgba(94,234,212,.35); box-shadow:0 22px 60px rgba(0,0,0,.35); padding:28px 34px; }}
.ph-top {{ display:flex; align-items:center; gap:16px; font-weight:800; font-size:34px; padding-bottom:20px;
  border-bottom:2px solid rgba(255,248,238,.14); }}
.ph-ico {{ width:44px; height:44px; }}
.ph-seen {{ margin-left:auto; font-size:26px; font-weight:700; color:rgba(255,248,238,.6); }}
.bubble {{ display:inline-block; font-weight:700; font-size:40px; padding:18px 26px; border-radius:28px; margin-top:34px; }}
.bubble.me {{ float:right; background:{MINT}; color:{DEEP}; border-bottom-right-radius:8px; }}
.tick {{ font-size:26px; margin-left:10px; color:{TEAL}; }}
.wait {{ clear:both; position:absolute; left:34px; bottom:40px; font-weight:700; font-size:36px; color:rgba(255,248,238,.75);
  display:flex; align-items:center; gap:18px; }}
.dots {{ display:inline-flex; gap:8px; padding:16px 20px; border-radius:24px; background:rgba(255,248,238,.12); }}
.dots i {{ width:14px; height:14px; border-radius:50%; background:rgba(255,248,238,.6); display:block; }}
/* MG2 poles */
.pole {{ position:absolute; left:80px; width:920px; height:390px; border-radius:34px; padding:34px 44px; }}
.pole.up {{ top:480px; background:{CREAM}; color:{TEAL}; }}
.pole.down {{ top:1000px; background:#2A1416; color:#FFB4B0; border:4px solid {RED}; }}
.pole-k {{ font-weight:800; font-size:40px; letter-spacing:.04em; text-transform:uppercase; opacity:.75; }}
.pole-w {{ display:flex; align-items:center; gap:34px; margin-top:44px; font-weight:800; font-size:128px; letter-spacing:-.02em; line-height:1; }}
.flip {{ position:absolute; left:490px; top:900px; width:100px; height:100px; border-radius:50%; background:{MINT};
  display:flex; align-items:center; justify-content:center; z-index:3; box-shadow:0 10px 30px rgba(0,0,0,.35); }}
.flip-ico {{ width:58px; height:58px; transform:rotate(90deg); }}
.flip-ico g {{ stroke:{DEEP}; }}
/* MG3 day path */
.node {{ position:absolute; left:80px; display:flex; align-items:center; gap:34px; }}
.nwrap {{ display:flex; flex-direction:column; gap:10px; }}
.nk {{ font-weight:800; font-size:36px; letter-spacing:.06em; text-transform:uppercase; color:rgba(255,248,238,.7); }}
.nlabel {{ font-weight:800; font-size:64px; padding:12px 30px; border-radius:22px; background:{CREAM}; color:{INK}; }}
.node.hot .nlabel {{ background:{RED}; color:#fff; }}
/* MG4 half + half */
.half {{ position:absolute; left:0; width:1080px; height:960px; overflow:hidden; }}
.half.top {{ top:0; }}
.half.bot {{ top:960px; background:radial-gradient(120% 90% at 20% 0%, {TEAL} 0%, {DEEP} 70%); }}
.half-img {{ position:absolute; left:0; top:-300px; width:1080px; height:1920px; object-fit:cover; transform-origin:50% 60%; }}
.half-shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.25), rgba(0,0,0,.32) 20%, rgba(0,0,0,.05) 40%, rgba(0,0,0,.35)); }}
.half.bot .mg-chip {{ position:absolute; left:80px; top:56px; }}
.help {{ position:absolute; left:80px; top:584px; width:880px; font-weight:700; font-size:28px; line-height:1.3; color:rgba(255,248,238,.85); }}
.help b {{ color:{MINT}; }}
.seam {{ position:absolute; left:0; top:954px; width:1080px; height:12px; background:{CREAM}; transform-origin:left center; z-index:3; }}
/* MG5 recap */
.grid6 {{ position:absolute; left:80px; top:480px; width:920px; display:grid; grid-template-columns:1fr 1fr; gap:22px; }}
.tile {{ display:flex; align-items:center; gap:20px; height:150px; padding:0 24px; border-radius:26px; background:{CREAM}; color:{INK};
  font-weight:800; font-size:36px; line-height:1.1; box-shadow:0 14px 34px rgba(0,0,0,.28); }}
.bigx {{ position:absolute; left:0; right:0; top:1110px; text-align:center; }}
.stamp-lg {{ display:inline-block; transform:rotate(-6deg); border:8px solid {RED}; color:{RED}; border-radius:18px; font-weight:800;
  font-size:76px; line-height:1.05; letter-spacing:.03em; padding:14px 30px 8px; background:rgba(255,248,238,.95); }}
"""
