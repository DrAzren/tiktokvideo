#!/usr/bin/env bash
# Final assembly for "Tiga Tanda Kemurungan Yang Anda Tak Perasan".
# Template: videos/ward-psikiatri/assemble.sh.
#
#   graphics/output.mp4          cut + punch-ins + headroom cards + full-screen B-roll / MG inserts
#   captions/bg_plus_caps.mp4    ^ + every caption drawn with normal blending (stroke/shadow intact),
#                                incl. the "KEMURUNGAN" hero
#   captions/project/frames_fg   subject matte — real only for the hero window (frames 178-286,
#                                5.9-9.5s; captions/matte_window.sh), transparent elsewhere
#   captions/fg_alpha.webm       front captions with real alpha, first 10s only; enabled just inside the
#                                matte window so the kicker/tail lines stay in front of the subject
#   audio/bed.wav                original ambient bed (tools/ambient_bed.py, key F, 60 bpm)
#                                → tools/mix_music.py (EQ'd out of the voice band, sidechain-ducked, -14 LUFS)
#   final.mp4                    master, 1080x1920 @ 30
#   final_tiktok.mp4             two-pass 1080p encode under 30 MB for download / upload
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../.. && pwd)"
PY="$ROOT/.venv/bin/python"
W0=5.9; W1=9.5   # matte window (keep in sync with captions/matte_window.sh and graphics HERO_WINDOW)

ffmpeg -nostdin -y -loglevel error \
  -i captions/bg_plus_caps.mp4 \
  -framerate 30 -i captions/project/frames_fg/f_%04d.png \
  -c:v libvpx-vp9 -i captions/fg_alpha.webm \
  -i graphics/output.mp4 \
  -filter_complex "[1:v]format=yuva420p[m];[0:v][m]overlay=format=auto[a];[2:v]format=yuva420p[c];[a][c]overlay=format=auto:eof_action=pass:enable='between(t,$W0,$W1)',format=yuv420p[v]" \
  -map "[v]" -map 3:a -r 30 -c:v libx264 -crf 14 -preset medium -g 30 -c:a copy \
  -movflags +faststart captions/captioned.mp4
echo "captioned → captions/captioned.mp4"

"$PY" "$ROOT/tools/mix_music.py" captions/captioned.mp4 audio/bed.wav -o final.mp4 --bed-lufs -20
"$PY" "$ROOT/tools/check_sync.py" edit/edl.json final.mp4 | tail -1
ffprobe -v error -show_entries stream=codec_type,width,height,duration,nb_frames -of compact final.mp4
ffmpeg -nostdin -hide_banner -i final.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"

# download copy < 30 MB: two-pass x264 at a bitrate that fits 28 MB including 160k audio
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 final.mp4)
VB=$("$PY" -c "print(int((28 * 8 * 1024 * 1024 / $DUR - 160_000) / 1000))")
ffmpeg -nostdin -y -loglevel error -i final.mp4 -c:v libx264 -preset slow -b:v ${VB}k -pass 1 -passlogfile /tmp/tt2pass -an -f mp4 /dev/null
ffmpeg -nostdin -y -loglevel error -i final.mp4 -c:v libx264 -preset slow -b:v ${VB}k -pass 2 -passlogfile /tmp/tt2pass \
  -pix_fmt yuv420p -g 60 -c:a aac -b:a 160k -movflags +faststart final_tiktok.mp4
ls -la final.mp4 final_tiktok.mp4
