"""Clean a grayscale alpha video (tools/rvm_matte.py output) against its source footage.

RVM keeps a soft band of whatever sat behind the head: on a car recording, the light-grey roof
lining rims the top of the hair and a sliver of the black headrest ghosts beside the ear.
Per frame:
  1. choke   alpha' = clip((alpha - LO) / (HI - LO)): drops the faint partial matte (ghosts)
  2. decontaminate: in the edge band only, pixels that are bright AND colourless (the roof
     lining, not skin or hair) lose their alpha
  3. --zone x0,y0,x1,y1 (repeatable, source px): fixed-camera areas where a dark seat/headrest sits
     right behind the subject; within ZONE_BAND px of the edge only skin-coloured pixels keep their alpha
  4. erode 1 px + 1 px blur so the edge is soft but never wider than the subject

Usage:
    python tools/refine_matte.py <video.mp4> <alpha.mp4> -o <alpha_refined.mp4> [--lo 0.25 --hi 0.85]
Both inputs must have the same size and frame count (cut them with the same EDL).
"""

from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

import numpy as np
from scipy import ndimage


ZONE_BAND = 30


def probe(path: Path) -> tuple[int, int, str]:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
         "-of", "csv=p=0", str(path)], text=True).strip().split(",")
    return int(out[0]), int(out[1]), out[2]


def smooth(x: np.ndarray, a: float, b: float) -> np.ndarray:
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=Path)
    ap.add_argument("alpha", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--lo", type=float, default=0.25)
    ap.add_argument("--hi", type=float, default=0.85)
    ap.add_argument("--band", type=int, default=9, help="edge band half-width in px for decontamination")
    ap.add_argument("--zone", action="append", default=[], help="x0,y0,x1,y1: static dark-object zone (repeatable)")
    args = ap.parse_args()

    w, h, fps = probe(args.video)
    rd = lambda p, fmt: subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(p), "-f", "rawvideo", "-pix_fmt", fmt, "-"],
                                         stdout=subprocess.PIPE)
    dv, da = rd(args.video, "rgb24"), rd(args.alpha, "gray")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{w}x{h}",
                            "-r", fps, "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "8",
                            "-pix_fmt", "yuv444p", "-g", "30", str(args.output)], stdin=subprocess.PIPE)
    zmask = np.zeros((h, w), np.float32)
    for z in args.zone:
        x0, y0, x1, y1 = map(int, z.split(","))
        zmask[y0:y1, x0:x1] = 1
    zmask = ndimage.gaussian_filter(zmask, 8)
    n, t0 = 0, time.time()
    while True:
        bv, ba = dv.stdout.read(w * h * 3), da.stdout.read(w * h)
        if len(bv) < w * h * 3 or len(ba) < w * h:
            break
        rgb = np.frombuffer(bv, np.uint8).reshape(h, w, 3).astype(np.float32) / 255
        a = np.frombuffer(ba, np.uint8).reshape(h, w).astype(np.float32) / 255
        a = np.clip((a - args.lo) / (args.hi - args.lo), 0, 1)
        mx, mn = rgb.max(2), rgb.min(2)
        lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
        sat = (mx - mn) / (mx + 1e-4)
        hard = a > 0.5
        band = ndimage.binary_dilation(hard, iterations=args.band) & ~ndimage.binary_erosion(hard, iterations=args.band)
        roof = smooth(lum, 0.26, 0.40) * (1 - smooth(sat, 0.12, 0.24))
        a = np.where(band, a * (1 - roof), a)
        if args.zone:
            near = ~ndimage.binary_erosion(a > 0.5, iterations=ZONE_BAND)
            # only skin survives there: warm and saturated (the seat is black/grey leather)
            skin = smooth(sat, 0.16, 0.28) * smooth(rgb[..., 0] - rgb[..., 2], 0.04, 0.10)
            seat = (1 - skin) * zmask
            a = np.where(near, a * (1 - seat), a)
        a = ndimage.grey_erosion(a, size=(3, 3))
        a = ndimage.gaussian_filter(a, 1.0)
        enc.stdin.write((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        n += 1
        if n % 300 == 0:
            print(f"{n} frames, {n / (time.time() - t0):.1f} fps", flush=True)
    enc.stdin.close()
    enc.wait()
    print(f"wrote {args.output}: {n} frames in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
