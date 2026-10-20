"""MMS_FA forced alignment of the (corrected) Whisper transcript, per speech island.

Whisper large-v3 word times drift; this re-times every word to ~20 ms. The first 30 s
were re-transcribed separately (the full pass hallucinated there).
Output: aligned.json = [{"text", "norm", "start", "end", "score", "island"}]
"""

import json
import re
import subprocess
from pathlib import Path

import numpy as np
import torch
import torchaudio

E = Path(__file__).parent
SR = 16000
INTRO = ("Bayangkan anda hidup pada tahun 1911. Waktu tu tak ada smartphone pun. Tak ada internet. Malaysia pun belum "
         "merdeka lagi. Tiba-tiba ada seorang ahli keluarga anda yang mula berubah. Dia bercakap seorang diri. Dia dengar "
         "suara yang orang tak boleh dengar. Kadang-kadang dia ketawa sendiri. Kadang-kadang dia jadi ketakutan. Paranoid. "
         "Keluarga dah macam tak tahu nak buat apa.")
NUM = {"1911": "sembilan belas sebelas", "1928": "sembilan belas dua puluh lapan", "1958": "sembilan belas lima puluh lapan",
       "1970-an": "sembilan belas tujuh puluhan", "1950-an": "sembilan belas lima puluhan", "ke-19": "kesembilan belas"}
FIX = {"macam -macam": "macam-macam", "abad ke -19": "abad ke-19", "1970 -an": "1970-an", "1950 -an": "1950-an",
       "wad -wad": "wad-wad", "rawatan -rawatan": "rawatan-rawatan", "sangat -sangat": "sangat-sangat",
       "hospital -hospital": "hospital-hospital", "film -film": "filem-filem", "cepat -cepat": "cepat-cepat",
       "tuan -tuan": "tuan-tuan", "Tiba -tiba": "Tiba-tiba", "Kadang -kadang": "Kadang-kadang"}


def norm(w: str) -> list[str]:
    core = re.sub(r"[^\w-]", "", w)
    if core in NUM:
        return NUM[core].split()
    t = re.sub(r"[^a-z']", "", core.lower().replace("-", ""))
    return [t] if t else []


def main():
    d = json.loads((E / "transcripts" / "voice.json").read_text())
    ws = [w for w in d["words"] if w["type"] == "word" and w["start"] >= 30.6]
    # islands from Whisper gaps (> 0.6 s), intro island 4.0–30.75; text fixes applied inside each island
    groups, cur = [], None
    for w in ws:
        if cur is None or w["start"] - cur[1] > 0.6:
            if cur:
                groups.append(cur)
            cur = [w["start"], w["end"], [w["text"]]]
        else:
            cur[1] = w["end"]
            cur[2].append(w["text"])
    groups.append(cur)
    isl = [[4.0, 30.75, INTRO.split()]]
    for st, en, words in groups:
        text = " ".join(words)
        for x, y in FIX.items():
            text = text.replace(x, y)
        isl.append([st, en, text.split()])
    raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(E / "audio.wav"), "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, np.float32).copy()
    bundle = torchaudio.pipelines.MMS_FA
    model = bundle.get_model(with_star=True).eval()
    tok, aligner = bundle.get_tokenizer(), bundle.get_aligner()
    out = []
    for k, (a, b, words) in enumerate(isl):
        lo = isl[k - 1][1] + 0.05 if k else 0.0
        hi = isl[k + 1][0] - 0.05 if k + 1 < len(isl) else len(audio) / SR
        a, b = max(lo, a - 1.2), min(hi, b + 1.2)
        groups = [norm(w) for w in words]
        flat = [t for g in groups for t in g]
        wav = torch.from_numpy(audio[int(a * SR):int(b * SR)]).unsqueeze(0)
        with torch.inference_mode():
            em, _ = model(wav)
        ratio = wav.shape[1] / em.shape[1] / SR
        spans = aligner(em[0], tok(flat))
        i = 0
        for w, g in zip(words, groups):
            if not g:
                continue
            sp = spans[i:i + len(g)]
            i += len(g)
            out.append({"text": w, "norm": " ".join(g), "start": round(a + sp[0][0].start * ratio, 3),
                        "end": round(a + sp[-1][-1].end * ratio, 3),
                        "score": round(float(np.mean([s.score for x in sp for s in x])), 3), "island": k})
        print(f"I{k:02d} {a:7.2f}-{b:7.2f} {len(words):3d} words")
    (E / "aligned.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(len(out), "aligned words")


if __name__ == "__main__":
    main()
