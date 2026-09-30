"""Post-compile patch of project/plan.json for the "BERGANTUNG" apex (run after make-cinematic.cjs,
then re-run make-composition.cjs). Template: videos/ward-psikiatri/captions/patch_apex.py.
The compiler's lockup wraps the kicker into a 546px left column, puts the tail line under the hero
(on this framing: across the forehead) and sizes the 10-letter hero wider than the frame. Patch:
  - hero 0.10h (~885px wide) and raised so its caps end ~y560: the head covers only the lower part
    of the middle letters
  - kicker + tail: one centred line each; the tail takes the kicker's slot the moment it is spoken
"""

import json
from pathlib import Path

P = Path(__file__).parent / "project" / "plan.json"
plan = json.loads(P.read_text())
hero = next(g for g in plan["groups"] if g.get("hero"))
plane = hero["plane"]
ctx = sorted((g for g in plan["groups"] if g["plane"] == plane and not g.get("hero") and not g["id"].endswith("-glow")),
             key=lambda g: g["in"])
kicker, tail = ctx[0], ctx[-1]
assert kicker is not tail, "expected kicker + tail around the hero"

swap = round(tail["in"] - 0.04, 3)
kicker["out"] = swap
tail["in"] = swap
for g in (kicker, tail):
    css = g["css"]
    css = css.replace("left:0px;right:auto;max-width:546px;text-align:left", "left:0;right:0;max-width:none;text-align:center; white-space:nowrap")
    css = css.replace("calc(0.05 * var(--h))", "calc(0.046 * var(--h))")
    if g is tail:
        css = css.replace("top:428px", "top:0px")
    assert "max-width:none" in css and "top:0px" in css, css[:120]
    g["css"] = css
n = 0
for g in plan["groups"]:
    if g["plane"] == plane and (g.get("hero") or g["id"].startswith(hero["id"])):
        g["css"] = g["css"].replace("calc(0.118*var(--h))", "calc(0.10*var(--h))").replace("top:163px", "top:128px")
        n += 1
assert "top:128px" in hero["css"] and "0.10*var" in hero["css"], hero["css"]
P.write_text(json.dumps(plan, indent=1, ensure_ascii=False))
print(f"apex patched ({n} hero groups): kicker out/tail in @ {swap}s; hero {hero['in']}–{hero['out']}s")
