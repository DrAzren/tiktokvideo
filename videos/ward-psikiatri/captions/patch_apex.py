"""Post-compile patch of project/plan.json for the "TIDAK" apex (run after make-cinematic.cjs,
then re-run make-composition.cjs). The compiler's lockup puts the tail line under the hero —
on this framing that is across the cheek and mouth — and centres the hero so the head hides
its middle letter. Patch:
  - raise the lockup plane so the head covers only the lower part of the letters
  - the tail line takes the kicker's slot (top of the lockup) the moment the kicker exits
  - hero colour = the cards' teal
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

plan["planes"][plane]["css"] = re.sub(r"top:\s*[\d.]+%", "top: 13%", plan["planes"][plane]["css"])
swap = round(tail["in"] - 0.04, 3)
kicker["out"] = swap
tail["in"] = swap
tail["css"] = re.sub(r"top:\d+px", "top:0px", tail["css"], count=1)
# kicker + tail: one centred full-width line each (the lockup's 680px left column wraps them)
for g in (kicker, tail):
    g["css"] = (g["css"].replace("left:25px;right:auto;max-width:680px;text-align:left",
                                 "left:0;right:0;max-width:none;text-align:center; white-space:nowrap")
                .replace("calc(0.062 * var(--h))", "calc(0.046 * var(--h))"))
for g in plan["groups"]:
    if g["plane"] == plane and (g.get("hero") or g["id"].startswith(hero["id"])):
        g["css"] = g["css"].replace("#0F766E", "#0E5E6F")
P.write_text(json.dumps(plan, indent=1, ensure_ascii=False))
print(f"apex patched: plane {plane} → top 13%; kicker out/tail in @ {swap}s; hero {hero['in']}–{hero['out']}s")
