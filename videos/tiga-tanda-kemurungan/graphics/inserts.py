"""Full-screen inserts for 'Tiga Tanda Kemurungan Yang Anda Tak Perasan'.

Template: videos/ward-psikiatri/graphics/inserts.py. Picture-only cutaways over the talking head;
the voice keeps running underneath and the captions are composited on top in the next stage.
  - broll:  AI stills (Canva, public/broll/*.jpg) with a slow cubic Ken Burns move + "Ilustrasi AI" tag
  - mg:     full-screen motion graphics, deep-teal ground, cream + mint type, icons, each element
            landing on its spoken word

Every time is anchored to a phrase in edit/cut_words.json, so inserts re-time themselves when
the cut changes. The caption line sits at y 370-460 (on top anyway); nothing important goes in
the bottom ~20% (TikTok UI) or the right ~15% (action buttons).
"""

import json
from pathlib import Path

W = Path(__file__).parent
WORDS = json.loads((W.parent / "edit" / "cut_words.json").read_text())
FPS = 30
TEAL, DEEP, MINT, CREAM, INK, RED, MUTED = "#0E5E6F", "#08323C", "#5EEAD4", "#FFF8EE", "#0B1F2A", "#E5484D", "#6B7C85"
HERO_WINDOW = (6.0, 9.35)  # the matted "KEMURUNGAN" apex ("ini mungkin tanda KEMURUNGAN … tak perasan"): keep clear


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
    "game": '<rect x="5" y="15" width="38" height="20" rx="10"/><path d="M14 21v8M10 25h8"/>'
            '<circle cx="31" cy="23" r="1.6" fill="#fff"/><circle cx="35" cy="28" r="1.6" fill="#fff"/>',
    "tv": '<rect x="6" y="11" width="36" height="24" rx="4"/><path d="M18 41h12M24 35v6"/><path d="M21 19l8 4-8 4z" fill="#fff"/>',
    "food": '<path d="M7 24h34a17 17 0 0 1-34 0z"/><path d="M17 17c0-3 3-3 3-6M25 17c0-3 3-3 3-6"/>',
    "friends": '<circle cx="17" cy="17" r="6"/><circle cx="32" cy="19" r="5"/><path d="M6 39c1-7 6-11 11-11s10 4 11 11"/><path d="M28 30c2-1 3-1 4-1 5 0 9 3 10 10"/>',
    "sun": '<circle cx="24" cy="24" r="8"/><path d="M24 5v5M24 38v5M5 24h5M38 24h5M10.5 10.5l3.5 3.5M34 34l3.5 3.5M37.5 10.5L34 14M14 34l-3.5 3.5"/>',
    "cloud": '<path d="M14 34a8 8 0 0 1 1.5-15.8A10 10 0 0 1 34 21a7 7 0 0 1-1 13.9H14z"/>',
    "moon": '<path d="M33 30A14 14 0 0 1 19 9a14 14 0 1 0 20 17 14 14 0 0 1-6 4z"/>',
    "bed": '<path d="M5 36V14M5 28h38v8M43 28v-5a5 5 0 0 0-5-5H21v10"/><circle cx="13" cy="22" r="3.5"/>',
    "empty": '<circle cx="24" cy="24" r="16"/><path d="M17 30c4-3 10-3 14 0"/><path d="M18 19h.1M30 19h.1"/>',
    "phone": '<rect x="14" y="5" width="20" height="38" rx="4"/><path d="M21 37h6"/>',
    "wave": '<path d="M5 24c4-12 9-12 13 0s9 12 13 0 9-12 12-4"/>',
    "fog": '<path d="M8 16h26M14 24h28M6 32h24M20 40h16"/>',
    "battery": '<rect x="5" y="15" width="34" height="18" rx="4"/><path d="M43 21v6"/><rect x="9" y="19" width="7" height="10" fill="#fff"/>',
}


def icon(name: str) -> str:
    return (f'<svg viewBox="0 0 48 48" class="mg-ico"><g stroke="#fff" stroke-width="3.2" stroke-linecap="round" '
            f'stroke-linejoin="round" fill="none">{ICON[name]}</g></svg>')


def build():
    """Returns (inserts, html_hosts, js_lines, css)."""
    I = []

    def broll(iid, img, start, end, move):
        I.append({"id": iid, "kind": "broll", "start": fq(start), "end": fq(end), "img": img, "move": move})

    # ---- motion graphics -----------------------------------------------------------
    # M1 — sign 1, myth vs reality: "bukan ... sebab nak diet / tak ada perasaan nak makan /
    #      bukan sebab malas / tapi badan rasa berat"
    s = T("bukan selalu skip breakfast")
    I.append({"id": "m1-sebab", "kind": "mg", "start": fq(s - 0.1), "end": fq(T("rasa berat", after=s, end=True) + 0.3), "body": f"""
      <div class="half top"><img src="broll/breakfast.jpg" class="half-img grim"/><div class="half-shade"></div>
        <div class="mg-chip red at-top" id="m1-c1">Bukan sebab…</div>
        <div class="myths">
          <div class="myth" id="m1-a"><span class="strk">Nak diet</span></div>
          <div class="myth" id="m1-b"><span class="strk">Malas</span></div>
        </div>
        <div class="bigx" id="m1-x"><div class="stamp-lg">TIDAK BENAR</div></div></div>
      <div class="half bot"><div class="mg-chip" id="m1-c2">Tapi sebab…</div>
        <div class="stack" style="top:150px; left:80px">
          <div class="crow" id="m1-r1"><span class="disc">{icon("food")}</span><span>Tak ada selera nak makan</span></div>
          <div class="crow" id="m1-r2"><span class="disc">{icon("bed")}</span><span>Badan rasa berat</span></div>
        </div></div>
      <div class="seam" id="m1-seam"></div>""",
        "anims": [("#m1-seam", s - 0.1, "grow"), ("#m1-c1", s - 0.05, "pop"),
                  ("#m1-a", T("diet", after=s) - LEAD, "rise"),
                  ("#m1-c2", T("skip breakfast sebab tak", after=s) - 0.1, "pop"),
                  ("#m1-r1", T("perasaan", after=s) - LEAD, "slidein"),
                  ("#m1-b", T("malas", after=s) - LEAD, "rise"),
                  ("#m1-a .strk", T("tapi", after=s) - 0.1, "strike"),
                  ("#m1-b .strk", T("tapi", after=s), "strike"),
                  ("#m1-x", T("tapi", after=s) + 0.1, "stamp"),
                  ("#m1-r2", T("berat", after=s) - LEAD, "slidein")]})

    # M2 — sign 2, anhedonia: the things that used to be fun, then "semua rasa kosong"
    s = T("kalau dulu suka")
    acts = [("game", "Main game", "game"), ("tv", "Tengok drama", "drama"),
            ("food", "Makan kat luar", "makan kat luar"), ("friends", "Lepak-lepak", "lepak")]
    rows = "".join(f'<div class="crow" id="m2-r{i}"><span class="disc" id="m2-d{i}">{icon(ic)}</span>'
                   f'<span class="strk">{txt}</span></div>' for i, (ic, txt, _) in enumerate(acts))
    k = T("kosong", after=s)
    I.append({"id": "m2-kosong", "kind": "mg", "start": fq(s - 0.12), "end": fq(T("kosong", after=s, end=True) + 0.55), "body": f"""
      <div class="head"><div class="mg-chip" id="m2-c">Dulu seronok</div>
        <div class="mg-title" id="m2-t">Dulu anda <span class="mint">suka…</span></div></div>
      <div class="stack" style="top:640px">{rows}</div>
      <div class="bigx" style="top:1290px" id="m2-x"><div class="stamp-lg mintstamp">SEMUA RASA KOSONG</div></div>""",
        "anims": [("#m2-c", s - 0.1, "pop"), ("#m2-t", s - 0.05, "rise")]
        + [a for i, (_, _, w) in enumerate(acts)
           for a in ((f"#m2-r{i}", T(w, after=s) - LEAD, "slidein"), (f"#m2-d{i}", T(w, after=s) - LEAD + 0.06, "pop"))]
        + [(f"#m2-r{i} .strk", k - 0.25 + 0.07 * i, "strike") for i in range(len(acts))]
        + [(".m2dim", k - 0.1, "dim"), ("#m2-x", k - LEAD, "stamp")]})

    # M3 — sign 4, a day of mood swings: pagi okey → tengah hari murung → malam nak menangis
    s = T("kejap pagi")
    day = [("sun", "Pagi", "Rasa okey", "okey"), ("cloud", "Tengah hari", "Rasa murung", "murung"),
           ("moon", "Malam", "Nak menangis", "menangis")]
    nodes = "".join(f'<div class="dnode" id="m3-n{i}" style="top:{700 + i * 230}px"><span class="disc big">{icon(ic)}</span>'
                    f'<span class="dtext"><span class="dwhen">{when}</span><span class="dwhat">{what}</span></span></div>'
                    for i, (ic, when, what, _) in enumerate(day))
    I.append({"id": "m3-hari", "kind": "mg", "start": fq(s - 0.12), "end": fq(T("menangis", after=s, end=True) + 0.45), "body": f"""
      <div class="head"><div class="mg-chip" id="m3-c">Mood swing</div>
        <div class="mg-title" id="m3-t">Dalam <span class="mint">satu hari</span></div></div>
      <svg class="rail" viewBox="0 0 40 520" style="left:146px; top:760px; width:40px; height:520px">
        <path id="m3-rail" d="M20 10V510" stroke="{MINT}" stroke-width="6" stroke-linecap="round" fill="none"/></svg>
      {nodes}""",
        "anims": [("#m3-c", s - 0.1, "pop"), ("#m3-t", s - 0.05, "rise"),
                  ("#m3-rail", s + 0.1, ("draw", T("menangis", after=s) - s))]
        + [(f"#m3-n{i}", T(w, after=s) - LEAD - (0.35 if i == 0 else 0.25), "slidein") for i, (_, _, _, w) in enumerate(day)]})

    # M4 — close, recap of all six signs on "kalau tanda-tanda ni makin kerap, jangan biarkan ianya melarat"
    s = T("kalau tanda tanda ni makin")
    six = [("bed", "Bangun lewat, skip makan"), ("empty", "Hilang minat"), ("phone", "Terus capai telefon"),
           ("wave", "Mood swing teruk"), ("fog", "Mudah lupa, brain fog"), ("battery", "Penat & cepat marah")]
    recap = "".join(f'<div class="rrow" id="m4-r{i}"><span class="rnum">{i + 1}</span><span class="disc sm">{icon(ic)}</span>'
                    f'<span>{txt.replace("&", "&amp;")}</span></div>' for i, (ic, txt) in enumerate(six))
    kerap = T("makin kerap", after=s)
    I.append({"id": "m4-recap", "kind": "mg", "start": fq(s - 0.12), "end": fq(T("melarat", after=s, end=True) + 0.5), "body": f"""
      <div class="head"><div class="mg-chip" id="m4-c">Ringkasan</div>
        <div class="mg-title" id="m4-t"><span class="mint">6 tanda</span> kemurungan</div></div>
      <div class="stack tight" style="top:520px">{recap}</div>
      <div class="bigx" style="top:1330px" id="m4-x"><div class="stamp-lg one">JANGAN BIARKAN MELARAT</div></div>""",
        "anims": [("#m4-c", s - 0.1, "pop"), ("#m4-t", s - 0.05, "rise")]
        + [(f"#m4-r{i}", s + 0.15 + i * ((kerap - s) / 6), "slidein") for i in range(6)]
        + [("#m4-x", T("melarat", after=s) - LEAD, "stamp")]})

    # ---- B-roll (Canva AI stills, design DAHXM1UREWM) ------------------------------------
    broll("b1-bed", "bed", T("minda") - 0.06, T("tak ada tenaga", after=T("minda"), end=True) + 0.1, (1.03, 1.12, 0, -24))
    broll("b2-phone", "phone", T("benda pertama") - 0.1, T("adalah telefon", end=True) + 0.15, (1.12, 1.03, 18, 0))
    broll("b3-fog", "fog", T("baca satu benda") - 0.1, T("nak ingat", end=True) + 0.1, (1.03, 1.11, -16, -10))
    broll("b4-rain", "rain", T("benda kecil pun") - 0.1, T("frustrated", end=True) + 0.15, (1.10, 1.02, 0, 18))
    broll("b5-clinic", "clinic", T("saya akan buat penilaian") - 0.1, T("sesuai untuk anda", end=True) + 0.1, (1.02, 1.10, 16, 0))

    I.sort(key=lambda x: x["start"])
    for a, b in zip(I, I[1:]):
        assert a["start"] < b["start"] and a["end"] <= b["end"], (a["id"], b["id"])
        assert b["start"] >= a["end"] - 0.5, f"{a['id']} / {b['id']} overlap by more than a crossfade"
    for x in I:
        assert 1.8 <= x["end"] - x["start"] <= 7.5, (x["id"], x["end"] - x["start"])
        assert x["end"] <= HERO_WINDOW[0] or x["start"] >= HERO_WINDOW[1], x["id"]

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
                elif kind == "strike":
                    js.append(f"tl.fromTo('{sel}', {{backgroundSize:'0% 8px'}}, {{backgroundSize:'100% 8px', duration:0.3, ease:'power2.inOut'}}, {t});")
                elif kind == "dim":
                    js.append(f"tl.to('#{iid}-in .crow', {{opacity:0.45, duration:0.3, ease:'power2.out'}}, {t});")
                elif isinstance(kind, tuple) and kind[0] == "draw":
                    js.append(f"tl.fromTo('{sel}', {{strokeDashoffset:720}}, {{strokeDashoffset:0, duration:{round(kind[1], 3)}, ease:'power1.inOut'}}, {t});")
        js.append(f"tl.to('{host}', {{opacity:0, duration:0.24, ease:'power2.in'}}, {round(en - 0.24, 3)});")
    return I, hosts, js, CSS


CSS = f"""
.ins {{ position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden; pointer-events:none; }}
.ins-in {{ position:absolute; inset:0; overflow:hidden; }}
.kb {{ position:absolute; left:0; top:0; width:1080px; height:1920px; object-fit:cover; transform-origin:50% 45%; }}
.cap-shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.34) 0%, rgba(0,0,0,.12) 12%,
  rgba(0,0,0,.30) 19%, rgba(0,0,0,.30) 25%, rgba(0,0,0,0) 34%); }}
.ai-tag {{ position:absolute; left:48px; top:150px; font:700 24px 'Plus Jakarta Sans'; letter-spacing:.08em; text-transform:uppercase;
  color:rgba(255,255,255,.92); background:rgba(0,0,0,.40); padding:7px 14px 6px; border-radius:10px; }}
.mg {{ position:absolute; inset:0; background:radial-gradient(120% 80% at 80% 10%, {TEAL} 0%, {DEEP} 62%, #051E25 100%);
  font-family:'Plus Jakarta Sans', sans-serif; color:{CREAM}; }}
.mg .mint {{ color:{MINT}; }}
.head {{ position:absolute; left:80px; top:150px; width:860px; }}  /* one-line titles only: captions run at y 370-460 */
.mg-chip {{ display:inline-block; font-weight:800; font-size:30px; letter-spacing:.08em; text-transform:uppercase;
  padding:10px 22px 9px; border-radius:999px; background:{MINT}; color:{DEEP}; }}
.mg-chip.red {{ background:{RED}; color:#fff; }}
.mg-title {{ font-weight:800; font-size:76px; line-height:1.04; letter-spacing:-.02em; margin-top:22px; }}
.stack {{ position:absolute; left:80px; width:860px; display:flex; flex-direction:column; gap:22px; }}
.stack.tight {{ gap:16px; }}
.crow {{ display:flex; align-items:center; gap:26px; height:118px; padding:0 30px; border-radius:26px; background:{CREAM};
  color:{INK}; font-weight:800; font-size:46px; box-shadow:0 14px 34px rgba(0,0,0,.28); }}
.rrow {{ display:flex; align-items:center; gap:20px; height:104px; padding:0 26px; border-radius:24px; background:{CREAM};
  color:{INK}; font-weight:800; font-size:40px; box-shadow:0 12px 30px rgba(0,0,0,.26); }}
.rnum {{ width:52px; height:52px; flex:none; border-radius:50%; background:{RED}; color:#fff; font-size:30px; display:inline-flex;
  align-items:center; justify-content:center; }}
.disc {{ width:78px; height:78px; border-radius:50%; background:{TEAL}; display:inline-flex; align-items:center; justify-content:center; flex:none; }}
.disc.sm {{ width:64px; height:64px; }}
.disc.big {{ width:116px; height:116px; border:6px solid {MINT}; }}
.mg-ico {{ width:50px; height:50px; }}
.disc.big .mg-ico {{ width:66px; height:66px; }}
.strk {{ background:linear-gradient({RED},{RED}) left 55%/0% 8px no-repeat; }}
.rail {{ position:absolute; }}
.rail path {{ stroke-dasharray:720; }}
.dnode {{ position:absolute; left:104px; display:flex; align-items:center; gap:34px; }}
.dtext {{ display:flex; flex-direction:column; padding:16px 30px; border-radius:24px; background:{CREAM}; color:{INK}; min-width:560px; }}
.dwhen {{ font-weight:700; font-size:32px; color:{TEAL}; text-transform:uppercase; letter-spacing:.06em; }}
.dwhat {{ font-weight:800; font-size:56px; line-height:1.05; }}
.half {{ position:absolute; left:0; width:1080px; height:960px; overflow:hidden; }}
.half.top {{ top:0; }}
.half.bot {{ top:960px; background:radial-gradient(120% 90% at 20% 0%, {TEAL} 0%, {DEEP} 70%); }}
.half-img {{ position:absolute; left:0; top:-300px; width:1080px; height:1920px; object-fit:cover; }}
.grim {{ filter:grayscale(.85) contrast(1.1) brightness(.62); }}
.half-shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.45), rgba(0,0,0,.2) 40%, rgba(0,0,0,.55)); }}
.at-top {{ position:absolute; left:80px; top:150px; }}
.myths {{ position:absolute; left:80px; top:520px; display:flex; gap:26px; }}
.myth {{ font-weight:800; font-size:64px; color:{CREAM}; background:rgba(8,50,60,.72); padding:10px 30px; border-radius:22px; }}
.bigx {{ position:absolute; left:0; right:0; top:690px; text-align:center; }}
.stamp-lg {{ display:inline-block; transform:rotate(-6deg); border:8px solid {RED}; color:{RED}; border-radius:18px; font-weight:800;
  font-size:72px; letter-spacing:.03em; padding:8px 28px 2px; background:rgba(255,248,238,.94); }}
.stamp-lg.one {{ font-size:52px; white-space:nowrap; }}
.stamp-lg.mintstamp {{ border-color:{MINT}; color:{DEEP}; background:{MINT}; font-size:64px; }}
.half.bot .mg-chip {{ position:absolute; left:80px; top:60px; }}
.seam {{ position:absolute; left:0; top:954px; width:1080px; height:12px; background:{CREAM}; transform-origin:left center; z-index:3; }}
"""
