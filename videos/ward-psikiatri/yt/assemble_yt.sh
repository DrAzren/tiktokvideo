#!/usr/bin/env bash
# 16:9 YouTube version: render the composition, mix the music bed, master, make a <30 MB share copy.
#   public/speaker_alpha.webm   the talking head with its background removed (hyperframes remove-background)
#   public/voice.wav            podcast-polished voice (tools/enhance_speech.py on edit/cut.mp4)
#   public/broll/*.mp4          Higgsfield Seedance 2.5 B-roll (16:9, 720p)
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../../.. && pwd)"
PY="$ROOT/.venv/bin/python"
export HYPERFRAMES_ROOT=~/hyperframes HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell \
       PUPPETEER_EXECUTABLE_PATH=$HOME/bin/headless_shell_nosandbox
"$PY" build_yt.py | head -1
(cd public && npx --yes hyperframes lint 2>&1 | grep -E "✗|◇")
npx --yes hyperframes render public -o "$PWD/render.mp4" > render.log 2>&1
tail -3 render.log | head -1
"$PY" "$ROOT/tools/mix_music.py" render.mp4 ../audio/bed.wav -o ../final_youtube.mp4 --bed-lufs -21
ffprobe -v error -show_entries stream=codec_type,width,height,duration,nb_frames -of compact ../final_youtube.mp4
ffmpeg -nostdin -hide_banner -i ../final_youtube.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
# share copy under 30 MB (two-pass, 1080p)
P=$(mktemp -d)/2pass
ffmpeg -nostdin -loglevel error -y -i ../final_youtube.mp4 -c:v libx264 -preset slower -b:v 1480k -g 60 -pix_fmt yuv420p -pass 1 -passlogfile "$P" -an -f null -
ffmpeg -nostdin -loglevel error -y -i ../final_youtube.mp4 -c:v libx264 -preset slower -b:v 1480k -g 60 -pix_fmt yuv420p -pass 2 -passlogfile "$P" \
  -c:a aac -b:a 160k -movflags +faststart ../final_youtube_share.mp4
ls -la ../final_youtube.mp4 ../final_youtube_share.mp4 | awk '{print $5, $9}'
