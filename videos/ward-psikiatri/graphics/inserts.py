"""Full-screen inserts for 'Keadaan Dalam Wad Psikiatri' (round 3).

Picture-only cutaways over the talking head. The voice keeps running underneath, and
the captions are composited on top in the next stage. Two kinds:
  - broll:  AI stills (Canva, broll/*.png) with a slow cubic Ken Burns move plus an "Ilustrasi AI" tag
  - mg:     full-screen motion graphics, deep-teal ground and cream type, each element
            landing on its spoken word

Every time is anchored to a phrase in edit/cut_words.json, so inserts re-time
themselves when the cut changes. Layout keeps the caption band clear
(y 568-703; the captions sit on top anyway) and puts nothing important in the
bottom ~20% (TikTok UI).
"""

import json
from pathlib import Path

W = Path(__file__).parent
WORDS = json.loads((W.parent / "edit" / "cut_words.json").read_text())
FPS = 30
TEAL, DEEP, MINT, CREAM, INK, RED, MUTED = "#0E5E6F", "#08323C", "#5EEAD4", "#FFF8EE", "#0B1F2A", "#E5484D", "#6B7C85"


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

# icons: white strokes on a teal disc (viewBox 0 0 48 48)
ICON = {
    "rain": '<path d="M15 27a8 8 0 0 1 1.5-15.8A10 10 0 0 1 35 14a7 7 0 0 1-1 13.9H15z" fill="none"/>'
            '<path d="M17 32l-2 6M25 32l-2 6M33 32l-2 6"/>',
    "pulse": '<path d="M5 25h9l4-10 6 20 5-14 3 4h11"/>',
    "wave": '<path d="M5 24c4-12 9-12 13 0s9 12 13 0 9-12 12-4"/>',
    "scatter": '<circle cx="24" cy="24" r="14" stroke-dasharray="5 5" fill="none"/><circle cx="24" cy="24" r="3" fill="#fff"/>',
    "bolt": '<path d="M27 5L12 27h11l-3 16 16-23H25z" fill="none"/>',
}


def icon(name: str) -> str:
    return (f'<svg viewBox="0 0 48 48" class="mg-ico"><g stroke="#fff" stroke-width="3.2" stroke-linecap="round" '
            f'stroke-linejoin="round" fill="none">{ICON[name]}</g></svg>')


def build():
    """Returns (inserts, html_hosts, js_lines, css)."""
    I = []

    # ---- B-roll ----------------------------------------------------------------
    def broll(iid, img, start, end, move, extra=""):
        I.append({"id": iid, "kind": "broll", "start": fq(start), "end": fq(end), "img": img, "move": move, "extra": extra})

    # dark "horror film" myth, lit by a flickering tube
    broll("b1-asylum", "asylum", T("macam dalam filem filem") - 0.08, 7.85, (1.03, 1.14, 0, -30), extra="flicker")
    # REALITI: an ordinary hospital ward
    broll("b2-ward", "ward", T("adalah salah satu wad") - 0.1, T("di hospital", end=True) + 0.08, (1.10, 1.02, 0, 16))
    broll("b3-consult", "consult", T("jumpa dengan doktor") - 0.12, T("mengikut keperluan", end=True) + 0.1, (1.03, 1.12, -24, 0))
    broll("b4-therapy", "therapy", T("aktiviti terapi") - 0.1, T("senaman ringan", end=True) + 0.08, (1.12, 1.03, 20, -10))
    broll("b5-return", "return", T("mereka kembali bekerja") - 0.06, T("seperti biasa", end=True) + 0.1, (1.04, 1.13, 0, -26))
    broll("b6-saferoom", "saferoom", T("tempat yang selamat") - 0.1, T("berehat distabilkan", end=True) + 0.08, (1.02, 1.10, 18, 0))

    # ---- motion graphics ---------------------------------------------------------
    s = T("tapi tidak sebenarnya")
    I.append({"id": "m1-filem", "kind": "mg", "start": fq(s - 0.1), "end": I[1]["start"] + 0.34, "body": f"""
      <div class="half top"><img src="broll/asylum.jpg" class="half-img grim"/><div class="half-shade"></div>
        <div class="mg-chip red at-top" id="m1-c1">Dalam filem</div>
        <div class="bigx" id="m1-x"><div class="stamp-lg">TIDAK BENAR</div></div></div>
      <div class="half bot"><div class="mg-chip" id="m1-c2">Realiti</div>
        <div class="mg-title" id="m1-t">Wad psikiatri<br/><span class="mint">di Malaysia</span></div>
        <div class="mg-sub" id="m1-s">= wad di hospital biasa</div></div>
      <div class="seam" id="m1-seam"></div>""",
        "anims": [("#m1-seam", s - 0.1, "grow"), ("#m1-c1", s - 0.05, "pop"),
                  ("#m1-x", T("tidak", after=s) - LEAD, "stamp"),
                  ("#m1-c2", T("di malaysia", after=s) - 0.3, "pop"),
                  ("#m1-t", T("di malaysia", after=s) - LEAD, "rise"),
                  ("#m1-s", T("wad psikiatri adalah", after=s) - LEAD, "rise")]})

    s = T("mereka mungkin mengalami")
    conds = [("rain", "Kemurungan teruk", "kemurungan"), ("pulse", "Anxiety melampau", "anxiety"),
             ("wave", "Bipolar tidak stabil", "bipolar"), ("scatter", "Skizofrenia tidak stabil", "skizofrenia"),
             ("bolt", "Krisis emosi", "krisis emosi")]
    rows = "".join(f'<div class="crow" id="m2-r{i}"><span class="disc" id="m2-d{i}">{icon(ic)}</span><span>{txt}</span></div>'
                   for i, (ic, txt, _) in enumerate(conds))
    I.append({"id": "m2-keadaan", "kind": "mg", "start": fq(s - 0.12), "end": fq(T("krisis emosi", end=True) + 0.55), "body": f"""
      <div class="head"><div class="mg-chip" id="m2-c">Bukan agresif</div>
        <div class="mg-title" id="m2-t">Mereka mungkin<br/>mengalami<span class="mint">…</span></div></div>
      <div class="stack" style="top:760px">{rows}</div>""",
        "anims": [("#m2-c", s - 0.1, "pop"), ("#m2-t", s - 0.05, "rise")]
        + [a for i, (_, _, w) in enumerate(conds)
           for a in ((f"#m2-r{i}", T(w, after=s) - LEAD, "slidein"), (f"#m2-d{i}", T(w, after=s) - LEAD + 0.06, "pop"))]})

    s = T("pertama berisiko")
    steps = [("1", "Berisiko cederakan diri sendiri", "pertama berisiko"),
             ("2", "Berisiko cederakan orang lain", "kedua berisiko"),
             ("3", "Cara lain tidak berjaya menenangkan", "semua cara lain")]
    ladder = "".join(f'<div class="rung" id="m3-r{i}" style="top:{1300 - i * 170}px; left:{80 + i * 34}px">'
                     f'<span class="rnum">{n}</span><span>{txt}</span></div>' for i, (n, txt, _) in enumerate(steps))
    I.append({"id": "m3-restraint", "kind": "mg", "start": fq(s - 0.3), "end": fq(T("tidak berjaya", end=True) + 0.45), "body": f"""
      <div class="head"><div class="mg-chip red" id="m3-c">Physical restraint</div>
        <div class="mg-title" id="m3-t">Hanya bila<br/><span class="mint">ketiga-tiga</span> berlaku</div></div>
      <svg class="rail" viewBox="0 0 40 700" style="left:36px; top:780px; width:40px; height:700px">
        <path id="m3-rail" d="M20 690V20" stroke="{MINT}" stroke-width="6" stroke-linecap="round" fill="none"/>
        <path d="M6 34L20 12 34 34" stroke="{MINT}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" fill="none" id="m3-tip"/></svg>
      {ladder}
      <div class="rung last" id="m3-top" style="top:790px; left:182px"><span>Langkah terakhir</span></div>""",
        "anims": [("#m3-c", s - 0.28, "pop"), ("#m3-t", s - 0.22, "rise")]
        + [(f"#m3-r{i}", T(w, after=s) - LEAD, "rise") for i, (_, _, w) in enumerate(steps)]
        + [("#m3-rail", s - 0.1, ("draw", T("tidak berjaya", after=s) - s + 0.1)),
           ("#m3-tip", T("tidak berjaya", after=s) - 0.05, "fade"),
           ("#m3-top", T("tidak berjaya", after=s) - LEAD, "stamp")]})

    s = T("selepas beberapa hari")
    nodes = [("Beberapa hari", "beberapa hari"), ("Beberapa minggu", "beberapa minggu"),
             ("Keluar semula", "keluar semula"), ("Sambung rawatan", "sambung rawatan")]
    path = "".join(f'<div class="node{" hi" if i == 2 else ""}" id="m4-n{i}" style="top:{800 + i * 180}px">'
                   f'<span class="dot"></span><span class="nlabel">{txt}</span></div>' for i, (txt, _) in enumerate(nodes))
    I.append({"id": "m4-pulih", "kind": "mg", "start": fq(s - 0.1), "end": I[4]["start"] + 0.34, "body": f"""
      <div class="head"><div class="mg-chip" id="m4-c">Realiti</div>
        <div class="mg-title" id="m4-t">Masuk wad <span class="mint">bukan</span><br/>pengakhiran</div></div>
      <svg class="rail" viewBox="0 0 40 560" style="left:122px; top:830px; width:40px; height:560px">
        <path id="m4-rail" d="M20 10V550" stroke="{MINT}" stroke-width="6" stroke-linecap="round" fill="none"/></svg>
      {path}""",
        "anims": [("#m4-c", s - 0.1, "pop"), ("#m4-t", s - 0.05, "rise"),
                  ("#m4-rail", s + 0.1, ("draw", T("sambung rawatan", after=s) - s)) ]
        + [(f"#m4-n{i}", T(w, after=s) - LEAD, "slidein") for i, (_, w) in enumerate(nodes)]})

    I.sort(key=lambda x: x["start"])
    for a, b in zip(I, I[1:]):
        assert a["start"] < b["start"] and a["end"] <= b["end"], (a["id"], b["id"])
        assert b["start"] >= a["end"] - 0.5, f"{a['id']} / {b['id']} overlap by more than a crossfade"
    for x in I:
        assert x["end"] - x["start"] >= 1.8, (x["id"], x["end"] - x["start"])
        # the "TIDAK" apex (7.9-10.95s) is matted from the talking head: inserts must stay clear of it
        assert x["end"] <= 7.9 or x["start"] >= 10.95, x["id"]

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
                elif isinstance(kind, tuple) and kind[0] == "draw":
                    js.append(f"tl.fromTo('{sel}', {{strokeDashoffset:720}}, {{strokeDashoffset:0, duration:{round(kind[1], 3)}, ease:'power1.inOut'}}, {t});")
        js.append(f"tl.to('{host}', {{opacity:0, duration:0.24, ease:'power2.in'}}, {round(en - 0.24, 3)});")
    return I, hosts, js, CSS


CSS = f"""
.ins {{ position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden; pointer-events:none; }}
.ins-in {{ position:absolute; inset:0; overflow:hidden; }}
.kb {{ position:absolute; left:0; top:0; width:1080px; height:1920px; object-fit:cover; transform-origin:50% 45%; }}
.cap-shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.30) 0%, rgba(0,0,0,0) 14%,
  rgba(0,0,0,0) 22%, rgba(0,0,0,.30) 29%, rgba(0,0,0,.30) 38%, rgba(0,0,0,0) 48%); }}
.flicker {{ position:absolute; inset:0; background:#000; opacity:0; }}
.ai-tag {{ position:absolute; left:48px; top:160px; font:700 24px 'Plus Jakarta Sans'; letter-spacing:.08em; text-transform:uppercase;
  color:rgba(255,255,255,.9); background:rgba(0,0,0,.38); padding:7px 14px 6px; border-radius:10px; }}
.mg {{ position:absolute; inset:0; background:radial-gradient(120% 80% at 80% 10%, {TEAL} 0%, {DEEP} 62%, #051E25 100%);
  font-family:'Plus Jakarta Sans', sans-serif; color:{CREAM}; }}
.mg .mint {{ color:{MINT}; }}
.head {{ position:absolute; left:80px; top:160px; width:920px; }}
.mg-chip {{ display:inline-block; font-weight:800; font-size:30px; letter-spacing:.08em; text-transform:uppercase;
  padding:10px 22px 9px; border-radius:999px; background:{MINT}; color:{DEEP}; }}
.mg-chip.red {{ background:{RED}; color:#fff; }}
.mg-title {{ font-weight:800; font-size:76px; line-height:1.04; letter-spacing:-.02em; margin-top:22px; }}
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
"""
