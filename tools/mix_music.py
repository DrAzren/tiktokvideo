"""Mix a music bed under a video's dialogue, then master the result.

  music: high-pass 140 Hz + 4 dB dip at 320 Hz (out of the voice's way), set to
         --bed-lufs, then sidechain-ducked by the dialogue (fast attack, slow release)
  mix:   dialogue + ducked music → two-pass loudnorm to -14 LUFS / -1 dBTP
  video: stream-copied (no re-encode)

Also reports how far the music sits below the voice during speech vs. pauses, so
the balance is measured, not guessed.

Usage:
    python tools/mix_music.py <video.mp4> <bed.wav> -o <out.mp4> [--bed-lufs -26] [--fade-out 2.5]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

MUSIC_EQ = "highpass=f=140:poles=2,equalizer=f=320:t=q:w=1.2:g=-4"
DUCK = "sidechaincompress=threshold=0.02:ratio=8:attack=20:release=450:knee=4:makeup=1"
TARGET = "I=-14:TP=-1:LRA=11"


def ff(*args: str) -> str:
    return subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", *args], capture_output=True, text=True, check=True).stderr


def integrated_lufs(path: str, af: str = "anull") -> float:
    err = ff("-i", path, "-af", f"{af},ebur128", "-f", "null", "-")
    return float(err.rsplit("I:", 1)[1].split("LUFS")[0])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("bed")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--bed-lufs", type=float, default=-26.0, help="undocked bed loudness")
    ap.add_argument("--fade-out", type=float, default=2.5)
    args = ap.parse_args()

    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", args.video], text=True))
    gain = args.bed_lufs - integrated_lufs(args.bed, MUSIC_EQ)
    music = (f"[1:a]{MUSIC_EQ},volume={gain:.2f}dB,atrim=0:{dur:.3f},"
             f"afade=t=out:st={dur - args.fade_out:.3f}:d={args.fade_out}[m]")
    graph = f"{music};[0:a]asplit=2[v][sc];[m][sc]{DUCK}[md];[v][md]amix=inputs=2:duration=first:normalize=0[mix]"

    with tempfile.TemporaryDirectory() as t:
        pre, ducked, voice = Path(t, "premix.wav"), Path(t, "ducked.wav"), Path(t, "voice.wav")
        ff("-y", "-i", args.video, "-i", args.bed, "-filter_complex", graph + ";[md]anull[dk]",
           "-map", "[mix]", "-c:a", "pcm_s24le", str(pre), "-map", "[dk]", "-c:a", "pcm_s24le", str(ducked))
        ff("-y", "-i", args.video, "-vn", "-c:a", "pcm_s24le", str(voice))

        # measured balance: music vs voice, speech frames vs pause frames (400ms windows)
        v, sr = sf.read(voice)
        m, _ = sf.read(ducked)
        v, m = v.mean(axis=1) if v.ndim > 1 else v, m.mean(axis=1) if m.ndim > 1 else m
        hop = int(0.4 * sr)
        k = min(len(v), len(m)) // hop
        vr = 20 * np.log10(np.sqrt((v[:k * hop].reshape(k, hop) ** 2).mean(1)) + 1e-9)
        mr = 20 * np.log10(np.sqrt((m[:k * hop].reshape(k, hop) ** 2).mean(1)) + 1e-9)
        speech = vr > np.percentile(vr, 60)
        pause = vr < np.percentile(vr, 15)
        print(f"music under speech: {np.median(mr[speech] - vr[speech]):+.1f} dB vs voice; "
              f"music level in pauses vs under speech: {np.median(mr[pause]) - np.median(mr[speech]):+.1f} dB (ducking)")

        err = ff("-i", str(pre), "-af", f"loudnorm={TARGET}:print_format=json", "-f", "null", "-")
        j = json.loads(err[err.rindex("{"):err.rindex("}") + 1])
        af = (f"loudnorm={TARGET}:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
              f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
        ff("-y", "-i", args.video, "-i", str(pre), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", af,
           "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", args.output)
    print(f"done: {args.output}  (bed gain {gain:+.1f} dB → {args.bed_lufs} LUFS undocked)")


if __name__ == "__main__":
    main()
