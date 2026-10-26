"""Sound for '10 Ayat Dilarang Cakap': synthesized SFX on every cue, then the master mix.

  sfx.wav    every cue in graphics/sfx_cues.json (written by build_graphics.py), synthesized here —
             soft whooshes, UI clicks/ticks, text pops, gentle bass impacts, a red-line "strike",
             risers and reverse swells. Nothing harsh: this is a mental-health topic.
  mix.wav    voice.wav (tools/enhance_speech.py --car) + sfx (~16 dB under the voice) + piano bed
             (tools/piano_bed.py; EQ'd out of the voice band and sidechain-ducked by the voice),
             two-pass loudnorm to -14 LUFS / -1 dBTP. Reports the measured balance.

Run: ../../../.venv/bin/python build_audio.py
"""

import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

A = Path(__file__).parent
ROOT = A.parent
SR = 48000
RNG = np.random.default_rng(10)


def env(n, attack, decay):
    t = np.arange(n) / SR
    return (1 - np.exp(-t / max(attack, 1e-4))) * np.exp(-t / decay)


def bandnoise(n, lo, hi):
    x = RNG.standard_normal(n)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, n)


def sweep_noise(n, f0, f1, q=0.35):
    """noise through a band that glides f0 -> f1 (short-time FFT filtering)"""
    x = RNG.standard_normal(n)
    hop, win = 512, 2048
    out = np.zeros(n + win)
    w = np.hanning(win)
    for i, s in enumerate(range(0, n, hop)):
        seg = np.zeros(win)
        seg[:min(win, n - s)] = x[s:s + win]
        fc = f0 * (f1 / f0) ** (s / max(1, n))
        X = np.fft.rfft(seg * w)
        f = np.fft.rfftfreq(win, 1 / SR)
        X *= np.exp(-0.5 * ((np.log(f + 1) - np.log(fc)) / q) ** 2)
        out[s:s + win] += np.fft.irfft(X, win) * w
    return out[:n] / 1.5


def tone(n, f0, f1=None, decay=0.2):
    t = np.arange(n) / SR
    f1 = f0 if f1 is None else f1
    ph = 2 * np.pi * np.cumsum(f0 + (f1 - f0) * (1 - np.exp(-t / 0.05))) / SR
    return np.sin(ph) * np.exp(-t / decay)


def make(kind):
    if kind == "whoosh":
        n = int(0.55 * SR)
        x = sweep_noise(n, 500, 3500) * np.sin(np.linspace(0, np.pi, n)) ** 2
        return x / np.abs(x).max() * 0.5
    if kind == "air":
        n = int(0.35 * SR)
        x = sweep_noise(n, 2500, 900, 0.5) * np.sin(np.linspace(0, np.pi, n)) ** 2
        return x / np.abs(x).max() * 0.3
    if kind == "pop":
        n = int(0.12 * SR)
        x = tone(n, 880, 1320, 0.035) * 0.8 + bandnoise(n, 2000, 7000) * env(n, 0.001, 0.008) * 0.3
        return x / np.abs(x).max() * 0.5
    if kind == "click":
        n = int(0.06 * SR)
        x = tone(n, 2200, 1800, 0.008) + bandnoise(n, 3000, 9000) * env(n, 0.0005, 0.004) * 0.5
        return x / np.abs(x).max() * 0.45
    if kind == "tick":
        n = int(0.05 * SR)
        x = bandnoise(n, 4000, 12000) * env(n, 0.0005, 0.006)
        return x / np.abs(x).max() * 0.25
    if kind in ("impact", "boom"):
        n = int(1.2 * SR)
        sub = tone(n, 95 if kind == "impact" else 70, 42, 0.32 if kind == "impact" else 0.22)
        body = bandnoise(n, 60, 600) * env(n, 0.002, 0.06) * 0.35
        x = sub + body
        if kind == "impact":
            x += sweep_noise(n, 3000, 400, 0.6) * env(n, 0.004, 0.25) * 0.25
        return x / np.abs(x).max() * (0.85 if kind == "impact" else 0.6)
    if kind == "strike":       # quick red-line swipe: bright swish + a soft low tap
        n = int(0.4 * SR)
        x = sweep_noise(n, 1500, 6000, 0.3) * env(n, 0.01, 0.12) + tone(n, 160, 90, 0.08) * 0.6
        return x / np.abs(x).max() * 0.5
    if kind == "swell":        # reverse swell: rising noise + tone into the hit point (ends at the cue)
        n = int(1.0 * SR)
        r = np.linspace(0, 1, n) ** 3
        x = (sweep_noise(n, 300, 2500, 0.6) * 0.6 + tone(n, 220, 220, 9) * 0.3) * r
        return x / np.abs(x).max() * 0.45
    if kind == "riser":
        n = int(1.4 * SR)
        r = np.linspace(0, 1, n) ** 2
        x = sweep_noise(n, 300, 5000, 0.45) * r
        return x / np.abs(x).max() * 0.35
    raise KeyError(kind)


def build_sfx(dur):
    cues = json.loads((ROOT / "graphics" / "sfx_cues.json").read_text())
    n = int(dur * SR)
    out = np.zeros((n, 2))
    last = {}
    for c in cues:
        if c["t"] - last.get(c["kind"], -9) < 0.12:       # no machine-gun repeats
            continue
        last[c["kind"]] = c["t"]
        x = make(c["kind"])
        rev = c["kind"] in ("swell", "riser")              # these END on the cue (they build into it)
        g = 10 ** (c["gain_db"] / 20)
        s0 = int(c["t"] * SR) - (len(x) if rev else 0)
        s0, x = (0, x[-s0:]) if s0 < 0 else (s0, x)
        e0 = min(n, s0 + len(x))
        pan = 0.5 + 0.12 * np.sin(c["t"] * 3.1)
        out[s0:e0, 0] += x[:e0 - s0] * g * (1.1 - pan)
        out[s0:e0, 1] += x[:e0 - s0] * g * (0.1 + pan)
    sf.write(A / "sfx.wav", out.astype(np.float32), SR, subtype="PCM_24")
    return len(cues)


def ff(*a):
    return subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", *a], capture_output=True, text=True, check=True).stderr


def lufs(path, af="anull"):
    err = ff("-i", str(path), "-af", f"{af},ebur128", "-f", "null", "-")
    return float(err.rsplit("I:", 1)[1].split("LUFS")[0])


def main():
    voice = A / "voice.wav"
    dur = sf.info(voice).duration
    ncue = build_sfx(dur)
    music_eq = "highpass=f=110:poles=2,equalizer=f=320:t=q:w=1.2:g=-4,equalizer=f=2800:t=q:w=1.5:g=-3"
    bed_target, sfx_target = -23.0, -27.0          # undocked bed / sfx loudness against a -14 LUFS voice
    g_bed = bed_target - lufs(A / "bed.wav", music_eq)
    g_sfx = sfx_target - lufs(A / "sfx.wav")
    graph = (f"[1:a]{music_eq},volume={g_bed:.2f}dB[m];[0:a]aformat=channel_layouts=stereo,asplit=2[v][sc];"
             f"[m][sc]sidechaincompress=threshold=0.04:ratio=5:attack=25:release=500:knee=6[md];"
             f"[2:a]volume={g_sfx:.2f}dB[s];[v][md][s]amix=inputs=3:duration=first:normalize=0[mix]")
    pre = A / "premix.wav"
    ff("-y", "-i", str(voice), "-i", str(A / "bed.wav"), "-i", str(A / "sfx.wav"), "-filter_complex", graph,
       "-map", "[mix]", "-c:a", "pcm_s24le", str(pre))
    target = "I=-14:TP=-1.5:LRA=11"
    err = ff("-i", str(pre), "-af", f"loudnorm={target}:print_format=json", "-f", "null", "-")
    j = json.loads(err[err.rindex("{"):err.rindex("}") + 1])
    ln = (f"loudnorm={target}:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    ff("-y", "-i", str(pre), "-af", f"{ln},alimiter=limit=0.87:attack=2:release=50:level=false:latency=true", "-ar", "48000",
       "-c:a", "pcm_s24le", str(A / "mix.wav"))
    pre.unlink()
    # measured balance (400 ms windows): music & sfx vs voice
    v, _ = sf.read(voice)
    v = v.mean(1) if v.ndim > 1 else v
    hop = int(0.4 * SR)
    k = len(v) // hop
    r = lambda x: 20 * np.log10(np.sqrt((x[:k * hop].reshape(k, hop) ** 2).mean(1)) + 1e-9)
    vr = r(v)
    speech = vr > np.percentile(vr, 50)
    print(f"{ncue} sfx cues · bed gain {g_bed:+.1f} dB · sfx gain {g_sfx:+.1f} dB")
    print(f"voice LUFS {lufs(voice):.1f}; bed (undocked) {bed_target}; sfx {sfx_target}")
    err = ff("-i", str(A / "mix.wav"), "-af", "ebur128=peak=true", "-f", "null", "-")
    tail = err[err.rindex("Summary:"):]
    print(" ".join(l.strip() for l in tail.splitlines() if l.strip().startswith(("I:", "Peak:", "LRA:"))))


if __name__ == "__main__":
    main()
