"""Generate the HyperFrames composition for 'Ubat Psikiatri Lamotrigine' (1080x1920 @ 30).

Layers, bottom to top:
  1. talking head (edit/cut.mp4 as input-video.mp4) inside #video-wrap (camera moves on the wrapper)
  2. full-screen inserts: B-roll slots (Seedance clips in public/broll/Bxx.mp4 when present, else a
     built motion-graphic fallback or nothing) and full-screen motion graphics
  3. cards in the chest band (y 1100-1370): the face sits high in this shot (chin ~y1082 at 1.08x)
  4. LAMOTRIGINE 3D title (full-screen slam that docks into the chest band)
  5. end card
  6. captions (y 1388-1535, x 70-910): above the TikTok UI band and left of the action buttons

Every time is anchored to a phrase in edit/cut_words.json, so the graphics re-time themselves when
the cut changes. On-screen text uses only the speaker's own words, plus the one safety line he
approved ("Ruam baru? Jumpa doktor segera.").

Outputs: public/index.html, storyboard.json, sfx_cues.json
"""

import html
import json
import math
import subprocess
import sys
from pathlib import Path

W = Path(__file__).parent
PUB = W / "public"
FPS = 30
WORDS = json.loads((W.parent / "edit" / "cut_words.json").read_text())
# video frame count, not the container duration (which follows the AAC padding)
DUR = int(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                                   "stream=nb_read_packets", "-of", "csv=p=0", str(PUB / "input-video.mp4")], text=True)) / FPS

NAVY_D, NAVY, NAVY_L = "#06142B", "#0B2347", "#163A6E"
BLUE, BLUE_S = "#3DA9FC", "#9FD8FF"
GOLD, GOLD_L = "#E2B857", "#F3D894"
WHITE, MUTED, CORAL = "#F7F9FC", "#A9BAD3", "#E8735A"
LEAD = 0.12          # an element starts this much before its word so it lands on it


def T(phrase: str, after: float = 0.0, end: bool = False) -> float:
    """Start (or end) of the first occurrence of `phrase` at/after `after` on the cut timeline."""
    toks = phrase.split()
    for i in range(len(WORDS) - len(toks) + 1):
        if WORDS[i]["start"] >= after - 1e-6 and [w["text"] for w in WORDS[i:i + len(toks)]] == toks:
            return WORDS[i + len(toks) - 1]["end"] if end else WORDS[i]["start"]
    raise KeyError(phrase)


def q(t: float) -> float:
    return round(round(min(max(t, 0), DUR) * FPS) / FPS, 4)


SFX = []   # (time, kind, gain_db) for the audio stage


def sfx(t: float, kind: str, gain: float = 0.0) -> None:
    SFX.append({"t": round(t, 3), "kind": kind, "gain_db": gain})


# ---------------------------------------------------------------------------------------------
# icons (stroke icons, viewBox 0 0 48 48)
ICONS = {
    "check": '<path d="M12 25l8 8 16-17"/>',
    "cross": '<path d="M14 14l20 20M34 14L14 34"/>',
    "sleep": '<path d="M30 9h9l-9 10h9"/><path d="M20 21a13 13 0 1 0 13 17A15 15 0 0 1 20 21z"/><path d="M8 8l32 32"/>',
    "sun": '<circle cx="24" cy="24" r="8"/><path d="M24 5v5M24 38v5M5 24h5M38 24h5M10.5 10.5l3.5 3.5M34 34l3.5 3.5M10.5 37.5L14 34M34 14l3.5-3.5"/>',
    "infinity": '<path d="M24 24c-4-6-8-8-12-8a8 8 0 0 0 0 16c4 0 8-2 12-8s8-8 12-8a8 8 0 0 1 0 16c-4 0-8-2-12-8z"/>',
    "steth": '<path d="M12 7v10a8 8 0 0 0 16 0V7"/><path d="M20 25v6a9 9 0 0 0 18 0v-3"/><circle cx="38" cy="25" r="3.5"/>',
    "warn": '<path d="M24 7L4 41h40z"/><path d="M24 19v11M24 35v1"/>',
    "head": '<path d="M28 41v-6h4a3 3 0 0 0 3-3v-5l4-2-4-7a14 14 0 1 0-21 15v8"/><path d="M19 17a5 5 0 1 1 6 5c-2 1-2 3-2 3"/>',
    "nausea": '<path d="M7 18c5-6 10-6 15 0s10 6 15 0"/><path d="M7 30c5-6 10-6 15 0s10 6 15 0"/><path d="M38 12l3-3M41 24h3"/>',
    "moon": '<path d="M30 8a16 16 0 1 0 10 26A18 18 0 0 1 30 8z"/><path d="M33 17h6l-6 7h6"/>',
    "stop": '<path d="M16 26V12a3 3 0 0 1 6 0v10M22 22V9a3 3 0 0 1 6 0v13M28 22V11a3 3 0 0 1 6 0v15"/><path d="M16 24v-4a3 3 0 0 0-6 0v8c0 9 6 15 14 15s12-6 12-14v-3"/>',
    "shield": '<path d="M24 5l15 6v11c0 10-6 17-15 21C15 39 9 32 9 22V11z"/><path d="M17 24l5 5 9-10"/>',
    "comment": '<path d="M8 10h32v22H22l-9 7v-7H8z"/><path d="M15 18h18M15 24h12"/>',
    "pill": '<rect x="6" y="17" width="36" height="14" rx="7"/><path d="M24 17v14"/>',
    "heart": '<path d="M24 40S7 30 7 18a8.5 8.5 0 0 1 17-2 8.5 8.5 0 0 1 17 2c0 12-17 22-17 22z"/>',
}


def icon(name: str, cls: str = "ico", color: str = WHITE) -> str:
    return (f'<svg viewBox="0 0 48 48" class="{cls}"><g fill="none" stroke="{color}" stroke-width="3.4" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g></svg>')


# ---------------------------------------------------------------------------------------------
# deterministic pseudo-random (LCG) for the procedural fallbacks
class Rng:
    def __init__(self, seed: int):
        self.s = seed

    def __call__(self) -> float:
        self.s = (1103515245 * self.s + 12345) % (2 ** 31)
        return self.s / 2 ** 31


def neural_svg(iid: str, seed: int, cx: float = 540, cy: float = 860, rx: float = 430, ry: float = 520,
               n: int = 54, link: float = 250):
    """A glowing neural network inside an ellipse; returns (svg, pulse_edge_ids, glint_node_ids)."""
    r = Rng(seed)
    pts = []
    while len(pts) < n:
        x, y = (r() * 2 - 1), (r() * 2 - 1)
        if x * x + y * y <= 1:
            pts.append((cx + x * rx, cy + y * ry, 3 + r() * 7))
    edges = []
    for i, (x1, y1, _) in enumerate(pts):
        near = sorted(((math.hypot(x1 - x2, y1 - y2), j) for j, (x2, y2, _) in enumerate(pts) if j != i))[:3]
        edges += [(i, j) for d, j in near if d < link and (j, i) not in edges]
    lines = "".join(f'<line x1="{pts[i][0]:.0f}" y1="{pts[i][1]:.0f}" x2="{pts[j][0]:.0f}" y2="{pts[j][1]:.0f}"/>'
                    for i, j in edges)
    pulse_ids, pulses = [], []
    for k, (i, j) in enumerate(edges[::3][:18]):
        L = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
        pid = f"{iid}-p{k}"
        pulse_ids.append((pid, L))
        pulses.append(f'<line id="{pid}" x1="{pts[i][0]:.0f}" y1="{pts[i][1]:.0f}" x2="{pts[j][0]:.0f}" '
                      f'y2="{pts[j][1]:.0f}" stroke-dasharray="46 {L + 60:.0f}" stroke-dashoffset="46"/>')
    glint_ids, nodes = [], []
    for k, (x, y, s) in enumerate(pts):
        gid = f"{iid}-n{k}"
        if k % 9 == 4:
            glint_ids.append(gid)
        nodes.append(f'<circle id="{gid}" cx="{x:.0f}" cy="{y:.0f}" r="{s:.1f}"/>')
    svg = (f'<svg class="net" viewBox="0 0 1080 1920" id="{iid}-net">'
           f'<g class="links">{lines}</g><g class="pulses">{"".join(pulses)}</g><g class="nodes">{"".join(nodes)}</g></svg>')
    return svg, pulse_ids, glint_ids


def molecule_svg(iid: str, seed: int):
    """Abstract hexagonal lattice (conceptual chemistry, not a real molecule)."""
    r = Rng(seed)
    hexes, atoms, bonds = [(540, 820), (540 + 156, 820 + 90), (540 - 156, 820 + 90), (540, 820 + 180 + 0),
                           (540 + 156, 820 - 90), (540 - 156, 820 - 90), (540 + 312, 820)], {}, set()
    for hx, hy in hexes:
        ring = []
        for a in range(6):
            ang = math.pi / 6 + a * math.pi / 3
            p = (round(hx + 104 * math.cos(ang)), round(hy + 104 * math.sin(ang)))
            atoms.setdefault(p, len(atoms))
            ring.append(atoms[p])
        for a in range(6):
            bonds.add(tuple(sorted((ring[a], ring[(a + 1) % 6]))))
    P = {v: k for k, v in atoms.items()}
    bl = "".join(f'<line x1="{P[a][0]}" y1="{P[a][1]}" x2="{P[b][0]}" y2="{P[b][1]}"/>' for a, b in sorted(bonds))
    pulse_ids, pulses = [], []
    for k, (a, b) in enumerate(sorted(bonds)[::2][:16]):
        L = math.hypot(P[a][0] - P[b][0], P[a][1] - P[b][1])
        pid = f"{iid}-p{k}"
        pulse_ids.append((pid, L))
        pulses.append(f'<line id="{pid}" x1="{P[a][0]}" y1="{P[a][1]}" x2="{P[b][0]}" y2="{P[b][1]}" '
                      f'stroke-dasharray="34 {L + 50:.0f}" stroke-dashoffset="34"/>')
    glint_ids, at = [], []
    for k, (x, y) in enumerate(atoms):
        gid = f"{iid}-a{k}"
        big = r() > 0.7
        if big:
            glint_ids.append(gid)
        at.append(f'<circle id="{gid}" class="{"gold" if big else ""}" cx="{x}" cy="{y}" r="{22 if big else 15}"/>')
    svg = (f'<svg class="mol" viewBox="0 0 1080 1920" id="{iid}-net"><defs>'
           f'<radialGradient id="{iid}-g" cx="35%" cy="30%" r="70%"><stop offset="0" stop-color="#E9F6FF"/>'
           f'<stop offset=".45" stop-color="{BLUE_S}"/><stop offset="1" stop-color="{NAVY_L}"/></radialGradient>'
           f'<radialGradient id="{iid}-gg" cx="35%" cy="30%" r="70%"><stop offset="0" stop-color="#FFF6DA"/>'
           f'<stop offset=".5" stop-color="{GOLD}"/><stop offset="1" stop-color="#6B4E12"/></radialGradient></defs>'
           f'<g class="bonds">{bl}</g><g class="pulses">{"".join(pulses)}</g>'
           f'<g class="atoms" style="--g:url(#{iid}-g);--gg:url(#{iid}-gg)">{"".join(at)}</g></svg>')
    return svg, pulse_ids, glint_ids


def probe_dur(p: Path) -> float:
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(p)], text=True))


INS_HOSTS, JS, STORY = [], [], []


def reveal(sel: str, t: float, style: str) -> None:
    if style == "circle":
        JS.append(f"tl.fromTo('{sel}', {{clipPath:'circle(0% at 50% 42%)'}}, {{clipPath:'circle(80% at 50% 42%)', "
                  f"duration:0.5, ease:'power3.inOut'}}, {q(t)});")
    elif style == "up":
        JS.append(f"tl.fromTo('{sel}', {{clipPath:'inset(100% 0% 0% 0%)'}}, {{clipPath:'inset(0% 0% 0% 0%)', "
                  f"duration:0.45, ease:'power3.inOut'}}, {q(t)});")
    elif style == "left":
        JS.append(f"tl.fromTo('{sel}', {{clipPath:'inset(0% 100% 0% 0%)'}}, {{clipPath:'inset(0% 0% 0% 0%)', "
                  f"duration:0.45, ease:'power3.inOut'}}, {q(t)});")
    else:  # fade
        JS.append(f"tl.fromTo('{sel}', {{opacity:0}}, {{opacity:1, duration:0.3, ease:'power2.out'}}, {q(t)});")


def pulses_js(pulse_ids, glint_ids, st, en):
    span = max(en - st - 0.6, 0.6)
    for k, (pid, L) in enumerate(pulse_ids):
        t0 = st + 0.15 + (k * 0.37) % span
        JS.append(f"tl.fromTo('#{pid}', {{strokeDashoffset:46}}, {{strokeDashoffset:{-L:.0f}, duration:0.9, ease:'power2.inOut'}}, {q(t0)});")
        JS.append(f"tl.set('#{pid}', {{opacity:1}}, {q(t0)});")
        JS.append(f"tl.to('#{pid}', {{opacity:0, duration:0.15, ease:'power2.in'}}, {q(t0 + 0.75)});")
    for k, gid in enumerate(glint_ids):
        t0 = st + 0.3 + (k * 0.53) % span
        JS.append(f"tl.fromTo('#{gid}', {{scale:1}}, {{scale:1.7, transformOrigin:'50% 50%', duration:0.35, ease:'power2.out', "
                  f"yoyo:true, repeat:1}}, {q(t0)});")


# ---------------------------------------------------------------------------------------------
# full-screen motion graphics
MG_LEGACY = {}   # name -> (a, b) -> (html, anims); used by scenes_v2.add_scenes


def mg(iid, st, en, body, anims, reveal_style="up"):
    """Register a motion graphic by name (iid 'mg-weight' -> 'weight'); the scene list places and times it."""
    MG_LEGACY[iid.removeprefix("mg-")] = lambda a, b: (body, anims)


def mg_anims(anims, st):
    for sel, t, kind in anims:
        t = q(max(t, st + 0.15))
        if kind == "rise":
            JS.append(f"tl.fromTo('{sel}', {{opacity:0, y:46}}, {{opacity:1, y:0, duration:0.45, ease:'power3.out'}}, {t});")
        elif kind == "pop":
            JS.append(f"tl.fromTo('{sel}', {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.36, ease:'back.out(1.7)'}}, {t});")
            sfx(t, "pop", -10)
        elif kind == "slide":
            JS.append(f"tl.fromTo('{sel}', {{opacity:0, x:-70}}, {{opacity:1, x:0, duration:0.42, ease:'power3.out'}}, {t});")
            sfx(t, "tick", -12)
        elif kind == "stamp":
            JS.append(f"tl.fromTo('{sel}', {{opacity:0, scale:1.8}}, {{opacity:1, scale:1, duration:0.28, ease:'power4.out'}}, {t});")
            sfx(t, "impact", -7)
        elif kind == "fade":
            JS.append(f"tl.fromTo('{sel}', {{opacity:0}}, {{opacity:1, duration:0.35, ease:'power2.out'}}, {t});")
        elif kind == "wipe":
            JS.append(f"tl.fromTo('{sel}', {{clipPath:'inset(0% 100% 0% 0%)'}}, {{clipPath:'inset(0% 0% 0% 0%)', duration:0.5, ease:'power3.inOut'}}, {t});")
        elif isinstance(kind, tuple) and kind[0] == "js":
            JS.append(kind[1].replace("@T", str(t)))
        elif isinstance(kind, tuple) and kind[0] == "sfx":
            sfx(t, kind[1], kind[2])


def add_mgs():
    # weight gauge: "risiko kenaikan berat badan dia sangat rendah ... ramai pasien yang suka"
    s, e = T("dan risiko") - 0.15, T("ubat ni juga dia tak") - 0.1
    # semicircle gauge 300px radius centred at (540, 900); needle settles in the low (left) zone
    arc = "M 240 900 A 300 300 0 0 1 840 900"
    ticks = "".join(
        f'<line x1="{540 - 330 * math.cos(math.radians(a)):.0f}" y1="{900 - 330 * math.sin(math.radians(a)):.0f}" '
        f'x2="{540 - 352 * math.cos(math.radians(a)):.0f}" y2="{900 - 352 * math.sin(math.radians(a)):.0f}"/>'
        for a in range(0, 181, 15))
    body = f"""
      <div class="mg-head"><div class="chip">Kelebihan</div>
        <div class="mg-title" id="g-t">Risiko kenaikan <span class="gold">berat badan</span></div></div>
      <svg class="gauge" viewBox="0 0 1080 1920"><defs><linearGradient id="g-grad" x1="0" x2="1">
        <stop offset="0" stop-color="{BLUE}"/><stop offset=".55" stop-color="{BLUE_S}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient></defs>
        <path d="{arc}" stroke="rgba(255,255,255,.10)" stroke-width="54" fill="none" stroke-linecap="round"/>
        <path id="g-arc" d="{arc}" stroke="url(#g-grad)" stroke-width="54" fill="none" stroke-linecap="round" stroke-dasharray="943" stroke-dashoffset="943"/>
        <g class="gticks">{ticks}</g>
        <g id="g-needle"><path d="M 540 900 L 528 900 L 540 640 L 552 900 Z" fill="{WHITE}"/><circle cx="540" cy="900" r="24" fill="{WHITE}"/>
          <circle cx="540" cy="900" r="10" fill="{NAVY}"/></g></svg>
      <div class="glabel" id="g-low">Sangat rendah</div>
      <div class="gsub" id="g-like">{icon("heart", "ico lg", GOLD)}<span>Ramai pasien suka ubat ni</span></div>"""
    low = T("sangat rendah")
    anims = [("#g-t", s + 0.2, "rise"),
             ("#g-arc", T("kenaikan") - 0.1, ("js", "tl.fromTo('#g-arc', {strokeDashoffset:943}, {strokeDashoffset:0, duration:0.9, ease:'power2.inOut'}, @T);")),
             ("#g-needle", low - 0.05, ("js", "tl.fromTo('#g-needle', {rotation:-90, svgOrigin:'540 900'}, {rotation:-62, svgOrigin:'540 900', duration:0.7, ease:'back.out(1.6)'}, @T);")),
             ("#g-low", T("rendah", after=low) - LEAD, "stamp"),
             ("#g-like", T("ramai pasien") - LEAD, "rise")]
    mg("mg-weight", s, e, body, anims, "up")

    # titration staircase: "perlahan-lahan kena titrate naik" (no doses, no schedule)
    s, e = T("perlahan lahan") - 0.25, T("sebab ada risiko") - 0.1
    bars = "".join(f'<div class="step" id="st-{i}" style="left:{110 + i * 165}px; height:{110 + i * 92}px"></div>' for i in range(5))
    body = f"""
      <div class="mg-head"><div class="chip">Cara mula</div>
        <div class="mg-title" id="st-t">Perlahan-lahan <span class="gold">naik</span></div></div>
      <div class="stairs">{bars}
        <svg class="stair-line" viewBox="0 0 1080 1920"><path id="st-path" d="M 150 1240 L 315 1148 L 480 1056 L 645 964 L 810 872"
          stroke="{GOLD}" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="760" stroke-dashoffset="760"/></svg>
        <div class="st-lab" id="st-l0">Mula rendah</div>
        <div class="st-word" id="st-w">Titrate</div></div>"""
    anims = [("#st-t", s + 0.15, "rise"), ("#st-l0", s + 0.25, "fade")]
    anims += [(f"#st-{i}", s + 0.2 + i * 0.22, ("js", f"tl.fromTo('#st-{i}', {{scaleY:0, transformOrigin:'50% 100%'}}, {{scaleY:1, duration:0.4, ease:'power3.out'}}, @T);"))
              for i in range(5)]
    anims += [("#st-path", T("titrate") - 0.4, ("js", "tl.fromTo('#st-path', {strokeDashoffset:760}, {strokeDashoffset:0, duration:0.9, ease:'power2.inOut'}, @T);")),
              ("#st-w", T("titrate") - LEAD, "pop")]
    mg("mg-titrate", s, e, body, anims, "left")

    # common side effects: three icon rows
    s, e = T("menyebabkan side effect") - 0.2, T("dan ubat ni juga dia tak") - 0.1
    rows = [("head", "Pening kepala", "pening kepala"), ("nausea", "Loya", "loya"), ("moon", "Susah tidur", "susah tidur")]
    body = f"""
      <div class="mg-head"><div class="chip">Side effect biasa</div>
        <div class="mg-title" id="se-t">Seperti <span class="gold">ubat lain</span></div></div>
      <div class="se-stack">{"".join(f'<div class="se-row" id="se-r{i}"><span class="disc">{icon(ic)}</span><span>{txt}</span></div>' for i, (ic, txt, _) in enumerate(rows))}</div>"""
    anims = [("#se-t", T("seperti ubat lain") - LEAD, "rise")]
    anims += [(f"#se-r{i}", T(w) - LEAD, "slide") for i, (_, _, w) in enumerate(rows)]
    mg("mg-sidefx", s, e, body, anims, "up")


# ---------------------------------------------------------------------------------------------
# chest-band cards (above inserts, below captions)
CARD_HOSTS = []


def card(cid, st, en, inner, anims, intent):
    st, en = q(st), q(en)
    CARD_HOSTS.append(f'<div class="card-host clip" id="card-{cid}" data-start="{st}" data-duration="{round(en - st, 4)}" '
                      f'data-track-index="6"><div class="panel" id="{cid}-p">{inner}</div></div>')
    STORY.append({"id": cid, "kind": "card", "start": st, "end": en, "intent": intent})
    JS.append(f"// card {cid}: {intent}")
    if st <= 0.001:
        JS.append(f"tl.set('#{cid}-p', {{opacity:1, y:0}}, 0);")
    else:
        JS.append(f"tl.fromTo('#{cid}-p', {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.42, ease:'power3.out'}}, {st});")
    for sel, t, kind in anims:
        t = q(max(t, st + 0.08)) if st > 0 else q(t)
        if t <= 0.001:
            JS.append(f"tl.set('{sel}', {{opacity:1}}, 0);")
        elif kind == "slide":
            JS.append(f"tl.fromTo('{sel}', {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:0.38, ease:'power3.out'}}, {t});")
        elif kind == "rise":
            JS.append(f"tl.fromTo('{sel}', {{opacity:0, y:26}}, {{opacity:1, y:0, duration:0.4, ease:'power3.out'}}, {t});")
        elif kind == "pop":
            JS.append(f"tl.fromTo('{sel}', {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.34, ease:'back.out(1.8)'}}, {t});")
            sfx(t, "tick", -14)
        elif kind == "under":
            JS.append(f"tl.fromTo('{sel}', {{scaleX:0, transformOrigin:'0% 50%'}}, {{scaleX:1, duration:0.45, ease:'power3.inOut'}}, {t});")
        elif kind == "fade":
            JS.append(f"tl.fromTo('{sel}', {{opacity:0}}, {{opacity:1, duration:0.3, ease:'power2.out'}}, {t});")
        elif kind == "dim":
            JS.append(f"tl.to('{sel}', {{opacity:0.4, duration:0.3, ease:'power2.out'}}, {t});")
        elif kind == "out":
            JS.append(f"tl.to('{sel}', {{opacity:0, y:-12, duration:0.25, ease:'power2.in'}}, {t});")
    JS.append(f"tl.to('#{cid}-p', {{opacity:0, y:-18, duration:0.25, ease:'power2.in'}}, {q(en - 0.25)});")


def row(rid, ic, text, color=WHITE, cls="row"):
    return f'<div class="{cls}" id="{rid}">{icon(ic, "ico", color)}<span>{text}</span></div>'


def add_cards(sc):
    S = {x["id"]: (x["a"], x["b"]) for x in sc}

    card("k00", 0, S["s01"][0] + 0.25,
         '<div class="kick" id="k00-k">Ubat psikiatri</div>'
         '<div class="ttl" id="k00-t">Ubat mood yang <span class="gold">underrated</span></div>'
         '<div class="uline" id="k00-u"></div>',
         [("#k00-k", 0, "fade"), ("#k00-t", 0, "fade"), ("#k00-u", 0.25, "under")],
         "Hook headline on frame 0 (his words: ubat, mood, underrated)")

    s = T("terutamanya") - 0.1
    card("k05", s, T("dan risiko") - 0.2,
         '<div class="kick" id="k05-k">Bipolar disorder · terutamanya</div>'
         '<div class="ttl" id="k05-t">Episod <span class="gold">kemurungan</span></div><div class="uline" id="k05-u"></div>',
         [("#k05-k", s + 0.05, "fade"), ("#k05-t", T("episod") - LEAD, "rise"), ("#k05-u", T("kemurungan") - LEAD, "under")],
         "Especially depressive episodes (his wording)")

    s = T("ubat ni juga dia tak")
    card("k06", s, S["s04"][0] + 0.2,
         '<div class="big-row" id="k06-r">' + icon("sleep", "ico xl", GOLD) +
         '<span>Tak buat rasa <b class="gold">mengantuk</b> sangat</span></div>',
         [("#k06-r", T("tak buat") - LEAD, "rise")],
         "Not very sedating")

    card("k08", S["s05"][0] + 0.15, S["s05"][1] - 0.3,
         row("k08-r2", "steth", 'Dengan <b class="gold">monitoring doktor</b>', GOLD, "row big"),
         [("#k08-r2", T("monitoring") - LEAD, "slide")],
         "With doctor monitoring (over the consultation clip)")

    s = T("setiap ubat pun") - 0.15
    card("k10", s, S["s06"][0] + 0.2,
         '<div class="ttl" id="k10-t">Setiap ubat ada</div>'
         '<div class="ttl xl gold" id="k10-w">Side effect</div><div class="uline" id="k10-u"></div>',
         [("#k10-t", s + 0.05, "rise"), ("#k10-w", T("side effect") - LEAD, "pop"), ("#k10-u", T("side effect") + 0.1, "under")],
         "Every medicine has side effects")

    card("k11", S["s06"][0] + 0.15, T("perlahan lahan") - 0.2,   # s06 runs on under the cube; the label leaves first
         row("k11-r", "pill", 'Mula dengan <b class="gold">dos yang rendah</b>', GOLD, "row big"),
         [("#k11-r", T("dos yang rendah") - LEAD, "slide")],
         "Start with a low dose (over the pill-organizer clip)")

    # serious rash: calm, non-graphic, no B-roll
    s = T("sebab ada risiko") - 0.1
    p2 = T("steven johnson") - 0.35
    card("k12", s, T("dan boleh menyebabkan") - 0.15,
         f'<div class="warnhead" id="k12-k">{icon("warn", "ico", GOLD)}<span>Penting</span></div>'
         '<div class="pgs"><div class="pg" id="k12-pg1"><div class="ttl" id="k12-t">Risiko <span class="gold">ruam kulit</span> yang serius</div></div>'
         '<div class="pg" id="k12-pg2"><div class="ttl" id="k12-t2">Stevens-Johnson <span class="gold">syndrome</span></div>'
         '<div class="sub" id="k12-s">Jarang, tetapi boleh berlaku</div>'
         '<div class="safety" id="k12-x">Ruam baru? Jumpa doktor segera.</div></div></div>',
         [("#k12-k", s + 0.05, "fade"), ("#k12-t", T("ruam kulit") - LEAD, "rise"),
          ("#k12-pg1", p2, "out"), ("#k12-t2", p2 + 0.3, "rise"),
          ("#k12-s", T("rare") - LEAD, "fade"), ("#k12-x", T("boleh berlakulah") + 0.2, "rise")],
         "Serious rash risk, SJS: rare but possible; approved safety line")

    s = T("dan ubat ni juga dia tak")
    card("k13", s, S["s07"][1] - 0.3,
         '<div class="kick" id="k13-k">Lamotrigine</div>'
         + row("k13-r1", "cross", 'Tak begitu kuat untuk <b>fasa mania</b>', CORAL)
         + row("k13-r2", "check", 'Lebih untuk <b class="gold">elak kemurungan</b> datang balik', BLUE_S),
         [("#k13-k", s + 0.05, "fade"), ("#k13-r1", T("tak begitu kuat") - LEAD, "slide"),
          ("#k13-r1", T("dia lebih kepada") - 0.1, "dim"), ("#k13-r2", T("elak kemurungan") - LEAD, "slide")],
         "Not strong for mania; more for preventing depression from returning (stays over the sunrise clip)")

    s = T("sama seperti ubat lain") - 0.05
    card("k14", s, S["m07"][0] + 0.2,
         '<div class="big-row" id="k14-r">' + icon("stop", "ico xl", GOLD) +
         '<span>Jangan <b class="gold">stop sendiri</b></span></div>'
         '<div class="sub" id="k14-s">tanpa advice doktor</div>',
         [("#k14-r", T("jangan stop") - LEAD, "rise"), ("#k14-s", T("tanpa advice") - LEAD, "fade")],
         "Don't stop on your own without the doctor's advice")

    s = T("boleh set appointment") - 0.1
    card("k16", s, S["s08"][0] + 0.15,
         '<div class="name" id="k16-n">Dr Fakrul Azren</div><div class="role" id="k16-r">Mental Health Education</div>'
         '<div class="uline" id="k16-u"></div>',
         [("#k16-n", s + 0.08, "rise"), ("#k16-u", s + 0.3, "under"), ("#k16-r", s + 0.35, "fade")],
         "Name strip (no clinic logo or credentials invented)")

    s = T("apa persoalan") - 0.05
    card("k17", s, T("take care", end=True) + 0.15,
         row("k17-r", "comment", 'Tanya di <b class="gold">ruang komen</b>', GOLD, "row big"),
         [("#k17-r", T("boleh tanya") - LEAD, "pop")],
         "Ask in the comments")


# ---------------------------------------------------------------------------------------------
# LAMOTRIGINE title: full-screen slam on the word, then docks into the chest band
def add_title(sc):
    st = q(T("lamotrigine") - 0.12)
    dock = q(T("pernah dengar") - 0.1)
    en = q(next(x["a"] for x in sc if x["id"] == "m02") + 0.2)
    INS_HOSTS.append(f'<div class="ins clip" id="ins-title" data-start="{st}" data-duration="{round(dock + 0.4 - st, 4)}" '
                     f'data-track-index="5" style="z-index:45"><div class="ins-in" id="title-bg"><div class="mg-bg"></div>'
                     f'<div class="beam" id="title-beam"></div></div></div>')
    letters = "LAMOTRIGINE"   # plain text: background-clip:text does not paint inline-block children
    CARD_HOSTS.append(
        f'<div class="title-host clip" id="title-host" data-start="{st}" data-duration="{round(en - st, 4)}" data-track-index="7">'
        f'<div class="title-plate" id="title-plate"></div>'
        f'<div class="title-wrap" id="title-wrap"><div class="t3d back">{letters}</div><div class="t3d front" id="title-front">{letters}</div>'
        f'<div class="title-sub" id="title-sub">Ubat yang stabilkan mood</div></div></div>')
    STORY.append({"id": "title", "kind": "3d-title", "start": st, "end": en})
    JS.append("// LAMOTRIGINE 3D title: slam, light sweep, dock into the chest band")
    JS.append(f"tl.fromTo('#title-bg', {{opacity:0}}, {{opacity:1, duration:0.2, ease:'power2.out'}}, {st});")
    JS.append(f"tl.fromTo('#title-beam', {{xPercent:-120, opacity:0.0}}, {{xPercent:120, opacity:0.9, duration:1.0, ease:'power2.inOut'}}, {st});")
    JS.append(f"tl.fromTo('#title-wrap', {{opacity:0, scale:1.35, rotationX:38, transformPerspective:900, y:820, filter:'blur(16px)'}}, "
              f"{{opacity:1, scale:1, rotationX:0, y:820, filter:'blur(0px)', duration:0.55, ease:'power3.out'}}, {st});")
    JS.append(f"tl.fromTo('#title-front', {{backgroundPosition:'-120% 0'}}, {{backgroundPosition:'220% 0', duration:1.1, ease:'power2.inOut'}}, {q(st + 0.35)});")
    JS.append(f"tl.fromTo('#title-sub', {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.4, ease:'power3.out'}}, {q(st + 0.45)});")
    JS.append(f"tl.to('#title-wrap', {{y:1060, x:-55, scale:0.6, duration:0.6, ease:'power3.inOut'}}, {dock});")
    JS.append(f"tl.fromTo('#title-plate', {{opacity:0, scaleY:0.6}}, {{opacity:1, scaleY:1, duration:0.45, ease:'power3.out'}}, {q(dock + 0.2)});")
    JS.append(f"tl.to('#title-bg', {{opacity:0, duration:0.4, ease:'power2.inOut'}}, {dock});")
    JS.append(f"tl.to('#title-wrap, #title-plate', {{opacity:0, duration:0.22, ease:'power2.in'}}, {q(en - 0.22)});")
    sfx(st, "impact", -3)
    sfx(st + 0.05, "shimmer", -12)
    sfx(dock + 0.25, "whoosh", -9)


# ---------------------------------------------------------------------------------------------
# camera moves on the talking-head wrapper (the EDL already carries the per-range punch-ins)
def add_camera(sc):
    S = {x["id"]: (x["a"], x["b"]) for x in sc}
    JS.append("// camera: opening punch-in, slow pushes on key lines (transform origin at the face)")
    JS.append("tl.fromTo('#video-wrap', {scale:1.0}, {scale:1.14, duration:0.3, ease:'power3.out'}, 0.04);")
    JS.append(f"tl.set('#video-wrap', {{scale:1.0}}, {q(S['s01'][0] + 0.5)});")
    d = q(T("pernah dengar") - 0.1)
    JS.append(f"tl.fromTo('#video-wrap', {{scale:1.0}}, {{scale:1.07, duration:1.4, ease:'power2.inOut', immediateRender:false}}, {d});")
    JS.append(f"tl.set('#video-wrap', {{scale:1.0}}, {q(S['m02'][0] + 0.7)});")
    s = q(T("sama seperti ubat lain"))
    JS.append(f"tl.fromTo('#video-wrap', {{scale:1.0}}, {{scale:1.06, duration:{round(S['m07'][0] - s, 3)}, ease:'power2.inOut', immediateRender:false}}, {s});")
    JS.append(f"tl.set('#video-wrap', {{scale:1.0}}, {q(S['m07'][0] + 0.5)});")
    s = q(S["m08"][1])
    JS.append(f"tl.fromTo('#video-wrap', {{scale:1.0}}, {{scale:1.05, duration:{round(S['s08'][0] - s, 3)}, ease:'power1.inOut', immediateRender:false}}, {s});")
    JS.append(f"tl.set('#video-wrap', {{scale:1.0}}, {q(S['s08'][0] + 0.7)});")
    sfx(0.04, "impact", -6)


# ---------------------------------------------------------------------------------------------
# end card
def add_end():
    st = q(T("take care", end=True) + 0.2)
    en = DUR
    CARD_HOSTS.append(
        f'<div class="end-host clip" id="end-host" data-start="{st}" data-duration="{round(en - st, 4)}" data-track-index="8">'
        f'<div class="end-bg" id="end-bg"></div><div class="end-wrap" id="end-wrap">'
        f'<div class="end-t" id="end-t1">Spread</div><div class="end-t gold" id="end-t2">Positivity</div>'
        f'<div class="end-line" id="end-line"></div><div class="end-name" id="end-name">Dr Fakrul Azren · Mental Health Education</div>'
        f'</div></div>')
    STORY.append({"id": "end", "kind": "end-card", "start": st, "end": en})
    JS.append("// end card")
    JS.append(f"tl.fromTo('#end-bg', {{opacity:0}}, {{opacity:1, duration:0.35, ease:'power2.out'}}, {st});")
    JS.append(f"tl.fromTo('#end-t1', {{opacity:0, y:50}}, {{opacity:1, y:0, duration:0.45, ease:'power3.out'}}, {q(st + 0.1)});")
    JS.append(f"tl.fromTo('#end-t2', {{opacity:0, y:50}}, {{opacity:1, y:0, duration:0.45, ease:'power3.out'}}, {q(st + 0.25)});")
    JS.append(f"tl.fromTo('#end-line', {{scaleX:0}}, {{scaleX:1, duration:0.5, ease:'power3.inOut'}}, {q(st + 0.5)});")
    JS.append(f"tl.fromTo('#end-name', {{opacity:0}}, {{opacity:1, duration:0.35, ease:'power2.out'}}, {q(st + 0.65)});")
    sfx(st, "whoosh", -6)
    sfx(q(st + 0.25), "shimmer", -8)


# ---------------------------------------------------------------------------------------------
# captions: hand-split chunks (max 2 lines), word-level highlight, gold keywords
# '*word*' = keyword (gold). Tokens must equal the cut words exactly (asserted).
CHUNKS = """Kalau cakap pasal ubat | yang stabilkan *mood*, | ramai yang tahu ubat *litium* je. |
Tapi sebenarnya ada satu lagi ubat | yang kita boleh kata *underrated*, | tapi *power* sebenarnya, | iaitu *Lamotrigine*. |
Pernah dengar tak pasal ubat ni? | *Lamotrigine* ni dia famous | untuk stabilkan *mood*, |
especially dalam penyakit *bipolar* *disorder*. | Terutamanya dalam *episod* *kemurungan* ~lah. |
Dan risiko kenaikan *berat* *badan* | dia sangat *rendah*. | Sebab tu ramai pasien | yang suka dengan ubat ni. |
Ubat ni juga dia tak buat | rasa *mengantuk* sangat. | Jadi ramai orang masih lagi | boleh *function* macam biasa |
pada siang hari, | dan sesuai untuk *long* ~-*term* *use*, | tapi dengan *monitoring* *doktor* ~lah. | Seperti biasa, |
setiap ubat pun ada keburukan | dan *side* *effect* dia juga. | Ubat ni dia kena start | dengan *dos* *yang* *rendah*, |
*perlahan* ~-*lahan* kena *titrate* naik, | sebab ada risiko untuk | *ruam* *kulit* yang *serius*. | Kita panggil sebagai |
*Stevens* ~-*Johnson* *syndrome*. | Dia *rare*, tapi | boleh berlakulah dengan ubat ni. | Dan boleh menyebabkan *side* *effect* |
yang biasa ~lah, seperti ubat lain, | seperti *pening* *kepala*, | *loya* ataupun *susah* *tidur*. | Dan ubat ni juga |
dia tak begitu kuat | untuk rawat *fasa* *mania* tu. | Dia lebih kepada | nak *elak* *kemurungan* tu datang balik. |
Sama seperti ubat lain, | *jangan* *stop* *sendiri* | tanpa *advice* *doktor*. | Tapi kena ingat, | ubat ni juga ada |
cara guna dia yang *selamat*. | Kalau anda rasa *struggle* | dengan *mood* *swing*, | boleh set *appointment* |
dengan saya dekat *Nilai*. | Kita sembang santai dahulu | sebelum kita decide | *plan* terbaik untuk anda. |
Apa persoalan, | boleh tanya di ruang komen. | Take care."""
# display -> cut-word token (the cut words are the aligner's lowercase spellings)
ALIAS = {"stevens": "steven"}


def norm(tok: str) -> str:
    t = tok.replace("*", "").lstrip("~").lower().strip(",.?!").lstrip("-")
    return ALIAS.get(t, t)


CAP_HOSTS = []
SRT = []   # (start, end, text) for captions_ms.srt


def srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def add_captions():
    chunks = [c.strip() for c in CHUNKS.replace("\n", " ").split("|") if c.strip()]
    toks = [(ci, tok) for ci, c in enumerate(chunks) for tok in c.split()]
    assert [norm(t) for _, t in toks] == [w["text"] for w in WORDS], next(
        (k, norm(t), WORDS[k]["text"]) for k, (_, t) in enumerate(toks) if norm(t) != WORDS[k]["text"])
    by_chunk = {}
    for k, (ci, tok) in enumerate(toks):
        by_chunk.setdefault(ci, []).append((tok, WORDS[k]))
    starts = [q(by_chunk[ci][0][1]["start"] - 0.06) for ci in range(len(chunks))]
    for ci in range(len(chunks)):
        items = by_chunk[ci]
        st = starts[ci]
        last_end = items[-1][1]["end"]
        en = q(min(starts[ci + 1], last_end + 0.6)) if ci + 1 < len(chunks) else q(last_end + 0.35)
        spans = []
        for j, (tok, w) in enumerate(items):
            glue = tok.startswith("~")
            raw = tok.lstrip("~")
            kw = raw.strip(",.?!").startswith("*") or "*" in raw
            text = raw.replace("*", "")
            wid = f"c{ci}w{j}"
            spans.append(("" if glue or j == 0 else " ")
                         + f'<span class="w{" kw" if kw else ""}" id="{wid}"><span class="hl"></span><span class="tx">{html.escape(text)}</span></span>')
            hs = q(w["start"] - 0.03)
            he = q(items[j + 1][1]["start"] - 0.03) if j + 1 < len(items) else q(w["end"] + 0.05)
            JS.append(f"tl.fromTo('#{wid} .hl', {{opacity:0, scaleX:0.7}}, {{opacity:1, scaleX:1, duration:0.1, ease:'power2.out'}}, {hs});")
            JS.append(f"tl.to('#{wid} .hl', {{opacity:0, duration:0.1, ease:'power2.in'}}, {max(he, q(hs + 0.12))});")
        SRT.append((st, en, "".join(("" if t.startswith("~") or j == 0 else " ") + t.lstrip("~").replace("*", "")
                                    for j, (t, _) in enumerate(items))))
        CAP_HOSTS.append(f'<div class="cap clip" id="cap{ci}" data-start="{st}" data-duration="{round(en - st, 4)}" '
                         f'data-track-index="9"><div class="cap-in" id="cap{ci}-in">{"".join(spans)}</div></div>')
        JS.append(f"tl.fromTo('#cap{ci}-in', {{opacity:0, y:16}}, {{opacity:1, y:0, duration:0.16, ease:'power3.out'}}, {st});")
    return chunks


CSS = f"""
* {{ box-sizing:border-box; }}
html, body {{ margin:0; padding:0; width:1080px; height:1920px; overflow:hidden; background:#000;
  font-family:'Plus Jakarta Sans', sans-serif; }}
#stage {{ position:relative; width:1080px; height:1920px; overflow:hidden; background:{NAVY_D}; }}
.video-wrapper {{ position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden; transform-origin:50% 38%; }}
.video-wrapper video {{ width:100%; height:100%; object-fit:cover; }}
.gold {{ color:{GOLD}; }}
b {{ font-weight:800; }}

/* inserts */
.ins {{ position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden; pointer-events:none; }}
.ins-in {{ position:absolute; inset:0; overflow:hidden; }}
.kbv {{ position:absolute; left:0; top:0; width:1080px; height:1920px; object-fit:cover; transform-origin:50% 45%; }}
.ins-shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(6,20,43,.35) 0%, rgba(6,20,43,0) 16%,
  rgba(6,20,43,0) 52%, rgba(6,20,43,.55) 72%, rgba(6,20,43,.7) 100%); }}
.ai-tag {{ position:absolute; left:48px; top:176px; font:700 22px 'Plus Jakarta Sans'; letter-spacing:.1em; text-transform:uppercase;
  color:rgba(255,255,255,.88); background:rgba(6,20,43,.5); padding:7px 14px 6px; border-radius:10px; }}
.mg-bg {{ position:absolute; inset:0; background:radial-gradient(90% 70% at 50% 45%, transparent 55%, rgba(0,0,0,.45) 100%),
  radial-gradient(110% 70% at 70% 18%, {NAVY_L} 0%, {NAVY} 45%, {NAVY_D} 100%); }}
.mg-grid {{ position:absolute; inset:0; opacity:.5;
  background-image:linear-gradient(rgba(159,216,255,.06) 1px, transparent 1px), linear-gradient(90deg, rgba(159,216,255,.06) 1px, transparent 1px);
  background-size:60px 60px; }}
.mg-vig {{ position:absolute; inset:0; background:radial-gradient(90% 70% at 50% 45%, transparent 55%, rgba(0,0,0,.45) 100%); }}
.net, .mol, .gauge, .stair-line {{ position:absolute; left:0; top:0; width:1080px; height:1920px; }}
.net .links line {{ stroke:rgba(61,169,252,.32); stroke-width:2; }}
.net .pulses line, .mol .pulses line {{ stroke:{BLUE_S}; stroke-width:5; stroke-linecap:round; opacity:0;
  filter:drop-shadow(0 0 8px {BLUE}); }}
.net .nodes circle {{ fill:{BLUE_S}; filter:drop-shadow(0 0 10px {BLUE}); }}
.mol .bonds line {{ stroke:rgba(159,216,255,.45); stroke-width:6; }}
.mol .atoms circle {{ fill:var(--g); filter:drop-shadow(0 0 14px rgba(61,169,252,.6)); }}
.mol .atoms circle.gold {{ fill:var(--gg); filter:drop-shadow(0 0 16px rgba(226,184,87,.6)); }}
.floor {{ position:absolute; left:0; right:0; top:1040px; bottom:0; background:linear-gradient(180deg, #0B2347 0%, #040D1C 100%); }}
.tab-wrap {{ position:absolute; left:340px; top:760px; width:400px; height:400px; }}
.tab {{ position:absolute; inset:0; border-radius:50%; overflow:hidden;
  background:radial-gradient(circle at 34% 28%, #FFFFFF 0%, #EEF2F8 38%, #CBD5E2 72%, #8E9CB1 100%);
  box-shadow:inset -18px -24px 40px rgba(20,40,80,.35), inset 10px 12px 26px rgba(255,255,255,.9), 0 0 0 3px rgba(226,184,87,.55); }}
.tab-sweep {{ position:absolute; top:-20%; bottom:-20%; left:30%; width:34%; transform:rotate(18deg);
  background:linear-gradient(90deg, transparent, rgba(255,255,255,.85), transparent); }}
.tab-shadow {{ position:absolute; left:20px; right:20px; bottom:-60px; height:80px; border-radius:50%;
  background:radial-gradient(closest-side, rgba(0,0,0,.6), transparent); }}
.tab-refl {{ position:absolute; left:40px; right:40px; top:420px; height:120px; border-radius:50%;
  background:radial-gradient(closest-side, rgba(255,255,255,.14), transparent); }}
.kin {{ position:absolute; left:0; right:0; text-align:center; font-weight:800; font-size:110px; letter-spacing:.08em; text-transform:uppercase;
  color:{WHITE}; top:330px; text-shadow:0 10px 40px rgba(0,0,0,.45); }}
.kin.gold {{ top:470px; color:{GOLD}; font-size:124px; }}
.mg-head {{ position:absolute; left:80px; top:240px; width:900px; }}
.chip {{ display:inline-block; font-weight:800; font-size:28px; letter-spacing:.1em; text-transform:uppercase;
  padding:10px 22px 9px; border-radius:999px; background:rgba(226,184,87,.14); color:{GOLD}; border:2px solid rgba(226,184,87,.6); }}
.mg-title {{ font-weight:800; font-size:76px; line-height:1.05; letter-spacing:-.02em; margin-top:24px; color:{WHITE}; }}
.gticks line {{ stroke:rgba(255,255,255,.35); stroke-width:4; }}
.glabel {{ position:absolute; left:0; right:0; top:960px; text-align:center; font-weight:800; font-size:92px; color:{GOLD};
  text-transform:uppercase; letter-spacing:.03em; }}
.gsub {{ position:absolute; left:0; right:0; top:1130px; display:flex; justify-content:center; align-items:center; gap:20px;
  font-weight:700; font-size:46px; color:{WHITE}; }}
.stairs {{ position:absolute; inset:0; }}
.step {{ position:absolute; bottom:640px; width:130px; border-radius:18px 18px 6px 6px;
  background:linear-gradient(180deg, rgba(61,169,252,.95), rgba(22,58,110,.9)); box-shadow:0 0 30px rgba(61,169,252,.25); }}
.st-lab {{ position:absolute; left:84px; top:1300px; font-weight:700; font-size:36px; color:{BLUE_S}; }}
.st-word {{ position:absolute; right:200px; top:630px; font-family:'Fraunces', serif; font-weight:800; font-size:96px; color:{GOLD}; }}
.se-stack {{ position:absolute; left:80px; top:620px; width:860px; display:flex; flex-direction:column; gap:26px; }}
.se-row {{ display:flex; align-items:center; gap:30px; height:150px; padding:0 34px; border-radius:30px;
  background:linear-gradient(160deg, rgba(22,58,110,.95), rgba(11,35,71,.95)); border:2px solid rgba(159,216,255,.18);
  color:{WHITE}; font-weight:800; font-size:58px; box-shadow:0 18px 40px rgba(0,0,0,.35); }}
.disc {{ width:96px; height:96px; flex:none; border-radius:50%; display:inline-flex; align-items:center; justify-content:center;
  background:rgba(226,184,87,.16); border:2px solid rgba(226,184,87,.7); }}
.disc .ico {{ width:58px; height:58px; }}

/* cards */
.card-host, .title-host, .end-host {{ position:absolute; left:0; top:0; width:1080px; height:1920px; pointer-events:none; }}
.card-host {{ z-index:60; }} .title-host {{ z-index:70; }} .end-host {{ z-index:80; }}
.panel {{ position:absolute; left:60px; bottom:552px; width:850px; padding:26px 34px 28px 44px; border-radius:28px;
  background:linear-gradient(160deg, rgba(22,58,110,.93), rgba(6,20,43,.93)); border:1.5px solid rgba(255,255,255,.13);
  box-shadow:0 24px 60px rgba(0,0,0,.38); color:{WHITE}; overflow:hidden; }}
.panel::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:9px; background:linear-gradient(180deg, {GOLD_L}, {GOLD}); }}
.panel > * + * {{ margin-top:12px; }}
.kick {{ font-weight:800; font-size:26px; letter-spacing:.12em; text-transform:uppercase; color:{BLUE_S}; }}
.ttl {{ font-weight:800; font-size:58px; line-height:1.08; letter-spacing:-.015em; }}
.ttl.xl {{ font-size:78px; text-transform:uppercase; letter-spacing:.01em; }}
.sub {{ font-weight:600; font-size:36px; color:{MUTED}; }}
.uline {{ height:7px; width:280px; border-radius:4px; background:linear-gradient(90deg, {GOLD}, {GOLD_L}); }}
.row {{ display:flex; align-items:center; gap:18px; font-weight:700; font-size:38px; line-height:1.18; }}
.row.big {{ font-size:44px; }}
.ico {{ width:46px; height:46px; flex:none; }}
.ico.lg {{ width:56px; height:56px; }}
.ico.xl {{ width:84px; height:84px; }}
.big-row {{ display:flex; align-items:center; gap:24px; font-weight:800; font-size:54px; line-height:1.1; }}
.warnhead {{ display:flex; align-items:center; gap:12px; font-weight:800; font-size:28px; letter-spacing:.12em; text-transform:uppercase; color:{GOLD}; }}
.warnhead .ico {{ width:38px; height:38px; }}
.pgs {{ display:grid; }} .pg {{ grid-area:1/1; align-self:start; }} .pg > * + * {{ margin-top:10px; }}
#k12-pg2 .ttl {{ font-size:52px; }} #k12-pg2 .sub {{ font-size:34px; }} #k12-pg2 .safety {{ font-size:32px; }}
.safety {{ display:inline-block; font-weight:800; font-size:34px; color:{NAVY_D}; background:{GOLD}; padding:8px 18px 7px; border-radius:12px; }}
.name {{ font-family:'Fraunces', serif; font-weight:800; font-size:62px; letter-spacing:.005em; }}
.role {{ font-weight:700; font-size:30px; letter-spacing:.14em; text-transform:uppercase; color:{GOLD}; }}

/* 3D title */
.title-plate {{ position:absolute; left:60px; top:1060px; width:850px; height:300px; border-radius:28px;
  background:linear-gradient(160deg, rgba(22,58,110,.93), rgba(6,20,43,.93)); border:1.5px solid rgba(255,255,255,.13);
  box-shadow:0 24px 60px rgba(0,0,0,.38); transform-origin:50% 50%; }}
.title-wrap {{ position:absolute; left:0; top:0; width:1080px; height:300px; transform-origin:50% 50%; transform-style:preserve-3d; }}
.t3d {{ position:absolute; left:0; right:0; top:40px; text-align:center; font-family:'Fraunces', serif; font-weight:800; font-size:118px;
  letter-spacing:.01em; line-height:1; white-space:nowrap; }}
.t3d.back {{ color:{NAVY}; text-shadow:0 2px 0 #0d2a55, 0 4px 0 #0c2750, 0 6px 0 #0a2348, 0 8px 0 #091f40, 0 10px 0 #081b38,
  0 12px 0 #071830, 0 30px 50px rgba(0,0,0,.6); }}
.t3d.front {{ background:linear-gradient(100deg, {GOLD} 0%, {GOLD_L} 30%, #FFFFFF 45%, {GOLD_L} 60%, {GOLD} 100%);
  background-size:220% 100%; -webkit-background-clip:text; background-clip:text; color:transparent; }}
.t3d .ch {{ display:inline-block; }}
.title-sub {{ position:absolute; left:0; right:0; top:215px; text-align:center; font-weight:700; font-size:44px; letter-spacing:.06em;
  color:{WHITE}; text-transform:uppercase; }}
.beam {{ position:absolute; top:-10%; bottom:-10%; left:30%; width:40%; transform:rotate(14deg);
  background:linear-gradient(90deg, transparent, rgba(159,216,255,.16), transparent); }}

/* end card */
.end-bg {{ position:absolute; inset:0; background:radial-gradient(100% 70% at 50% 40%, rgba(22,58,110,.9), rgba(6,20,43,.97)); }}
.end-wrap {{ position:absolute; left:0; right:0; top:690px; text-align:center; }}
.end-t {{ font-family:'Fraunces', serif; font-weight:800; font-size:132px; line-height:1.0; color:{WHITE}; text-transform:uppercase; letter-spacing:.04em; }}
.end-line {{ width:360px; height:7px; margin:34px auto 26px; border-radius:4px; background:linear-gradient(90deg, {GOLD}, {GOLD_L}); }}
.end-name {{ font-weight:700; font-size:34px; letter-spacing:.08em; color:{MUTED}; }}

/* round 2: transitions, paper frames, new motion graphics */
.ai-tag.r {{ left:auto; right:48px; }}
.vscene {{ opacity:0; }}
.fshade {{ position:absolute; inset:0; background:linear-gradient(90deg, rgba(0,0,0,.75), rgba(0,0,0,.15)); opacity:0; pointer-events:none; z-index:8; }}
.tear-band {{ position:absolute; inset:0; z-index:9; pointer-events:none; clip-path:polygon(0% 0%, 0% 0%, 0% 0%);
  background:linear-gradient(90deg, #C9BFAC 0%, #FBF8F1 45%, #EDE5D5 100%); }}
.paper-bg {{ position:absolute; inset:0; background:radial-gradient(90% 60% at 50% 40%, {NAVY_L} 0%, {NAVY} 55%, {NAVY_D} 100%); }}
.paper-bg::after {{ content:""; position:absolute; inset:0; opacity:.10; mix-blend-mode:overlay; background-image:url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)' opacity='.55'/></svg>\"); }}
.pol {{ position:absolute; left:170px; top:200px; width:740px; height:1110px; padding:30px 30px 0; border-radius:6px;
  background:#F6F1E6; box-shadow:0 40px 90px rgba(0,0,0,.55), 0 4px 10px rgba(0,0,0,.25); }}
.pol::after {{ content:""; position:absolute; inset:0; border-radius:6px; opacity:.16; mix-blend-mode:multiply; pointer-events:none;
  background-image:url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)' opacity='.55'/></svg>\"); }}
.pol.ghost {{ background:#E4DCCB; }}
.pol-photo {{ position:relative; width:680px; height:930px; overflow:hidden; background:#000; }}
.pv {{ width:100%; height:100%; object-fit:cover; }}
.pol-label {{ font-family:'Caveat', cursive; font-weight:700; font-size:76px; line-height:1; color:#14284B; text-align:center; margin-top:34px; }}
.tape {{ position:absolute; width:190px; height:56px; top:-20px; background:rgba(236,224,190,.82); box-shadow:0 2px 8px rgba(0,0,0,.18); }}
.tape.t1 {{ left:-50px; transform:rotate(-28deg); }}
.tape.t2 {{ right:-50px; transform:rotate(26deg); }}
.tile-wrap {{ position:absolute; left:290px; top:600px; width:500px; height:560px; transform-style:preserve-3d; }}
.tile-face {{ position:absolute; inset:0; border-radius:36px; display:flex; flex-direction:column; align-items:center; justify-content:center;
  background:linear-gradient(160deg, {NAVY_L}, {NAVY}); border:6px solid {GOLD}; box-shadow:0 30px 70px rgba(0,0,0,.45);
  backface-visibility:hidden; -webkit-backface-visibility:hidden; color:{WHITE}; }}
.tile-face.back {{ transform:rotateY(180deg); }}
.tn {{ position:absolute; left:40px; top:30px; font-weight:800; font-size:58px; color:{BLUE_S}; }}
.ts {{ font-family:'Fraunces', serif; font-weight:800; font-size:250px; line-height:1; }}
.tname {{ font-weight:800; font-size:52px; margin-top:10px; letter-spacing:.02em; }}
.cal {{ position:absolute; left:190px; top:660px; width:700px; height:600px; }}
.page {{ position:absolute; inset:0; border-radius:26px; background:#F6F1E6; box-shadow:0 26px 60px rgba(0,0,0,.4); overflow:hidden; }}
.page-head {{ height:110px; background:linear-gradient(90deg, {GOLD}, {GOLD_L}); }}
.page-grid {{ position:absolute; left:40px; right:40px; top:150px; bottom:40px;
  background-image:linear-gradient(rgba(20,40,75,.18) 2px, transparent 2px), linear-gradient(90deg, rgba(20,40,75,.18) 2px, transparent 2px);
  background-size:89px 78px; }}
.rings {{ position:absolute; left:80px; right:80px; top:-26px; height:60px; z-index:30;
  background:radial-gradient(circle at 20px 30px, #C9D3E0 14px, transparent 15px) 0 0/120px 60px repeat-x; }}
.shield {{ position:absolute; left:0; top:0; width:1080px; height:1920px; }}
.sh-word {{ position:absolute; left:0; right:0; top:1255px; text-align:center; font-weight:800; font-size:64px; color:{WHITE}; }}
.wave {{ position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:visible; }}
.wave-line {{ fill:none; stroke:{BLUE_S}; stroke-width:9; stroke-linejoin:round; stroke-linecap:round; }}
.wave-glow {{ fill:none; stroke:{BLUE}; stroke-width:30; opacity:.28; filter:blur(10px); }}

/* captions */
.cap {{ position:absolute; left:70px; top:1388px; width:840px; pointer-events:none; z-index:100; }}
.cap-in {{ text-align:center; font-weight:800; font-size:58px; line-height:1.22; color:#FFFFFF; letter-spacing:-.005em;
  text-shadow:0 0 3px {NAVY_D}, 2px 2px 0 {NAVY_D}, -2px 2px 0 {NAVY_D}, 2px -2px 0 {NAVY_D}, -2px -2px 0 {NAVY_D},
  0 5px 14px rgba(0,0,0,.55); }}
.w {{ position:relative; display:inline-block; }}
.w .tx {{ position:relative; }}
.w.kw .tx {{ color:{GOLD_L}; }}
.w .hl {{ position:absolute; left:-8px; right:-8px; top:4px; bottom:2px; border-radius:12px; background:rgba(61,169,252,.92);
  opacity:0; box-shadow:0 6px 18px rgba(0,0,0,.3); }}
"""


exec((W / "scenes_v2.py").read_text(), globals())   # scene engine shares this module's helpers


def main() -> None:
    add_mgs()                 # registers weight / titrate / sidefx
    sc = add_scenes()         # round 2: B-roll + motion graphics with varied transitions (scenes_v2.py)
    add_title(sc)
    add_cards(sc)
    add_end()
    add_camera(sc)
    covered = sum(x["b"] - x["a"] for x in sc) + 1.1   # + the full-screen title slam
    print(f"non-talking-head coverage: {covered:.1f}s of {DUR:.1f}s ({100 * covered / DUR:.0f}%)")
    n_js = len(JS)
    chunks = add_captions()
    out_dir = PUB
    (W.parent / "captions_ms.srt").write_text("\n".join(f"{k + 1}\n{srt_time(a)} --> {srt_time(b)}\n{t}\n" for k, (a, b, t) in enumerate(SRT)))
    (W.parent / "transcript_final.md").write_text(
        "# Ubat Psikiatri Lamotrigine: final cut transcript\n\nTimecodes on final.mp4 (identical to the burned-in captions).\n\n"
        + "".join(f"**{int(a // 60)}:{a % 60:05.2f}** {t}  \n" for a, _, t in SRT))
    if "--clean" in sys.argv:     # caption-free deliverable: same composition, no caption layer
        del JS[n_js:]
        CAP_HOSTS.clear()
        out_dir = W / "public_clean"
        out_dir.mkdir(exist_ok=True)
        for name in ("fonts", "vendor", "broll", "input-video.mp4"):
            link = out_dir / name
            if not link.exists():
                link.symlink_to(Path("..") / "public" / name)

    fonts = "".join(
        f'@font-face{{font-family:"Plus Jakarta Sans";src:url("fonts/PlusJakartaSans-{w}.woff2") format("woff2");'
        f'font-weight:{w};font-style:normal;font-display:block;}}' for w in (500, 700, 800))
    fonts += "".join(
        f'@font-face{{font-family:"Fraunces";src:url("fonts/Fraunces-{w}.woff2") format("woff2");'
        f'font-weight:{w};font-style:normal;font-display:block;}}' for w in (600, 800))
    fonts += ('@font-face{font-family:"Caveat";src:url("fonts/Caveat-700-latin.woff2") format("woff2");'
              'font-weight:700;font-style:normal;font-display:block;}')
    page = f"""<!doctype html>
<html lang="ms">
<head>
<meta charset="utf-8" />
<style>
{fonts}
{CSS}
</style>
</head>
<body>
<div id="stage" data-composition-id="lamotrigine-reel" data-start="0" data-duration="{DUR}" data-fps="{FPS}" data-width="1080" data-height="1920">
  <div class="video-wrapper" id="video-wrap">
    <video id="bg-video" class="clip" src="input-video.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="1"></video>
  </div>
  <audio id="source-audio" src="input-video.mp4" data-start="0" data-duration="{DUR}" data-track-index="10" data-volume="1"></audio>
  {chr(10).join(INS_HOSTS)}
  {chr(10).join(CARD_HOSTS)}
  {chr(10).join(CAP_HOSTS)}
  <script src="vendor/gsap.min.js"></script>
  <script>
  (function () {{
    const tl = window.gsap.timeline({{ paused: true }});
    {(chr(10) + '    ').join(JS)}
    window.__timelines["lamotrigine-reel"] = tl;
  }})();
  </script>
</div>
</body>
</html>
"""
    (out_dir / "index.html").write_text(page)
    if out_dir != PUB:
        print(f"clean build -> {out_dir / 'index.html'}")
        return
    (W / "storyboard.json").write_text(json.dumps({"durationSeconds": DUR, "fps": FPS, "items": sorted(STORY, key=lambda x: x["start"]),
                                                   "captions": chunks}, indent=1, ensure_ascii=False))
    (W / "sfx_cues.json").write_text(json.dumps(sorted(SFX, key=lambda x: x["t"]), indent=1))
    br = [x for x in STORY if x["kind"].startswith("broll")]
    print(f"duration {DUR}s | {len(br)} B-roll slots ({sum(1 for x in br if x['source'].endswith('.mp4'))} delivered) | "
          f"{sum(1 for x in STORY if x['kind'] == 'motion-graphic')} MGs | {sum(1 for x in STORY if x['kind'] == 'card')} cards | "
          f"{len(chunks)} caption chunks | {len(JS)} timeline statements | {len(SFX)} SFX cues")


if __name__ == "__main__":
    main()
