"""Synth instruments shared with Episode 1's score (strings, drone, piano, pluck, impact, whoosh, tick, noise beds,
paper, ink, footstep, glass, blip, frame drum, reverb). Pure numpy/scipy, deterministic."""

import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
rng = np.random.default_rng(7)


def hz(m: float) -> float:
    return 440.0 * 2 ** ((m - 69) / 12)


def t_(n: int) -> np.ndarray:
    return np.arange(n) / SR


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x, axis=0)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x, axis=0)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x, axis=0)


def add(bus, sig, t0, pan=0.5, gain=1.0):
    """Add a mono signal to a stereo bus at time t0 (s) with equal-power pan."""
    n = len(bus)
    s0 = int(round(t0 * SR))
    if s0 >= n:
        return
    if s0 < 0:
        sig, s0 = sig[-s0:], 0
    sig = sig[: n - s0]
    l, r = np.cos(pan * np.pi / 2), np.sin(pan * np.pi / 2)
    bus[s0:s0 + len(sig), 0] += sig * gain * l * 1.414
    bus[s0:s0 + len(sig), 1] += sig * gain * r * 1.414


def env_ar(n, att, rel):
    e = np.ones(n)
    a, r = int(att * SR), int(rel * SR)
    if a:
        e[:a] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, a))   # cubic-ish (raised cosine) swell, never linear
    if r:
        e[-r:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, r))
    return e


def reverb(x, seconds=3.0, seed=3, damp=6000):
    g = np.random.default_rng(seed)
    n = int(seconds * SR)
    ir = g.standard_normal((n, 2)) * np.exp(-np.arange(n) / (SR * seconds / 6.9))[:, None]
    ir = lp(ir, damp)
    ir[: int(0.012 * SR)] = 0                      # pre-delay
    size = 1 << int(np.ceil(np.log2(len(x) + n)))
    wet = np.stack([np.fft.irfft(np.fft.rfft(x[:, c], size) * np.fft.rfft(ir[:, c], size), size)[: len(x)] for c in range(2)], 1)
    return wet / (np.max(np.abs(wet)) + 1e-9) * (np.max(np.abs(x)) + 1e-9)


# ------------------------------------------------------------------ instruments
def strings(notes, dur, att=2.0, rel=2.5, bright=2200, seed=0):
    n = int(dur * SR)
    t = t_(n)
    g = np.random.default_rng(seed)
    out = np.zeros(n)
    for m in notes:
        f = hz(m)
        for det in (-0.004, 0.0, 0.0045):
            vib = 1 + 0.0025 * np.sin(2 * np.pi * (4.6 + g.uniform(-.4, .4)) * t + g.uniform(0, 6.28))
            ph = np.cumsum(2 * np.pi * f * (1 + det) * vib / SR) + g.uniform(0, 6.28)
            saw = 2 * ((ph / (2 * np.pi)) % 1.0) - 1
            out += saw
    out = lp(lp(out, bright), bright * 1.3)
    out = hp(out, 70)
    return out * env_ar(n, att, rel) / (len(notes) * 3)


def drone(m, dur, att=3.0, rel=3.0):
    n = int(dur * SR)
    t = t_(n)
    f = hz(m)
    lfo = 1 + 0.25 * np.sin(2 * np.pi * 0.09 * t)
    x = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2 * f * t + 1) * lfo + 0.2 * np.sin(2 * np.pi * 3.01 * f * t)
    return x * env_ar(n, att, rel) / 1.7


def piano(m, dur=3.5, vel=1.0):
    n = int(dur * SR)
    t = t_(n)
    f = hz(m)
    B = 0.0004
    x = np.zeros(n)
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + B * k * k)
        if fk > 12000:
            break
        x += (0.9 ** k) / k ** 0.6 * np.sin(2 * np.pi * fk * t) * np.exp(-t * (0.9 + 0.55 * k))
    ham = np.random.default_rng(int(m)).standard_normal(int(0.006 * SR)) * np.exp(-np.arange(int(0.006 * SR)) / 60)
    x[: len(ham)] += 0.05 * ham
    x *= (1 - np.exp(-t / 0.002))
    return lp(x, 5000 + 3000 * vel) * vel * 0.5


def pluck(m, dur=2.5, seed=1):
    """Karplus-Strong harp-like pluck."""
    n = int(dur * SR)
    p = int(SR / hz(m))
    g = np.random.default_rng(seed)
    buf = lp(g.uniform(-1, 1, p), 3000)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.996 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out * 0.6


def impact(dur=3.5, level=1.0, low=34):
    n = int(dur * SR)
    t = t_(n)
    f = low + 70 * np.exp(-t / 0.08)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.9)
    nz = lp(rng.standard_normal(n), 900) * np.exp(-t / 0.12) * 0.6
    return (boom + nz) * level


def whoosh(dur=1.6, level=1.0, reverse=False, lo=300, hi=4000):
    n = int(dur * SR)
    x = rng.standard_normal(n)
    out = np.zeros(n)
    steps = 24
    for i in range(steps):          # moving band-pass sweep, cross-faded in chunks
        a, b = i * n // steps, (i + 1) * n // steps
        fc = lo * (hi / lo) ** (i / (steps - 1))
        seg = bp(x, fc * 0.7, min(fc * 1.4, SR / 2 - 100))[a:b]
        out[a:b] = seg
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    if reverse:
        e = np.linspace(0, 1, n) ** 3
    return out * e * level


def tick(hi=True):
    n = int(0.06 * SR)
    t = t_(n)
    f = 2900 if hi else 2300
    return (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.006) + 0.4 * hp(rng.standard_normal(n), 3000) * np.exp(-t / 0.002)) * 0.5


def noise_bed(dur, lo, hi, att=1.5, rel=1.5, mod=0.0, seed=0):
    n = int(dur * SR)
    g = np.random.default_rng(seed)
    x = bp(g.standard_normal(n), lo, hi)
    if mod:
        x *= 1 + 0.5 * np.sin(2 * np.pi * mod * t_(n) + g.uniform(0, 6))
    return x * env_ar(n, att, rel)


def paper(dur=1.4, seed=0):
    n = int(dur * SR)
    g = np.random.default_rng(seed)
    imp = (g.uniform(0, 1, n) > 0.9965) * g.uniform(-1, 1, n)
    crack = bp(imp, 1200, 7000) * 6
    rustle = bp(g.standard_normal(n), 1500, 6000) * 0.35 * (0.5 + 0.5 * np.sin(2 * np.pi * 3.1 * t_(n)))
    return (crack + rustle) * env_ar(n, 0.15, 0.4)


def ink(dur=1.6, seed=0):
    n = int(dur * SR)
    g = np.random.default_rng(seed)
    am = np.abs(np.sin(2 * np.pi * (9 + 6 * np.sin(2 * np.pi * 0.7 * t_(n))) * t_(n))) ** 3
    return bp(g.standard_normal(n), 2500, 8000) * am * env_ar(n, 0.1, 0.3) * 0.5


def footstep():
    n = int(0.5 * SR)
    t = t_(n)
    return (np.sin(2 * np.pi * (60 + 40 * np.exp(-t / 0.02)) * t) * np.exp(-t / 0.09)
            + 0.3 * lp(rng.standard_normal(n), 1500) * np.exp(-t / 0.03))


def glass(seed=0):
    n = int(1.8 * SR)
    t = t_(n)
    g = np.random.default_rng(seed)
    base = g.uniform(1900, 2400)
    x = sum(a * np.sin(2 * np.pi * base * r * t + g.uniform(0, 6)) * np.exp(-t / d)
            for r, a, d in ((1, 1, .9), (2.32, .5, .6), (3.71, .3, .4), (5.12, .15, .25)))
    return x * 0.25


def blip(f=880, dur=0.18):
    n = int(dur * SR)
    t = t_(n)
    return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.05) * (1 - np.exp(-t / 0.003)) * 0.4


def frame_drum():
    n = int(0.9 * SR)
    t = t_(n)
    return (np.sin(2 * np.pi * (70 + 60 * np.exp(-t / 0.03)) * t) * np.exp(-t / 0.22)
            + 0.25 * bp(rng.standard_normal(n), 200, 1800) * np.exp(-t / 0.04))


