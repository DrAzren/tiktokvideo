"""Synthesize a small, original UI sound-effect kit (no samples, no licences), 48 kHz stereo WAV.

    whoosh  band-passed noise sweeping up then down, cubic swell and fade (~0.55 s)
    pop     sine with a fast pitch drop + tiny noise transient (~0.12 s)
    tick    short filtered click (~0.04 s)
    stamp   low thud (pitch-dropping sine) + paper slap noise burst (~0.35 s)
    chime   two soft bell notes (inharmonic partials, exponential decay) (~1.4 s)

Each file is peak-normalised to -3 dBFS; set the mix level where they are placed.
Usage: python tools/sfx_synth.py <out_dir>
"""

import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

SR = 48000
rng = np.random.default_rng(7)


def t(d):
    return np.arange(int(d * SR)) / SR


def norm(x, db=-3.0):
    x = x - np.mean(x)
    return x / (np.max(np.abs(x)) + 1e-12) * 10 ** (db / 20)


def fade(x, a=0.002, r=0.01):
    n = len(x)
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na) ** 2
    e[n - nr:] = np.linspace(1, 0, nr) ** 2
    return x * e


def whoosh():
    d = 0.55
    tt = t(d)
    noise = rng.standard_normal(len(tt))
    out = np.zeros_like(tt)
    # sweep a band-pass centre 400 Hz -> 3.2 kHz -> 1.2 kHz in 10 ms blocks
    blk = int(0.01 * SR)
    for i in range(0, len(tt), blk):
        p = i / len(tt)
        fc = 400 * (8 ** (p / 0.6)) if p < 0.6 else 3200 * (0.375 ** ((p - 0.6) / 0.4))
        sos = butter(2, [fc * 0.6, min(fc * 1.6, 20000)], btype="band", fs=SR, output="sos")
        seg = noise[max(0, i - 2 * blk):i + blk]
        out[i:i + blk] = sosfilt(sos, seg)[-len(out[i:i + blk]):]
    env = np.where(tt < d * 0.6, (tt / (d * 0.6)) ** 3, (1 - (tt - d * 0.6) / (d * 0.4)) ** 2)
    x = out * env
    return np.stack([x * (0.85 + 0.15 * np.sin(2 * np.pi * 1.5 * tt)), x * (0.85 - 0.15 * np.sin(2 * np.pi * 1.5 * tt))], 1)


def pop():
    tt = t(0.12)
    f = 900 * np.exp(-tt * 35) + 320
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-tt * 38)
    x[:int(0.004 * SR)] += rng.standard_normal(int(0.004 * SR)) * 0.25
    return fade(x, 0.001, 0.02)


def tick():
    tt = t(0.04)
    x = rng.standard_normal(len(tt)) * np.exp(-tt * 260)
    x = sosfilt(butter(2, [2500, 7000], btype="band", fs=SR, output="sos"), x)
    x += 0.5 * np.sin(2 * np.pi * 2200 * tt) * np.exp(-tt * 200)
    return fade(x, 0.0005, 0.01)


def stamp():
    tt = t(0.35)
    f = 140 * np.exp(-tt * 18) + 55
    thud = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 14)
    slap = sosfilt(butter(2, [700, 4500], btype="band", fs=SR, output="sos"), rng.standard_normal(len(tt))) * np.exp(-tt * 55)
    return fade(1.0 * thud + 0.55 * slap / np.max(np.abs(slap)), 0.0008, 0.05)


def chime():
    d = 1.4
    tt = t(d)
    x = np.zeros_like(tt)
    for start, f0 in ((0.0, 1046.5), (0.16, 1568.0)):  # C6 then G6
        m = tt >= start
        tl = tt[m] - start
        for ratio, amp, dec in ((1.0, 1.0, 3.2), (2.76, 0.35, 6.0), (5.40, 0.12, 9.0)):
            x[m] += amp * np.sin(2 * np.pi * f0 * ratio * tl) * np.exp(-tl * dec) * (1 - np.exp(-tl * 400))
    return fade(x, 0.001, 0.08)


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in (("whoosh", whoosh), ("pop", pop), ("tick", tick), ("stamp", stamp), ("chime", chime)):
        x = norm(fn())
        if x.ndim == 1:
            x = np.stack([x, x], 1)
        sf.write(out / f"{name}.wav", x.astype(np.float32), SR)
        print(f"{name}: {len(x) / SR:.2f}s")


if __name__ == "__main__":
    main()
