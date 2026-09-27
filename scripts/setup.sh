#!/usr/bin/env bash
# One-time (or per-container) setup for the editing studio.
# Installs ffmpeg, Python deps for video-use helpers, and warms the hyperframes CLI.
#   scripts/setup.sh              core pipeline (cut, graphics)
#   scripts/setup.sh --captions   + CPU torch/torchaudio (MMS forced alignment) and a built
#                                 hyperframes checkout at ~/hyperframes (embedded-captions needs it)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CAPTIONS=0; [ "${1:-}" = "--captions" ] && CAPTIONS=1

if ! command -v ffmpeg >/dev/null; then
  if command -v brew >/dev/null; then brew install ffmpeg
  elif command -v apt-get >/dev/null; then
    SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
    $SUDO apt-get update -qq && $SUDO apt-get install -y -qq ffmpeg
  else
    echo "Install ffmpeg manually: https://ffmpeg.org/download.html" >&2; exit 1
  fi
fi

cd "$ROOT"
if command -v uv >/dev/null; then
  uv venv -q .venv 2>/dev/null || true
  uv pip install -q --python .venv/bin/python -r requirements.txt
else
  python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt
fi

if [ "$CAPTIONS" = 1 ]; then
  uv pip install -q --python .venv/bin/python torch torchaudio --index-url https://download.pytorch.org/whl/cpu
  if [ ! -f ~/hyperframes/packages/cli/dist/cli.js ]; then
    command -v bun >/dev/null || { echo "bun is required to build hyperframes (https://bun.sh)" >&2; exit 1; }
    [ -d ~/hyperframes ] || git clone --depth 1 https://github.com/heygen-com/hyperframes ~/hyperframes
    (cd ~/hyperframes && PUPPETEER_SKIP_DOWNLOAD=1 bun install && bun run build)
  fi
  echo "hyperframes checkout OK: export HYPERFRAMES_ROOT=~/hyperframes"
  # root in the cloud container: Chromium needs --no-sandbox (caption scripts launch puppeteer)
  HS="$(ls -d /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell 2>/dev/null | head -1)"
  if [ -n "$HS" ]; then
    mkdir -p ~/bin
    printf '#!/bin/sh\nexec %s --no-sandbox "$@"\n' "$HS" > ~/bin/headless_shell_nosandbox
    chmod +x ~/bin/headless_shell_nosandbox
    echo "export PUPPETEER_EXECUTABLE_PATH=~/bin/headless_shell_nosandbox HYPERFRAMES_BROWSER_PATH=$HS"
  fi
fi

node_major="$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)"
if [ "$node_major" -lt 22 ]; then
  echo "WARNING: HyperFrames needs Node.js 22+ (found: $(node -v 2>/dev/null || echo none))" >&2
else
  npx --yes hyperframes --version >/dev/null && echo "hyperframes CLI OK"
fi

[ -f .env ] || cp .env.example .env
ffprobe -version | head -1
.venv/bin/python .claude/skills/video-use/helpers/timeline_view.py --help >/dev/null && echo "video-use helpers OK"
grep -q '^ELEVENLABS_API_KEY=..' .env || [ -n "${ELEVENLABS_API_KEY:-}" ] \
  || echo "NOTE: no ELEVENLABS_API_KEY yet — add it to .env for best filler-word detection (Whisper fallback works without it)."
