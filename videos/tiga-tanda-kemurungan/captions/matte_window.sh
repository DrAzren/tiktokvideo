#!/usr/bin/env bash
# Subject matte for the hero window only (CPU matting runs ~0.5-2 fps here; the whole clip would take 1h+).
# Only the "KEMURUNGAN" apex is drawn BEHIND the subject, so only its frames need a real matte:
#   1. trim edit/cut.mp4 to the window (graphics don't touch the subject there) → _matte_win/source.mp4
#   2. embedded-captions matte.cjs on that temp project (+ safe-zones.cjs on the real frames only)
#   3. project/frames_fg/f_%04d.png for the whole clip: real mattes inside the window, a shared
#      fully transparent PNG everywhere else (overlay = no-op), same numbering as matte.cjs (f_0001 = t 0)
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../../.. && pwd)"
SD="$ROOT/.claude/skills/embedded-captions/scripts"
F0=${1:-177}   # first frame of the window (0-based) — 5.90s
F1=${2:-285}   # last frame (inclusive) — 9.50s
FPS=30
NF=$(ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 ../edit/cut.mp4)
export HYPERFRAMES_ROOT=~/hyperframes PUPPETEER_EXECUTABLE_PATH=~/bin/headless_shell_nosandbox

if [ "${REMATTE:-0}" = 1 ] || [ ! -d _matte_win/frames_fg ]; then   # matting is the slow part: reuse it
  rm -rf _matte_win && mkdir _matte_win
  ffmpeg -nostdin -loglevel error -y -i ../edit/cut.mp4 \
    -vf "trim=start_frame=$F0:end_frame=$((F1 + 1)),setpts=PTS-STARTPTS" -an -c:v libx264 -crf 12 -g 30 _matte_win/source.mp4
  node "$SD/matte.cjs" _matte_win
  node "$SD/safe-zones.cjs" _matte_win
fi

mkdir -p project/frames_fg project/frames_bg
rm -f project/frames_fg/*.png
rm -f project/_clear.png
"$ROOT/.venv/bin/python" -c "from PIL import Image; Image.new('RGBA',(1080,1920),(0,0,0,0)).save('project/_clear.png')"
for ((i = 1; i <= NF; i++)); do ln -f project/_clear.png "$(printf 'project/frames_fg/f_%04d.png' "$i")"; done
n=0
for f in _matte_win/frames_fg/f_*.png; do
  k=$((10#$(basename "$f" .png | sed 's/f_//') + F0))
  # --remove-destination: the target is a hard link to the shared clear frame; writing through it
  # would overwrite that one inode (= every transparent frame) with this matte
  cp --remove-destination "$f" "$(printf 'project/frames_fg/f_%04d.png' "$k")"; n=$((n + 1))
done
cp _matte_win/safe-zones.json project/safe-zones.json
echo "$FPS" > project/matte.fps
# guard: the shared clear frame must still be fully transparent, and the real mattes distinct from it
"$ROOT/.venv/bin/python" - <<'PY'
import numpy as np; from PIL import Image
c = np.asarray(Image.open("project/_clear.png"))[..., 3]
m = np.asarray(Image.open("project/frames_fg/f_0230.png"))[..., 3]
assert c.max() == 0, "clear frame is not transparent"
assert (m > 128).mean() > 0.2, "hero-window matte frame looks empty"
print(f"check: clear frame transparent; f_0230 subject coverage {(m > 128).mean():.0%}")
PY
echo "frames_fg: $NF frames, $n real mattes (frames $((F0 + 1))-$((F0 + n)) = $(echo "scale=2; $F0/$FPS" | bc)s+)"
