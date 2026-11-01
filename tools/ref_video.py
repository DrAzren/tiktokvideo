"""Download, transcribe and analyze a reference video (someone else's TikTok/Reel/Short).

    .venv/bin/python tools/ref_video.py <url-or-local-file> [--model small] [--language ms]
                                        [--cookies cookies.txt] [--scene 0.3] [--out references]

Writes references/<slug>/:
    video.mp4          the download (or a copy of the local file)
    video.info.json    yt-dlp metadata (title, uploader, views, likes, upload date, ...)
    transcript.json    raw openai-whisper output with word timestamps
    words.json         Scribe-shaped {language_code, words:[{text,start,end}]} (same shape as edit/transcripts)
    transcript.srt/.txt
    contact.jpg        one frame per shot, labelled with its start time
    analysis.json/.md  format, pacing (cuts/min, shot lengths), speech (wpm, pauses), loudness, hook

Steps are cached: re-running skips anything already on disk (delete a file to redo it).

yt-dlp runs with `--compat-options no-certifi` so it trusts the system CA store (the cloud
container's HTTPS proxy re-signs TLS; yt-dlp's bundled certifi list would reject it).
YouTube/TikTok/Instagram often block datacenter IPs. If a download fails with 403 or
"IP address is blocked", pass browser cookies (--cookies) or have the user upload the file and
run this on the local path instead.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV_BIN = Path(sys.executable).parent


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, text=True, **kw)


def slugify(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", s).strip("-")[:80] or "ref"


# ---------------------------------------------------------------- download
def ytdlp_cmd() -> list[str]:
    exe = VENV_BIN / "yt-dlp"
    return [str(exe) if exe.exists() else "yt-dlp", "--compat-options", "no-certifi", "--js-runtimes", "node"]


def resolve_slug(src: str, extra: list[str]) -> str:
    out = run(ytdlp_cmd() + extra + ["--no-warnings", "--skip-download", "--print", "%(extractor_key)s-%(id)s", src],
              capture_output=True)
    return slugify(out.stdout.strip().splitlines()[-1])


def download(src: str, dest: Path, extra: list[str]) -> None:
    if (dest / "video.mp4").exists():
        print(f"cached: {dest / 'video.mp4'}")
        return
    run(ytdlp_cmd() + extra + [
        "--no-playlist", "--no-progress",
        "-f", "bv*[height<=1920][vcodec^=avc1]+ba[acodec^=mp4a]/bv*[height<=1920]+ba/b",
        "--merge-output-format", "mp4", "--remux-video", "mp4",
        "--write-info-json", "-o", str(dest / "video.%(ext)s"), src,
    ])


# ---------------------------------------------------------------- transcribe
def transcribe(video: Path, dest: Path, model_name: str, language: str | None) -> dict:
    tj = dest / "transcript.json"
    if tj.exists():
        print(f"cached: {tj}")
        return json.loads(tj.read_text())
    import whisper
    from whisper.utils import get_writer

    wav = dest / "audio.wav"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(wav)])
    model = whisper.load_model(model_name, device="cpu")
    result = model.transcribe(str(wav), language=language, word_timestamps=True, fp16=False, verbose=False)
    tj.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    for fmt in ("srt", "txt"):
        get_writer(fmt, str(dest))(result, str(dest / "transcript.wav"))
    words = [{"text": w["word"].strip(), "start": round(w["start"], 3), "end": round(w["end"], 3)}
             for s in result["segments"] for w in s.get("words", [])]
    (dest / "words.json").write_text(json.dumps(
        {"language_code": result.get("language"), "words": words}, ensure_ascii=False, indent=1))
    wav.unlink(missing_ok=True)
    return result


# ---------------------------------------------------------------- analyze
def probe(video: Path) -> dict:
    out = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(video)],
              capture_output=True)
    return json.loads(out.stdout)


def scene_cuts(video: Path, threshold: float) -> list[float]:
    p = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(video), "-an", "-vf",
                        f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"],
                       capture_output=True, text=True)
    return [float(m) for m in re.findall(r"pts_time:([0-9.]+)", p.stderr)]


def loudness(video: Path) -> dict:
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-vn",
                        "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    summary = p.stderr.split("Summary:")[-1]

    def grab(label: str) -> float | None:
        m = re.search(label + r":\s+(-?[0-9.]+|-inf)", summary)
        return float(m.group(1)) if m and m.group(1) != "-inf" else None

    return {"integrated_lufs": grab("I"), "lra_lu": grab("LRA"), "true_peak_dbtp": grab("Peak")}


def contact_sheet(video: Path, shots: list[tuple[float, float]], out: Path, max_tiles: int = 30) -> None:
    from PIL import Image, ImageDraw

    if len(shots) > max_tiles:
        step = len(shots) / max_tiles
        shots = [shots[int(i * step)] for i in range(max_tiles)]
    tiles = []
    tmp = out.parent / ".frames"
    tmp.mkdir(exist_ok=True)
    for i, (a, b) in enumerate(shots):
        f = tmp / f"{i:03d}.jpg"
        t = a + min(0.5, (b - a) / 2)
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1",
             "-vf", "scale=-2:360", str(f)])
        if f.exists():
            im = Image.open(f).convert("RGB")
            ImageDraw.Draw(im).rectangle([0, 0, 120, 26], fill=(0, 0, 0))
            ImageDraw.Draw(im).text((6, 6), f"#{i + 1} {a:6.2f}s", fill=(255, 255, 0))
            tiles.append(im)
    shutil.rmtree(tmp, ignore_errors=True)
    if not tiles:
        return
    cols = min(6, len(tiles))
    rows = -(-len(tiles) // cols)
    w, h = tiles[0].size
    sheet = Image.new("RGB", (cols * w, rows * h), (20, 20, 20))
    for i, im in enumerate(tiles):
        sheet.paste(im.resize((w, h)), ((i % cols) * w, (i // cols) * h))
    sheet.save(out, quality=85)


def analyze(video: Path, dest: Path, result: dict, threshold: float) -> dict:
    meta = probe(video)
    v = next((s for s in meta["streams"] if s["codec_type"] == "video"), {})
    a = next((s for s in meta["streams"] if s["codec_type"] == "audio"), {})
    dur = float(meta["format"]["duration"])
    num, den = (v.get("avg_frame_rate") or "0/1").split("/")
    fps = round(float(num) / float(den), 3) if float(den) else None

    cuts = [c for c in scene_cuts(video, threshold) if 0.2 < c < dur - 0.2]
    edges = [0.0] + cuts + [dur]
    shots = list(zip(edges[:-1], edges[1:]))
    lens = [b - a for a, b in shots]

    words = [w for s in result.get("segments", []) for w in s.get("words", [])]
    speech = sum(w["end"] - w["start"] for w in words)
    gaps = [b["start"] - a["end"] for a, b in zip(words, words[1:])]
    first_word = words[0]["start"] if words else None

    info_path = dest / "video.info.json"
    info = json.loads(info_path.read_text()) if info_path.exists() else {}
    keep = ("title", "uploader", "channel", "webpage_url", "upload_date", "duration", "view_count",
            "like_count", "comment_count", "repost_count", "description", "tags", "track", "artist")
    a_info = {
        "source": {k: info[k] for k in keep if info.get(k) not in (None, "", [])},
        "format": {"duration_s": round(dur, 2), "width": v.get("width"), "height": v.get("height"), "fps": fps,
                   "orientation": ("vertical" if (v.get("height") or 0) > (v.get("width") or 0) else "horizontal"),
                   "video_codec": v.get("codec_name"), "audio_codec": a.get("codec_name")},
        "pacing": {"scene_threshold": threshold, "shots": len(shots),
                   "cuts_per_min": round(len(cuts) / dur * 60, 1) if dur else None,
                   "shot_len_avg_s": round(statistics.mean(lens), 2),
                   "shot_len_median_s": round(statistics.median(lens), 2),
                   "shot_len_min_s": round(min(lens), 2), "shot_len_max_s": round(max(lens), 2),
                   "cut_times_s": [round(c, 2) for c in cuts]},
        "speech": {"language": result.get("language"), "words": len(words),
                   "wpm": round(len(words) / dur * 60, 1) if dur else None,
                   "speech_ratio": round(speech / dur, 2) if dur else None,
                   "first_word_at_s": round(first_word, 2) if first_word is not None else None,
                   "pauses_over_0_5s": int(sum(g > 0.5 for g in gaps)),
                   "longest_pause_s": round(max(gaps), 2) if gaps else None},
        "loudness": loudness(video) if a else {},
        "hook_first_3s": " ".join(w["word"].strip() for w in words if w["start"] < 3.0),
    }
    (dest / "analysis.json").write_text(json.dumps(a_info, ensure_ascii=False, indent=1, default=lambda o: o.item()))
    contact_sheet(video, shots, dest / "contact.jpg")

    src, fm, pc, sp, ld = (a_info[k] for k in ("source", "format", "pacing", "speech", "loudness"))
    md = [f"# Reference: {src.get('title', video.name)}", ""]
    if src:
        md += [f"- **By:** {src.get('uploader') or src.get('channel', '?')} · {src.get('webpage_url', '')}",
               f"- **Posted:** {src.get('upload_date', '?')} · views {src.get('view_count', '?')} · "
               f"likes {src.get('like_count', '?')} · comments {src.get('comment_count', '?')}", ""]
    md += [f"- **Format:** {fm['width']}×{fm['height']} {fm['orientation']} @ {fm['fps']} fps, {fm['duration_s']} s",
           f"- **Pacing:** {pc['shots']} shots, {pc['cuts_per_min']} cuts/min, shot length avg "
           f"{pc['shot_len_avg_s']} s / median {pc['shot_len_median_s']} s (min {pc['shot_len_min_s']}, "
           f"max {pc['shot_len_max_s']})",
           f"- **Speech:** {sp['language']}, {sp['words']} words, {sp['wpm']} wpm, speech fills "
           f"{sp['speech_ratio']} of runtime, first word at {sp['first_word_at_s']} s, "
           f"{sp['pauses_over_0_5s']} pauses > 0.5 s (longest {sp['longest_pause_s']} s)",
           f"- **Loudness:** {ld.get('integrated_lufs')} LUFS integrated, LRA {ld.get('lra_lu')} LU, "
           f"true peak {ld.get('true_peak_dbtp')} dBTP",
           "", f"**Hook (first 3 s):** {a_info['hook_first_3s'] or '(no speech)'}", "",
           "## Transcript", "", (dest / "transcript.txt").read_text().strip() if (dest / "transcript.txt").exists()
           else "", "", "Contact sheet: `contact.jpg` (one frame per shot). Cut times are in `analysis.json`."]
    (dest / "analysis.md").write_text("\n".join(md) + "\n")
    return a_info


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="URL (anything yt-dlp supports) or a local video file")
    ap.add_argument("--out", type=Path, default=ROOT / "references")
    ap.add_argument("--name", help="folder name (default: <extractor>-<id> or the file stem)")
    ap.add_argument("--model", default="small", help="whisper model: tiny/base/small/medium/large-v3/turbo")
    ap.add_argument("--language", help="force a language code (default: auto-detect)")
    ap.add_argument("--scene", type=float, default=0.3, help="ffmpeg scene-change threshold for cut detection")
    ap.add_argument("--cookies", help="Netscape cookies.txt for sites that need sign-in or block this IP")
    ap.add_argument("--skip-transcribe", action="store_true")
    args = ap.parse_args()

    extra = ["--cookies", args.cookies] if args.cookies else []
    local = Path(args.source).expanduser()
    if local.exists():
        dest = args.out / (args.name or slugify(local.stem))
        dest.mkdir(parents=True, exist_ok=True)
        video = dest / "video.mp4"
        if not video.exists():
            if local.suffix.lower() == ".mp4":
                shutil.copy2(local, video)
            else:
                run(["ffmpeg", "-v", "error", "-y", "-i", str(local), "-c", "copy", str(video)])
    else:
        dest = args.out / (args.name or resolve_slug(args.source, extra))
        dest.mkdir(parents=True, exist_ok=True)
        download(args.source, dest, extra)
        video = dest / "video.mp4"

    result = {} if args.skip_transcribe else transcribe(video, dest, args.model, args.language)
    analyze(video, dest, result, args.scene)
    print((dest / "analysis.md").read_text())
    print(f"→ {dest}")


if __name__ == "__main__":
    main()
