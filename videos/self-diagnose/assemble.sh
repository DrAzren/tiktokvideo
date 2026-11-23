#!/usr/bin/env bash
# Final assembly for "Self Diagnose".
#   graphics/output.mp4     HyperFrames render: cut + cards + B-roll + motion graphics + captions (silent)
#   edit/voice_clean.wav    tools/enhance_speech.py on edit/cut.mp4
#   audio/sfx.wav           audio/make_sfx.py (synthesized cues from graphics/sfx_events.json)
#   audio/bed.wav           tools/ambient_bed.py (original, licence-free)
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../.. && pwd)"; PY="$ROOT/.venv/bin/python"

ffmpeg -nostdin -y -loglevel error -i edit/voice_clean.wav -i audio/sfx.wav -filter_complex \
  "[0:a]aresample=48000,aformat=channel_layouts=stereo[v];[1:a]volume=-9dB[s];[v][s]amix=inputs=2:normalize=0[a]" \
  -map "[a]" -c:a pcm_s16le audio/voice_sfx.wav
ffmpeg -nostdin -y -loglevel error -i graphics/output.mp4 -i audio/voice_sfx.wav -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 256k -movflags +faststart audio/premix.mp4
"$PY" "$ROOT/tools/mix_music.py" audio/premix.mp4 audio/bed.wav -o final.mp4 --bed-lufs -16
ffprobe -v error -show_entries stream=codec_type,codec_name,width,height,r_frame_rate,duration,nb_frames -of compact final.mp4
ffmpeg -nostdin -hide_banner -i final.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
