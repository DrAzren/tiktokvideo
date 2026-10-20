"""Cut the narration: drop retakes/false starts, shrink long pauses, keep real room tone at every join.

Inputs: audio (raw mp3), aligned.json (MMS_FA word times).
Outputs: voice_cut.wav (48 kHz mono), edl.json (source ranges), cut_words.json (display words at output times).
Run: ../../../.venv/bin/python build_voice.py
"""

import json
import re
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

E = Path(__file__).parent
RAW = E.parent / "raw" / "Sejarah Wad Psikiatri Di Malaysia.mp3"
SR = 48000
A = json.loads((E / "aligned.json").read_text())

DROP = {218,                      # first "Bayangkan." (retaken after a 3.4 s pause)
        279,                      # "Ha"
        393, 394, 395,            # "dalam wad psikiatri" → corrected to "dalam hospital psikiatri"
        541, 542, 543, 544, 545,  # "Dan satu perkara yang jelas" → restated as "...yang penting"
        563, 564,                 # "And then,"
        598,                      # "Malaysia." repeated
        668, 669, 670, 671,       # false start "pesakit yang sebelum ini"
        767,                      # "terus terus"
        976, 977,                 # false start "kalau tuan-tuan"
        197}                      # stutter "Rawatan, rawatan pun"

# Whisper spellings → what is said (subtitles); index → display text ("" hides a token merged into the previous one)
DISPLAY = {198: "Rawatan", 304: "", 193: "sepenuhnya", 194: "", 266: "psikiatri", 303: "menggambarkan",
           348: "psikiatri", 392: "pesakit", 404: "pesakit", 426: "mood", 452: "psikiatri", 581: "chlorpromazine",
           685: "psikiatri", 692: "direkodkan", 695: "psikiatri", 825: "team", 859: "pemantauan", 935: "saringan",
           941: "Azren", 942: "di", 943: "Klinik", 944: "Nissa.", 945: "", 959: "White", 960: "Coat", 961: "Books.",
           953: "Doktor,", 957: "Ke?", 984: "wad", 985: "psikiatri", 923: "Cepat-cepat", 924: "", 913: "Kalau",
           930: "mental.", 939: "saya,", 912: "sebenarnya.", 975: "difahami.", 993: "komen.", 1000: "komen.",
           1002: "care.", 591: "penting", 597: "Malaysia.", 667: "sebenarnya.", 891: "lama."}


def target(prev_text: str) -> float:
    if re.search(r"[.?!]$", prev_text):
        return 0.42
    if prev_text.endswith(","):
        return 0.28
    return 0.22


def main():
    raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(RAW), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).copy()
    keep = [(i, w) for i, w in enumerate(A) if i not in DROP]
    # source ranges
    ranges = []
    s0 = keep[0][1]["start"] - 0.12
    for k in range(len(keep) - 1):
        (i, w), (j, nw) = keep[k], keep[k + 1]
        g = nw["start"] - w["end"]
        t = target(DISPLAY.get(i, w["text"]) or w["text"])
        if g > t + 0.08 or j != i + 1:
            half = min(g, t) / 2
            ranges.append([round(s0, 3), round(w["end"] + half, 3)])
            s0 = nw["start"] - half
    ranges.append([round(s0, 3), round(keep[-1][1]["end"] + 0.6, 3)])
    # render with 20 ms equal-power fades at every join
    fade = int(0.02 * SR)
    out, offs = [], []
    t_out = 0.0
    for a, b in ranges:
        seg = x[int(a * SR):int(b * SR)].copy()
        r = np.linspace(0, 1, fade)
        seg[:fade] *= np.sin(r * np.pi / 2)
        seg[-fade:] *= np.cos(r * np.pi / 2)
        out.append(seg)
        offs.append((a, b, t_out))
        t_out += len(seg) / SR
    y = np.concatenate(out)
    sf.write(E / "voice_cut.wav", y, SR, subtype="PCM_24")

    def map_t(t):
        for a, b, o in offs:
            if a - 0.001 <= t <= b + 0.001:
                return round(o + (t - a), 3)
        raise ValueError(t)

    words = []
    for i, w in keep:
        txt = DISPLAY.get(i, w["text"])
        if txt == "":
            words[-1]["end"] = map_t(min(w["end"], next(b for a, b, _ in offs if a <= w["start"] <= b)))
            continue
        words.append({"i": i, "text": txt, "start": map_t(w["start"]), "end": map_t(w["end"])})
    (E / "cut_words.json").write_text(json.dumps(words, indent=1, ensure_ascii=False))
    (E / "edl.json").write_text(json.dumps({"source": str(RAW.name), "ranges": ranges}, indent=1))
    print(f"{len(ranges)} ranges, {len(y) / SR:.2f} s (source {len(x) / SR:.1f} s), {len(words)} words")


if __name__ == "__main__":
    main()
