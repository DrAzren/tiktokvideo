"""Original, licence-free score + sound design + narration mix for the 120 s documentary.

Everything is synthesized here (no samples): strings pads, drones, piano, harp plucks, impacts,
whooshes, clock ticks, rain, paper, ink scratches, wind, footsteps, glass, electronic pulses.
Deterministic (fixed seeds). The music is sidechain-ducked under the narration.

Writes ../audio/mix_premaster.wav (48 kHz stereo); master with ffmpeg loudnorm (see assemble.sh).
Run: ../../../.venv/bin/python score.py
"""

import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, sosfiltfilt

D = Path(__file__).parent
A = D.parent / "audio"
SR = 48000
DUR = 120.0
N = int(DUR * SR)
TL = json.loads((D / "timeline.json").read_text())
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
    s0 = int(round(t0 * SR))
    if s0 >= N:
        return
    if s0 < 0:
        sig, s0 = sig[-s0:], 0
    sig = sig[: N - s0]
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


# ------------------------------------------------------------------ cue sheet
def build_music():
    mus = np.zeros((N, 2))
    sfx = np.zeros((N, 2))
    S = {s["id"]: s for s in TL["scenes"]}

    # Scene 1 — hook (D minor): impact, drone, rain, ticking, rising strings to the title
    add(sfx, impact(4.5, 1.0), 0.0, 0.5, 0.9)
    add(mus, drone(38, 15.5, 1.5, 2.0), 0.0, 0.5, 0.55)                       # D2
    add(sfx, noise_bed(4.8, 300, 6000, 0.6, 1.2, mod=0.3, seed=1), 0.0, 0.5, 0.10)   # rain
    for i, tt in enumerate(np.arange(4.5, 12.0, 1.0)):
        add(sfx, tick(i % 2 == 0), tt, 0.62, 0.32)
    add(mus, strings([50, 57, 62, 65], 9.0, att=6.5, rel=1.0, seed=1), 3.4, 0.5, 0.55)   # Dm swell
    add(mus, strings([46, 53, 58, 62, 65], 4.6, att=0.6, rel=2.8, seed=2), 11.6, 0.5, 0.6)  # Bb lift under the title
    add(sfx, whoosh(1.4, 0.55, reverse=True), 10.6, 0.5)
    add(sfx, impact(4.0, 0.75, low=40), 12.0, 0.5, 0.8)                       # title hit

    # Scene 2 — ancient (D dorian): wind, paper, restrained frame drum, ink
    s = S["s2"]["start"]
    add(sfx, paper(1.6, seed=3), s - 0.2, 0.4, 0.55)
    add(sfx, noise_bed(18.5, 150, 1200, 3.0, 3.0, mod=0.12, seed=4), s, 0.5, 0.12)   # wind
    add(mus, drone(38, 19.0, 2.0, 2.5), s, 0.5, 0.42)
    for i, (t0, ch) in enumerate([(0.0, [50, 57, 60, 65]), (6.0, [55, 59, 62, 67]), (12.0, [53, 57, 60, 64])]):
        add(mus, strings(ch, 7.2, att=2.2, rel=2.4, bright=1800, seed=10 + i), s + t0, 0.5, 0.42)
    for tt in np.arange(s + 4.0, s + 17.5, 1.71):                              # 70 bpm, every other beat
        add(mus, frame_drum(), tt, 0.45, 0.30)
    add(sfx, ink(1.8, seed=5), s + 14.6, 0.6, 0.45)

    # Scene 3 — Hippocrates (F major rise), writing, whoosh into the brain
    s = S["s3"]["start"]
    add(sfx, whoosh(1.2, 0.45), s - 0.9, 0.5)
    for i, (t0, ch) in enumerate([(0.0, [53, 60, 65, 69]), (4.5, [48, 55, 64, 67]), (9.0, [45, 52, 60, 64]), (13.0, [46, 53, 62, 65])]):
        add(mus, strings(ch, 5.6, att=1.8, rel=2.2, bright=2400, seed=20 + i), s + t0, 0.5, 0.40)
    for i, m in enumerate([65, 69, 72, 77, 72, 69, 74, 77]):
        add(mus, pluck(m, 2.2, seed=30 + i), s + 0.4 + i * 0.55, 0.35 + 0.04 * i, 0.22)
    add(sfx, ink(2.2, seed=6), s + 11.6, 0.6, 0.5)
    add(sfx, whoosh(1.8, 0.65, lo=200, hi=6000), s + 14.2, 0.5)

    # Scene 4 — institutions (A minor, sombre) then hopeful strings (C major) from the reformers
    s = S["s4"]["start"]
    turn = S["s4"]["turn"]
    add(mus, drone(33, turn - s + 2.0, 2.0, 2.5), s, 0.5, 0.45)                # A1
    for i, (t0, ch) in enumerate([(0.0, [45, 52, 57, 60]), (4.0, [41, 48, 57, 60]), (8.0, [38, 45, 53, 57])]):
        add(mus, strings(ch, 5.4, att=2.0, rel=2.4, bright=1400, seed=40 + i), s + t0, 0.5, 0.40)
    add(sfx, noise_bed(turn - s, 100, 900, 2.0, 2.0, mod=0.08, seed=7), s, 0.5, 0.09)   # cold room tone
    for i, tt in enumerate(np.arange(s + 4.6, s + 10.6, 0.62)):                 # distant footsteps down the corridor
        add(sfx, footstep(), tt, 0.4 + 0.2 * (i % 2), 0.20 * (1 - (tt - s - 4.6) / 8))
    add(sfx, whoosh(1.6, 0.4, reverse=True), turn - 1.4, 0.5)
    for i, (t0, ch) in enumerate([(0.0, [48, 55, 60, 64, 67]), (3.0, [43, 55, 59, 62, 67]), (6.0, [45, 52, 60, 64, 69]), (8.4, [41, 53, 60, 65, 69])]):
        add(mus, strings(ch, 4.4 if i < 3 else 5.4, att=1.4, rel=2.0, bright=2800, seed=50 + i), turn + t0, 0.5, 0.42)

    # Scene 5 — 1952 (G major): glass, electronic pulses, inspiring lift
    s = S["s5"]["start"]
    add(sfx, impact(3.0, 0.45, low=44), s, 0.5, 0.6)
    for i, tt in enumerate([s + 0.6, s + 2.4, s + 4.6, s + 5.3]):
        add(sfx, glass(seed=60 + i), tt, 0.3 + 0.15 * i, 0.30)
    for i, (t0, ch) in enumerate([(0.0, [43, 55, 59, 62]), (4.0, [40, 52, 59, 64]), (8.0, [36, 52, 55, 64]), (11.5, [38, 50, 57, 62, 66])]):
        add(mus, strings(ch, 4.8 if i < 3 else 5.0, att=1.6, rel=2.0, bright=2600, seed=70 + i), s + t0, 0.5, 0.40)
    for i, tt in enumerate(np.arange(s + 8.0, s + 15.4, 0.43)):
        add(mus, blip(1320 if i % 4 == 0 else 880), tt, 0.3 + 0.4 * (i % 3) / 2, 0.20)
    add(sfx, whoosh(1.5, 0.5), s + 7.6, 0.5)

    # Scene 6 — present day (C major): warm piano, strings, a restrained "stigma" hit, resolution
    s = S["s6"]["start"]
    stig = S["s6"]["stigma"]
    add(sfx, whoosh(1.3, 0.4, reverse=True), s - 1.1, 0.5)
    prog = [[48, 55, 60, 64], [47, 55, 59, 62], [45, 52, 57, 60], [41, 53, 57, 60]]
    for bar in range(6):
        ch = prog[bar % 4]
        t0 = s + bar * 2.2
        if t0 > stig - 0.6:
            break
        for k, m in enumerate([ch[0] + 12, ch[2] + 12, ch[3] + 12, ch[1] + 24]):
            add(mus, piano(m, 3.2, 0.7 if k else 0.85), t0 + k * 0.55, 0.35 + 0.1 * k, 0.55)
        add(mus, strings(ch, 2.9, att=1.0, rel=1.4, bright=2000, seed=80 + bar), t0, 0.5, 0.30)
    add(sfx, impact(3.5, 0.55, low=36), stig - 0.02, 0.5, 0.65)
    add(mus, drone(36, 6.5, 0.5, 3.0), stig, 0.5, 0.35)
    rec = S["s6"]["recap"]
    for bar, ch in enumerate([[45, 52, 57, 60, 64], [41, 53, 57, 60, 65], [43, 55, 59, 62, 67]]):
        add(mus, strings(ch, 3.4, att=1.2, rel=1.6, bright=2400, seed=90 + bar), rec + bar * 2.4, 0.5, 0.40)
        for k, m in enumerate([ch[1] + 12, ch[3] + 12]):
            add(mus, piano(m, 3.0, 0.6), rec + bar * 2.4 + k * 0.8, 0.4 + 0.2 * k, 0.45)
    end = S["end"]["start"]
    add(mus, strings([41, 53, 57, 60, 65, 69], 3.0, att=1.4, rel=1.2, bright=2600, seed=95), end - 4.6, 0.5, 0.45)
    add(mus, strings([43, 55, 59, 62, 67, 71], 2.6, att=0.8, rel=1.0, bright=2800, seed=96), end - 1.8, 0.5, 0.48)
    add(mus, strings([36, 48, 55, 60, 64, 67, 72], DUR - end + 0.2, att=0.9, rel=4.5, bright=3000, seed=97), end + 0.6, 0.5, 0.55)
    for k, m in enumerate([60, 64, 67, 72, 76]):
        add(mus, piano(m, 5.0, 0.75), end + 0.6 + k * 0.32, 0.3 + 0.1 * k, 0.5)
    add(sfx, impact(4.0, 0.35, low=40), end + 0.6, 0.5, 0.5)

    # chapter whooshes (visual seams)
    for t in TL.get("whooshes", []):
        add(sfx, whoosh(1.1, 0.35), t - 0.75, 0.5)
    return mus, sfx


def load_voice():
    v = np.zeros(N)
    for sid, off in TL["vo"].items():
        raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(A / f"vo_{sid}.mp3"),
                              "-af", "highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2",
                              "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.float32)
        s0 = int(round(off * SR))
        v[s0:s0 + len(x)] += x[: N - s0]
    return v


def main():
    mus, sfx = build_music()
    mus = 0.72 * mus + 0.45 * reverb(mus, 3.2, seed=3)
    sfx = 0.8 * sfx + 0.35 * reverb(sfx, 1.6, seed=5, damp=5000)
    voice = load_voice()

    # sidechain duck: music −9 dB while the narrator speaks (40 ms attack, 450 ms release), SFX −5 dB
    env = np.abs(voice)
    env = sosfiltfilt(butter(1, 6, "low", fs=SR, output="sos"), env)
    active = (env > 0.01).astype(float)
    k = np.exp(-1 / (0.45 * SR))
    sm = np.empty_like(active)
    acc = 0.0
    for i in range(0, N, 480):                      # 10 ms blocks are plenty for a ducker
        a = active[i:i + 480].max()
        acc = a if a > acc else acc * k ** 480
        sm[i:i + 480] = acc
    sm = sosfiltfilt(butter(1, 8, "low", fs=SR, output="sos"), sm)
    duck_m = 10 ** (-9 * sm / 20)
    duck_s = 10 ** (-5 * sm / 20)

    mus *= 0.46 / (np.max(np.abs(mus)) + 1e-9)
    sfx *= 0.50 / (np.max(np.abs(sfx)) + 1e-9)
    voice *= 0.80 / (np.max(np.abs(voice)) + 1e-9)
    mix = mus * duck_m[:, None] + sfx * duck_s[:, None] + voice[:, None]
    fo = int(2.5 * SR)
    mix[-fo:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fo)))[:, None]
    mix *= 0.89 / np.max(np.abs(mix))
    sf.write(A / "mix_premaster.wav", mix.astype(np.float32), SR, subtype="PCM_24")
    sf.write(A / "stem_voice.wav", voice.astype(np.float32), SR, subtype="PCM_24")
    sf.write(A / "stem_music_sfx.wav", (mus * duck_m[:, None] + sfx * duck_s[:, None]).astype(np.float32), SR, subtype="PCM_24")
    print("wrote mix_premaster.wav", f"{DUR}s")


if __name__ == "__main__":
    main()
