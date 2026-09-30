"""Full-screen inserts for 'Ada Halusinasi Yang Normal'.

Picture-only cutaways over the talking head. The voice keeps running underneath, and the
captions are composited on top in the next stage. Two kinds:
  - broll:  AI stills (Canva design DAHWpHUFMB8, exported 1080x1920 -> public/broll/*.jpg) with a
            slow cubic Ken Burns move, an "Ilustrasi AI" tag and optional word-synced text
  - mg:     full-screen motion graphics, deep-teal ground, cream + mint type, icons,
            each element landing on its spoken word

Every time is anchored to a phrase in edit/cut_words.json (T()), so inserts re-time themselves
when the cut changes. Layout: header (chip + title) in y 150-440, the caption band y 460-575
is left clear (captions sit on top anyway), content from y ~620, nothing important below
y 1500 (TikTok UI).
"""

import json
from pathlib import Path

W = Path(__file__).parent
WORDS = json.loads((W.parent / "edit" / "cut_words.json").read_text())
FPS = 30
TEAL, DEEP, MINT, CREAM, INK, RED, MUTED = "#0E5E6F", "#08323C", "#5EEAD4", "#FFF8EE", "#0B1F2A", "#E5484D", "#6B7C85"
LEAD = 0.12          # an element starts this much before its word so it lands on it
HERO = (14.25, 15.5)  # "Itu adalah HALUSINASI" — matted behind the head: inserts must stay clear


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
    "ear": '<path d="M16 19a9 9 0 0 1 18 0c0 6-6 7-6 13a5 5 0 0 1-9 2"/><path d="M21 19a4 4 0 0 1 8 0c0 3-3 3-3 6"/>',
    "eye": '<path d="M4 24s7-11 20-11 20 11 20 11-7 11-20 11S4 24 4 24z"/><circle cx="24" cy="24" r="5"/>',
    "nose": '<path d="M26 8c-1 9-2 14 3 21a5 5 0 0 1-3 9h-6"/><path d="M16 33a4 4 0 0 0 4 5"/>',
    "taste": '<path d="M14 18h20v6a10 10 0 0 1-20 0z"/><path d="M24 26v8"/><path d="M12 18c3-5 21-5 24 0"/>',
    "hand": '<path d="M16 26V13a2.5 2.5 0 0 1 5 0v10M21 22V10a2.5 2.5 0 0 1 5 0v12M26 22V12a2.5 2.5 0 0 1 5 0v12'
            'M31 24v-6a2.5 2.5 0 0 1 5 0v10c0 8-5 13-12 13-5 0-8-3-11-8l-4-7a2.5 2.5 0 0 1 4-3l3 4"/>',
    "speech": '<path d="M8 12h32v20H22l-8 7v-7H8z"/><path d="M15 20h18M15 26h11"/>',
    "person": '<circle cx="24" cy="13" r="6"/><path d="M12 42v-8a12 12 0 0 1 24 0v8"/>',
    "bolt": '<path d="M27 5L12 27h11l-3 16 16-23H25z"/>',
    "rain": '<path d="M15 27a8 8 0 0 1 1.5-15.8A10 10 0 0 1 35 14a7 7 0 0 1-1 13.9H15z"/><path d="M17 32l-2 6M25 32l-2 6M33 32l-2 6"/>',
    "pill": '<rect x="9" y="17" width="30" height="14" rx="7" transform="rotate(-35 24 24)"/><path d="M20 17l8 14"/>',
    "head": '<path d="M30 40v-6h4a3 3 0 0 0 3-3v-5l3-1-3-6c0-8-6-13-14-13S9 11 9 19c0 5 2 8 5 11v10"/>'
            '<path d="M22 14l-3 6h5l-3 6"/>',
    "brain": '<path d="M24 10v28M24 12a6 6 0 0 0-10 2 6 6 0 0 0-4 9 6 6 0 0 0 3 9 6 6 0 0 0 11 4'
             'M24 12a6 6 0 0 1 10 2 6 6 0 0 1 4 9 6 6 0 0 1-3 9 6 6 0 0 1-11 4"/>',
}


def icon(name: str, cls: str = "mg-ico") -> str:
    return (f'<svg viewBox="0 0 48 48" class="{cls}"><g stroke="#fff" stroke-width="3.2" stroke-linecap="round" '
            f'stroke-linejoin="round" fill="none">{ICON[name]}</g></svg>')


def build():
    """Returns (inserts, html_hosts, js_lines, css)."""
    I = []

    # ---- B-roll ----------------------------------------------------------------
    def broll(iid, img, start, end, move, text=None):
        I.append({"id": iid, "kind": "broll", "start": fq(start), "end": fq(end), "img": img, "move": move,
                  "text": text or []})

    # "atau anda nampak bayang-bayang hitam lalu, tapi bila tengok balik, tak ada apa-apa, kosong"
    broll("b1-hallway", "hallway", T("bayang bayang hitam") - 0.1, T("kosong", end=True) + 0.08, (1.04, 1.13, 18, -10))
    # "pernah tak rasa ada sesuatu yang tarik selimut anda, tapi bila buka mata ..."
    broll("b2-bedroom", "bedroom", T("pernah tak rasa") - 0.1, T("buka mata", end=True) + 0.25, (1.12, 1.03, 0, 14))
    # "bila anda tak cukup rehat selama beberapa hari, contohnya lima hari, tidur dua tiga jam je"
    s = T("bila anda tak cukup")
    broll("b3-desk", "desk", s - 0.1, T("jam je", after=s, end=True) + 0.2, (1.03, 1.12, -20, 0),
          text=[("stat", '<div class="kb-stat"><span id="b3-t1">5 hari</span> <span id="b3-x" class="mint">×</span> '
                         '<span id="b3-t2">2–3 jam tidur</span></div>', None),
                ("#b3-t1", None, T("lima hari", after=s) - LEAD), ("#b3-x", None, T("tidur dua", after=s) - 0.2),
                ("#b3-t2", None, T("dua tiga jam", after=s) - LEAD)])
    # "tapi kalau ia berterusan, better jumpa doktor untuk check"
    s = T("tapi kalau ia berterusan")
    broll("b4-doctor", "doctor", s - 0.1, T("untuk check", after=s, end=True) + 0.15, (1.10, 1.02, 0, -16),
          text=[("q", '<div class="kb-stat"><span id="b4-t1">Berterusan?</span><br/>'
                      '<span id="b4-t2" class="mint">Jumpa doktor</span></div>', None),
                ("#b4-t1", None, T("berterusan", after=s) - LEAD), ("#b4-t2", None, T("jumpa doktor", after=s) - LEAD)])

    # ---- motion graphics ---------------------------------------------------------
    # m1: the five senses, one row per spoken sense
    s = T("ia boleh melibatkan")
    senses = [("ear", "Pendengaran", "pendengaran"), ("eye", "Penglihatan", "penglihatan"), ("nose", "Bau", "bau"),
              ("taste", "Rasa", "rasa"), ("hand", "Sentuhan", "sentuhan")]
    rows = "".join(f'<div class="crow" id="m1-r{i}"><span class="disc" id="m1-d{i}">{icon(ic)}</span><span>{txt}</span></div>'
                   for i, (ic, txt, _) in enumerate(senses))
    I.append({"id": "m1-deria", "kind": "mg", "start": fq(s - 0.1), "end": fq(T("tak wujud pun", after=s, end=True) + 0.1),
              "body": f"""
      <div class="head"><div class="mg-chip" id="m1-c">Melibatkan 5 deria</div>
        <div class="mg-title" id="m1-t">Yang sebenarnya<br/><span class="mint">tak wujud</span></div></div>
      <div class="stack" style="top:640px">{rows}</div>""",
              "anims": [("#m1-c", s - 0.05, "pop"), ("#m1-t", s + 0.05, "rise")]
              + [a for i, (_, _, w) in enumerate(senses)
                 for a in ((f"#m1-r{i}", T(w, after=s) - LEAD, "slidein"), (f"#m1-d{i}", T(w, after=s) - LEAD + 0.06, "pop"))]})

    # m2: myth vs reality split (the myth card precedes it, so the top half arrives already stamped)
    s = T("ia juga boleh berlaku")
    I.append({"id": "m2-realiti", "kind": "mg", "start": fq(s - 0.12), "end": fq(T("orang yang sihat", end=True) + 0.3),
              "body": f"""
      <div class="half top"><div class="mg-chip red at-top" id="m2-c1">Mitos</div>
        <div class="myth" id="m2-m"><span class="strikeword on">Hanya pesakit mental</span></div>
        <div class="bigx" id="m2-x"><div class="stamp-lg">TIDAK BENAR</div></div></div>
      <div class="half bot"><div class="mg-chip" id="m2-c2">Realiti</div>
        <div class="mg-title" id="m2-t">Boleh berlaku pada<br/><span class="mint">sesiapa saja</span></div>
        <div class="pills"><span class="pill-lg" id="m2-p1">Orang normal</span><span class="pill-lg" id="m2-p2">Orang sihat</span></div></div>
      <div class="seam" id="m2-seam"></div>""",
              "anims": [("#m2-seam", s - 0.1, "grow"), ("#m2-c1", s - 0.1, "pop"), ("#m2-m", s - 0.08, "fade"),
                        ("#m2-x", s, "stamp"), ("#m2-c2", s + 0.1, "pop"),
                        ("#m2-t", T("sesiapa saja", after=s) - LEAD, "rise"),
                        ("#m2-p1", T("orang yang normal", after=s) - LEAD, "pop"),
                        ("#m2-p2", T("orang yang sihat", after=s) - LEAD, "pop")]})

    # m3: before sleep vs after waking — two AI stills, top then bottom
    s = T("ada juga halusinasi yang berlaku selepas")
    I.append({"id": "m3-tidur", "kind": "mg", "start": fq(s - 0.1), "end": fq(T("hypnopompic hallucination", after=s, end=True) + 0.35),
              "body": f"""
      <div class="half top"><img src="broll/bedroom.jpg" class="half-img" style="top:-420px"/><div class="half-shade"></div>
        <div class="slot" style="top:150px"><div class="mg-chip" id="m3-c1">#1 · Sebelum tidur</div>
          <div class="slot-title" id="m3-t1">Hypnagogic</div></div></div>
      <div class="half bot img"><img src="broll/morning.jpg" class="half-img" id="m3-img2" style="top:-560px"/><div class="half-shade dark"></div>
        <div class="slot" style="top:120px"><div class="mg-chip sun" id="m3-c2">#2 · Selepas bangun</div>
          <div class="slot-title" id="m3-t2">Hypnopompic</div></div></div>
      <div class="seam" id="m3-seam"></div>
      <div class="ai-tag" style="top:1440px">Ilustrasi AI</div>""",
              "anims": [("#m3-c1", s - 0.05, "pop"), ("#m3-t1", s + 0.05, "rise"),
                        ("#m3-img2", T("selepas kita bangun", after=s) - 0.3, "wipeup"),
                        ("#m3-seam", T("selepas kita bangun", after=s) - 0.3, "grow"),
                        ("#m3-c2", T("selepas kita bangun", after=s) - LEAD, "pop"),
                        ("#m3-t2", T("hypnopompic", after=s) - LEAD, "rise")]})

    # m4: other causes, one icon row per spoken cause
    s = T("halusinasi ini boleh disebabkan")
    causes = [("bolt", "Stres melampau", "stres"), ("rain", "Kesedihan berpanjangan", "kesedihan"),
              ("pill", "Penggunaan dadah", "penggunaan dadah"), ("head", "Migrain", "migrain"),
              ("brain", "Gangguan neurologi", "gangguan neurologi")]
    rows = "".join(f'<div class="crow" id="m4-r{i}"><span class="disc" id="m4-d{i}">{icon(ic)}</span><span>{txt}'
                   + ('<span class="crow-sub" id="m4-sub"> · Parkinson</span>' if i == 4 else "") + '</span></div>'
                   for i, (ic, txt, _) in enumerate(causes))
    I.append({"id": "m4-punca", "kind": "mg", "start": fq(s - 0.1), "end": fq(T("parkinson", after=s, end=True) + 0.35),
              "body": f"""
      <div class="head"><div class="mg-chip" id="m4-c">Punca lain</div>
        <div class="mg-title" id="m4-t">Boleh disebabkan<br/><span class="mint">banyak faktor</span></div></div>
      <div class="stack" style="top:640px">{rows}</div>""",
              "anims": [("#m4-c", s - 0.05, "pop"), ("#m4-t", T("disebabkan", after=s) - LEAD, "rise")]
              + [a for i, (_, _, w) in enumerate(causes)
                 for a in ((f"#m4-r{i}", T(w, after=s) - LEAD, "slidein"), (f"#m4-d{i}", T(w, after=s) - LEAD + 0.06, "pop"))]
              + [("#m4-sub", T("parkinson", after=s) - LEAD, "fade")]})

    # m5: warning ladder -> needs treatment
    s = T("tapi kalau halusinasi ini semakin")
    steps = [("1", "Semakin kerap", "semakin kerap"), ("2", "Ganggu kehidupan seharian", "mengganggu kehidupan"),
             ("3", "Rasa takut atau paranoid", "perasaan takut")]
    ladder = "".join(f'<div class="rung" id="m5-r{i}" style="top:{1270 - i * 165}px; left:{80 + i * 34}px">'
                     f'<span class="rnum">{n}</span><span>{txt}</span></div>' for i, (n, txt, _) in enumerate(steps))
    I.append({"id": "m5-amaran", "kind": "mg", "start": fq(s - 0.1), "end": fq(T("memerlukan rawatan", after=s, end=True) + 0.4),
              "body": f"""
      <div class="head"><div class="mg-chip red" id="m5-c">Bila perlu risau?</div>
        <div class="mg-title" id="m5-t">Tanda <span class="mint">amaran</span></div></div>
      <svg class="rail" viewBox="0 0 40 700" style="left:36px; top:640px; width:40px; height:700px">
        <path id="m5-rail" d="M20 690V20" stroke="{MINT}" stroke-width="6" stroke-linecap="round" fill="none"/>
        <path d="M6 34L20 12 34 34" stroke="{MINT}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" fill="none" id="m5-tip"/></svg>
      {ladder}
      <div class="rung-top" id="m5-p" style="top:650px; left:182px">Petanda masalah mental</div>
      <div class="rung last" id="m5-top" style="top:760px; left:182px"><span>Perlukan rawatan</span></div>""",
              "anims": [("#m5-c", s - 0.05, "pop"), ("#m5-t", s + 0.05, "rise")]
              + [(f"#m5-r{i}", T(w, after=s) - LEAD, "rise") for i, (_, _, w) in enumerate(steps)]
              + [("#m5-rail", s + 0.1, ("draw", T("petanda", after=s) - s)),
                 ("#m5-tip", T("petanda", after=s) - 0.05, "fade"),
                 ("#m5-p", T("petanda masalah", after=s) - LEAD, "rise"),
                 ("#m5-top", T("memerlukan rawatan", after=s) - LEAD, "stamp")]})

    I.sort(key=lambda x: x["start"])
    for a, b in zip(I, I[1:]):
        assert a["start"] < b["start"] and a["end"] <= b["end"], (a["id"], b["id"])
        assert b["start"] >= a["end"] - 0.5, f"{a['id']} / {b['id']} overlap by more than a crossfade"
    for x in I:
        assert 1.8 <= x["end"] - x["start"], (x["id"], x["end"] - x["start"])
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
            body = f'<div class="mg">{x["body"]}</div>'
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
                elif kind == "wipeup":
                    js.append(f"tl.fromTo('{sel}', {{clipPath:'inset(100% 0% 0% 0%)'}}, {{clipPath:'inset(0% 0% 0% 0%)', duration:0.5, ease:'power3.inOut'}}, {t});")
                elif isinstance(kind, tuple) and kind[0] == "draw":
                    js.append(f"tl.fromTo('{sel}', {{strokeDashoffset:720}}, {{strokeDashoffset:0, duration:{round(kind[1], 3)}, ease:'power1.inOut'}}, {t});")
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
.kb-stat {{ position:absolute; left:70px; right:70px; top:700px; text-align:center; font-family:'Plus Jakarta Sans'; font-weight:800;
  font-size:84px; line-height:1.08; letter-spacing:-.02em; color:{CREAM}; text-shadow:0 6px 28px rgba(0,0,0,.6); }}
.kb-stat .mint, .mg .mint {{ color:{MINT}; }}
.mg {{ position:absolute; inset:0; background:radial-gradient(120% 80% at 80% 10%, {TEAL} 0%, {DEEP} 62%, #051E25 100%);
  font-family:'Plus Jakarta Sans', sans-serif; color:{CREAM}; }}
.head {{ position:absolute; left:80px; top:150px; width:920px; }}
.mg-chip {{ display:inline-block; font-weight:800; font-size:30px; letter-spacing:.08em; text-transform:uppercase;
  padding:10px 22px 9px; border-radius:999px; background:{MINT}; color:{DEEP}; }}
.mg-chip.red {{ background:{RED}; color:#fff; }}
.mg-chip.sun {{ background:#FFD58A; color:{DEEP}; }}
.mg-title {{ font-weight:800; font-size:76px; line-height:1.04; letter-spacing:-.02em; margin-top:20px; }}
.stack {{ position:absolute; left:80px; width:920px; display:flex; flex-direction:column; gap:22px; }}
.crow {{ display:flex; align-items:center; gap:26px; height:124px; padding:0 30px; border-radius:26px; background:{CREAM};
  color:{INK}; font-weight:800; font-size:48px; box-shadow:0 14px 34px rgba(0,0,0,.28); }}
.crow-sub {{ color:{TEAL}; font-weight:700; }}
.disc {{ width:82px; height:82px; border-radius:50%; background:{TEAL}; display:inline-flex; align-items:center; justify-content:center; flex:none; }}
.mg-ico {{ width:52px; height:52px; }}
.rail {{ position:absolute; }}
.rail path {{ stroke-dasharray:720; }}
.rung {{ position:absolute; width:820px; height:130px; display:flex; align-items:center; gap:24px; padding:0 30px; border-radius:24px;
  background:{CREAM}; color:{INK}; font-weight:800; font-size:42px; line-height:1.1; box-shadow:0 14px 34px rgba(0,0,0,.28); }}
.rung.last {{ width:700px; height:120px; background:{RED}; color:#fff; font-size:54px; box-shadow:0 14px 40px rgba(229,72,77,.35);
  justify-content:center; transform-origin:center; }}
.rung-top {{ position:absolute; font-weight:800; font-size:40px; color:{MINT}; }}
.rnum {{ width:64px; height:64px; flex:none; border-radius:50%; background:{RED}; color:#fff; font-size:34px; display:inline-flex;
  align-items:center; justify-content:center; }}
.half {{ position:absolute; left:0; width:1080px; height:960px; overflow:hidden; }}
.half.top {{ top:0; background:radial-gradient(120% 90% at 80% 0%, #1B3A44 0%, #0A1E25 70%); }}
.half.bot {{ top:960px; background:radial-gradient(120% 90% at 20% 0%, {TEAL} 0%, {DEEP} 70%); }}
.half-img {{ position:absolute; left:0; width:1080px; height:1920px; object-fit:cover; }}
.half-shade.dark {{ background:linear-gradient(180deg, rgba(4,20,26,.78) 0%, rgba(4,20,26,.55) 38%, rgba(0,0,0,.05) 62%, rgba(0,0,0,.35)); }}
.half-shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.45), rgba(0,0,0,.1) 45%, rgba(0,0,0,.5)); }}
.at-top {{ position:absolute; left:80px; top:170px; }}
.myth {{ position:absolute; left:80px; top:640px; font-weight:800; font-size:70px; color:rgba(255,248,238,.62); }}
.strikeword {{ background:linear-gradient({RED},{RED}) left 55%/0% 8px no-repeat; }}
.strikeword.on {{ background-size:100% 8px; }}
.bigx {{ position:absolute; right:70px; top:760px; }}
.stamp-lg {{ display:inline-block; transform:rotate(-7deg); border:8px solid {RED}; color:{RED}; border-radius:18px; font-weight:800;
  font-size:76px; letter-spacing:.04em; padding:8px 28px 2px; background:rgba(255,248,238,.94); }}
.half.bot > .mg-chip {{ position:absolute; left:80px; top:70px; }}
.half.bot > .mg-title {{ position:absolute; left:80px; top:150px; font-size:86px; margin:0; }}
.pills {{ position:absolute; left:80px; top:420px; display:flex; gap:22px; }}
.pill-lg {{ font-weight:800; font-size:50px; padding:18px 32px; border-radius:22px; background:{CREAM}; color:{INK}; }}
.slot {{ position:absolute; left:80px; }}
.slot-title {{ font-weight:800; font-size:104px; letter-spacing:-.02em; margin-top:18px; color:{CREAM}; text-shadow:0 6px 30px rgba(0,0,0,.5); }}
.seam {{ position:absolute; left:0; top:954px; width:1080px; height:12px; background:{CREAM}; transform-origin:left center; z-index:3; }}
"""
