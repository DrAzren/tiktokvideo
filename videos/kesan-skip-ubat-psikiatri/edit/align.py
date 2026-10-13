"""CTC forced alignment (torchaudio MMS_FA) of corrected Malay text per speech island.
Template: videos/ubat-psikiatri-olanzapine/edit/align.py.

Whisper word times drift, so cut edges come from here. Each island lists one or more text
hypotheses; the best-scoring one wins. '*' = unknown sound (breath, "eee", lip smack).
Spellings are phonetic where MMS needs it (captions get the display spelling in
captions/build_transcript.py). Island edges sit on energy minima (envelope.py).
The source is a CapCut export (several clips already joined, some mirrored); the silent
"listening" shots between takes (4-9 s, 18.6-22.8 s, 46-48.5 s) are not aligned.
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
    "I00": (1.26, 4.03, ["assalamualaikum saya doktor azren saya doktor psikiatri *",
                         "asalamualaikum saya doktor azren saya doktor psikiatri *",
                         "assalamualaikum saya doktor azren saya doktor saikiatri *"]),
    "I01": (8.66, 14.83, ["doktor saya dah sihat sikit saya nak berhenti ubat sendiri tak apa ke doktor",
                          "* doktor saya dah sihat sikit saya nak berhenti ubat sendiri tak apa ke doktor",
                          "doktor saya dah sihat sikit saya nak berhenti ubat sendiri takpe ke doktor"]),
    "I02": (14.83, 15.97, ["*", "tengok", "okey"]),
    "I03": (15.97, 18.28, ["saya ada berita baik", "* saya ada berita baik", "saya ada berita baik *"]),
    "I04": (22.45, 45.89, [
        "sebelum tu saya ada berita baik di klinik saya di nilai kami ada menyediakan servis konsultasi dan juga saringan kesihatan mental secara wan on wan boleh bincang tentang isu kemurungan ke angzaieti ke masalah tidur dan lain lain lagi lah nak start rawatan ataupun nak dapatkan sekan opinion sebelum ambil ubat nak tentukan diagnosis boleh datang klinik saya di nilai",
        "* sebelum tu saya ada berita baik di klinik saya di nilai kami ada menyediakan servis konsultasi dan juga saringan kesihatan mental secara wan on wan boleh bincang tentang isu kemurungan ke angzaieti ke masalah tidur dan lain lain lagi lah nak start rawatan ataupun nak dapatkan sekan opinion sebelum main berubat nak tentukan diagnosis boleh datang klinik saya di nilai",
        "* sebelum tu saya ada berita baik di klinik saya di nilai kami ada menyediakan servis konsultasi dan juga saringan kesihatan mental secara wan on wan boleh bincang tentang isu kemurungan ke angzaieti ke masalah tidur dan lain lain lagi lah nak start rawatan ataupun nak dapatkan sekan opinion sebelum ambil ubat nak tentukan diagnosis boleh datang klinik saya di nilai",
        "* sebelum tu saya ada berita baik di klinik saya di nilai kami ada menyediakan servis konsultasi dan juga saringan kesihatan mental secara wan on wan boleh bincang tentang isu kemurungan ke angzaieti ke masalah tidur dan lain lain lagi lah nak start rawatan ataupun nak dapatkan sekan opinion sebelum mula berubat nak tentukan diagnosis boleh datang klinik saya di nilai"]),
    "I05": (48.57, 57.02, [
        "okey berbalik kepada topik tadi jom kita sembang sekejap apa jadi kalau kita skip ubat psikiatri tanpa bincang dengan doktor",
        "ok berbalik kepada topik tadi jom kita sembang sekejap apa jadi kalau kita skip ubat psikiatri tanpa bincang dengan doktor",
        "* okey berbalik kepada topik tadi jom kita sembang sekejap apa jadi kalau kita skip ubat psikiatri tanpa bincang dengan doktor"]),
    "I06": (57.02, 69.27, [
        "yang pertama adalah risiko rilaps gejala berulang berlaku semula ubat psikiatri ni dia macam pelindung untuk kita jadi bila kita stop tiba tiba otak kita boleh jadi tak stabil semula",
        "yang pertama adalah risiko rilaps gejala berulang berlaku semula ubat psikiatri ini dia macam pelindung untuk kita jadi bila kita stop tiba tiba otak kita boleh jadi tak stabil semula",
        "yang pertama adalah risiko rilaps * gejala berulang berlaku semula * ubat psikiatri ni dia macam pelindung untuk kita jadi bila kita stop tiba tiba otak kita boleh jadi tak stabil semula"]),
    "I07": (69.27, 77.98, [
        "contohnya dia boleh dapat mud swing balik dia rasa cemas dia semakin menjadi jadi atau boleh sampai tahap boleh masuk wad balik",
        "contohnya dia boleh dapat mud swing balik dia rasa cemas dia semakin menjadi jadi * atau boleh sampai tahap boleh masuk wad balik",
        "* contohnya dia boleh dapat mud swing balik dia rasa cemas dia semakin menjadi jadi atau boleh sampai tahap boleh masuk wad balik"]),
    "I08": (77.98, 81.84, ["yang kedua adalah widdrowal simptom gejala penarikan",
                           "yang kedua adalah widdrowal simptom gejala penaikan",
                           "yang kedua adalah widdrowal simptom * gejala penarikan"]),
    "I09": (81.84, 96.62, [
        "bukan semua tapi ada ubat bila berhenti secara mengejut dia boleh dapat simptom simptom seperti rasa loya pening kepala gangguan tidur rasa macam emosi huru hara otak jadi serabut dan lain lain lagi lah",
        "* bukan semua tapi ada ubat bila berhenti secara mengejut dia boleh dapat simptom simptom seperti rasa loya pening kepala gangguan tidur rasa macam emosi huru hara otak jadi serabut dan lain lain lagi lah",
        "* bukan semua tapi ada ubat bila berhenti secara mengejut * dia boleh dapat simptom simptom seperti rasa loya pening kepala gangguan tidur * rasa macam emosi huru hara otak jadi serabut dan lain lain lagi lah"]),
    "I10": (96.62, 107.53, [
        "yang ketiga dia boleh merosakkan proses rawatan bila setiap kali stop start ubat stop start stop start dia macam kita umpamanya tekan riset baten balik",
        "* yang ketiga dia boleh merosakkan proses rawatan bila setiap kali stop start ubat stop start stop start dia macam kita umpamanya tekan riset baten balik",
        "yang ketiga dia boleh merosakkan proses rawatan * bila setiap kali stop start ubat stop start stop start * dia macam kita umpamanya tekan riset baten balik"]),
    "I11": (107.53, 114.41, [
        "jadi lambat sembuhnya kena mula balik daripada bawah dan kadang kadang ubat tu dah jadi tak efektif macam dulu lagi",
        "jadi lambat sembuhnya kena mula balik daripada bawah dan kadang kadang ubat itu dah jadi tak efektif macam dulu lagi",
        "jadi lambat sembuhnya kena mula balik daripada bawah * dan kadang kadang ubat tu dah jadi tak efektif macam dulu lagi"]),
    "I12": (114.41, 129.10, [
        "dan kalau anda sendiri tengah keliru patut teruskan rawatan ataupun tidak atau rasa macam nak mulakan rawatan tapi tak pasti boleh jumpa dengan profesional kesihatan mental atau boleh datang klinik saya di nilai tek ker",
        "dan kalau anda sendiri tengah keliru patut teruskan rawatan ataupun tidak * atau rasa macam nak mulakan rawatan tapi tak pasti * boleh jumpa dengan profesional kesihatan mental atau boleh datang klinik saya di nilai * tek ker",
        "* dan kalau anda sendiri tengah keliru patut teruskan rawatan ataupun tidak atau rasa macam nak mulakan rawatan tapi tak pasti boleh jumpa dengan profesional kesihatan mental atau boleh datang klinik saya di nilai tek ker *"]),
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
