#!/usr/bin/env bash
# Caption previews without extracting all 3240 bg frames: frames_bg/ = the real graphics frame at each
# requested time, one hard-linked blank elsewhere. usage: preview.sh t1 t2 ...
set -euo pipefail
cd "$(dirname "$0")"
export HYPERFRAMES_ROOT=~/hyperframes PUPPETEER_EXECUTABLE_PATH=$HOME/bin/headless_shell_nosandbox
B=project/frames_bg; rm -rf $B && mkdir $B
for i in $(seq 1 3240); do ln matte/blank.png $B/$(printf "f_%04d.png" $i); done
for t in "$@"; do n=$(python3 -c "print(round($t*30))"); f=$B/$(printf "f_%04d.png" $((n + 1)))
  rm -f $f; ffmpeg -nostdin -v error -y -i ../graphics/output.mp4 -vf "select='eq(n\,$n)'" -frames:v 1 $f; done
node ../../../.claude/skills/embedded-captions/scripts/preview-frames.cjs project "$@" 2>&1 | tail -2
