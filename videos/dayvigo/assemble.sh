#!/usr/bin/env bash
# Final assembly for "Ubat Psikiatri Dayvigo".
#
#   graphics/output.mp4        HyperFrames render: cut talking head + cards + B-roll/MG inserts + captions
#                              (picture only), with the INSOMNIA hero drawn above the video
#   captions/hero_matte.mov    subject cut-out (remove-background, ProRes 4444) for the hero window only:
#                              laid back over the render so the hero sits BEHIND the head. Nothing else
#                              in front touches the subject in that window (no caption there; the kicker
#                              card is in the headroom), so no front-layer re-composite is needed.
#   audio/mix.wav              voice + ducked music bed + sound design, mastered -14 LUFS / -1 dBTP
#
# Outputs: final.mp4 (TikTok master, H.264 High CRF 17, AAC 192k) and final_share.mp4 (< 30 MB, 2-pass).
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../.. && pwd)"
PY="$ROOT/.venv/bin/python"

read -r H0 H1 < <("$PY" -c "import json;h=json.load(open('graphics/storyboard.json'))['hero'];print(round(h['start']*30), round(h['end']*30))")
T0=$(echo "scale=6; $H0/30" | bc); T1=$(echo "scale=6; $H1/30 - 0.001" | bc)

ffmpeg -nostdin -y -loglevel error \
  -i graphics/output.mp4 -i captions/hero_matte.mov -i audio/mix.wav \
  -filter_complex "[1:v]setpts=PTS+${T0}/TB,format=yuva444p[m];[0:v][m]overlay=format=auto:eof_action=pass:enable='between(t,${T0},${T1})',format=yuv420p[v]" \
  -map "[v]" -map 2:a -r 30 -c:v libx264 -profile:v high -crf 17 -preset slow -g 60 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart final.mp4
# (-shortest is safe here: mix.wav is exactly the cut's length and the picture carries the tail hold)

# shareable copy under 30 MB (the chat can send at most 30 MB); looks the same after TikTok re-compresses
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 final.mp4)
VB=$("$PY" -c "print(int((29.0*8*1024*1024/ $DUR - 160000) * 0.97))")
ffmpeg -nostdin -y -loglevel error -i final.mp4 -c:v libx264 -preset slow -b:v "$VB" -pass 1 -passlogfile /tmp/dayvigo2p -an -f null /dev/null
ffmpeg -nostdin -y -loglevel error -i final.mp4 -c:v libx264 -preset slow -b:v "$VB" -pass 2 -passlogfile /tmp/dayvigo2p \
  -c:a aac -b:a 160k -movflags +faststart final_share.mp4

ffprobe -v error -show_entries stream=codec_name,profile,width,height,r_frame_rate,duration,nb_frames:format=size -of compact final.mp4
ls -la final.mp4 final_share.mp4
ffmpeg -nostdin -hide_banner -i final.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|LRA|Peak):"
