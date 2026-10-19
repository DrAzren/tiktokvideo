"""Episode 1 'Sejarah Penyakit Mental' — 120 s, 16:9, 24 fps HyperFrames composition.

Layers (bottom → top): shots (Kling B-roll / stills / full-frame motion graphics) → grade (vignette, grain)
→ era timeline + kinetic text + lower thirds → disclosure tags → subtitles.
Shot list and VO offsets: timeline.json. Word times: vo_words.json (MMS_FA forced alignment of the script).
Run: ../../../.venv/bin/python build_doc.py   →  public/index.html
"""

import html
import json
import re
from pathlib import Path

D = Path(__file__).parent
P = D / "public"
TL = json.loads((D / "timeline.json").read_text())
VW = json.loads((D / "vo_words.json").read_text())
FPS, W, H, DUR = TL["fps"], 1920, 1080, TL["duration"]

INK, NAVY, TEAL, TEAL_L, GOLD, CREAM, PARCH, SEPIA = ("#0B1418", "#0A1A2F", "#0E4F55", "#5CC8BE",
                                                      "#D9A441", "#F4EBD8", "#E9DCC0", "#3B2A1A")


def fq(t: float) -> float:
    return round(round(t * FPS) / FPS, 4)


def word_times():
    """Global word list per scene with display text."""
    out = {}
    for sid, ws in VW.items():
        off = TL["vo"][sid]
        out[sid] = [{"text": w["text"], "start": round(w["start"] + off, 3), "end": round(w["end"] + off, 3)} for w in ws]
    return out


WT = word_times()


def T(sid: str, phrase: str, end=False) -> float:
    toks = phrase.split()
    ws = WT[sid]
    norm = lambda s: re.sub(r"[^\w]", "", s.lower())
    for i in range(len(ws) - len(toks) + 1):
        if [norm(w["text"]) for w in ws[i:i + len(toks)]] == [norm(t) for t in toks]:
            return ws[i + len(toks) - 1]["end"] if end else ws[i]["start"]
    raise KeyError(phrase)


js: list[str] = []
body: list[str] = []


def A(sel, t, frm, to, dur, ease="power3.out", ir=True):
    extra = "" if ir else ", immediateRender:false"
    js.append(f"tl.fromTo('{sel}', {json.dumps(frm)}, {{...{json.dumps(to)}, duration:{round(dur, 3)}, ease:'{ease}'{extra}}}, {fq(t)});")


def TO(sel, t, to, dur, ease="power2.in"):
    js.append(f"tl.to('{sel}', {{...{json.dumps(to)}, duration:{round(dur, 3)}, ease:'{ease}'}}, {fq(t)});")


def SET(sel, t, props):
    js.append(f"tl.set('{sel}', {json.dumps(props)}, {fq(t)});")


# ------------------------------------------------------------------ graphics bodies
NODES = [("ZAMAN PURBA", 0), ("± 400 SM", 1), ("AKHIR ABAD KE-18", 2), ("1952", 3), ("HARI INI", 4)]


def timeline_svg(prefix: str, x0: int, x1: int, y: int, big=False):
    """Era timeline: rail + 5 nodes. Returns (html, node_x list)."""
    xs = [round(x0 + (x1 - x0) * i / 4) for i in range(5)]
    r = 13 if big else 8
    fs = 30 if big else 20
    parts = [f'<div class="tlrail" id="{prefix}-rail" style="left:{x0}px;top:{y}px;width:{x1 - x0}px"></div>',
             f'<div class="tlprog" id="{prefix}-prog" style="left:{x0}px;top:{y}px;width:{x1 - x0}px"></div>']
    for (lab, i), x in zip(NODES, xs):
        parts.append(f'<div class="tlnode{" big" if big else ""}" id="{prefix}-n{i}" style="left:{x - r}px;top:{y - r + 1}px;width:{2 * r}px;height:{2 * r}px"></div>')
        parts.append(f'<div class="tllab{" big" if big else ""}" id="{prefix}-l{i}" style="left:{x - 200}px;top:{y + (30 if big else 20)}px;font-size:{fs}px">{html.escape(lab)}</div>')
    return "".join(parts), xs


def g_title():
    return f"""<div class="dark"></div><div class="tex" style="opacity:.10;mix-blend-mode:screen"></div>
<div class="vign2"></div>
<div class="ttl" id="g01-t">{''.join(f'<span class="ch">{html.escape(c) if c != " " else "&nbsp;"}</span>' for c in "SEJARAH PENYAKIT MENTAL")}</div>
<div class="ttl-sub" id="g01-s">Dari Zaman Purba ke Era Moden</div>
<svg class="ttl-line" viewBox="0 0 1200 40" id="g01-line"><path id="g01-path" d="M10 20 L1190 20" stroke="{GOLD}" stroke-width="2" fill="none"/>
{''.join(f'<circle id="g01-d{i}" cx="{10 + i * 295}" cy="20" r="6" fill="{GOLD}"/>' for i in range(5))}</svg>"""


CULT = [("Yunani", 470, 380), ("Mesir Purba", 610, 640), ("Mesopotamia", 900, 470), ("India", 1240, 660), ("China", 1500, 400)]


def g_cultures():
    dots = "".join(
        f'<div class="cnode" id="g02-c{i}" style="left:{x - 150}px;top:{y - 60}px">'
        f'<svg viewBox="0 0 120 120" class="cring"><circle cx="60" cy="60" r="44" class="inkc" id="g02-r{i}"/>'
        f'<circle cx="60" cy="60" r="9" fill="{SEPIA}"/></svg><div class="clab">{n}</div></div>'
        for i, (n, x, y) in enumerate(CULT))
    path = "M" + " L".join(f"{x} {y}" for _, x, y in sorted(CULT, key=lambda c: c[1]))
    return f"""<div class="tex"></div><div class="vign3"></div>
<svg class="cpath" viewBox="0 0 1920 1080"><path id="g02-p" d="{path}" stroke="{SEPIA}" stroke-opacity=".45" stroke-width="3" stroke-dasharray="10 12" fill="none"/></svg>
{dots}
<div class="chead" id="g02-h">Budaya berbeza, tafsiran berbeza</div>"""


HUM = [("Darah", "#8E2A23"), ("Kahak", "#7E95A0"), ("Hempedu Kuning", "#C99A2E"), ("Hempedu Hitam", "#2A221C")]


def g_humours():
    cells = "".join(
        f'<div class="hcell" id="g03-c{i}" style="left:{560 + (i % 2) * 460}px;top:{330 + (i // 2) * 250}px">'
        f'<div class="hdot" style="background:{c}"></div><div class="hname">{n}</div></div>'
        for i, (n, c) in enumerate(HUM))
    return f"""<div class="tex"></div><div class="vign3"></div>
<div class="hk" id="g03-k">Teori lama · Hippocrates</div>
<div class="hhead" id="g03-h">Keseimbangan Empat Cecair Badan</div>
{cells}
<div class="stamp" id="g03-st"><span>TIDAK LAGI DITERIMA</span></div>"""


def g_portraits():
    def card(i, img, name, dates, place):
        return (f'<div class="pcard" id="g04-p{i}"><div class="pframe"><img src="img/{img}" class="pimg" id="g04-i{i}"/></div>'
                f'<div class="pname">{name}</div><div class="pmeta">{dates}</div><div class="pmeta2">{place}</div></div>')
    return f"""<div class="slate"></div><div class="tex" style="opacity:.16;mix-blend-mode:multiply"></div><div class="vign2"></div>
<div class="phead" id="g04-h">AKHIR ABAD KE-18</div>
<div class="prow">{card(0, "pinel.jpg", "Philippe Pinel", "1745 – 1826", "Paris, Perancis")}{card(1, "tuke.jpg", "William Tuke", "1732 – 1822", "The Retreat, York, England · 1796")}</div>
<div class="credit">Potret: etsa C. Callet · Wellcome Collection (CC BY 4.0)</div>"""


def g_modern():
    ticks = "".join(f'<div class="mtick" style="left:{x}px"></div><div class="mtl" style="left:{x - 60}px">{lab}</div>'
                    for x, lab in ((260, "1952"), (620, "1970"), (980, "1990"), (1340, "2010"), (1660, "HARI INI")))
    chips = "".join(f'<div class="mchip" id="g05-c{i}" style="left:{x}px">{t}</div>'
                    for i, (t, x) in enumerate((("Penyelidikan", 420), ("Hak pesakit", 860), ("Penjagaan", 1260))))
    return f"""<div class="navybg"></div><div class="grid"></div><div class="vign2"></div>
<div class="mhead" id="g05-h">ERA RAWATAN MODEN</div>
<div class="mline" id="g05-l"></div>{ticks}{chips}"""


def g_recap():
    tl_html, _ = timeline_svg("g06", 260, 1660, 470, big=True)
    return f"""<div class="navybg teal"></div><div class="tex" style="opacity:.07;mix-blend-mode:screen"></div><div class="vign2"></div>
{tl_html}
<div class="rk" id="g06-a">PENGETAHUAN BERUBAH</div>
<div class="rk gold" id="g06-b">MARUAH MANUSIA</div>"""


def g_end():
    words = "PENYAKIT MENTAL BUKAN KELEMAHAN".split()
    return f"""<div class="endbg"></div><div class="vign2"></div>
<div class="e1">{''.join(f'<span class="ew" id="g07-w{i}">{w}</span>' for i, w in enumerate(words))}</div>
<div class="e2" id="g07-s">Bersama Kita Hapuskan Stigma</div>
<div class="brand" id="g07-b"><span class="bl"></span><span class="bt">BORAK JIWA</span><span class="bl"></span></div>
<div class="ep" id="g07-ep">Episod 1 · Sejarah Penyakit Mental</div>
<div class="help" id="g07-help">Perlukan sokongan? Talian HEAL 15555 · Befrienders KL 03-7627 2929</div>"""


GFX = {"title": g_title, "cultures": g_cultures, "humours": g_humours, "portraits": g_portraits,
       "modern": g_modern, "recap": g_recap, "end": g_end}


# ------------------------------------------------------------------ shots
def build_shots():
    shots = TL["shots"]
    for z, s in enumerate(shots):
        sid, t0, t1 = s["id"], fq(s["t0"]), fq(s["t1"])
        nxt = shots[z + 1] if z + 1 < len(shots) else None
        # transition windows (incoming shot): cut = 0.3 s dissolve, ink/tear = 0.8 s reveal, fade = 1.0 s
        WIN = {"cut": (-0.25, 0.05), "ink": (-0.5, 0.3), "tear": (-0.5, 0.3), "fade": (-0.4, 0.6), "black": (0, 0)}
        hold = fq(min(DUR, nxt["t0"] + WIN[nxt.get("in", "cut")][1] + 0.05)) if nxt else DUR
        mode = s.get("in", "cut")
        if s["kind"] == "video":
            dur = round(min(s.get("srcdur", 5.04) - s.get("mstart", 0), hold - t0 + 0.04), 3)
            if hold - t0 > s.get("srcdur", 5.04) - s.get("mstart", 0) + 0.05:
                raise SystemExit(f"{sid}: needs {hold - t0:.2f}s of footage")
            ms = f' data-media-start="{s["mstart"]}"' if s.get("mstart") else ""
            inner = (f'<div class="kb" id="{sid}-kb"><video class="clip shotv" id="{sid}-v" src="broll/{s["src"]}.mp4" muted playsinline '
                     f'data-start="{t0}" data-duration="{dur}"{ms} data-track-index="{1 + z % 2}"></video></div>')
            js.append(f"tl.fromTo('#{sid}-kb', {{scale:1.0}}, {{scale:1.035, duration:{round(hold - t0, 3)}, ease:'sine.inOut'}}, {t0});")
        elif s["kind"] == "still":
            inner = f'<div class="kb" id="{sid}-kb"><img class="shotimg" src="img/{s["src"]}" /></div>'
            js.append(f"tl.fromTo('#{sid}-kb', {{scale:1.02, xPercent:0}}, {{scale:1.11, xPercent:-1.5, duration:{round(hold - t0, 3)}, ease:'sine.inOut'}}, {t0});")
        else:
            inner = f'<div class="gfx" id="{sid}-g">{GFX[s["kind"]]()}</div>'
        body.append(f'<div class="shot" id="{sid}" style="z-index:{10 + z}"><div class="shin{" ink" if mode == "ink" else ""}" id="{sid}-in">{inner}</div></div>')
        a, b = WIN[mode]
        SET(f"#{sid}", t0 + a - 0.05, {"opacity": 1})
        if mode == "cut":
            A(f"#{sid}-in", t0 + a, {"opacity": 0}, {"opacity": 1}, b - a, "power1.inOut")      # short dissolve
        elif mode == "black":
            A(f"#{sid}-in", 0, {"opacity": 0}, {"opacity": 1}, 1.2, "power2.out")
        elif mode == "fade":
            A(f"#{sid}-in", t0 + a, {"opacity": 0}, {"opacity": 1}, b - a, "power2.inOut")
        elif mode == "ink":                                                                    # ink-bleed reveal
            js.append(f"tl.fromTo('#{sid}-in', {{'--r':'0%'}}, {{'--r':'140%', duration:{b - a}, ease:'power2.inOut'}}, {fq(t0 + a)});")
        elif mode == "tear":                                                                   # paper tear, left → right
            body.append(f'<div class="tear" id="{sid}-tear" style="z-index:{10 + z}"><svg viewBox="0 0 60 1080" preserveAspectRatio="none">'
                        f'<path d="{tear_path()}" fill="{PARCH}"/></svg></div>')
            js.append(f"tl.fromTo('#{sid}-in', {{clipPath:'inset(0% 100% 0% 0%)'}}, {{clipPath:'inset(0% 0% 0% 0%)', duration:{b - a}, ease:'power3.inOut'}}, {fq(t0 + a)});")
            js.append(f"tl.fromTo('#{sid}-tear', {{x:-40, opacity:1}}, {{x:1940, duration:{b - a}, ease:'power3.inOut'}}, {fq(t0 + a)});")
            SET(f"#{sid}-tear", t0 + b + 0.02, {"opacity": 0})
        SET(f"#{sid}", hold, {"opacity": 0})
    return shots


def tear_path():
    import random
    r = random.Random(5)
    pts = [(0, 0)]
    y = 0
    while y < 1080:
        y += r.randint(18, 42)
        pts.append((r.randint(18, 52), min(y, 1080)))
    pts.append((0, 1080))
    return "M" + " L".join(f"{x} {y}" for x, y in pts) + " Z"


def graphics_anims():
    S = {s["id"]: s for s in TL["shots"]}
    # g01 title: letters emerge from darkness
    t = 11.85
    js.append(f"tl.fromTo('#g01-t .ch', {{opacity:0, y:14, scale:1.25}}, {{opacity:1, y:0, scale:1, duration:1.1, ease:'power3.out', stagger:0.035}}, {fq(t + 0.75)});")
    A("#g01-s", t + 1.9, {"opacity": 0, "y": 16}, {"opacity": 1, "y": 0}, 0.8)
    js.append(f"tl.fromTo('#g01-path', {{strokeDashoffset:1200}}, {{strokeDashoffset:0, duration:1.4, ease:'power2.inOut'}}, {fq(t + 1.7)});")
    for i in range(5):
        A(f"#g01-d{i}", t + 1.8 + i * 0.25, {"opacity": 0, "scale": 0, "transformOrigin": "50% 50%"}, {"opacity": 1, "scale": 1}, 0.35, "back.out(2)")
    TO("#g01-t, #g01-s, #g01-line", 14.95, {"opacity": 0}, 0.4)

    # g02 cultures: path draws, ink rings one by one
    t0 = S["g02"]["t0"]
    A("#g02-h", t0 + 0.2, {"opacity": 0, "y": -14}, {"opacity": 1, "y": 0}, 0.6)
    js.append(f"tl.fromTo('#g02-p', {{strokeDashoffset:2400}}, {{strokeDashoffset:0, duration:2.6, ease:'power1.inOut'}}, {fq(t0 + 0.4)});")
    order = sorted(range(len(CULT)), key=lambda i: CULT[i][1])
    for k, i in enumerate(order):
        tt = t0 + 0.45 + k * 0.5
        A(f"#g02-c{i}", tt, {"opacity": 0, "y": 12}, {"opacity": 1, "y": 0}, 0.45)
        js.append(f"tl.fromTo('#g02-r{i}', {{strokeDashoffset:280}}, {{strokeDashoffset:0, duration:0.7, ease:'power2.out'}}, {fq(tt)});")

    # g03 humours + stamp on "tidak lagi diterima"
    t0 = S["g03"]["t0"]
    A("#g03-k", t0 + 0.15, {"opacity": 0}, {"opacity": 1}, 0.5)
    A("#g03-h", t0 + 0.25, {"opacity": 0, "y": 14}, {"opacity": 1, "y": 0}, 0.6)
    for i in range(4):
        A(f"#g03-c{i}", t0 + 0.55 + i * 0.22, {"opacity": 0, "scale": 0.8}, {"opacity": 1, "scale": 1}, 0.45, "back.out(1.6)")
    ts = T("s3", "tidak lagi diterima")
    A("#g03-st", ts, {"opacity": 0, "scale": 2.2, "rotation": -14}, {"opacity": 1, "scale": 1, "rotation": -9}, 0.28, "power4.in")
    A(".hcell", ts + 0.1, {"opacity": 1}, {"opacity": 0.35}, 0.4, "power2.out")

    # g04 portraits
    t0 = S["g04"]["t0"]
    A("#g04-h", t0 + 0.15, {"opacity": 0, "scale": 1.12}, {"opacity": 1, "scale": 1}, 1.0)
    tp, tt_ = T("s4", "Philippe Pinel"), T("s4", "William Tuke")
    A("#g04-p0", t0 + 0.5, {"opacity": 0, "x": -60}, {"opacity": 1, "x": 0}, 0.8)
    A("#g04-p1", t0 + 0.95, {"opacity": 0, "x": 60}, {"opacity": 1, "x": 0}, 0.8)
    A("#g04-p0 .pname", tp - 0.05, {"color": CREAM}, {"color": GOLD}, 0.4, "power2.out")
    A("#g04-p1 .pname", tt_ - 0.05, {"color": CREAM}, {"color": GOLD}, 0.4, "power2.out")
    for i, tt in ((0, t0 + 0.5), (1, t0 + 0.95)):
        js.append(f"tl.fromTo('#g04-i{i}', {{scale:1.0}}, {{scale:1.08, duration:{round(S['g04']['t1'] - tt + 0.5, 2)}, ease:'sine.inOut'}}, {fq(tt)});")
    A(".credit", t0 + 0.6, {"opacity": 0}, {"opacity": 1}, 0.6)

    # g05 modern era
    t0 = S["g05"]["t0"]
    A("#g05-h", t0 + 0.1, {"opacity": 0, "y": 16}, {"opacity": 1, "y": 0}, 0.6)
    A("#g05-l", t0 + 0.2, {"scaleX": 0, "transformOrigin": "0% 50%"}, {"scaleX": 1}, 1.6, "power2.inOut")
    for i, tt in enumerate((t0 + 0.6, T("s5", "hak") - 0.1, T("s5", "penjagaan") - 0.1)):
        A(f"#g05-c{i}", tt, {"opacity": 0, "y": 20}, {"opacity": 1, "y": 0}, 0.45)

    # g06 recap: nodes light up across the whole history, then two kinetic lines
    t0 = S["g06"]["t0"]
    A("#g06-rail", t0, {"scaleX": 0, "transformOrigin": "0% 50%"}, {"scaleX": 1}, 0.9, "power2.inOut")
    A("#g06-prog", t0 + 0.4, {"scaleX": 0, "transformOrigin": "0% 50%"}, {"scaleX": 1}, 2.2, "power2.inOut")
    for i in range(5):
        A(f"#g06-n{i}", t0 + 0.4 + i * 0.5, {"scale": 0.4, "backgroundColor": "rgba(244,235,216,.25)"}, {"scale": 1, "backgroundColor": GOLD}, 0.35, "back.out(2)")
        A(f"#g06-l{i}", t0 + 0.45 + i * 0.5, {"opacity": 0, "y": 10}, {"opacity": 1, "y": 0}, 0.4)
    A("#g06-a", T("s6", "pengetahuan berubah") - 0.1, {"opacity": 0, "y": 24}, {"opacity": 1, "y": 0}, 0.6)
    A("#g06-b", T("s6", "maruah manusia") - 0.1, {"opacity": 0, "y": 24}, {"opacity": 1, "y": 0}, 0.6)

    # g07 end screen
    t0 = S["g07"]["t0"]
    for i in range(4):
        A(f"#g07-w{i}", t0 + 0.35 + i * 0.22, {"opacity": 0, "y": 30}, {"opacity": 1, "y": 0}, 0.7)
    A("#g07-s", t0 + 1.9, {"opacity": 0, "y": 16}, {"opacity": 1, "y": 0}, 0.8)
    A("#g07-b", t0 + 3.6, {"opacity": 0, "scale": 1.15}, {"opacity": 1, "scale": 1}, 1.0)
    A("#g07-ep", t0 + 4.2, {"opacity": 0}, {"opacity": 1}, 0.7)
    A("#g07-help", t0 + 4.6, {"opacity": 0}, {"opacity": 0.85}, 0.7)


# ------------------------------------------------------------------ overlays: era timeline, kinetic text, lower thirds, chips
def overlays():
    rail, xs = timeline_svg("et", 560, 1360, 74)
    body.append(f'<div class="era" id="et">{rail}</div>')
    # appearances: (time, active node, progress fraction 0..1 of full rail)
    apps = [(T("s2", "zaman purba"), 0, 0.0), (T("s3", "Lebih dua ribu"), 1, 0.25), (T("s4", "sepanjang sejarah"), 1.5, 0.375),
            (T("s4", "Pada penghujung") - 0.1, 2, 0.5), (T("s5", "Menjelang"), 3, 0.75), (T("s6", "Hari ini"), 4, 1.0)]
    prev = 0.0
    for k, (t, node, frac) in enumerate(apps):
        if k == 3:   # the portraits card already shows AKHIR ABAD KE-18: no bar over it
            prev = frac
            continue
        A("#et", t - 0.1, {"opacity": 0}, {"opacity": 1}, 0.5, "power2.out", ir=(k == 0))
        A("#et-prog", t + 0.2, {"scaleX": prev, "transformOrigin": "0% 50%"}, {"scaleX": frac}, 1.0, "power2.inOut", ir=(k == 0))
        for i in range(5):
            on = i <= node
            cur = abs(i - node) < 0.01
            js.append(f"tl.set('#et-n{i}', {{backgroundColor:'{GOLD if on else 'rgba(244,235,216,.35)'}', scale:{1.35 if cur else 1}}}, {fq(t + 0.2 + (0.6 if cur else 0))});")
            js.append(f"tl.set('#et-l{i}', {{opacity:{1 if cur else 0.45}, color:'{GOLD if cur else CREAM}'}}, {fq(t + 0.2 + (0.6 if cur else 0))});")
        TO("#et", t + 3.4, {"opacity": 0}, 0.5)
        prev = frac

    def kin(id_, cls, text, t, t_out, style=""):
        body.append(f'<div class="{cls}" id="{id_}" style="{style}">{text}</div>')
        A(f"#{id_}", t, {"opacity": 0, "y": 18}, {"opacity": 1, "y": 0}, 0.7)
        TO(f"#{id_}", t_out, {"opacity": 0}, 0.45)

    # chapter word over Mesopotamia
    tz = T("s2", "zaman purba")
    kin("k-purba", "chap", "ZAMAN PURBA", tz + 0.15, tz + 4.0)
    kin("k-purba2", "place", "Rekaan semula · Mesopotamia", tz + 0.7, tz + 4.0)
    # Hippocrates lower third
    th = T("s3", "Hippocrates")
    body.append(f"""<div class="l3" id="l3-h"><div class="l3rule" id="l3-hr"></div><div class="l3n">HIPPOCRATES</div>
<div class="l3m">± 400 SM · Kos, Yunani</div><div class="l3chip" id="l3-hc">Penjelasan Semula Jadi</div></div>""")
    A("#l3-h", 37.35, {"opacity": 0, "x": -30}, {"opacity": 1, "x": 0}, 0.6)
    A("#l3-hr", 37.35, {"scaleY": 0, "transformOrigin": "50% 0%"}, {"scaleY": 1}, 0.6)
    A("#l3-hc", T("s3", "semula jadi") - 0.15, {"opacity": 0, "y": 12}, {"opacity": 1, "y": 0}, 0.45)
    TO("#l3-h", 40.85, {"opacity": 0, "x": -20}, 0.35)
    _ = th
    # institutions place tag
    kin("k-inst", "place", "Rekaan semula · Eropah, abad ke-18 – 19", 52.3, 55.6)
    # garden: humane treatment
    kin("k-humane", "humane", "Rawatan Lebih Berperikemanusiaan", T("s4", "memperjuangkan") + 0.4, 73.0)
    # 1952 + chlorpromazine
    t52 = T("s5", "sembilan belas")
    body.append('<div class="yr" id="k-1952">1952</div><div class="drug" id="k-cpz">CHLORPROMAZINE</div>'
                '<div class="drug2" id="k-cpz2">Mula digunakan dalam psikiatri · Paris, Perancis</div>')
    A("#k-1952", t52 - 0.05, {"opacity": 0, "scale": 1.25}, {"opacity": 1, "scale": 1}, 0.9)
    tc = T("s5", "chlorpromazine")
    A("#k-cpz", tc - 0.1, {"opacity": 0, "scale": 1.18}, {"opacity": 1, "scale": 1}, 0.8)
    A("#k-cpz2", tc + 0.25, {"opacity": 0}, {"opacity": 1}, 0.4)
    TO("#k-1952, #k-cpz, #k-cpz2", 77.2, {"opacity": 0}, 0.3)
    # present-day treatment list
    items = [("Psikoterapi", T("s6", "psikoterapi")), ("Ubat, apabila sesuai", T("s6", "ubat apabila")),
             ("Sokongan keluarga", T("s6", "sokongan keluarga")), ("Pemulihan dalam komuniti", T("s6", "pemulihan"))]
    body.append('<div class="tx" id="tx">' + "".join(f'<div class="txi" id="tx{i}"><span class="txd"></span>{n}</div>' for i, (n, _) in enumerate(items)) + "</div>")
    for i, (_, t) in enumerate(items):
        A(f"#tx{i}", t - 0.1, {"opacity": 0, "x": -24}, {"opacity": 1, "x": 0}, 0.5)
    TO("#tx", T("s6", "Tetapi satu") + 0.2, {"opacity": 0, "x": -20}, 0.45)
    # STIGMA
    ts = T("s6", "stigma")
    body.append('<div class="stig" id="k-stig">STIGMA</div>')
    A("#k-stig", ts - 0.05, {"opacity": 0, "scale": 1.22}, {"opacity": 1, "scale": 1}, 0.6)
    TO("#k-stig", 100.85, {"opacity": 0}, 0.3)

    # disclosure tags: dramatisation / AI visuals on generated footage
    ai = [(s["t0"], s["t1"]) for s in TL["shots"] if s["kind"] in ("video", "still")]
    body.append('<div class="tag" id="tag-ai">Dramatisasi · visual dijana AI</div>')
    on, first = False, True
    for k, (a, b) in enumerate(ai):
        if not on:
            A("#tag-ai", a + 0.3, {"opacity": 0}, {"opacity": 0.6}, 0.4, "power1.out", ir=first)
            first = False
            on = True
        nxt = ai[k + 1][0] if k + 1 < len(ai) else None
        if nxt is None or nxt > b + 0.2:
            TO("#tag-ai", b - 0.3, {"opacity": 0}, 0.3, "power1.in")
            on = False


# ------------------------------------------------------------------ subtitles
EMPH_GOLD = {"200", "2,000", "Hippocrates", "Yunani", "Philippe", "Pinel", "William", "Tuke", "ke-18", "1952", "zaman", "purba",
             "stigma", "maruah", "ghaib"}
EMPH_TEAL = {"semula", "jadi", "perubatan", "chlorpromazine", "psikoterapi", "keluarga", "komuniti", "bantuan", "budaya",
             "berperikemanusiaan", "lemah"}
MERGE = [(("dua", "ratus"), "200"), (("dua", "ribu"), "2,000"), (("kelapan", "belas"), "ke-18"),
         (("sembilan", "belas", "lima", "puluh", "dua"), "1952")]


def tokens(sid):
    ws = WT[sid]
    out, i = [], 0
    norm = lambda s: re.sub(r"[^\w]", "", s.lower())
    while i < len(ws):
        for seq, rep in MERGE:
            n = len(seq)
            if tuple(norm(w["text"]) for w in ws[i:i + n]) == seq:
                tail = re.sub(r"^[\w-]+", "", ws[i + n - 1]["text"])
                out.append({"text": rep + tail, "start": ws[i]["start"], "end": ws[i + n - 1]["end"]})
                i += n
                break
        else:
            out.append(dict(ws[i]))
            i += 1
    return out


KEEP = {("cecair", "badan"), ("ketika", "itu"), ("abad", "ke-18"), ("semula", "jadi"), ("gangguan", "mental"),
        ("kesihatan", "mental"), ("philippe", "pinel"), ("william", "tuke"), ("tingkah", "laku"), ("tak", "dengar"), ("tidak", "lagi"), ("lagi", "diterima"), ("kini", "tidak"), ("keadaan", "mental"), ("pinel", "dan"), ("dan", "william"), ("keseimbangan", "cecair"), ("sejak", "zaman")}


def split_balanced(ws, maxc=50):
    """Split one sentence into the fewest lines <= maxc chars, balanced, preferring breaks after commas."""
    import itertools
    L = sum(len(w["text"]) + 1 for w in ws) - 1
    if L <= maxc + 4:
        return [ws]
    best = None
    for k in range(2, 5):
        for cuts in itertools.combinations(range(1, len(ws)), k - 1):
            parts = [ws[i:j] for i, j in zip((0,) + cuts, cuts + (len(ws),))]
            lens = [sum(len(w["text"]) + 1 for w in p_) - 1 for p_ in parts]
            if max(lens) > maxc + 4:
                continue
            cost = sum((x - L / k) ** 2 for x in lens) + 350 * k
            cost -= sum(400 for p_ in parts[:-1] if p_[-1]["text"].endswith(","))
            cost += sum(900 for p_ in parts if len(p_) == 1)
            nk = lambda t: re.sub(r"[^\w-]", "", t.lower())
            cost += sum(5000 for c in cuts if (nk(ws[c - 1]["text"]), nk(ws[c]["text"])) in KEEP)
            if best is None or cost < best[0]:
                best = (cost, parts)
    return best[1] if best else [ws]


def subtitles():
    segs = []
    for sid in WT:
        sent = []
        for w in tokens(sid):
            sent.append(w)
            if re.search(r"[.?!:]$", w["text"]):
                segs += split_balanced(sent)
                sent = []
        if sent:
            segs += split_balanced(sent)
    # merge orphans (1 short word) into previous segment
    merged = []
    for s in segs:
        if merged and len(s) == 1 and sum(len(x["text"]) for x in merged[-1]) < 34 and s[0]["start"] - merged[-1][-1]["end"] < 0.4:
            merged[-1] += s
        else:
            merged.append(s)
    for k, s in enumerate(merged):
        a = s[0]["start"] - 0.08
        b = s[-1]["end"] + 0.35
        if k + 1 < len(merged):
            b = min(b, merged[k + 1][0]["start"] - 0.1)
        txt = []
        for w in s:
            core = re.sub(r"[^\w,-]", "", w["text"]).rstrip(",")
            cls = "g" if core in EMPH_GOLD else ("t" if core.lower() in EMPH_TEAL else "")
            word = html.escape(w["text"].rstrip(".,:") if w is s[-1] else w["text"])
            txt.append(f'<span class="{cls}">{word}</span>' if cls else word)
        body.append(f'<div class="sub" id="sub{k}"><span class="subin">{" ".join(txt)}</span></div>')
        A(f"#sub{k}", a, {"opacity": 0, "y": 6}, {"opacity": 1, "y": 0}, 0.16, "power2.out")
        TO(f"#sub{k}", b - 0.12, {"opacity": 0}, 0.12, "power1.in")
        SET(f"#sub{k}", b, {"opacity": 0})
    return merged


CSS = f"""
@font-face{{font-family:"Cinzel";src:url("fonts/Cinzel-600.woff2") format("woff2");font-weight:600;font-display:block}}
@font-face{{font-family:"Corm";src:url("fonts/CormorantGaramond-600.woff2") format("woff2");font-weight:600;font-display:block}}
@font-face{{font-family:"CormI";src:url("fonts/CormorantGaramond-500i.woff2") format("woff2");font-weight:500;font-style:italic;font-display:block}}
@font-face{{font-family:"PJS";src:url("fonts/PlusJakartaSans-500.woff2") format("woff2");font-weight:500;font-display:block}}
@font-face{{font-family:"PJS";src:url("fonts/PlusJakartaSans-700.woff2") format("woff2");font-weight:700;font-display:block}}
@font-face{{font-family:"PJS";src:url("fonts/PlusJakartaSans-800.woff2") format("woff2");font-weight:800;font-display:block}}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; padding:0; width:{W}px; height:{H}px; overflow:hidden; background:#000; font-family:"PJS", sans-serif; }}
#stage {{ position:relative; width:100%; height:100%; overflow:hidden; background:#000; }}
.shot {{ position:absolute; inset:0; opacity:0; overflow:hidden; }}
.shin {{ position:absolute; inset:0; --r:140%; }}
.shin.ink {{ -webkit-mask-image:radial-gradient(circle at 50% 55%, #000 calc(var(--r) - 18%), rgba(0,0,0,.55) calc(var(--r) - 9%), transparent var(--r));
  mask-image:radial-gradient(circle at 50% 55%, #000 calc(var(--r) - 18%), rgba(0,0,0,.55) calc(var(--r) - 9%), transparent var(--r)); }}
.kb {{ position:absolute; inset:0; }}
.shotv, .shotimg {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
.gfx {{ position:absolute; inset:0; overflow:hidden; }}
.tear {{ position:absolute; top:0; left:0; width:60px; height:1080px; opacity:0; filter:drop-shadow(-8px 0 14px rgba(0,0,0,.45)); }}
.tear svg {{ width:60px; height:1080px; }}
.dark {{ position:absolute; inset:0; background:radial-gradient(70% 70% at 50% 50%, #1a1410 0%, #070504 100%); }}
.tex {{ position:absolute; inset:0; background:url("img/parchment.png") center/cover no-repeat; }}
.vign2 {{ position:absolute; inset:0; box-shadow:inset 0 0 260px 60px rgba(0,0,0,.6); }}
.vign3 {{ position:absolute; inset:0; box-shadow:inset 0 0 240px 50px rgba(60,35,10,.38); }}
.ttl {{ position:absolute; left:0; right:0; top:420px; text-align:center; font-family:"Cinzel"; font-weight:600; font-size:104px;
  letter-spacing:.08em; color:{CREAM}; text-shadow:0 0 40px rgba(217,164,65,.25), 0 6px 30px rgba(0,0,0,.6); white-space:nowrap; }}
.ttl .ch {{ display:inline-block; }}
.ttl-sub {{ position:absolute; left:0; right:0; top:560px; text-align:center; font-family:"CormI"; font-style:italic; font-size:50px; color:{GOLD}; }}
.ttl-line {{ position:absolute; left:360px; top:660px; width:1200px; height:40px; }}
#g01-path {{ stroke-dasharray:1200; }}
.cpath {{ position:absolute; inset:0; width:1920px; height:1080px; }}
#g02-p {{ stroke-dasharray:10 12; }}
.cnode {{ position:absolute; width:300px; display:flex; flex-direction:column; align-items:center; }}
.cring {{ width:120px; height:120px; }}
.inkc {{ fill:none; stroke:{SEPIA}; stroke-width:4; stroke-dasharray:280; stroke-linecap:round; }}
.clab {{ font-family:"Cinzel"; font-weight:600; font-size:38px; color:{SEPIA}; margin-top:6px; white-space:nowrap; }}
.chead {{ position:absolute; left:0; right:0; top:150px; text-align:center; font-family:"CormI"; font-style:italic; font-size:64px; color:{SEPIA}; }}
.hk {{ position:absolute; left:0; right:0; top:150px; text-align:center; font-family:"Cinzel"; font-weight:600; font-size:28px; letter-spacing:.2em; color:#7a5a2e; }}
.hhead {{ position:absolute; left:0; right:0; top:200px; text-align:center; font-family:"Corm"; font-weight:600; font-size:70px; color:{SEPIA}; }}
.hcell {{ position:absolute; width:420px; height:200px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:16px; }}
.hdot {{ width:96px; height:96px; border-radius:50%; box-shadow:inset 0 -8px 20px rgba(0,0,0,.35), 0 4px 14px rgba(60,35,10,.35); }}
.hname {{ font-family:"Corm"; font-weight:600; font-size:46px; color:{SEPIA}; }}
.stamp {{ position:absolute; left:560px; top:470px; width:800px; height:150px; display:flex; align-items:center; justify-content:center;
  border:8px solid #A3271F; border-radius:14px; color:#A3271F; font-family:"PJS"; font-weight:800; font-size:62px; letter-spacing:.12em;
  background:rgba(233,220,192,.55); opacity:0; mix-blend-mode:multiply; }}
.slate {{ position:absolute; inset:0; background:linear-gradient(180deg, #2c3540 0%, #1b222b 100%); }}
.phead {{ position:absolute; left:0; right:0; top:84px; text-align:center; font-family:"Cinzel"; font-weight:600; font-size:66px; letter-spacing:.22em; color:{GOLD}; }}
.prow {{ position:absolute; left:0; right:0; top:200px; display:flex; justify-content:center; gap:150px; }}
.pcard {{ width:470px; display:flex; flex-direction:column; align-items:center; opacity:0; }}
.pframe {{ width:400px; height:500px; overflow:hidden; border:2px solid rgba(217,164,65,.7); box-shadow:0 20px 50px rgba(0,0,0,.55); background:#d8c8a8; }}
.pimg {{ width:100%; height:100%; object-fit:cover; object-position:50% 30%; filter:sepia(.35) contrast(1.05); }}
.pname {{ font-family:"Cinzel"; font-weight:600; font-size:44px; color:{CREAM}; margin-top:22px; white-space:nowrap; }}
.pmeta {{ font-family:"CormI"; font-style:italic; font-size:34px; color:{GOLD}; }}
.pmeta2 {{ font-family:"PJS"; font-weight:500; font-size:22px; color:rgba(244,235,216,.8); margin-top:4px; white-space:nowrap; }}
.credit {{ position:absolute; right:40px; bottom:24px; font-family:"PJS"; font-size:17px; color:rgba(244,235,216,.6); opacity:0; }}
.navybg {{ position:absolute; inset:0; background:radial-gradient(90% 90% at 50% 40%, #12305a 0%, {NAVY} 70%); }}
.navybg.teal {{ background:radial-gradient(90% 90% at 50% 40%, #145a60 0%, #082a30 75%); }}
.grid {{ position:absolute; inset:0; background-image:linear-gradient(rgba(92,200,190,.07) 1px, transparent 1px), linear-gradient(90deg, rgba(92,200,190,.07) 1px, transparent 1px); background-size:60px 60px; }}
.mhead {{ position:absolute; left:0; right:0; top:250px; text-align:center; font-family:"PJS"; font-weight:800; font-size:76px; letter-spacing:.18em; color:{CREAM}; }}
.mline {{ position:absolute; left:260px; top:620px; width:1400px; height:4px; background:linear-gradient(90deg, {GOLD}, {TEAL_L}); border-radius:2px; }}
.mtick {{ position:absolute; top:606px; width:4px; height:32px; background:{TEAL_L}; border-radius:2px; }}
.mtl {{ position:absolute; top:654px; width:124px; text-align:center; font-family:"PJS"; font-weight:700; font-size:26px; color:rgba(244,235,216,.85); white-space:nowrap; }}
.mchip {{ position:absolute; top:470px; padding:14px 30px; border-radius:40px; border:2px solid {TEAL_L}; background:rgba(14,79,85,.55);
  font-family:"PJS"; font-weight:700; font-size:34px; color:{CREAM}; opacity:0; white-space:nowrap; }}
.tlrail {{ position:absolute; height:3px; background:rgba(244,235,216,.35); border-radius:2px; }}
.tlprog {{ position:absolute; height:3px; background:{GOLD}; border-radius:2px; transform:scaleX(0); transform-origin:0% 50%; }}
.tlnode {{ position:absolute; border-radius:50%; background:rgba(244,235,216,.35); box-shadow:0 0 0 3px rgba(0,0,0,.25); }}
.tllab {{ position:absolute; width:400px; text-align:center; font-family:"PJS"; font-weight:700; letter-spacing:.12em; color:{CREAM}; white-space:nowrap;
  text-shadow:0 2px 10px rgba(0,0,0,.7); }}
.tllab.big {{ font-family:"Cinzel"; font-weight:600; letter-spacing:.08em; }}
.era {{ position:absolute; inset:0; z-index:70; opacity:0; pointer-events:none; }}
.era::before {{ content:""; position:absolute; left:0; right:0; top:0; height:170px; background:linear-gradient(180deg, rgba(0,0,0,.5), rgba(0,0,0,0)); }}
.rk {{ position:absolute; left:0; right:0; top:640px; text-align:center; font-family:"Cinzel"; font-weight:600; font-size:72px; letter-spacing:.14em; color:{CREAM}; opacity:0; }}
.rk.gold {{ top:740px; color:{GOLD}; }}
.endbg {{ position:absolute; inset:0; background:radial-gradient(85% 85% at 50% 45%, #10464b 0%, #072528 70%, #041619 100%); }}
.e1 {{ position:absolute; left:0; right:0; top:330px; text-align:center; font-family:"Cinzel"; font-weight:600; font-size:76px; letter-spacing:.06em; color:{CREAM}; white-space:nowrap; }}
.ew {{ display:inline-block; margin:0 .22em; opacity:0; }}
.e2 {{ position:absolute; left:0; right:0; top:450px; text-align:center; font-family:"CormI"; font-style:italic; font-size:58px; color:{GOLD}; opacity:0; }}
.brand {{ position:absolute; left:0; right:0; top:600px; display:flex; align-items:center; justify-content:center; gap:28px; opacity:0;
  font-family:"PJS"; font-weight:800; font-size:44px; letter-spacing:.3em; color:{TEAL_L}; }}
.brand .bl {{ width:120px; height:2px; background:{TEAL_L}; opacity:.7; }}
.ep {{ position:absolute; left:0; right:0; top:690px; text-align:center; font-family:"PJS"; font-weight:500; font-size:26px; letter-spacing:.08em; color:rgba(244,235,216,.75); opacity:0; }}
.help {{ position:absolute; left:0; right:0; top:770px; text-align:center; font-family:"PJS"; font-weight:500; font-size:24px; color:rgba(244,235,216,.85); opacity:0; }}
.chap {{ position:absolute; left:140px; top:330px; z-index:72; font-family:"Cinzel"; font-weight:600; font-size:120px; letter-spacing:.1em; color:{CREAM};
  text-shadow:0 6px 40px rgba(0,0,0,.65); opacity:0; }}
.place {{ position:absolute; left:146px; top:478px; z-index:72; font-family:"CormI"; font-style:italic; font-size:38px; color:{GOLD};
  text-shadow:0 3px 18px rgba(0,0,0,.8); opacity:0; }}
#k-inst {{ top:690px; left:120px; font-size:34px; }}
.humane {{ position:absolute; left:0; right:0; top:690px; z-index:72; text-align:center; font-family:"CormI"; font-style:italic; font-size:62px; color:{CREAM};
  text-shadow:0 4px 26px rgba(0,0,0,.75); opacity:0; }}
.l3 {{ position:absolute; left:120px; top:640px; z-index:72; padding-left:30px; opacity:0; }}
.l3rule {{ position:absolute; left:0; top:6px; width:4px; height:150px; background:{GOLD}; }}
.l3n {{ font-family:"Cinzel"; font-weight:600; font-size:64px; letter-spacing:.08em; color:{CREAM}; text-shadow:0 4px 24px rgba(0,0,0,.7); }}
.l3m {{ font-family:"CormI"; font-style:italic; font-size:38px; color:{GOLD}; text-shadow:0 3px 16px rgba(0,0,0,.8); }}
.l3chip {{ display:inline-block; margin-top:12px; padding:8px 22px; border-radius:30px; background:rgba(14,79,85,.85); border:2px solid {TEAL_L};
  font-family:"PJS"; font-weight:700; font-size:26px; color:{CREAM}; opacity:0; }}
.yr {{ position:absolute; left:0; right:0; top:250px; z-index:72; text-align:center; font-family:"Cinzel"; font-weight:600; font-size:240px; letter-spacing:.06em;
  color:{CREAM}; text-shadow:0 10px 60px rgba(0,0,0,.6); opacity:0; }}
.drug {{ position:absolute; left:0; right:0; top:560px; z-index:72; text-align:center; font-family:"PJS"; font-weight:800; font-size:58px; color:{TEAL_L};
  letter-spacing:.28em; text-shadow:0 4px 24px rgba(0,0,0,.8); opacity:0; }}
.drug2 {{ position:absolute; left:0; right:0; top:650px; z-index:72; text-align:center; font-family:"CormI"; font-style:italic; font-size:36px; color:{CREAM};
  text-shadow:0 3px 16px rgba(0,0,0,.85); opacity:0; }}
.tx {{ position:absolute; left:110px; top:250px; z-index:72; display:flex; flex-direction:column; gap:18px; }}
.txi {{ display:flex; align-items:center; gap:18px; padding:14px 30px 14px 22px; border-radius:16px; background:rgba(10,26,47,.62);
  border-left:4px solid {TEAL_L}; font-family:"PJS"; font-weight:700; font-size:36px; color:{CREAM}; opacity:0; white-space:nowrap; width:max-content; }}
.txd {{ width:14px; height:14px; border-radius:50%; background:{GOLD}; }}
.stig {{ position:absolute; left:0; right:0; top:390px; z-index:72; text-align:center; font-family:"PJS"; font-weight:800; font-size:170px; letter-spacing:.32em;
  color:{CREAM}; text-shadow:0 10px 50px rgba(0,0,0,.7); opacity:0; }}
.tag {{ position:absolute; right:44px; top:34px; z-index:80; font-family:"PJS"; font-weight:500; font-size:18px; letter-spacing:.06em; color:{CREAM};
  text-shadow:0 1px 6px rgba(0,0,0,.8); opacity:0; }}
.vig {{ position:absolute; inset:0; z-index:60; pointer-events:none; background:radial-gradient(85% 85% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,.42) 100%); }}
.grain {{ position:absolute; inset:-20px; z-index:61; pointer-events:none; background-image:url("img/grain.png"); background-size:512px 512px; opacity:.075; mix-blend-mode:overlay; }}
.sub {{ position:absolute; left:0; right:0; bottom:104px; z-index:90; text-align:center; opacity:0; pointer-events:none; }}
.subin {{ display:inline-block; max-width:1400px; padding:10px 28px 12px; border-radius:12px; background:rgba(6,12,16,.42);
  font-family:"PJS"; font-weight:700; font-size:46px; line-height:1.25; color:#F7F0E2; text-shadow:0 2px 10px rgba(0,0,0,.75); }}
.subin .g {{ color:{GOLD}; }}
.subin .t {{ color:{TEAL_L}; }}
"""


def main():
    build_shots()
    graphics_anims()
    overlays()
    body.append('<div class="vig"></div><div class="grain" id="grain"></div>')
    js.append(f"tl.fromTo('#grain', {{backgroundPosition:'0px 0px'}}, {{backgroundPosition:'-9300px -6100px', duration:{DUR}, ease:'steps({int(DUR * 12)})'}}, 0);")
    segs = subtitles()
    page = f"""<!doctype html>
<html lang="ms"><head><meta charset="utf-8" />
<style>{CSS}</style></head>
<body>
<div id="stage" data-composition-id="sejarah-pm" data-start="0" data-duration="{DUR}" data-fps="{FPS}" data-width="{W}" data-height="{H}">
  {chr(10).join(body)}
  <audio id="mix" src="audio/mix.wav" data-start="0" data-duration="{DUR}" data-track-index="10" data-volume="1"></audio>
  <script src="vendor/gsap.min.js"></script>
  <script>
  (function () {{
    const tl = window.gsap.timeline({{ paused: true }});
    {(chr(10) + '    ').join(js)}
    window.__timelines["sejarah-pm"] = tl;
  }})();
  </script>
</div>
</body></html>
"""
    (P / "index.html").write_text(page)
    (D / "subtitles.json").write_text(json.dumps([{"start": s[0]["start"], "end": s[-1]["end"], "text": " ".join(w["text"] for w in s)} for s in segs],
                                                 indent=1, ensure_ascii=False))
    print(f"{len(TL['shots'])} shots, {len(segs)} subtitle lines, {len(js)} timeline statements")


if __name__ == "__main__":
    main()
