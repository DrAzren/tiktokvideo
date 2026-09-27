"""Verify a rendered EDL keeps audio in sync: cross-correlate each range's source
audio against the output at its expected position and report the lag.

Usage:
    python tools/check_sync.py <edl.json> <rendered.mp4> [--tolerance-ms 25]
Exit code 1 if any range lags more than the tolerance.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 16000


def load_audio(path: str, tmp: Path) -> np.ndarray:
    wav = tmp / (Path(path).stem + ".wav")
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", path, "-vn", "-ac", "1",
                    "-ar", str(SR), str(wav)], check=True)
    return sf.read(wav)[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("edl", type=Path)
    ap.add_argument("rendered")
    ap.add_argument("--tolerance-ms", type=float, default=25)
    args = ap.parse_args()

    edl = json.loads(args.edl.read_text())
    src_path = next(iter(edl["sources"].values()))
    fps = Fraction(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                            "stream=r_frame_rate", "-of", "csv=p=0", src_path], text=True).strip())
    with tempfile.TemporaryDirectory() as t:
        src, out = load_audio(src_path, Path(t)), load_audio(args.rendered, Path(t))

    worst, t_out = 0.0, 0.0
    for i, r in enumerate(edl["ranges"]):
        s = float(Fraction(round(r["start"] * fps)) / fps)
        d = float(Fraction(round(r["end"] * fps)) / fps) - s
        m = min(d - 0.1, 1.0)
        if m > 0.2:
            ref = src[int((s + 0.05) * SR):int((s + 0.05 + m) * SR)]
            w = int(0.6 * SR)
            lo = max(0, int((t_out + 0.05) * SR) - w)
            win = out[lo:int((t_out + 0.05 + m) * SR) + w]
            lag = (int(np.argmax(np.correlate(win, ref, mode="valid"))) + lo) / SR - (t_out + 0.05)
            worst = max(worst, abs(lag))
            print(f"range {i:3d} @ {t_out:7.2f}s  lag {lag * 1000:+6.1f} ms")
        t_out += d
    print(f"worst |lag| = {worst * 1000:.1f} ms (tolerance {args.tolerance_ms:.0f} ms)")
    sys.exit(1 if worst * 1000 > args.tolerance_ms else 0)


if __name__ == "__main__":
    main()
