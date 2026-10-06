#!/usr/bin/env bash
# Rebuild every stage after an EDL change: cut → words → graphics → captions → assembly.
# Graphics and captions are phrase-anchored, so they re-time themselves; the hero-window matte is
# reused unless REMATTE=1 (only needed if the cut changes before ~9.5s). FROM=graphics|captions resumes.
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../.. && pwd)"; PY="$ROOT/.venv/bin/python"
export HYPERFRAMES_ROOT=~/hyperframes HYPERFRAMES_BROWSER_PATH=~/bin/headless_shell_nosandbox PUPPETEER_EXECUTABLE_PATH=~/bin/headless_shell_nosandbox
CLI=~/hyperframes/packages/cli/dist/cli.js
FROM=${FROM:-cut}
if [ "$FROM" = cut ]; then
echo "== cut";      "$PY" edit/build_edl.py && "$PY" "$ROOT/tools/render_edl.py" edit/edl.json -o edit/cut.mp4 | tail -1
"$PY" "$ROOT/tools/check_sync.py" edit/edl.json edit/cut.mp4 | tail -1
"$PY" edit/map_words.py > edit/map_words.log && head -1 edit/map_words.log
fi
if [ "$FROM" = cut ] || [ "$FROM" = graphics ]; then
echo "== graphics"
"$PY" - <<'PY'
import json, subprocess
n = int(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                                 "stream=nb_read_packets", "-of", "csv=p=0", "edit/cut.mp4"]).decode())
json.dump({"duration": round(n / 30, 4), "width": 1080, "height": 1920, "fps": 30}, open("graphics/metadata.json", "w"))
print("duration", round(n / 30, 4))
PY
(cd graphics && "$PY" build_graphics.py > build.log && head -1 build.log && node measure_pages.cjs > /dev/null && "$PY" build_graphics.py > build.log)
node $CLI render graphics/public --skill=talking-head-recut --fps 30 -o "$PWD/graphics/output.mp4" > graphics/render.log 2>&1
"$PY" "$ROOT/tools/check_sync.py" edit/edl.json graphics/output.mp4 | tail -1
fi
echo "== captions"
captions/matte_window.sh | tail -2
captions/build.sh | tail -4
node $CLI render captions/project --skill=embedded-captions --fps 30 -o "$PWD/captions/bg_plus_caps.mp4" > captions/bg_render.log 2>&1
captions/make_fg_alpha.sh | tail -1
echo "== assemble"
./assemble.sh
