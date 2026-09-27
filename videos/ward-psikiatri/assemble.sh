#!/usr/bin/env bash
# Final assembly for "Keadaan Dalam Wad Psikiatri".
#
#   graphics/output.mp4          cut + punch-ins + graphic cards (talking-head-recut)
#   captions/bg_plus_caps.mp4    ^ + the "TIDAK" hero caption drawn BEHIND the subject
#   captions/project/frames_fg   subject matte — real only for the hero window (frames
#                                211-435), transparent elsewhere (overlay = no-op there)
#   captions/fg_alpha.webm       front captions with real alpha, first 11s only. The bg layer
#                                already carries every caption (normal blend, stroke/shadow
#                                intact); the front copy is needed only inside the matte window
#                                (7.9-10.95s), where the matte would otherwise cover captions
#                                that touch the subject — so it is enabled just there.
#   audio/bed.wav                original ambient bed → tools/mix_music.py (ducked, -14 LUFS)
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../.. && pwd)"
PY="$ROOT/.venv/bin/python"

ffmpeg -nostdin -y -loglevel error \
  -i captions/bg_plus_caps.mp4 \
  -framerate 30 -i captions/project/frames_fg/f_%04d.png \
  -c:v libvpx-vp9 -i captions/fg_alpha.webm \
  -i graphics/output.mp4 \
  -filter_complex "[1:v]format=yuva420p[m];[0:v][m]overlay=format=auto[a];[2:v]format=yuva420p[c];[a][c]overlay=format=auto:eof_action=pass:enable='between(t,7.9,10.95)',format=yuv420p[v]" \
  -map "[v]" -map 3:a -r 30 -c:v libx264 -crf 14 -preset medium -g 30 -c:a copy \
  -movflags +faststart captions/captioned.mp4
echo "captioned → captions/captioned.mp4"

"$PY" "$ROOT/tools/mix_music.py" captions/captioned.mp4 audio/bed.wav -o final.mp4 --bed-lufs -20
"$PY" "$ROOT/tools/check_sync.py" edit/edl.json final.mp4 | tail -1
ffprobe -v error -show_entries stream=codec_type,width,height,duration,nb_frames -of compact final.mp4
ffmpeg -nostdin -hide_banner -i final.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
