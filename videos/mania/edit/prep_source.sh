#!/usr/bin/env bash
# Working source for the cut: raw/MANIA.mp4 is a 720x1280 CapCut camera recording (VN 'vicut' export,
# original_volume 500 -> ~1.3% of samples at/over full scale).
#   video: CFR 30, lanczos upscale to 1080x1920 + light luma unsharp, intra-heavy GOP for exact seeks
#   audio: mono (L/R identical), adeclip, -3.5 dB headroom, PCM 48k
set -euo pipefail
cd "$(dirname "$0")"
ffmpeg -nostdin -y -loglevel error -i ../raw/MANIA.mp4 \
  -vf "fps=30,scale=1080:1920:flags=lanczos,unsharp=5:5:0.4:5:5:0,format=yuv420p" \
  -c:v libx264 -crf 12 -preset medium -g 15 -bf 0 \
  -af "pan=mono|c0=c0,aresample=48000,adeclip,volume=-3.5dB" -c:a pcm_s16le \
  source_1080_dc.mov
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames,duration,sample_rate,channels -of compact source_1080_dc.mov
