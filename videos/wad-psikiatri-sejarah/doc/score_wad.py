"""Original score + sound design for 'Sejarah Wad Psikiatri di Malaysia', mixed under the user's narration.

Cues are anchored to the same narration phrases as the picture (build_wad.T). Music is sidechain-ducked under the
voice. Writes ../audio/mix_premaster.wav plus stems. Master with loudnorm (see assemble.sh).
Run: ../../../.venv/bin/python score_wad.py
"""

import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt

import build_wad as bw
from synth import (SR, add, bp, drone, footstep, frame_drum, glass, impact, ink, noise_bed, paper, piano, pluck, reverb,
                   strings, t_, tick, whoosh, blip, env_ar)

D = Path(__file__).parent
A = D.parent / "audio"
T = bw.T
DUR = bw.DUR
N = int(DUR * SR)
S = {s[0]: s[3] for s in bw.SHOTS}


def crickets(dur, seed=0):
    n = int(dur * SR)
    g = np.random.default_rng(seed)
    x = bp(g.standard_normal(n), 4200, 5200)
    am = (np.sin(2 * np.pi * 28 * t_(n)) > 0.2) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.6 * t_(n) + g.uniform(0, 6)))
    return x * am * env_ar(n, 1.5, 1.5) * 0.6


def heartbeat(n_beats, bpm=62):
    period = 60 / bpm
    out = np.zeros(int((n_beats * period + 1) * SR))
    for k in range(n_beats):
        for off, a in ((0.0, 1.0), (0.22, 0.6)):
            s0 = int((k * period + off) * SR)
            m = int(0.25 * SR)
            tt = t_(m)
            out[s0:s0 + m] += a * np.sin(2 * np.pi * (48 + 30 * np.exp(-tt / 0.02)) * tt) * np.exp(-tt / 0.07)
    return out


def murmur(dur, seed=0):
    n = int(dur * SR)
    g = np.random.default_rng(seed)
    x = bp(g.standard_normal(n), 250, 1400)
    am = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * (2.3 + np.sin(2 * np.pi * 0.17 * t_(n))) * t_(n)))
    return x * am * env_ar(n, 1.0, 1.2) * 0.5


def bird(seed=0):
    g = np.random.default_rng(seed)
    out = []
    for _ in range(g.integers(2, 5)):
        n = int(g.uniform(0.06, 0.12) * SR)
        tt = t_(n)
        f0 = g.uniform(2800, 4200)
        out.append(np.sin(2 * np.pi * np.cumsum(f0 + 900 * np.sin(np.pi * tt / tt[-1])) / SR) * np.sin(np.pi * tt / tt[-1]))
        out.append(np.zeros(int(g.uniform(0.04, 0.1) * SR)))
    return np.concatenate(out) * 0.25


def stamp_hit():
    n = int(0.6 * SR)
    tt = t_(n)
    return (np.sin(2 * np.pi * (90 + 60 * np.exp(-tt / 0.01)) * tt) * np.exp(-tt / 0.06)
            + 0.5 * bp(np.random.default_rng(3).standard_normal(n), 300, 3000) * np.exp(-tt / 0.03))


def build():
    mus = np.zeros((N, 2))
    sfx = np.zeros((N, 2))
    # --- hook: kampung night, 1911 (D minor)
    add(sfx, noise_bed(S["s01"] + 1.0, 300, 6000, 0.3, 1.5, mod=0.3, seed=1), 0.0, 0.5, 0.16)         # rain
    add(sfx, impact(4.0, 0.7, low=36), T("1911.") - 0.05, 0.5, 0.7)
    add(sfx, crickets(S["g01"] - S["s01"], seed=2), S["s01"], 0.6, 0.06)
    add(mus, drone(38, S["g02"] + 1.0, 2.5, 2.0), 0.0, 0.5, 0.5)
    add(mus, strings([50, 57, 62, 65], S["s03"] - 1.0, att=4.0, rel=2.0, bright=1600, seed=1), 1.0, 0.5, 0.40)
    add(sfx, heartbeat(int((S["s04"] - S["s03"]) / 0.97)), S["s03"], 0.5, 0.30)
    add(mus, strings([46, 53, 58, 62], S["g01"] - S["s03"] + 1.0, att=3.0, rel=2.0, bright=1500, seed=2), S["s03"], 0.5, 0.40)
    add(sfx, murmur(S["g01"] - S["s04"], seed=3), S["s04"], 0.45, 0.10)
    add(sfx, whoosh(1.2, 0.45, reverse=True), S["g01"] - 1.0, 0.5)
    add(sfx, impact(3.5, 0.45, low=42), T("penyakit mental yang serius") - 0.05, 0.5, 0.6)
    # title
    add(sfx, whoosh(1.6, 0.55, reverse=True), S["g02"] - 0.8, 0.5)
    add(sfx, impact(4.5, 0.85, low=38), S["g02"] + 0.3, 0.5, 0.8)
    add(mus, strings([46, 53, 58, 62, 65], 7.0, att=0.6, rel=3.0, bright=2400, seed=3), S["g02"] + 0.3, 0.5, 0.55)
    # --- 19th century (D dorian, paper + plucks)
    t = S["g03"]
    add(sfx, paper(1.5, seed=4), t - 0.3, 0.4, 0.5)
    for i, (dt, ch) in enumerate([(0, [50, 57, 60, 65]), (7, [55, 59, 62, 67]), (14, [53, 57, 60, 64]), (21, [50, 57, 62, 65])]):
        add(mus, strings(ch, 8.0, att=2.0, rel=2.5, bright=1800, seed=10 + i), t + dt, 0.5, 0.38)
    for i, m in enumerate([62, 65, 69, 72, 69, 65]):
        add(mus, pluck(m, 2.0, seed=20 + i), T("Seawal abad") + i * 0.6, 0.35 + 0.05 * i, 0.20)
    add(sfx, whoosh(1.0, 0.35), S["s09"] - 0.6, 0.5)
    add(sfx, ink(1.6, seed=6), S["g04"] + 0.2, 0.6, 0.35)
    add(mus, drone(33, S["k2"] - S["g04"], 2.0, 2.0), S["g04"], 0.5, 0.38)                                # A1: limits of the era
    for i, (dt, ch) in enumerate([(0, [45, 52, 57, 60]), (6, [41, 48, 57, 60]), (12, [38, 45, 53, 57]), (18, [40, 47, 52, 59])]):
        add(mus, strings(ch, 7.0, att=2.0, rel=2.5, bright=1400, seed=30 + i), S["g04"] + dt, 0.5, 0.36)
    add(sfx, noise_bed(S["k2"] - S["e01"], 120, 900, 1.5, 1.5, mod=0.08, seed=7), S["e01"], 0.5, 0.08)     # cold room tone
    add(sfx, heartbeat(3, 58), T("Dia takut"), 0.5, 0.25)
    # --- 1911 Tanjung Rambutan (F major → A minor)
    t = S["k2"]
    add(sfx, whoosh(1.5, 0.5, reverse=True), t - 1.0, 0.5)
    add(sfx, impact(4.0, 0.8, low=38), T("1911", after=t - 0.5) - 0.05, 0.5, 0.75)
    for i, (dt, ch) in enumerate([(0, [53, 60, 65, 69]), (5, [48, 55, 64, 67]), (10, [45, 52, 60, 64]), (16, [46, 53, 62, 65]),
                                  (22, [45, 52, 57, 60])]):
        add(mus, strings(ch, 7.0, att=1.8, rel=2.4, bright=2000, seed=40 + i), t + dt, 0.5, 0.38)
    add(sfx, paper(1.4, seed=8), S["g05"] - 0.3, 0.45, 0.45)
    add(sfx, stamp_hit(), T("penghinaan") - 0.05, 0.5, 0.55)
    add(sfx, ink(1.4, seed=9), T("penghinaan") + 0.1, 0.6, 0.35)
    for i in range(4):
        add(sfx, tick(i % 2 == 0), T("tiga wad lelaki") - 0.1 + i * 0.25 if i < 3 else T("satu wad perempuan") - 0.1, 0.4 + 0.1 * i, 0.30)
    for i, tt in enumerate(np.arange(S["s16"] + 0.5, S["s17"], 0.6)):
        add(sfx, footstep(), tt, 0.4 + 0.2 * (i % 2), 0.12)
    for i, key in enumerate(("Pada tahun 1928", "Central Mental", "hospital bahagia")):
        add(mus, pluck([69, 72, 76][i], 2.5, seed=50 + i), T(key) - 0.1, 0.5, 0.30)
    # --- medicines today vs 1911
    t = S["g08"]
    add(mus, strings([48, 55, 60, 64], T("pada zaman 1911") - t, att=1.0, rel=1.0, bright=2600, seed=60), t, 0.5, 0.34)
    for i, key in enumerate(("skizofrenia", "kemurungan", "bipolar")):
        add(sfx, blip([880, 988, 1175][i]), T(key, after=t - 0.5) - 0.1, 0.5, 0.25)
    tb = T("pada zaman 1911")
    add(sfx, whoosh(1.4, 0.5, reverse=True), tb - 0.9, 0.5)
    add(mus, drone(36, S["g09"] - tb + 1.0, 1.0, 2.0), tb, 0.5, 0.38)
    for i in range(3):
        add(sfx, ink(0.5, seed=70 + i), tb + 0.9 + i * 0.2, 0.55, 0.40)
    # institutional care (A minor), garden birds
    for i, (dt, ch) in enumerate([(0, [45, 52, 57, 60]), (6, [41, 48, 57, 60]), (12, [43, 50, 55, 59]), (18, [45, 52, 57, 60])]):
        add(mus, strings(ch, 7.0, att=2.0, rel=2.5, bright=1500, seed=80 + i), S["e03"] + dt, 0.5, 0.36)
    for k, tt in enumerate(list(np.arange(S["e04"] + 0.5, S["s19"], 1.3)) + list(np.arange(S["s20"] + 0.4, S["g09"], 1.5))):
        add(sfx, bird(seed=90 + k), tt, 0.3 + 0.4 * (k % 2), 0.10)
    add(sfx, paper(1.2, seed=11), S["g09"] - 0.3, 0.45, 0.4)
    add(mus, drone(33, S["e06"] - S["g09"], 1.5, 2.0), S["g09"], 0.5, 0.34)
    add(sfx, whoosh(2.0, 0.55, lo=200, hi=6000), S["e05"] + 1.2, 0.5)                                    # brain morph
    # --- 1950s (G major), glass, pulses
    t = S["e06"]
    add(sfx, impact(3.0, 0.45, low=44), t, 0.5, 0.5)
    for i, tt in enumerate([S["e07"] + 0.4, S["e07"] + 2.0, S["s23"] + 0.5]):
        add(sfx, glass(seed=100 + i), tt, 0.3 + 0.2 * i, 0.28)
    for i, (dt, ch) in enumerate([(0, [43, 55, 59, 62]), (5, [40, 52, 59, 64]), (10, [36, 52, 55, 64]), (15, [38, 50, 57, 62, 66]),
                                  (20, [43, 55, 59, 62, 67]), (26, [40, 52, 59, 64]), (32, [36, 48, 55, 64])]):
        add(mus, strings(ch, 6.6, att=1.6, rel=2.0, bright=2400, seed=110 + i), t + dt, 0.5, 0.36)
    for i, tt in enumerate(np.arange(S["e08"] + 0.3, S["g10"], 0.43)):
        add(mus, blip(1320 if i % 4 == 0 else 880), tt, 0.3 + 0.4 * (i % 3) / 2, 0.14)
    # --- 1958 Penang, general hospital (C major), spread across Malaysia
    t = S["s26"]
    add(sfx, whoosh(1.4, 0.45, reverse=True), t - 1.0, 0.5)
    add(sfx, impact(3.5, 0.55, low=40), T("1958") - 0.05, 0.5, 0.6)
    for i, (dt, ch) in enumerate([(0, [48, 55, 60, 64, 67]), (6, [43, 55, 59, 62, 67]), (12, [45, 52, 60, 64, 69]), (18, [41, 53, 60, 65, 69]),
                                  (24, [48, 55, 60, 64, 67]), (30, [43, 55, 59, 62, 67]), (36, [45, 52, 60, 64, 69])]):
        add(mus, strings(ch, 6.6, att=1.4, rel=2.0, bright=2800, seed=130 + i), t + dt, 0.5, 0.38)
    add(sfx, paper(1.2, seed=12), S["g12"] - 0.3, 0.45, 0.35)
    for i in range(len(bw.MAPS["my"]["pins"])):
        add(mus, pluck([60, 64, 67, 72, 76, 79, 84][i % 7], 1.6, seed=140 + i), S["g14"] + 0.8 + i * 0.28, 0.2 + 0.6 * (i % 5) / 4, 0.16)
    # --- modern: myth (eerie) vs reality (warm piano + hospital tone)
    t = S["s28"]
    add(sfx, whoosh(1.3, 0.45, reverse=True), t - 0.9, 0.5)
    add(mus, drone(31, S["k3"] - t + 0.5, 0.8, 0.8), t, 0.5, 0.45)
    add(sfx, noise_bed(S["k3"] - t, 1800, 5200, 0.6, 0.6, mod=1.7, seed=13), t, 0.6, 0.06)               # eerie scrape
    add(sfx, stamp_hit(), T("filem-filem seram") - 0.05, 0.5, 0.5)
    add(sfx, impact(3.0, 0.4, low=46), S["k3"], 0.5, 0.45)
    prog = [[48, 55, 60, 64], [43, 50, 55, 59], [45, 52, 57, 60], [41, 48, 53, 57]]
    tt, bar = S["k3"], 0
    while tt < S["s31"] - 1.0:
        ch = prog[bar % 4]
        for k, m in enumerate([ch[0] + 12, ch[2] + 12, ch[3] + 12, ch[1] + 24]):
            add(mus, piano(m, 3.0, 0.6 if k else 0.75), tt + k * 0.6, 0.35 + 0.1 * k, 0.40)
        add(mus, strings(ch, 2.8, att=0.9, rel=1.3, bright=2000, seed=150 + bar), tt, 0.5, 0.24)
        tt += 2.6
        bar += 1
    add(sfx, noise_bed(S["s31"] - S["k3"], 150, 1200, 1.5, 1.5, mod=0.05, seed=14), S["k3"], 0.5, 0.05)     # ward room tone
    for i, tt in enumerate(np.arange(S["k3"] + 1.0, S["s29"], 0.58)):
        add(sfx, footstep(), tt, 0.6, 0.05)
    # --- CTA: warm resolution
    t = S["s31"]
    add(sfx, whoosh(1.2, 0.35, reverse=True), t - 0.9, 0.5)
    prog = [[41, 53, 57, 60], [43, 55, 59, 62], [45, 52, 57, 60], [48, 55, 60, 64]]
    tt, bar = t, 0
    while tt < S["g18"] - 0.5:
        ch = prog[bar % 4]
        for k, m in enumerate([ch[1] + 12, ch[2] + 12, ch[3] + 12]):
            add(mus, piano(m, 3.2, 0.55), tt + k * 0.7, 0.4 + 0.1 * k, 0.40)
        add(mus, strings(ch, 3.4, att=1.0, rel=1.6, bright=2400, seed=170 + bar), tt, 0.5, 0.30)
        tt += 3.0
        bar += 1
    add(sfx, paper(1.0, seed=15), S["g17"] - 0.2, 0.45, 0.3)
    add(sfx, bird(seed=200), S["k4"] + 2.0, 0.3, 0.12)
    add(sfx, bird(seed=201), S["k4"] + 4.5, 0.7, 0.12)
    end = S["g18"]
    add(mus, strings([36, 48, 55, 60, 64, 67, 72], DUR - end + 0.3, att=0.9, rel=3.5, bright=3000, seed=190), end, 0.5, 0.5)
    for k, m in enumerate([60, 64, 67, 72, 76]):
        add(mus, piano(m, 5.0, 0.7), end + 0.3 + k * 0.3, 0.3 + 0.1 * k, 0.45)
    add(sfx, impact(4.0, 0.35, low=40), end + 0.3, 0.5, 0.45)
    return mus, sfx


def main():
    mus, sfx = build()
    mus = 0.72 * mus + 0.45 * reverb(mus, 3.2, seed=3)
    sfx = 0.8 * sfx + 0.35 * reverb(sfx, 1.6, seed=5, damp=5000)
    vx, sr = sf.read(A / "voice_polished.wav")
    if vx.ndim > 1:
        vx = vx.mean(1)
    assert sr == SR
    voice = np.zeros(N)
    s0 = int(bw.OFF * SR)
    voice[s0:s0 + len(vx)] = vx[: N - s0]
    env = sosfiltfilt(butter(1, 6, "low", fs=SR, output="sos"), np.abs(voice))
    active = (env > 0.01).astype(float)
    k = np.exp(-1 / (0.45 * SR))
    sm = np.empty_like(active)
    acc = 0.0
    for i in range(0, N, 480):
        a = active[i:i + 480].max()
        acc = a if a > acc else acc * k ** 480
        sm[i:i + 480] = acc
    sm = sosfiltfilt(butter(1, 8, "low", fs=SR, output="sos"), sm)
    duck_m = 10 ** (-7 * sm / 20)
    duck_s = 10 ** (-5 * sm / 20)
    mus *= 0.95 / (np.max(np.abs(mus)) + 1e-9)
    sfx *= 1.00 / (np.max(np.abs(sfx)) + 1e-9)
    voice *= 0.80 / (np.max(np.abs(voice)) + 1e-9)
    bed = mus * duck_m[:, None] + sfx * duck_s[:, None]
    mix = bed + voice[:, None]
    fo = int(2.5 * SR)
    mix[-fo:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fo)))[:, None]
    mix *= 0.89 / np.max(np.abs(mix))
    sf.write(A / "mix_premaster.wav", mix.astype(np.float32), SR, subtype="PCM_24")
    sf.write(A / "stem_voice.wav", voice.astype(np.float32), SR, subtype="PCM_24")
    sf.write(A / "stem_music_sfx.wav", bed.astype(np.float32), SR, subtype="PCM_24")
    print(f"wrote mix_premaster.wav {DUR:.2f}s")


if __name__ == "__main__":
    main()
