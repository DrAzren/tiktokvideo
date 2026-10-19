#!/usr/bin/env bash
# Rebuild everything after Higgsfield assets are in place:
#   broll/*.mp4 (Kling), stills/*.png, audio/vo_s1..6.mp3 (ElevenLabs via Higgsfield), doc/public/img/{pinel,tuke}.jpg
# Usage: doc/assemble.sh [1080|4k]
set -euo pipefail
cd "$(dirname "$0")"
RES="${1:-4k}"
PY=../../../.venv/bin/python
export HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell
export PUPPETEER_EXECUTABLE_PATH=$HOME/bin/headless_shell_nosandbox

$PY score.py                                   # score + SFX + narration premix → ../audio/mix_premaster.wav
IN=../audio/mix_premaster.wav
J=$(ffmpeg -nostdin -hide_banner -i $IN -af loudnorm=I=-14:TP=-1.2:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
M=$(echo "$J" | python3 -c "import json,sys;d=json.load(sys.stdin);print(f\"measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:offset={d['target_offset']}\")")
mkdir -p public/audio
ffmpeg -nostdin -loglevel error -y -i $IN -af "loudnorm=I=-14:TP=-1.2:LRA=11:$M:linear=true" -ar 48000 -c:a pcm_s24le public/audio/mix.wav

$PY build_doc.py
python3 make_srt.py
(cd public && npx --yes hyperframes lint 2>&1 | grep -E "✗|◇")
if [ "$RES" = 4k ]; then
  npx --yes hyperframes render public -o "$PWD/render_4k.mp4" --quality delivery --resolution landscape-4k > render_4k.log 2>&1
  OUT=../final_4k.mp4; SRC=render_4k.mp4
else
  npx --yes hyperframes render public -o "$PWD/render_1080.mp4" --quality delivery > render_1080.log 2>&1
  OUT=../final_1080.mp4; SRC=render_1080.mp4
fi
# replace the render's AAC with a high-bitrate encode of the exact master, faststart for YouTube
ffmpeg -nostdin -loglevel error -y -i $SRC -i public/audio/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -ar 48000 \
  -movflags +faststart $OUT
ffprobe -v error -show_entries stream=codec_type,width,height,r_frame_rate,duration -of compact $OUT
ffmpeg -nostdin -hide_banner -i $OUT -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
