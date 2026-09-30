"""CTC forced alignment (torchaudio MMS_FA) of the corrected Malay text over the whole clip.

Differences from the ward-psikiatri version (which aligned per island):
  - the CapCut draft is already tight (few pauses), so islands are long and fuzzy; instead the
    emission is computed in overlapping 30s windows, stitched, and the full text aligned once;
  - a '*' (unknown-sound) slot sits between every pair of words, so voiced hesitations
    ("aa", "eee", "mmm") land in a '*' span with exact times instead of being absorbed into a
    neighbouring word. A '*' costs at least one 20ms frame even when nothing is there.

Text = unprompted large-v3 transcript, corrected by ear-free checks (alignment score, context).
Numbers are spelled out for the romanised tokenizer. Output: aligned.json
  {"words": [{text, start, end, score, i}], "stars": [{after, start, end}]}
"""

import json
import re
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio

E = Path(__file__).parent
WIN, HOP = 30.0, 20.0     # emission windows (s); the middle of each window is kept

TEXT = """
pernah tak anda dengar suara orang panggil nama anda tapi bila toleh tak ada siapa pun
ataupun ada orang yang berbisik dengan bisikan yang sangat jelas cakap benda negatif tentang diri anda
atau anda nampak bayang bayang hitam lalu tapi bila tengok balik tak ada apa apa kosong
itu adalah halusinasi tapi adakah halusinasi ini hanya berlaku kepada pesakit mental jom kita bincangkan
okay definisi halusinasi bermaksud persepsi deria yang terjadi tanpa rangsangan sebenar daripada persekitaran
without any external stimulation ia boleh melibatkan pendengaran penglihatan bau rasa sentuhan yang tak wujud pun sebenarnya
sebenarnya halusinasi ini bukannya hanya dialami oleh pesakit mental seperti pesakit skizofrenia atau gangguan mental yang lain
ia juga boleh berlaku pada sesiapa saja sebenarnya termasuklah orang yang normal orang yang sihat
contoh yang pertama adalah halusinasi yang kita panggil sebagai hypnagogic hallucination
iaitu bayangan atau suara yang muncul sebelum kita tidur
pernah tak rasa macam ada sesuatu yang tarik selimut anda tapi bila buka mata tak ada apa apa pun sebenarnya
itu normal dan tak semestinya tanda penyakit
ada juga halusinasi yang berlaku selepas kita bangun dari tidur yang kita panggil sebagai hypnopompic hallucination
ada juga halusinasi yang berlaku akibat seorang itu kurang tidur bila anda tak cukup rehat selama beberapa hari
contohnya lima hari tidur dua tiga jam je otak boleh jadi overload dan boleh mencipta image atau bunyi yang sebenarnya tak wujud pun
jadi halusinasi ini boleh disebabkan oleh banyak faktor yang lain seperti stres yang melampau kesedihan yang berpanjangan
penggunaan dadah migrain atau gangguan neurologi seperti parkinson
tapi kalau halusinasi ini semakin kerap boleh mengganggu kehidupan seharian anda atau datang dengan perasaan takut atau paranoid
itu mungkin menjadi petanda masalah mental dan memerlukan rawatan jangan takut untuk dapatkan bantuan
jadi kesimpulannya tak semua halusinasi tanda sakit mental tapi kalau ia berterusan better jumpa doktor untuk check
jangan lupa follow untuk lebih banyak perkongsian ilmu kesihatan mental apa apa soalan boleh tanya di ruang komen take care
"""


def emissions(model, audio: np.ndarray, sr: int) -> tuple[torch.Tensor, float]:
    """Log-prob emission for the whole clip from overlapping windows (keep each window's middle)."""
    total = len(audio) / sr
    chunks, t = [], 0.0
    ratio = None
    while t < total:
        a, b = int(t * sr), int(min(total, t + WIN) * sr)
        with torch.inference_mode():
            em, _ = model(torch.from_numpy(audio[a:b]).unsqueeze(0))
        em = em[0]
        ratio = (b - a) / em.shape[0] / sr if ratio is None else ratio
        keep_from = 0 if t == 0 else int(((WIN - HOP) / 2) / ratio)
        keep_to = em.shape[0] if t + WIN >= total else int((WIN - (WIN - HOP) / 2) / ratio)
        chunks.append((t + keep_from * ratio, em[keep_from:keep_to]))
        if t + WIN >= total:
            break
        t += HOP
    # stitch by absolute frame index
    n = int(round(total / ratio))
    out = torch.full((n, chunks[0][1].shape[1]), float("nan"))
    for t0, em in chunks:
        i0 = int(round(t0 / ratio))
        out[i0:i0 + em.shape[0]] = em[:max(0, min(em.shape[0], n - i0))]
    assert not torch.isnan(out).any(), "emission stitching left a hole"
    return out, ratio


def main() -> None:
    bundle = torchaudio.pipelines.MMS_FA
    model = bundle.get_model(with_star=True).eval()
    tokenizer, aligner = bundle.get_tokenizer(), bundle.get_aligner()
    audio, sr = sf.read(E / "audio.wav", dtype="float32")
    assert sr == bundle.sample_rate
    em, ratio = emissions(model, audio, sr)

    words = re.sub(r"\s+", " ", TEXT).strip().split()
    seq = []
    for k, w in enumerate(words):
        seq.append(w)
        if k + 1 < len(words):
            seq.append("*")
    spans = aligner(em, tokenizer(seq))

    out_w, stars = [], []
    for tok, ws in zip(seq, spans):
        s, e = round(ws[0].start * ratio, 3), round(ws[-1].end * ratio, 3)
        if tok == "*":
            stars.append({"after": len(out_w) - 1, "start": s, "end": e})
        else:
            out_w.append({"i": len(out_w), "text": tok, "start": s, "end": e,
                          "score": round(float(np.mean([x.score for x in ws])), 3)})
    score = float(np.mean([w["score"] for w in out_w]))
    (E / "aligned.json").write_text(json.dumps({"score": round(score, 3), "words": out_w, "stars": stars},
                                               indent=1, ensure_ascii=False))
    low = [f"{w['text']}@{w['start']:.2f}({w['score']:.2f})" for w in out_w if w["score"] < 0.35]
    print(f"{len(out_w)} words, mean score {score:.3f}; low-score words: {' '.join(low) or 'none'}")


if __name__ == "__main__":
    main()
