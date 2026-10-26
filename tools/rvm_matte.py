"""Human video matting with RobustVideoMatting (temporally consistent, CPU) → grayscale alpha video.

hyperframes remove-background (u2net_human_seg, per frame) glues nearby objects to the
subject (a car-seat headrest, a seatbelt) and flickers at the hair. RVM tracks the person
through time with a recurrent state and keeps only the human.

Runs the official ONNX exports with onnxruntime (model graphs only, no third-party Python code).
Setup (once per container, ~120 MB):
    mkdir -p ~/models/rvm && cd ~/models/rvm
    curl -sSLO https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_resnet50_fp32.onnx
    curl -sSLO https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx
    uv pip install --python .venv/bin/python onnxruntime

Usage:
    python tools/rvm_matte.py <video> -o alpha.mp4 [--model resnet50|mobilenetv3] [--downsample 0.4]
Output is a gray yuv444 H.264 (crf 8) the same size/fps/frame count as the input; composite with
    ffmpeg -i bg -i video -i alpha.mp4 -filter_complex "[1][2]alphamerge[fg];[0][fg]overlay"
"""

from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort

RVM = Path.home() / "models" / "rvm"


def probe(path: Path) -> tuple[int, int, str]:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
         "-of", "csv=p=0", str(path)], text=True).strip().split(",")
    return int(out[0]), int(out[1]), out[2]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--model", default="resnet50", choices=["resnet50", "mobilenetv3"])
    ap.add_argument("--downsample", type=float, default=0.4, help="RVM downsample_ratio (0.25-0.5 for 720p portrait)")
    ap.add_argument("--threads", type=int, default=0)
    args = ap.parse_args()
    opts = ort.SessionOptions()
    if args.threads:
        opts.intra_op_num_threads = args.threads
    net = ort.InferenceSession(str(RVM / f"rvm_{args.model}_fp32.onnx"), opts, providers=["CPUExecutionProvider"])

    w, h, fps = probe(args.video)
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(args.video), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{w}x{h}",
                            "-r", fps, "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "8",
                            "-pix_fmt", "yuv444p", "-g", "30", str(args.output)], stdin=subprocess.PIPE)
    rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4
    ratio = np.array([args.downsample], np.float32)
    n, t0 = 0, time.time()
    while True:
        buf = dec.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        src = np.frombuffer(buf, np.uint8).reshape(1, h, w, 3).transpose(0, 3, 1, 2).astype(np.float32) / 255
        _, pha, *rec = net.run(None, {"src": src, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3],
                                      "downsample_ratio": ratio})
        enc.stdin.write(np.clip(pha[0, 0] * 255 + 0.5, 0, 255).astype(np.uint8).tobytes())
        n += 1
        if n % 150 == 0:
            print(f"{n} frames, {n / (time.time() - t0):.2f} fps", flush=True)
    enc.stdin.close()
    enc.wait()
    dec.wait()
    print(f"wrote {args.output}: {n} frames in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
