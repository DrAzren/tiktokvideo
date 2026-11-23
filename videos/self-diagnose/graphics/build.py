"""Generate the HyperFrames composition for 'Self Diagnose' (1080x1920 @ 30fps).

One composition, bottom to top:
  1. cut.mp4 upscaled (public/input-video.mp4)
  2. headroom cards (y 140-370: the hair line sits at ~y 400)
  3. full-screen inserts: AI B-roll (3 Gemini clips, 3 stills with a cubic Ken Burns) and motion graphics
  4. one-line captions at y~1420 (below the chin, above TikTok's bottom UI, clear of the right rail)

All times are seconds on the cut timeline and come from edit/cut_words.json (W[i] = start of word i),
so the graphics follow the words if the cut is rebuilt with the same word list.

Outputs: public/index.html, captions_ms.srt, sfx_events.json
"""

import html
import json
from pathlib import Path

G = Path(__file__).parent
PUB = G / "public"
FPS = 30
DUR = 2900 / FPS            # cut.mp4 = 96.68s -> 2900 whole frames
WORDS = json.loads((G.parent / "edit" / "cut_words.json").read_text())
W = [w["start"] for w in WORDS]
PS = 1.14                   # headroom panels are authored at 840px wide and scaled up to fill 60..1018
LEAD = 0.10                 # motion starts this early so it lands on the word

TEAL, DEEP, CREAM, INK, AMBER, RED, MINT, MUTED = (
    "#0E5E6F", "#06232B", "#FFF8EE", "#0B1F2A", "#F5A524", "#E5484D", "#5EEAD4", "#6B7C85")


def f(t: float) -> float:
    return round(round(t * FPS) / FPS, 4)


tl: list[str] = []          # GSAP timeline statements
body: list[str] = []
sfx: list[dict] = []        # {"t": s, "kind": whoosh|pop|impact|tick|rise}


def anim(sel: str, kind: str, at: float, **kw) -> None:
    at = f(max(0, at - LEAD))
    if kind == "pop":
        tl.append(f"tl.fromTo('{sel}',{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.34,ease:'back.out(1.8)'}},{at});")
        sfx.append({"t": at, "kind": "pop"})
    elif kind == "slide":
        tl.append(f"tl.fromTo('{sel}',{{opacity:0,x:{kw.get('x', -44)}}},{{opacity:1,x:0,duration:0.4,ease:'power3.out'}},{at});")
        sfx.append({"t": at, "kind": "tick"})
    elif kind == "rise":
        tl.append(f"tl.fromTo('{sel}',{{opacity:0,y:{kw.get('y', 40)}}},{{opacity:1,y:0,duration:0.42,ease:'power3.out'}},{at});")
    elif kind == "fade":
        tl.append(f"tl.fromTo('{sel}',{{opacity:0}},{{opacity:1,duration:0.3,ease:'power2.out'}},{at});")
    elif kind == "stamp":
        r = kw.get("rot", -6)
        tl.append(f"tl.fromTo('{sel}',{{opacity:0,scale:2.3,rotation:{r - 10}}},{{opacity:1,scale:1,rotation:{r},duration:0.26,ease:'power4.in'}},{at});")
        sfx.append({"t": at + 0.24, "kind": "impact"})
    elif kind == "draw":
        d = kw.get("d", 0.8)
        tl.append(f"tl.fromTo('{sel}',{{strokeDashoffset:{kw['len']}}},{{strokeDashoffset:0,duration:{d},ease:'power2.inOut'}},{at});")
    elif kind == "dim":
        tl.append(f"tl.to('{sel}',{{opacity:{kw.get('to', 0.35)},duration:0.3,ease:'power2.out'}},{at});")
    else:
        raise ValueError(kind)


# ---------------------------------------------------------------- cards (headroom)
def card(cid: str, start: float, end: float, inner: str, height: int = 220, bare: bool = False) -> None:
    start, end = f(start), f(end)
    cls = "bare" if bare else "panel"
    body.append(
        f'<div id="card-{cid}" class="clip card-host" data-start="{start}" data-duration="{round(end - start, 4)}" '
        f'data-track-index="2"><div class="{cls}" id="{cid}" style="height:{height}px">{inner}</div></div>')
    tl.append(f"tl.fromTo('#{cid}',{{opacity:0,y:-36,scale:{0.97 * PS:.3f}}},{{opacity:1,y:0,scale:{PS},duration:0.42,ease:'power3.out'}},{start});")
    tl.append(f"tl.to('#{cid}',{{opacity:0,y:-22,duration:0.24,ease:'power2.in'}},{f(end - 0.27)});")
    sfx.append({"t": start, "kind": "whoosh"})


def chip(text: str, color: str = TEAL) -> str:
    return f'<span class="chip" style="background:{color}">{html.escape(text)}</span>'


CROSS = f'<svg viewBox="0 0 24 24" class="ico"><circle cx="12" cy="12" r="11" fill="{RED}"/><path d="M8 8l8 8M16 8l-8 8" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/></svg>'
CHECK = f'<svg viewBox="0 0 24 24" class="ico"><circle cx="12" cy="12" r="11" fill="{TEAL}"/><path d="M7 12.5l3.2 3.2L17.5 8.5" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'
WARN = f'<svg viewBox="0 0 24 24" class="ico"><path d="M12 2.5L23 21.5H1z" fill="{AMBER}"/><path d="M12 9v6" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/><circle cx="12" cy="18" r="1.4" fill="{INK}"/></svg>'
ARROW = f'<svg viewBox="0 0 24 24" class="ico"><path d="M4 12h15M12.5 5.5L19 12l-6.5 6.5" stroke="{TEAL}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# 1. HOOK — kinetic type, no panel
ECG = "M0 60 H250 l22 -12 l22 12 h40 l18 -50 l26 104 l24 -84 l16 30 h70 l22 -12 l22 12 H960"
card("hookA", 0.0, 2.42, f'''
  <div class="kin a" id="hk1">JANTUNG</div>
  <div class="kin amber a" id="hk2">NAK MELETUP</div>
  <svg class="ecg" viewBox="0 0 960 120"><path id="hkecg" d="{ECG}" fill="none" stroke="{RED}" stroke-width="7"
     stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="1400" stroke-dashoffset="1400"/></svg>''', 250, bare=True)
anim("#hk1", "pop", W[3]); anim("#hk2", "stamp", W[6], rot=-3); anim("#hkecg", "draw", W[6] + 0.15, len=1400, d=0.9)
card("hookB", 2.45, 4.42, '''
  <div class="kin sm a" id="hk3">DIA YAKIN</div>
  <div class="kin a" id="hk4">DIA AKAN <span style="color:#E5484D">MATI</span></div>''', 250, bare=True)
anim("#hk3", "rise", W[9]); anim("#hk4", "stamp", W[12] + 0.1, rot=0)

# 2. ID + disclaimer
card("id", 4.5, 9.33, f'''
  <div class="a" id="id1">{chip("Dr Azren")}<span class="tag">Kesihatan mental</span></div>
  <div class="title a" id="id2">Satu malam, saya on-call…</div>
  <div class="row a" id="id3">{ARROW}<span>Remaja, <b style="color:{TEAL}">17 tahun</b></span></div>
  <div class="fine a" id="id4">Kisah diubah suai untuk melindungi identiti.</div>''', 226)
anim("#id1", "pop", 4.6); anim("#id2", "slide", W[16]); anim("#id3", "slide", W[24]); anim("#id4", "fade", 5.4)

# 3. pucat
card("pucat", W[37], 13.97, f'''
  <div class="label a" id="pc1">Bila sampai…</div>
  <div class="grid"><span class="pill big a" id="pc2">Sangat pucat</span></div>''', 170)
anim("#pc1", "fade", W[37] + 0.1); anim("#pc2", "pop", W[40])

# 4. takut berbulan
dots = "".join(f'<span class="dot a" id="tk-d{i}"></span>' for i in range(5))
card("takut", W[55], 23.83, f'''
  <div class="a" id="tk1">{chip("Dia beritahu", TEAL)}</div>
  <div class="title a" id="tk2">Sering rasa <span style="color:{RED}">takut</span></div>
  <div class="row a" id="tk3"><span class="sub">Sejak beberapa bulan</span><span class="dots">{dots}</span></div>''', 222)
anim("#tk1", "pop", W[58]); anim("#tk2", "slide", W[61]); anim("#tk3", "fade", W[64])
for i in range(5):
    anim(f"#tk-d{i}", "pop", W[65] + i * 0.12)

# 5. tak pernah jumpa doktor
card("nodoc", W[95], 35.3, f'''
  <div class="title a" id="nd1">Jumpa doktor?</div>
  <div class="stampwrap"><span class="stamp a" id="nd2">TAK PERNAH</span></div>
  <div class="row a" id="nd3">{CROSS}<span>Tiada rawatan profesional</span></div>''', 190)
anim("#nd1", "slide", W[95] + 0.1); anim("#nd2", "stamp", W[98]); anim("#nd3", "slide", W[104])

# 6. self-diagnose
card("selfdx", W[106], 39.37, f'''
  <div class="title xl a" id="sd1" style="color:{TEAL}">SELF-DIAGNOSE</div>
  <div class="row a" id="sd2"><span class="plus">+</span><span>cari <i>solution</i> sendiri</span></div>''', 200)
anim("#sd1", "pop", W[107]); anim("#sd2", "slide", W[111])

# 7. tiada perubahan
card("noeffect", W[133], 47.3, f'''
  <div class="label a" id="ne1">Supplement dari media sosial</div>
  <div class="row big a" id="ne2">{CROSS}<span>Tiada perubahan positif</span></div>''', 170)
anim("#ne1", "fade", W[133] + 0.1); anim("#ne2", "slide", W[136])

# 8. semakin teruk — rising bars
bars = "".join(f'<span class="bar a" id="wr-b{i}" style="height:{28 + i * 22}px;background:{RED if i > 2 else AMBER}"></span>' for i in range(5))
card("worse", W[142], 50.47, f'''
  <div class="a" id="wr1">{chip("Malam itu", RED)}</div>
  <div class="title a" id="wr2">Serangan<br>semakin <span style="color:{RED}">teruk</span></div>
  <div class="bars">{bars}</div>''', 220)
anim("#wr1", "pop", W[143]); anim("#wr2", "slide", W[145])
for i in range(5):
    anim(f"#wr-b{i}", "rise", W[150] + i * 0.11, y=30)
sfx.append({"t": f(W[150]), "kind": "rise"})

# 9. assessment
card("assess", W[152], 53.87, f'''
  <div class="a" id="as1">{chip("Di hospital")}</div>
  <div class="row big a" id="as2">{CHECK}<span>Penilaian oleh doktor</span></div>''', 170)
anim("#as1", "pop", W[152] + 0.1); anim("#as2", "slide", W[155])

# 10. spiral
card("spiral", W[167], 62.8, f'''
  <div class="steps"><span class="step a" id="sp1">Asingkan diri</span><span class="sep a" id="sp2">+</span>
    <span class="step a" id="sp3">Maklumat tak sahih</span></div>
  <div class="row big a" id="sp4"><svg viewBox="0 0 24 24" class="ico"><path d="M12 4v15M5.5 12.5L12 19l6.5-6.5" stroke="{RED}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
    <span style="color:{RED}">Keadaan makin buruk</span></div>''', 230)
anim("#sp1", "pop", W[170]); anim("#sp2", "fade", W[172]); anim("#sp3", "pop", W[175]); anim("#sp4", "slide", W[180])

# 11. bahaya
card("danger", W[183], 64.73, f'''
  <div class="title a" id="dg1" style="font-size:62px">Self-diagnose</div>
  <div class="stampwrap mid"><span class="stamp big a" id="dg2">BAHAYA</span></div>''', 150)
anim("#dg1", "slide", W[183] + 0.1); anim("#dg2", "stamp", W[186])

# 12. salah faham + rawatan salah
card("wrong", W[200], 73.6, f'''
  <div class="label a" id="wg1">Self-diagnose boleh bawa kepada</div>
  <div class="row big a" id="wg2">{WARN}<span>Salah faham</span></div>
  <div class="row big a" id="wg3">{WARN}<span>Rawatan yang salah</span></div>''', 222)
anim("#wg1", "fade", W[201]); anim("#wg2", "slide", W[203]); anim("#wg3", "slide", W[206])

# 13. rawatan awal
card("early", W[212], 80.5, f'''
  <div class="title a" id="er1">Rawatan <span style="color:{TEAL}">awal</span> itu penting</div>
  <div class="row a" id="er2">{ARROW}<span>Boleh elak serangan panik<br>yang lebih teruk</span></div>''', 210)
anim("#er1", "pop", W[214]); anim("#er2", "slide", W[225])

# 14. keluarga
card("family", W[231], 83.13, f'''
  <div class="a" id="fm1">{chip("Keluarga")}</div>
  <div class="title a" id="fm2">Peranan yang <span style="color:{TEAL}">besar</span></div>
  <div class="row a" id="fm3">{CHECK}<span>Sokongan ibu bapa</span></div>''', 222)
anim("#fm1", "pop", W[231] + 0.1); anim("#fm2", "slide", W[233]); anim("#fm3", "slide", W[236])

# 15. jangan takut
card("help", W[250], 93.27, f'''
  <div class="label a" id="hp1">Ada gejala seperti ini?</div>
  <div class="title xl a" id="hp2" style="color:{TEAL}">Jangan takut</div>
  <div class="row a" id="hp3">{CHECK}<span>Dapatkan bantuan profesional</span></div>''', 226)
anim("#hp1", "fade", W[255]); anim("#hp2", "pop", W[260]); anim("#hp3", "slide", W[263])

# 16. end card
card("end", W[267], DUR, f'''
  <div class="title a" id="en1">Ada soalan?</div>
  <div class="row a" id="en2">{ARROW}<span>Tulis di ruangan komen</span></div>
  <div class="a" id="en3">{chip("Dr Azren")}<span class="tag">Ikuti untuk info kesihatan mental</span></div>''', 226)
anim("#en1", "pop", W[269]); anim("#en2", "slide", W[273]); anim("#en3", "fade", W[275])
tl[:] = [s for s in tl if "'#end',{opacity:0,y:-22" not in s]   # the end card stays to the last frame


# ---------------------------------------------------------------- full-screen inserts
def insert(iid: str, start: float, end: float, inner: str, mg: bool = False, clear: bool = False) -> None:
    start, end = f(start), f(end)
    body.append(
        f'<div id="ins-{iid}" class="clip ins" data-start="{start}" data-duration="{round(end - start, 4)}" '
        f'data-track-index="3"><div class="ins-in{" mg" if mg else ""}{" clear" if clear else ""}" id="{iid}">{inner}</div></div>')
    if clear:   # overlay of a hard-cut video: no scale, quick fade
        tl.append(f"tl.fromTo('#{iid}',{{opacity:0}},{{opacity:1,duration:0.12,ease:'power2.out'}},{start});")
    else:
        tl.append(f"tl.fromTo('#{iid}',{{opacity:0,scale:1.06}},{{opacity:1,scale:1,duration:0.3,ease:'power3.out'}},{start});")
        tl.append(f"tl.to('#{iid}',{{opacity:0,duration:0.2,ease:'power2.in'}},{f(end - 0.22)});")
    sfx.append({"t": start, "kind": "whoosh"})


AI = '<div class="ai-tag">Ilustrasi AI</div>'


def broll_video(iid: str, start: float, end: float, src: str, label: str = "", label_at: float = 0) -> None:
    start, end = f(start), f(end)
    lab = f'<div class="blabel a" id="{iid}-lb">{html.escape(label)}</div>' if label else ""
    # a <video> takes no timing from a wrapper: it is a direct child of the root (straight cut in/out),
    # and the shade/tag/label ride in their own clip on top
    body.append(f'<video id="{iid}-v" class="kb" src="broll/{src}" muted playsinline data-start="{start}" '
                f'data-duration="{round(end - start, 4)}" data-track-index="4"></video>')
    insert(iid, start, end, f'<div class="shade"></div>{AI}{lab}', clear=True)
    if label:
        anim(f"#{iid}-lb", "rise", label_at or start + 0.4)


def broll_still(iid: str, start: float, end: float, src: str, frm: dict, to: dict, label: str = "", label_at: float = 0) -> None:
    lab = f'<div class="blabel a" id="{iid}-lb">{html.escape(label)}</div>' if label else ""
    insert(iid, start, end, f'<img id="{iid}-img" class="kb" src="broll/{src}"><div class="shade"></div>{AI}{lab}')
    d = round(f(end) - f(start), 4)
    tl.append(f"tl.fromTo('#{iid}-img',{json.dumps(frm)},{{...{json.dumps(to)},duration:{d},ease:'power2.out'}},{f(start)});")
    if label:
        anim(f"#{iid}-lb", "rise", label_at or start + 0.4)


broll_video("er", W[28], 12.13, "er_30.mp4", "Jabatan Kecemasan", W[35])
broll_still("hands", W[41] - 0.1, 15.43, "hands.jpg", {"scale": 1.0, "x": -60, "y": -40}, {"scale": 1.12, "x": -110, "y": -90},
            "Menggigil", W[41])
broll_video("phone", W[68], W[68] + 2.97, "phone_30.mp4", "Baca simptom di media sosial", W[72])
broll_still("room", W[115], 41.2, "room.jpg", {"scale": 1.14, "x": 0, "y": -60}, {"scale": 1.0, "x": 0, "y": 0},
            "Tak keluar rumah langsung", W[116])
broll_still("supp", W[125], 45.3, "supp.jpg", {"scale": 1.0, "x": 40, "y": 0}, {"scale": 1.13, "x": -30, "y": -40},
            "Supplement dari media sosial", W[126])
broll_video("consult", W[239], W[239] + 2.97, "consult_30.mp4", "Langkah penting dalam pemulihan", W[244])

# MG1 — symptoms on a body silhouette
BODY = ('<path d="M540 600a130 130 0 1 1 0.1 0zM260 1250c0-330 70-570 280-570s280 240 280 570z" fill="#0B3F4B" '
        'stroke="#5EEAD4" stroke-opacity=".35" stroke-width="3"/>')
insert("mgsym", W[44] - 0.05, 17.55, f'''
  <div class="mg-chip a" id="sy0">Simptom malam itu</div>
  <svg class="mgsvg" viewBox="0 0 1080 1300">{BODY}
    <g id="sy-lung" class="a"><path d="M470 790c-70 20-110 120-100 250 60 20 110 0 110-60zM610 790c70 20 110 120 100 250-60 20-110 0-110-60z"
       fill="none" stroke="{MINT}" stroke-width="8" stroke-linejoin="round"/><circle id="sy-ring" cx="540" cy="900" r="150" fill="none" stroke="{MINT}" stroke-width="4" opacity=".0"/></g>
    <g id="sy-heart" class="a" style="transform-origin:575px 880px"><path d="M575 930c-70-50-90-90-60-120 24-22 50-10 60 12 10-22 36-34 60-12 30 30 10 70-60 120z" fill="{RED}"/></g>
  </svg>
  <div class="mg-tags"><span class="mtag a" id="sy1">Pucat</span><span class="mtag a" id="sy2">Menggigil</span></div>
  <div class="callout left a" id="sy3">Sesak nafas</div>
  <div class="callout right red a" id="sy4">Sakit dada</div>''', mg=True)
anim("#sy0", "pop", W[44]); anim("#sy1", "fade", W[44] + 0.15); anim("#sy2", "fade", W[44] + 0.3)
anim("#sy-lung", "fade", W[45]); anim("#sy3", "slide", W[45], x=-60)
anim("#sy-heart", "pop", W[47]); anim("#sy4", "slide", W[47], x=60)
tl.append(f"tl.fromTo('#sy-ring',{{opacity:0.7,scale:0.6,transformOrigin:'540px 900px'}},{{opacity:0,scale:1.5,duration:0.9,ease:'power2.out'}},{f(W[45])});")
tl.append(f"tl.to('#sy-heart',{{scale:1.22,duration:0.12,ease:'power2.inOut',yoyo:true,repeat:3}},{f(W[48] + 0.1)});")

# MG2 — the three labels from social media
feed = "".join(f'<div class="feed" id="fd{i}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"></div>'
               for i, (x, y, w, h) in enumerate([(70, 260, 300, 380), (720, 200, 290, 330), (90, 900, 260, 300), (740, 820, 270, 360)]))
HEAD = ('<path d="M540 520a150 150 0 1 1 0.1 0zM230 1300c0-420 90-720 310-720s310 300 310 720z" fill="#0B3F4B" '
        'stroke="#5EEAD4" stroke-opacity=".35" stroke-width="3"/>')
insert("mglabels", W[78], 32.47, f'''{feed}
  <div class="mg-chip a" id="lb0">Dia yakin dia ada…</div>
  <svg class="mgsvg" viewBox="0 0 1080 1300">{HEAD}</svg>
  <div class="note a" id="lb1" style="left:70px;top:470px">Borderline<br>Personality<br>Disorder</div>
  <div class="note n2 a" id="lb2" style="left:610px;top:610px">Major<br>Depressive<br>Disorder</div>
  <div class="note n3 a" id="lb3" style="left:330px;top:900px">ADHD</div>
  <div class="mg-foot a" id="lb4">…daripada apa yang dibaca di media sosial</div>''', mg=True)
anim("#lb0", "pop", W[80])
anim("#lb1", "stamp", W[84], rot=-7); anim("#lb2", "stamp", W[87], rot=5); anim("#lb3", "stamp", W[91], rot=-3)
anim("#lb4", "fade", W[91] + 0.35)
for i in range(4):
    tl.append(f"tl.fromTo('#fd{i}',{{y:{60 + i * 20}}},{{y:{-80 - i * 30},duration:5.4,ease:'power1.out'}},{f(W[78])});")

# MG3 — reveal
insert("mgreveal", W[158], 57.17, f'''
  <div class="mg-chip dim a" id="rv0">Sangkaan sendiri</div>
  <div class="mini-notes"><span class="mnote a" id="rv1">BPD ?</span><span class="mnote a" id="rv2">MDD ?</span><span class="mnote a" id="rv3">ADHD ?</span></div>
  <div class="mg-chip mint a" id="rv4" style="top:640px">Penilaian doktor</div>
  <div class="reveal a" id="rv5">ANXIETY<br>DISORDER</div>
  <svg class="underline" viewBox="0 0 800 30"><path id="rv6" d="M10 18 C200 4 600 4 790 16" fill="none" stroke="{AMBER}" stroke-width="10" stroke-linecap="round" stroke-dasharray="800" stroke-dashoffset="800"/></svg>
  <div class="mg-foot a" id="rv7" style="top:1160px">yang sangat serius</div>''', mg=True)
anim("#rv0", "fade", W[158] + 0.1)
for i in (1, 2, 3):
    anim(f"#rv{i}", "pop", W[158] + 0.1 + i * 0.14)
anim("#rv4", "pop", W[161])
for i in (1, 2, 3):
    anim(f"#rv{i}", "dim", W[162])
anim("#rv5", "stamp", W[162] + 0.1, rot=0); anim("#rv6", "draw", W[163] + 0.3, len=800, d=0.5); anim("#rv7", "fade", W[165])

# MG4 — internet vs professional assessment
rows = "".join(f'<div class="crow a" id="cp-r{i}">{CHECK}<span>{t}</span></div>'
               for i, t in enumerate(["Temu bual dengan doktor", "Sejarah &amp; latar belakang", "Diagnosis &amp; pelan rawatan"]))
insert("mgcompare", W[189], 69.3, f'''
  <div class="half top a" id="cp1"><div class="hlabel">Baca simptom di internet</div>
    <div class="search"><svg viewBox="0 0 24 24" width="46" height="46"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="{MUTED}" stroke-width="2.6"/><path d="M15.5 15.5L21 21" stroke="{MUTED}" stroke-width="2.6" stroke-linecap="round"/></svg>
      <span class="typed" id="cp-type">kenapa saya selalu rasa takut</span></div>
    <div class="res a" id="cp-s1"></div><div class="res w2 a" id="cp-s2"></div><div class="res w3 a" id="cp-s3"></div></div>
  <div class="neq a" id="cp2">≠</div>
  <div class="half bot a" id="cp3"><div class="hlabel teal">Penilaian profesional</div>{rows}</div>''', mg=True)
anim("#cp1", "rise", W[190], y=-50)
tl.append(f"tl.fromTo('#cp-type',{{clipPath:'inset(0 100% 0 0)'}},{{clipPath:'inset(0 0% 0 0)',duration:0.9,ease:'power1.inOut'}},{f(W[190] + 0.15)});")
for i in (1, 2, 3):
    anim(f"#cp-s{i}", "fade", W[192] + i * 0.14)
anim("#cp2", "stamp", W[195], rot=0); anim("#cp3", "rise", W[198], y=50)
for i in range(3):
    anim(f"#cp-r{i}", "slide", W[198] + 0.25 + i * 0.28)


# ---------------------------------------------------------------- captions
# One token per aligned word. "_" = absorbed into the previous token, "^" = highlight, "/" = line break.
CAPS = """Dia rasa macam ^jantung / dia nak ^meletup, / dan dia yakin yang / dia akan ^mati. /
Ketika saya bertugas / sebagai doktor ^on-call, _ / ada seorang remaja / umur ^17 _ tahun /
yang dibawa oleh / kedua ibu bapanya / ke ^Jabatan ^Kecemasan. / Dia kelihatan sangat ^pucat, / ^menggigil tangan dia, /
mengadu ^sesak ^nafas, / ^sakit ^dada. / Mak ayah dia pun / nampak cemas. / Remaja tersebut ada beritahu /
yang dia sering rasa ^takut / sejak beberapa bulan lepas. / Dia ada baca di / ^media ^sosial / tentang gejala yang dialami. /
Remaja itu yakin / yang dia alami / ^Borderline ^Personality ^Disorder, / ^Major ^Depressive ^Disorder / dan ^ADHD. _ _ _ /
Tapi dia tak pernah / jumpa ^doktor pun / untuk dapatkan / ^rawatan ^profesional. / Dia ^self-diagnose _ sendiri /
dan cari solution sendiri, / termasuklah dia / ^tak ^keluar ^rumah langsung. / Dia juga ada try / untuk ambil ^supplement /
yang ada jual / dekat media sosial, / tapi tak ada / ^perubahan yang ^positif / pun yang berlaku. / Jadi malam itu, serangan /
yang dia alami itu / ^semakin ^teruk. / Selepas saya buat ^assessment, / kita dapati yang / remaja tersebut mengalami /
^anxiety ^disorder / yang sangat serius. / Tindakan dia yang / ^mengasingkan ^diri / atau bergantung kepada /
^maklumat yang ^tak ^sahih itu / ^burukkan lagi keadaan. / ^Self-diagnose _ sangat ^bahaya / untuk kita, /
sebab baca simptom / dekat internet ini / ^tak ^sama dengan / ^penilaian ^profesional. / Dia boleh menyebabkan / ^salah ^faham /
dan ^rawatan yang ^salah / dekat diri kita. / ^Rawatan yang ^awal / itu penting. / Kalau remaja tersebut / dapat rawatan awal, /
dia boleh mengelakkan / ^serangan ^panik / yang lebih teruk. / ^Keluarga memainkan / peranan yang ^besar. /
^Sokongan ibu bapa / bawa dia datang hospital / adalah ^langkah ^penting / dalam proses ^pemulihan dia. /
Jika anda atau / orang terdekat / mengalami gejala-gejala _ / seperti ini, / ^jangan ^takut / untuk dapatkan ^bantuan /
yang sepatutnya. / Apa-apa _ soalan, / boleh tanya di / ^ruangan ^komen. / Take care."""


def caption_lines() -> list[dict]:
    lines, k = [], 0
    for raw in CAPS.replace("\n", " ").split("/"):
        toks = raw.split()
        if not toks:
            continue
        first, last = k, k + len(toks) - 1
        lines.append({"toks": [t for t in toks if t != "_"], "start": WORDS[first]["start"], "end": WORDS[last]["end"]})
        k += len(toks)
    assert k == len(WORDS), (k, len(WORDS))
    for a, b in zip(lines, lines[1:]):       # hold each line until the next one, unless there is a real pause
        a["out"] = b["start"] if b["start"] - a["end"] < 0.9 else a["end"] + 0.35
    lines[-1]["out"] = min(DUR, lines[-1]["end"] + 1.2)
    return lines


LINES = caption_lines()
for i, ln in enumerate(LINES):
    s, e = f(max(0, ln["start"] - 0.04)), f(ln["out"] - 0.04)
    spans = " ".join(f'<span class="hl">{html.escape(t[1:])}</span>' if t.startswith("^") else html.escape(t) for t in ln["toks"])
    body.append(f'<div id="cap-{i}" class="clip cap" data-start="{s}" data-duration="{round(e - s, 4)}" data-track-index="6">'
                f'<div class="capin" id="capin-{i}">{spans}</div></div>')
    tl.append(f"tl.fromTo('#capin-{i}',{{opacity:0,y:16,scale:0.96}},{{opacity:1,y:0,scale:1,duration:0.14,ease:'power3.out'}},{s});")


def srt_time(t: float) -> str:
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


# SRT: two caption lines per cue, plain text
cues = []
for i in range(0, len(LINES), 2):
    grp = LINES[i:i + 2]
    cues.append((grp[0]["start"], grp[-1]["out"] - 0.04, "\n".join(" ".join(t.lstrip("^") for t in g["toks"]) for g in grp)))
(G / "captions_ms.srt").write_text("".join(f"{n}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n\n" for n, (a, b, txt) in enumerate(cues, 1)))
(G / "sfx_events.json").write_text(json.dumps(sorted(sfx, key=lambda e: e["t"]), indent=0))

# ---------------------------------------------------------------- page
FONT = "".join(f'@font-face{{font-family:"Plus Jakarta Sans";src:url("fonts/PlusJakartaSans-{w}.woff2") format("woff2");'
               f'font-weight:{w};font-style:normal;font-display:block;}}' for w in (500, 700, 800))
CSS = FONT + f"""
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0;width:1080px;height:1920px;overflow:hidden;background:#000;font-family:"Plus Jakarta Sans",sans-serif}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}}
#bg,video.kb{{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover}}
.a{{opacity:0}}
.card-host,.ins,.cap{{position:absolute;left:0;top:0;width:1080px;height:1920px;pointer-events:none}}
.panel{{position:absolute;left:60px;top:128px;width:840px;transform-origin:left top;background:{CREAM};border-radius:32px;padding:24px 36px 24px 46px;color:{INK};
  box-shadow:0 22px 60px rgba(8,22,30,.34);overflow:hidden;display:flex;flex-direction:column;justify-content:center;gap:10px}}
.panel::before{{content:"";position:absolute;left:0;top:0;bottom:0;width:12px;background:{TEAL}}}
.bare{{position:absolute;left:60px;top:120px;width:960px;display:flex;flex-direction:column;align-items:flex-start;gap:0}}
.kin{{font-weight:800;font-size:112px;line-height:.98;letter-spacing:-.02em;color:#fff;transform-origin:left center;
  text-shadow:0 6px 0 rgba(0,0,0,.35),0 10px 34px rgba(0,0,0,.55)}}
.kin.amber{{color:{AMBER}}} .kin.sm{{font-size:78px}}
.ecg{{position:absolute;left:0;top:206px;width:960px;height:120px;filter:drop-shadow(0 4px 10px rgba(0,0,0,.5))}}
.chip{{display:inline-block;color:#fff;font-weight:800;font-size:28px;letter-spacing:.07em;text-transform:uppercase;padding:8px 18px 7px;border-radius:999px}}
.tag{{font-weight:700;font-size:28px;color:{MUTED};margin-left:14px;letter-spacing:.02em}}
.title{{font-weight:800;font-size:54px;line-height:1.06;letter-spacing:-.015em}}
.title.xl{{font-size:84px;letter-spacing:-.025em;line-height:1}}
.sub{{font-weight:700;font-size:36px;color:#44525A}}
.label{{font-weight:700;font-size:30px;color:#44525A;text-transform:uppercase;letter-spacing:.06em}}
.fine{{font-weight:500;font-size:22px;color:{MUTED}}}
.row{{display:flex;align-items:center;gap:16px;font-weight:700;font-size:38px;line-height:1.14}}
.row.big{{font-size:46px;font-weight:800}}
.ico{{width:42px;height:42px;flex:none}}
.plus{{color:{TEAL};font-weight:800;font-size:46px;line-height:1}}
.grid{{display:flex;gap:14px}}
.pill{{display:inline-block;font-weight:800;font-size:36px;padding:12px 26px;border-radius:18px;background:#E3F4F1;color:{TEAL};border:2px solid rgba(14,94,111,.25)}}
.pill.big{{font-size:50px}}
.dots{{display:inline-flex;gap:10px;margin-left:8px}} .dot{{width:22px;height:22px;border-radius:50%;background:{TEAL}}}
.bars{{position:absolute;right:40px;bottom:26px;display:flex;align-items:flex-end;gap:10px}} .bar{{width:26px;border-radius:7px 7px 0 0}}
.steps{{display:flex;align-items:center;flex-wrap:wrap;gap:12px;font-weight:800;font-size:38px}}
.step{{display:inline-block;padding:9px 20px;border-radius:16px;background:#E3F4F1;color:{TEAL}}} .sep{{color:{MUTED}}}
.stampwrap{{position:absolute;right:34px;top:22px}} .stampwrap.mid{{top:30px;right:30px}}
.stamp{{display:inline-block;border:6px solid {RED};color:{RED};border-radius:14px;font-weight:800;font-size:44px;letter-spacing:.04em;
  padding:6px 18px 2px;background:rgba(255,248,238,.94)}} .stamp.big{{font-size:64px}}
.ins-in{{position:absolute;inset:0;overflow:hidden;background:#000;opacity:0}} .ins-in.clear{{background:none}}
.kb{{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover}}
img.kb{{left:-108px;top:-192px;width:1296px;height:2304px}}
.shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.42) 0%,rgba(0,0,0,0) 20%,rgba(0,0,0,0) 62%,rgba(0,0,0,.55) 80%,rgba(0,0,0,.55) 100%)}}
.ai-tag{{position:absolute;left:48px;top:150px;font-weight:700;font-size:24px;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.92);
  background:rgba(0,0,0,.42);padding:7px 14px 6px;border-radius:10px}}
.blabel{{position:absolute;left:48px;top:210px;max-width:860px;font-weight:800;font-size:58px;line-height:1.05;letter-spacing:-.015em;color:#fff;
  text-shadow:0 4px 0 rgba(0,0,0,.35),0 8px 30px rgba(0,0,0,.6)}}
.mg{{background:radial-gradient(120% 80% at 78% 8%,{TEAL} 0%,#08323C 58%,{DEEP} 100%);color:{CREAM}}}
.mgsvg{{position:absolute;left:0;top:140px;width:1080px;height:1300px}}
.mg-chip{{position:absolute;left:60px;top:150px;font-weight:800;font-size:44px;letter-spacing:.02em;color:{DEEP};background:{CREAM};padding:14px 28px 12px;border-radius:18px}}
.mg-chip.dim{{background:rgba(255,248,238,.16);color:{CREAM}}} .mg-chip.mint{{background:{MINT}}}
.mg-foot{{position:absolute;left:60px;top:1250px;width:900px;font-weight:700;font-size:46px;color:rgba(255,248,238,.82)}}
.mg-tags{{position:absolute;left:60px;top:256px;display:flex;gap:14px}}
.mtag{{font-weight:700;font-size:34px;padding:9px 20px;border-radius:14px;background:rgba(255,248,238,.14);border:2px solid rgba(255,248,238,.3)}}
.callout{{position:absolute;font-weight:800;font-size:60px;padding:14px 28px;border-radius:20px;background:{MINT};color:{DEEP};box-shadow:0 14px 40px rgba(0,0,0,.4)}}
.callout.left{{left:60px;top:800px}} .callout.right{{right:100px;top:1215px}} .callout.red{{background:{RED};color:#fff}}
.feed{{position:absolute;border-radius:26px;background:rgba(255,248,238,.07);border:2px solid rgba(255,248,238,.12)}}
.note{{position:absolute;width:400px;padding:26px 28px 22px;background:#FFE08A;color:{INK};font-weight:800;font-size:50px;line-height:1.08;border-radius:6px;
  box-shadow:0 18px 40px rgba(0,0,0,.45)}} .note.n2{{background:#FFB3A7}} .note.n3{{background:#B8F0E4;width:300px;font-size:80px;text-align:center}}
.mini-notes{{position:absolute;left:60px;top:290px;display:flex;gap:16px}}
.mnote{{font-weight:800;font-size:44px;padding:14px 22px;border-radius:8px;background:#FFE08A;color:{INK}}}
.reveal{{position:absolute;left:60px;top:760px;font-weight:800;font-size:150px;line-height:.95;letter-spacing:-.03em;color:#fff;transform-origin:left center;
  text-shadow:0 8px 0 rgba(0,0,0,.3)}}
.underline{{position:absolute;left:60px;top:1060px;width:800px;height:30px}}
.half{{position:absolute;left:60px;width:900px;border-radius:30px;padding:30px 36px}}
.half.top{{top:170px;height:470px;background:rgba(255,248,238,.10);border:2px solid rgba(255,248,238,.18)}}
.half.bot{{top:860px;height:430px;background:{CREAM};color:{INK}}}
.hlabel{{font-weight:800;font-size:46px;margin-bottom:22px}} .hlabel.teal{{color:{TEAL}}}
.search{{display:flex;align-items:center;gap:14px;background:#fff;border-radius:999px;padding:14px 26px;color:{INK};font-weight:500;font-size:36px}}
.typed{{display:inline-block;white-space:nowrap}}
.res{{height:34px;border-radius:10px;background:rgba(255,248,238,.22);margin-top:22px;width:88%}} .res.w2{{width:70%}} .res.w3{{width:80%}}
.neq{{position:absolute;left:420px;top:650px;width:200px;text-align:center;font-weight:800;font-size:190px;line-height:1;color:{AMBER};text-shadow:0 8px 0 rgba(0,0,0,.3)}}
.crow{{display:flex;align-items:center;gap:16px;font-weight:700;font-size:42px;margin-top:20px}}
.capin{{position:absolute;left:70px;top:1380px;width:860px;text-align:center;font-weight:800;font-size:62px;line-height:1.1;letter-spacing:-.01em;color:#fff;
  -webkit-text-stroke:10px #0B1F2A;paint-order:stroke fill;text-shadow:0 6px 18px rgba(0,0,0,.6);white-space:nowrap}}
.hl{{color:{AMBER}}}
"""

PAGE = f"""<!doctype html>
<html lang="ms"><head><meta charset="utf-8"><title>Self Diagnose</title><style>{CSS}</style></head>
<body>
<div id="root" data-composition-id="selfdx" data-start="0" data-duration="{round(DUR, 4)}" data-fps="{FPS}" data-width="1080" data-height="1920">
<video id="bg" src="input-video.mp4" muted playsinline data-start="0" data-duration="{round(DUR, 4)}" data-track-index="1"></video>
{chr(10).join(body)}
<script src="vendor/gsap.min.js"></script>
<script>
(function(){{
  const tl = window.gsap.timeline({{paused:true}});
  {chr(10).join("  " + s for s in tl)}
  window.__timelines = window.__timelines || {{}};
  window.__timelines["selfdx"] = tl;
}})();
</script>
</div>
</body></html>
"""
(PUB / "index.html").write_text(PAGE)
print(f"{len(LINES)} caption lines, {len(cues)} SRT cues, {len(sfx)} sfx events, {len(tl)} tweens → public/index.html")
