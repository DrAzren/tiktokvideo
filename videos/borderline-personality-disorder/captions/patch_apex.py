"""Post-compile patch of project/plan.json for the "BPD" apex (run after make-cinematic.cjs,
then re-run make-composition.cjs). Template: videos/ward-psikiatri/captions/patch_apex.py.
The compiler's width-fit raise blows a 3-letter hero up to ~0.28h and stacks the tail line
under it — across the face and into the TikTok UI. Patch:
  - lockup plane at 6% (the headroom is card-free during the apex), kicker/tail line on top
  - hero back to HERO_H with its top at HERO_TOP inside the plane: letters span y ~250-540, so
    the head (hair top ~430) covers only the lower middle of the word
  - the tail line takes the kicker's slot the moment the kicker exits
  - hero colour = the cards' teal
"""

import json
import re
from pathlib import Path

PLANE_TOP, HERO_H, HERO_TOP = "6%", 0.2, 82   # px inside the plane

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
# kicker + tail: one centred full-width line each (the lockup's 680px left column wraps them)
for g in (kicker, tail):
    g["css"] = re.sub(r"left:\d+px;right:auto;max-width:\d+px;text-align:left",
                      "left:0;right:0;max-width:none;text-align:center; white-space:nowrap", g["css"])
    g["css"] = re.sub(r"calc\(0\.0\d+ \* var\(--h\)\)", "calc(0.044 * var(--h))", g["css"], count=1)
for g in plan["groups"]:
    if g["plane"] == plane and (g.get("hero") or g["id"].startswith(hero["id"])):
        g["css"] = g["css"].replace("#0F766E", "#0E5E6F")
        g["css"] = re.sub(r"top:\d+px", f"top:{HERO_TOP}px", g["css"], count=1)
        g["css"] = re.sub(r"font-size: calc\([\d.]+ \* var\(--h\)\)", f"font-size: calc({HERO_H} * var(--h))", g["css"])
P.write_text(json.dumps(plan, indent=1, ensure_ascii=False))
print(f"apex patched: plane {plane} → top {PLANE_TOP}, hero {HERO_H}h @ {HERO_TOP}px; kicker out/tail in @ {swap}s; hero {hero['in']}–{hero['out']}s")
