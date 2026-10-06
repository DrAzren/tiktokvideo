#!/usr/bin/env bash
# preview-frames.cjs needs frames_bg/f_NNNN.png (NNNN = round(t*fps)); dumping all 3160 frames would
# take ~9 GB, so extract only the sampled ones, then run the preview.   ./preview.sh t1 t2 ...
set -euo pipefail
cd "$(dirname "$0")"
export HYPERFRAMES_ROOT=~/hyperframes PUPPETEER_EXECUTABLE_PATH=~/bin/headless_shell_nosandbox HYPERFRAMES_BROWSER_PATH=~/bin/headless_shell_nosandbox
mkdir -p project/frames_bg
for t in "$@"; do
  fi=$(python3 -c "print(max(1, round($t*30)))")
  out=$(printf 'project/frames_bg/f_%04d.png' "$fi")
  [ -f "$out" ] || ffmpeg -nostdin -loglevel error -y -ss "$(python3 -c "print(($fi-1)/30)")" -i project/source.mp4 -frames:v 1 "$out"
done
node ../../../.claude/skills/embedded-captions/scripts/preview-frames.cjs project "$@" 2>&1 | tail -3
