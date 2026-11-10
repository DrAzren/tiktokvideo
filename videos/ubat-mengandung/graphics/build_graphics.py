"""Motion graphics for '10 Ubat Psikiatri Dilarang Untuk Mengandung' (talking-head-recut style).

Same visual system as videos/ward-psikiatri (cream panel, teal #0E5E6F accent, Plus Jakarta Sans,
deep-teal full-screen inserts), re-laid out for this framing: the head sits high (hair ~y420,
chin ~y1280 of 1920), so cards live in a compact band in the headroom (y 140-376, under TikTok's
top tabs) and captions go on the chest band (y ~1330-1470) in the caption stage.

Every time is anchored to a phrase in edit/cut_words.json (T()), so the graphics re-time themselves
whenever the cut changes. Element motion lands on the spoken word (LEAD before it).

Inserts are full-screen, picture only (the voice keeps running; captions are composited on top later):
  broll: AI video clips (Higgsfield, broll/<id>.mp4) with an "Ilustrasi AI" tag; skipped if the file is missing
  mg:    full-screen motion graphics
Outputs: public/index.html, public/cards/*.html, storyboard.json
"""

import html
import json
from pathlib import Path

W = Path(__file__).parent
PUB = W / "public"
FPS = 30
DUR = json.loads((W / "metadata.json").read_text())["duration"]
WORDS = [w for w in json.loads((W.parent / "edit" / "cut_words.json").read_text()) if w["text"] not in ("*", "ha", "uh")]
LEAD = 0.12

TEAL, DEEP, MINT, CREAM, INK, RED, MUTED = "#0E5E6F", "#08323C", "#5EEAD4", "#FFF8EE", "#0B1F2A", "#E5484D", "#6B7C85"


def T(phrase: str, after: float = 0.0, end: bool = False) -> float:
    """Start (or end) of the first occurrence of `phrase` at/after `after` on the cut timeline."""
    toks = phrase.split()
    for i in range(len(WORDS) - len(toks) + 1):
        if WORDS[i]["start"] >= after - 1e-6 and [w["text"] for w in WORDS[i:i + len(toks)]] == toks:
            return WORDS[i + len(toks) - 1]["end"] if end else WORDS[i]["start"]
    raise KeyError(f"{phrase!r} after {after}")


def fq(t: float) -> float:
    return round(round(min(max(t, 0), DUR) * FPS) / FPS, 4)


# ---- icons: white strokes, viewBox 0 0 48 48 ------------------------------------------------------
ICON = {
    "brain": '<path d="M21 9a6 6 0 0 0-9 4 6 6 0 0 0-4 10 6 6 0 0 0 3 9 6 6 0 0 0 10 6z"/><path d="M27 9a6 6 0 0 1 9 4 6 6 0 0 1 4 10 6 6 0 0 1-3 9 6 6 0 0 1-10 6z"/>',
    "heart": '<path d="M24 40S7 30 7 18a8.5 8.5 0 0 1 17-3 8.5 8.5 0 0 1 17 3c0 12-17 22-17 22z"/><path d="M12 24h7l3-5 4 9 3-4h7"/>',
    "spine": '<rect x="16" y="5" width="16" height="7" rx="3.5"/><rect x="16" y="16" width="16" height="7" rx="3.5"/><rect x="16" y="27" width="16" height="7" rx="3.5"/><path d="M24 38v6"/>',
    "baby": '<circle cx="24" cy="15" r="8"/><path d="M21 14h.01M27 14h.01M21.5 18.5c1.5 1.3 3.5 1.3 5 0"/><path d="M11 42c0-8 6-13 13-13s13 5 13 13"/>',
    "moon": '<path d="M33 31A13 13 0 0 1 19 10a14 14 0 1 0 14 21z"/><path d="M31 8h7l-7 8h7"/>',
    "lip": '<path d="M5 24c5-7 10-9 14-6 2 1.5 3 1.5 5 0 4-3 9-1 14 6-5 8-11 11-19 11S10 32 5 24z"/><path d="M5 24h34"/><path d="M24 12v8" stroke-dasharray="2 3"/>',
    "scale": '<path d="M9 41h30l-4-23H13z"/><circle cx="24" cy="11" r="5"/><path d="M24 26v6"/>',
    "drop": '<path d="M24 6s-12 13-12 22a12 12 0 0 0 24 0C36 19 24 6 24 6z"/><path d="M18 29a6 6 0 0 0 6 6"/>',
    "eye": '<path d="M4 24s7-12 20-12 20 12 20 12-7 12-20 12S4 24 4 24z"/><circle cx="24" cy="24" r="5.5"/>',
    "steth": '<path d="M13 6v11a8 8 0 0 0 16 0V6"/><path d="M21 25v5a9 9 0 0 0 18 0v-4"/><circle cx="39" cy="23" r="3.5"/>',
    "chat": '<path d="M7 9h34v22H22l-9 8v-8H7z"/><path d="M15 18h18M15 24h11"/>',
    "pill": '<rect x="5" y="17" width="38" height="14" rx="7" transform="rotate(-38 24 24)"/><path d="M19.5 14.5l9 19"/>',
    "bump": '<circle cx="22" cy="8" r="4.5"/><path d="M19 15c-3 5-3 10 0 14l-2 14M24 15c2 2 3 5 2 7 7 1 10 6 8 11-2 4-7 5-10 3l1 7"/>',
    "cal": '<rect x="7" y="10" width="34" height="31" rx="5"/><path d="M7 19h34M16 6v8M32 6v8M17 29l5 5 9-9"/>',
    "alert": '<path d="M24 6L4 41h40z"/><path d="M24 18v11M24 35v.01"/>',
    "wave": '<path d="M5 24c4-12 9-12 13 0s9 12 13 0 9-12 12-4"/>',
}


def icon(name: str, cls: str = "ico") -> str:
    return (f'<svg viewBox="0 0 48 48" class="{cls}"><g stroke="#fff" stroke-width="3.4" stroke-linecap="round" '
            f'stroke-linejoin="round" fill="none">{ICON[name]}</g></svg>')


def disc(name: str, color: str = TEAL, cls: str = "disc") -> str:
    tone = " on-mint" if color == MINT else ""   # dark strokes on the light mint disc
    return f'<span class="{cls}{tone}" style="background:{color}">{icon(name)}</span>'


def chip(text: str, color: str = TEAL) -> str:
    return f'<span class="chip" style="background:{color}">{text}</span>'


# =====================================================================================================
# HEADROOM CARDS
# card: {id, start, end, badge (number str or icon name), pages: [(t_in, [(key, html, t, anim)])]}
# =====================================================================================================
def drug(n, name_phrase, name, brand, use_phrase, use, risk_phrase, risks, extra=None, until=None):
    """A drug card: page 0 = number + name (+brand) + use, page 1 = RISIKO rows, optional page 2."""
    s = T(f"yang {['', 'pertama', 'kedua', 'ketiga', 'keempat', 'kelima', 'keenam', 'ketujuh', 'kelapan', 'kesembilan', 'kesepuluh'][n]}")
    tn = T(name_phrase, after=s)
    p0 = [("name", f'<div class="dname">{name}</div>', tn - LEAD, "slide")]
    if brand:
        p0.append(("brand", f'<span class="brand">{brand[1]}</span>', T(brand[0], after=s) - LEAD, "pop"))
    p0.append(("use", f'<div class="use"><span class="ulab">Untuk</span>{use}</div>', T(use_phrase, after=s) - LEAD, "fade"))
    tr = T(risk_phrase, after=s)
    p1 = [("rk", chip("Risiko kepada bayi", RED), tr - 0.2, "pop")]
    for i, (ph, ic, txt) in enumerate(risks):
        p1.append((f"r{i}", f'<div class="rrow">{disc(ic, RED, "rdisc")}<span>{txt}</span></div>', T(ph, after=tr) - LEAD, "slide"))
    pages = [(s, p0), (tr - 0.25, p1)]
    if extra:
        te = T(extra[0], after=tr)
        pages.append((te - 0.3, [("ok", chip("Boleh guna, tapi…"), te - 0.25, "pop"),
                                 ("x", f'<div class="rrow">{disc("eye")}<span>{extra[1]}</span></div>', te - LEAD, "slide")]))
    return {"id": f"d{n:02d}", "start": s - 0.05, "end": until, "badge": str(n), "pages": pages,
            "intent": f"#{n} {name}"}


def build_cards():
    C = []
    s = T("assalamualaikum")
    C.append({"id": "c-intro", "start": s, "end": T("kalau anda tengah") - 0.05, "badge": "steth", "intent": "Name tag",
              "pages": [(s, [("t", '<div class="dname">Dr Azren</div>', T("azren") - LEAD, "slide"),
                             ("u", '<div class="use big">Doktor Psikiatri</div>', T("psikiatri", after=s) - LEAD, "fade")])]})
    D = [
        drug(1, "sodium valproate", "Sodium Valproate", ("epilim", "Epilim"), "sawan ataupun", "Sawan · Bipolar",
             "risiko tinggi", [("kecacatan otak", "brain", "Kecacatan otak &amp; sistem saraf")]),
        drug(2, "litium", "Litium", None, "bipolar juga", "Bipolar",
             "risiko untuk masalah", [("jantung bayi", "heart", "Masalah jantung bayi")],
             extra=("kena monitor", "Perlu pemantauan rapi doktor")),
        drug(3, "carbamazepine", "Carbamazepine", None, "bipolar dan kadang", "Bipolar · Sawan",
             "risiko neural", [("neural tube", "spine", "Neural tube defect<br/><small>kecacatan saraf tunjang</small>")]),
        drug(4, "paroxetine", "Paroxetine", ("antidepressant", "Antidepresan"), "depression", "Depresi · Anxiety",
             "dikaitkan dengan", [("kecacatan jantung", "heart", "Kecacatan jantung bayi")]),
        drug(5, "alprazolam", "Alprazolam", ("xanax", "Xanax"), "anxiety ataupun panic", "Anxiety · Panic attack",
             "risiko bayi", [("bayi boleh jadi lemah", "baby", "Bayi lemah")]),
        drug(6, "diazepam", "Diazepam", ("valium", "Valium"), "anxiety muscle", "Anxiety · Otot · Sawan",
             "risiko baby floppy", [("baby floppy", "baby", "Floppy baby syndrome<br/><small>bayi lembik, otot lemah</small>")]),
        drug(7, "clonazepam", "Clonazepam", None, "anxiety ataupun sawan", "Anxiety · Sawan",
             "risiko sedation", [("sedation", "moon", "Sedasi pada bayi<br/><small>bayi terlalu mengantuk</small>")]),
        drug(8, "topiramate", "Topiramate", None, "topiramate ni", "Sawan · Migrain",
             "risiko cleft", [("cleft lip", "lip", "Bibir &amp; lelangit sumbing")]),
        drug(9, "risperidone", "Risperidone", None, "skizofrenia bipolar", "Skizofrenia · Bipolar · Agresif",
             "risiko hormonal", [("hormonal", "drop", "Kesan hormon &amp; metabolik")],
             extra=("kena ada pemantauan", "Perlu pemantauan rapi doktor")),
        drug(10, "olanzapine", "Olanzapine", None, "skizofrenia dan", "Skizofrenia · Bipolar",
             "risiko berat", [("berat bayi", "scale", "Berat bayi jadi besar"), ("metabolik side", "drop", "Masalah metabolik")]),
    ]
    for a, b in zip(D, D[1:]):
        a["end"] = b["start"] - 0.02
    D[-1]["end"] = T("jadi ubat yang saya") - 0.05
    C += D
    s = T("ataupun tengah pregnant")
    C.append({"id": "c-hamil", "start": s - 0.1, "end": T("kena bagitahu") - 0.05, "badge": "bump", "intent": "Pregnant or planning",
              "pages": [(s - 0.1, [("t", '<div class="dname sm">Sedang hamil<br/>atau plan hamil?</div>', s - LEAD, "slide")])]})
    s = T("apa apa soalan")
    C.append({"id": "c-end", "start": s - 0.08, "end": DUR, "badge": "chat", "intent": "CTA: ask in the comments",
              "pages": [(s - 0.08, [("k", chip("Ada soalan?"), s - LEAD, "pop"),
                                    ("t", '<div class="dname">Tanya di komen</div>', T("tanya di") - LEAD, "slide")])]})
    for c in C:
        c["start"], c["end"] = fq(c["start"]), fq(c["end"])
    return C


# =====================================================================================================
# FULL-SCREEN INSERTS
# =====================================================================================================
BROLL_DIR = PUB / "broll"


def build_inserts():
    I = []

    def broll(iid, start, end, label=None):
        if not (BROLL_DIR / f"{iid}.mp4").exists():
            print(f"  (skipping {iid}: public/broll/{iid}.mp4 not there yet)")
            return
        I.append({"id": iid, "kind": "broll", "start": fq(start), "end": fq(end), "label": label})

    # ---- motion graphics ----
    s = T("berhati hati")
    I.append({"id": "m0-hook", "kind": "mg", "start": fq(s - 0.15), "end": fq(T("assalamualaikum") - 0.04), "body": f"""
      <div class="head"><div class="mg-chip red" id="m0-c">{icon("alert", "chip-ico")} Amaran</div>
        <div class="mg-title" id="m0-t">10 Ubat Psikiatri</div></div>
      <div class="hookline" id="m0-a" style="top:560px">Perlu <span class="mint big">berhati-hati</span></div>
      <div class="hookline" id="m0-b" style="top:720px">atau <span class="hl big">elakkan</span></div>
      <div class="hookline sm" id="m0-w" style="top:900px">ketika anda…</div>
      <div class="pills" style="top:1010px">
        <div class="pill2" id="m0-p1">{disc("bump", MINT, "pdisc")}<span>Sedang hamil</span></div>
        <div class="pill2" id="m0-p2">{disc("cal", MINT, "pdisc")}<span>Plan hamil</span></div></div>""",
        "anims": [("#m0-c", s - 0.12, "pop"), ("#m0-t", s - 0.08, "rise"), ("#m0-a", s - LEAD, "rise"),
                  ("#m0-b", T("elakkanlah") - LEAD, "rise"),
                  ("#m0-w", T("ketika anda") - LEAD, "fade"),
                  ("#m0-p1", T("pregnant", after=s) - LEAD, "slidein"),
                  ("#m0-p2", T("plan nak pregnant") - LEAD, "slidein")]})

    s = T("jadi ubat yang saya")
    names = ["Sodium Valproate", "Litium", "Carbamazepine", "Paroxetine", "Alprazolam",
             "Diazepam", "Clonazepam", "Topiramate", "Risperidone", "Olanzapine"]
    tiles = "".join(f'<div class="tile" id="m1-g{i}" style="left:{80 + (i % 2) * 470}px; top:{410 + (i // 2) * 146}px">'
                    f'<span class="tnum">{i + 1}</span><span>{n}</span></div>' for i, n in enumerate(names))
    I.append({"id": "m1-recap", "kind": "mg", "start": fq(s - 0.1), "end": None, "body": f"""
      <div class="head"><div class="mg-chip" id="m1-c">Ringkasan</div>
        <div class="mg-title sm" id="m1-t">10 ubat yang perlu berhati-hati</div></div>
      {tiles}
      <div class="bigx" id="m1-x" style="top:1135px"><div class="stamp-lg one">BUKAN 100% DILARANG</div></div>""",
        "anims": [("#m1-c", s - 0.08, "pop"), ("#m1-t", s - 0.04, "rise")]
        + [(f"#m1-g{i}", s + 0.1 + i * 0.11, "tile") for i in range(10)]
        + [("#m1-x", T("seratus peratus") - LEAD, "stamp")]})

    s = T("kena bagitahu doktor")
    I.append({"id": "m2-doktor", "kind": "mg", "start": fq(s - 0.12), "end": fq(T("dilakukanlah", end=True) + 0.25), "body": f"""
      <div class="head"><div class="mg-chip" id="m2-c">Penting</div></div>
      <div class="bigdisc" id="m2-d">{icon("steth", "big-ico")}</div>
      <div class="mg-title center" id="m2-t" style="top:820px">Beritahu<br/><span class="mint">doktor anda</span></div>
      <svg class="arrow" id="m2-a" viewBox="0 0 48 90" style="top:1090px"><path d="M24 4v76M8 64l16 18 16-18" stroke="{MINT}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
      <div class="pill2 center" id="m2-p" style="top:1210px">{disc("eye", TEAL, "pdisc")}<span>Pemantauan rapi</span></div>""",
        "anims": [("#m2-c", s - 0.1, "pop"), ("#m2-d", s - 0.08, "pop"), ("#m2-t", T("bagitahu") - LEAD, "rise"),
                  ("#m2-a", T("supaya") - LEAD, "fade"), ("#m2-p", T("pemantauan rapi", after=s) - LEAD, "rise")]})

    # ---- AI B-roll (Higgsfield video, 4 s clips) ----
    broll("b1-hamil", T("kalau anda tengah") - 0.08, T("kalau anda tengah") + 3.95)
    broll("b2-ultrasound", T("kalau nak bagi") - 0.08, T("ubat yang pertama") - 0.06)
    tb = T("bayi boleh jadi lemah")
    broll("b3-bayi", tb - 0.1, tb + 3.9, label=("Risiko", "Bayi lemah · withdrawal selepas lahir"))
    tk = T("kalau anda ada ambik")
    broll("b4-konsultasi", tk - 0.1, tk + 3.9)

    I.sort(key=lambda x: x["start"])
    rec = next(x for x in I if x["id"] == "m1-recap")
    nxt = [x for x in I if x["start"] > rec["start"]]
    rec["end"] = fq(nxt[0]["start"] + 0.3) if nxt and nxt[0]["start"] < T("tapi kalau anda") + 0.6 else fq(T("tapi kalau anda") + 0.05)
    for a, b in zip(I, I[1:]):
        assert b["start"] >= a["end"] - 0.5, f"{a['id']} / {b['id']} overlap by more than a crossfade"
    for x in I:
        assert x["end"] - x["start"] >= 1.8, (x["id"], x["end"] - x["start"])
        assert x["start"] >= 2.0, f"{x['id']} would cover the '10 UBAT' hero behind the head (0-2.2s)"
    return I


def insert_html_js(I):
    hosts, js = [], []
    for z, x in enumerate(I):
        iid, st, en = x["id"], x["start"], x["end"]
        host = f"#{iid}-in"   # animate the inner wrapper: the framework owns clip visibility
        if x["kind"] == "broll":
            label = ""
            if x["label"]:
                label = (f'<div class="blabel" id="{iid}-lab"><span class="mg-chip red">{x["label"][0]}</span>'
                         f'<div class="bl-t">{x["label"][1]}</div></div>')
            # timing lives on the <video> (never on an ancestor too: lint video_nested_in_timed_element)
            hosts.append(f'<div id="ins-{iid}" class="ins" style="z-index:{20 + z}"><div class="ins-in" id="{iid}-in" style="opacity:0">'
                         f'<video id="{iid}-v" class="clip kbv" src="broll/{iid}.mp4" muted playsinline data-start="{st}" '
                         f'data-duration="{round(en - st, 4)}" data-track-index="{5 + z % 2}"></video>'
                         f'<div class="cap-shade"></div>{label}<div class="ai-tag">Ilustrasi AI</div></div></div>')
            js.append(f"// insert {iid} (broll) {st:.2f}-{en:.2f}s")
            js.append(f"tl.fromTo('{host}', {{opacity:0}}, {{opacity:1, duration:0.22, ease:'power2.out'}}, {st});")
            js.append(f"tl.fromTo('#{iid}-v', {{scale:1.06}}, {{scale:1.0, duration:{round(en - st, 3)}, ease:'sine.out'}}, {st});")
            if label:
                js.append(f"tl.fromTo('#{iid}-lab', {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:0.4, ease:'power3.out'}}, {round(st + 0.35, 3)});")
            js.append(f"tl.to('{host}', {{opacity:0, duration:0.2, ease:'power2.in'}}, {round(en - 0.2, 3)});")
            continue
        hosts.append(f'<div id="ins-{iid}" class="ins clip" data-start="{st}" data-duration="{round(en - st, 4)}" '
                     f'data-track-index="{5 + z % 2}" style="z-index:{20 + z}"><div class="ins-in" id="{iid}-in"><div class="mg">{x["body"]}</div></div></div>')
        js.append(f"// insert {iid} (mg) {st:.2f}-{en:.2f}s")
        js.append(f"tl.fromTo('{host}', {{clipPath:'inset(100% 0% 0% 0%)'}}, {{clipPath:'inset(0% 0% 0% 0%)', duration:0.42, ease:'power3.inOut'}}, {st});")
        for sel, t, kind in x["anims"]:
            t = round(max(t, st + 0.12), 3)
            if kind == "pop":
                js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.34, ease:'back.out(1.8)'}}, {t});")
            elif kind == "rise":
                js.append(f"tl.fromTo('{sel}', {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.42, ease:'power3.out'}}, {t});")
            elif kind == "slidein":
                js.append(f"tl.fromTo('{sel}', {{opacity:0, x:90}}, {{opacity:1, x:0, duration:0.4, ease:'power3.out'}}, {t});")
            elif kind == "fade":
                js.append(f"tl.fromTo('{sel}', {{opacity:0}}, {{opacity:1, duration:0.3, ease:'power2.out'}}, {t});")
            elif kind == "tile":
                js.append(f"tl.fromTo('{sel}', {{opacity:0, y:30, scale:0.92}}, {{opacity:1, y:0, scale:1, duration:0.32, ease:'power3.out'}}, {t});")
            elif kind == "stamp":
                js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:1.9}}, {{opacity:1, scale:1, duration:0.26, ease:'power4.out'}}, {t});")
        js.append(f"tl.to('{host}', {{opacity:0, duration:0.22, ease:'power2.in'}}, {round(en - 0.22, 3)});")
    return hosts, js


# =====================================================================================================
# CARD RENDERING
# =====================================================================================================
PANEL = {"left": 60, "top": 140, "w": 960, "h": 236}


def card_fragment(card) -> str:
    cid = card["id"]
    b = card["badge"]
    badge = (f'<div class="badge"><span class="bn">{b}</span><span class="bd">/10</span></div>' if b.isdigit()
             else f'<div class="badge icon">{icon(b, "badge-ico")}</div>')
    pages = []
    for p, (t_in, els) in enumerate(card["pages"]):
        inner = "".join(f'<div id="{cid}-{key}" class="el">{frag}</div>' for key, frag, t, anim in els)
        pages.append(f'<div class="page" id="{cid}-page{p}">{inner}</div>')
    return (f'<div class="card" data-card-id="{cid}"><div class="panel" id="{cid}-panel">{badge}'
            f'<div class="col">{"".join(pages)}</div></div></div>')


def card_end(card, inserts) -> float:
    """A card whose end falls during a full-screen insert leaves just after the insert covers it."""
    e = card["end"]
    for x in inserts:
        if x["start"] + 0.3 < e <= x["end"] + 0.5:
            return round(x["start"] + 0.3, 4)
    return e


def timeline_js(card, inserts) -> list[str]:
    cid, s = card["id"], card["start"]
    E = card_end(card, inserts)
    host = f'.card-host[data-card-id="{cid}"]'
    panel = f"#{cid}-panel"
    js = [f"// {cid}: {card['intent']}  {s:.2f}-{E:.2f}",
          f"tl.fromTo('{panel}', {{opacity:0, y:-30, scale:0.97}}, {{opacity:1, y:0, scale:1, duration:0.42, ease:'power3.out'}}, {s});",
          f"tl.fromTo('{panel} .badge', {{scale:0.4, rotate:-12}}, {{scale:1, rotate:0, duration:0.45, ease:'back.out(2)'}}, {round(s + 0.05, 3)});"]
    pages = card["pages"]
    for p, (t_in, els) in enumerate(pages):
        pg = f"#{cid}-page{p}"
        t_in = fq(max(t_in, s))
        if p == 0:
            js.append(f"tl.set('{pg}', {{opacity:1}}, {s});")
        else:
            prev = f"#{cid}-page{p - 1}"
            js.append(f"tl.to('{prev}', {{opacity:0, y:-16, duration:0.26, ease:'power2.in'}}, {round(t_in - 0.26, 3)});")
            js.append(f"tl.fromTo('{pg}', {{opacity:0, y:16}}, {{opacity:1, y:0, duration:0.3, ease:'power3.out'}}, {t_in});")
        for key, frag, t, anim in els:
            sel = f"#{cid}-{key}"
            T_ = fq(max(t, t_in + 0.04, s + 0.05))
            if anim == "pop":
                js.append(f"tl.fromTo('{sel}', {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.34, ease:'back.out(1.8)'}}, {T_});")
            elif anim == "slide":
                js.append(f"tl.fromTo('{sel}', {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:0.38, ease:'power3.out'}}, {T_});")
            elif anim == "fade":
                js.append(f"tl.fromTo('{sel}', {{opacity:0}}, {{opacity:1, duration:0.3, ease:'power2.out'}}, {T_});")
    if E < DUR:
        js.append(f"tl.to('{panel}', {{opacity:0, y:-20, duration:0.28, ease:'power2.in'}}, {round(E - 0.28, 4)});")
    return js


CSS = f"""
.card-host {{ position:absolute; left:0; top:0; width:1080px; height:1920px; pointer-events:none; overflow:hidden; }}
.card {{ position:relative; width:100%; height:100%; }}
.panel {{ position:absolute; left:{PANEL['left']}px; top:{PANEL['top']}px; width:{PANEL['w']}px; height:{PANEL['h']}px; display:flex; gap:28px;
  align-items:center; background:{CREAM}; border-radius:32px; padding:22px 32px 22px 22px; opacity:0;
  box-shadow:0 22px 60px rgba(8,22,30,.32), 0 2px 0 rgba(255,255,255,.6) inset; font-family:'Plus Jakarta Sans', sans-serif; color:{INK}; }}
.badge {{ width:178px; height:178px; flex:none; border-radius:28px; background:{TEAL}; color:#fff; display:flex; align-items:baseline;
  justify-content:center; padding-top:30px; }}
.badge.icon {{ align-items:center; padding:0; }}
.bn {{ font-weight:800; font-size:112px; line-height:1; letter-spacing:-.04em; }}
.bd {{ font-weight:700; font-size:34px; opacity:.75; margin-left:4px; }}
.badge-ico {{ width:104px; height:104px; }}
.col {{ flex:1; display:grid; align-self:stretch; align-items:center; }}
.page {{ grid-area:1/1; opacity:0; }}
.page .el + .el {{ margin-top:12px; }}
.page .el:has(.brand) {{ display:inline-block; margin:0 0 0 14px; vertical-align:middle; }}
.dname {{ display:inline-block; vertical-align:middle; font-weight:800; font-size:60px; line-height:1.04; letter-spacing:-.02em; }}
.dname.sm {{ font-size:50px; }}
.brand {{ display:inline-block; font-weight:800; font-size:30px; color:{TEAL}; background:#E3F4F1; border:2px solid rgba(14,94,111,.25);
  border-radius:14px; padding:6px 14px 5px; }}
.use {{ font-weight:700; font-size:36px; color:#33444C; display:flex; align-items:center; gap:14px; }}
.use.big {{ font-size:42px; color:{TEAL}; }}
.ulab {{ font-weight:800; font-size:24px; letter-spacing:.08em; text-transform:uppercase; color:#fff; background:{MUTED};
  border-radius:10px; padding:5px 10px 4px; }}
.chip {{ display:inline-block; color:#fff; font-weight:800; font-size:26px; letter-spacing:.07em; text-transform:uppercase;
  padding:8px 18px 7px; border-radius:999px; }}
.rrow {{ display:flex; align-items:center; gap:18px; font-weight:800; font-size:42px; line-height:1.08; }}
.rrow small {{ display:block; font-weight:700; font-size:28px; color:#5B6A72; margin-top:4px; }}
.rdisc, .disc {{ width:64px; height:64px; flex:none; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; }}
.ico {{ width:40px; height:40px; }}
.ins {{ position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden; pointer-events:none; }}
.ins-in {{ position:absolute; inset:0; overflow:hidden; }}
.kbv {{ position:absolute; left:0; top:0; width:1080px; height:1920px; object-fit:cover; transform-origin:50% 45%; }}
.cap-shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.28) 0%, rgba(0,0,0,0) 16%,
  rgba(0,0,0,0) 62%, rgba(0,0,0,.32) 70%, rgba(0,0,0,.32) 78%, rgba(0,0,0,0) 86%); }}
.ai-tag {{ position:absolute; left:48px; top:150px; font:700 24px 'Plus Jakarta Sans'; letter-spacing:.08em; text-transform:uppercase;
  color:rgba(255,255,255,.92); background:rgba(0,0,0,.40); padding:7px 14px 6px; border-radius:10px; }}
.blabel {{ position:absolute; left:60px; top:210px; width:960px; background:{CREAM}; border-radius:28px; padding:24px 30px;
  box-shadow:0 20px 50px rgba(0,0,0,.35); font-family:'Plus Jakarta Sans'; color:{INK}; }}
.bl-t {{ font-weight:800; font-size:48px; line-height:1.1; margin-top:12px; }}
.mg {{ position:absolute; inset:0; background:radial-gradient(120% 80% at 80% 10%, {TEAL} 0%, {DEEP} 62%, #051E25 100%);
  font-family:'Plus Jakarta Sans', sans-serif; color:{CREAM}; }}
.mg .mint {{ color:{MINT}; }}
.head {{ position:absolute; left:80px; top:200px; width:920px; }}
.mg-chip {{ display:inline-flex; align-items:center; gap:10px; font-weight:800; font-size:30px; letter-spacing:.08em; text-transform:uppercase;
  padding:10px 22px 9px; border-radius:999px; background:{MINT}; color:{DEEP}; }}
.mg-chip.red {{ background:{RED}; color:#fff; }}
.chip-ico {{ width:34px; height:34px; }}
.mg-title {{ font-weight:800; font-size:92px; line-height:1.02; letter-spacing:-.025em; margin-top:22px; }}
.mg-title.sm {{ font-size:64px; }}
.mg-title.center {{ position:absolute; left:0; right:0; text-align:center; margin:0; font-size:104px; }}
.hookline {{ position:absolute; left:80px; font-weight:800; font-size:64px; color:rgba(255,248,238,.88); }}
.hookline.sm {{ font-size:46px; color:rgba(255,248,238,.7); }}
.hookline .big {{ font-size:112px; letter-spacing:-.03em; }}
.hl {{ color:#fff; background:linear-gradient({RED},{RED}) left 88%/100% 18px no-repeat; padding:0 6px; }}
.pills {{ position:absolute; left:80px; width:920px; display:flex; flex-direction:column; gap:22px; }}
.pill2 {{ display:flex; align-items:center; gap:24px; height:116px; padding:0 34px 0 22px; border-radius:60px; background:{CREAM};
  color:{INK}; font-weight:800; font-size:50px; box-shadow:0 14px 34px rgba(0,0,0,.3); width:max-content; }}
.pill2.center {{ position:absolute; left:50%; transform:translateX(-50%); }}
.pdisc {{ width:76px; height:76px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; flex:none; }}
.pdisc .ico {{ width:48px; height:48px; }}
.on-mint .ico g {{ stroke:{DEEP}; }}
.tile {{ position:absolute; width:450px; height:128px; display:flex; align-items:center; gap:20px; padding:0 24px; border-radius:24px;
  background:{CREAM}; color:{INK}; font-weight:800; font-size:38px; box-shadow:0 12px 30px rgba(0,0,0,.28); }}
.tnum {{ width:64px; height:64px; flex:none; border-radius:50%; background:{TEAL}; color:#fff; font-size:34px; display:inline-flex;
  align-items:center; justify-content:center; }}
.bigx {{ position:absolute; left:0; right:0; text-align:center; }}
.stamp-lg {{ display:inline-block; transform:rotate(-7deg); border:9px solid {RED}; color:{RED}; border-radius:20px; font-weight:800;
  font-size:84px; letter-spacing:.03em; padding:10px 30px 4px; background:rgba(255,248,238,.95); box-shadow:0 20px 60px rgba(0,0,0,.45); }}
.stamp-lg.one {{ font-size:66px; white-space:nowrap; padding:8px 26px 2px; }}
.bigdisc {{ position:absolute; left:50%; top:440px; width:300px; height:300px; margin-left:-150px; border-radius:50%; background:{TEAL};
  display:flex; align-items:center; justify-content:center; box-shadow:0 0 0 22px rgba(94,234,212,.18); }}
.big-ico {{ width:170px; height:170px; }}
.arrow {{ position:absolute; left:50%; width:48px; height:90px; margin-left:-24px; }}
"""


def main() -> None:
    (PUB / "cards").mkdir(parents=True, exist_ok=True)
    cards = build_cards()
    inserts = build_inserts()
    ins_hosts, ins_js = insert_html_js(inserts)

    hosts, js = [], []
    for c in cards:
        frag = card_fragment(c)
        (PUB / "cards" / f"{c['id']}.html").write_text(frag)
        E = card_end(c, inserts)
        hosts.append(f'<div id="card-{c["id"]}" class="card-host clip" data-card-id="{c["id"]}" data-start="{c["start"]}" '
                     f'data-duration="{round(E - c["start"], 4)}" data-track-index="2">{frag}</div>')
        js += timeline_js(c, inserts)

    storyboard = {
        "schemaVersion": 3,
        "composition": {"fps": FPS, "width": 1080, "height": 1920, "durationSeconds": DUR, "layout": "portrait"},
        "cards": [{"id": c["id"], "intent": c["intent"], "startSec": c["start"], "endSec": card_end(c, inserts)} for c in cards],
        "inserts": [{"id": x["id"], "kind": x["kind"], "startSec": x["start"], "endSec": x["end"]} for x in inserts],
    }
    (W / "storyboard.json").write_text(json.dumps(storyboard, indent=2, ensure_ascii=False))

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
html, body {{ margin:0; padding:0; width:100%; height:100%; overflow:hidden; background:#000; font-family:"Plus Jakarta Sans", sans-serif; }}
#stage {{ position:relative; width:1080px; height:1920px; overflow:hidden; background:#000; }}
.video-wrapper {{ position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden; }}
.video-wrapper video {{ width:100%; height:100%; object-fit:cover; }}
{CSS}
</style>
</head>
<body>
<div id="stage" data-composition-id="talking-head-recut" data-start="0" data-duration="{DUR}" data-fps="{FPS}" data-width="1080" data-height="1920">
  <div class="video-wrapper" id="video-wrap">
    <video id="bg-video" class="clip" src="input-video.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="1"></video>
  </div>
  <audio id="source-audio" src="input-video.mp4" data-start="0" data-duration="{DUR}" data-track-index="10" data-volume="1"></audio>
  {(chr(10) + '  ').join(hosts)}
  {(chr(10) + '  ').join(ins_hosts)}
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
    print(f"{len(cards)} cards, {len(inserts)} inserts ({sum(x['kind'] == 'broll' for x in inserts)} b-roll), "
          f"{len(js) + len(ins_js)} timeline statements")
    for x in inserts:
        print(f"  {x['id']:16} {x['start']:7.2f}-{x['end']:7.2f}")


if __name__ == "__main__":
    main()
