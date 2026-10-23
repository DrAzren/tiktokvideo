"""Synthesize restrained SFX and lay them under the enhanced voice at graphics/sfx_cues.json.

Kinds (all generated here, no samples): whoosh (band-swept noise), impact (soft low thump + air),
pulse (two-tone digital blip with echo), tick (short filtered click), shimmer (bell partials).
Levels sit well under speech: peaks -20..-30 dBFS before the cue's own gain_db.

Usage: python sfx_mix.py <voice.wav> <sfx_cues.json> -o voice_sfx.wav
"""

import argparse
import json

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

SR = 48000
rng = np.random.default_rng(23)


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(t / max(a, 1e-4), 1.0) * np.exp(-np.maximum(t - a, 0) / d)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), x)


def whoosh():
    n = int(0.55 * SR)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    steps = 24
    for k in range(steps):  # sweep a band upward, piecewise
        a, b = k * n // steps, (k + 1) * n // steps
        f = 300 * (12 ** (k / steps))
        out[a:b] = bp(noise, f, min(f * 2.2, 16000))[a:b]
    t = np.linspace(0, 1, n)
    shape = np.sin(np.pi * t ** 0.7) ** 2
    return out * shape, -24


def impact():
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    f = 70 * np.exp(-t * 3) + 42
    thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.004, 0.22)
    air = bp(rng.standard_normal(n), 2000, 9000) * env(n, 0.002, 0.05) * 0.25
    return thump + air, -18


def pulse():
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for k, (f, d) in enumerate([(1046.5, 0.0), (1568.0, 0.09), (1046.5, 0.26), (1568.0, 0.35)]):
        i = int(d * SR)
        m = n - i
        y[i:] += np.sin(2 * np.pi * f * t[:m]) * env(m, 0.003, 0.06) * (0.55 ** (k // 2))
    return y, -28


def tick():
    n = int(0.08 * SR)
    return bp(rng.standard_normal(n), 2500, 7000) * env(n, 0.0005, 0.012), -30


def shimmer():
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * f * t) * env(n, 0.01, 0.5 / (k + 1)) / (k + 1)
            for k, f in enumerate([1318.5, 1975.5, 2637.0, 3951.1]))
    return y, -26


def swish():
    """Short, bright whoosh for whip pans."""
    n = int(0.28 * SR)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    for k in range(16):
        a, b = k * n // 16, (k + 1) * n // 16
        f = 1200 * (6 ** (k / 16))
        out[a:b] = bp(noise, f, min(f * 1.8, 18000))[a:b]
    t = np.linspace(0, 1, n)
    return out * np.sin(np.pi * t) ** 3, -24


def paper_rip():
    """Torn paper: a train of short crackles under a band-limited noise body."""
    n = int(0.5 * SR)
    body = bp(rng.standard_normal(n), 900, 6000) * np.sin(np.pi * np.linspace(0, 1, n)) ** 0.6
    crack = np.zeros(n)
    t = 0
    while t < n - 400:
        t += int(rng.integers(150, 900))
        m = min(300, n - t)
        crack[t:t + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / 40) * rng.uniform(0.4, 1.0)
    return body * 0.35 + bp(crack, 1500, 9000), -24


def page_flip():
    """Page turn: airy swish with a fast flutter, ending in a soft paper tap."""
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    air = bp(rng.standard_normal(n), 500, 5000) * np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    flutter = 0.6 + 0.4 * np.sin(2 * np.pi * 22 * t)
    tap = np.zeros(n)
    i = int(0.36 * SR)
    tap[i:] = bp(rng.standard_normal(n - i), 300, 3000) * np.exp(-np.arange(n - i) / (0.012 * SR))
    return air * flutter + tap * 0.8, -24


def cube():
    """3D rotation: low whoosh with a gentle thump as the face lands."""
    w, _ = whoosh()
    y, _ = impact()
    n = len(w) + int(0.1 * SR)
    out = np.zeros(n)
    out[:len(w)] += sosfilt(butter(2, 2500, fs=SR, output="sos"), w)
    i = int(0.42 * SR)
    m = min(len(y), n - i)
    out[i:i + m] += y[:m] * 0.5
    return out, -22


def paper_drop():
    """A photo print dropping onto a table: short flutter + soft slap."""
    n = int(0.4 * SR)
    t = np.arange(n) / SR
    flutter = bp(rng.standard_normal(n), 800, 6000) * env(n, 0.05, 0.12) * (0.6 + 0.4 * np.sin(2 * np.pi * 30 * t))
    slap = np.zeros(n)
    i = int(0.22 * SR)
    slap[i:] = (bp(rng.standard_normal(n - i), 200, 2500) + 0.5 * np.sin(2 * np.pi * 110 * t[:n - i])) \
        * np.exp(-np.arange(n - i) / (0.02 * SR))
    return flutter * 0.5 + slap, -22


def pop():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    f = 900 * np.exp(-t * 18) + 300
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.03), -28


KINDS = {"whoosh": whoosh, "impact": impact, "pulse": pulse, "tick": tick, "shimmer": shimmer, "swish": swish,
         "paper_rip": paper_rip, "page_flip": page_flip, "cube": cube, "paper_drop": paper_drop, "pop": pop}
# where in the sound the transition "lands" (seconds), so the cue lines up with the visual
ALIGN = {"whoosh": 0.3, "swish": 0.14, "paper_rip": 0.1, "page_flip": 0.1, "cube": 0.3, "paper_drop": 0.2}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("voice")
    ap.add_argument("cues")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()
    voice, sr = sf.read(args.voice, dtype="float64", always_2d=True)
    assert sr == SR, sr
    bus = np.zeros_like(voice)
    cues = json.load(open(args.cues))
    for c in cues:
        y, peak_db = KINDS[c["kind"]]()
        y = y / (np.max(np.abs(y)) + 1e-9) * 10 ** ((peak_db + c["gain_db"]) / 20)
        i = int(round(c["t"] * SR))
        i -= int(ALIGN.get(c["kind"], 0.0) * SR)   # the sound peaks as the transition lands
        i = max(i, 0)
        m = min(len(y), len(bus) - i)
        if m <= 0:
            continue
        # slight stereo width: whooshes pan across, the rest sit centre
        pan = np.linspace(-0.6, 0.6, m) if c["kind"] in ("whoosh", "swish", "cube") else np.zeros(m)
        bus[i:i + m, 0] += y[:m] * np.sqrt((1 - pan) / 2) * np.sqrt(2)
        bus[i:i + m, 1] += y[:m] * np.sqrt((1 + pan) / 2) * np.sqrt(2)
    out = voice + bus
    peak = np.max(np.abs(out))
    if peak > 0.89:                 # keep headroom for the music mix's loudnorm
        out *= 0.89 / peak
    sf.write(args.output, out, SR, subtype="PCM_24")
    print(f"{len(cues)} cues -> {args.output}  (sfx bus peak {20 * np.log10(np.max(np.abs(bus)) + 1e-9):.1f} dBFS)")


if __name__ == "__main__":
    main()
