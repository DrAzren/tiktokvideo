"""CTC forced alignment (torchaudio MMS_FA) of corrected Malay text per speech island.

Whisper word times drift (large-v3 glues 82-137s into one run), so cut edges come from here.
Each island lists one or more text hypotheses; the best-scoring one wins.
'*' = unknown sound (breath, "eee", lip smack). Spellings are phonetic where MMS needs it
(captions get the display spelling in captions/build_transcript.py).
Islands are split at real energy dips (envelope.py); first plug take (16.9-29.5s) is not aligned:
it is replaced by the complete retake at 35.3s.
Output: aligned.json
"""

import json
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio

E = Path(__file__).parent
ISL = {  # island id: (start, end, [hypotheses])
    "I00": (0.05, 3.45, ["pernah dengar nama ubat olanzapin", "* pernah dengar nama ubat olanzapin"]),
    # "patient" in Manglish ("pe-syen"): pesyen 0.772 > pasien 0.760 > pesakit 0.663 (isolated large-v3 said "pesakit")
    "I01": (3.45, 5.45, ["ada pesyen panggil *", "ada pasien panggil *", "ada pesakit panggil *"]),
    "I02": (9.20, 14.64, ["jom saya terangkan apa sebenarnya kebaikan dan keburukan ubat ni",
                          "* jom saya terangkan apa sebenarnya kebaikan dan keburukan ubat ni"]),
    "I04": (34.40, 52.38, [
        "tapi jangan risau kalau anda ada mula ambil ubat psikiatri tapi risau pasal kesan sampingan atau nak dapatkan khidmat nasihat tentang kesihatan mental di klinik saya di nilai kami ada buat konsultasi dan saringan kesihatan mental secara wan on wan boleh tekan di bio untuk buk slot anda",
        "* tapi jangan risau kalau anda ada mula ambil ubat psikiatri tapi risau pasal kesan sampingan atau nak dapatkan khidmat nasihat tentang kesihatan mental di klinik saya di nilai kami ada buat * konsultasi dan saringan kesihatan mental secara wan on wan boleh tekan di bio untuk buk slot anda",
        "* tapi jangan risau kalau anda dah mula ambil ubat psikiatri tapi risau pasal kesan sampingan atau nak dapatkan khidmat nasihat tentang kesihatan mental di klinik saya di nilai kami ada buat * konsultasi dan saringan kesihatan mental secara wan on wan boleh tekan di bio untuk buk slot anda",
        "* tapi jangan risau kalau anda ada mula ambil ubat psikiatri tapi risau pasal kesan sampingan atau nak dapatkan khidmat nasihat tentang kesihatan mental di klinik saya di nilai kami ada buat aa konsultasi dan saringan kesihatan mental secara wan on wan boleh tekan di bio untuk buk slot anda"]),
    "I05": (52.38, 64.86, [
        "pertama kebaikan ubat olanzapin ni ubat olanzapin ni memang sangat bagus sebenarnya tidak dinafikan kerana ia boleh stabilkan mood sesuai untuk pesakit yang mengalami bipolar skizofrenia ataupun gangguan psikosis",
        "* pertama kebaikan ubat olanzapin ni ubat olanzapin ni memang sangat bagus sebenarnya tidak dinafikan kerana ia boleh stabilkan mood sesuai untuk pesakit yang mengalami bipolar skizofrenia ataupun gangguan psikosis",
        "pertama kebaikan ubat olanzapin ini ubat olanzapin ini memang sangat bagus sebenarnya tidak dinafikan kerana ia boleh stabilkan mood sesuai untuk pesakit yang mengalami bipolar skizofrenia ataupun gangguan psikosis"]),
    "I06": (64.86, 74.90, [
        "ia boleh kurangkan halusinasi delusi boleh bantu otak seseorang itu jadi lebih tenang dan boleh meningkatkan selera dan juga tidur seseorang",
        "dia boleh kurangkan halusinasi delusi boleh bantu otak seseorang itu jadi lebih tenang dan boleh meningkatkan selera dan juga tidur seseorang",
        "ia boleh kurangkan halusinasi dilusi boleh bantu otak seseorang itu jadi lebih tenang dan boleh meningkatkan selera dan juga tidur seseorang"]),
    "I07": (74.90, 81.84, [
        "ia berguna lah kalau pesakit yang terlalu cemas sampai hilang nafsu makan ataupun insomnia",
        "dia berguna lah kalau pesakit yang terlalu cemas sampai hilang nafsu makan ataupun insomnia",
        "* ia berguna lah kalau pesakit yang terlalu cemas sampai hilang nafsu makan ataupun insomnia"]),
    # I08 runs to 91.4 so the hesitation after "ubat ni" (86.71-87.11) and "ubat ini" are aligned in one pass
    # (split islands put "ni" at 87.62 and scored 'sebenarnya ubat ni sangat bagus' < 0.5)
    "I08": (81.84, 91.10, ["ada juga yang cakap dunia dia dah kembali senyap bila makan ubat ni * sebenarnya ubat ini sangat bagus untuk penyakit penyakit tertentu",
                           "* ada juga yang cakap dunia dia dah kembali senyap bila makan ubat ni * sebenarnya ubat ini sangat bagus untuk penyakit penyakit tertentu",
                           "* ada juga yang cakap dunia dia dah kembali senyap bila makan ubat ni * sebenarnya ubat ni sangat bagus untuk penyakit penyakit yang tertentu"]),
    "I09": (91.10, 110.65, [
        "tapi kita kena tahu juga kesan sampingan ubat ni seperti kenaikan berat badan sebab ini antara yang paling komen lah kadang kadang naik pelan pelan kadang kadang naik drastik jadi apa yang saya bagi tahu selalunya kita kena amalkan pemakanan yang seimbang lah kesan sampingan yang lain seperti mengantuk terutamanya masa awal awal start rawatan dulu",
        "tapi kita kena tahu juga kesan sampingan ubat ni seperti kenaikan berat badan sebab ini antara yang paling komen lah kadang kadang naik pelan pelan kadang kadang naik drastik jadi apa yang saya bagi tahu selalunya kita kena amalkan pemakanannya seimbang lah kesan sampingan yang lain seperti mengantuk terutamanya masa awal awal start rawatan dulu"]),
    "I10": (110.65, 123.40, [
        "yang ketiga boleh mengakibatkan metabolik said efek risiko kenaikan kolesterol gula dan tekanan darah sebab itulah doktor akan pantau darah berat badan kalau anda ada ambil ubat olanzapin ni",
        "yang ketiga boleh mengakibatkan metabolik said efek risiko kenaikan kolesterol gula dan tekanan darah sebab itulah doktor akan pantau darah berat badan kalau anda ada ambil ubat olanzapin ni *"]),
    "I11": (128.16, 138.20, [
        "yang penting kita jangan stop ubat sendiri jangan give up kalau anda perlukan bantuan boleh",
        "* yang penting kita jangan stop ubat sendiri jangan giv ap kalau anda perlukan bantuan boleh",
        "yang penting kita jangan stop ubat sendiri jangan giv ap kalau anda perlukan bantuan boleh *"]),
    "I12": (138.20, 141.90, ["boleh tekan di bio atau di em untuk buat appointment",
                             "boleh tekan di bio atau di em untuk buat apointmen"]),
    # noisy: large-v3 hears "apa-apa ... di dalam" but alignment prefers the shorter reading (0.601 vs 0.513)
    "I13": (142.30, 145.85, ["kalau ada soalan boleh tanya dalam komen tek ker",
                             "kalau ada apa apa soalan boleh tanya di dalam komen tek ker",
                             "kalau ada apa apa soalan boleh tanya dalam komen tek ker"]),
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
