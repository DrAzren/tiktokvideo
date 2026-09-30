"""Build the working source src_clean.mp4 from the CapCut export (raw/ubat.mp4, 2160x3840 @ 60).

The export has CapCut captions burned in (text never above y=1421 on the 1080x1920 grid) and a
music bed under the voice. User picked "use this file": crop the frame so the captions fall off
the bottom (crop bottom at y=1404/1920 -> 1.3675x, taken from the 4K pixels so no upscale), and
replace the audio with the demucs vocal stem (edit/sep/htdemucs/take/vocals.wav) so cuts don't
chop the music; a new bed goes on in stage 6. Only the talking take (0-78.5 s) is kept.
"""
import subprocess
from pathlib import Path

E = Path(__file__).parent
TAKE = 78.5
CROP_H = 2808            # 4K pixels: 1404 * 2 (burned captions start at 1421 * 2)
CROP_W = 1580            # CROP_H * 9/16, even
FACE_X = 572 * 2         # face centre (glasses 320-825 on the 1080 grid)
x0 = FACE_X - CROP_W // 2
assert 0 <= x0 and x0 + CROP_W <= 2160
vf = f"crop={CROP_W}:{CROP_H}:{x0}:0,fps=30,scale=1080:1920:flags=lanczos,format=yuv420p"
subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-t", str(TAKE), "-i", str(E.parent / "raw" / "ubat.mp4"),
                "-i", str(E / "sep/htdemucs/take/vocals.wav"), "-map", "0:v", "-map", "1:a", "-vf", vf,
                "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-g", "30", "-keyint_min", "30",
                "-c:a", "pcm_s16le", "-t", str(TAKE), str(E / "src_clean.mov")], check=True)
print("src_clean.mov", vf)
