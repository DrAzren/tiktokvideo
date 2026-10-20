"""Session 2: re-time spots where aligned.json is wrong, and locate extra sounds/retakes to cut.

Each window is re-aligned with MMS_FA against the words actually said there (from large-v3 on the cut voice). Tokens:
  "518:dan"  → aligned.json word 518 gets these times
  "~ha"      → an extra sound or retake to cut (build_voice drops it)
  "_word"    → said but not indexed (context only)
Alternative wordings per window are all tried; the best mean score wins.
Output: realign.json = {"words": {idx: [start, end]}, "extra": [[label, start, end]]}
Run: ../../../.venv/bin/python realign.py
"""

import json
import subprocess
from pathlib import Path

import numpy as np
import torch
import torchaudio

from align import norm

E = Path(__file__).parent
SR = 16000

WINDOWS = [
    # 3:24 in the video: "Dan penting untuk kita faham, amalan rawatan berbeza mengikut" said twice
    (239.0, 248.2, ["_yang _tinggi ~dan ~penting ~untuk ~kita ~faham ~amalan ~rawatan ~berbeza ~mengikut 518:dan "
                    "519:penting 520:untuk 521:kita 522:faham 523:amalan 524:rawatan 525:berbeza 526:mengikut 527:hospital 528:dan 529:zaman"]),
    # the "Ha," sounds themselves are too short for MMS; they are cut by hand below (MANUAL)
    (293.6, 296.3, ["628:gangguan 629:pemikiran 630:pada 631:masa 632:yang 633:sama 634:juga"]),
    (299.0, 302.5, ["640:lain 641:semakin 642:berkembang 643:rawatan 644:masih 645:mempunyai"]),
    # "pada tahun, pada tahun 1958" — the first "pada tahun" hid inside word 672 (1.5 s long)
    (317.9, 323.0, ["~pada ~tahun 672:pada 673:tahun 674:sembilan_belas_lima_puluh_lapan 675:satu 676:lagi 677:perkembangan",
                    "~pada ~tahun 672:pada 673:tahun 674:nineteen_fifty_eight 675:satu 676:lagi 677:perkembangan"]),
    # "dalam filem, filem barat tu" — stutter
    (369.9, 372.2, ["790:digambarkan 791:dalam ~filem 792:filem 793:barat 794:tu"]),
]

# extra sounds located on the energy envelope (25 ms steps) between two well-aligned words
MANUAL = [("ha294", 294.70, 295.00),   # "Ha," after "gangguan pemikiran."
          ("ha300", 300.67, 300.94),   # "Ha," after "semakin berkembang."
          ("lah358", 358.29, 358.45),  # "lah" after "rawatan perubatan" (the "-an" ends at 358.28)
          ("ha424", 424.22, 424.42)]   # "Ha," before "Kalau anda" (the k closure starts 424.43)


def main():
    raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(E / "audio.wav"), "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, np.float32).copy()
    bundle = torchaudio.pipelines.MMS_FA
    model = bundle.get_model(with_star=True).eval()
    tok, aligner = bundle.get_tokenizer(), bundle.get_aligner()
    out = {"words": {}, "extra": []}
    for a, b, alts in WINDOWS:
        wav = torch.from_numpy(audio[int(a * SR):int(b * SR)]).unsqueeze(0)
        with torch.inference_mode():
            em, _ = model(wav)
        ratio = wav.shape[1] / em.shape[1] / SR
        best = None
        for text in alts:
            toks = text.split()
            words = [t.split(":", 1)[1] if ":" in t else t.lstrip("~_") for t in toks]
            groups = [[p for w in word.split("_") for p in norm(w)] for word in words]
            spans = aligner(em[0], tok([t for g in groups for t in g]))
            res, i = [], 0
            for t, g in zip(toks, groups):
                sp = spans[i:i + len(g)]
                i += len(g)
                res.append((t, round(a + sp[0][0].start * ratio, 3), round(a + sp[-1][-1].end * ratio, 3),
                            float(np.mean([s.score for x in sp for s in x]))))
            sc = float(np.mean([r[3] for r in res]))
            print(f"  {a:.1f} score {sc:.3f}: " + " ".join(f"{t}@{s:.2f}-{e:.2f}({q:.2f})" for t, s, e, q in res))
            if best is None or sc > best[0]:
                best = (sc, res)
        for t, s, e, _ in best[1]:
            if t.startswith("~"):
                out["extra"].append([f"x{a:.0f}{t}", s, e])
            elif ":" in t:
                out["words"][t.split(":")[0]] = [s, e]
    out["extra"] += [list(m) for m in MANUAL]
    (E / "realign.json").write_text(json.dumps(out, indent=1))
    print(len(out["words"]), "words re-timed,", len(out["extra"]), "extras to cut")


if __name__ == "__main__":
    main()
