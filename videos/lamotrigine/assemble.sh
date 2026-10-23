#!/usr/bin/env bash
# Final assembly for "Ubat Psikiatri Lamotrigine".
#
#   graphics/output.mp4      cut + camera moves + B-roll slots / motion graphics + cards + title + captions
#   graphics/output_clean.mp4  the same without captions (optional; built with build_graphics.py --clean)
#   edit/voice.wav           enhanced voice (tools/enhance_speech.py on edit/cut.mp4)
#   audio/voice_sfx.wav      ^ + synthesized SFX at graphics/sfx_cues.json (audio/sfx_mix.py)
#   audio/bed.wav            original F-major ambient bed (tools/ambient_bed.py) -> tools/mix_music.py
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../.. && pwd)"
PY="$ROOT/.venv/bin/python"

"$PY" audio/sfx_mix.py edit/voice.wav graphics/sfx_cues.json -o audio/voice_sfx.wav
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 graphics/output.mp4)
"$PY" "$ROOT/tools/ambient_bed.py" -o audio/bed.wav --duration "$DUR" --key F --bpm 72 --seed 5

for v in "" _clean; do
  src="graphics/output$v.mp4"
  [ -f "$src" ] || continue
  ffmpeg -nostdin -y -loglevel error -i "$src" -i audio/voice_sfx.wav -map 0:v -map 1:a \
    -c:v copy -c:a aac -b:a 256k -ar 48000 -movflags +faststart "audio/premix$v.mp4"
  "$PY" "$ROOT/tools/mix_music.py" "audio/premix$v.mp4" audio/bed.wav -o "final$v.mp4" --bed-lufs -22
  echo "== final$v.mp4"
  "$PY" "$ROOT/tools/check_sync.py" edit/edl.json "final$v.mp4" | tail -1
  ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration -of compact "final$v.mp4"
  ffmpeg -nostdin -hide_banner -i "final$v.mp4" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
done
