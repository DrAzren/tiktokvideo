"""Podcast-style voice polish ("Adobe Podcast Enhance"-like), ffmpeg only, fully local.

Chain (order matters):
  highpass 75 Hz → FFT denoise (afftdn, tracks the noise floor) → soft downward expander for room
  tone between phrases → de-mud -3 dB @ 300 Hz → presence +2.5 dB @ 3.2 kHz → air +2 dB shelf
  @ 10 kHz → de-esser → 3:1 compressor → two-pass loudnorm (-14 LUFS / -1 dBTP by default).

There is no neural de-reverb here; for heavily echoey rooms run the voice through a model-based
enhancer first (Adobe Podcast, DeepFilterNet) and pass that file in.

Usage: python tools/enhance_speech.py in.(wav|mp4) -o out.wav [--lufs -14]
"""
import argparse
import json
import subprocess

CHAIN = ("highpass=f=75:poles=2,afftdn=nr=14:nf=-50:tn=1,"
         "agate=threshold=0.012:ratio=2:attack=5:release=180:range=0.25,"
         "equalizer=f=300:t=q:w=1.0:g=-3,equalizer=f=3200:t=q:w=1.2:g=2.5,treble=g=2:f=10000,"
         "deesser=i=0.35,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2:knee=4")


def ff(*a):
    return subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", *a], capture_output=True, text=True, check=True).stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--lufs", type=float, default=-14.0)
    a = ap.parse_args()
    target = f"I={a.lufs}:TP=-1:LRA=9"
    err = ff("-i", a.input, "-vn", "-af", f"{CHAIN},loudnorm={target}:print_format=json", "-f", "null", "-")
    j = json.loads(err[err.rindex("{"):err.rindex("}") + 1])
    ln = (f"loudnorm={target}:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    ff("-y", "-i", a.input, "-vn", "-af", f"{CHAIN},{ln}", "-ar", "48000", "-c:a", "pcm_s24le", a.output)
    print(f"enhanced → {a.output}  (input {j['input_i']} LUFS)")


if __name__ == "__main__":
    main()
