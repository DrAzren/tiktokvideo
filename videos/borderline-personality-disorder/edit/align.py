"""CTC forced alignment (torchaudio MMS_FA) of the corrected Malay text per speech island.

Whisper word times drift 0.1-0.9s, so cut edges come from here instead.
English loanwords are spelled the way they are pronounced (MMS works on letters):
mudi=moody, mud swing=mood swing, eksplen=explain, bipidi=BPD, wasap=WhatsApp, perfek=perfect,
hepi=happy, syoping=shopping, self harm, stres; captions/build_transcript.py maps them back.

Hidden hesitations: besides the listed hypotheses, each island is searched greedily for '*'
(unknown sound: "aaa", "eee", "mmm", a breath) at every word boundary; an insertion is kept
only if it raises the island's mean token score by > STAR_GAIN. Output: aligned.json
"""

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio

E = Path(__file__).parent
STAR_GAIN = 0.004
ISL = {  # island id: (start, end, [hypotheses])
    "I00": (0.00, 9.21, ["orang kata borderline personality disorder ni dia sekadar mudi je mud swing betul ke"]),
    "I01": (9.21, 34.22, ["jadi jom saya eksplen tunjukkan tanda tanda utama bipidi supaya kita mudah kita lebih faham tentang penyakit ini pertama orang bipidi ni dia takut ditinggalkan contohnya kalau pasangan dia lambat balas wasap ke terus dia rasa macam diabaikan dia terus rasa panik waktu tu yang kedua hubungan mereka ni tak stabil",
                          "jom saya eksplen tunjukkan tanda tanda utama bipidi supaya kita mudah kita lebih faham tentang penyakit ini pertama orang bipidi ni dia takut ditinggalkan contohnya kalau pasangan dia lambat balas wasap ke terus dia rasa macam diabaikan dia terus rasa panik waktu tu yang kedua hubungan mereka ni tak stabil",
                          "jadi jom saya eksplen tunjukkan tanda tanda utama bipidi supaya kita mudah kita lebih faham tentang penyakit ini pertama orang bipidi ni dia takut ditinggalkan contohnya kalau pasangan dia lambat balas wasap ke terus dia rasa macam diabaikan dia terus rasa panik waktu itu yang kedua hubungan mereka ni tak stabil"]),
    "I02": (34.22, 48.76, ["sekejap rasa orang tu perfek dia sekejap rasa orang tu jahat hubungan dia jadi naik turun kalau dia percaya dengan orang tu dia mudah percaya kalau dia benci dengan orang tu dia akan benci sangat sangat yang ketiga emosi tak stabil emosi dia turun naik dengan cepat"]),
    "I03": (48.76, 67.44, ["contohnya pagi dia rasa hepi tengah hari rasa kosong malam tiba tiba marah yang keempat rasa kosong yang berpanjangan walaupun dikelilingi dengan ramai orang tetapi jiwa dia rasa kosong dalam jiwa dia tu yang kelima kemarahan yang melampau dan susah nak kawal",
                           "contohnya pagi dia rasa hepi tengah hari rasa kosong malam tiba tiba marah yang ke empat rasa kosong yang berpanjangan walaupun dikelilingi dengan ramai orang tetapi jiwa dia rasa kosong dalam jiwa dia tu yang kelima kemarahan yang melampau dan susah nak kawal"]),
    "I04": (67.44, 86.74, ["tiba tiba marah tiba tiba marah yang melampau bila rasa tak difahami walaupun benda tu benda kecil je sebenarnya nombor enam adalah tingkah laku yang impulsif contohnya syoping yang berlebihan ataupun buat sesuatu ambil risiko yang berbahaya atau self harm bila stres"]),
    "I05": (86.74, 92.49, ["kalau ada tanda tanda ni bukan bermakna anda gila ke apa ini mungkin",
                           "kalau ada tanda tanda ni bukanlah bermakna anda gila ke apa ini mungkin"]),
    "I06": (100.40, 124.50, ["kalau ada tanda tanda ni bukanlah bermakna anda gila ke apa ini adalah gejala gejala borderline personality disorder dan rawatan untuk penyakit ini memang ada kalau anda nak buat konsultasi dan saringan kesihatan mental anda boleh datang ke klinik saya di nilai sama ada nak faham tentang keadaan diri ataupun nak dapatkan rawatan yang sesuai insyaallah kami boleh bantu apa apa soalan boleh tanya di ruang komen tek ker",
                             "kalau ada tanda tanda ni bukanlah bermakna anda gila ke apa ini adalah gejala gejala borderline personality disorder dan rawatan untuk penyakit ni memang ada kalau anda nak buat konsultasi dan saringan kesihatan mental anda boleh datang ke klinik saya di nilai sama ada nak faham tentang keadaan diri ataupun nak dapatkan rawatan yang sesuai insyaallah kami boleh bantu apa apa soalan boleh tanya di ruang komen tek ker"]),
}


def main() -> None:
    only = set(sys.argv[1:])  # optional: re-align just these islands, merging into aligned.json
    bundle = torchaudio.pipelines.MMS_FA
    model = bundle.get_model(with_star=True).eval()
    tokenizer = bundle.get_tokenizer()
    aligner = bundle.get_aligner()
    audio, sr = sf.read(E / "audio.wav", dtype="float32")
    assert sr == bundle.sample_rate

    out = json.loads((E / "aligned.json").read_text()) if only and (E / "aligned.json").exists() else {}
    for iid, (a, b, hyps) in ISL.items():
        if only and iid not in only:
            continue
        wav = torch.from_numpy(audio[int(a * sr):int(b * sr)]).unsqueeze(0)
        with torch.inference_mode():
            emission, _ = model(wav)
        ratio = wav.shape[1] / emission.shape[1] / sr  # seconds per frame

        def score(words):
            spans = aligner(emission[0], tokenizer(words))
            return float(np.mean([s.score for ws in spans for s in ws])), spans

        best = max(((score(h.split())[0], h) for h in hyps))
        words = best[1].split()
        cur, _ = score(words)
        stars = []
        while True:   # greedy '*' insertion at word boundaries
            cands = [(score(words[:i] + ["*"] + words[i:])[0], i) for i in range(1, len(words))
                     if words[i - 1] != "*" and words[i] != "*"]
            s, i = max(cands)
            if s - cur <= STAR_GAIN:
                break
            words = words[:i] + ["*"] + words[i:]
            stars.append(f"{words[i - 1]}_*_{words[i + 1]}(+{s - cur:.3f})")
            cur = s
        _, spans = score(words)
        out[iid] = {
            "hyp": best[1], "score": round(cur, 3),
            "words": [{"text": w, "start": round(a + ws[0].start * ratio, 3), "end": round(a + ws[-1].end * ratio, 3),
                       "score": round(float(np.mean([s.score for s in ws])), 3)} for w, ws in zip(words, spans)],
        }
        alts = "" if len(hyps) == 1 else f"  (picked {hyps.index(best[1]) + 1}/{len(hyps)})"
        print(f"{iid} score={cur:.3f}{alts}  stars: {' '.join(stars) or '-'}")
    out = dict(sorted(out.items(), key=lambda kv: kv[1]["words"][0]["start"]))
    (E / "aligned.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
