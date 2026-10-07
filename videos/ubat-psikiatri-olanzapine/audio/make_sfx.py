"""Synthesize transition SFX and lay them on a track that matches the edit (no samples, no licences).

Events come from graphics/sfx_events.json (written by build_graphics.py / inserts.py, so every sound sits
on the frame its animation starts) plus the "OLANZAPINE" hero slam from the caption plan.
  whoosh_in / whoosh_out / whoosh_swap  full-screen insert in / out / insert→insert   (band-passed noise sweep)
  swish                                 card panel / list row slides in                (short bright air)
  ting                                  chip / pill / icon pops                        (bell, pitch rotates)
  chime                                 quote lands on the B-roll                      (two-note bell)
  thud                                  stamp ("PALING COMMON", "VS")                  (pitch-dropped low hit)
  impact                                hero word slams behind the head                (sub boom + air burst)
User asked for SFX that are "prominent and clear", so levels are set well above a polite UI-sound bed;
tools/mix_music.py --sfx mixes this AFTER the music ducking so the voice never ducks them.

Usage: python make_sfx.py <video-for-duration> -o sfx.wav
"""

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

SR = 48000
A = Path(__file__).parent
RNG = np.random.default_rng(7)
LEVEL_DB = {"whoosh_in": -8, "whoosh_out": -11, "whoosh_swap": -9, "swish": -13, "ting": -12,
            "chime": -11, "thud": -7, "impact": -5}
MIN_GAP = {"ting": 0.22, "swish": 0.3}   # same-kind events closer than this collapse into one


def env(n, attack, release_shape=3.0):
    a = max(1, int(attack * n))
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a) ** 2
    e[a:] = (1 - np.linspace(0, 1, n - a)) ** release_shape
    return e


def sweep_noise(dur, f0, f1, q=1.6):
    """Noise through a band-pass whose centre glides f0→f1 (exponential), processed in 10ms blocks."""
    n = int(dur * SR)
    x = RNG.standard_normal(n)
    out = np.zeros(n)
    blk = SR // 100
    for i in range(0, n, blk):
        fc = f0 * (f1 / f0) ** (i / n)
        lo, hi = fc / q, min(fc * q, SR / 2 - 100)
        sos = butter(2, [lo, hi], btype="band", fs=SR, output="sos")
        out[i:i + blk] = sosfilt(sos, x[max(0, i - 2048):i + blk])[-len(x[i:i + blk]):]
    return out / (np.abs(out).max() + 1e-9)


def whoosh(kind):
    if kind == "whoosh_in":
        s = sweep_noise(0.55, 350, 4200) * env(int(0.55 * SR), 0.78, 1.5)
    elif kind == "whoosh_out":
        s = sweep_noise(0.42, 3800, 420) * env(int(0.42 * SR), 0.25, 2.2)
    else:   # swap: up then down
        s = np.concatenate([sweep_noise(0.28, 400, 4000) * env(int(0.28 * SR), 0.9, 1.0),
                            sweep_noise(0.26, 4000, 600) * env(int(0.26 * SR), 0.05, 2.0)])
    return s


def swish():
    s = sweep_noise(0.2, 2500, 7000, q=1.4)
    return s * env(len(s), 0.35, 2.5)


def bell(f0, dur=0.7, tau=0.28):
    t = np.arange(int(dur * SR)) / SR
    s = sum(a * np.sin(2 * np.pi * f0 * r * t) * np.exp(-t / (tau / (1 + 0.6 * k)))
            for k, (r, a) in enumerate([(1, 1.0), (2.76, 0.32), (5.40, 0.14), (8.93, 0.05)]))
    s *= np.minimum(1, t / 0.003)
    return s / np.abs(s).max()


TING_PITCH = [1568.0, 1760.0, 1975.5, 2093.0, 1760.0, 2349.3]


def thud():
    t = np.arange(int(0.38 * SR)) / SR
    f = 55 + 70 * np.exp(-t / 0.05)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.11)
    click = sosfilt(butter(2, [900, 3500], btype="band", fs=SR, output="sos"), RNG.standard_normal(len(t))) * np.exp(-t / 0.012)
    s = body + 0.35 * click / np.abs(click).max()
    return s / np.abs(s).max()


def impact():
    t = np.arange(int(1.4 * SR)) / SR
    f = 38 + 90 * np.exp(-t / 0.07)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.35)
    air = sosfilt(butter(2, 1200, btype="high", fs=SR, output="sos"), RNG.standard_normal(len(t))) * np.exp(-t / 0.09)
    s = boom + 0.25 * air / np.abs(air).max()
    return s / np.abs(s).max()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", args.video], text=True))
    ev = json.loads((A.parent / "graphics" / "sfx_events.json").read_text())
    cin = json.loads((A.parent / "captions" / "project" / "cinematic.json").read_text())
    tr = json.loads((A.parent / "captions" / "project" / "transcript.json").read_text())["words"]
    hero = next(l for b in cin["blocks"] for l in b["lines"] if l.get("hero"))
    hero_t = next(w["start"] for w in tr if w["text"] == hero["words"][0])
    ev.append({"t": round(hero_t - 0.02, 3), "kind": "impact", "src": "hero"})
    ev.sort(key=lambda e: e["t"])

    kept, last = [], {}
    for e in ev:
        if e["t"] - last.get(e["kind"], -9) < MIN_GAP.get(e["kind"], 0.12):
            continue
        last[e["kind"]] = e["t"]
        kept.append(e)

    track = np.zeros((int((dur + 2) * SR), 2))
    n_ting = 0
    for e in kept:
        k = e["kind"]
        if k.startswith("whoosh"):
            s = whoosh(k)
        elif k == "swish":
            s = swish()
        elif k == "ting":
            s = bell(TING_PITCH[n_ting % len(TING_PITCH)])
            n_ting += 1
        elif k == "chime":
            s = np.pad(bell(1318.5, 1.0, 0.35), (0, int(0.1 * SR))) * 0.8
            s[int(0.1 * SR):] += bell(1760.0, 1.0, 0.4)[:len(s) - int(0.1 * SR)]
            s /= np.abs(s).max()
        elif k == "thud":
            s = thud()
        elif k == "impact":
            s = impact()
        else:
            continue
        g = 10 ** (LEVEL_DB[k] / 20)
        # whooshes pan with the motion (left→right in, right→left out); bells/thuds centred
        if k.startswith("whoosh") or k == "swish":
            pan = np.linspace(-0.6, 0.6, len(s)) if k != "whoosh_out" else np.linspace(0.6, -0.6, len(s))
        else:
            pan = np.zeros(len(s))
        L, R = np.sqrt((1 - pan) / 2) * s * g, np.sqrt((1 + pan) / 2) * s * g
        i0 = int(max(0, e["t"]) * SR)
        i1 = min(len(track), i0 + len(s))
        track[i0:i1, 0] += L[:i1 - i0]
        track[i0:i1, 1] += R[:i1 - i0]
    track = track[:int(dur * SR)]
    peak = np.abs(track).max()
    if peak > 0.89:
        track *= 0.89 / peak
    sf.write(args.output, track, SR, subtype="PCM_24")
    counts = {}
    for e in kept:
        counts[e["kind"]] = counts.get(e["kind"], 0) + 1
    print(f"{len(kept)} sfx ({len(ev) - len(kept)} collapsed) {counts} → {args.output}, peak {20 * np.log10(peak + 1e-9):.1f} dBFS")


if __name__ == "__main__":
    main()
