"""Round 2 scene engine for build_graphics.py: more B-roll, varied transitions, paper frames.

Spliced into build_graphics.py's namespace (it uses T, q, sfx, icon, JS, INS_HOSTS, STORY, PUB ...).
Every scene is one full-screen layer:
  video  - a Higgsfield Seedance 2.0 Mini clip (public/broll/S*.mp4), full bleed or in a paper polaroid
  mg     - a HyperFrames motion graphic
Transitions (in): zoom, whip, tear (paper tear), flip (3D page turn), cube (3D cube with the outgoing layer),
polaroid (paper print drops in), iris, up. Out: fade, whip, flip, zoom, cube (back to the speaker), drop.
Each transition carries its own SFX cue. Adjacent scenes overlap by the incoming transition so the outgoing
picture stays underneath (the incoming layer sits above it).
"""

TIN = {"zoom": 0.45, "whip": 0.38, "tear": 0.6, "flip": 0.6, "cube": 0.6, "polaroid": 0.6, "iris": 0.5, "up": 0.45}
JAG = [0.0, 1.1, -0.8, 1.4, -1.2, 0.6, -1.5, 1.0, -0.5, 1.3, -0.9, 0.8, -0.3]   # % offsets of the torn edge
JAG2 = [0.7, -0.6, 1.0, -1.1, 0.4, -0.9, 1.2, -0.4, 0.9, -1.3, 0.5, -0.7, 1.1]


def tear_poly(x: float, band: bool = False) -> str:
    n = len(JAG) - 1
    right = [f"{x + JAG[k]:.2f}% {100 * k / n:.2f}%" for k in range(n + 1)]
    if not band:
        return "polygon(0% 0%, " + ", ".join(right) + ", 0% 100%)"
    left = [f"{x - 2.6 + JAG2[k]:.2f}% {100 * k / n:.2f}%" for k in range(n, -1, -1)]
    return "polygon(" + ", ".join(right + left) + ")"


def t_in(iid, t, kind, prev):
    """prev: the outgoing layer's selector (a scene inner wrapper, or '#video-wrap' for the speaker)."""
    h = f"#{iid}-in"
    t = q(t)
    if kind == "zoom":
        JS.append(f"tl.fromTo('{h}', {{opacity:0, scale:1.35, filter:'blur(18px)'}}, {{opacity:1, scale:1, filter:'blur(0px)', duration:0.45, ease:'power3.out'}}, {t});")
        sfx(t + 0.2, "whoosh", -5)
    elif kind == "whip":
        JS.append(f"tl.fromTo('{h}', {{xPercent:100, filter:'blur(26px)'}}, {{xPercent:0, filter:'blur(0px)', duration:0.38, ease:'power4.out'}}, {t});")
        if prev and prev != "#video-wrap":
            JS.append(f"tl.to('{prev}', {{xPercent:-35, filter:'blur(14px)', duration:0.38, ease:'power4.out'}}, {t});")
        sfx(t + 0.1, "swish", -3)
    elif kind == "tear":
        JS.append(f"tl.fromTo('{h}', {{clipPath:'{tear_poly(-8)}'}}, {{clipPath:'{tear_poly(108)}', duration:0.6, ease:'power2.inOut'}}, {t});")
        JS.append(f"tl.fromTo('#{iid}-band', {{clipPath:'{tear_poly(-8, True)}'}}, {{clipPath:'{tear_poly(108, True)}', duration:0.6, ease:'power2.inOut'}}, {t});")
        sfx(t + 0.05, "paper_rip", -2)
    elif kind == "flip":
        JS.append(f"tl.fromTo('{h}', {{rotationY:-100, transformOrigin:'0% 50%', transformPerspective:1800}}, {{rotationY:0, transformOrigin:'0% 50%', transformPerspective:1800, duration:0.6, ease:'power3.out'}}, {t});")
        JS.append(f"tl.fromTo('#{iid}-fs', {{opacity:0.65}}, {{opacity:0, duration:0.6, ease:'power2.out'}}, {t});")
        sfx(t + 0.1, "page_flip", -2)
    elif kind == "cube":
        JS.append(f"tl.fromTo('{h}', {{rotationY:90, transformOrigin:'0% 50%', transformPerspective:2000}}, {{rotationY:0, transformOrigin:'0% 50%', transformPerspective:2000, duration:0.6, ease:'power2.inOut'}}, {t});")
        if prev:
            JS.append(f"tl.to('{prev}', {{rotationY:-90, transformOrigin:'100% 50%', transformPerspective:2000, duration:0.6, ease:'power2.inOut'}}, {t});")
            if prev == "#video-wrap":   # put the speaker back, unseen, for the next time it is on screen
                JS.append(f"tl.set('#video-wrap', {{rotationY:0, transformOrigin:'50% 38%'}}, {q(t + 0.65)});")
            else:                       # scene -> scene: the gap behind the cube shows the navy stage, not the speaker
                JS.append(f"tl.set('#video-wrap', {{opacity:0}}, {t});")
                JS.append(f"tl.set('#video-wrap', {{opacity:1}}, {q(t + 0.65)});")
        sfx(t + 0.3, "cube", -2)
    elif kind == "polaroid":
        JS.append(f"tl.fromTo('{h}', {{opacity:0}}, {{opacity:1, duration:0.25, ease:'power2.out'}}, {t});")
        JS.append(f"tl.fromTo('#{iid}-gh', {{y:-1500, rotation:14}}, {{y:0, rotation:5, duration:0.55, ease:'power3.out'}}, {t});")
        JS.append(f"tl.fromTo('#{iid}-pol', {{y:-1550, rotation:-16, scale:1.08}}, {{y:0, rotation:-3, scale:1, duration:0.6, ease:'power3.out'}}, {q(t + 0.05)});")
        JS.append(f"tl.fromTo('#{iid}-pol .tape', {{opacity:0}}, {{opacity:1, duration:0.2, ease:'power2.out', stagger:0.08}}, {q(t + 0.6)});")
        sfx(t + 0.5, "paper_drop", -2)
    elif kind == "iris":
        JS.append(f"tl.fromTo('{h}', {{clipPath:'circle(0% at 50% 42%)'}}, {{clipPath:'circle(80% at 50% 42%)', duration:0.5, ease:'power3.inOut'}}, {t});")
        sfx(t + 0.25, "whoosh", -6)
    else:  # up
        JS.append(f"tl.fromTo('{h}', {{clipPath:'inset(100% 0% 0% 0%)'}}, {{clipPath:'inset(0% 0% 0% 0%)', duration:0.45, ease:'power3.inOut'}}, {t});")
        sfx(t + 0.2, "whoosh", -6)


def t_out(iid, en, kind):
    """Exit back to the speaker (used only when no scene follows straight away)."""
    h = f"#{iid}-in"
    if kind == "whip":
        JS.append(f"tl.to('{h}', {{xPercent:-100, filter:'blur(26px)', duration:0.32, ease:'power3.in'}}, {q(en - 0.32)});")
        sfx(en - 0.12, "swish", -5)
    elif kind == "flip":
        JS.append(f"tl.to('{h}', {{rotationY:100, transformOrigin:'100% 50%', transformPerspective:1800, duration:0.45, ease:'power3.in'}}, {q(en - 0.45)});")
        sfx(en - 0.3, "page_flip", -4)
    elif kind == "zoom":
        JS.append(f"tl.to('{h}', {{scale:1.45, opacity:0, filter:'blur(16px)', duration:0.35, ease:'power2.in'}}, {q(en - 0.35)});")
        sfx(en - 0.25, "whoosh", -7)
    elif kind == "cube":
        s = q(en - 0.6)
        JS.append(f"tl.to('{h}', {{rotationY:-90, transformOrigin:'100% 50%', transformPerspective:2000, duration:0.6, ease:'power2.inOut'}}, {s});")
        JS.append(f"tl.set('#video-wrap', {{rotationY:90, transformOrigin:'0% 50%', transformPerspective:2000}}, {s});")
        JS.append(f"tl.to('#video-wrap', {{rotationY:0, duration:0.6, ease:'power2.inOut'}}, {s});")
        JS.append(f"tl.set('#video-wrap', {{transformOrigin:'50% 38%'}}, {q(en + 0.02)});")
        sfx(s + 0.3, "cube", -3)
    elif kind == "drop":
        s = q(en - 0.4)
        JS.append(f"tl.to('#{iid}-pol, #{iid}-gh', {{y:1700, rotation:12, duration:0.4, ease:'power3.in'}}, {s});")
        JS.append(f"tl.to('{h}', {{opacity:0, duration:0.2, ease:'power2.in'}}, {q(en - 0.2)});")
        sfx(s + 0.15, "swish", -7)
    else:  # fade
        JS.append(f"tl.to('{h}', {{opacity:0, duration:0.22, ease:'power2.in'}}, {q(en - 0.22)});")


def mg_body(kind, iid, a, b):
    """Returns (html, anims) for the round-2 motion graphics (anims use mg()'s vocabulary)."""
    if kind == "molecule":
        svg, pids, gids = molecule_svg(iid, 11)
        JS.append(f"tl.fromTo('#{iid}-net', {{scale:1.0, rotation:-4, transformOrigin:'50% 45%'}}, {{scale:1.16, rotation:4, duration:{round(b - a, 3)}, ease:'power1.inOut'}}, {q(a)});")
        pulses_js(pids, gids, a, b)
        sfx(a + 0.35, "pulse", -7)
        return svg, []
    if kind == "litium":
        html_ = (f'<div class="mg-head"><div class="chip">Ubat mood</div><div class="mg-title" id="{iid}-t">Ramai yang tahu…</div></div>'
                 f'<div class="tile-wrap" id="{iid}-tile"><div class="tile-face front"><span class="tn">3</span><span class="ts">Li</span>'
                 f'<span class="tname">Litium</span></div><div class="tile-face back"><span class="ts gold">?</span>'
                 f'<span class="tname">Satu lagi ubat</span></div></div>')
        flip = T("satu lagi") - 0.15
        return html_, [(f"#{iid}-t", a + 0.15, "rise"),
                       (f"#{iid}-tile", T("litium") - 0.2, ("js", f"tl.fromTo('#{iid}-tile', {{opacity:0, scale:0.5, rotationY:-35, transformPerspective:1600}}, {{opacity:1, scale:1, rotationY:0, transformPerspective:1600, duration:0.5, ease:'back.out(1.5)'}}, @T);")),
                       (f"#{iid}-tile", flip, ("js", f"tl.to('#{iid}-tile', {{rotationY:180, transformPerspective:1600, duration:0.65, ease:'power3.inOut'}}, @T);")),
                       (f"#{iid}-tile", flip + 0.05, ("sfx", "page_flip", -4))]
    if kind == "calendar":
        pages = "".join(f'<div class="page" id="{iid}-pg{k}" style="z-index:{20 - k}"><div class="page-head"></div><div class="page-grid"></div></div>'
                        for k in range(6))
        html_ = (f'<div class="mg-head"><div class="chip">Jangka panjang</div><div class="mg-title" id="{iid}-t">Sesuai untuk '
                 f'<span class="gold">long-term use</span></div></div><div class="cal" id="{iid}-cal">{pages}<div class="rings"></div></div>')
        an = [(f"#{iid}-t", T("long term") - 0.5, "rise"),
              (f"#{iid}-cal", a + 0.1, ("js", f"tl.fromTo('#{iid}-cal', {{opacity:0, y:80, rotation:-4}}, {{opacity:1, y:0, rotation:-2, duration:0.45, ease:'power3.out'}}, @T);"))]
        for k in range(5):
            an.append((f"#{iid}-pg{k}", a + 0.55 + k * 0.3, ("js", f"tl.to('#{iid}-pg{k}', {{rotationX:-170, transformOrigin:'50% 0%', transformPerspective:1600, opacity:0, duration:0.45, ease:'power2.in'}}, @T);")))
            an.append((f"#{iid}-pg{k}", a + 0.6 + k * 0.3, ("sfx", "page_flip", -12)))
        return html_, an
    if kind == "shield":
        html_ = (f'<div class="mg-head"><div class="chip">Kena ingat</div></div>'
                 f'<svg class="shield" viewBox="0 0 1080 1920"><circle id="{iid}-ring" cx="540" cy="900" r="300" fill="none" stroke="{BLUE}" stroke-width="6" opacity="0"/>'
                 f'<g transform="translate(204,564) scale(14)"><path id="{iid}-sh" d="M24 5l15 6v11c0 10-6 17-15 21C15 39 9 32 9 22V11z" pathLength="100" '
                 f'stroke-dasharray="100" stroke-dashoffset="100" fill="none" stroke="{GOLD}" stroke-width="0.6" stroke-linejoin="round"/>'
                 f'<path id="{iid}-fill" d="M24 5l15 6v11c0 10-6 17-15 21C15 39 9 32 9 22V11z" fill="rgba(226,184,87,.16)"/>'
                 f'<path id="{iid}-ck" d="M17 24l5 5 9-10" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" fill="none" stroke="{WHITE}" '
                 f'stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/></g></svg>'
                 f'<div class="sh-word" id="{iid}-w">Cara guna yang <span class="gold">selamat</span></div>')
        ck = T("selamat") - 0.3
        return html_, [(f"#{iid}-sh", a + 0.2, ("js", f"tl.fromTo('#{iid}-sh', {{strokeDashoffset:100}}, {{strokeDashoffset:0, duration:0.8, ease:'power2.inOut'}}, @T);")),
                       (f"#{iid}-fill", a + 0.6, "fade"),
                       (f"#{iid}-w", T("cara guna") - 0.12, "rise"),
                       (f"#{iid}-ck", ck, ("js", f"tl.fromTo('#{iid}-ck', {{strokeDashoffset:100}}, {{strokeDashoffset:0, duration:0.4, ease:'power3.out'}}, @T);")),
                       (f"#{iid}-ck", ck + 0.05, ("sfx", "pop", -6)),
                       (f"#{iid}-ring", ck + 0.2, ("js", f"tl.fromTo('#{iid}-ring', {{opacity:0.8, scale:0.85, svgOrigin:'540 900'}}, {{opacity:0, scale:1.3, svgOrigin:'540 900', duration:0.9, ease:'power2.out', immediateRender:false}}, @T);"))]
    if kind == "wave":
        pts = []
        for k in range(0, 3241, 18):
            x = k / 3240
            amp = 300 * (0.55 + 0.45 * math.sin(2 * math.pi * x * 1.7 + 0.4))
            y = 920 + amp * (0.62 * math.sin(2 * math.pi * x * 9.0) + 0.38 * math.sin(2 * math.pi * x * 15.0 + 1.1))
            pts.append(f"{k} {y:.0f}")
        d = "M " + " L ".join(pts)
        html_ = (f'<svg class="wave" viewBox="0 0 1080 1920"><g id="{iid}-g"><path d="{d}" class="wave-glow"/><path d="{d}" class="wave-line"/></g></svg>'
                 f'<div class="mg-head"><div class="chip">Mood swing</div></div>')
        dur = round(b - a, 3)
        return html_, [(f"#{iid}-g", a, ("js", f"tl.fromTo('#{iid}-g', {{x:0}}, {{x:-2160, duration:{dur}, ease:'power1.inOut'}}, @T);")),
                       (f"#{iid}-g", a + dur * 0.35, ("js", f"tl.fromTo('#{iid}-g', {{scaleY:1}}, {{scaleY:0.22, svgOrigin:'540 920', duration:{round(dur * 0.6, 3)}, ease:'power2.inOut'}}, @T);"))]
    raise KeyError(kind)


def scenes():
    """The round-2 scene list (anchored to phrases on the cut timeline)."""
    return [
        dict(id="s01", src="S1", a=T("yang stabilkan mood") - 0.25, b=T("ramai yang tahu") - 0.1, tin="zoom", ms=0.2),
        dict(id="m01", mg="litium", a=T("ramai yang tahu") - 0.1, b=T("kata underrated") - 0.2, tin="whip"),
        dict(id="s02", src="S2", a=T("kata underrated") - 0.2, b=T("lamotrigine") + 0.13, tin="tear", ms=0.3, kinetic=True),
        dict(id="m02", mg="molecule", a=T("famous untuk") - 0.15, b=T("especially"), tin="cube"),
        dict(id="s03", src="S3", paper="Bipolar disorder", a=T("especially"), b=T("terutamanya") - 0.1, tin="polaroid", tout="flip"),
        dict(id="m03", mg="weight", a=T("dan risiko") - 0.15, b=T("ubat ni juga dia tak") - 0.1, tin="flip", tout="whip"),
        dict(id="s04", src="S4", paper="Function macam biasa", a=T("jadi ramai orang") - 0.15, b=T("dan sesuai untuk") - 0.1, tin="polaroid"),
        dict(id="m04", mg="calendar", a=T("dan sesuai untuk") - 0.1, b=T("tapi dengan monitoring") - 0.15, tin="whip"),
        dict(id="s05", src="S5", a=T("tapi dengan monitoring") - 0.15, b=T("seperti biasa setiap") - 0.1, tin="flip", tout="zoom", ms=0.0),
        dict(id="s06", src="S6", a=T("ubat ni dia kena start") - 0.15, b=T("perlahan lahan") - 0.25, tin="iris", ms=0.2),
        dict(id="m05", mg="titrate", a=T("perlahan lahan") - 0.25, b=T("sebab ada risiko") - 0.1, tin="cube", tout="fade"),
        dict(id="m06", mg="sidefx", a=T("menyebabkan side effect") - 0.2, b=T("dan ubat ni juga dia tak") - 0.1, tin="tear", tout="cube"),
        dict(id="s07", src="S7", a=T("nak elak") - 0.1, b=T("sama seperti ubat lain") - 0.1, tin="iris", tout="whip"),
        dict(id="m07", mg="shield", a=T("tapi kena ingat") - 0.15, b=T("kalau anda rasa") - 0.12, tin="zoom"),
        dict(id="m08", mg="wave", a=T("kalau anda rasa") - 0.12, b=T("boleh set appointment") - 0.15, tin="whip", tout="flip"),
        dict(id="s08", src="S5", paper="Sembang santai dahulu", a=T("kita sembang") - 0.1, b=T("apa persoalan") - 0.15,
             tin="polaroid", tout="drop", ms=0.0),
    ]


def add_scenes():
    sc = sorted(scenes(), key=lambda s: s["a"])
    for s in sc:
        s["a"], s["b"] = q(s["a"]), q(s["b"])
    # adjacent scenes: the outgoing one stays underneath until the incoming transition has landed
    for p, n in zip(sc, sc[1:]):
        assert n["a"] >= p["b"] - 0.05, (p["id"], n["id"], p["b"], n["a"])
        if n["a"] - p["b"] < 0.06:
            p["b"] = q(n["a"] + TIN[n["tin"]] + 0.05)
            p["tout"] = "under"
            n["prev"] = f"#{p['id']}-in"
    for k, s in enumerate(sc):
        iid, a, b = s["id"], s["a"], s["b"]
        z = 20 + k
        prev = s.get("prev", "#video-wrap")
        # only the layers a transition needs (clip-path / gradient overlays are heavy for the capture engine)
        common = ((f'<div class="fshade" id="{iid}-fs"></div>' if s["tin"] == "flip" else "")
                  + (f'<div class="tear-band" id="{iid}-band"></div>' if s["tin"] == "tear" else ""))
        if "src" in s:
            clip = PUB / "broll" / f"{s['src']}.mp4"
            d = probe_dur(clip)
            span = b - a
            rate = 1.0 if span <= d - s.get("ms", 0) - 0.05 else round((d - s.get("ms", 0) - 0.05) / span, 3)
            ms = s.get("ms", round(max(0.0, (d - span) / 2), 3))
            vid = (f'<video id="{iid}-v" class="clip {"pv" if "paper" in s else "kbv"}" src="broll/{s["src"]}.mp4" muted playsinline '
                   f'data-start="{a}" data-duration="{round(span, 4)}" data-media-start="{ms}"'
                   + (f' data-playback-rate="{rate}"' if rate != 1.0 else "") + f' data-track-index="{3 + k % 2}"></video>')
            if "paper" in s:
                body = (f'<div class="paper-bg"></div><div class="pol ghost" id="{iid}-gh"></div>'
                        f'<div class="pol" id="{iid}-pol"><div class="pol-photo">{vid}</div>'
                        f'<div class="pol-label" id="{iid}-lb">{s["paper"]}</div>'
                        f'<div class="tape t1"></div><div class="tape t2"></div></div>')
            else:
                body = vid + '<div class="ins-shade"></div>'
                if s.get("kinetic"):
                    body += f'<div class="kin" id="{iid}-k1">Underrated</div><div class="kin gold" id="{iid}-k2">Tapi power</div>'
            body += f'<div class="ai-tag{" r" if "paper" in s else ""}">Ilustrasi AI</div>' + common
            INS_HOSTS.append(f'<div class="ins vscene" id="{iid}-in" style="z-index:{z}">{body}</div>')
            JS.append(f"// scene {iid}: {s['src']} {'paper frame' if 'paper' in s else 'full'} {a:.2f}-{b:.2f} in:{s['tin']} out:{s.get('tout', 'fade')}")
            if s["tin"] not in ("polaroid", "zoom"):     # those transitions fade the layer in themselves
                JS.append(f"tl.set('#{iid}-in', {{opacity:1}}, {a});")
            JS.append(f"tl.set('#{iid}-in', {{opacity:0}}, {b});")
            if "paper" not in s:
                JS.append(f"tl.fromTo('#{iid}-v', {{scale:1.08}}, {{scale:1.0, duration:{round(span, 3)}, ease:'power1.out'}}, {a});")
            else:
                JS.append(f"tl.fromTo('#{iid}-lb', {{opacity:0, x:-30}}, {{opacity:1, x:0, duration:0.4, ease:'power3.out'}}, {q(a + 0.75)});")
            if s.get("kinetic"):
                t1, t2 = T("underrated") - LEAD, T("tapi power") - LEAD
                JS.append(f"tl.fromTo('#{iid}-k1', {{opacity:0, y:40, scaleX:1.18}}, {{opacity:1, y:0, scaleX:1, duration:0.5, ease:'power3.out'}}, {q(max(t1, a + 0.4))});")
                JS.append(f"tl.to('#{iid}-k1', {{opacity:0.35, duration:0.3, ease:'power2.out'}}, {q(t2 - 0.1)});")
                JS.append(f"tl.fromTo('#{iid}-k2', {{opacity:0, scale:1.4}}, {{opacity:1, scale:1, duration:0.32, ease:'power4.out'}}, {q(t2)});")
                sfx(t2, "impact", -8)
            STORY.append({"id": iid, "kind": "broll-paper" if "paper" in s else "broll", "source": f"{s['src']}.mp4",
                          "start": a, "end": b, "in": s["tin"], "out": s.get("tout", "fade"), "rate": rate})
        else:
            if s["mg"] in MG_LEGACY:
                html_, anims = MG_LEGACY[s["mg"]](a, b)
            else:
                html_, anims = mg_body(s["mg"], iid, a, b)
            INS_HOSTS.append(f'<div class="ins clip" id="ins-{iid}" data-start="{a}" data-duration="{round(b - a, 4)}" '
                             f'data-track-index="5" style="z-index:{z}"><div class="ins-in" id="{iid}-in"><div class="mg-bg"></div>'
                             f'<div class="mg-grid"></div>{html_}{common}</div></div>')
            JS.append(f"// scene {iid}: motion graphic '{s['mg']}' {a:.2f}-{b:.2f} in:{s['tin']} out:{s.get('tout', 'fade')}")
            mg_anims(anims, a)
            STORY.append({"id": iid, "kind": "motion-graphic", "mg": s["mg"], "start": a, "end": b,
                          "in": s["tin"], "out": s.get("tout", "fade")})
        t_in(iid, a, s["tin"], prev)
        if s.get("tout", "fade") != "under":
            t_out(iid, b, s.get("tout", "fade"))
    return sc
