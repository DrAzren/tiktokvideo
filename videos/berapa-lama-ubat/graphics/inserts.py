"""Full-screen inserts for 'Berapa Lama Makan Ubat Psikiatri'.

Template: videos/ward-psikiatri/graphics/inserts.py. Picture-only cutaways over the talking head;
the voice keeps running underneath and captions are composited on top in the next stage.
  - broll:  AI stills (Canva, broll/*.jpg) with a slow cubic Ken Burns move plus an "Ilustrasi AI" tag
  - mg:     full-screen motion graphics, deep-teal ground, cream + mint type, each element on its word

Every time is anchored to a phrase in edit/cut_words.json. Layout: this framing has little headroom,
so the caption line sits at y~360-480; MG titles stay above it (y 150-340) and content starts at
y~560, and nothing important goes in the bottom ~20% (TikTok UI).
"""

import json
from pathlib import Path

W = Path(__file__).parent
WORDS = json.loads((W.parent / "edit" / "cut_words.json").read_text())
FPS = 30
TEAL, DEEP, MINT, CREAM, INK, RED, MUTED = "#0E5E6F", "#08323C", "#5EEAD4", "#FFF8EE", "#0B1F2A", "#E5484D", "#6B7C85"
HERO_WINDOW = (6.2, 8.85)   # "BERGANTUNG" is matted behind the head here: inserts must stay clear


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
    "cal": '<rect x="7" y="10" width="34" height="30" rx="5"/><path d="M7 19h34M16 6v8M32 6v8"/>',
    "loop": '<path d="M36 18a13 13 0 1 0 2 10"/><path d="M38 9v10h-10"/>',
    "pillx": '<rect x="6" y="17" width="36" height="14" rx="7" transform="rotate(-30 24 24)"/><path d="M17 31l14-14" />',
    "brain": '<path d="M19 8a6 6 0 0 0-6 6 6 6 0 0 0-4 10 6 6 0 0 0 4 10 6 6 0 0 0 6 6V8zM29 8a6 6 0 0 1 6 6 6 6 0 0 1 4 10 6 6 0 0 1-4 10 6 6 0 0 1-6 6V8z"/>',
    "heart": '<path d="M24 40S7 30 7 18a9 9 0 0 1 17-4 9 9 0 0 1 17 4c0 12-17 22-17 22z"/><path d="M11 24h8l3-5 4 9 3-4h8"/>',
    "drop": '<path d="M24 6s13 15 13 24a13 13 0 0 1-26 0C11 21 24 6 24 6z"/>',
    "shield": '<path d="M24 5l16 6v11c0 10-7 17-16 21C15 39 8 32 8 22V11z"/><path d="M17 24l5 5 9-10"/>',
}


def icon(name: str, cls: str = "mg-ico") -> str:
    return (f'<svg viewBox="0 0 48 48" class="{cls}"><g stroke="#fff" stroke-width="3.2" stroke-linecap="round" '
            f'stroke-linejoin="round" fill="none">{ICON[name]}</g></svg>')


def build():
    """Returns (inserts, html_hosts, js_lines, css)."""
    I = []

    # ---- B-roll (no faces; calm, clinical, nothing sensational) ---------------------------
    def broll(iid, img, start, end, move, extra=""):
        I.append({"id": iid, "kind": "broll", "start": fq(start), "end": fq(end), "img": img, "move": move, "extra": extra})

    broll("b1-consult", "consult", T("doktor nak pastikan") - 0.1, T("betul betul stabil dulu", end=True) + 0.12, (1.03, 1.12, -20, 0))
    broll("b2-organizer", "organizer", T("ubat mungkin perlu") - 0.08, T("yang panjang", end=True) + 0.25, (1.10, 1.02, 0, 18))
    broll("b3-cutter", "cutter", T("kalau sampai masa") - 0.08, T("proses tapering") - 0.12, (1.02, 1.11, 0, -20))
    broll("b4-walk", "walk", T("dapatkan semula") - 0.08, T("kualiti hidup kita", end=True) + 0.12, (1.04, 1.13, 0, -26))

    # ---- motion graphics ------------------------------------------------------------------
    # M1: how long? bars that grow on the spoken durations
    s = T("kalau kemurungan")
    bars = [("Ringan", "kemurungan · anxiety", "6–12 bulan", "kemurungan", "enam", "bulan", 52),
            ("Pernah relapse", "gejala berulang", "Lebih lama", "relapse", "tempoh boleh", "jadi lama", 92)]
    rows = "".join(
        f'<div class="brow" id="m1-r{i}"><div class="blabel"><span class="bt">{a}</span><span class="bs">{b}</span></div>'
        f'<div class="btrack"><div class="bfill{" hi" if i else ""}" id="m1-f{i}" style="width:{w}%"></div>'
        f'<span class="bval" id="m1-v{i}">{c}</span></div></div>'
        for i, (a, b, c, *_ , w) in enumerate(bars))
    I.append({"id": "m1-tempoh", "kind": "mg", "start": fq(s - 0.1), "end": fq(T("jadi lama", end=True) + 0.3), "body": f"""
      <div class="head"><div class="mg-chip" id="m1-c">Berapa lama?</div>
        <div class="mg-title" id="m1-t">Ikut <span class="mint">tahap gejala</span></div></div>
      <div class="stack" style="top:600px; gap:60px">{rows}</div>
      <div class="mg-foot" id="m1-ft">{icon("cal", "foot-ico")}<span>anggaran biasa — doktor tentukan ikut pesakit</span></div>""",
        "anims": [("#m1-c", s - 0.05, "pop"), ("#m1-t", s, "rise")]
        + [a for i, (_, _, _, w0, w1, w2, _) in enumerate(bars)
           for a in ((f"#m1-r{i}", T(w0, after=s) - LEAD, "slidein"),
                     (f"#m1-f{i}", T(w1, after=s) - LEAD, ("growx", T(w2, after=s, end=True) - T(w1, after=s))),
                     (f"#m1-v{i}", T(w2, after=s) - LEAD, "pop"))]
        + [("#m1-ft", T("relapse", after=s) + 0.2, "fade")]})

    # M2: stop too early -> symptoms come back (cause -> effect -> risk gauge)
    s = T("kalau ubat stop")
    I.append({"id": "m2-awal", "kind": "mg", "start": fq(s - 0.1), "end": fq(T("balik tinggi", end=True) + 0.4), "body": f"""
      <div class="head"><div class="mg-chip red" id="m2-c">Awas</div>
        <div class="mg-title" id="m2-t">Stop <span class="mint">terlalu awal?</span></div></div>
      <div class="cnode" id="m2-a" style="top:600px"><span class="disc red">{icon("pillx")}</span><span>Ubat dihentikan awal</span></div>
      <svg class="rail" viewBox="0 0 40 150" style="left:150px; top:752px; width:40px; height:150px">
        <path id="m2-ar" d="M20 6V132" stroke="{MINT}" stroke-width="7" stroke-linecap="round" fill="none"/>
        <path id="m2-tip" d="M6 118L20 140 34 118" stroke="{MINT}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
      <div class="cnode" id="m2-b" style="top:920px"><span class="disc">{icon("loop")}</span><span>Simptom datang balik</span></div>
      <div class="gauge" id="m2-g"><svg viewBox="0 0 300 170" class="gsvg">
        <path d="M30 150A120 120 0 0 1 270 150" stroke="rgba(255,248,238,.18)" stroke-width="26" fill="none" stroke-linecap="round"/>
        <path id="m2-garc" d="M30 150A120 120 0 0 1 270 150" stroke="{RED}" stroke-width="26" fill="none" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"/>
        <g id="m2-needle"><path d="M150 150L150 48" stroke="{CREAM}" stroke-width="9" stroke-linecap="round"/></g>
        <circle cx="150" cy="150" r="15" fill="{CREAM}"/></svg>
        <div class="glabel">Risiko <b id="m2-hi">TINGGI</b></div></div>""",
        "anims": [("#m2-c", s - 0.05, "pop"), ("#m2-t", s, "rise"),
                  ("#m2-a", T("stop", after=s) - LEAD, "slidein"),
                  ("#m2-ar", T("terlalu awal", after=s) + 0.1, ("draw", 0.45)),
                  ("#m2-tip", T("risiko", after=s) - 0.1, "fade"),
                  ("#m2-b", T("simptom", after=s) - LEAD, "slidein"),
                  ("#m2-g", T("datang balik", after=s) - LEAD, "rise"),
                  ("#m2-garc", T("tinggi", after=s) - 0.3, ("dash", 0.5)),
                  ("#m2-needle", T("tinggi", after=s) - 0.3, ("needle", 0.5)),
                  ("#m2-hi", T("tinggi", after=s) - LEAD, "stamp")]})

    # M3: chronic mental illness = chronic physical illness (split with an equals badge)
    s = T("sama juga macam")
    I.append({"id": "m3-sama", "kind": "mg", "start": fq(s - 0.1), "end": fq(T("badan mereka", end=True) + 0.3), "body": f"""
      <div class="head"><div class="mg-chip" id="m3-c">Penyakit kronik</div>
        <div class="mg-title" id="m3-t">Sama juga <span class="mint">macam…</span></div></div>
      <div class="sbox" id="m3-l" style="top:560px"><span class="disc">{icon("brain")}</span>
        <div><div class="sbt">Bipolar · Skizofrenia</div><div class="sbs">kesihatan mental</div></div></div>
      <div class="eq" id="m3-eq">=</div>
      <div class="pairrow" style="top:960px">
        <div class="sbox pair" id="m3-r1"><span class="disc red">{icon("heart")}</span><div class="sbt">Darah tinggi</div></div>
        <div class="sbox pair" id="m3-r2"><span class="disc red">{icon("drop")}</span><div class="sbt">Kencing manis</div></div></div>
      <div class="kawal" id="m3-k"><span class="klabel">Ubat untuk kawal</span>
        <span class="kchip" id="m3-k1">tekanan darah</span><span class="kchip" id="m3-k2">gula</span></div>""",
        "anims": [("#m3-c", s - 0.05, "pop"), ("#m3-t", s, "rise"), ("#m3-l", s + 0.05, "slidein"),
                  ("#m3-eq", T("macam", after=s) - LEAD, "stamp"),
                  ("#m3-r1", T("darah tinggi", after=s) - LEAD, "rise"),
                  ("#m3-r2", T("kencing manis", after=s) - LEAD, "rise"),
                  ("#m3-k", T("perlukan ubat", after=s) - LEAD, "fade"),
                  ("#m3-k1", T("tekanan darah", after=s) - LEAD, "pop"),
                  ("#m3-k2", T("gula", after=s) - LEAD, "pop")]})

    # M4: tapering staircase — the dose steps down one step per spoken beat
    s = T("proses tapering")
    steps = [("100%", "proses tapering"), ("75%", "kurangkan dos"), ("50%", "secara perlahan"), ("25%", "lahan")]
    stair = "".join(f'<div class="stair" id="m4-s{i}" style="left:{90 + i * 232}px; height:{520 - i * 118}px">'
                    f'<span class="spill" style="width:{100 - i * 22}%"></span><span class="sval">{v}</span></div>'
                    for i, (v, _) in enumerate(steps))
    I.append({"id": "m4-tapering", "kind": "mg", "start": fq(s - 0.12), "end": fq(T("withdrawal symptom", end=True) + 0.3), "body": f"""
      <div class="head"><div class="mg-chip" id="m4-c">Proses tapering</div>
        <div class="mg-title" id="m4-t">Dos turun <span class="mint">perlahan-lahan</span></div></div>
      <div class="stairs">{stair}</div>
      <div class="dose-label" id="m4-dl">Dos ubat</div>
      <div class="shieldrow" id="m4-sh"><span class="disc">{icon("shield")}</span><span>Elak <span class="mint">withdrawal symptom</span></span></div>""",
        "anims": [("#m4-c", s - 0.08, "pop"), ("#m4-t", s, "rise"), ("#m4-dl", s + 0.1, "fade")]
        + [(f"#m4-s{i}", T(w, after=s) - LEAD, "stepup") for i, (_, w) in enumerate(steps)]
        + [("#m4-sh", T("elakkan", after=s) - LEAD, "rise")]})

    I.sort(key=lambda x: x["start"])
    for a, b in zip(I, I[1:]):
        assert a["start"] < b["start"] and a["end"] <= b["end"], (a["id"], b["id"])
        assert b["start"] >= a["end"] - 0.5, f"{a['id']} / {b['id']} overlap by more than a crossfade"
    for x in I:
        assert x["end"] - x["start"] >= 1.8, (x["id"], x["end"] - x["start"])
        # the "BERGANTUNG" apex is matted from the talking head: inserts must stay clear of it
        assert x["end"] <= HERO_WINDOW[0] or x["start"] >= HERO_WINDOW[1], x["id"]

    hosts, js = [], []
    for z, x in enumerate(I):
        iid, st, en = x["id"], x["start"], x["end"]
        host = f"#{iid}-in"   # animate the inner wrapper: the framework owns the clip element's visibility
        if x["kind"] == "broll":
            body = (f'<img src="broll/{x["img"]}.jpg" class="kb" id="{iid}-img"/>'
                    f'<div class="cap-shade"></div>'
                    + ('<div class="flicker" id="%s-fl"></div>' % iid if x["extra"] == "flicker" else "")
                    + '<div class="ai-tag">Ilustrasi AI</div>')
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
            if x["extra"] == "flicker":   # a failing tube: irregular dips, stepped not tweened
                for k, (dt, o) in enumerate([(0.35, .55), (0.42, .1), (0.9, .42), (0.97, .05), (1.02, .5), (1.1, .12), (1.6, .35), (1.66, .08)]):
                    js.append(f"tl.set('#{iid}-fl', {{opacity:{o}}}, {round(st + dt, 3)});")
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
                elif kind == "stepup":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0, y:60, scaleY:0.6}}, {{opacity:1, y:0, scaleY:1, duration:0.4, ease:'power3.out'}}, {t});")
                elif isinstance(kind, tuple) and kind[0] == "growx":
                    js.append(f"tl.fromTo('{sel}', {{scaleX:0}}, {{scaleX:1, duration:{round(max(0.35, kind[1]), 3)}, ease:'power2.out'}}, {t});")
                elif isinstance(kind, tuple) and kind[0] == "dash":
                    js.append(f"tl.fromTo('{sel}', {{strokeDashoffset:100}}, {{strokeDashoffset:12, duration:{kind[1]}, ease:'power3.out'}}, {t});")
                elif isinstance(kind, tuple) and kind[0] == "needle":
                    js.append(f"tl.fromTo('{sel}', {{rotation:-90, svgOrigin:'150 150'}}, {{rotation:62, svgOrigin:'150 150', duration:{kind[1]}, ease:'back.out(1.6)'}}, {t});")
                elif isinstance(kind, tuple) and kind[0] == "draw":
                    js.append(f"tl.fromTo('{sel}', {{strokeDashoffset:720}}, {{strokeDashoffset:0, duration:{round(kind[1], 3)}, ease:'power1.inOut'}}, {t});")
        js.append(f"tl.to('{host}', {{opacity:0, duration:0.24, ease:'power2.in'}}, {round(en - 0.24, 3)});")
    return I, hosts, js, CSS


CSS = f"""
.ins {{ position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden; pointer-events:none; }}
.ins-in {{ position:absolute; inset:0; overflow:hidden; }}
.kb {{ position:absolute; left:0; top:0; width:1080px; height:1920px; object-fit:cover; transform-origin:50% 45%; }}
.cap-shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.25) 0%, rgba(0,0,0,0) 12%,
  rgba(0,0,0,0) 16%, rgba(0,0,0,.32) 19%, rgba(0,0,0,.32) 26%, rgba(0,0,0,0) 32%); }}
.flicker {{ position:absolute; inset:0; background:#000; opacity:0; }}
.ai-tag {{ position:absolute; left:48px; top:1440px; font:700 24px 'Plus Jakarta Sans'; letter-spacing:.08em; text-transform:uppercase;
  color:rgba(255,255,255,.9); background:rgba(0,0,0,.38); padding:7px 14px 6px; border-radius:10px; }}
.mg {{ position:absolute; inset:0; background:radial-gradient(120% 80% at 80% 10%, {TEAL} 0%, {DEEP} 62%, #051E25 100%);
  font-family:'Plus Jakarta Sans', sans-serif; color:{CREAM}; }}
.mg .mint {{ color:{MINT}; }}
.head {{ position:absolute; left:80px; top:150px; width:920px; }}
.mg-chip {{ display:inline-block; font-weight:800; font-size:30px; letter-spacing:.08em; text-transform:uppercase;
  padding:10px 22px 9px; border-radius:999px; background:{MINT}; color:{DEEP}; }}
.mg-chip.red {{ background:{RED}; color:#fff; }}
.mg-title {{ font-weight:800; font-size:72px; line-height:1.04; letter-spacing:-.02em; margin-top:18px; white-space:nowrap; }}
.mg-sub {{ font-weight:700; font-size:44px; color:rgba(255,248,238,.82); margin-top:22px; }}
.stack {{ position:absolute; left:80px; width:920px; display:flex; flex-direction:column; gap:22px; }}
.crow {{ display:flex; align-items:center; gap:26px; height:118px; padding:0 30px; border-radius:26px; background:{CREAM};
  color:{INK}; font-weight:800; font-size:46px; box-shadow:0 14px 34px rgba(0,0,0,.28); }}
.disc {{ width:78px; height:78px; border-radius:50%; background:{TEAL}; display:inline-flex; align-items:center; justify-content:center; flex:none; }}
.mg-ico {{ width:50px; height:50px; }}
.rail {{ position:absolute; }}
.rail path {{ stroke-dasharray:720; }}
.rung {{ position:absolute; width:820px; height:130px; display:flex; align-items:center; gap:24px; padding:0 30px; border-radius:24px;
  background:{CREAM}; color:{INK}; font-weight:800; font-size:40px; line-height:1.1; box-shadow:0 14px 34px rgba(0,0,0,.28); }}
.rung.last {{ width:700px; height:120px; background:transparent; border:6px solid {RED}; color:#fff; font-size:50px; box-shadow:none;
  justify-content:center; transform-origin:center; }}
.rnum {{ width:64px; height:64px; flex:none; border-radius:50%; background:{RED}; color:#fff; font-size:34px; display:inline-flex;
  align-items:center; justify-content:center; }}
.node {{ position:absolute; left:112px; display:flex; align-items:center; gap:34px; }}
.node .dot {{ width:60px; height:60px; border-radius:50%; background:{DEEP}; border:8px solid {MINT}; flex:none; }}
.node.hi .dot {{ background:{MINT}; }}
.nlabel {{ font-weight:800; font-size:54px; padding:14px 28px; border-radius:22px; background:{CREAM}; color:{INK}; }}
.node.hi .nlabel {{ background:{MINT}; color:{DEEP}; }}
.half {{ position:absolute; left:0; width:1080px; height:960px; overflow:hidden; }}
.half.top {{ top:0; }}
.half.bot {{ top:960px; background:radial-gradient(120% 90% at 20% 0%, {TEAL} 0%, {DEEP} 70%); }}
.half-img {{ position:absolute; left:0; top:-280px; width:1080px; height:1920px; object-fit:cover; }}
.grim {{ filter:grayscale(1) contrast(1.15) brightness(.7); }}
.half-shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.35), rgba(0,0,0,.15) 40%, rgba(0,0,0,.55)); }}
.at-top {{ position:absolute; left:80px; top:170px; }}
.bigx {{ position:absolute; left:0; right:0; top:760px; text-align:center; }}
.stamp-lg {{ display:inline-block; transform:rotate(-7deg); border:8px solid {RED}; color:{RED}; border-radius:18px; font-weight:800;
  font-size:84px; letter-spacing:.04em; padding:8px 28px 2px; background:rgba(255,248,238,.93); }}
.half.bot .mg-chip {{ position:absolute; left:80px; top:70px; }}
.half.bot .mg-title {{ position:absolute; left:80px; top:150px; font-size:92px; margin:0; }}
.half.bot .mg-sub {{ position:absolute; left:80px; top:370px; margin:0; font-size:50px; }}
.seam {{ position:absolute; left:0; top:954px; width:1080px; height:12px; background:{CREAM}; transform-origin:left center; z-index:3; }}
/* berapa-lama additions */
.mg-foot {{ position:absolute; left:80px; top:1330px; display:flex; align-items:center; gap:16px; font-weight:700; font-size:32px; color:rgba(255,248,238,.72); }}
.foot-ico {{ width:40px; height:40px; }}
.brow {{ display:flex; flex-direction:column; gap:16px; }}
.blabel {{ display:flex; align-items:baseline; gap:18px; }}
.bt {{ font-weight:800; font-size:54px; color:{CREAM}; }}
.bs {{ font-weight:700; font-size:34px; color:rgba(255,248,238,.65); }}
.btrack {{ position:relative; height:104px; border-radius:22px; background:rgba(255,248,238,.12); overflow:hidden; }}
.bfill {{ position:absolute; left:0; top:0; bottom:0; border-radius:22px; background:{MINT}; transform-origin:left center; }}
.bfill.hi {{ background:linear-gradient(90deg, {MINT}, #FFD37A); }}
.bval {{ position:absolute; left:32px; top:50%; margin-top:-30px; line-height:60px; font-weight:800; font-size:50px; color:{DEEP}; }}
.cnode {{ position:absolute; left:80px; width:920px; height:140px; display:flex; align-items:center; gap:28px; padding:0 34px; border-radius:28px;
  background:{CREAM}; color:{INK}; font-weight:800; font-size:50px; box-shadow:0 14px 34px rgba(0,0,0,.28); }}
.disc.red {{ background:{RED}; }}
.gauge {{ position:absolute; left:240px; top:1110px; width:600px; text-align:center; }}
.gsvg {{ width:420px; height:238px; }}
.glabel {{ font-weight:800; font-size:48px; color:{CREAM}; margin-top:-6px; }}
.glabel b {{ display:inline-block; color:#fff; background:{RED}; padding:2px 18px; border-radius:12px; margin-left:8px; }}
.sbox {{ position:absolute; left:80px; width:920px; min-height:150px; display:flex; align-items:center; gap:28px; padding:22px 34px; border-radius:28px;
  background:{CREAM}; color:{INK}; box-shadow:0 14px 34px rgba(0,0,0,.28); }}
.sbox.pair {{ position:relative; left:auto; width:auto; flex:1; flex-direction:column; justify-content:center; gap:16px; min-height:250px; }}
.sbt {{ font-weight:800; font-size:48px; line-height:1.1; }}
.sbs {{ font-weight:700; font-size:32px; color:#44525A; margin-top:6px; }}
.eq {{ position:absolute; left:470px; top:770px; width:140px; height:140px; border-radius:50%; background:{MINT}; color:{DEEP};
  font-weight:800; font-size:110px; line-height:132px; text-align:center; box-shadow:0 12px 30px rgba(0,0,0,.3); }}
.pairrow {{ position:absolute; left:80px; width:920px; display:flex; gap:28px; }}
.kawal {{ position:absolute; left:80px; width:920px; top:1270px; display:flex; flex-wrap:wrap; align-items:center; gap:16px; }}
.klabel {{ font-weight:700; font-size:38px; color:rgba(255,248,238,.8); margin-right:6px; }}
.kchip {{ font-weight:800; font-size:40px; padding:10px 24px; border-radius:18px; background:{MINT}; color:{DEEP}; }}
.stairs {{ position:absolute; left:0; top:640px; width:1080px; height:540px; }}
.stair {{ position:absolute; bottom:0; width:206px; border-radius:24px 24px 8px 8px; background:{CREAM}; box-shadow:0 14px 34px rgba(0,0,0,.28);
  transform-origin:bottom center; display:flex; flex-direction:column; align-items:center; justify-content:flex-start; padding-top:26px; gap:18px; }}
.spill {{ display:block; height:34px; border-radius:17px; background:{TEAL}; }}
.sval {{ font-weight:800; font-size:48px; color:{INK}; }}
.dose-label {{ position:absolute; left:90px; top:580px; font-weight:700; font-size:34px; color:rgba(255,248,238,.72); text-transform:uppercase; letter-spacing:.08em; }}
.shieldrow {{ position:absolute; left:80px; top:1250px; display:flex; align-items:center; gap:26px; font-weight:800; font-size:52px; color:{CREAM}; }}
"""
