"""Full-screen inserts for 'Kesan Skip Ubat Psikiatri'. Template: videos/ubat-psikiatri-olanzapine/graphics/inserts.py.

Picture-only cutaways over the talking head. The voice keeps running underneath, and
the captions are composited on top in the next stage. Two kinds:
  - broll:  AI stills (Canva, broll/*.jpg) with a slow cubic Ken Burns move, an "Ilustrasi AI" tag and
            our own designed label (cream panel: chip + name), each part landing on its spoken word
  - mg:     full-screen motion graphics, deep-teal ground, cream + mint type, icons, each element
            landing on its spoken word

Every time is anchored to a phrase in edit/cut_words.json, so inserts re-time themselves when the
cut changes. The caption line sits at y ~390-500 (just above the speaker's hair); inserts keep that
band free of important type, and nothing important goes in the bottom ~20% (TikTok UI).
Each insert also emits SFX events → sfx_events.json (audio/make_sfx.py turns them into a cue sheet).
"""

import json
from pathlib import Path

W = Path(__file__).parent
WORDS = json.loads((W.parent / "edit" / "cut_words.json").read_text())
FPS = 30
TEAL, DEEP, MINT, CREAM, INK, RED, MUTED = "#0E5E6F", "#08323C", "#5EEAD4", "#FFF8EE", "#0B1F2A", "#E5484D", "#6B7C85"
AMBER = "#F5A524"
HERO_WINDOW = (1.6, 4.1)   # "BERHENTI" apex lockup (matted behind the head): no insert may cover it


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
    "wave": '<path d="M4 30c5-10 9-10 14 0s9 10 14 0 9-10 14 0"/><path d="M4 18c5-7 9-7 14 0s9 7 14 0"/>',
    "bolt": '<path d="M27 4L11 27h11l-3 17 18-25H25z"/>',
    "nausea": '<circle cx="24" cy="24" r="17"/><path d="M17 20h1M30 20h1"/><path d="M15 32c3-3 6 0 9-3s6 0 9-3"/>',
    "spiral": '<path d="M24 24a3 3 0 0 1 3 3 6 6 0 0 1-6 6 9 9 0 0 1-9-9 12 12 0 0 1 12-12 15 15 0 0 1 15 15"/>',
    "moonx": '<path d="M30 32A13 13 0 0 1 17 13a13 13 0 1 0 15 18z"/><path d="M34 7l8 8M42 7l-8 8"/>',
    "storm": '<path d="M14 27a7 7 0 0 1 1-14 9 9 0 0 1 17 0 6.5 6.5 0 0 1 1 13"/><path d="M25 24l-5 8h7l-4 10"/>',
    "tangle": '<path d="M7 31c7-20 15 9 21-7s-17-7-10 7 18 9 23-6"/>',
    "reset": '<path d="M38 24a14 14 0 1 1-4-10"/><path d="M37 5v10H27"/>',
    "nochat": '<path d="M8 10h32v20H22l-8 7v-7H8z"/><path d="M5 5l38 38"/>',
    "capsule": '<rect x="5" y="17" width="38" height="14" rx="7" transform="rotate(-35 24 24)"/><path d="M19 16l10 16"/>',
    "stop": '<path d="M16 6h16l10 10v16L32 42H16L6 32V16z"/><path d="M17 24h14"/>',
    "play": '<path d="M16 10l22 14-22 14z"/>',
    "skip": '<path d="M7 12l15 12-15 12z"/><path d="M22 12l15 12-15 12z"/><path d="M41 12v24"/>',
}


def icon(name: str, cls: str = "mg-ico") -> str:
    return (f'<svg viewBox="0 0 48 48" class="{cls}"><g stroke="#fff" stroke-width="3.2" stroke-linecap="round" '
            f'stroke-linejoin="round" fill="none">{ICON[name]}</g></svg>')


def build():
    """Returns (inserts, html_hosts, js_lines, css, sfx_events)."""
    I = []

    # ---- B-roll ----------------------------------------------------------------
    # label: [(part, html, t)]  part in chip / name / sub; drawn on a cream panel high in frame
    def broll(iid, img, start, end, move, label=(), quote=None):
        I.append({"id": iid, "kind": "broll", "start": fq(start), "end": fq(end), "img": img, "move": move,
                  "label": label, "quote": quote})

    # "Ubat psikiatri ni macam pelindung untuk kita" — an umbrella sheltering in the rain
    s = T("ubat psikiatri ni")
    broll("b0-pelindung", "umbrella", s - 0.08, T("bila kita stop") - 0.08, (1.03, 1.12, 0, -20),
          quote=("Ubat = <span class=\"mint\">pelindung</span>", T("pelindung", after=s) - LEAD))
    # "atau sampai tahap boleh masuk wad balik" — an empty, calm ward (no people)
    s = T("atau sampai")
    broll("b1-wad", "ward", s - 0.06, T("yang kedua") + 0.2, (1.10, 1.02, 0, 16),
          label=[("chip", "Paling teruk", T("sampai tahap", after=s) - LEAD),
                 ("name", "Masuk wad <span class=\"red\">balik</span>", T("masuk wad", after=s) - LEAD)])
    # "tapi ada ubat bila berhenti secara mengejut" — a generic, unbranded pill organiser
    s = T("tapi ada ubat")
    broll("b2-ubat", "pills", s + 0.25, T("boleh dapat simptom") - 0.1, (1.03, 1.11, -14, 0),
          label=[("chip", "Bila berhenti", T("berhenti", after=s) - LEAD),
                 ("name", "Secara <span class=\"red\">mengejut</span>", T("mengejut", after=s) - LEAD)])
    # "lambat sembuhnya, kena mula balik daripada bawah" — stairs from the bottom step
    s = T("lambat sembuhnya")
    broll("b3-tangga", "stairs", s - 0.08, T("kadang kadang") - 0.08, (1.12, 1.03, 0, -24),
          label=[("chip", "Lambat sembuh", s - LEAD + 0.1),
                 ("name", "Mula balik dari <span class=\"red\">bawah</span>", T("mula balik", after=s) - LEAD)])
    # plug, moved to the end: "Saya ada berita baik. Di klinik saya di Nilai…" — an empty consultation room
    s = T("saya ada berita baik")
    broll("b4-klinik", "clinic", s - 0.08, T("kami menyediakan") - 0.12, (1.03, 1.11, 16, -10),
          label=[("chip", "Berita baik!", T("berita", after=s) - LEAD),
                 ("name", "Klinik saya · <span class=\"teal\">Nilai</span>", T("klinik saya", after=s) - LEAD)])
    # CTA: "kalau anda tengah keliru, patut teruskan rawatan ataupun tidak" — a blank signpost at a fork
    s = T("kalau anda tengah keliru")
    broll("b5-keliru", "signpost", s - 0.08, T("atau rasa nak") - 0.1, (1.10, 1.02, 14, 0),
          label=[("chip", "Keliru?", T("keliru", after=s) - LEAD),
                 ("name", "Teruskan rawatan <span class=\"red\">atau tidak?</span>", T("teruskan", after=s) - LEAD)])

    # ---- motion graphics ---------------------------------------------------------
    # MG1 — the question: "Apa jadi kalau kita SKIP ubat psikiatri tanpa bincang dengan doktor?"
    s = T("apa jadi kalau")
    I.append({"id": "m1-skip", "kind": "mg", "start": fq(s - 0.15), "end": fq(T("yang pertama") - 0.06), "body": f"""
      <div class="head"><div class="mg-chip" id="m1-c">Apa jadi kalau…</div></div>
      <div class="skipwrap">
        <span class="bigdisc red" id="m1-d">{icon("skip", "big-ico")}</span>
        <div class="skipword" id="m1-w">SKIP</div>
        <div class="skipsub" id="m1-s">ubat psikiatri</div>
      </div>
      <div class="nochat" id="m1-n"><span class="disc red-bg">{icon("nochat")}</span><span>tanpa bincang dengan <b>doktor?</b></span></div>
      <div class="three" id="m1-3"><span class="n" id="m1-31">1</span><span class="n" id="m1-32">2</span><span class="n" id="m1-33">3</span>
        <span class="tl">kesan</span></div>""",
        "anims": [("#m1-c", s - 0.1, "pop"), ("#m1-d", T("skip", after=s) - LEAD, "pop"),
                  ("#m1-w", T("skip", after=s) - LEAD + 0.04, "slam"),
                  ("#m1-s", T("ubat psikiatri", after=s) - LEAD, "rise"),
                  ("#m1-n", T("tanpa", after=s) - LEAD, "slidein"),
                  ("#m1-3", T("dengan doktor", after=s) - 0.1, "fade"),
                  ("#m1-31", T("dengan doktor", after=s) - 0.06, "pop"), ("#m1-32", T("dengan doktor", after=s) + 0.08, "pop"),
                  ("#m1-33", T("dengan doktor", after=s) + 0.22, "pop")]})

    # MG2 — relapse, escalating: mood swing → cemas → (the ward still takes the third step)
    s = T("contohnya")
    I.append({"id": "m2-relapse", "kind": "mg", "start": fq(s - 0.15), "end": broll_start(I, "b1-wad"), "body": f"""
      <div class="head"><div class="mg-chip red" id="m2-c">Kesan #1 · Relapse</div>
        <div class="mg-title" id="m2-t">Contohnya…</div></div>
      <div class="stack" style="top:660px">
        <div class="crow" id="m2-r0"><span class="disc amber-bg" id="m2-d0">{icon("wave")}</span><span>Mood swing <span class="tealtx">balik</span></span></div>
        <div class="crow" id="m2-r1"><span class="disc red-bg" id="m2-d1">{icon("bolt")}</span><span>Cemas makin <span class="redtx">menjadi-jadi</span></span></div>
      </div>
      <div class="ladder" id="m2-l"><div class="ltrack"><div class="lfill" id="m2-f"></div></div>
        <div class="llab"><span>ringan</span><span>teruk</span></div></div>""",
        "anims": [("#m2-c", s - 0.1, "pop"), ("#m2-t", s - 0.02, "rise"), ("#m2-l", s + 0.3, "fade"),
                  ("#m2-r0", T("mud swing", after=s) - LEAD, "slidein"), ("#m2-d0", T("mud swing", after=s) - LEAD + 0.06, "pop"),
                  ("#m2-f", T("mud swing", after=s) - LEAD + 0.1, ("fillx", 0.34)),
                  ("#m2-r1", T("cemas", after=s) - LEAD, "slidein"), ("#m2-d1", T("cemas", after=s) - LEAD + 0.06, "pop"),
                  ("#m2-f", T("cemas", after=s) - LEAD + 0.1, ("fillx", 0.68))]})

    # MG3 — withdrawal symptoms: five rows with icons, one per spoken symptom
    s = T("boleh dapat simptom")
    rows = [("nausea", "Rasa loya", "loya"), ("spiral", "Pening kepala", "pening"),
            ("moonx", "Gangguan tidur", "gangguan"), ("storm", "Emosi huru-hara", "emosi"),
            ("tangle", "Otak jadi serabut", "otak jadi")]
    html = "".join(f'<div class="crow" id="m3-r{i}"><span class="disc" id="m3-d{i}">{icon(ic)}</span><span>{txt}</span></div>'
                   for i, (ic, txt, _) in enumerate(rows))
    I.append({"id": "m3-withdrawal", "kind": "mg", "start": fq(s - 0.12), "end": fq(T("serabut", end=True) + 0.45), "body": f"""
      <div class="head"><div class="mg-chip red" id="m3-c">Kesan #2 · Withdrawal</div>
        <div class="mg-title" id="m3-t">Simptom <span class="mint">penarikan</span></div></div>
      <div class="stack" style="top:610px">{html}</div>""",
        "anims": [("#m3-c", s - 0.1, "pop"), ("#m3-t", T("simptom", after=s) - LEAD, "rise")]
        + [a for i, (_, _, w) in enumerate(rows)
           for a in ((f"#m3-r{i}", T(w, after=s) - LEAD, "slidein"), (f"#m3-d{i}", T(w, after=s) - LEAD + 0.06, "pop"))]})

    # MG4 — stop / start / stop / start … = pressing reset
    s = T("setiap kali")
    flips = [("stop", T("stop", after=s)), ("start", T("start", after=s))]
    t2 = T("stop start stop start", after=flips[1][1])
    flips += [("stop", t2), ("start", T("start", after=t2)), ("stop", T("stop", after=t2 + 0.3)),
              ("start", T("start", after=T("stop", after=t2 + 0.3)))]
    words = "".join(f'<div class="flip {k}" id="m4-f{i}">{k.upper()}</div>' for i, (k, _) in enumerate(flips))
    I.append({"id": "m4-reset", "kind": "mg", "start": fq(s - 0.15), "end": fq(T("riset baten balik", end=True) + 0.08), "body": f"""
      <div class="head"><div class="mg-chip red" id="m4-c">Kesan #3 · Rawatan rosak</div>
        <div class="mg-title" id="m4-t">Setiap kali…</div></div>
      <div class="flipbox">{words}</div>
      <div class="count" id="m4-n"><span id="m4-n1">●</span><span id="m4-n2">●</span><span id="m4-n3">●</span></div>
      <div class="resetbtn" id="m4-b"><div class="rb-in" id="m4-bi">{icon("reset", "mg-ico xl")}<span>RESET</span></div></div>""",
        "anims": [("#m4-c", s - 0.1, "pop"), ("#m4-t", s - 0.02, "rise")]
        + [(f"#m4-f{i}", t - 0.06, "flip") for i, (_, t) in enumerate(flips)]
        + [(f"#m4-n{k + 1}", flips[2 * k + 1][1], "pop") for k in range(3)]
        + [("#m4-b", T("tekan", after=s) - LEAD, "pop"), ("#m4-bi", T("riset", after=s) - 0.04, "press")],
        "flips": [f"#m4-f{i}" for i in range(len(flips))]})

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
            parts = "".join(f'<div class="bl-{p}" id="{iid}-l{k}">{h}</div>' for k, (p, h, _) in enumerate(x["label"]))
            body = (f'<img src="broll/{x["img"]}.jpg" class="kb" id="{iid}-img"/>'
                    f'<div class="cap-shade"></div>'
                    + (f'<div class="blabel" id="{iid}-lb">{parts}</div>' if x["label"] else "")
                    + (f'<div class="quote" id="{iid}-q">{x["quote"][0]}</div>' if x["quote"] else "")
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
            if x["label"]:
                t0 = round(max(st + 0.12, min(t for _, _, t in x["label"]) - 0.05), 3)
                js.append(f"tl.fromTo('#{iid}-lb', {{opacity:0, y:-24}}, {{opacity:1, y:0, duration:0.36, ease:'power3.out'}}, {t0});")
                for k, (part, _, t) in enumerate(x["label"]):
                    t = round(max(t, st + 0.15), 3)
                    sel = f"#{iid}-l{k}"
                    if part == "chip":
                        js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.34, ease:'back.out(1.8)'}}, {t});")
                    else:
                        js.append(f"tl.fromTo('{sel}', {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.4, ease:'power3.out'}}, {t});")
                        sfx.append({"t": t, "kind": "label", "src": sel})
            if x["quote"]:
                tq = round(max(st + 0.15, x["quote"][1]), 3)
                js.append(f"tl.fromTo('#{iid}-q', {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.45, ease:'power3.out'}}, {tq});")
                sfx.append({"t": tq, "kind": "chime", "src": iid})
        else:
            js.append(f"tl.fromTo('{host}', {{clipPath:'inset(100% 0% 0% 0%)'}}, {{clipPath:'inset(0% 0% 0% 0%)', duration:0.42, ease:'power3.inOut'}}, {st});")
            flips = x.get("flips", [])
            for sel, t, kind in x["anims"]:
                t = round(max(t, st + 0.12), 3)
                if kind == "pop":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.34, ease:'back.out(1.8)'}}, {t});")
                    sfx.append({"t": t, "kind": "ting", "src": sel})
                elif kind == "rise":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.42, ease:'power3.out'}}, {t});")
                elif kind == "slam":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:1.8}}, {{opacity:1, scale:1, duration:0.3, ease:'power4.out'}}, {t});")
                    sfx.append({"t": t + 0.2, "kind": "thud", "src": sel})
                elif kind == "slidein":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0, x:80}}, {{opacity:1, x:0, duration:0.4, ease:'power3.out'}}, {t});")
                    sfx.append({"t": t, "kind": "swish", "src": sel})
                elif kind == "fade":
                    js.append(f"tl.fromTo('{sel}', {{opacity:0}}, {{opacity:1, duration:0.3, ease:'power2.out'}}, {t});")
                elif kind == "press":
                    js.append(f"tl.to('{sel}', {{scale:0.86, duration:0.09, ease:'power2.in'}}, {t});")
                    js.append(f"tl.to('{sel}', {{scale:1, duration:0.3, ease:'back.out(2.2)'}}, {round(t + 0.09, 3)});")
                    js.append(f"tl.fromTo('{sel} svg', {{rotation:0}}, {{rotation:-360, duration:0.7, ease:'power3.inOut'}}, {t});")
                    sfx.append({"t": t, "kind": "press", "src": sel})
                elif kind == "flip":
                    i = flips.index(sel)
                    if i:
                        js.append(f"tl.to('{flips[i - 1]}', {{opacity:0, y:-60, rotationX:70, duration:0.16, ease:'power2.in'}}, {t});")
                    js.append(f"tl.fromTo('{sel}', {{opacity:0, y:60, rotationX:-70}}, {{opacity:1, y:0, rotationX:0, duration:0.22, ease:'power3.out'}}, {t});")
                    sfx.append({"t": t, "kind": "flip", "src": sel})
                elif isinstance(kind, tuple) and kind[0] == "fillx":
                    js.append(f"tl.to('{sel}', {{scaleX:{kind[1]}, duration:0.5, ease:'power3.out'}}, {t});")
        nxt_adjacent = z + 1 < len(I) and abs(I[z + 1]["start"] - en) < 0.05
        js.append(f"tl.to('{host}', {{opacity:0, duration:0.24, ease:'power2.in'}}, {round(en - 0.24, 3)});")
        sfx.append({"t": en - 0.12, "kind": "whoosh_swap" if nxt_adjacent else "whoosh_out", "src": iid})
    return I, hosts, js, CSS, sfx


def broll_start(I, iid):
    return next(x["start"] for x in I if x["id"] == iid)


CSS = f"""
.ins {{ position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden; pointer-events:none; }}
.ins-in {{ position:absolute; inset:0; overflow:hidden; }}
.kb {{ position:absolute; left:0; top:0; width:1080px; height:1920px; object-fit:cover; transform-origin:50% 45%; }}
.cap-shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.30) 0%, rgba(0,0,0,0) 12%,
  rgba(0,0,0,0) 17%, rgba(0,0,0,.30) 21%, rgba(0,0,0,.30) 26%, rgba(0,0,0,0) 32%); }}
.ai-tag {{ position:absolute; left:48px; top:1440px; font:700 24px 'Plus Jakarta Sans'; letter-spacing:.08em; text-transform:uppercase;
  color:rgba(255,255,255,.92); background:rgba(0,0,0,.40); padding:7px 14px 6px; border-radius:10px; }}
.blabel {{ position:absolute; left:60px; top:560px; max-width:960px; background:{CREAM}; border-radius:34px; padding:26px 40px 30px;
  box-shadow:0 22px 60px rgba(8,22,30,.35); font-family:'Plus Jakarta Sans'; color:{INK}; overflow:hidden; }}
.blabel::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:12px; background:{TEAL}; }}
.bl-chip {{ display:inline-block; color:#fff; background:{TEAL}; font-weight:800; font-size:30px; letter-spacing:.07em; text-transform:uppercase;
  padding:9px 20px 8px; border-radius:999px; transform-origin:left center; }}
.bl-name {{ font-weight:800; font-size:76px; line-height:1.04; letter-spacing:-.02em; margin-top:14px; }}
.bl-name .red, .quote .red {{ color:{RED}; }}
.bl-name .teal {{ color:{TEAL}; }}
.quote {{ position:absolute; left:80px; right:80px; top:1060px; font:800 112px/1.0 'Plus Jakarta Sans'; letter-spacing:-.02em; color:{CREAM};
  text-shadow:0 6px 30px rgba(0,0,0,.55); }}
.quote .mint {{ color:{MINT}; }}
.mg {{ position:absolute; inset:0; background:radial-gradient(120% 80% at 80% 10%, {TEAL} 0%, {DEEP} 62%, #051E25 100%);
  font-family:'Plus Jakarta Sans', sans-serif; color:{CREAM}; }}
.mg .mint {{ color:{MINT}; }}
.head {{ position:absolute; left:80px; top:140px; width:920px; }}
.mg-chip {{ display:inline-block; font-weight:800; font-size:30px; letter-spacing:.08em; text-transform:uppercase;
  padding:10px 22px 9px; border-radius:999px; background:{MINT}; color:{DEEP}; transform-origin:left center; }}
.mg-chip.red {{ background:{RED}; color:#fff; }}
.mg-title {{ font-weight:800; font-size:66px; line-height:1.02; letter-spacing:-.02em; margin-top:18px; }}  /* ends ~y300: caption line is y~392 */
.stack {{ position:absolute; left:80px; width:920px; display:flex; flex-direction:column; gap:22px; }}
.crow {{ display:flex; align-items:center; gap:26px; height:118px; padding:0 30px; border-radius:26px; background:{CREAM};
  color:{INK}; font-weight:800; font-size:46px; box-shadow:0 14px 34px rgba(0,0,0,.28); }}
.tealtx {{ color:{TEAL}; }}
.redtx {{ color:{RED}; }}
.disc {{ width:78px; height:78px; border-radius:50%; background:{TEAL}; display:inline-flex; align-items:center; justify-content:center; flex:none; }}
.disc.red-bg {{ background:{RED}; }}
.disc.amber-bg {{ background:{AMBER}; }}
.mg-ico {{ width:50px; height:50px; }}
.mg-ico.xl {{ width:120px; height:120px; }}
/* MG1 */
.skipwrap {{ position:absolute; left:0; right:0; top:560px; display:flex; flex-direction:column; align-items:center; }}
.bigdisc {{ width:170px; height:170px; border-radius:50%; display:flex; align-items:center; justify-content:center; }}
.bigdisc.red {{ background:{RED}; }}
.big-ico {{ width:104px; height:104px; }}
.skipword {{ font-weight:800; font-size:250px; line-height:.9; letter-spacing:-.03em; color:{MINT}; margin-top:24px; }}
.skipsub {{ font-weight:800; font-size:64px; letter-spacing:.02em; text-transform:uppercase; color:{CREAM}; margin-top:6px; }}
.nochat {{ position:absolute; left:80px; right:80px; top:1150px; display:flex; align-items:center; gap:26px; padding:26px 32px;
  border-radius:28px; background:{CREAM}; color:{INK}; font-weight:700; font-size:46px; box-shadow:0 14px 34px rgba(0,0,0,.3); }}
.nochat b {{ color:{RED}; font-weight:800; }}
.three {{ position:absolute; left:0; right:0; top:1350px; display:flex; justify-content:center; align-items:center; gap:18px; }}
.three .n {{ width:70px; height:70px; border-radius:50%; background:{MINT}; color:{DEEP}; font-weight:800; font-size:38px;
  display:inline-flex; align-items:center; justify-content:center; }}
.three .tl {{ font-weight:800; font-size:44px; color:{CREAM}; margin-left:8px; text-transform:uppercase; letter-spacing:.06em; }}
/* MG2 ladder */
.ladder {{ position:absolute; left:80px; width:920px; top:1000px; }}
.ltrack {{ height:30px; border-radius:15px; background:rgba(255,248,238,.18); overflow:hidden; }}
.lfill {{ height:100%; width:100%; transform:scaleX(0); transform-origin:left center; border-radius:15px;
  background:linear-gradient(90deg, {AMBER}, {RED}); }}
.llab {{ display:flex; justify-content:space-between; margin-top:12px; font-weight:700; font-size:32px; color:rgba(255,248,238,.8);
  text-transform:uppercase; letter-spacing:.06em; }}
/* MG4 flips + reset */
.flipbox {{ position:absolute; left:0; right:0; top:560px; height:260px; perspective:900px; }}
.flip {{ position:absolute; left:0; right:0; text-align:center; font-weight:800; font-size:210px; line-height:260px; letter-spacing:-.02em; opacity:0; }}
.flip.stop {{ color:#FF8A8D; }}
.flip.start {{ color:{MINT}; }}
.count {{ position:absolute; left:0; right:0; top:860px; display:flex; justify-content:center; gap:22px; font-size:40px; color:{AMBER}; }}
.count span {{ opacity:0; }}
.resetbtn {{ position:absolute; left:340px; top:990px; width:400px; height:400px; border-radius:50%; background:{RED};
  box-shadow:0 18px 0 #8E1F24, 0 30px 60px rgba(0,0,0,.45); display:flex; align-items:center; justify-content:center; }}
.rb-in {{ display:flex; flex-direction:column; align-items:center; gap:10px; color:#fff; font-weight:800; font-size:56px; letter-spacing:.1em; }}
"""
