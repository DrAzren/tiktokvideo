"""Place the SFX kit (audio/sfx/*.wav, from tools/sfx_synth.py) on the cut timeline → audio/sfx_track.wav.

Cue times come straight from graphics/build_graphics.py (cards, pages, inserts), so every sound lands on
the graphic it belongs to and re-times itself with the cut:
    whoosh  each full-screen insert (B-roll / motion graphic) — its swell peaks as the insert lands
    pop     each headroom card entering
    tick    each drug name sliding in
    chime   each "Risiko kepada bayi" page
    stamp   "BUKAN 100% DILARANG"
Levels are set here (dB applied to the -3 dBFS-peak kit) so effects sit well under the voice.
"""

import importlib.util
import io
import contextlib
from pathlib import Path

import numpy as np
import soundfile as sf

A = Path(__file__).parent
G = A.parent / "graphics"
SR = 48000
GAIN = {"whoosh": -13.0, "pop": -17.0, "tick": -21.0, "chime": -17.0, "stamp": -9.0}
LAND = {"whoosh": 0.30}   # whoosh peaks ~0.3 s in: start it early so the peak hits the cut

spec = importlib.util.spec_from_file_location("bg", G / "build_graphics.py")
bg = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(bg)
    cards, inserts = bg.build_cards(), bg.build_inserts()

cues = [(x["start"], "whoosh") for x in inserts]
for c in cards:
    cues.append((c["start"], "pop"))
    if c["id"].startswith("d"):
        for p, (t_in, els) in enumerate(c["pages"]):
            for key, frag, t, anim in els:
                if p == 0 and key == "name":
                    cues.append((t, "tick"))
                if p == 1 and key == "rk":
                    cues.append((t, "chime"))
rec = next(x for x in inserts if x["id"] == "m1-recap")
cues.append((next(t for sel, t, k in rec["anims"] if sel == "#m1-x"), "stamp"))

# a card that enters under a full-screen insert is hidden: drop its pop; thin out collisions (< 0.18 s)
cover = [(x["start"] + 0.25, x["end"] - 0.2) for x in inserts]
cues = [(t, n) for t, n in cues if not (n in ("pop", "tick") and any(a <= t <= b for a, b in cover))]
cues.sort()
kept = []
for t, n in cues:
    if kept and t - kept[-1][0] < 0.18:
        if GAIN[n] > GAIN[kept[-1][1]]:
            kept[-1] = (t, n)
        continue
    kept.append((t, n))

dur = bg.DUR
out = np.zeros((int(dur * SR) + SR, 2))
kit = {n: sf.read(A / "sfx" / f"{n}.wav")[0] for n in GAIN}
for t, n in kept:
    x = kit[n] * 10 ** (GAIN[n] / 20)
    i = max(0, int((t - LAND.get(n, 0.0)) * SR))
    out[i:i + len(x)] += x[:len(out) - i]
out = out[:int(round(dur * SR))]
sf.write(A / "sfx_track.wav", out.astype(np.float32), SR)
counts = {n: sum(1 for _, m in kept if m == n) for n in GAIN}
print(f"{len(kept)} cues {counts}; peak {20 * np.log10(np.abs(out).max() + 1e-9):.1f} dBFS; {dur:.2f}s")
