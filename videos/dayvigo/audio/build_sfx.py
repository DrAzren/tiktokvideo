"""Synthesize the sound-design track for 'Ubat Psikiatri Dayvigo' from graphics/sfx_cues.json.

No samples, no licences: every sound is generated here (numpy), deterministic per cue (seeded by
time + kind), and varied per instance (pitch / length / filter / pan) so no two hits are identical.
Each cue sits on the same clock as the animation that causes it (build_graphics.py emits both).
Directional sounds pan right → left with the film's current.

Output: audio/sfx.wav (48 kHz stereo float), peak-normalised to -6 dBFS; mixed under the voice by mix.py.
"""

import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

A = Path(__file__).parent
SR = 48000
cues = json.loads((A.parent / "graphics" / "sfx_cues.json").read_text())
DUR = cues["duration"]


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype="high", fs=SR, output="sos"), x)


def env(n, a, d, shape=3.0):
    """attack fraction a (0..1) then a curved decay."""
    t = np.linspace(0, 1, n)
    na = max(1, int(n * a))
    e = np.ones(n)
    e[:na] = (t[:na] / max(t[na - 1], 1e-9)) ** 2
    e[na:] = (1 - (t[na:] - t[na]) / max(1 - t[na], 1e-9)) ** (shape * d)
    return e


def swept_noise(r, n, f0, f1, q=0.6):
    """noise through a band-pass whose centre sweeps f0 → f1 (block-wise, cheap)."""
    x = r.standard_normal(n)
    out = np.zeros(n)
    blk = 512
    for i in range(0, n, blk):
        fc = f0 * (f1 / f0) ** (i / max(n - 1, 1))
        lo, hi = max(40, fc * (1 - q / 2)), min(SR / 2 - 100, fc * (1 + q / 2))
        out[i:i + blk] = bp(x[i:i + blk + 256], lo, hi)[:len(out[i:i + blk])]
    return out


def tone(n, f0, f1, decay):
    t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / max(t[-1], 1e-9))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay)


def pan(x, p0, p1=None):
    """equal-power pan, -1 = left, +1 = right; p0 → p1 across the sound."""
    p = np.linspace(p0, p0 if p1 is None else p1, len(x))
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1)


def synth(kind, r, dur=None):
    v = r.uniform(0.85, 1.18)   # per-instance variation
    if kind in ("whoosh", "whoosh_soft", "whoosh_text", "swish"):
        L = {"whoosh": 0.5, "whoosh_soft": 0.32, "whoosh_text": 0.24, "swish": 0.2}[kind] * v
        n = int(L * SR)
        f0, f1 = {"whoosh": (380, 3400), "whoosh_soft": (2400, 500), "whoosh_text": (1500, 6500), "swish": (2500, 7000)}[kind]
        x = swept_noise(r, n, f0 * v, f1 * v) * env(n, 0.62 if kind == "whoosh" else 0.4, 0.6)
        g = {"whoosh": 1.0, "whoosh_soft": 0.55, "whoosh_text": 0.5, "swish": 0.4}[kind]
        return pan(x * g, 0.6, -0.6)
    if kind == "paper_slide":
        n = int(0.26 * v * SR)
        grit = 1 + 0.6 * np.repeat(r.standard_normal(n // 240 + 1), 240)[:n]
        x = bp(r.standard_normal(n), 900 * v, 5200) * grit * env(n, 0.25, 0.7)
        return pan(x * 0.55, 0.4, -0.3)
    if kind == "paper_tear":
        n = int(0.5 * v * SR)
        clicks = (r.random(n) < 0.035).astype(float) * r.uniform(0.3, 1.0, n)
        crackle = bp(clicks, 1400, 7000) * 3.0
        fiber = bp(r.standard_normal(n), 2000, 6000) * 0.35
        x = (crackle + fiber) * env(n, 0.7, 0.25)
        return pan(x * 0.9, 0.7, -0.7)
    if kind == "slap":
        n = int(0.22 * SR)
        t = np.arange(n) / SR
        thump = np.sin(2 * np.pi * 120 * v * t) * np.exp(-t / 0.035)
        snap = hp(r.standard_normal(n), 1200) * np.exp(-t / 0.012)
        rustle = bp(r.standard_normal(n), 1500, 5000) * np.exp(-t / 0.06) * 0.25
        return pan((thump * 0.8 + snap * 0.7 + rustle) * 0.8, r.uniform(-0.3, 0.3))
    if kind == "pop":
        n = int(0.12 * SR)
        x = tone(n, 950 * v, 320 * v, 0.035) + hp(r.standard_normal(n), 3000) * np.exp(-np.arange(n) / SR / 0.004) * 0.3
        return pan(x * 0.5, r.uniform(-0.2, 0.2))
    if kind == "tick":
        n = int(0.09 * SR)
        t = np.arange(n) / SR
        x = hp(r.standard_normal(n), 2500) * np.exp(-t / 0.003) + np.sin(2 * np.pi * 3100 * v * t) * np.exp(-t / 0.015) * 0.4
        return pan(x * 0.4, r.uniform(-0.3, 0.3))
    if kind in ("marker", "scribble"):
        L = (dur or 0.35) * (1.0 if kind == "scribble" else v)
        n = int(L * SR)
        t = np.arange(n) / SR
        rate = r.uniform(6, 9) if kind == "scribble" else 2.5
        strokes = 0.55 + 0.45 * np.abs(np.sin(np.pi * rate * t))
        x = bp(r.standard_normal(n), 1800 * v, 4800) * strokes * env(n, 0.08, 0.3)
        squeak = np.sin(2 * np.pi * (2300 * v + 300 * np.sin(2 * np.pi * rate * t)) * t) * 0.06
        return pan((x + squeak) * 0.6, 0.3, -0.3)
    if kind == "stamp":
        n = int(0.42 * SR)
        t = np.arange(n) / SR
        x = (np.sin(2 * np.pi * 72 * t) * np.exp(-t / 0.09) * 1.0 + np.sin(2 * np.pi * 210 * v * t) * np.exp(-t / 0.04) * 0.5
             + lp(r.standard_normal(n), 2500) * np.exp(-t / 0.02) * 0.8)
        return pan(x * 0.9, 0.0)
    if kind == "impact":
        n = int(1.4 * SR)
        t = np.arange(n) / SR
        boom = tone(n, 62 * v, 36, 0.45)
        trans = lp(r.standard_normal(n), 3500) * np.exp(-t / 0.018) * 0.6
        tail = lp(r.standard_normal(n), 900) * np.exp(-t / 0.35) * 0.12
        return pan((boom + trans + tail) * 0.95, 0.0)
    if kind == "drop":
        n = int(1.5 * SR)
        x = tone(n, 95, 28, 0.6) + lp(r.standard_normal(n), 1500) * np.exp(-np.arange(n) / SR / 0.05) * 0.4
        return pan(x * 0.9, 0.0)
    if kind == "riser":
        L = dur or 0.7
        n = int(L * SR)
        t = np.linspace(0, 1, n)
        x = swept_noise(r, n, 600, 6000, 0.5) * t ** 2.2 + tone(n, 180, 720, 10.0) * t ** 2.5 * 0.25
        return pan(x * 0.7, -0.4, 0.4)
    if kind == "thud":
        n = int(0.25 * SR)
        t = np.arange(n) / SR
        x = np.sin(2 * np.pi * 88 * v * t) * np.exp(-t / 0.05) + lp(r.standard_normal(n), 1800) * np.exp(-t / 0.01) * 0.5
        return pan(x * 0.8, r.uniform(-0.3, 0.3))
    if kind == "creak":
        n = int(0.6 * SR)
        t = np.arange(n) / SR
        f = 160 * v * (1 + 0.15 * np.sin(2 * np.pi * 3 * t))
        saw = 2 * ((np.cumsum(f) / SR) % 1) - 1
        jitter = 1 + 0.5 * np.repeat(r.standard_normal(n // 300 + 1), 300)[:n]
        x = bp(saw * jitter, 300, 2200) * env(n, 0.2, 0.6)
        return pan(x * 0.25, 0.3)
    if kind == "click":
        n = int(0.12 * SR)
        t = np.arange(n) / SR
        c = np.zeros(n)
        for k, a in ((0, 1.0), (int(0.016 * SR), 0.6)):
            c[k:] += a * (hp(r.standard_normal(n - k), 1800) * np.exp(-t[:n - k] / 0.004)
                          + np.sin(2 * np.pi * 2600 * t[:n - k]) * np.exp(-t[:n - k] / 0.01) * 0.5)
        return pan(c * 0.9, 0.2)
    if kind == "clock":
        n = int(0.9 * SR)
        x = np.zeros(n)
        for k, f in ((0, 3300), (int(0.5 * SR), 2600)):
            m = int(0.06 * SR)
            t = np.arange(m) / SR
            x[k:k + m] += hp(r.standard_normal(m), 2000) * np.exp(-t / 0.004) + np.sin(2 * np.pi * f * t) * np.exp(-t / 0.012) * 0.5
        return pan(x * 0.5, 0.0)
    if kind.startswith("amb_"):
        L = dur or 3.0
        n = int(L * SR)
        t = np.arange(n) / SR
        bed = lp(r.standard_normal(n), 700) * 0.18
        if kind == "amb_night":    # crickets + ceiling-fan air
            x = bed + lp(r.standard_normal(n), 450) * (0.5 + 0.5 * np.sin(2 * np.pi * 1.6 * t)) * 0.12
            for _ in range(3):
                f, rate, period, off = r.uniform(4200, 5200), r.uniform(26, 34), r.uniform(0.55, 0.9), r.uniform(0, 0.5)
                gate = ((t + off) % period < 0.16) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * rate * t)))
                x += np.sin(2 * np.pi * f * t) * lp(gate.astype(float), 200) * 0.05
        elif kind == "amb_office":  # aircon + faint keys
            x = bed * 1.2 + np.sin(2 * np.pi * 120 * t) * 0.006
            for k in r.uniform(0.2, L - 0.1, int(L * 3)):
                i = int(k * SR)
                m = min(int(0.02 * SR), n - i)
                x[i:i + m] += hp(r.standard_normal(m), 2500) * np.exp(-np.arange(m) / SR / 0.004) * 0.06
        elif kind == "amb_morning":  # birds outside + soft room
            x = bed * 0.8
            for k in r.uniform(0.3, L - 0.4, int(L * 1.6)):
                i = int(k * SR)
                m = min(int(r.uniform(0.07, 0.16) * SR), n - i)
                tt = np.arange(m) / SR
                f0 = r.uniform(2600, 4200)
                x[i:i + m] += np.sin(2 * np.pi * (f0 + 900 * np.sin(2 * np.pi * r.uniform(15, 30) * tt)) * tt) \
                    * np.sin(np.pi * tt / tt[-1]) * 0.05
        elif kind == "amb_ward":     # fluorescent hum + distant monitor beep
            x = bed + (np.sin(2 * np.pi * 100 * t) + 0.4 * np.sin(2 * np.pi * 200 * t)) * 0.01
            for k in np.arange(r.uniform(0.4, 1.0), L - 0.2, 1.9):
                i = int(k * SR)
                m = min(int(0.11 * SR), n - i)
                x[i:i + m] += np.sin(2 * np.pi * 980 * np.arange(m) / SR) * np.sin(np.pi * np.arange(m) / m) * 0.025
        else:                        # amb_clinic: calm room tone, a little air
            x = bed * 0.9 + lp(r.standard_normal(n), 2500) * 0.02
        fade = np.minimum(1, np.minimum(t / 0.35, (L - t) / 0.35))
        st = pan(x * fade, -0.15)
        st[:, 1] = np.roll(st[:, 1], 240)  # a little width
        return st
    raise KeyError(kind)


def main() -> None:
    out = np.zeros((int((DUR + 2) * SR), 2))
    for c in cues["cues"]:
        r = np.random.default_rng(int(c["t"] * 1000) * 31 + sum(map(ord, c["kind"])))
        s = synth(c["kind"], r, c.get("dur"))
        s = s / (np.abs(s).max() + 1e-9) * 10 ** (c["gain"] / 20)
        i = int(c["t"] * SR)
        out[i:i + len(s)] += s[:len(out) - i]
    out = out[:int(DUR * SR)]
    out = hp(out.T, 60).T                     # keep the sub-lows out of the voice mix
    out *= 10 ** (-6 / 20) / (np.abs(out).max() + 1e-9)
    sf.write(A / "sfx.wav", out.astype(np.float32), SR, subtype="FLOAT")
    print(f"{len(cues['cues'])} cues → sfx.wav ({DUR:.2f}s)")


if __name__ == "__main__":
    main()
