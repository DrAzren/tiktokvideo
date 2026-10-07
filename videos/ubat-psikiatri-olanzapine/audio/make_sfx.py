"""Synthesize transition SFX and lay them on a track that matches the edit (no samples, no licences).

Round 2 (user: "pelbagaikan sound effect, jangan ulang ting dan whoosh banyak kali"): instead of one
sound per event kind (38 tings + 17 whooshes), every event gets a cue chosen from WHAT is on screen:
  B-roll photo in / photo->photo         shutter / polaroid click+whirr / soft swell, matched to the still
  full-screen motion graphic in          each MG its own: riser, zip, deep whoosh, tape riser
  MG out                                  only the two long MGs (reverse swoosh / air) — the rest cut clean
  card enters                             rotates paper slide / swipe / card flick
  list items (pills, rows, steps)         rising musical notes, a different instrument per card
                                          (marimba, kalimba, xylophone, bubble pop)
  Darah / Berat badan ticks              "check" two-tone ding
  risiko naik (3 tiles)                  rising blips
  JANGAN stop / JANGAN give up           low "dun" / warm major chord
  stamps (VS, PALING COMMON)             punch / rubber-stamp thud
  quote on the lake                      sparkle shimmer
  "Ada soalan?"                          message pop
  hero "OLANZAPINE"                      sub impact
Kicker chips that land with their card get no sound of their own (the card's entry covers them), and a
non-accent cue within MIN_GAP of the previous cue is dropped, so nothing machine-guns.
Events (times) come from graphics/sfx_events.json (build_graphics.py / inserts.py) + the caption hero.
tools/mix_music.py --sfx mixes this AFTER the music ducking so the voice never ducks them.

Usage: python make_sfx.py <video-for-duration> -o sfx.wav
"""

import argparse
import json
import re
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

SR = 48000
A = Path(__file__).parent
RNG = np.random.default_rng(7)
MIN_GAP = 0.32           # seconds between two non-accent cues
ACCENTS = {"impact", "stamp", "punch", "shutter", "polaroid", "soft_swell", "riser", "zip", "deep_whoosh", "tape_riser"}


# ---- building blocks ---------------------------------------------------------------------------
def t_(dur):
    return np.arange(int(dur * SR)) / SR


def norm(x):
    return x / (np.abs(x).max() + 1e-9)


def band(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)


def hp(x, f):
    return sosfilt(butter(2, f, btype="high", fs=SR, output="sos"), x)


def lp(x, f):
    return sosfilt(butter(2, f, btype="low", fs=SR, output="sos"), x)


def env(n, attack, shape=3.0):
    a = max(1, int(attack * n))
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a) ** 2
    e[a:] = (1 - np.linspace(0, 1, n - a)) ** shape
    return e


def sweep_noise(dur, f0, f1, q=1.6):
    n = int(dur * SR)
    x = RNG.standard_normal(n)
    out = np.zeros(n)
    blk = SR // 100
    for i in range(0, n, blk):
        fc = f0 * (f1 / f0) ** (i / n)
        sos = butter(2, [fc / q, min(fc * q, SR / 2 - 100)], btype="band", fs=SR, output="sos")
        out[i:i + blk] = sosfilt(sos, x[max(0, i - 2048):i + blk])[-len(x[i:i + blk]):]
    return norm(out)


def glide(f0, f1, dur, harmonics=(1.0,)):
    t = t_(dur)
    f = f0 * (f1 / f0) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return sum(a * np.sin((k + 1) * ph) for k, a in enumerate(harmonics))


def tone(f, dur, partials, tau):
    t = t_(dur)
    s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (tau / (1 + 0.8 * k)))
            for k, (r, a) in enumerate(partials))
    return norm(s * np.minimum(1, t / 0.002))


def hz(note):
    names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    m = re.match(r"([A-G])(#?)(\d)", note)
    midi = 12 * (int(m.group(3)) + 1) + names[m.group(1)] + (1 if m.group(2) else 0)
    return 440 * 2 ** ((midi - 69) / 12)


# ---- the palette -------------------------------------------------------------------------------
def shutter(air=False):
    s = np.zeros(int(0.32 * SR))
    for k, (t0, f) in enumerate([(0.0, 3200), (0.075, 2600)]):
        i = int(t0 * SR)
        n = int(0.012 * SR)
        s[i:i + n] += band(RNG.standard_normal(n), 1500, 7000) * np.exp(-np.arange(n) / (0.003 * SR)) * (1 - 0.3 * k)
        thunk = np.sin(2 * np.pi * 140 * t_(0.04)) * np.exp(-t_(0.04) / 0.01)
        s[i:i + len(thunk)] += 0.5 * thunk
    s = norm(s)
    if air:
        a = lp(RNG.standard_normal(int(0.32 * SR)), 1800) * env(int(0.32 * SR), 0.5, 2)
        s = s + 0.35 * norm(a)
    return norm(s)


def polaroid():           # click + motor whirr
    c = shutter()[:int(0.06 * SR)]
    n = int(0.45 * SR)
    t = t_(0.45)
    whirr = band(np.sign(np.sin(2 * np.pi * 95 * t)) + 0.3 * RNG.standard_normal(n), 300, 2400) * env(n, 0.15, 1.5)
    s = np.zeros(int(0.05 * SR) + n)
    s[:len(c)] += c
    s[int(0.05 * SR):] += 0.45 * norm(whirr)
    return norm(s)


def soft_swell():         # gentle breath of air for calm stills (lake, bedroom)
    n = int(0.7 * SR)
    x = band(RNG.standard_normal(n), 200, 2200) * env(n, 0.6, 2.0)
    return norm(x + 0.25 * tone(hz("A4"), 0.7, [(1, 1), (2, .2)], 0.4) * env(n, 0.6, 2.0))


def riser():               # MG1: noise + rising tone, lands on the cut
    n = int(0.6 * SR)
    s = 0.7 * sweep_noise(0.6, 300, 5000) + 0.3 * norm(glide(220, 880, 0.6, (1, .4, .2)))
    return norm(s * env(n, 0.92, 1.0))


def zip_():                # MG2: fast zipper sweep up
    n = int(0.22 * SR)
    s = sweep_noise(0.22, 800, 6000, q=1.3) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 70 * t_(0.22))))
    return norm(s * env(n, 0.7, 1.5))


def deep_whoosh():         # MG3: low, heavy pass-by with a sub
    n = int(0.7 * SR)
    s = sweep_noise(0.7, 120, 1100, q=1.8) + 0.6 * norm(glide(70, 45, 0.7)) * env(n, 0.5, 2)
    return norm(s * env(n, 0.55, 2.0))


def tape_riser():          # MG4: pitched-up synth with a tape wobble
    n = int(0.5 * SR)
    t = t_(0.5)
    f = 180 * (4 ** (t / 0.5)) * (1 + 0.01 * np.sin(2 * np.pi * 7 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)
    return norm(lp(s, 3000) * env(n, 0.95, 1.0))


def rev_swoosh():
    n = int(0.45 * SR)
    return norm(sweep_noise(0.45, 4000, 500) * env(n, 0.15, 2.5))


def air_out():
    n = int(0.35 * SR)
    return norm(lp(RNG.standard_normal(n), 1400) * env(n, 0.2, 2.5))


def paper():
    n = int(0.22 * SR)
    x = hp(RNG.standard_normal(n), 2500) * (0.5 + 0.5 * np.abs(RNG.standard_normal(n // 240 + 1)).repeat(240)[:n])
    return norm(x * env(n, 0.25, 2.2))


def swipe():
    n = int(0.16 * SR)
    return norm(sweep_noise(0.16, 1500, 4500, q=1.5) * env(n, 0.4, 2))


def flick():
    s = np.zeros(int(0.12 * SR))
    c = int(0.004 * SR)
    s[:c] = band(RNG.standard_normal(c), 2000, 8000)
    s[c:] += 0.4 * band(RNG.standard_normal(len(s) - c), 3000, 9000) * np.exp(-np.arange(len(s) - c) / (0.02 * SR))
    return norm(s)


INSTR = {
    "marimba": lambda f: tone(f, 0.45, [(1, 1), (3.9, .25), (9.2, .06)], 0.16),
    "kalimba": lambda f: tone(f, 0.7, [(1, 1), (5.4, .18), (2.0, .1)], 0.3),
    "xylo": lambda f: tone(f, 0.35, [(1, 1), (3.0, .35), (6.0, .12)], 0.09),
    "bubble": lambda f: norm(glide(f, f * 2.1, 0.07) * np.exp(-t_(0.07) / 0.025)),
}


def check_ding():
    a = tone(hz("E6"), 0.4, [(1, 1), (2.0, .2)], 0.12)
    b = tone(hz("A6"), 0.6, [(1, 1), (2.0, .2)], 0.2)
    s = np.zeros(int(0.09 * SR) + len(b))
    s[:len(a)] += a
    s[int(0.09 * SR):] += b
    return norm(s)


def blip_up(f):
    s = glide(f, f * 2, 0.16, (1, 0, .33, 0, .2))
    return norm(lp(s, 5000) * env(len(s), 0.1, 1.5))


def punch():
    t = t_(0.22)
    s = np.sin(2 * np.pi * np.cumsum(90 * np.exp(-t / 0.04) + 50) / SR) * np.exp(-t / 0.06)
    c = band(RNG.standard_normal(len(t)), 1500, 6000) * np.exp(-t / 0.008)
    return norm(s + 0.5 * norm(c))


def stamp():
    t = t_(0.38)
    body = np.sin(2 * np.pi * np.cumsum(55 + 70 * np.exp(-t / 0.05)) / SR) * np.exp(-t / 0.11)
    click = band(RNG.standard_normal(len(t)), 900, 3500) * np.exp(-t / 0.012)
    return norm(body + 0.35 * norm(click))


def impact():
    t = t_(1.4)
    boom = np.sin(2 * np.pi * np.cumsum(38 + 90 * np.exp(-t / 0.07)) / SR) * np.exp(-t / 0.35)
    air = hp(RNG.standard_normal(len(t)), 1200) * np.exp(-t / 0.09)
    return norm(boom + 0.25 * norm(air))


def sparkle():
    s = np.zeros(int(0.9 * SR))
    for k in range(7):
        f = 3000 + 4000 * RNG.random()
        p = tone(f, 0.3, [(1, 1)], 0.06) * (0.9 - 0.08 * k)
        i = int((0.04 + 0.09 * k) * SR)
        s[i:i + len(p)] += p
    return norm(s)


def dun():
    s = np.concatenate([tone(hz("G3"), 0.16, [(1, 1), (2, .5), (3, .3)], 0.08),
                        tone(hz("D3"), 0.4, [(1, 1), (2, .5), (3, .3)], 0.16)])
    return norm(lp(s, 2000))


def warm_chord():
    s = sum(tone(hz(n), 1.0, [(1, 1), (2, .15)], 0.45) for n in ("C5", "E5", "G5", "C6"))
    return norm(s * np.minimum(1, t_(1.0) / 0.03))


def message_pop():
    a, b = INSTR["bubble"](700), INSTR["bubble"](1050)
    s = np.zeros(int(0.12 * SR) + len(b))
    s[:len(a)] += a
    s[int(0.12 * SR):] += b
    return norm(s)


def soft_click():
    n = int(0.03 * SR)
    return norm(band(RNG.standard_normal(n), 2500, 7000) * np.exp(-np.arange(n) / (0.004 * SR)))


# ---- cue sheet ---------------------------------------------------------------------------------
LEVEL = {"shutter": -10, "polaroid": -11, "soft_swell": -14, "riser": -9, "zip": -10, "deep_whoosh": -8, "tape_riser": -10, "rev_swoosh": -13,
         "air_out": -15, "paper": -15, "swipe": -14, "flick": -14, "note": -14, "check": -12, "blip": -14,
         "punch": -8, "stamp": -8, "impact": -5, "sparkle": -13, "dun": -11, "chord": -12, "message": -11,
         "click": -16}
MG_IN = {"m1-split": ("riser", riser), "m2-bantu": ("zip", zip_), "m3-metabolik": ("deep_whoosh", deep_whoosh),
         "m4-penting": ("tape_riser", tape_riser)}
MG_OUT = {"m2-bantu": ("rev_swoosh", rev_swoosh), "m4-penting": ("air_out", air_out)}
# each photo insert gets a cue that fits it, so six photo entries are not six identical shutters
PHOTO_IN = {"b0-olanzapine": ("shutter", lambda: shutter(air=True)), "b1-senyap": ("soft_swell", soft_swell),
            "b2-ubat": ("polaroid", polaroid), "b3-makan": ("polaroid", polaroid),
            "b4-mengantuk": ("soft_swell", soft_swell), "b5-klinik": ("shutter", lambda: shutter(air=True))}
CARD_IN = [("paper", paper), ("swipe", swipe), ("flick", flick)]
# list series → (instrument, notes); each card/MG gets its own sound and scale direction
SERIES = {"c01": ("marimba", ["C5", "E5", "G5"]), "c02": ("kalimba", ["D5", "F#5", "A5"]),
          "c03-s": ("marimba", ["G5", "D5"]),            # pelan-pelan → drastik: falls
          "c07": ("bubble", [600, 800, 1050]), "m2-r": ("xylo", ["C6", "D6", "E6", "G6", "A6"])}


def cues(events, hero_t):
    out = []                                   # (t, name, synth)
    card_i = 0
    series_pos = {}
    for e in events:
        t, kind, src = e["t"], e["kind"], e["src"]
        if kind == "whoosh_in":
            if src in MG_IN:
                out.append((t - 0.35, *MG_IN[src]))          # risers land ON the cut
            else:
                out.append((t, *PHOTO_IN[src]))
        elif kind == "whoosh_swap":
            nxt = {"m1-split": "b0-olanzapine", "b1-senyap": "b2-ubat", "b4-mengantuk": "m3-metabolik"}[src]
            if nxt in MG_IN:
                out.append((t - 0.2, *MG_IN[nxt]))     # MG lands on the cut with its own transition
            else:
                out.append((t + 0.1, *PHOTO_IN[nxt]))
        elif kind == "whoosh_out":
            if src in MG_OUT:
                out.append((t, *MG_OUT[src]))
        elif kind == "swish" and not src.startswith("#"):              # card panel enters
            name, fn = CARD_IN[card_i % len(CARD_IN)]
            card_i += 1
            out.append((t, name, fn))
        elif kind == "ting":
            if "kicker" in src or src in ("#m1-c", "#m2-c", "#m3-c", "#m4-c", "#m1-d1"):
                continue                                               # lands with its card / MG entry
            m = re.match(r"#(c0\d)-p\d", src) or re.match(r"#(c03-s)\d", src)
            if m:
                key = m.group(1)
                if key == "c05":
                    out.append((t, "check", check_ding))
                    continue
                inst, notes = SERIES[key]
                k = series_pos.get(key, 0)
                series_pos[key] = k + 1
                f = notes[k % len(notes)]
                f = hz(f) if isinstance(f, str) else f
                out.append((t, "note", (lambda inst=inst, f=f: INSTR[inst](f))))
            elif re.match(r"#m2-d\d", src):
                continue                                               # the row's own note covers it
            elif re.match(r"#m3-u(\d)", src):
                k = int(src[-1])
                out.append((t, "blip", (lambda k=k: blip_up(500 * 1.26 ** k))))
            elif src == "#m1-d2":
                continue                                               # VS punch is 10ms away
            elif src == "#b0-olanzapine-lc":
                out.append((t, "click", soft_click))
            elif src == "#c08-cta-t3":
                out.append((t, "message", message_pop))
        elif kind == "swish" and re.match(r"#m2-r\d", src):
            k = series_pos.get("m2-r", 0)
            series_pos["m2-r"] = k + 1
            f = hz(SERIES["m2-r"][1][k])
            out.append((t, "note", (lambda f=f: INSTR["xylo"](f))))
        elif kind == "swish" and src == "#m4-r1":
            out.append((t, "dun", dun))
        elif kind == "swish" and src == "#m4-r2":
            out.append((t, "chord", warm_chord))
        elif kind == "thud":
            out.append((t, "punch" if src == "#m1-vs" else "stamp", punch if src == "#m1-vs" else stamp))
        elif kind == "chime":
            out.append((t, "sparkle", sparkle))
    out.append((hero_t - 0.02, "impact", impact))
    out.sort(key=lambda c: c[0])

    kept, last_t, last_name = [], -9.0, None
    for t, name, fn in out:
        if name not in ACCENTS and t - last_t < MIN_GAP:
            continue
        if name == last_name and name not in ("note", "blip") and t - last_t < 1.0:
            continue                                                   # never the same cue twice in a row
        kept.append((t, name, fn))
        last_t, last_name = t, name
    return kept


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

    kept = cues(ev, hero_t)
    track = np.zeros((int((dur + 2) * SR), 2))
    for t, name, fn in kept:
        s = fn() * 10 ** (LEVEL[name] / 20)
        sweeping = name in ("riser", "zip", "deep_whoosh", "tape_riser", "rev_swoosh", "swipe", "paper")
        pan = np.linspace(-0.5, 0.5, len(s)) if sweeping else np.zeros(len(s))
        i0 = int(max(0.0, t) * SR)
        i1 = min(len(track), i0 + len(s))
        track[i0:i1, 0] += (np.sqrt((1 - pan) / 2) * s)[:i1 - i0]
        track[i0:i1, 1] += (np.sqrt((1 + pan) / 2) * s)[:i1 - i0]
    track = track[:int(dur * SR)]
    peak = np.abs(track).max()
    if peak > 0.89:
        track *= 0.89 / peak
    sf.write(args.output, track, SR, subtype="PCM_24")
    counts = {}
    for _, name, _ in kept:
        counts[name] = counts.get(name, 0) + 1
    (A / "sfx_cues.txt").write_text("".join(f"{t:7.2f}  {name}\n" for t, name, _ in kept))
    print(f"{len(kept)} cues, {len(counts)} different sounds {dict(sorted(counts.items(), key=lambda kv: -kv[1]))}"
          f" → {args.output}, peak {20 * np.log10(peak + 1e-9):.1f} dBFS")


if __name__ == "__main__":
    main()
