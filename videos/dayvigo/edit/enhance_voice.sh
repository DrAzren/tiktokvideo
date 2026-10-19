#!/usr/bin/env bash
# Podcast-style voice chain for the whole continuous source track (run once, before cutting, so every
# segment gets identical treatment). Source is clipped at capture (-6 LUFS, ~37k full-scale samples)
# and very bass-heavy (80-200 Hz ~29 dB above 2.5-5 kHz), noise floor already ~-73 dBFS.
#   declip -> headroom -> rumble HPF -> de-boom / de-mud -> presence + air -> de-ess -> light FFT denoise
#   -> gentle 2.5:1 compression. Loudness is set later (render_edl loudnorm, then the final mix).
# The chain's lookahead delays the voice ~24.7 ms (measured by cross-correlation): atrim removes it, apad
# restores the length. Output: voice_enh.wav (48 kHz mono float) and source_enh.mov (original video stream
# + enhanced audio). MOV, not MKV: MKV's 1 ms timestamps made render_edl's -ss/-t drop a video frame on some
# ranges, slipping audio a frame (33 ms) per affected cut.
set -euo pipefail
cd "$(dirname "$0")"
SRC="../raw/Ubat Psikiatri Dayvigo.mp4"
AF="aformat=sample_fmts=fltp,pan=mono|c0=0.5*c0+0.5*c1,
adeclip=window=55:overlap=75:arorder=8:threshold=10:hsize=1000,
volume=-9dB,
highpass=f=75:poles=2,
equalizer=f=160:t=q:w=1.0:g=-7,
equalizer=f=340:t=q:w=1.3:g=-2,
equalizer=f=3200:t=q:w=1.4:g=4,
equalizer=f=5600:t=q:w=1.6:g=2.5,
highshelf=f=9000:g=3,
deesser=i=0.35:m=0.5:f=0.5,
afftdn=nr=6:nf=-62:tn=1,
acompressor=threshold=-24dB:ratio=2.5:attack=8:release=150:knee=4:makeup=3,
aresample=48000,atrim=start_sample=1186,apad=pad_len=1186"
ffmpeg -nostdin -y -loglevel error -i "$SRC" -vn -af "$(echo "$AF" | tr -d '\n')" -c:a pcm_f32le voice_enh.wav
ffmpeg -nostdin -y -loglevel error -i "$SRC" -i voice_enh.wav -map 0:v -map 1:a -c:v copy -c:a pcm_s24le source_enh.mov
echo "wrote voice_enh.wav, source_enh.mov"
"$(dirname "$0")/../../../.venv/bin/python" - <<'PY'
import numpy as np, soundfile as sf
from scipy.signal import correlate, resample_poly
import subprocess
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", "../raw/Ubat Psikiatri Dayvigo.mp4", "-vn", "-ac", "1",
                "-ar", "48000", "_raw48.wav"], check=True)
a, b = sf.read("_raw48.wav")[0], sf.read("voice_enh.wav")[0]
lags = []
for t in (10, 60, 120):
    x = a[t * 48000:(t + 2) * 48000]
    c = correlate(b[t * 48000 - 4800:(t + 2) * 48000 + 4800], x, mode="valid")
    lags.append((np.argmax(c) - 4800) / 48)
print("voice chain residual lag ms:", lags)
assert max(abs(l) for l in lags) < 1.0, lags
PY
rm -f _raw48.wav
