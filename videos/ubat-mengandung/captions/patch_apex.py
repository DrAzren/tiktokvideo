"""Post-compile patch of project/plan.json for the "10 UBAT" apex (run after make-cinematic.cjs, then
make-composition.cjs). The compiler's lockup stacks the tail ("psikiatri yang perlu") under the hero,
left-aligned at y~680 — across the forehead on this framing. Patch:
  - lockup plane at HERO_TOP: the head (hair top ~y420) covers the lower part of "10 UBAT"
  - the tail line moves down into the caption band on the chest (same place, size and centring as
    every other caption line), so the screen still reads top->bottom in spoken order
Usage: python patch_apex.py [hero_top_pct] [hero_size_h]
"""

import json
import re
import sys
from pathlib import Path

P = Path(__file__).parent / "project" / "plan.json"
HERO_TOP = float(sys.argv[1]) if len(sys.argv) > 1 else 11.5
HERO_SIZE = float(sys.argv[2]) if len(sys.argv) > 2 else 0.13
H = 1920
plan = json.loads(P.read_text())
hero = next(g for g in plan["groups"] if g.get("hero"))
plane = hero["plane"]
ctx = [g for g in plan["groups"] if g["plane"] == plane and not g.get("hero") and not g["id"].endswith("-glow")]
assert len(ctx) == 1, [g["id"] for g in ctx]
tail = ctx[0]

plan["planes"][plane]["css"] = re.sub(r"top:\s*[\d.]+%", f"top: {HERO_TOP}%", plan["planes"][plane]["css"])
narr_top = float(re.search(r"top:\s*([\d.]+)%", plan["planes"]["narr"]["css"]).group(1))
dy = round((narr_top - HERO_TOP) / 100 * H)
tail["css"] = re.sub(r"position:absolute;top:\d+px;left:\d+px;right:auto;max-width:\d+px;text-align:left;",
                     f"position:absolute;top:{dy}px;left:0;right:0;max-width:none;text-align:center;white-space:nowrap;",
                     tail["css"])
tail["css"] = re.sub(r"font-size:\s*calc\([\d.]+\s*\*\s*var\(--h\)\)", "font-size: calc(0.047*var(--h))", tail["css"], count=1)
assert f"top:{dy}px" in tail["css"], tail["css"][:160]
# the compiler's mass rule sizes the hero at 0.40h (768 px: "10 UBAT" overflows the frame and the head
# hides almost all of it); HERO_SIZE fits it across the headroom with the hair covering its lower edge
for g in plan["groups"]:
    if g["plane"] == plane and (g.get("hero") or g["id"].startswith(hero["id"])):
        g["css"] = re.sub(r"font-size:\s*calc\([\d.]+\s*\*\s*var\(--h\)\)", f"font-size: calc({HERO_SIZE} * var(--h))", g["css"])
P.write_text(json.dumps(plan, indent=1, ensure_ascii=False))
print(f"apex patched: lockup plane top {HERO_TOP}%, hero {HERO_SIZE}h; tail '{' '.join(w['text'] for w in tail['words'])}' -> chest band (+{dy}px)")
