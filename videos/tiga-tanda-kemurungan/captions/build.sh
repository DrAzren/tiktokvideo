#!/usr/bin/env bash
# Caption chain, in order and exactly once (patch_apex.py is not idempotent):
#   transcript → cinematic.json → make-cinematic → patch_apex → make-composition → inject-fonts → gates
set -euo pipefail
cd "$(dirname "$0")"
PY=../../../.venv/bin/python
S=../../../.claude/skills/embedded-captions/scripts
export HYPERFRAMES_ROOT=~/hyperframes PUPPETEER_EXECUTABLE_PATH=~/bin/headless_shell_nosandbox HYPERFRAMES_BROWSER_PATH=~/bin/headless_shell_nosandbox
$PY build_transcript.py > project/_transcript.log && head -1 project/_transcript.log
$PY author_captions.py > project/_author.log && head -1 project/_author.log
node $S/make-cinematic.cjs project > project/_make_cinematic.log 2>&1
grep -v "visible only" project/_make_cinematic.log | tail -4
echo "short lines (< 0.6s page-flip): $(grep -c 'visible only' project/_make_cinematic.log || true)"
$PY patch_apex.py > project/_patch.log && head -2 project/_patch.log
node $S/make-composition.cjs project 2>&1 | tail -1
node $S/inject-fonts.cjs project | tail -1
node $S/check-timing.cjs project --strict 2>&1 | tail -3
node $S/check-occlusion.cjs project --strict 2>&1 | tail -3
