#!/usr/bin/env bash
# Caption chain for "Fasa Mania": transcript -> cinematic.json -> compile -> apex patch -> fonts -> gates.
# (make_matte.sh first; then render: bg pass of project/index.html -> bg_plus_caps.mp4, make_fg_alpha.sh, ../assemble.sh)
set -euo pipefail
cd "$(dirname "$0")"
PY=../../../.venv/bin/python; SD=../../../../.claude/skills/embedded-captions/scripts
export HYPERFRAMES_ROOT=~/hyperframes HYPERFRAMES_BROWSER_PATH=$HOME/bin/headless_shell_nosandbox PUPPETEER_EXECUTABLE_PATH=$HOME/bin/headless_shell_nosandbox
$PY build_transcript.py | sed -n 1p
$PY author_captions.py | sed -n 1p
cp transcript.json project/transcript.json
ln -sf ../../graphics/output.mp4 project/source.mp4
(cd project && node $SD/make-cinematic.cjs . 2>&1 | grep -E "hero|canvas|ERROR" || true)
$PY patch_apex.py | sed -n 1p
(cd project && node $SD/make-composition.cjs . 2>&1 | tail -1)
node ../../../.claude/skills/embedded-captions/scripts/inject-fonts.cjs project | tail -2
node ../../../.claude/skills/embedded-captions/scripts/check-timing.cjs project --strict | tail -2
timeout 240 node ../../../.claude/skills/embedded-captions/scripts/check-occlusion.cjs project --strict > project/_occlusion.log 2>&1 || true
grep -E "word-fail|FAIL|PASS|occlu" project/_occlusion.log | tail -6
