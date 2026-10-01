#!/usr/bin/env bash
# Final assembly for "Fasa Mania dalam Bipolar Mood Disorder".
#
#   graphics/output.mp4          cut + punch-ins + teal header band (picture shifted 180px) + cards
#                                + full-screen B-roll / MG inserts
#   captions/bg_plus_caps.mp4    ^ + every caption (normal blend: dark stroke/shadow intact), including
#                                the "BIPOLAR" hero that must sit BEHIND the head
#   captions/project/frames_fg   subject matte — real only for the hero window (5.40-7.93s, make_matte.sh),
#                                transparent elsewhere (overlay = no-op there)
#   captions/fg_alpha.webm       front captions with real alpha (first 9s): inside the matte window the
#                                matte would otherwise cover caption lines that touch the head, so the
#                                front copy is enabled just there
#   audio/bed.wav                original ambient bed (tools/ambient_bed.py) → tools/mix_music.py:
#                                voice chain (--voice-fx enhance), sidechain-ducked bed, -14 LUFS / -1 dBTP
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../.. && pwd)"
PY="$ROOT/.venv/bin/python"
W0=5.40; W1=7.93   # matte window (seconds on the cut)

ffmpeg -nostdin -y -loglevel error \
  -i captions/bg_plus_caps.mp4 \
  -framerate 30 -i captions/project/frames_fg/f_%04d.png \
  -c:v libvpx-vp9 -i captions/fg_alpha.webm \
  -i graphics/output.mp4 \
  -filter_complex "[1:v]format=yuva420p[m];[0:v][m]overlay=format=auto[a];[2:v]format=yuva420p[c];[a][c]overlay=format=auto:eof_action=pass:enable='between(t,$W0,$W1)',format=yuv420p[v]" \
  -map "[v]" -map 3:a -r 30 -c:v libx264 -crf 14 -preset medium -g 30 -c:a copy \
  -movflags +faststart captions/captioned.mp4
echo "captioned → captions/captioned.mp4"

"$PY" "$ROOT/tools/mix_music.py" captions/captioned.mp4 audio/bed.wav -o final.mp4 --bed-lufs -26 --voice-fx enhance --tp -1.5
"$PY" "$ROOT/tools/check_sync.py" edit/edl.json final.mp4 | tail -1
ffprobe -v error -show_entries stream=codec_type,width,height,duration,nb_frames -of compact final.mp4
ffmpeg -nostdin -hide_banner -i final.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
