"""Sync-safe EDL renderer (video-use EDL format, no overlays/subtitles).

Why: video-use's render.py encodes each segment's audio to AAC separately and
concatenates with `-c copy`. Every AAC file carries ~21ms of encoder priming,
so audio drifts later by ~21ms per cut — ~0.5s after 25 cuts. This renderer
instead seeks each range as its own input, snaps range edges to frame
boundaries, applies the 30ms edge fades, and joins video+audio in ONE concat
filter, so both streams share every cut point exactly.

Punch-ins: a range may carry "zoom" (e.g. 1.08); the crop is centred on the
EDL-level "zoom_focus" [x, y] (fractions of the frame, default [0.5, 0.5]) so
that point stays fixed. Alternating zoom across jump cuts disguises them.

Optional: per-range "gain_db" (level-match a softly delivered line) and EDL-level
"tail_hold" seconds (freeze the last frame + silence so an end card can land).

Loudness: two-pass loudnorm to -14 LUFS / -1 dBTP (audio-only second pass).

Usage:
    python tools/render_edl.py <edl.json> -o <out.mp4> [--draft] [--no-loudnorm]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".claude/skills/video-use/helpers"))
from grade import get_preset  # noqa: E402

FADE = 0.03


def probe_fps(path: str) -> Fraction:
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=r_frame_rate", "-of", "csv=p=0", path], text=True)
    return Fraction(out.strip())


def probe_size(path: str) -> tuple[int, int]:
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height", "-of", "csv=p=0", path], text=True)
    w, h = out.strip().split(",")
    return int(w), int(h)


def zoom_filter(z: float, focus: list[float], w: int, h: int) -> str:
    if not z or z <= 1.0:
        return ""
    cw, ch = int(w / z) // 2 * 2, int(h / z) // 2 * 2
    x, y = round((w - cw) * focus[0]), round((h - ch) * focus[1])
    return f"crop={cw}:{ch}:{x}:{y},scale={w}:{h}:flags=lanczos,setsar=1,"


def grade_filter(grade: str | None) -> str:
    if not grade or grade == "none":
        return ""
    try:
        return get_preset(grade)
    except Exception:
        return grade  # raw ffmpeg filter string


def loudnorm(src: Path, dst: Path) -> None:
    target = "I=-14:TP=-1:LRA=11"
    p = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", str(src), "-af",
                        f"loudnorm={target}:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, check=True)
    m = json.loads(p.stderr[p.stderr.rindex("{"):p.stderr.rindex("}") + 1])
    print(f"  measured I={m['input_i']} LUFS  TP={m['input_tp']} dBTP")
    af = (f"loudnorm={target}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", str(src), "-c:v", "copy",
                    "-af", af, "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(dst)],
                   check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Render an EDL with exact A/V sync")
    ap.add_argument("edl", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--draft", action="store_true", help="720p ultrafast CRF 28")
    ap.add_argument("--no-loudnorm", action="store_true")
    args = ap.parse_args()

    edl = json.loads(args.edl.read_text())
    sources = edl["sources"]
    fps = probe_fps(next(iter(sources.values())))
    width, height = probe_size(next(iter(sources.values())))
    focus = edl.get("zoom_focus", [0.5, 0.5])

    inputs, chains, labels = [], [], []
    for i, r in enumerate(edl["ranges"]):
        s = Fraction(round(r["start"] * fps)) / fps          # frame-aligned edges
        e = Fraction(round(r["end"] * fps)) / fps
        d = float(e - s)
        inputs += ["-ss", f"{float(s):.6f}", "-t", f"{d:.6f}", "-i", sources[r["source"]]]
        # exact lengths: -ss/-t input seeking can emit one extra frame on short ranges, and concat then
        # pads the audio by that frame -> everything after drifts 33ms off the EDL timeline
        nf, ns = round((e - s) * fps), round(d * 48000)
        chains.append(f"[{i}:v]trim=end_frame={nf},{zoom_filter(r.get('zoom', 1.0), focus, width, height)}"
                      f"setpts=PTS-STARTPTS[v{i}]")
        gain = f"volume={r['gain_db']}dB," if r.get("gain_db") else ""
        chains.append(f"[{i}:a]aresample=48000,atrim=end_sample={ns},{gain}asetpts=PTS-STARTPTS,"
                      f"afade=t=in:st=0:d={FADE},afade=t=out:st={d - FADE:.6f}:d={FADE}[a{i}]")
        labels.append(f"[v{i}][a{i}]")

    hold = float(edl.get("tail_hold", 0) or 0)
    vf = [f for f in [grade_filter(edl.get("grade")),
                      f"tpad=stop_mode=clone:stop_duration={hold}" if hold else "",
                      "scale=-2:720" if args.draft else "", "format=yuv420p"] if f]
    af = f"apad=pad_dur={hold}" if hold else "anull"
    graph = (";".join(chains) + ";" + "".join(labels) + f"concat=n={len(labels)}:v=1:a=1[vc][ac0];"
             f"[vc]{','.join(vf)}[v];[ac0]{af}[ac]")

    out = args.output
    tmp = out.with_suffix(".prenorm.mp4") if not args.no_loudnorm else out
    enc = ["-c:v", "libx264", "-preset", "ultrafast" if args.draft else "medium",
           "-crf", "28" if args.draft else "16", "-r", str(fps),
           "-g", str(round(fps)), "-keyint_min", str(round(fps))]  # dense GOP: HyperFrames seeks every frame
    cmd = ["ffmpeg", "-nostdin", "-y", "-loglevel", "error", *inputs, "-filter_complex", graph,
           "-map", "[v]", "-map", "[ac]", *enc, "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-movflags", "+faststart", str(tmp)]
    print(f"rendering {len(labels)} ranges @ {float(fps):g}fps → {tmp.name}")
    subprocess.run(cmd, check=True)

    if not args.no_loudnorm:
        print("loudnorm (two-pass, -14 LUFS / -1 dBTP)")
        loudnorm(tmp, out)
        tmp.unlink()
    print(f"done: {out}")


if __name__ == "__main__":
    main()
