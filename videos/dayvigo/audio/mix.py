"""Final audio mix for 'Ubat Psikiatri Dayvigo': voice (edit/cut.mp4, already enhanced + -14 LUFS)
+ synthesized music bed (bed.wav) + sound design (sfx.wav) → mix.wav, mastered to -14 LUFS / -1 dBTP.

  voice: untouched (the loudest, clearest element)
  music: out of the voice band (HPF 120 Hz, -4 dB @ 320 Hz, -3 dB @ 2.5 kHz), set to --bed-lufs,
         sidechain-ducked hard by the voice (fast attack, slow release)
  sfx:   HPF 80 Hz, set so its peaks sit --sfx-peak dB under the voice peaks, ducked lightly by the
         voice (ratio 2) so a hit never masks a word
  master: two-pass loudnorm (linear) → -14 LUFS, -1 dBTP

Prints the measured music-vs-voice gap during speech, and the SFX level vs voice, so the
balance is reported, not guessed. Also writes dialogue.wav (the clean enhanced dialogue stem).
"""

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

A = Path(__file__).parent
VOICE = A.parent / "edit" / "cut.mp4"
TARGET = "I=-14:TP=-1:LRA=11"


def run(args, **kw):
    return subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-y", *args], check=True, capture_output=True, text=True, **kw)


def lufs(path_or_filter_args):
    p = run([*path_or_filter_args, "-af", "ebur128", "-f", "null", "-"])
    line = [ln for ln in p.stderr.splitlines() if ln.strip().startswith("I:")][-1]
    return float(line.split()[1])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bed-lufs", type=float, default=-21.0)
    ap.add_argument("--sfx-peak", type=float, default=5.0, help="SFX peaks this many dB under voice peaks")
    args = ap.parse_args()

    run(["-i", str(VOICE), "-vn", "-ac", "2", "-ar", "48000", "-c:a", "pcm_f32le", str(A / "dialogue.wav")])
    v, sr = sf.read(A / "dialogue.wav")
    s, _ = sf.read(A / "sfx.wav")
    bed_in = lufs(["-i", str(A / "bed.wav")])
    v_peak = 20 * np.log10(np.abs(v).max())
    s_peak = 20 * np.log10(np.abs(s).max())
    sfx_gain = v_peak - args.sfx_peak - s_peak
    bed_gain = args.bed_lufs - bed_in

    graph = (
        "[0:a]aformat=sample_fmts=fltp:channel_layouts=stereo,asplit=3[vo][sc1][sc2];"
        f"[1:a]highpass=f=120:poles=2,equalizer=f=320:t=q:w=1.2:g=-4,equalizer=f=2500:t=q:w=1.0:g=-3,volume={bed_gain:.2f}dB[m0];"
        "[m0][sc1]sidechaincompress=threshold=0.04:ratio=5:attack=25:release=650:knee=6:makeup=1[m];"
        f"[2:a]highpass=f=80,volume={sfx_gain:.2f}dB[s0];"
        "[s0][sc2]sidechaincompress=threshold=0.08:ratio=2:attack=10:release=250:knee=4:makeup=1[s];"
        "[vo][m][s]amix=inputs=3:normalize=0:duration=first[mx]"
    )
    pre = A / "_premix.wav"
    run(["-i", str(A / "dialogue.wav"), "-i", str(A / "bed.wav"), "-i", str(A / "sfx.wav"), "-filter_complex", graph,
         "-map", "[mx]", "-c:a", "pcm_f32le", str(pre)])
    p = run(["-i", str(pre), "-af", f"loudnorm={TARGET}:print_format=json", "-f", "null", "-"])
    m = json.loads(p.stderr[p.stderr.rindex("{"):p.stderr.rindex("}") + 1])
    af = (f"loudnorm={TARGET}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000")
    run(["-i", str(pre), "-af", af, "-c:a", "pcm_f32le", str(A / "mix.wav")])
    pre.unlink()

    # ---- balance report (the ducked stems, rendered separately with the same graph)
    for name, keep, drop in (("music", "[m]", "[s]"), ("sfx", "[s]", "[m]")):
        g = graph.replace("[vo][m][s]amix=inputs=3:normalize=0:duration=first[mx]", f"[vo]anullsink;{drop}anullsink")
        run(["-i", str(A / "dialogue.wav"), "-i", str(A / "bed.wav"), "-i", str(A / "sfx.wav"), "-filter_complex", g,
             "-map", keep, "-c:a", "pcm_f32le", str(A / f"_{name}.wav")])
    mu, _ = sf.read(A / "_music.wav")
    sx, _ = sf.read(A / "_sfx.wav")
    n = min(len(v), len(mu), len(sx))
    hop = sr // 10
    def rms_db(x):
        k = len(x) // hop
        return 20 * np.log10(np.sqrt((x[:k * hop].mean(1).reshape(k, hop) ** 2).mean(1)) + 1e-9)
    vd, md = rms_db(v[:n]), rms_db(mu[:n])
    speech = vd > np.percentile(vd, 40)
    print(f"bed {bed_in:.1f} LUFS → {args.bed_lufs:.0f} (gain {bed_gain:+.1f} dB); sfx gain {sfx_gain:+.1f} dB")
    print(f"music under voice during speech: {np.median(vd[speech] - md[speech]):.1f} dB; in pauses: "
          f"{np.median(vd[~speech] - md[~speech]):.1f} dB")
    print(f"peaks: voice {v_peak:.1f} dBFS, sfx (ducked) {20 * np.log10(np.abs(sx).max()):.1f} dBFS")
    for f in ("_music.wav", "_sfx.wav"):
        (A / f).unlink()
    p = run(["-i", str(A / "mix.wav"), "-af", "ebur128=peak=true", "-f", "null", "-"])
    tail = [ln.strip() for ln in p.stderr.splitlines() if ln.strip().startswith(("I:", "Peak:", "LRA:"))]
    print("master:", " | ".join(tail[-3:]))


if __name__ == "__main__":
    main()
