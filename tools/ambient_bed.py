"""Synthesize an original, royalty-free ambient music bed (no samples, no licences).

A slow four-chord pad (additive, detuned, soft harmonics) plus a sparse, quiet
keys arpeggio, through a generated-IR reverb. Deterministic: same args → same file.
Meant to sit UNDER speech — mix it with tools/mix_music.py (sidechain ducking).

Usage:
    python tools/ambient_bed.py -o bed.wav --duration 149.3 [--key D] [--bpm 64] [--no-keys]
"""

from __future__ import annotations

import argparse

import numpy as np
import soundfile as sf

SR = 48000
NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
# I maj9 – vi m9 – IV maj9 – V sus2, as semitone offsets from the tonic (voiced low → high)
PROGRESSION = [[0, 7, 11, 14, 16], [-3, 4, 7, 11, 14], [-7, 0, 4, 11, 14], [-5, 2, 7, 9, 14]]


def hz(midi: float) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def pad_note(f: float, n: int, rng: np.random.Generator) -> np.ndarray:
    t = np.arange(n) / SR
    out = np.zeros(n)
    for detune in (-0.0025, 0.0, 0.0025):          # ±4 cents chorus
        ph = rng.uniform(0, 2 * np.pi)
        for k, a in ((1, 1.0), (2, 0.32), (3, 0.10), (4, 0.04)):
            out += a * np.sin(2 * np.pi * f * k * (1 + detune) * t + ph * k)
    return out / 3


def keys_note(f: float, n: int) -> np.ndarray:
    t = np.arange(n) / SR
    env = (1 - np.exp(-t / 0.004)) * np.exp(-t / 0.55)
    return env * (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) + 0.06 * np.sin(6 * np.pi * f * t))


def reverb(x: np.ndarray, seconds: float = 2.8, seed: int = 3) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    ir = rng.standard_normal((n, 2)) * np.exp(-np.arange(n) / (SR * seconds / 6.9))[:, None]
    ir[:, 0] *= 1.0
    ir[:, 1] *= 0.97
    size = 1 << int(np.ceil(np.log2(len(x) + n)))
    wet = np.stack([np.fft.irfft(np.fft.rfft(x[:, c], size) * np.fft.rfft(ir[:, c], size), size)[:len(x)]
                    for c in range(2)], axis=1)
    return wet / (np.max(np.abs(wet)) + 1e-9)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--key", default="D", choices=list(NOTE))
    ap.add_argument("--bpm", type=float, default=64)
    ap.add_argument("--no-keys", action="store_true")
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    n = int(args.duration * SR)
    beat = 60 / args.bpm
    chord_len = 8 * beat                              # two bars of 4/4 per chord
    xfade = 2 * beat
    root = 48 + NOTE[args.key]                        # tonic around C3–B3
    mix = np.zeros((n, 2))

    # pad: overlapping raised-cosine chord envelopes
    i = 0
    while i * chord_len < args.duration + chord_len:
        start = i * chord_len - xfade / 2
        seg = int((chord_len + xfade) * SR)
        s0 = int(start * SR)
        env_t = np.linspace(0, 1, seg)
        env = np.clip(np.minimum(env_t * (chord_len + xfade) / xfade, (1 - env_t) * (chord_len + xfade) / xfade), 0, 1)
        env = 0.5 - 0.5 * np.cos(np.pi * env)
        chord = PROGRESSION[i % len(PROGRESSION)]
        voice = sum(pad_note(hz(root + s), seg, rng) * (0.9 if s < 5 else 0.6) for s in chord) * env
        pan = 0.5 + 0.15 * np.sin(i * 1.7)
        a, b = max(0, s0), min(n, s0 + seg)
        if b > a:
            mix[a:b, 0] += voice[a - s0:b - s0] * (1 - pan)
            mix[a:b, 1] += voice[a - s0:b - s0] * pan
        i += 1
    mix /= np.max(np.abs(mix)) + 1e-9

    if not args.no_keys:                              # sparse arpeggio: one note every 2 beats
        keys = np.zeros((n, 2))
        step, k = 2 * beat, 0
        while k * step < args.duration:
            t0 = k * step
            chord = PROGRESSION[int(t0 // chord_len) % len(PROGRESSION)]
            note = root + 12 + chord[[1, 3, 2, 4][k % 4]]
            seg = min(int(2.5 * SR), n - int(t0 * SR))
            v = keys_note(hz(note), seg) * (0.55 + 0.2 * ((k * 7) % 3) / 2)
            pan = 0.3 + 0.4 * ((k * 5) % 4) / 3
            s0 = int(t0 * SR)
            keys[s0:s0 + seg, 0] += v * (1 - pan)
            keys[s0:s0 + seg, 1] += v * pan
            k += 1
        mix += 0.22 * keys / (np.max(np.abs(keys)) + 1e-9)

    wet = reverb(mix)
    out = 0.55 * mix / (np.max(np.abs(mix)) + 1e-9) + 0.45 * wet
    tremolo = 1 + 0.06 * np.sin(2 * np.pi * 0.07 * np.arange(n) / SR)
    out *= tremolo[:, None]
    fade_in, fade_out = int(2.0 * SR), int(3.0 * SR)
    out[:fade_in] *= np.linspace(0, 1, fade_in)[:, None]
    out[-fade_out:] *= np.linspace(1, 0, fade_out)[:, None]
    out *= 10 ** (-3 / 20) / (np.max(np.abs(out)) + 1e-9)   # peak -3 dBFS; level is set in the mix
    sf.write(args.output, out.astype(np.float32), SR, subtype="PCM_24")
    print(f"wrote {args.output} ({args.duration:.1f}s, key {args.key}, {args.bpm:g} bpm)")


if __name__ == "__main__":
    main()
