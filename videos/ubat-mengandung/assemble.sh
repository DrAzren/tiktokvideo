#!/usr/bin/env bash
# Final assembly for "10 Ubat Psikiatri Dilarang Untuk Mengandung".
#
#   graphics/output.mp4          cut + grade + punch-ins + cards + full-screen MG / AI B-roll inserts (voice)
#   captions/bg_plus_caps.mp4    ^ + every caption, incl. the "10 UBAT" hero (normal blend, strokes intact)
#   captions/_matte_hero/frames_fg  subject matte for the hero window only (frames 1-72 = 0-2.4 s):
#                                overlaid there so the hero reads as BEHIND the head
#   captions/fg_alpha.webm       front captions with real alpha, 0-2.4 s (the matte would otherwise cover
#                                the chest caption line that sits on the subject)
#   audio/bed.wav                original ambient bed (tools/ambient_bed.py) → ducked under the voice
#   audio/sfx_track.wav          synthesized SFX placed on the graphics' own cue times (audio/build_sfx.py)
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../.. && pwd)"
PY="$ROOT/.venv/bin/python"
N=$(ffprobe -v error -count_packets -select_streams v:0 -show_entries stream=nb_read_packets -of csv=p=0 graphics/output.mp4)

ffmpeg -nostdin -y -loglevel error \
  -i captions/bg_plus_caps.mp4 \
  -framerate 30 -i captions/_matte_hero/frames_fg/f_%04d.png \
  -c:v libvpx-vp9 -i captions/fg_alpha.webm \
  -i graphics/output.mp4 \
  -filter_complex "[1:v]format=yuva420p[m];[0:v][m]overlay=format=auto:eof_action=pass:enable='lt(t,2.4)'[a];[2:v]format=yuva420p[c];[a][c]overlay=format=auto:eof_action=pass:enable='lt(t,2.4)',format=yuv420p[v]" \
  -map "[v]" -map 3:a -frames:v "$N" -r 30 -c:v libx264 -crf 14 -preset medium -g 30 -c:a copy \
  -movflags +faststart captions/captioned.mp4
echo "captioned → captions/captioned.mp4 ($N frames)"

"$PY" audio/build_sfx.py
"$PY" "$ROOT/tools/mix_music.py" captions/captioned.mp4 audio/bed.wav --sfx audio/sfx_track.wav -o final.mp4 --bed-lufs -20
"$PY" "$ROOT/tools/check_sync.py" edit/edl.json final.mp4 | tail -1
ffprobe -v error -show_entries stream=codec_type,width,height,duration,nb_frames -of compact final.mp4
ffmpeg -nostdin -hide_banner -i final.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
