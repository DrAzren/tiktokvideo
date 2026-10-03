#!/usr/bin/env bash
# Subject matte for the "BPD" apex window ONLY (pattern from videos/ward-psikiatri/captions).
# Matting runs at ~0.5-2 fps here, so the full 84s clip would take an hour+. Only the hero is
# drawn BEHIND the subject, so:
#   1. trim graphics/output.mp4 to the hero window and matte that clip (temp project _hero/)
#   2. safe-zones.cjs on the temp project (real frames only) → copy safe-zones.json over
#   3. project/frames_fg = the real matte inside the window, fully transparent PNGs elsewhere
#      (overlaying a transparent frame is a no-op, so the composite is unchanged outside it)
# Frame k (1-based) shows time (k-1)/30 on the cut.
set -euo pipefail
cd "$(dirname "$0")"
SD=../../../.claude/skills/embedded-captions/scripts
FPS=30
T0=7.9; T1=10.95                       # = graphics/inserts.py HERO (keep in sync)
F0=$(python3 -c "print(round($T0*$FPS)+1)")
N=$(python3 -c "print(round(($T1-$T0)*$FPS))")
TOTAL=$(ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 project/source.mp4)

rm -rf _hero && mkdir _hero
ffmpeg -nostdin -v error -y -ss "$(python3 -c "print(($F0-1)/$FPS)")" -i project/source.mp4 -frames:v "$N" \
  -c:v libx264 -crf 12 -g 1 -an _hero/source.mp4
node "$SD/matte.cjs" "$PWD/_hero"
node "$SD/safe-zones.cjs" "$PWD/_hero"
cp _hero/safe-zones.json project/safe-zones.json

rm -rf project/frames_fg && mkdir -p project/frames_fg
../../../.venv/bin/python - "$F0" "$N" "$TOTAL" <<'EOF'
import os, shutil, sys
from PIL import Image
f0, n, total = map(int, sys.argv[1:])
blank = "project/frames_fg/_blank.png"
Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)).save(blank)
real = sorted(os.listdir("_hero/frames_fg"))
assert len(real) >= n - 1, (len(real), n)
for k in range(1, total + 1):
    dst = f"project/frames_fg/f_{k:04d}.png"
    i = k - f0
    if 0 <= i < len(real):
        shutil.copy(f"_hero/frames_fg/{real[i]}", dst)
    else:
        os.link(blank, dst)
os.remove(blank)
print(f"frames_fg: {total} frames, real matte at f_{f0:04d}..f_{f0 + len(real) - 1:04d}")
EOF
echo "$FPS" > project/matte.fps
