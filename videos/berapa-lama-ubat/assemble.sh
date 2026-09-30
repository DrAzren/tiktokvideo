#!/usr/bin/env bash
# Final assembly for "Berapa Lama Makan Ubat Psikiatri" (template: videos/ward-psikiatri/assemble.sh).
#
#   graphics/output.mp4          cut + punch-ins + headroom cards + full-screen B-roll / MG inserts
#   captions/bg_plus_caps.mp4    ^ + every caption (normal blend), incl. the "BERGANTUNG" hero
#   captions/project/frames_fg   subject matte — real only for the hero window (frames 181-270 of
#                                the cut = 6.0-9.0s), transparent elsewhere (overlay = no-op there)
#   captions/fg_alpha.webm       front captions with real alpha, first 9.2s only; enabled just inside
#                                the matte window, where the matte would otherwise cover them
#   audio/bed.wav                original ambient bed (tools/ambient_bed.py) → tools/mix_music.py
#   final.mp4                    master (CRF 14);  final_tiktok.mp4  the <30 MB delivery file
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../.. && pwd)"
PY="$ROOT/.venv/bin/python"

ffmpeg -nostdin -y -loglevel error \
  -i captions/bg_plus_caps.mp4 \
  -framerate 30 -i captions/project/frames_fg/f_%04d.png \
  -c:v libvpx-vp9 -i captions/fg_alpha.webm \
  -i graphics/output.mp4 \
  -filter_complex "[1:v]format=yuva420p[m];[0:v][m]overlay=format=auto[a];[2:v]format=yuva420p[c];[a][c]overlay=format=auto:eof_action=pass:enable='between(t,6.0,9.0)',format=yuv420p[v]" \
  -map "[v]" -map 3:a -r 30 -c:v libx264 -crf 14 -preset medium -g 30 -c:a copy \
  -movflags +faststart captions/captioned.mp4
echo "captioned → captions/captioned.mp4"

"$PY" "$ROOT/tools/mix_music.py" captions/captioned.mp4 audio/bed.wav -o final.mp4 --bed-lufs -20
"$PY" "$ROOT/tools/check_sync.py" edit/edl.json final.mp4 | tail -1
ffprobe -v error -show_entries stream=codec_type,width,height,duration,nb_frames -of compact final.mp4
ffmpeg -nostdin -hide_banner -i final.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"

# delivery: 1080x1920, two-pass to ~27 MB (TikTok re-encodes anyway; audio copied from the master)
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 final.mp4)
VBR=$("$PY" -c "print(int((27*8*1024*1024/$DUR - 192000)/1000))")
ffmpeg -nostdin -y -loglevel error -i final.mp4 -c:v libx264 -preset slow -b:v ${VBR}k -pass 1 -passlogfile _x264 -an -f null /dev/null
ffmpeg -nostdin -y -loglevel error -i final.mp4 -c:v libx264 -preset slow -b:v ${VBR}k -maxrate $((VBR*2))k -bufsize $((VBR*2))k \
  -pass 2 -passlogfile _x264 -pix_fmt yuv420p -c:a copy -movflags +faststart final_tiktok.mp4
rm -f _x264*
ls -la final_tiktok.mp4
