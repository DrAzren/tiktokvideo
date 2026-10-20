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


# Session 2: lexical fillers the user asked to remove (punctuation moves to the previous word via DISPLAY)
FILLERS = {51, 52,          # "dah macam" (Keluarga dah macam tak tahu)
           60,              # "dah" (Masyarakat pula dah mula)
           106,             # "ni" (mereka ni dihantar)
           122, 131, 145,   # "ni" (Malaysia ni / Tanah Melayu ni)
           163,             # first of "seperti di kawasan seperti"
           184,             # "lah"
           274, 282,        # "dia" (nama asal dia), "ni" (lunatik ni)
           335,             # "je"
           359, 386,        # "dia" (nama dia berubah), "lah"
           595,             # "ini" (psikiatri ini dekat Malaysia)
           667,             # "sebenarnya"
           683,             # "ni" (tanah Melayu ni)
           774, 784, 786,   # "lah", "ni", "dia"
           826, 866, 871, 877,  # "lah", "ni", "lah", "je"
           912}             # "sebenarnya"
DROP |= FILLERS
# "ni"/"tu" fused into the next word (mental ni masih, kemurungan ni, seseorang tu, filem barat tu, seram tu) stay: a cut there clips both
DISPLAY.update({121: "Malaysia.", 183: "terhad.", 334: "perempuan.", 385: "dengar.", 666: "besar.", 682: "Melayu,",
                773: "Malaysia.", 783: "modern,", 797: "tu.", 798: "Kat", 825: "team.", 870: "pesakit,",
                876: "hari,", 911: "seorang.", 638: "psikiatri", 792: "filem", 681: "Tanah"})

# realign.json (from realign.py): corrected times for misaligned words, plus extra sounds/retakes to cut
RE = json.loads((E / "realign.json").read_text()) if (E / "realign.json").exists() else {"words": {}, "extra": []}


def target(prev_text: str) -> float:
    if re.search(r"[.?!]$", prev_text):
        return 0.42
    if prev_text.endswith(","):
        return 0.28
    return 0.22


def room_tone(x: np.ndarray, n: int) -> np.ndarray:
    """Real room tone from the quietest 0.5 s between words, looped with crossfades."""
    if not hasattr(room_tone, "src"):
        w = int(0.5 * SR)
        hop = w // 4
        rms = [(np.sqrt(np.mean(x[k:k + w] ** 2)), k) for k in range(30 * SR, len(x) - w, hop)]
        rms = [r for r in rms if r[0] > 1e-5]
        k = min(rms)[1]
        room_tone.src = x[k:k + w].copy()
    src, out, f = room_tone.src, np.zeros(n, np.float32), int(0.05 * SR)
    pos = 0
    while pos < n:
        seg = src.copy()
        seg[:f] *= np.linspace(0, 1, f)
        seg[-f:] *= np.linspace(1, 0, f)
        m = min(len(seg), n - pos)
        out[pos:pos + m] += seg[:m]
        pos += len(src) - f
    return out


def main():
    raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(RAW), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).copy()
    seq = []
    for i, w in enumerate(A):
        st, en = RE["words"].get(str(i), (w["start"], w["end"]))
        seq.append({"id": i, "text": w["text"], "start": st, "end": en, "drop": i in DROP})
    for label, st, en in RE["extra"]:
        seq.append({"id": label, "text": label, "start": st, "end": en, "drop": True})
    seq.sort(key=lambda w: w["start"])
    keep = [k for k, w in enumerate(seq) if not w["drop"]]
    # pieces: ("src", a, b) or ("tone", seconds)
    pieces = []
    s0 = seq[keep[0]]["start"] - 0.12
    for a_, b_ in zip(keep, keep[1:]):
        w, nw = seq[a_], seq[b_]
        g = nw["start"] - w["end"]
        t = target(DISPLAY.get(w["id"], w["text"]) or w["text"])
        if b_ == a_ + 1 and g <= t + 0.08:
            continue
        if b_ == a_ + 1:
            pa = pb = min(g, t) / 2
            tone = 0.0
        else:   # dropped words/sounds in between: stop just short of them, fill with room tone
            dropped = seq[a_ + 1:b_]
            pa = max(0.0, min(t / 2, min(d["start"] for d in dropped) - w["end"] - 0.015))
            pb = max(0.0, min(t / 2, nw["start"] - max(d["end"] for d in dropped) - 0.015))
            want = t if re.search(r"[.?!,]$", DISPLAY.get(w["id"], w["text"]) or w["text"]) else 0.09
            tone = max(0.0, want - pa - pb)
        pieces.append(("src", s0, w["end"] + pa))
        if tone > 0.005:
            pieces.append(("tone", tone))
        s0 = nw["start"] - pb
    pieces.append(("src", s0, seq[keep[-1]]["end"] + 0.6))
    # render with 20 ms equal-power fades at every join
    fade = int(0.02 * SR)
    r = np.linspace(0, 1, fade)
    out, offs = [], []
    t_out = 0.0
    for pc in pieces:
        if pc[0] == "src":
            seg = x[int(pc[1] * SR):int(pc[2] * SR)].copy()
            offs.append((pc[1], pc[2], t_out))
        else:
            seg = room_tone(x, int(pc[1] * SR))
        if len(seg) > 2 * fade:
            seg[:fade] *= np.sin(r * np.pi / 2)
            seg[-fade:] *= np.cos(r * np.pi / 2)
        out.append(seg)
        t_out += len(seg) / SR
    y = np.concatenate(out)
    sf.write(E / "voice_cut.wav", y, SR, subtype="PCM_24")

    def map_t(t):
        for a, b, o in offs:
            if a - 0.001 <= t <= b + 0.001:
                return round(o + (t - a), 3)
        raise ValueError(t)

    words = []
    for k in keep:
        w = seq[k]
        txt = DISPLAY.get(w["id"], w["text"])
        if txt == "":
            words[-1]["end"] = map_t(min(w["end"], next(b for a, b, _ in offs if a - 0.001 <= w["start"] <= b + 0.001)))
            continue
        words.append({"i": w["id"], "text": txt, "start": map_t(w["start"]), "end": map_t(w["end"])})
    (E / "cut_words.json").write_text(json.dumps(words, indent=1, ensure_ascii=False))
    ranges = [[round(pc[1], 3), round(pc[2], 3)] for pc in pieces if pc[0] == "src"]
    (E / "edl.json").write_text(json.dumps({"source": str(RAW.name), "ranges": ranges,
                                            "room_tone": [round(pc[1], 3) for pc in pieces if pc[0] == "tone"]}, indent=1))
    print(f"{len(ranges)} ranges, {len(y) / SR:.2f} s (source {len(x) / SR:.1f} s), {len(words)} words")


if __name__ == "__main__":
    main()
