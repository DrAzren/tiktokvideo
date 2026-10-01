#!/usr/bin/env bash
# Front-caption layer with REAL alpha (first 9s = covers the hero matte window 5.40-7.93s) → fg_alpha.webm.
# Copies project/index_fg.html, removes the a-roll <video>/<audio> (HyperFrames composites media
# itself, so CSS-hiding them still yields an opaque frame) and makes every background transparent.
set -euo pipefail
cd "$(dirname "$0")"
rm -rf _fg_alpha fg_alpha.webm && mkdir _fg_alpha
for p in project/*; do b=$(basename "$p"); case "$b" in index.html|index_fg.html|history|_*|preview|frames_fg|frames_bg|source.mp4) continue;; esac; ln -sf "$PWD/$p" "_fg_alpha/$b"; done
../../../.venv/bin/python - <<'EOF'
import re
s = open("project/index_fg.html").read()
s, nv = re.subn(r'<video\s+id="a-roll".*?</video>', '', s, flags=re.S)
s, na = re.subn(r'<audio\s+id="a-roll-audio".*?</audio>', '', s, flags=re.S)
s = s.replace("html.fg-only body { background: #000 !important; }", "html.fg-only body, html.fg-only { background: transparent !important; }")
s = s.replace("html.fg-only #fg-cover { position: absolute; inset: 0; background: #000; z-index: 1; pointer-events: none; }", "html.fg-only #fg-cover { display: none; }")
s = re.sub(r"(html, body \{[^}]*?)background: #000;", r"\1background: transparent;", s, count=1)
dur = re.search(r'data-duration="([\d.]+)"', s).group(1)
s = s.replace(f'data-duration="{dur}"', 'data-duration="9"')
open("_fg_alpha/index.html", "w").write(s)
assert nv == 1 and na == 1, (nv, na)
print("removed video:", nv, "audio:", na, "| black bg left:", s.count("background: #000"), "| duration", dur, "→ 9")
EOF
export HYPERFRAMES_ROOT=~/hyperframes HYPERFRAMES_BROWSER_PATH=$HOME/bin/headless_shell_nosandbox PUPPETEER_EXECUTABLE_PATH=$HOME/bin/headless_shell_nosandbox
node ~/hyperframes/packages/cli/dist/cli.js render _fg_alpha --skill=embedded-captions --fps 30 --format webm -o "$PWD/fg_alpha.webm" > fg_render.log 2>&1
ffmpeg -nostdin -loglevel error -y -c:v libvpx-vp9 -ss 6.5 -i fg_alpha.webm -frames:v 1 -pix_fmt rgba _fga.png
../../../.venv/bin/python -c "
from PIL import Image; import numpy as np; a=np.asarray(Image.open('_fga.png'))[...,3]; print('fg_alpha @6.5s transparent', round(float((a<5).mean()),4))"
