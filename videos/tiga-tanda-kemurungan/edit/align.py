"""CTC forced alignment (torchaudio MMS_FA) of corrected Malay text per speech island.

Template: videos/ward-psikiatri/edit/align.py. Islands come from envelope.py's silence map;
text from faster-whisper medium + an unprompted large-v3 pass (captions_src/large_v3.json).
Each island lists one or more text hypotheses; the best-scoring one wins.
'*' = unknown sound (breath, hesitation "aa"/"mmm", unclear syllable). Output: aligned.json
"""

import json
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio

E = Path(__file__).parent
ISL = {  # island id: (start, end, [hypotheses])
    "I00": (0.45, 4.80, ["kalau tiga tanda tanda yang saya sebut ni ada pada anda",
                         "* kalau tiga tanda tanda yang saya sebut ni ada pada anda"]),
    "I01": (4.95, 10.65, ["ini mungkin bukan penat yang biasa ini mungkin tanda kemurungan yang ramai orang tak perasan"]),
    "I02": (10.70, 29.35, [
        "yang nombor tiga tu yang paling common sebenarnya nombor satu adalah bangun lewat dan selalu skip breakfast ha dia bukan selalu skip breakfast sebab nak diet ke apa dia skip breakfast sebab dah tak ada perasaan nak makan ha bukan sebab malas ke tapi badan dah rasa berat minda tu dah rasa kosong nak bangun pun dah tak ada tenaga dah",
        "yang nombor tiga tu yang paling common sebenarnya nombor satu adalah bangun lewat dan selalu skip breakfast dia bukan selalu skip breakfast sebab nak diet ke apa dia skip breakfast sebab dah tak ada perasaan nak makan bukan sebab malas ke tapi badan dah rasa berat minda tu dah rasa kosong nak bangun pun dah tak ada tenaga dah",
        "yang nombor tiga tu yang paling common sebenarnya nombor satu adalah bangun lewat dan selalu skip breakfast ha dia bukan selalu skip breakfast sebab nak diet tu apa dia skip breakfast sebab dah tak ada perasaan nak makan ha bukan sebab malas ke tapi badan dah rasa berat minda tu dah rasa kosong nak bangun pun dah tak ada tenaga dah",
        "yang nombor tiga tu yang paling common sebenarnya * nombor satu adalah * bangun lewat dan selalu skip breakfast ha dia bukan selalu skip breakfast sebab nak diet ke apa dia skip breakfast sebab dah tak ada perasaan nak makan ha bukan sebab malas ke tapi badan dah rasa berat minda tu dah rasa kosong nak bangun pun dah tak ada tenaga dah",
    ]),
    "I03": (29.35, 40.15, [
        "yang kedua benda yang dulu seronok tapi sekarang dah tak rasa apa apa dah kalau macam dulu suka main game tengok drama ke makan kat luar ke lepak lepak sekarang ni semua tu dah rasa kosong dah",
        "yang kedua * benda yang dulu seronok tapi sekarang dah tak rasa apa apa dah kalau macam dulu suka main game tengok drama ke makan kat luar ke lepak lepak sekarang ni semua tu dah rasa kosong dah",
    ]),
    "I04": (40.15, 47.90, [
        "yang ni yang kita panggil sebagai anhedonia hilang minat terhadap perkara yang sebelum ni pernah menggembirakan anda",
        "yang ni yang kita panggil sebagai anhidonia hilang minat terhadap perkara yang sebelum ni pernah menggembirakan anda",
        "yang ni yang kita panggil sebagai anhedonia * hilang minat terhadap perkara yang sebelum ni pernah menggembirakan anda",
    ]),
    "I05": (48.15, 49.25, ["iklan"]),
    # 49.4-51.0 is a false start "kalau anda rasa" (large-v3 on the snippet); the take restarts at 52.2
    "I06": (49.25, 65.20, [
        "kalau anda rasa kalau anda rasa * banyak * tanda tanda ni berlaku pada diri sendiri anda boleh datang ke klinik saya di nilai kita buat konsultasi dan saringan kesihatan mental saya akan buat penilaian yang lengkap dan kita * bincangkan rawatan apa yang sesuai untuk anda",
        "kalau anda rasa * kalau anda rasa * banyak * tanda tanda ni berlaku pada diri sendiri anda boleh datang ke klinik saya di nilai kita buat konsultasi dan saringan kesihatan mental saya akan buat penilaian yang lengkap dan kita * bincangkan rawatan apa yang sesuai untuk anda",
        "kalau anda rasa * kalau anda rasa * banyak * tanda tanda ni berlaku pada diri sendiri anda boleh datang ke klinik saya dinilai kita buat konsultasi dan saringan kesihatan mental saya akan buat penilaian yang lengkap dan kita * bincangkan rawatan apa yang sesuai untuk anda",
    ]),
    "I07": (65.20, 67.70, ["okey kita sambung nombor tiga", "okey kita sambung nombor tiga *"]),
    "I08": (68.85, 71.80, ["bangun okey kita sambung", "* bangun okey kita sambung"]),
    "I09": (72.20, 77.75, ["okey kita sambung bila bangun pagi benda pertama yang kita capai adalah telefon",
                           "okey kita sambung bila bangun pagi * benda pertama yang kita capai adalah telefon"]),
    "I10": (77.75, 88.70, [
        "sebenarnya bukan nak scroll pun kadang kadang cuma nak lari daripada realiti nak cari distraction disebabkan hati tak stabil hati ataupun mood yang tak stabil tu",
        "sebenarnya bukan nak scroll pun kadang kadang cuma nak lari daripada realiti nak nak cari distraction disebabkan hati tak stabil hati ataupun mood yang tak stabil tu",
        "sebenarnya bukan nak scroll pun kadang kadang cuma nak lari daripada realiti nak cari distraction disebabkan hati * tak stabil hati ataupun mood yang tak stabil tu",
        "sebenarnya bukan nak scroll pun kadang kadang cuma nak lari daripada realiti nak nak cari distraction disebabkan hati * tak stabil hati ataupun mood yang tak stabil tu",
    ]),
    "I11": (88.70, 91.60, ["yang keempat mood swing yang teruk", "yang keempat * mood swing yang teruk"]),
    "I12": (91.60, 94.30, ["bukan macam apa panggil", "bukan macam * apa panggil"]),
    "I13": (96.30, 106.35, [
        "mood swing yang teruk kejap pagi rasa okey tengah hari rasa murung malam macam rasa macam nak menangis emosi tu naik turun tanpa sebab yang jelas",
        "mood swing yang teruk kejap pagi rasa okey * tengah hari rasa murung * malam macam rasa macam nak menangis emosi tu naik turun tanpa sebab yang jelas",
    ]),
    "I14": (106.35, 109.65, ["yang kelima mudah lupa dan susah fokus", "yang kelima * mudah lupa dan susah fokus"]),
    "I15": (109.70, 114.95, ["baca satu benda sampai tiga kali pun tak boleh nak ingat otak jadi serabut",
                             "baca satu benda sampai tiga kali tak boleh nak ingat otak jadi serabut",
                             "baca satu benda sampai tiga kali pun tak boleh nak ingat otak * jadi serabut"]),
    "I16": (115.00, 116.60, ["atau orang", "atau orang *"]),
    "I17": (116.60, 118.65, ["otak jadi serabut", "otak * jadi serabut"]),
    "I18": (118.70, 121.80, ["atau kita panggil sebagai brain fog", "atau * kita panggil sebagai brain fog"]),
    "I19": (122.30, 126.65, ["nombor enam rasa penat dan cepat marah sepanjang masa",
                             "nombor * enam rasa penat dan cepat marah sepanjang masa"]),
    "I20": (126.65, 141.00, [
        "letih tapi bukan letih fizikal dia letih dalam kepala benda kecil pun membuatkan kita rasa frustrated kalau tanda tanda ni makin kerap jangan biarkan ianya melarat kesihatan mental ni sebenarnya sama penting dengan kesihatan fizikal",
        "letih tapi bukan letih fizikal letih dalam kepala benda kecil pun membuatkan kita rasa frustrated kalau tanda tanda ni makin kerap jangan biarkan ianya melarat kesihatan mental ni sebenarnya sama penting dengan kesihatan fizikal",
    ]),
    "I21": (140.95, 142.90, ["kalau perlukan bantuan"]),
    "I22": (147.70, 154.45, ["untuk mendapatkan konsultasi dan saringan kesihatan mental bersama saya doktor azren boleh klik di bio",
                             "untuk mendapatkan konsultasi dan saringan kesihatan mental bersama saya doktor azren * boleh klik di bio"]),
    # large-v3 on the snippet: "apa persoalan boleh tanya di dalam komen take care"
    "I23": (157.90, 160.26, ["apa persoalan boleh tanya di dalam komen take care",
                             "apa apa persoalan boleh tanya di dalam komen take care",
                             "apa persoalan boleh tanya dalam komen take care",
                             "apa persoalan boleh tanya di ruangan komen take care"]),
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
        best, scores = None, []
        for h in hyps:
            words = h.split()
            spans = aligner(emission[0], tokenizer(words))
            score = float(np.mean([s.score for ws in spans for s in ws]))
            scores.append(round(score, 3))
            if best is None or score > best[0]:
                best = (score, h, words, spans)
        score, h, words, spans = best
        out[iid] = {
            "hyp": h, "score": round(score, 3),
            "words": [{"text": w, "start": round(a + ws[0].start * ratio, 3), "end": round(a + ws[-1].end * ratio, 3),
                       "score": round(float(np.mean([s.score for s in ws])), 3)} for w, ws in zip(words, spans)],
        }
        alts = "" if len(hyps) == 1 else f"  (picked {hyps.index(h) + 1}/{len(hyps)}: {scores})"
        print(f"{iid} score={score:.3f}{alts}")
    out = dict(sorted(out.items(), key=lambda kv: kv[1]["words"][0]["start"]))
    (E / "aligned.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
