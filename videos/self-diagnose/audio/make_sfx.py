"""Synthesize the sound-effect track from graphics/sfx_events.json (no samples, licence-free).

whoosh = band-swept noise, pop = short rising blip, tick = soft click, impact = low thump, rise = short riser.
Events closer than 0.15 s collapse to the strongest one so cues never pile up. Output: audio/sfx.wav (48 kHz stereo).
"""
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

A = Path(__file__).parent
SR = 48000
DUR = 2900 / 30
rng = np.random.default_rng(7)
PRIO = {"impact": 4, "whoosh": 3, "rise": 2, "pop": 1, "tick": 0}
GAIN = {"impact": 0.30, "whoosh": 0.16, "rise": 0.12, "pop": 0.13, "tick": 0.07}


def env(n, a, r):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-np.maximum(t - a, 0) / r)


def whoosh():
    n = int(0.42 * SR); x = rng.standard_normal(n); out = np.zeros(n)
    for k, (lo, hi) in enumerate([(300, 900), (700, 2200), (1800, 5000)]):   # three bands fading in turn = upward sweep
        b = sosfilt(butter(2, [lo, hi], "bandpass", fs=SR, output="sos"), x)
        c = (k + 0.5) / 3 * n
        out += b * np.exp(-0.5 * ((np.arange(n) - c) / (0.16 * n)) ** 2)
    return out / np.abs(out).max()


def pop():
    n = int(0.09 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (520 * t + 1800 * t ** 2)) * env(n, 0.004, 0.022)


def tick():
    n = int(0.04 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1700 * t) * env(n, 0.001, 0.008)


def impact():
    n = int(0.5 * SR); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (58 * t + 40 * np.exp(-t * 30) / 30)) * env(n, 0.003, 0.13)
    thump = sosfilt(butter(2, 500, "lowpass", fs=SR, output="sos"), rng.standard_normal(n)) * env(n, 0.001, 0.03)
    return body + 0.5 * thump / np.abs(thump).max()


def rise():
    n = int(0.7 * SR); t = np.arange(n) / SR
    x = sosfilt(butter(2, [900, 4200], "bandpass", fs=SR, output="sos"), rng.standard_normal(n))
    return x / np.abs(x).max() * (t / t[-1]) ** 2 * np.minimum((t[-1] - t) / 0.03, 1)


MAKE = {"whoosh": whoosh, "pop": pop, "tick": tick, "impact": impact, "rise": rise}
ev = sorted(json.loads((A.parent / "graphics" / "sfx_events.json").read_text()), key=lambda e: e["t"])
kept = []
for e in ev:
    if kept and e["t"] - kept[-1]["t"] < 0.15:
        if PRIO[e["kind"]] > PRIO[kept[-1]["kind"]]:
            kept[-1] = e
    else:
        kept.append(e)
out = np.zeros((int(DUR * SR), 2))
for i, e in enumerate(kept):
    s = MAKE[e["kind"]]() * GAIN[e["kind"]]
    if e["kind"] == "whoosh":
        s = s[::-1] if False else s
    i0 = int(max(0, e["t"] - (0.25 if e["kind"] in ("whoosh", "rise") else 0)) * SR)   # whooshes peak ON the cut
    n = min(len(s), len(out) - i0)
    pan = 0.5 + 0.18 * (-1) ** i
    out[i0:i0 + n, 0] += s[:n] * (1 - pan) * 2
    out[i0:i0 + n, 1] += s[:n] * pan * 2
sf.write(A / "sfx.wav", out, SR, subtype="PCM_16")
print(f"{len(kept)} cues (from {len(ev)}), peak {20 * np.log10(np.abs(out).max()):.1f} dBFS")
