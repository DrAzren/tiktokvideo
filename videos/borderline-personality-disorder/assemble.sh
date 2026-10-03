#!/usr/bin/env bash
# Final assembly for "Borderline Personality Disorder" (template: videos/ward-psikiatri/assemble.sh).
#
#   graphics/output.mp4          cut + punch-ins + headroom cards + full-screen B-roll / MG inserts
#   captions/bg_plus_caps.mp4    ^ + every caption (normal blend, stroke/shadow intact) + the "BPD"
#                                hero drawn BEHIND the subject
#   captions/project/frames_fg   subject matte — real only for the hero window (frames 238-328 =
#                                7.9-10.95s), transparent elsewhere (overlay = no-op there)
#   captions/fg_alpha.webm       front captions with real alpha, first 11s only; enabled just inside
#                                the matte window, where the matte would otherwise cover captions
#   audio/bed.wav                original ambient bed (tools/ambient_bed.py)
#   audio/voice_af.txt           dialogue chain: rumble high-pass, 1761 Hz whine notch, presence EQ,
#                                gentle compression (no FFT denoise: it delays the voice 25 ms)
#
# Outputs: final.mp4 (master, CRF 14) and final_tiktok_1080p.mp4 (< 30 MB, for upload/download).
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd ../.. && pwd)"
PY="$ROOT/.venv/bin/python"
HERO_T0=7.9; HERO_T1=10.95             # = graphics/inserts.py HERO

ffmpeg -nostdin -y -loglevel error \
  -i captions/bg_plus_caps.mp4 \
  -framerate 30 -i captions/project/frames_fg/f_%04d.png \
  -c:v libvpx-vp9 -i captions/fg_alpha.webm \
  -i graphics/output.mp4 \
  -filter_complex "[1:v]format=yuva420p[m];[0:v][m]overlay=format=auto[a];[2:v]format=yuva420p[c];[a][c]overlay=format=auto:eof_action=pass:enable='between(t,$HERO_T0,$HERO_T1)',format=yuv420p[v]" \
  -map "[v]" -map 3:a -r 30 -c:v libx264 -crf 14 -preset medium -g 30 -c:a copy \
  -movflags +faststart captions/captioned.mp4
echo "captioned → captions/captioned.mp4"

"$PY" "$ROOT/tools/mix_music.py" captions/captioned.mp4 audio/bed.wav -o final.mp4 --bed-lufs -17 \
  --voice-af "$(cat audio/voice_af.txt)"

# delivery copy under 30 MB: two-pass x264 at a bitrate computed from the duration
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 final.mp4)
VK=$(python3 -c "print(int((29.0*8*1024) / $DUR - 160))")        # kbit/s for video, 160k audio, ~1 MB margin
ffmpeg -nostdin -y -loglevel error -i final.mp4 -c:v libx264 -preset slow -b:v ${VK}k -pass 1 \
  -passlogfile /tmp/bpd_x264 -an -f null /dev/null
ffmpeg -nostdin -y -loglevel error -i final.mp4 -c:v libx264 -preset slow -b:v ${VK}k -pass 2 \
  -passlogfile /tmp/bpd_x264 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart final_tiktok_1080p.mp4
echo "delivery: final_tiktok_1080p.mp4 @ ${VK}k video"

# checks. Sync: the EDL check runs on the pre-music file (with the bed underneath, its 0.27s snippet on
# one-word ranges like "walaupun" can lock onto a false peak: -344ms reported, +4ms real). The mix stage
# is then checked against that file in 1s windows (voice chain = +4ms phase).
"$PY" "$ROOT/tools/check_sync.py" edit/edl.json captions/captioned.mp4 | tail -1
for f in final.mp4 final_tiktok_1080p.mp4; do
  ffmpeg -nostdin -v error -y -i captions/captioned.mp4 -vn -ac 1 -ar 16000 /tmp/_pre.wav
  ffmpeg -nostdin -v error -y -i "$f" -vn -ac 1 -ar 16000 /tmp/_out.wav
  "$PY" - "$f" <<'EOF2'
import sys, numpy as np, soundfile as sf
a, sr = sf.read("/tmp/_pre.wav"); b, _ = sf.read("/tmp/_out.wav")
lags = []
for t in np.arange(0.5, len(a) / sr - 2, 1.0):
    x = a[int(t * sr):int((t + 1) * sr)]
    if np.sqrt((x ** 2).mean()) < 0.01:
        continue
    lo = int((t - 0.4) * sr); y = b[lo:int((t + 1.4) * sr)]
    lags.append(((np.argmax(np.correlate(y, x, "valid")) + lo) / sr - t) * 1000)
lags = np.array(lags)
print(f"{sys.argv[1]} vs pre-mix: {len(lags)} windows, median {np.median(lags):+.1f} ms, worst {np.abs(lags).max():.1f} ms")
sys.exit(1 if np.abs(lags).max() > 25 else 0)
EOF2
done
for f in final.mp4 final_tiktok_1080p.mp4; do
  echo "== $f  $(du -m $f | cut -f1) MB"
  ffprobe -v error -show_entries stream=codec_type,width,height,r_frame_rate,duration,nb_frames -of compact "$f"
  ffmpeg -nostdin -hide_banner -i "$f" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
done
echo "== black frames (>0.1s):"
ffmpeg -nostdin -hide_banner -i final.mp4 -vf blackdetect=d=0.1:pix_th=0.08 -an -f null - 2>&1 | grep -o "black_start.*" || echo "   none"
echo "== frozen stretches (>1.5s):"
ffmpeg -nostdin -hide_banner -i final.mp4 -vf freezedetect=n=0.002:d=1.5 -an -f null - 2>&1 | grep -oE "freeze_(start|end|duration): [0-9.]+" | paste - - - || echo "   none"
