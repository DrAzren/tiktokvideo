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

rm -rf _matte_win && mkdir _matte_win
ffmpeg -nostdin -loglevel error -y -i ../edit/cut.mp4 \
  -vf "trim=start_frame=$F0:end_frame=$((F1 + 1)),setpts=PTS-STARTPTS" -an -c:v libx264 -crf 12 -g 30 _matte_win/source.mp4
node "$SD/matte.cjs" _matte_win
node "$SD/safe-zones.cjs" _matte_win

mkdir -p project/frames_fg project/frames_bg
rm -f project/frames_fg/*.png
"$ROOT/.venv/bin/python" -c "from PIL import Image; Image.new('RGBA',(1080,1920),(0,0,0,0)).save('project/_clear.png')"
for ((i = 1; i <= NF; i++)); do ln -f project/_clear.png "$(printf 'project/frames_fg/f_%04d.png' "$i")"; done
n=0
for f in _matte_win/frames_fg/f_*.png; do
  k=$((10#$(basename "$f" .png | sed 's/f_//') + F0))
  cp -f "$f" "$(printf 'project/frames_fg/f_%04d.png' "$k")"; n=$((n + 1))
done
cp _matte_win/safe-zones.json project/safe-zones.json
echo "$FPS" > project/matte.fps
echo "frames_fg: $NF frames, $n real mattes (frames $((F0 + 1))-$((F0 + n)) = $(echo "scale=2; $F0/$FPS" | bc)s+)"
