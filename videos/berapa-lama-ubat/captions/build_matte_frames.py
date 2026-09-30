"""Full-length frames_fg/ for the captions project with a REAL matte only in the hero window.

Matting is CPU-bound (~0.7 fps here); only "BERGANTUNG" is drawn behind the subject, so only
6.0-9.0 s of the cut is matted (_matte/, via embedded-captions matte.cjs on a trimmed clip).
Every other frame is a hard-linked transparent PNG (overlay = no-op). frames_bg/ is extracted
from project/source.mp4 (= graphics/output.mp4) for preview-frames.cjs.
"""
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image

C = Path(__file__).parent
P = C / "project"
WIN_START_FRAME = 180            # 6.0 s * 30 fps: _matte/frames_fg/f_0001 == project frame f_0181
N = int(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                                 "stream=nb_read_packets", "-of", "csv=p=0", str(P / "source.mp4")], text=True))
fg = P / "frames_fg"
shutil.rmtree(fg, ignore_errors=True); fg.mkdir()
blank = C / "_blank.png"
Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)).save(blank)
real = sorted((C / "_matte" / "frames_fg").glob("f_*.png"))
for i in range(1, N + 1):
    k = i - WIN_START_FRAME
    src = real[k - 1] if 1 <= k <= len(real) else blank
    os.link(src, fg / f"f_{i:04d}.png")
bg = P / "frames_bg"
shutil.rmtree(bg, ignore_errors=True); bg.mkdir()
subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(P / "source.mp4"), "-start_number", "1",
                str(bg / "f_%04d.png")], check=True)
(P / "matte.fps").write_text("30")
print(f"{N} frames; real matte f_{WIN_START_FRAME + 1:04d}-f_{WIN_START_FRAME + len(real):04d}; frames_bg {len(list(bg.iterdir()))}")
