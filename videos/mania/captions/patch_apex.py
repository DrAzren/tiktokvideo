"""Post-compile patch of project/plan.json for the "BIPOLAR" apex (run after make-cinematic.cjs, then
re-run make-composition.cjs) — same fix as videos/ward-psikiatri/captions/patch_apex.py. The compiler's
lockup puts the tail line ("gangguan bipolar ni") under the hero, which on this framing is across the
eyes, and centres the hero low enough that the head hides most of its middle letters. Patch:
  - raise the lockup plane so the hair covers only the lower part of the letters (~20% occluded)
  - the tail line takes the kicker's slot (top of the lockup) the moment the kicker exits
  - kicker/tail: one centred full-width line each, body size; hero colour = the cards' teal
"""

import json
import re
from pathlib import Path

PLANE_TOP = "13%"   # kicker/tail line at y~250 (over the teal band, below TikTok's top bar)
HERO_TOP = 170      # hero ~y420-735: the hair (y~600) covers only the lower part of the middle letters
P = Path(__file__).parent / "project" / "plan.json"
plan = json.loads(P.read_text())
hero = next(g for g in plan["groups"] if g.get("hero"))
plane = hero["plane"]
ctx = sorted((g for g in plan["groups"] if g["plane"] == plane and not g.get("hero") and not g["id"].endswith("-glow")),
             key=lambda g: g["in"])
kicker, tail = ctx[0], ctx[-1]
assert kicker is not tail, "expected kicker + tail around the hero"

plan["planes"][plane]["css"] = re.sub(r"top:\s*[\d.]+%", f"top: {PLANE_TOP}", plan["planes"][plane]["css"])
swap = round(tail["in"] - 0.04, 3)
kicker["out"] = swap
tail["in"] = swap
tail["css"] = re.sub(r"top:\d+px", "top:0px", tail["css"], count=1)
for g in (kicker, tail):
    g["css"] = re.sub(r"left:\d+px;right:auto;max-width:\d+px;text-align:left",
                      "left:0;right:0;max-width:none;text-align:center; white-space:nowrap", g["css"])
    g["css"] = re.sub(r"font-size: calc\(0\.0\d+ \* var\(--h\)\)", "font-size: calc(0.046 * var(--h))", g["css"])
for g in plan["groups"]:
    if g["plane"] == plane and (g.get("hero") or g["id"].startswith(hero["id"])):
        g["css"] = re.sub(r"#[0-9A-Fa-f]{6}(?= !important)", "#0E5E6F", g["css"])
        g["css"] = re.sub(r"top:\d+px", f"top:{HERO_TOP}px", g["css"], count=1)
P.write_text(json.dumps(plan, indent=1, ensure_ascii=False))
print(f"apex patched: plane {plane} -> top {PLANE_TOP}; kicker out/tail in @ {swap}s; hero {hero['in']}-{hero['out']}s")
print(" kicker:", kicker["css"][:120], "\n tail:", tail["css"][:120])
