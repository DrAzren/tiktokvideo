"""Post-compile patch of project/plan.json for the "OLANZAPINE" apex (run after make-cinematic.cjs,
then re-run make-composition.cjs). Template: videos/ward-psikiatri/captions/patch_apex.py.

The compiler's lockup centres the hero on the subject: on this framing (head top y ~420-460) that hides
the middle letters completely, and it stacks the tail line ("JOM SAYA TERANGKAN") under the hero —
across the eyes. Patch:
  - lockup plane at 9% and the hero directly under the kicker, so the letters sit at y ~280-490 and the
    head covers only their lower part
  - the tail line takes the kicker's slot (top of the lockup) the moment the kicker exits
  - kicker + tail: one centred full-width line each, body size
"""

import json
import re
from pathlib import Path

P = Path(__file__).parent / "project" / "plan.json"
plan = json.loads(P.read_text())
hero = next(g for g in plan["groups"] if g.get("hero"))
plane = hero["plane"]
ctx = sorted((g for g in plan["groups"] if g["plane"] == plane and not g.get("hero") and not g["id"].endswith("-glow")),
             key=lambda g: g["in"])
kicker, tail = ctx[0], ctx[-1]
assert kicker is not tail, "expected kicker + tail around the hero"

plan["planes"][plane]["css"] = re.sub(r"top:\s*[\d.]+%", "top: 9%", plan["planes"][plane]["css"])
for g in plan["groups"]:
    if g["plane"] == plane and (g.get("hero") or g["id"].startswith(hero["id"])):
        g["css"] = re.sub(r"top:\d+px", "top:96px", g["css"], count=1)
swap = round(tail["in"] - 0.04, 3)
kicker["out"] = swap
tail["in"] = swap
tail["css"] = re.sub(r"top:\d+px", "top:0px", tail["css"], count=1)
for g in (kicker, tail):
    g["css"] = (re.sub(r"left:\d+px;right:auto;max-width:\d+px;text-align:left",
                       "left:0;right:0;max-width:none;text-align:center; white-space:nowrap", g["css"])
                .replace("calc(0.05 * var(--h))", "calc(0.046 * var(--h))"))
P.write_text(json.dumps(plan, indent=1, ensure_ascii=False))
print(f"apex patched: plane {plane} → top 9%, hero top 96px; kicker out/tail in @ {swap}s; hero {hero['in']}–{hero['out']}s")
