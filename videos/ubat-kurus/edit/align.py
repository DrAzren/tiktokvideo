"""CTC forced alignment (torchaudio MMS_FA) of corrected Malay text per speech island.

Whisper word times drift on this clip, so cut edges come from here instead.
Each island lists one or more text hypotheses; the best-scoring one wins.
'*' = unknown sound (breath, "ehm", unclear syllable). Output: aligned.json
Islands follow Whisper (medium + large-v3) segment bounds: the speaker barely pauses.
"""

import json
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio

E = Path(__file__).parent
ISL = {  # island id: (start, end, [hypotheses])
    "I00": (0.00, 3.02, ["assalamualaikum saya doktor azren saya merupakan doktor di jabatan psikiatri",
                         "assalamualaikum saya doktor azrin saya merupakan doktor di jabatan psikiatri"]),
    "I01": (3.02, 9.50, ["sebelum ni saya pernah buat satu video explain senarai ubat ubatan yang sering dikaitkan dengan kenaikan berat badan"]),
    "I02": (9.50, 16.25, ["tapi kali ni saya nak cerita ubat ubat yang sering dikaitkan dengan penurunan berat badan pula"]),
    "I03": (16.25, 24.38, ["ok ubat yang pertama adalah bupropion ubat ni adalah sejenis antidepressant yang boleh kurangkan selera makan sebenarnya",
                           "okay ubat yang pertama adalah bupropion ubat ni adalah sejenis antidepressant yang boleh kurangkan selera makan sebenarnya"]),
    "I04": (24.38, 30.15, ["biasanya digunakan untuk merawat kemurungan dan juga bantu orang untuk berhenti merokok juga"]),
    "I05": (30.15, 36.45, ["tapi ingat bukan semua orang akan turun berat bergantung pada badan masing masing"]),
    "I06": (36.90, 44.60, ["yang kedua adalah topiramate ini asalnya adalah ubat sawan sebenarnya tapi doktor kadang kadang guna untuk masalah mood juga",
                           "yang kedua adalah topiramid ini asalnya adalah ubat sawan sebenarnya tapi doktor kadang kadang guna untuk masalah mood juga"]),
    # false start: unknown sound 45.35-45.7, "dia ada" 46.19-46.53, then the real "dia boleh" from 47.04
    # (re-aligned from 45.25: "* dia boleh" 0.915 beats every reading that puts "dia" in the 46.2 burst)
    "I07": (44.60, 52.25, ["* dia ada * dia boleh turunkan berat badan dan buat rasa kenyang dengan cepat dan kurang craving",
                           "* * dia boleh turunkan berat badan dan buat rasa kenyang dengan cepat dan kurang craving"]),
    "I08": (52.25, 59.40, ["tapi kesan sampingan dia ada banyak sikit ada orang yang senang rasa semput sikit kalau ambil dengan dos yang tinggi"]),
    "I09": (60.80, 64.30, ["yang ketiga adalah fluoxetine"]),
    "I14": (88.30, 96.45, ["fluoxetine ni adalah ssri yang commonly and widely used for antidepressant and also untuk masalah anxiety",
                           "fluoxetine ni adalah ssri yang commonly and widely used for antidepressant and also untuk untuk masalah anxiety",
                           "fluoxetine ni adalah ssri yang commonly and widely used for antidepressant and also * untuk masalah anxiety"]),
    "I16": (98.55, 112.00, ["kadang kadang boleh buat orang turun berat badan masa awal awal rawatan tu sebab ada orang dia hilang selera makan tapi untuk jangka panjang sebenarnya berat badan mungkin akan naik balik sedikit lah jadi benda ni kena monitor"]),
    "I17": (112.00, 121.72, ["yang penting kita kena faham setiap ubat dia ada kesan yang berbeza beza untuk setiap orang mungkin ketiga tiga ubat yang saya sebut ni boleh menyebabkan kenaikan berat badan pada setengah orang"]),
    "I18": (121.72, 131.79, ["jangan pilih ubat sebab nak kurus semata mata kena sentiasa berbincang dengan doktor untuk rawatan yang paling sesuai dengan anda apa apa soalan boleh tanya di dalam komen take care",
                             "jangan pilih ubat sebab nak kurus semata mata kena sentiasa berbincang dengan doktor untuk rawatan yang paling sesuai dengan anda apa apa soalan boleh tanya di ruangan komen take care",
                             "jangan pilih ubat sebab nak kurus semata mata kena sentiasa berbincang dengan doktor untuk rawatan yang paling sesuai dengan anda apa apa soalan boleh tanya di ruang komen take care"]),
}


def main() -> None:
    import sys
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
        best = None
        for h in hyps:
            words = h.split()
            spans = aligner(emission[0], tokenizer(words))
            score = float(np.mean([s.score for ws in spans for s in ws]))
            if best is None or score > best[0]:
                best = (score, h, words, spans)
        score, h, words, spans = best
        out[iid] = {
            "hyp": h, "score": round(score, 3),
            "words": [{"text": w, "start": round(a + ws[0].start * ratio, 3), "end": round(a + ws[-1].end * ratio, 3),
                       "score": round(float(np.mean([s.score for s in ws])), 3)} for w, ws in zip(words, spans)],
        }
        alts = "" if len(hyps) == 1 else f"  (picked {hyps.index(h) + 1}/{len(hyps)})"
        print(f"{iid} score={score:.3f}{alts}")
    out = dict(sorted(out.items(), key=lambda kv: kv[1]["words"][0]["start"]))
    (E / "aligned.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
