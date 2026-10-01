#!/usr/bin/env bash
# Delivery QA: format, A/V sync per EDL range, loudness/true peak, black (>=0.1s) and frozen (>=1s) frames,
# contact sheet (edit/verify/<name>_sheet.png). usage: qa.sh [final.mp4]
set -euo pipefail
cd "$(dirname "$0")"
F="${1:-final.mp4}"; ROOT="$(cd ../.. && pwd)"
ffprobe -v error -show_entries stream=codec_name,codec_type,width,height,r_frame_rate,nb_frames,duration,bit_rate -of compact "$F"
ls -l "$F" | awk '{printf "size %.1f MB\n", $5/1048576}'
"$ROOT/.venv/bin/python" "$ROOT/tools/check_sync.py" edit/edl.json "$F" | tail -1
ffmpeg -nostdin -hide_banner -i "$F" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|LRA|Peak):"
echo "black (>=0.1s):"; ffmpeg -nostdin -hide_banner -i "$F" -vf blackdetect=d=0.1:pix_th=0.10 -an -f null - 2>&1 | grep -o "black_start.*" || echo "  none"
echo "frozen (>=1s):"; ffmpeg -nostdin -hide_banner -i "$F" -vf freezedetect=n=-60dB:d=1 -an -f null - 2>&1 | grep -o "freeze_start.*\|freeze_duration.*" || echo "  none"
mkdir -p edit/verify
ffmpeg -nostdin -v error -y -i "$F" -vf "fps=1/4,scale=216:-1,tile=9x3" -frames:v 1 "edit/verify/$(basename "$F" .mp4)_sheet.png"
echo "sheet → edit/verify/$(basename "$F" .mp4)_sheet.png"
