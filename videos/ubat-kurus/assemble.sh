#!/usr/bin/env bash
# Final assembly for "3 Ubat Psikiatri Kuruskan Badan".
#
#   edit/cut.mp4                 cut + grade + punch-ins, 1080x1920 (tools/render_edl.py)
#   graphics/output.mp4          ^ + headroom cards + full-screen inserts (Seedance clip, chart, JANGAN)
#   captions/project/            embedded-captions `loud`, one line on the chest band. Every caption is
#                                IN FRONT of the subject, so no matte: the project's own index.html render
#                                (captions drawn over the video, normal blending) is the captioned video.
#   audio/bed.wav                original ambient bed (tools/ambient_bed.py) → tools/mix_music.py
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../.. && pwd)"
PY="$ROOT/.venv/bin/python"
export HYPERFRAMES_ROOT=~/hyperframes
export HYPERFRAMES_BROWSER_PATH=$(ls -d /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell \
  /opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell 2>/dev/null | head -1)
export PUPPETEER_EXECUTABLE_PATH=~/bin/headless_shell_nosandbox

npx --yes hyperframes render captions/project -o "$PWD/captions/captioned.mp4" --keyframe-interval 1 \
  --skill embedded-captions 2>&1 | grep -v "npm notice" | tail -3
"$PY" "$ROOT/tools/check_sync.py" edit/edl.json captions/captioned.mp4 | tail -1

"$PY" "$ROOT/tools/mix_music.py" captions/captioned.mp4 audio/bed.wav -o final.mp4 --bed-lufs -20
"$PY" "$ROOT/tools/check_sync.py" edit/edl.json final.mp4 | tail -1
ffprobe -v error -show_entries stream=codec_type,width,height,duration,nb_frames -of compact final.mp4
ffmpeg -nostdin -hide_banner -i final.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
