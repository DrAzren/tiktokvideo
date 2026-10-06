"""Post-compile patch of project/plan.json for the "KEMURUNGAN" apex (run after make-cinematic.cjs,
then re-run make-composition.cjs). Template: videos/ward-psikiatri/captions/patch_apex.py.

The compiler centres the lockup on the subject: on this framing that puts the hero across the
forehead (y ~435-640, mostly hidden) and the tail line ("yang ramai orang tak perasan") across the
face. Patch:
  - lockup plane at y PLANE_TOP: the kicker ("ini mungkin tanda") is one line at the top
  - hero just below it, so the hair (top ~y 405-420 here) covers only the lower part of the letters
  - the tail line takes the kicker's slot the moment the kicker exits (same top line, never on the face)
  - kicker + tail: one centred full-width line at TAIL_H (the 28-char tail wraps at the compiler's size)
  - hero colour = the cards' teal (#0E5E6F)
  - cross-plane hand-off: the compiler page-flips only WITHIN a plane, so when the next line lands in
    another plane (hook "high" → hero lockup → body "narr" → closing "high") the previous one would
    linger ~0.15-0.3s on top of it; every group now ends when the next group in another plane begins
"""

import json
import re
from pathlib import Path

P = Path(__file__).parent / "project" / "plan.json"
PLANE_TOP = "8.9%"     # y ~171
HERO_TOP = 130         # px below the plane top → glyphs ~y 330-480; the hair (top ~405-420) hides their lower third
TAIL_H = "calc(0.040 * var(--h))"

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
for g in (kicker, tail):
    g["css"] = re.sub(r"top:\d+px", "top:0px", g["css"], count=1)
    g["css"] = re.sub(r"left:0px;right:auto;max-width:\d+px;text-align:left",
                      "left:0;right:0;max-width:none;text-align:center; white-space:nowrap", g["css"])
    g["css"] = re.sub(r"font-size: calc\(0\.0\d+ \* var\(--h\)\)", f"font-size: {TAIL_H}", g["css"], count=1)
for g in plan["groups"]:
    if g["plane"] == plane and (g.get("hero") or g["id"].startswith(hero["id"])):
        g["css"] = re.sub(r"top:\d+px", f"top:{HERO_TOP}px", g["css"], count=1)
        g["css"] = g["css"].replace("#0F766E", "#0E5E6F")
# cross-plane hand-off (a hero and its -glow companions count as one unit)
def unit(g):
    return hero["id"] if g["id"].startswith(hero["id"]) else g["id"]
order = sorted(plan["groups"], key=lambda g: g["in"])
firsts = {}
for g in order:
    firsts.setdefault(unit(g), g)
units = sorted(firsts.values(), key=lambda g: g["in"])
clipped = 0
for a, b in zip(units, units[1:]):
    if a["plane"] != b["plane"]:
        for g in plan["groups"]:
            if unit(g) == unit(a) or (g["plane"] == a["plane"] and g["in"] <= a["in"] < g["out"]):
                last = max([w.get("end", 0) for w in g.get("words", [])] + [0])
                new_out = round(max(b["in"], last + 0.02), 3)   # never before its own last word ends
                if g["out"] > new_out and g["in"] < b["in"]:
                    g["out"] = new_out
                    clipped += 1
print(f"cross-plane hand-offs clipped: {clipped}")
P.write_text(json.dumps(plan, indent=1, ensure_ascii=False))
print(f"apex patched: plane {plane} → top {PLANE_TOP}; hero top {HERO_TOP}px; kicker out/tail in @ {swap}s; "
      f"hero {hero['in']}–{hero['out']}s")
for g in [kicker, hero, tail]:
    print(" ", g["id"], g["in"], g["out"], g["css"][:150])
