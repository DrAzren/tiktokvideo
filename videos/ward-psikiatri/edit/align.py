"""CTC forced alignment (torchaudio MMS_FA) of corrected Malay text per speech island.

Whisper word times drift 0.1-0.9s on this clip, so cut edges come from here instead.
Each island lists one or more text hypotheses; the best-scoring one wins.
'*' = unknown sound (breath, unclear syllable). Output: aligned.json
"""

import json
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio
import torchaudio.functional as F

E = Path(__file__).parent
ISL = {  # island id: (start, end, [hypotheses])
    "I00": (0.80, 2.45, ["saya pernah ada pesakit", "* saya pernah ada pesakit"]),
    "I01": (2.50, 5.90, ["aa tanya dekat saya doktor macam mana saya masa",
                         "aa tanya dekat saya doktor macam mana saya mas"]),
    "I02": (6.00, 14.30, ["doktor macam mana keadaan dalam wad psikiatri ya saya takutlah saya tengok aa macam dalam filem filem barat tu nampak seram sangat okay sebenarnya"]),
    "I03": (14.35, 15.00, ["tidak"]),
    "I04": (16.20, 29.75, ["* sebenarnya tidak wad psikiatri malaysia jauh berbeza dengan apa yang anda bayangkan kalau anda * kalau anda ahli keluarga sedang bergelut dengan masalah kesihatan mental boleh datang buat saringan * *",
                          "sebenarnya tidak wad psikiatri malaysia jauh berbeza dengan apa yang anda bayangkan kalau anda * kalau anda ahli keluarga sedang bergelut dengan masalah kesihatan mental boleh datang buat saringan * *"]),
    "I05": (30.70, 38.40, ["boleh datang buat saringan konsultasi kesihatan mental di klinik saya untuk kita bincang dulu aa diagnosis dan pilihan rawatan apa yang sesuai untuk anda"]),
    "I07": (42.95, 45.85, ["kita bincang dahulu pilihan rawatan yang paling sesuai untuk anda"]),
    "I08": (46.15, 50.95, ["okey balik kepada topik tadi ramai orang bayangkan wad psikiatri ini macam dalam filem"]),
    "I09": (51.05, 60.70, ["gelap semua pesakit meracau racau dekat dalam wad aa kena ikat sepanjang masa tapi tidak sebenarnya di malaysia wad adalah wad hospital yang",
                          "gelap semua pesakit meracau racau dekat dalam wad kena ikat sepanjang masa tapi tidak sebenarnya di malaysia wad adalah wad hospital yang"]),
    "I13": (74.90, 85.10, ["di malaysia wad psikiatri adalah salah satu wad di hospital yang dikendalikan oleh doktor psikiatri jururawat terlatih",
                          "* di malaysia wad psikiatri adalah salah satu wad di hospital yang dikendalikan oleh doktor psikiatri jururawat terlatih"]),
    # I14..I17 re-aligned as one passage: "kaunselor" is the short burst at ~87.1-87.8s
    # (large-v3, unprompted: p=0.97); what sits at ~88.3-88.7s before "terapi" is tested.
    "I14": (85.15, 102.10, ["ahli psikologi kaunselor terapi jurupulih kerja dan lain lain lagi apa pesakit buat dalam wad pesakit akan jumpa dengan doktor setiap hari ataupun mengikut keperluan dan pesakit perlulah mengambil ubat mengikut jadual dan pemerhatian rapi dan keselamatan",
                            "ahli psikologi kaunselor * terapi jurupulih kerja dan lain lain lagi apa pesakit buat dalam wad pesakit akan jumpa dengan doktor setiap hari ataupun mengikut keperluan dan pesakit perlulah mengambil ubat mengikut jadual dan pemerhatian rapi dan keselamatan",
                            "ahli psikologi kaunselor aa terapi jurupulih kerja dan lain lain lagi apa pesakit buat dalam wad pesakit akan jumpa dengan doktor setiap hari ataupun mengikut keperluan dan pesakit perlulah mengambil ubat mengikut jadual dan pemerhatian rapi dan keselamatan",
                            "ahli psikologi kaunselor te terapi jurupulih kerja dan lain lain lagi apa pesakit buat dalam wad pesakit akan jumpa dengan doktor setiap hari ataupun mengikut keperluan dan pesakit perlulah mengambil ubat mengikut jadual dan pemerhatian rapi dan keselamatan"]),
    "I18": (102.12, 103.60, ["dipantau", "akan dipantau"]),
    "I19": (104.80, 113.40, ["aktiviti terapi seperti terapi cara kerja senaman ringan sesi kaunseling ini bergantung pada hospital dan keadaan pesakitlah akan dijalankan juga"]),
    "I20": (113.42, 116.00, ["dan makan dan rehat adalah"]),
    "I21": (116.05, 122.60, ["ikut jadual semua tujuan utama dia adalah untuk menstabilkan pesakit bukan untuk menghukum pesakit adakah",
                            "ikut jadual semua tujuan utama dia adalah untuk menstabilkan pesakit bukan untuk menghukum pesakit",
                            "ikut jadual * tujuan utama dia adalah untuk menstabilkan pesakit bukan untuk menghukum pesakit adakah"]),
    "I22": (123.10, 127.05, ["datang pula soalan kedua adakah semua pesakit dalam wad ni agresif",
                            "adakah datang pula soalan kedua adakah semua pesakit dalam wad ni agresif"]),
    "I24": (129.15, 142.70, ["jawapannya tidak pesakit dalam wad psikiatri ini mereka mengalami mereka mungkin mengalami kemurungan yang teruk anxiety yang melampau bipolar yang tidak stabil skizofrenia yang tidak stabil ataupun krisis emosi yang"]),
    "I25": (143.05, 144.50, ["memerlukan pemantauan"]),
    "I26": (144.60, 146.75, ["ramai yang pendiam takut"]),
    "I27": (146.85, 149.40, ["sebab mereka sedang berjuang dengan penyakit mereka"]),
    "I31": (156.65, 194.00, ["ada juga yang tanya saya kenapa ada pesakit sampai kena ikat doktor betul ke ni mereka pernah kena ikat ini adalah salah faham yang paling biasalah physical restraint bukanlah rutin yang dijalankan ia hanyalah digunakan sebagai langkah terakhir apabila seseorang itu pertama berisiko mencederakan diri sendiri yang kedua berisiko mencederakan orang lain dan semua cara lain untuk menenangkan pesakit tidak berjaya apabila pesakit sudah stabil restrain tersebut akan dihentikan secepat mungkin ikut prosedur dan pemantauan yang ketatlah yang penting kat sini adalah masuk wad psikiatri ni bukan bermaksud hidup dah berakhir dah bukan bermaksud anda gila ke apa",
                            "* ada juga yang tanya saya kenapa ada pesakit sampai kena ikat doktor betul ke ni mereka pernah kena ikat ini adalah salah faham yang paling biasalah physical restraint bukanlah rutin yang dijalankan ia hanyalah digunakan sebagai langkah terakhir apabila seseorang itu pertama berisiko mencederakan diri sendiri yang kedua berisiko mencederakan orang lain dan semua cara lain untuk menenangkan pesakit tidak berjaya apabila pesakit sudah stabil restrain tersebut akan dihentikan secepat mungkin ikut prosedur dan pemantauan yang ketatlah yang penting kat sini adalah masuk wad psikiatri ni bukan bermaksud hidup dah berakhir dah bukan bermaksud anda gila ke apa"]),
    "I33": (196.80, 209.60, ["tidak ramai pesakit masuk wad psikiatri selepas beberapa hari beberapa minggu keluar semula sambung rawatan mereka kembali bekerja kembali belajar kembali hidup seperti biasa wad psikiatri ni bukan tempat hukum ke apa ia adalah tempat"]),
    "I34": (210.45, 217.60, ["ia adalah tempat yang selamat sebenarnya untuk seseorang itu berehat distabilkan dan diberi peluang untuk"]),
    "I35": (218.25, 227.00, ["memulakan proses sembuh itu jadi kalau anda ataupun orang tersayang sedang bergelut dengan kesihatan mental jangan takut untuk mendapatkan bantuan rawatan"]),
    "I36": (227.35, 231.50, ["jangan takut untuk mendapatkan bantuan apa apa soalan minta anda komen take care",
                            "jangan takut untuk mendapatkan bantuan apa apa soalan minta anda komen tekeh"]),
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
