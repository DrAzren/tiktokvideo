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
    "I00": (2.30, 12.90, ["teringat satu hari tu ketika saya bertugas sebagai doktor di atas panggilan doktor on call ada seorang remaja umur tujuh belas tahun yang dibawa oleh kedua ibu bapanya ke jabatan kecemasan"]),
    "I01": (12.90, 16.45, ["dia kelihatan sangat pucat menggigil tangan dia"]),
    "I02": (16.45, 20.95, ["mengadu sesak nafas dan sakit dada dan nampak dia macam crying non stop",
                           "mengadu sesak nafas sakit dada dan nampak dia macam crying non stop",
                           "mengadu sesak nafas yang sakit dada dan nampak dia macam crying non stop"]),
    "I03": (20.95, 28.70, ["mak ayah dia pun nampak cemas kata doktor tolonglah anak kami dia rasa macam nak mati sangat sangat dia kata dada dia sakit sangat jadi"]),
    "I04": (28.80, 31.95, ["setelah remaja tersebut ditenangkan", "setelah remaja tersebut ditenangkan *"]),
    "I05": (32.00, 34.65, ["saya mulakan sesi soal jawab", "* saya mulakan sesi soal jawab"]),
    "I06": (34.70, 42.95, ["remaja tersebut ada beritahu yang dia sering rasa takut sejak beberapa bulan lepas dia ada baca di media sosial tentang gejala yang dialami"]),
    "I07": (42.95, 49.25, ["remaja itu yakin yang dia alami borderline personality disorder major depressive disorder dan ei di eic di",
                           "remaja itu * yakin yang dia alami borderline personality disorder major depressive disorder dan ei di eic di"]),
    "I08": (49.25, 53.45, ["tapi dia tak pernah jumpa doktor pun untuk dapatkan pandangan profesional sebaliknya",
                           "tapi dia tak pernah jumpa doktor pun untuk dapatkan nasihat profesional sebaliknya",
                           "tapi dia tak pernah jumpa doktor pun untuk dapatkan bantuan profesional sebaliknya",
                           "tapi dia tak pernah jumpa doktor pun untuk dapatkan diagnosis profesional sebaliknya",
                           "tapi dia tak pernah jumpa doktor pun untuk dapatkan rawatan profesional sebaliknya",
                           "tapi dia tak pernah jumpa doktor pun untuk dapatkan evaluasi profesional sebaliknya"]),
    "I09": (53.45, 62.90, ["dia self diagnose sendiri dan * cari solution sendiri termasuklah dia tak keluar rumah langsung mengelakkan diri daripada * socialise",
                           "dia self diagnose sendiri dan cari solution sendiri termasuklah dia tak keluar rumah langsung mengelakkan diri daripada socialise"]),
    "I10": (62.90, 71.30, ["dia juga ada try untuk ambil supplement yang ada jual dekat media sosial tapi sebenarnya tak ada perubahan yang positif pun yang berlaku",
                           "dia * juga ada try untuk ambil supplement yang * ada jual dekat media sosial tapi sebenarnya tak ada perubahan yang positif pun yang berlaku"]),
    "I11": (71.90, 86.70, ["jadi malam itu serangan yang dia alami itu semakin teruk dia rasa macam jantung dia nak meletup dan dia yakin yang dia akan mati lepas itu itulah sebab dia minta mak ayah dia bawa dia datang ke hospital",
                           "jadi malam itu * serangan yang dia alami itu semakin teruk dia rasa macam jantung dia nak meletup dan dia yakin yang dia akan mati lepas itu itulah sebab dia minta mak ayah dia bawa dia datang ke hospital"]),
    "I12": (95.40, 99.25, ["jadi selepas saya buat assessment", "jadi * selepas saya buat assessment"]),
    "I13": (99.30, 104.60, ["kita dapati yang remaja tersebut mengalami anxiety disorder yang sangat serius lah",
                            "kita dapatkan yang remaja tersebut mengalami anxiety disorder yang sangat serius lah"]),
    "I14": (105.00, 117.40, ["tapi dia tak pernah dapat bantuan yang sepatutnya sebab tindakan dia yang mengasingkan diri atau bergantung kepada maklumat yang tak sahih itu sebenarnya burukkan lagi keadaan",
                             "tapi dia tak pernah dapat bantuan * yang sepatutnya sebab * tindakan dia yang mengasingkan diri atau bergantung kepada maklumat yang tak sahih itu sebenarnya burukkan lagi keadaan"]),
    "I15": (123.00, 129.00, ["point dia kat sini adalah okay point dia kat sini adalah self diagnose sebenarnya sangat bahaya untuk kita"]),
    "I16": (129.05, 140.40, ["sebab baca symptom dekat internet ini tak sama dengan penilaian profesional dan dia boleh menyebabkan kita salah faham lah dan dapat salah faham",
                             "sebab baca symptom dekat internet ini tak sama dengan penilaian profesional dan * dia boleh menyebabkan kita salah faham lah dan * dapat * salah faham"]),
    "I17": (144.70, 151.00, ["dia boleh menyebabkan salah faham dan rawatan yang salah dekat diri kita",
                             "dia * boleh menyebabkan salah faham dan * rawatan yang salah dekat diri kita"]),
    "I18": (151.20, 159.30, ["sebab rawatan yang awal itu penting kalau remaja tersebut dapat rawatan awal dia boleh mengelakkan serangan panik yang lebih teruk sebenarnya"]),
    "I19": (163.90, 170.10, ["dan juga keluarga memainkan * yang penting", "dan * juga keluarga memainkan * yang * penting", "dan juga keluarga memainkan peranan yang penting"]),
    "I20": (170.10, 185.00, ["keluarga tersebut dia memainkan peranan yang besar sebenarnya adalah sokongan sokongan ibu bapa * bawa dia datang hospital adalah langkah penting sebenarnya dalam proses pemulihan dia jadi kesihatan mental adalah isu yang penting sebenarnya dan bantuan profesional",
                             "keluarga tersebut dia memainkan peranan yang besar sebenarnya adalah sokongan sokongan ibu bapa macam saya sebut bawa dia datang hospital adalah langkah penting sebenarnya dalam proses pemulihan dia jadi kesihatan mental adalah isu yang penting sebenarnya dan bantuan profesional",
                             "keluarga tersebut dia memainkan peranan yang besar sebenarnya adalah sokongan sokongan ibu bapa bagi saya sebut bawa dia datang hospital adalah langkah penting sebenarnya dalam proses pemulihan dia jadi kesihatan mental adalah isu yang penting sebenarnya dan bantuan profesional",
                             "keluarga tersebut dia memainkan peranan yang besar sebenarnya adalah sokongan sokongan ibu bapa seperti saya sebut bawa dia datang hospital adalah langkah penting sebenarnya dalam proses pemulihan dia jadi kesihatan mental adalah isu yang penting sebenarnya dan bantuan profesional"]),
    "I21": (185.20, 188.95, ["boleh buat perubahan yang besar kepada seseorang", "boleh * buat perubahan yang besar kepada seseorang", "boleh buat perubahan yang besar kepada seorang"]),
    "I22": (189.00, 198.50, ["jika anda atau orang terdekat mengalami gejala gejala seperti ini jangan takut untuk dapatkan bantuan yang sepatutnya apa apa soalan boleh tanya di ruangan komen jaga diri",
                             "jika anda atau orang terdekat mengalami gejala gejala seperti ini jangan takut untuk dapatkan bantuan yang sepatutnya apa apa soalan boleh tanya di kolom komentar jaga jaga",
                             "jika anda atau orang terdekat mengalami gejala gejala seperti ini jangan takut untuk dapatkan bantuan yang sepatutnya apa apa soalan boleh tanya di ruangan komen take care",
                             "jika anda atau orang terdekat mengalami gejala gejala seperti ini jangan takut untuk dapatkan bantuan yang sepatutnya apa apa soalan boleh tanya di kolum komen jaga diri",
                             "jika anda atau orang terdekat mengalami gejala gejala seperti ini jangan takut untuk dapatkan bantuan yang sepatutnya apa apa soalan boleh tanya di kolum komen take care"]),
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
