"""Synthesize an original "cinematic ambient piano with a gentle modern pulse" bed (no samples, no licences).

Layers: a soft felt-piano chord on every bar plus a sparse melody (additive partials with slight
inharmonicity, per-partial decay, hammer noise), a warm pad underneath, and a muted pulse
(sub thump on beats 1 and 3, a quiet filtered tick on the off-beats) — all through a generated
stereo reverb. The last bars resolve on the tonic and ring out. Deterministic.
Meant to sit UNDER speech: mix with sidechain ducking (tools/mix_music.py or a project mix).

Usage:
    python tools/piano_bed.py -o bed.wav --duration 119.6 [--key D] [--bpm 72] [--no-pulse]
"""

from __future__ import annotations

import argparse

import numpy as np
import soundfile as sf

SR = 48000
NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
# vi m7 – IV maj7 – I add9 – V sus4, voiced from the tonic (semitones); warm, unresolved, hopeful
PROG = [[-3, 4, 7, 12, 16], [-7, 4, 9, 12, 16], [0, 7, 12, 14, 16], [-5, 5, 7, 12, 14]]
TONIC = [0, 7, 12, 16, 19]


def hz(m: float) -> float:
    return 440.0 * 2 ** ((m - 69) / 12)


def piano(f: float, seconds: float, vel: float, rng: np.random.Generator) -> np.ndarray:
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    B = 0.00018                                        # string inharmonicity
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + B * k * k)
        if fk > 9000:
            break
        amp = (0.9 ** (k - 1)) / k ** 0.6 * (1.0 if k > 1 else 1.25)
        dec = 3.2 / (1 + 0.45 * (k - 1)) * (220 / max(f, 110)) ** 0.35
        out += amp * np.exp(-t / dec) * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28))
    att = 1 - np.exp(-t / 0.006)
    hammer = rng.standard_normal(n) * np.exp(-t / 0.010) * 0.015
    felt = np.convolve(out * att + hammer, np.ones(10) / 10, mode="same")   # felt: soften the top
    return vel * felt


def pad(f: float, n: int) -> np.ndarray:
    t = np.arange(n) / SR
    return sum(a * np.sin(2 * np.pi * f * k * (1 + d) * t) for k, a in ((1, 1), (2, .25)) for d in (-.002, .002)) / 4


def reverb(x: np.ndarray, seconds: float = 3.2, seed: int = 5) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    env = np.exp(-np.arange(n) / (SR * seconds / 6.9))
    ir = rng.standard_normal((n, 2)) * env[:, None]
    ir[: int(0.012 * SR)] = 0                          # pre-delay
    size = 1 << int(np.ceil(np.log2(len(x) + n)))
    wet = np.stack([np.fft.irfft(np.fft.rfft(x[:, c], size) * np.fft.rfft(ir[:, c], size), size)[:len(x)] for c in range(2)], 1)
    return wet / (np.max(np.abs(wet)) + 1e-9)


def lowpass(x: np.ndarray, hz_: float) -> np.ndarray:
    a = np.exp(-2 * np.pi * hz_ / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):                            # one-pole; only used on short hits
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--key", default="D", choices=list(NOTE))
    ap.add_argument("--bpm", type=float, default=72)
    ap.add_argument("--no-pulse", action="store_true")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    n = int((a.duration + 4) * SR)
    beat = 60 / a.bpm
    bar = 4 * beat
    root = 50 + NOTE[a.key] - NOTE["D"]                # D3 for D
    dry = np.zeros((n, 2))
    nbars = int(np.ceil(a.duration / bar))
    for b in range(nbars + 1):
        t0 = b * bar
        last = b >= nbars - 1
        chord = TONIC if last else PROG[(b // 2) % len(PROG)]
        if b % 2 == 0 or last:                         # chord every two bars, rolled like a pianist
            for j, s in enumerate(chord):
                v = piano(hz(root + s), 6.0 if last else 4.5, 0.55 if j else 0.7, rng)
                s0 = int((t0 + 0.035 * j) * SR)
                e0 = min(n, s0 + len(v))
                pan = 0.35 + 0.3 * j / len(chord)
                dry[s0:e0, 0] += v[:e0 - s0] * (1 - pan)
                dry[s0:e0, 1] += v[:e0 - s0] * pan
        if not last:                                   # sparse melody: beats 2 and 4, upper chord tones
            for k, beat_i in enumerate((1, 3)):
                if (b + k) % 3 == 2:
                    continue
                m = root + 12 + chord[[2, 3, 4][(b + k) % 3]]
                v = piano(hz(m), 3.0, 0.32, rng)
                s0 = int((t0 + beat_i * beat) * SR)
                e0 = min(n, s0 + len(v))
                dry[s0:e0, 0] += v[:e0 - s0] * 0.45
                dry[s0:e0, 1] += v[:e0 - s0] * 0.55
        seg = int(2 * bar * SR)                        # pad under each two-bar chord
        if b % 2 == 0:
            s0 = int(t0 * SR)
            e0 = min(n, s0 + seg)
            env = np.sin(np.linspace(0, np.pi, seg)) ** 1.5
            p = sum(pad(hz(root - 12 + s), seg) for s in chord[:3]) * env * 0.18
            dry[s0:e0] += p[:e0 - s0, None]
    dry /= np.max(np.abs(dry)) + 1e-9
    out = 0.6 * dry + 0.5 * reverb(dry)

    if not a.no_pulse:                                 # gentle modern pulse, enters after the first 2 bars
        pulse = np.zeros((n, 2))
        tk = int(0.25 * SR)
        tt = np.arange(tk) / SR
        thump = np.sin(2 * np.pi * (52 + 30 * np.exp(-tt / 0.03)) * tt) * np.exp(-tt / 0.12)
        tick = lowpass(rng.standard_normal(int(0.05 * SR)) * np.exp(-np.arange(int(0.05 * SR)) / (0.008 * SR)), 4500)
        k = 8
        while k * beat < a.duration - 2 * bar:
            s0 = int(k * beat * SR)
            if k % 2 == 0:
                pulse[s0:s0 + tk] += thump[:, None] * 0.55
            off = int((k + 0.5) * beat * SR)
            pulse[off:off + len(tick), 0] += tick * 0.10
            pulse[off:off + len(tick), 1] += tick * 0.13
            k += 1
        out += pulse
    out = out[:int(a.duration * SR)]
    fi, fo = int(1.5 * SR), int(3.0 * SR)
    out[:fi] *= np.linspace(0, 1, fi)[:, None]
    out[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
    out *= 10 ** (-3 / 20) / (np.max(np.abs(out)) + 1e-9)
    sf.write(a.output, out.astype(np.float32), SR, subtype="PCM_24")
    print(f"wrote {a.output} ({a.duration:.1f}s, key {a.key}, {a.bpm:g} bpm)")


if __name__ == "__main__":
    main()
