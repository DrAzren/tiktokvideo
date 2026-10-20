#!/usr/bin/env bash
# 9:16 TikTok version: blurred backdrop + the 16:9 film as a band + captions.ass (header, chapters, captions).
# Usage: tiktok/compose.sh <16:9 render without subtitles> <mix.wav> <out.mp4> [extra ffmpeg input/output args]
set -euo pipefail
cd "$(dirname "$0")"
IN=$1; AUD=$2; OUT=$3; shift 3
FG="[0:v]split[a][b];
[a]scale=-2:640,crop=360:640,boxblur=14:2,scale=1080:1920,eq=brightness=-0.16:saturation=0.8[bg];
[b]scale=1080:608:flags=lanczos[fg];
[bg][fg]overlay=0:470,drawbox=x=0:y=468:w=1080:h=2:color=0xD9A441@0.85:t=fill,drawbox=x=0:y=1078:w=1080:h=2:color=0xD9A441@0.85:t=fill,
ass=captions.ass:fontsdir=fonts[v]"
ffmpeg -nostdin -loglevel error -y "$@" -i "$IN" -i "$AUD" -filter_complex "$FG" -map "[v]" -map 1:a \
  -c:v libx264 -preset medium -crf 20 -maxrate 7M -bufsize 14M -pix_fmt yuv420p -r 24 \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest "$OUT"
