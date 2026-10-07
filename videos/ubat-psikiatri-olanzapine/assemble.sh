#!/usr/bin/env bash
# Final assembly for "Ubat Psikiatri Olanzapine". Template: videos/ward-psikiatri/assemble.sh.
#
#   graphics/output.mp4          cut + punch-ins + graphic cards + full-screen B-roll / MG inserts
#   captions/bg_plus_caps.mp4    ^ + every caption (normal blend, stroke/shadow intact), incl. the
#                                "OLANZAPINE" hero drawn BEHIND the subject
#   captions/project/frames_fg   subject matte — real only for the hero window (frames 1-111 of the cut),
#                                transparent elsewhere (overlay = no-op there)
#   captions/fg_alpha.webm       front captions with real alpha, first 4s only — needed only inside the
#                                matte window (0-3.65s), where the matte would otherwise cover the
#                                kicker/tail lines that touch the subject, so it is enabled just there.
#   audio/bed.wav                original ambient bed (tools/ambient_bed.py)
#   audio/sfx.wav                transition SFX (audio/make_sfx.py), mixed after the ducking
#   → final.mp4 (-14 LUFS / -1 dBTP) and final_tiktok.mp4 (two-pass 1080p, < 30 MB, for download)
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../.. && pwd)"
PY="$ROOT/.venv/bin/python"

ffmpeg -nostdin -y -loglevel error \
  -i captions/bg_plus_caps.mp4 \
  -framerate 30 -i captions/project/frames_fg/f_%04d.png \
  -c:v libvpx-vp9 -i captions/fg_alpha.webm \
  -i graphics/output.mp4 \
  -filter_complex "[1:v]format=yuva420p[m];[0:v][m]overlay=format=auto[a];[2:v]format=yuva420p[c];[a][c]overlay=format=auto:eof_action=pass:enable='between(t,0,3.65)',format=yuv420p[v]" \
  -map "[v]" -map 3:a -r 30 -c:v libx264 -crf 14 -preset medium -g 30 -c:a copy \
  -movflags +faststart captions/captioned.mp4
echo "captioned → captions/captioned.mp4"

"$PY" audio/make_sfx.py captions/captioned.mp4 -o audio/sfx.wav
"$PY" "$ROOT/tools/mix_music.py" captions/captioned.mp4 audio/bed.wav -o final.mp4 --bed-lufs -20 --sfx audio/sfx.wav
"$PY" "$ROOT/tools/check_sync.py" edit/edl.json final.mp4 | tail -1
ffprobe -v error -show_entries stream=codec_type,width,height,duration,nb_frames -of compact final.mp4
ffmpeg -nostdin -hide_banner -i final.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"

# download copy < 30 MB: two-pass x264 at a bitrate that fits, audio copied (already mastered)
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 final.mp4)
VB=$(awk "BEGIN{printf \"%d\", (27.5*8*1024/$DUR) - 192}")
ffmpeg -nostdin -y -loglevel error -i final.mp4 -c:v libx264 -preset slow -b:v ${VB}k -pass 1 -passlogfile /tmp/x264_olz -an -f null /dev/null
ffmpeg -nostdin -y -loglevel error -i final.mp4 -c:v libx264 -preset slow -b:v ${VB}k -pass 2 -passlogfile /tmp/x264_olz -c:a copy -movflags +faststart final_tiktok.mp4
ls -la final.mp4 final_tiktok.mp4
