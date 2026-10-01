"""Full-screen inserts for 'Fasa Mania dalam Bipolar Mood Disorder'.

Picture-only cutaways over the talking head (same system as videos/ward-psikiatri and
videos/ada-halusinasi-yang-normal). The voice keeps running underneath, and the captions are
composited on top in the next stage. Two kinds:
  - broll:  AI stills (Canva design DAHWvUcjQms, exported 1080x1920 -> public/broll/*.jpg) with a
            slow cubic Ken Burns move, an "Ilustrasi AI" tag and optional word-synced text.
            No faces (hands only in the consult still); nothing sensational.
  - mg:     full-screen motion graphics, deep-teal ground, cream + mint type, icons,
            each element landing on its spoken word

Every time is anchored to a phrase in edit/cut_words.json (T()), so inserts re-time themselves
when the cut changes. Layout: header (chip + title) in y 150-440, the caption band y 460-580 is
left clear (captions sit on top anyway), content from y ~620, nothing important below y 1500
(TikTok UI).
"""

import json
from pathlib import Path

W = Path(__file__).parent
WORDS = json.loads((W.parent / "edit" / "cut_words.json").read_text())
FPS = 30
TEAL, DEEP, MINT, CREAM, INK, RED, MUTED = "#0E5E6F", "#08323C", "#5EEAD4", "#FFF8EE", "#0B1F2A", "#E5484D", "#6B7C85"
LEAD = 0.12           # an element starts this much before its word so it lands on it
HERO = (5.55, 7.8)    # "kita kena tahu BIPOLAR, gangguan bipolar ni" — matted behind the head: inserts must stay clear


def T(phrase: str, after: float = 0.0, end: bool = False) -> float:
    """Start (or end) time of the first occurrence of `phrase` at/after `after` on the cut."""
    toks = phrase.split()
    for i in range(len(WORDS) - len(toks) + 1):
        if WORDS[i]["start"] >= after and [w["text"] for w in WORDS[i:i + len(toks)]] == toks:
            return WORDS[i + len(toks) - 1]["end"] if end else WORDS[i]["start"]
    raise KeyError(phrase)


def fq(t: float) -> float:
    return round(round(t * FPS) / FPS, 4)


# icons: white strokes on a teal disc (viewBox 0 0 48 48)
ICON = {
    "speech": '<path d="M8 12h32v20H22l-8 7v-7H8z"/><path d="M15 20h18M15 26h11"/>',
    "up": '<path d="M24 40V9M12 21L24 9l12 12"/>',
    "sun": '<circle cx="24" cy="24" r="8"/><path d="M24 5v5M24 38v5M5 24h5M38 24h5M10.5 10.5l3.5 3.5M34 34l3.5 3.5M10.5 37.5l3.5-3.5M34 14l3.5-3.5"/>',
    "star": '<path d="M24 6l5.3 11.6L42 19l-9.5 8.6L35 40l-11-6.4L13 40l2.5-12.4L6 19l12.7-1.4z"/>',
    "run": '<circle cx="29" cy="9" r="4"/><path d="M14 23l7-7 8 3 4 8 7 2"/><path d="M21 16l-3 13 8 6-2 9M18 29l-8 9"/>',
    "warn": '<path d="M24 7L43 40H5z"/><path d="M24 19v10M24 34v1"/>',
    "bolt": '<path d="M27 5L12 27h11l-3 16 16-23H25z"/>',
    "moon": '<path d="M36 30A15 15 0 0 1 19 9a15 15 0 1 0 17 21z"/>',
    "battery": '<rect x="5" y="15" width="34" height="18" rx="3"/><path d="M43 21v6M10 20v8M16 20v8M22 20v8M28 20v8"/>',
    "bulb": '<path d="M17 30a11 11 0 1 1 14 0v5H17z"/><path d="M19 40h10M21 44h6"/>',
    "target": '<circle cx="24" cy="24" r="17"/><circle cx="24" cy="24" r="9"/><circle cx="24" cy="24" r="2"/>',
    "pill": '<rect x="9" y="17" width="30" height="14" rx="7" transform="rotate(-35 24 24)"/><path d="M20 17l8 14"/>',
    "money": '<rect x="5" y="14" width="38" height="20" rx="3"/><circle cx="24" cy="24" r="5"/><path d="M11 19v10M37 19v10"/>',
    "bag": '<path d="M10 16h28l-3 26H13z"/><path d="M18 20v-6a6 6 0 0 1 12 0v6"/>',
    "angry": '<circle cx="24" cy="24" r="17"/><path d="M15 17l6 3M33 17l-6 3"/><path d="M17 34c4-4 10-4 14 0"/>',
    "flame": '<path d="M24 5c2 8 12 12 12 23a12 12 0 0 1-24 0c0-6 4-9 6-13 1 4 3 6 5 6-2-6 0-12 1-16z"/>',
    "therapy": '<path d="M5 9h24v15H16l-6 5v-5H5z"/><path d="M33 19h10v14h-4v5l-6-5h-9v-5"/>',
    "sliders": '<path d="M9 14h30M9 24h30M9 34h30"/><circle cx="17" cy="14" r="4"/><circle cx="31" cy="24" r="4"/><circle cx="20" cy="34" r="4"/>',
    "heart": '<path d="M24 41S7 31 7 19a9 9 0 0 1 17-4 9 9 0 0 1 17 4c0 12-17 22-17 22z"/>',
    "calendar": '<rect x="7" y="10" width="34" height="31" rx="4"/><path d="M7 19h34M16 6v8M32 6v8"/>',
    "person": '<circle cx="24" cy="13" r="6"/><path d="M12 42v-8a12 12 0 0 1 24 0v8"/>',
    "swap": '<path d="M8 16h28l-7-7M40 32H12l7 7"/>',
    "speech2": '<path d="M8 12h32v20H22l-8 7v-7H8z"/><path d="M16 22h2M23 22h2M30 22h2"/>',
    "work": '<rect x="6" y="15" width="36" height="25" rx="3"/><path d="M18 15v-5h12v5M6 25h36"/>',
}


def icon(name: str, cls: str = "mg-ico") -> str:
    return (f'<svg viewBox="0 0 48 48" class="{cls}"><g stroke="#fff" stroke-width="3.2" stroke-linecap="round" '
            f'stroke-linejoin="round" fill="none">{ICON[name]}</g></svg>')


def rows_html(prefix, items, top, h=124):
    return (f'<div class="stack" style="top:{top}px">' + "".join(
        f'<div class="crow" id="{prefix}-r{i}" style="height:{h}px"><span class="disc" id="{prefix}-d{i}">{icon(ic)}</span>'
        f'<span>{txt}</span></div>' for i, (ic, txt, _) in enumerate(items)) + "</div>")


def rows_anims(prefix, items, after):
    return [a for i, (_, _, w) in enumerate(items)
            for a in ((f"#{prefix}-r{i}", T(w, after=after) - LEAD, "slidein"),
                      (f"#{prefix}-d{i}", T(w, after=after) - LEAD + 0.06, "pop"))]


def build():
    """Returns (inserts, html_hosts, js_lines, css)."""
    I = []

    # ---- B-roll ----------------------------------------------------------------
    def broll(iid, img, start, end, move, text=None):
        I.append({"id": iid, "kind": "broll", "start": fq(start), "end": fq(end), "img": img, "move": move,
                  "text": text or []})

    # "buat banyak projek tanpa dapat menyiapkannya"
    s = T("buat banyak projek")
    broll("b1-projek", "desk", s - 0.1, T("menyiapkannya", after=s, end=True) + 0.1, (1.03, 1.12, -16, 10),
          text=[("t", '<div class="kb-stat"><span id="b1-t1">Banyak projek</span><br/>'
                      '<span id="b1-t2" class="mint">tak siap</span></div>', None),
                ("#b1-t1", None, s - LEAD), ("#b1-t2", None, T("menyiapkannya", after=s) - LEAD)])
    # "tengok orang yang ada dalam fasa mania, tidur dalam dua tiga jam je satu hari"
    s = T("tengok orang")
    broll("b2-tidur", "sleep", s - 0.08, T("satu hari", after=s, end=True) + 0.1, (1.12, 1.03, 0, -14),
          text=[("t", '<div class="kb-stat"><span id="b2-t1">2–3 jam</span><br/>'
                      '<span id="b2-t2" class="mint">tidur sehari</span></div>', None),
                ("#b2-t1", None, T("dua tiga jam", after=s) - LEAD), ("#b2-t2", None, T("satu hari", after=s) - LEAD)])
    # "pergi panjat gunung, tanpa pakai baju, tanpa pakai kasut, sebab nak cari Puteri Gunung Ledang di sana"
    s = T("panjat gunung")
    broll("b3-gunung", "mountain", s - 0.1, T("puteri gunung ledang", after=s, end=True) + 0.18, (1.03, 1.13, 0, 24),
          text=[("t", '<div class="kb-stat sm"><span id="b3-t1">Panjat gunung</span><br/>'
                      '<span id="b3-t2" class="cream2">tanpa baju · tanpa kasut</span><br/>'
                      '<span id="b3-t3" class="mint">cari Puteri Gunung Ledang</span></div>', None),
                ("#b3-t1", None, s - LEAD), ("#b3-t2", None, T("tanpa pakai baju", after=s) - LEAD),
                ("#b3-t3", None, T("puteri gunung ledang", after=s) - 0.4)])
    # "penting untuk saya ingatkan bahawa gangguan bipolar memerlukan rawatan yang sesuai"
    s = T("penting untuk")
    broll("b4-rawatan", "consult", s - 0.1, T("rawatan yang sesuai", after=s, end=True) + 0.04, (1.10, 1.02, 0, -16),
          text=[("t", '<div class="kb-stat"><span id="b4-t1">Bipolar perlukan</span><br/>'
                      '<span id="b4-t2" class="mint">rawatan yang sesuai</span></div>', None),
                ("#b4-t1", None, T("gangguan bipolar", after=s) - LEAD),
                ("#b4-t2", None, T("memerlukan rawatan", after=s) - LEAD)])

    # ---- motion graphics ---------------------------------------------------------
    # m1: myth vs reality — the myth (already stamped on card c01) on top, the mood swing drawn below
    s = T("perubahan mood")
    I.append({"id": "m1-realiti", "kind": "mg", "start": fq(s - 0.1), "end": fq(T("depression", after=s, end=True) + 0.1),
              "body": f"""
      <div class="myth-band"><div class="mg-chip red" id="m1-c1">Mitos</div>
        <div class="myth" id="m1-m"><span class="strikeword on">Gangguan personaliti / identiti</span></div>
        <div class="stamp-lg sm" id="m1-x">TIDAK BENAR</div></div>
      <div class="seam" id="m1-seam" style="top:560px"></div>
      <div class="head" style="top:610px"><div class="mg-chip" id="m1-c2">Realiti</div>
        <div class="mg-title" id="m1-t">Perubahan <span class="mint">mood</span> drastik</div></div>
      <svg class="wave" viewBox="0 0 920 560" style="left:80px; top:880px; width:920px; height:560px">
        <path d="M0 280H920" stroke="rgba(255,248,238,.22)" stroke-width="3" stroke-dasharray="10 12" fill="none"/>
        <path id="m1-wave" d="M0 280 C 90 280, 150 60, 250 60 S 400 280, 460 280 S 560 500, 660 500 S 830 280, 920 280"
          stroke="{MINT}" stroke-width="10" stroke-linecap="round" fill="none"/>
      </svg>
      <div class="wlabel up" id="m1-hi" style="left:430px; top:850px"><span class="wl1">Fasa tinggi</span>
        <span class="wl2" id="m1-hi2">MANIA</span></div>
      <div class="wlabel down" id="m1-lo" style="left:120px; top:1310px"><span class="wl1">Fasa rendah</span>
        <span class="wl2" id="m1-lo2">DEPRESSION</span></div>""",
              "anims": [("#m1-c1", s - 0.05, "fade"), ("#m1-m", s - 0.05, "fade"), ("#m1-x", s, "stamp"),
                        ("#m1-seam", s, "grow"), ("#m1-c2", s + 0.05, "pop"), ("#m1-t", s + 0.1, "rise"),
                        ("#m1-wave", T("di antara", after=s) - 0.2, ("draw", T("fasa rendah", after=s, end=True) - T("di antara", after=s))),
                        ("#m1-hi", T("fasa tinggi", after=s) - LEAD, "pop"),
                        ("#m1-hi2", T("fasa mania", after=s) - LEAD, "pop"),
                        ("#m1-lo", T("fasa rendah", after=s) - LEAD, "pop"),
                        ("#m1-lo2", T("depression", after=s) - LEAD, "pop")]})

    # m2: racing thoughts — one icon row per spoken symptom
    s = T("fikiran sangat laju")
    think = [("bulb", "Terlalu banyak idea", "terlalu banyak idea"), ("warn", "Idea yang berisiko", "melibatkan risiko"),
             ("target", "Susah nak fokus", "kesukaran")]
    I.append({"id": "m2-fikiran", "kind": "mg", "start": fq(s - 0.1), "end": fq(T("sesuatu", after=s, end=True) + 0.08),
              "body": f"""
      <div class="head"><div class="mg-chip" id="m2-c">Fikiran</div>
        <div class="mg-title" id="m2-t">Sangat <span class="mint">laju</span></div></div>
      <div class="speed" id="m2-speed">{"".join(f'<i style="top:{40 + k * 34}px; width:{220 - k * 40}px"></i>' for k in range(4))}</div>
      {rows_html("m2", think, 660)}""",
              "anims": [("#m2-c", s - 0.05, "pop"), ("#m2-t", T("sangat laju", after=s) - LEAD, "rise"),
                        ("#m2-speed", T("sangat laju", after=s), "slidein")] + rows_anims("m2", think, s)})

    # m3: risky behaviour — six rows over the (dimmed) shopping still
    s = T("seperti penggunaan")
    risks = [("pill", "Dadah / alkohol berlebihan", "dadah"), ("money", "Wang tidak terkawal", "pengeluaran wang"),
             ("bag", "Belanja berlebihan", "berbelanja"), ("angry", "Kelakuan agresif", "kelakuan agresif"),
             ("flame", "Cepat marah", "cepat marah"), ("bolt", "Impulsif", "impulsif")]
    I.append({"id": "m3-risiko", "kind": "mg", "start": fq(s - 0.1), "end": fq(T("lain lain lagi", after=s, end=True) + 0.12),
              "bg": "shopping",
              "body": f"""
      <div class="head"><div class="mg-chip red" id="m3-c">Risiko tak masuk akal</div>
        <div class="mg-title" id="m3-t">Contohnya…</div></div>
      {rows_html("m3", risks, 620, h=112)}""",
              "anims": [("#m3-c", s - 0.05, "pop"), ("#m3-t", s + 0.05, "rise")] + rows_anims("m3", risks, s)})

    # m4: treatment ladder — therapy -> medication -> manage symptoms -> quality of life
    s = T("seperti terapi")
    steps = [("therapy", "Terapi", "terapi"), ("pill", "Ubat-ubatan", "ubat ubatan"),
             ("sliders", "Urus gejala", "menguruskan gejala"), ("heart", "Kualiti hidup ↑", "kualiti hidup")]
    ladder = "".join(f'<div class="rung" id="m4-r{i}" style="top:{1300 - i * 190}px; left:{80 + i * 40}px">'
                     f'<span class="disc sm">{icon(ic)}</span><span>{txt}</span></div>'
                     for i, (ic, txt, _) in enumerate(steps))
    I.append({"id": "m4-rawatan", "kind": "mg", "start": fq(s - 0.06), "end": fq(T("menghidapnya", after=s, end=True) + 0.1),
              "body": f"""
      <div class="head"><div class="mg-chip" id="m4-c">Rawatan</div>
        <div class="mg-title" id="m4-t">Bipolar <span class="mint">boleh diurus</span></div></div>
      <svg class="rail" viewBox="0 0 40 760" style="left:30px; top:660px; width:40px; height:760px">
        <path id="m4-rail" d="M20 750V20" stroke="{MINT}" stroke-width="6" stroke-linecap="round" fill="none"/>
        <path d="M6 34L20 12 34 34" stroke="{MINT}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" fill="none" id="m4-tip"/></svg>
      {ladder}""",
              "anims": [("#m4-c", s - 0.02, "pop"), ("#m4-t", s + 0.05, "rise"),
                        ("#m4-rail", s + 0.1, ("draw", T("kualiti hidup", after=s) - s))]
              + [(f"#m4-r{i}", T(w, after=s) - LEAD, "rise") for i, (_, _, w) in enumerate(steps)]
              + [("#m4-tip", T("kualiti hidup", after=s) - 0.05, "fade")]})

    I.sort(key=lambda x: x["start"])
    for a, b in zip(I, I[1:]):
        assert a["start"] < b["start"] and a["end"] <= b["end"], (a["id"], b["id"])
        assert b["start"] >= a["end"] - 0.5, f"{a['id']} / {b['id']} overlap by more than a crossfade"
    for x in I:
        d = x["end"] - x["start"]
        assert 1.8 <= d, (x["id"], d)
        assert x["kind"] != "broll" or d <= 4.8, (x["id"], d, "B-roll stills stay 2-4s (+ fades)")
        assert x["end"] <= HERO[0] or x["start"] >= HERO[1], f"{x['id']} crosses the matted hero window"

    hosts, js = [], []
    for z, x in enumerate(I):
        iid, st, en = x["id"], x["start"], x["end"]
        host = f"#{iid}-in"   # animate the inner wrapper: the framework owns the clip element's visibility
        if x["kind"] == "broll":
            body = (f'<img src="broll/{x["img"]}.jpg" class="kb" id="{iid}-img"/><div class="cap-shade"></div>'
                    + "".join(frag for _, frag, _ in x["text"] if frag)
                    + '<div class="ai-tag">Ilustrasi AI</div>')
        else:
            bg = (f'<img src="broll/{x["bg"]}.jpg" class="kb mg-bgimg" id="{iid}-img"/><div class="mg-veil"></div>'
                  '<div class="ai-tag" style="left:auto; right:48px">Ilustrasi AI</div>') if x.get("bg") else ""
            body = f'<div class="mg{" has-bg" if bg else ""}">{bg}{x["body"]}</div>'
        hosts.append(f'<div id="ins-{iid}" class="ins clip" data-start="{st}" data-duration="{round(en - st, 4)}" '
                     f'data-track-index="{5 + z % 2}" style="z-index:{20 + z}"><div class="ins-in" id="{iid}-in">{body}</div></div>')
        js.append(f"// insert {iid} ({x['kind']}) {st:.2f}-{en:.2f}s")
        if x["kind"] == "broll":
            s0, s1, dx, dy = x["move"]
            js.append(f"tl.fromTo('{host}', {{opacity:0, scale:1.05}}, {{opacity:1, scale:1, duration:0.3, ease:'power2.out'}}, {st});")
            js.append(f"tl.fromTo('#{iid}-img', {{scale:{s0}, x:0, y:0}}, {{scale:{s1}, x:{dx}, y:{dy}, "
                      f"duration:{round(en - st, 3)}, ease:'sine.inOut'}}, {st});")
            for sel, frag, t in x["text"]:
                if t is not None:
                    js.append(f"tl.fromTo('{sel}', {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.36, ease:'power3.out'}}, {round(max(t, st + 0.15), 3)});")
        else:
            js.append(f"tl.fromTo('{host}', {{clipPath:'inset(100% 0% 0% 0%)'}}, {{clipPath:'inset(0% 0% 0% 0%)', duration:0.42, ease:'power3.inOut'}}, {st});")
            if x.get("bg"):
                js.append(f"tl.fromTo('#{iid}-img', {{scale:1.04}}, {{scale:1.12, duration:{round(en - st, 3)}, ease:'sine.inOut'}}, {st});")
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
                    js.append(f"tl.fromTo('{sel}', {{strokeDashoffset:1400}}, {{strokeDashoffset:0, duration:{round(kind[1], 3)}, ease:'power1.inOut'}}, {t});")
        js.append(f"tl.to('{host}', {{opacity:0, duration:0.24, ease:'power2.in'}}, {round(en - 0.24, 3)});")
    return I, hosts, js, CSS


CSS = f"""
.ins {{ position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden; pointer-events:none; }}
.ins-in {{ position:absolute; inset:0; overflow:hidden; }}
.kb {{ position:absolute; left:0; top:0; width:1080px; height:1920px; object-fit:cover; transform-origin:50% 45%; }}
.cap-shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.34) 0%, rgba(0,0,0,0) 14%,
  rgba(0,0,0,0) 20%, rgba(0,0,0,.34) 25%, rgba(0,0,0,.30) 32%, rgba(0,0,0,0) 42%, rgba(0,0,0,0) 52%, rgba(0,0,0,.45) 66%, rgba(0,0,0,.2) 80%); }}
.ai-tag {{ position:absolute; left:48px; top:160px; font:700 24px 'Plus Jakarta Sans'; letter-spacing:.08em; text-transform:uppercase;
  color:rgba(255,255,255,.92); background:rgba(0,0,0,.40); padding:7px 14px 6px; border-radius:10px; z-index:5; }}
.kb-stat {{ position:absolute; left:70px; right:70px; top:700px; z-index:2; text-align:center; font-family:'Plus Jakarta Sans'; font-weight:800;
  font-size:84px; line-height:1.08; letter-spacing:-.02em; color:{CREAM}; text-shadow:0 6px 28px rgba(0,0,0,.6); }}
.kb-stat::before {{ content:""; position:absolute; left:-60px; right:-60px; top:-70px; bottom:-70px; z-index:-1;
  background:radial-gradient(closest-side, rgba(4,20,26,.62), rgba(4,20,26,.38) 60%, rgba(4,20,26,0)); }}
.kb-stat.sm {{ font-size:66px; line-height:1.18; }}
.kb-stat .mint, .mg .mint {{ color:{MINT}; }}
.kb-stat .cream2 {{ color:{CREAM}; font-size:52px; font-weight:700; }}
.mg {{ position:absolute; inset:0; background:radial-gradient(120% 80% at 80% 10%, {TEAL} 0%, {DEEP} 62%, #051E25 100%);
  font-family:'Plus Jakarta Sans', sans-serif; color:{CREAM}; }}
.mg.has-bg {{ background:{DEEP}; }}
.mg-bgimg {{ filter:saturate(.7); }}
.mg-veil {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(5,30,37,.92) 0%, rgba(8,50,60,.84) 40%, rgba(5,30,37,.80) 75%, rgba(5,30,37,.92) 100%); }}
.head {{ position:absolute; left:80px; top:150px; width:920px; }}
.mg-chip {{ display:inline-block; font-weight:800; font-size:30px; letter-spacing:.08em; text-transform:uppercase;
  padding:10px 22px 9px; border-radius:999px; background:{MINT}; color:{DEEP}; }}
.mg-chip.red {{ background:{RED}; color:#fff; }}
.mg-title {{ font-weight:800; font-size:76px; line-height:1.04; letter-spacing:-.02em; margin-top:20px; }}
.stack {{ position:absolute; left:80px; width:920px; display:flex; flex-direction:column; gap:20px; }}
.crow {{ display:flex; align-items:center; gap:26px; height:124px; padding:0 30px; border-radius:26px; background:{CREAM};
  color:{INK}; font-weight:800; font-size:46px; box-shadow:0 14px 34px rgba(0,0,0,.28); }}
.disc {{ width:82px; height:82px; border-radius:50%; background:{TEAL}; display:inline-flex; align-items:center; justify-content:center; flex:none; }}
.disc.sm {{ width:72px; height:72px; }}
.mg-ico {{ width:52px; height:52px; }}
.disc.sm .mg-ico {{ width:44px; height:44px; }}
.rail {{ position:absolute; }}
.rail path {{ stroke-dasharray:1400; }}
.rung {{ position:absolute; width:800px; height:140px; display:flex; align-items:center; gap:26px; padding:0 30px; border-radius:26px;
  background:{CREAM}; color:{INK}; font-weight:800; font-size:50px; line-height:1.1; box-shadow:0 14px 34px rgba(0,0,0,.28); }}
.rung:last-child {{ background:{MINT}; }}
.myth-band {{ position:absolute; left:0; top:0; width:1080px; height:560px; background:radial-gradient(120% 90% at 80% 0%, #1B3A44 0%, #0A1E25 70%); }}
.myth-band .mg-chip {{ position:absolute; left:80px; top:170px; }}
.myth {{ position:absolute; left:80px; top:250px; font-weight:800; font-size:58px; color:rgba(255,248,238,.62); }}
.strikeword {{ background:linear-gradient({RED},{RED}) left 55%/0% 8px no-repeat; }}
.strikeword.on {{ background-size:100% 8px; }}
.stamp-lg {{ display:inline-block; transform:rotate(-7deg); border:8px solid {RED}; color:{RED}; border-radius:18px; font-weight:800;
  font-size:76px; letter-spacing:.04em; padding:8px 28px 2px; background:rgba(255,248,238,.94); }}
.stamp-lg.sm {{ position:absolute; right:80px; top:360px; font-size:56px; border-width:7px; }}
.seam {{ position:absolute; left:0; width:1080px; height:12px; background:{CREAM}; transform-origin:left center; z-index:3; }}
.wave {{ position:absolute; overflow:visible; }}
.wave #m1-wave {{ stroke-dasharray:1400; }}
.wlabel {{ position:absolute; display:flex; flex-direction:column; align-items:flex-start; gap:6px; }}
.wl1 {{ font-weight:700; font-size:36px; color:rgba(255,248,238,.85); }}
.wl2 {{ font-weight:800; font-size:64px; letter-spacing:.02em; padding:6px 22px 4px; border-radius:16px; }}
.wlabel.up .wl2 {{ background:{MINT}; color:{DEEP}; }}
.wlabel.down .wl2 {{ background:{CREAM}; color:{TEAL}; }}
.speed {{ position:absolute; right:80px; top:300px; width:240px; height:180px; }}
.speed i {{ position:absolute; right:0; height:10px; border-radius:6px; background:{MINT}; opacity:.75; }}
"""
