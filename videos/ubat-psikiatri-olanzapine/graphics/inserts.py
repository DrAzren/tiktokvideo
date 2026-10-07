"""Full-screen inserts for 'Ubat Psikiatri Olanzapine'. Template: videos/ward-psikiatri/graphics/inserts.py.

Picture-only cutaways over the talking head. The voice keeps running underneath, and
the captions are composited on top in the next stage. Two kinds:
  - broll:  AI stills (Canva, broll/*.jpg) with a slow cubic Ken Burns move plus an "Ilustrasi AI" tag
  - mg:     full-screen motion graphics, deep-teal ground, cream + mint type, icons, each element
            landing on its spoken word

Every time is anchored to a phrase in edit/cut_words.json, so inserts re-time themselves when the
cut changes. The caption line sits at y ~390-480 (just above the speaker's hair); inserts keep that
band free of important type, and nothing important goes in the bottom ~20% (TikTok UI).
Each insert also emits SFX events (whoosh in/out, ting on items, thud on stamps) → sfx_events.json.
"""

import json
from pathlib import Path

W = Path(__file__).parent
WORDS = json.loads((W.parent / "edit" / "cut_words.json").read_text())
FPS = 30
TEAL, DEEP, MINT, CREAM, INK, RED, MUTED = "#0E5E6F", "#08323C", "#5EEAD4", "#FFF8EE", "#0B1F2A", "#E5484D", "#6B7C85"
HERO_WINDOW = (0.0, 3.65)   # "OLANZAPINE" apex lockup (matted behind the head): no insert may cover it


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
    "ear": '<path d="M16 20a9 9 0 0 1 18 0c0 6-6 7-6 13a5 5 0 0 1-9 2"/><path d="M21 21a3.5 3.5 0 0 1 7 0"/>'
           '<path d="M38 14l4-3M39 21h5M38 28l4 3"/>',
    "cloud": '<path d="M14 30a7 7 0 0 1 1-14 9 9 0 0 1 17 0 6.5 6.5 0 0 1 1 13z"/><circle cx="12" cy="37" r="2.5"/><circle cx="7" cy="42" r="1.5"/>',
    "brain": '<path d="M24 10v28"/><path d="M24 12a6 6 0 0 0-11 2 6 6 0 0 0-4 9 6 6 0 0 0 3 9 6 6 0 0 0 12 4"/>'
             '<path d="M24 12a6 6 0 0 1 11 2 6 6 0 0 1 4 9 6 6 0 0 1-3 9 6 6 0 0 1-12 4"/>',
    "fork": '<path d="M15 6v12a4 4 0 0 0 8 0V6M19 6v36"/><path d="M33 42V6c-4 2-6 8-6 14h6"/>',
    "moon": '<path d="M33 30A13 13 0 0 1 20 12a13 13 0 1 0 15 17z"/><path d="M34 8l1.5 3 3 1.5-3 1.5L34 17l-1.5-3-3-1.5 3-1.5z"/>',
    "drop": '<path d="M24 6c6 9 11 15 11 21a11 11 0 0 1-22 0c0-6 5-12 11-21z"/>',
    "cube": '<path d="M24 6l15 8v16l-15 8-15-8V14z"/><path d="M9 14l15 8 15-8M24 22v16"/>',
    "gauge": '<path d="M8 32a16 16 0 1 1 32 0"/><path d="M24 32l8-10"/><circle cx="24" cy="32" r="2.5"/>',
    "stop": '<path d="M16 6h16l10 10v16L32 42H16L6 32V16z"/><path d="M16 24h16"/>',
    "heart": '<path d="M24 40S8 30 8 19a8 8 0 0 1 16-3 8 8 0 0 1 16 3c0 11-16 21-16 21z"/>',
    "check": '<path d="M12 25l8 8 16-17"/>',
    "warn": '<path d="M24 7L4 41h40z"/><path d="M24 19v10M24 35v1"/>',
    "pill": '<rect x="6" y="17" width="36" height="14" rx="7" transform="rotate(-35 24 24)"/><path d="M19 15l10 18" transform="rotate(0)"/>',
}


def icon(name: str, cls: str = "mg-ico") -> str:
    return (f'<svg viewBox="0 0 48 48" class="{cls}"><g stroke="#fff" stroke-width="3.2" stroke-linecap="round" '
            f'stroke-linejoin="round" fill="none">{ICON[name]}</g></svg>')


def build():
    """Returns (inserts, html_hosts, js_lines, css, sfx_events)."""
    I = []

    # ---- B-roll ----------------------------------------------------------------
    def broll(iid, img, start, end, move, extra=""):
        I.append({"id": iid, "kind": "broll", "start": fq(start), "end": fq(end), "img": img, "move": move, "extra": extra})

    # "Pertama, kebaikan ubat olanzapine ni. Ubat olanzapine ni memang sangat bagus" — generic yellow tablets in a
    # blister (AI, deliberately unbranded: the user asked for a brand lookalike; a real product's packaging is not
    # recreated), bright white still, so the label is dark ink in the empty area above the tablets;
    # our own type on top: chip lands on "kebaikan", the name on "olanzapine"
    broll("b0-olanzapine", "olanzapine", T("pertama") - 0.06, T("tidak dinafikan") - 0.1, (1.03, 1.12, 0, 20), extra="label")
    # "Ada juga yang cakap, dunia kembali senyap…" — a still lake at dawn, the quote typed over it
    broll("b1-senyap", "lake", T("ada juga yang cakap") - 0.1, T("ubat ini") - 0.02, (1.04, 1.13, 0, -24), extra="quote")
    # "Ubat ini sangat bagus untuk penyakit-penyakit tertentu"
    broll("b2-ubat", "pills", T("ubat ini") - 0.02, T("tapi kita kena") - 0.1, (1.12, 1.03, 16, -10))
    # "kita kena amalkan pemakanan yang seimbang"
    broll("b3-makan", "meal", T("kita kena amalkan") - 0.1, T("kesan sampingan yang lain") - 0.08, (1.03, 1.12, 0, 18))
    # "terutamanya masa awal-awal start rawatan dulu" (mengantuk)
    broll("b4-mengantuk", "bedroom", T("terutamanya masa") - 0.1, T("yang ketiga") - 0.12, (1.10, 1.02, -20, 0))
    # plug: "atau nak dapatkan khidmat nasihat tentang kesihatan mental"
    broll("b5-klinik", "clinic", T("atau nak dapatkan") - 0.1, T("di klinik saya") - 0.1, (1.03, 1.11, 18, -12))

    # ---- motion graphics ---------------------------------------------------------
    # MG1 — the promise: Kebaikan vs Keburukan split
    s = T("kebaikan dan keburukan")
    I.append({"id": "m1-split", "kind": "mg", "start": fq(s - 0.15), "end": fq(T("pertama") - 0.06), "body": f"""
      <div class="half top good"><div class="split-in">
        <span class="bigdisc mint" id="m1-d1">{icon("check", "big-ico dark")}</span>
        <div class="split-word" id="m1-w1">KEBAIKAN</div></div></div>
      <div class="half bot bad"><div class="split-in">
        <span class="bigdisc red" id="m1-d2">{icon("warn", "big-ico")}</span>
        <div class="split-word" id="m1-w2">KEBURUKAN</div></div></div>
      <div class="seam" id="m1-seam"></div>
      <div class="vs" id="m1-vs">VS</div>
      <div class="mg-chip center-chip" id="m1-c">Ubat olanzapine</div>""",
        "anims": [("#m1-c", s - 0.12, "pop"), ("#m1-seam", s - 0.1, "grow"),
                  ("#m1-d1", s - LEAD, "pop"), ("#m1-w1", s - LEAD + 0.05, "rise"),
                  ("#m1-vs", T("dan", after=s) - 0.05, "stamp"),
                  ("#m1-d2", T("keburukan", after=s) - LEAD, "pop"), ("#m1-w2", T("keburukan", after=s) - LEAD + 0.05, "rise")]})

    # MG2 — what it helps: 5 rows with icons, one per spoken benefit
    s = T("ia boleh kurangkan")
    rows = [("ear", "Kurangkan halusinasi", "halusinasi"), ("cloud", "Kurangkan delusi", "dilusi"),
            ("brain", "Otak lebih tenang", "tenang"), ("fork", "Selera makan meningkat", "selera"),
            ("moon", "Tidur lebih lena", "tidur")]
    html = "".join(f'<div class="crow" id="m2-r{i}"><span class="disc" id="m2-d{i}">{icon(ic)}</span><span>{txt}</span></div>'
                   for i, (ic, txt, _) in enumerate(rows))
    I.append({"id": "m2-bantu", "kind": "mg", "start": fq(s - 0.15), "end": fq(T("tidur seseorang", end=True) + 0.45), "body": f"""
      <div class="head"><div class="mg-chip" id="m2-c">Kebaikan</div>
        <div class="mg-title" id="m2-t">Olanzapine<br/><span class="mint">boleh bantu…</span></div></div>
      <div class="stack" style="top:720px">{html}</div>""",
        "anims": [("#m2-c", s - 0.12, "pop"), ("#m2-t", s - 0.05, "rise")]
        + [a for i, (_, _, w) in enumerate(rows)
           for a in ((f"#m2-r{i}", T(w, after=s) - LEAD, "slidein"), (f"#m2-d{i}", T(w, after=s) - LEAD + 0.06, "pop"))]})

    # MG3 — side effect #3: metabolic trio, three gauges rising on each word
    s = T("yang ketiga")
    trio = [("drop", "Kolesterol", "kolesterol"), ("cube", "Gula", "gula"), ("gauge", "Tekanan darah", "tekanan darah")]
    tiles = "".join(f'<div class="tile" id="m3-t{i}" style="left:{80 + i * 316}px"><span class="disc lg" id="m3-d{i}">{icon(ic)}</span>'
                    f'<div class="tlabel">{txt}</div><div class="bar"><div class="fill" id="m3-f{i}"></div></div>'
                    f'<div class="up" id="m3-u{i}">▲</div></div>' for i, (ic, txt, _) in enumerate(trio))
    I.append({"id": "m3-metabolik", "kind": "mg", "start": fq(s - 0.15), "end": fq(T("tekanan darah", end=True) + 0.5), "body": f"""
      <div class="head"><div class="mg-chip red" id="m3-c">Kesan sampingan #3</div>
        <div class="mg-title" id="m3-tt">Metabolik<br/><span class="mint">side effect</span></div></div>
      <div class="risk" id="m3-r">Risiko naik:</div>
      {tiles}""",
        "anims": [("#m3-c", s - 0.12, "pop"), ("#m3-tt", T("metabolik", after=s) - LEAD, "rise"),
                  ("#m3-r", T("risiko", after=s) - LEAD, "fade")]
        + [a for i, (_, _, w) in enumerate(trio)
           for a in ((f"#m3-t{i}", T(w, after=s) - LEAD, "rise"), (f"#m3-f{i}", T(w, after=s) - LEAD + 0.1, ("fill", 0.7)),
                     (f"#m3-u{i}", T(w, after=s) + 0.35, "pop"))]})

    # MG4 — the two rules: jangan stop sendiri / jangan give up
    s = T("yang penting")
    I.append({"id": "m4-penting", "kind": "mg", "start": fq(s - 0.12), "end": fq(T("giv ap", end=True) + 0.25), "body": f"""
      <div class="head"><div class="mg-chip" id="m4-c">Yang penting</div></div>
      <div class="rule" id="m4-r1" style="top:640px"><span class="disc xl red-bg">{icon("stop", "mg-ico xl")}</span>
        <div><div class="rk">JANGAN</div><div class="rt">stop ubat sendiri</div></div></div>
      <div class="rule" id="m4-r2" style="top:960px"><span class="disc xl">{icon("heart", "mg-ico xl")}</span>
        <div><div class="rk">JANGAN</div><div class="rt mint">give up</div></div></div>""",
        "anims": [("#m4-c", s - 0.1, "pop"), ("#m4-r1", T("jangan stop", after=s) - LEAD, "slidein"),
                  ("#m4-r2", T("jangan giv", after=s) - LEAD, "slidein")]})

    I.sort(key=lambda x: x["start"])
    for a, b in zip(I, I[1:]):
        assert a["start"] < b["start"] and a["end"] <= b["end"], (a["id"], b["id"])
        assert b["start"] >= a["end"] - 0.5, f"{a['id']} / {b['id']} overlap by more than a crossfade"
    for x in I:
        assert x["end"] - x["start"] >= 1.8, (x["id"], x["end"] - x["start"])
        assert x["kind"] != "broll" or x["end"] - x["start"] <= 4.2, (x["id"], x["end"] - x["start"])
        assert x["end"] <= HERO_WINDOW[0] or x["start"] >= HERO_WINDOW[1], x["id"]

    hosts, js, sfx = [], [], []
    for z, x in enumerate(I):
        iid, st, en = x["id"], x["start"], x["end"]
        host = f"#{iid}-in"   # animate the inner wrapper: the framework owns the clip element's visibility
        if x["kind"] == "broll":
            body = (f'<img src="broll/{x["img"]}.jpg" class="kb" id="{iid}-img"/>'
                    f'<div class="cap-shade"></div>'
                    + (f'<div class="quote" id="{iid}-q"><span class="qmark">“</span>Dunia kembali <span class="mint">senyap</span>”'
                       f'<div class="qby" id="{iid}-qb">— kata pesakit</div></div>' if x["extra"] == "quote" else "")
                    + (f'<div class="label" id="{iid}-lb"><div class="mg-chip" id="{iid}-lc">Pertama · Kebaikan</div>'
                       f'<div class="lname" id="{iid}-ln">OLANZAPINE</div><div class="lsub" id="{iid}-ls">Ubat psikiatri</div></div>'
                       if x["extra"] == "label" else "")
                    + '<div class="ai-tag">Ilustrasi AI</div>')
        else:
            body = f'<div class="mg">{x["body"]}</div>'
        hosts.append(f'<div id="ins-{iid}" class="ins clip" data-start="{st}" data-duration="{round(en - st, 4)}" '
                     f'data-track-index="{5 + z % 2}" style="z-index:{20 + z}"><div class="ins-in" id="{iid}-in">{body}</div></div>')
        js.append(f"// insert {iid} ({x['kind']}) {st:.2f}-{en:.2f}s")
        prev_adjacent = z > 0 and abs(I[z - 1]["end"] - st) < 0.05
        if not prev_adjacent:
            sfx.append({"t": st, "kind": "whoosh_in", "src": iid})
        if x["kind"] == "broll":
            s0, s1, dx, dy = x["move"]
            js.append(f"tl.fromTo('{host}', {{opacity:0, scale:1.05}}, {{opacity:1, scale:1, duration:0.3, ease:'power2.out'}}, {st});")
            js.append(f"tl.fromTo('#{iid}-img', {{scale:{s0}, x:0, y:0}}, {{scale:{s1}, x:{dx}, y:{dy}, "
                      f"duration:{round(en - st, 3)}, ease:'sine.inOut'}}, {st});")
            if x["extra"] == "label":
                for sel, t, kind in ((f"#{iid}-lc", T("kebaikan", after=st) - LEAD, "pop"),
                                     (f"#{iid}-ln", T("olanzapin", after=st) - LEAD, "rise"),
                                     (f"#{iid}-ls", T("olanzapin", after=st) + 0.35, "fade")):
                    if kind == "pop":
                        js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.34, ease:'back.out(1.8)'}}, {round(t, 3)});")
                        sfx.append({"t": round(t, 3), "kind": "ting", "src": sel})
                    elif kind == "rise":
                        js.append(f"tl.fromTo('{sel}', {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.42, ease:'power3.out'}}, {round(t, 3)});")
                    else:
                        js.append(f"tl.fromTo('{sel}', {{opacity:0}}, {{opacity:1, duration:0.3, ease:'power2.out'}}, {round(t, 3)});")
            if x["extra"] == "quote":
                tq = round(T("dunia") - LEAD, 3)
                js.append(f"tl.fromTo('#{iid}-q', {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.5, ease:'power3.out'}}, {tq});")
                js.append(f"tl.fromTo('#{iid}-qb', {{opacity:0}}, {{opacity:1, duration:0.4, ease:'power2.out'}}, {round(T('senyap') + 0.2, 3)});")
                sfx.append({"t": tq, "kind": "chime", "src": iid})
        else:
            js.append(f"tl.fromTo('{host}', {{clipPath:'inset(100% 0% 0% 0%)'}}, {{clipPath:'inset(0% 0% 0% 0%)', duration:0.42, ease:'power3.inOut'}}, {st});")
            for sel, t, kind in x["anims"]:
                t = round(max(t, st + 0.12), 3)
                if kind == "pop":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.34, ease:'back.out(1.8)'}}, {t});")
                    sfx.append({"t": t, "kind": "ting", "src": sel})
                elif kind == "rise":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.42, ease:'power3.out'}}, {t});")
                elif kind == "slidein":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0, x:80}}, {{opacity:1, x:0, duration:0.4, ease:'power3.out'}}, {t});")
                    sfx.append({"t": t, "kind": "swish", "src": sel})
                elif kind == "fade":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0}}, {{opacity:1, duration:0.3, ease:'power2.out'}}, {t});")
                elif kind == "stamp":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:1.9}}, {{opacity:1, scale:1, duration:0.26, ease:'power4.out'}}, {t});")
                    sfx.append({"t": t + 0.2, "kind": "thud", "src": sel})
                elif kind == "grow":
                    js.append(f"tl.fromTo('{sel}', {{scaleX:0}}, {{scaleX:1, duration:0.5, ease:'power3.inOut'}}, {t});")
                elif isinstance(kind, tuple) and kind[0] == "fill":
                    js.append(f"tl.fromTo('{sel}', {{scaleY:0}}, {{scaleY:1, duration:{kind[1]}, ease:'power3.out'}}, {t});")
        nxt_adjacent = z + 1 < len(I) and abs(I[z + 1]["start"] - en) < 0.05
        js.append(f"tl.to('{host}', {{opacity:0, duration:0.24, ease:'power2.in'}}, {round(en - 0.24, 3)});")
        sfx.append({"t": en - 0.12, "kind": "whoosh_swap" if nxt_adjacent else "whoosh_out", "src": iid})
    return I, hosts, js, CSS, sfx


CSS = f"""
.ins {{ position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden; pointer-events:none; }}
.ins-in {{ position:absolute; inset:0; overflow:hidden; }}
.kb {{ position:absolute; left:0; top:0; width:1080px; height:1920px; object-fit:cover; transform-origin:50% 45%; }}
.cap-shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.34) 0%, rgba(0,0,0,0) 12%,
  rgba(0,0,0,0) 17%, rgba(0,0,0,.30) 21%, rgba(0,0,0,.30) 26%, rgba(0,0,0,0) 32%); }}
.ai-tag {{ position:absolute; left:48px; top:150px; font:700 24px 'Plus Jakarta Sans'; letter-spacing:.08em; text-transform:uppercase;
  color:rgba(255,255,255,.92); background:rgba(0,0,0,.40); padding:7px 14px 6px; border-radius:10px; }}
.quote {{ position:absolute; left:80px; right:80px; top:1040px; font:800 92px/1.02 'Plus Jakarta Sans'; letter-spacing:-.02em; color:{CREAM};
  text-shadow:0 6px 30px rgba(0,0,0,.45); }}
.quote .mint {{ color:{MINT}; }}
.label {{ position:absolute; left:80px; right:80px; top:540px; font-family:'Plus Jakarta Sans'; }}
.lname {{ font-weight:800; font-size:128px; line-height:1; letter-spacing:-.01em; color:{INK}; margin-top:22px; }}
.lsub {{ font-weight:700; font-size:46px; color:{TEAL}; margin-top:12px; }}
.qmark {{ color:{MINT}; }}
.qby {{ font:700 40px 'Plus Jakarta Sans'; color:rgba(255,248,238,.9); margin-top:22px; letter-spacing:0; }}
.mg {{ position:absolute; inset:0; background:radial-gradient(120% 80% at 80% 10%, {TEAL} 0%, {DEEP} 62%, #051E25 100%);
  font-family:'Plus Jakarta Sans', sans-serif; color:{CREAM}; }}
.mg .mint {{ color:{MINT}; }}
.head {{ position:absolute; left:80px; top:140px; width:920px; }}
.mg-chip {{ display:inline-block; font-weight:800; font-size:30px; letter-spacing:.08em; text-transform:uppercase;
  padding:10px 22px 9px; border-radius:999px; background:{MINT}; color:{DEEP}; }}
.mg-chip.red {{ background:{RED}; color:#fff; }}
.mg-title {{ font-weight:800; font-size:66px; line-height:1.02; letter-spacing:-.02em; margin-top:18px; }}  /* ends ~y350: caption line is y~392 */
.stack {{ position:absolute; left:80px; width:920px; display:flex; flex-direction:column; gap:22px; }}
.crow {{ display:flex; align-items:center; gap:26px; height:118px; padding:0 30px; border-radius:26px; background:{CREAM};
  color:{INK}; font-weight:800; font-size:46px; box-shadow:0 14px 34px rgba(0,0,0,.28); }}
.disc {{ width:78px; height:78px; border-radius:50%; background:{TEAL}; display:inline-flex; align-items:center; justify-content:center; flex:none; }}
.disc.lg {{ width:110px; height:110px; }}
.disc.xl {{ width:150px; height:150px; }}
.disc.red-bg {{ background:{RED}; }}
.mg-ico {{ width:50px; height:50px; }}
.disc.lg .mg-ico {{ width:66px; height:66px; }}
.mg-ico.xl {{ width:88px; height:88px; }}
/* MG1 split */
.half {{ position:absolute; left:0; width:1080px; height:960px; overflow:hidden; }}
.half.top {{ top:0; background:radial-gradient(120% 90% at 80% 20%, {TEAL} 0%, {DEEP} 75%); }}
.half.bot {{ top:960px; background:radial-gradient(120% 90% at 20% 80%, #3A1418 0%, #1C0A0D 80%); }}
.split-in {{ position:absolute; left:0; right:0; display:flex; flex-direction:column; align-items:center; gap:26px; }}
.half.top .split-in {{ top:520px; }}
.half.bot .split-in {{ top:150px; }}
.bigdisc {{ width:150px; height:150px; border-radius:50%; display:flex; align-items:center; justify-content:center; }}
.bigdisc.mint {{ background:{MINT}; }}
.bigdisc.red {{ background:{RED}; }}
.big-ico {{ width:92px; height:92px; }}
.big-ico.dark g {{ stroke:{DEEP}; }}
.split-word {{ font-weight:800; font-size:120px; letter-spacing:-.01em; line-height:1; }}
.half.top .split-word {{ color:{MINT}; }}
.half.bot .split-word {{ color:#FFB4B6; }}
.seam {{ position:absolute; left:0; top:954px; width:1080px; height:12px; background:{CREAM}; transform-origin:left center; z-index:3; }}
.vs {{ position:absolute; left:470px; top:890px; width:140px; height:140px; border-radius:50%; background:{CREAM}; color:{INK};
  font-weight:800; font-size:56px; display:flex; align-items:center; justify-content:center; z-index:4; box-shadow:0 10px 30px rgba(0,0,0,.4); }}
.center-chip {{ position:absolute; left:50%; top:160px; transform-origin:left center; translate:-50% 0; }}
/* MG3 tiles */
.risk {{ position:absolute; left:80px; top:690px; font-weight:800; font-size:48px; color:rgba(255,248,238,.85); }}
.tile {{ position:absolute; top:790px; width:290px; height:560px; border-radius:30px; background:{CREAM}; color:{INK};
  display:flex; flex-direction:column; align-items:center; padding-top:40px; gap:24px; box-shadow:0 14px 34px rgba(0,0,0,.3); }}
.tlabel {{ font-weight:800; font-size:40px; text-align:center; line-height:1.08; height:88px; display:flex; align-items:center; padding:0 12px; }}
.bar {{ width:70px; height:200px; border-radius:18px; background:#E3EEEC; overflow:hidden; display:flex; align-items:flex-end; }}
.fill {{ width:100%; height:82%; background:linear-gradient(0deg, {RED}, #FF8A8D); border-radius:18px; transform-origin:50% 100%; }}
.up {{ position:absolute; right:26px; top:26px; color:{RED}; font-size:40px; font-weight:800; }}
/* MG4 rules */
.rule {{ position:absolute; left:80px; width:920px; height:260px; border-radius:34px; background:{CREAM}; color:{INK};
  display:flex; align-items:center; gap:40px; padding:0 44px; box-shadow:0 14px 34px rgba(0,0,0,.3); }}
.rk {{ font-weight:800; font-size:44px; letter-spacing:.1em; color:{RED}; }}
.rt {{ font-weight:800; font-size:76px; line-height:1.0; letter-spacing:-.02em; }}
.rt.mint {{ color:{TEAL}; }}
"""
