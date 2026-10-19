"""CTC forced alignment (torchaudio MMS_FA) of corrected Malay text per speech island.

Whisper word times drift up to ~1s on this clip, so cut edges come from here instead.
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
ISL = {  # island id: (start, end, [hypotheses]); spellings are phonetic for the MMS romanizer
    "I00": (0.00, 8.40, ["badan penat mata dah terpejam pejam dah tapi otak still busy pusing pusing pada pukul tiga pagi pernah tak",
                         "badan penat mata dah terpejam pejam lah tapi otak still busy pusing pusing pada pukul tiga pagi pernah tak"]),
    # 8.4-12.1: breath/handling noise only (unprompted large-v3 hallucinates "terima kasih kerana menonton")
    "I04": (12.10, 33.05, ["pernah tak dengar ubat nama dia dayvigo apa itu dayvigo dayvigo ni adalah ubat tidur generasi baru dia bukan di bawah kelas benzodiazepin macam alprazolam clonazepam tu dia bukan ubat untuk buat kita pengsan ke apa ubat ni adalah daripada kumpulan orexin receptor antagonist bahasa senang dia ubat ni function dia untuk",
                           "pernah tak dengar ubat nama dia devigo apa itu devigo devigo ni adalah ubat tidur generasi baru dia bukan di bawah kelas benzodiazepin macam aprazolam klonazepam tu dia bukan ubat untuk buat kita pengsan ke apa ubat ni adalah daripada kumpulan orexin reseptor antagonis ni bahasa senang dia ubat ni function dia untuk",
                           "pernah tak dengar ubat nama dia devigo apa itu devigo devigo ni adalah ubat tidur generasi baru dia bukan di bawah kelas benzodiazepin macam aprazolam klonazepam tu dia bukan ubat untuk buat kita pengsan ke apa ubat ni adalah daripada kumpulan orexin reseptor antagonis bahasa senang dia ubat ni function dia untuk"]),
    "I05": (33.55, 43.98, ["dalam bahasa senang dia ubat ni function dia untuk switch off butang jaga dalam otak kita tu dia tak paksa tidur pun sebenarnya",
                           "* dalam bahasa senang dia ubat ni function dia untuk switch off butang jaga dalam otak kita tu dia tak paksa tidur pun sebenarnya"]),
    "I07": (44.85, 78.15, ["* antara fungsi utama ubat devigo ni adalah untuk rawat insomnia dia untuk kes susah nak tidur mudah terjaga pada waktu malam tidur tak lena terutamanya insomnia yang berkait dengan anxiety dan juga overthinking kelebihan devigo ni tidur tu rasa lebih natural kurang ketagihan berbanding dengan ubat benzodiazepin dia kurang hangover effect juga pada waktu pagi dan boleh kekalkan tidur dengan lebih lama tapi of course setiap ubat pun ada kesan sampingan dia antara contohnya ubat ni dia boleh mengantuk pada",
                           "antara fungsi utama ubat devigo ni adalah untuk rawat insomnia dia untuk kes susah nak tidur mudah terjaga pada waktu malam tidur tak lena terutamanya insomnia yang berkait dengan anxiety dan juga overthinking kelebihan devigo ni tidur tu rasa lebih natural kurang ketagihan berbanding dengan ubat benzodiazepin dia kurang hangover effect juga pada waktu pagi dan boleh kekalkan tidur dengan lebih lama tapi of course setiap ubat pun ada kesan sampingan dia antara contohnya ubat ni dia boleh mengantuk pada",
                           "* antara fungsi utama ubat devigo ni adalah untuk rawat insomnia dia untuk kes susah nak tidur mudah terjaga pada waktu malam tidur tak lena terutamanya insomnia yang berkait dengan anxiety dan juga overthinking kelebihan devigo ni tidur tu rasa lebih natural kurang ketagihan berbanding dengan ubat benzodiazepin dia kurang hangover effect juga pada waktu pagi dan boleh kekalkan tidur dengan lebih lama tapi of course setiap ubat pun ada kesan sampingan dia contohnya ubat ni dia boleh mengantuk pada"]),
    "I08": (79.75, 106.00, ["macam ubat ni dia boleh menyebabkan mengantuk pada siang hari terutamanya pada awal pengambilan ubat ni boleh menyebabkan mimpi pelik pelik rasa lemah sementara tapi ni sebenarnya ringan je dan dikawal dengan dos yang sesuai lah devigo ni dia bukan untuk semua orang tak sesuai kalau masih perlu jaga malam contohnya macam kerja kena kerja shift malam ke tak sesuai dia perlu ambil ikut arahan doktor dan elakkan alkohol kalau ambil ubat ni",
                            "macam ubat ni dia boleh menyebabkan mengantuk pada siang hari terutamanya pada awal pengambilan ubat ni boleh melibatkan mimpi pelik pelik rasa lemah sementara tapi ni sebenarnya ringan je dah dikawal dengan dos yang sesuai lah devigo ni dia bukan untuk semua orang tak sesuai kalau masih perlu jaga malam contohnya macam kerja kena kerja shift malam ke tak sesuai dia perlu ambil ikut arahan doktor dan elakkan alkohol kalau ambil ubat ni",
                            "macam ubat ni dia boleh menyebabkan mengantuk pada siang hari terutamanya pada awal pengambilan ubat ni boleh menyebabkan mimpi pelik pelik rasa lemah sementara tapi ni sebenarnya ringan je dan boleh dikawal dengan dos yang sesuai lah devigo ni dia bukan untuk semua orang tak sesuai kalau masih perlu jaga malam contohnya macam kerja kena kerja shift malam ke tak sesuai dia perlu ambil ikut arahan doktor dan elakkan alkohol kalau ambil ubat ni"]),
    "I10": (106.85, 122.65, ["kalau insomnia dah lama sangat sampai kacau emosi kerja kesihatan mental jangan tunggu lagi tidur yang terganggu boleh menyebabkan otak jadi rosak boleh buat penilaian daripada profesional kesihatan mental untuk cari punca sebenar",
                             "kalau insomnia dah lama sangat sampai kacau emosi kerja kesihatan jangan tunggu lagi tidur yang terganggu boleh menyebabkan otak jadi rosak boleh buat penilaian daripada profesional kesihatan mental untuk cari punca sebenar"]),
    "I11": (123.35, 125.35, ["ataupun boleh datang di klinik saya"]),
    "I12": (126.15, 132.60, ["ataupun boleh buat saringan dan konsultasi kesihatan mental bersama saya doktor azren di klinik saya di nilai apa apa soalan boleh tanya di komen take care",
                             "ataupun boleh buat saringan dan konsultasi kesihatan mental bersama saya doktor azren di klinik saya di nilai apa soalan boleh tanya di komen take care",
                             "ataupun boleh buat saringan dan konsultasi kesihatan mental bersama saya doktor azren di klinik saya di nilai apa apa soalan boleh tanya di komen tekeh"]),
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
