"""CTC forced alignment (torchaudio MMS_FA) of corrected Malay text per passage.

Same pattern as videos/ward-psikiatri/edit/align.py: Whisper word times drift, so cut edges come
from here. Each passage lists text hypotheses (from medium + unprompted large-v3); the
best-scoring one wins. '*' = unknown sound (hesitation, breath). Output: aligned.json
Only passages that touch the cut are listed (take-1 hook and the lithium false starts are dropped
whole, so their edges come from the neighbouring passages).
"""

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio

E = Path(__file__).parent
ISL = {  # passage id: (start, end, [hypotheses])
    "P01": (14.30, 23.25, ["sepuluh ubat psikiatri yang perlu berhati hati atau kalau boleh elakkanlah ketika anda pregnant ataupun ada plan nak pregnant"]),
    "P02": (23.30, 26.40, ["assalamualaikum saya doktor azren saya bukan doktor saya doktor psikiatri",
                           "assalamualaikum saya doktor azren saya doktor dan doktor psikiatri"]),
    "P03": (26.42, 29.30, ["assalamualaikum saya doktor azren saya doktor psikiatri",
                           "* assalamualaikum saya doktor azren saya doktor psikiatri"]),
    "P04": (33.50, 35.00, ["kalau anda", "kalau anda *", "kalau anda tengah"]),
    "P05": (36.40, 53.50, ["kalau anda tengah pregnant ataupun plan nak mengandung sebenarnya ada beberapa ubat psikiatri yang doktor akan sangat berhati hati kalau nak bagi sebab dia boleh bagi kesan dekat baby ubat yang pertama adalah sodium valproate ataupun epilim selalunya digunakan dalam kes sawan ataupun bipolar lah",
                           "kalau anda tengah pregnant ataupun plan nak mengandung sebenarnya ada beberapa ubat psikiatri yang doktor akan sangat berhati hati kalau nak bagi sebab dia boleh bagi kesan dekat baby ubat yang pertama adalah sodium valproate ataupun epilim selalunya digunakan dalam kes sawan ataupun bipolar * lah"]),
    "P06": (54.00, 66.40, ["ha ubat ni dia ada risiko tinggi boleh menyebabkan kecacatan otak dan juga sistem saraf bayi yang kedua adalah litium ha ni pun ubat untuk bipolar juga selalunya ubat ni risiko dia tinggi kalau ubat",
                           "uh ubat ni dia ada risiko tinggi boleh menyebabkan kecacatan otak dan juga sistem saraf bayi yang kedua adalah litium ha ni pun ubat untuk bipolar juga selalunya ubat ni risiko dia tinggi kalau ubat"]),
    "P07": (71.20, 78.90, ["ubat ni dia ada risiko untuk masalah jantung bayi dia boleh guna tapi dia kena monitor dengan tapi",
                           "ubat ni dia ada risiko untuk masalah jantung bayi dia boleh guna tapi dia kena monitor dengan * tapi"]),
    "P08": (80.35, 87.85, ["kena monitor betul betul kena ada pemantauan yang rapi oleh doktor lah ha yang ketiga adalah carbamazepine",
                           "kena monitor betul betul kena ada ada pemantauan yang rapi oleh doktor lah ha yang ketiga adalah carbamazepine",
                           "kena monitor betul betul kena ada * pemantauan yang rapi oleh doktor lah ha yang ketiga adalah carbamazepine"]),
    "P09": (88.30, 96.50, ["yang ketiga adalah carbamazepine ha ini pun ubat untuk bipolar dan kadang kadang digunakan untuk sawan juga ha ni ubat ada risiko ha",
                           "yang ketiga adalah carbamazepine ha ini pun ubat untuk bipolar dan kadang kadang digunakan untuk sawan juga ha ni ubat ada risiko"]),
    "P10": (97.35, 110.45, ["ubat ni dia ada risiko neural tube defect ha yang keempat adalah paroxetine ha paroxetine ni adalah antidepressant yang digunakan untuk depression dan juga anxiety ha dia dikaitkan dengan risiko kecacatan jantung bayi juga",
                            "ubat ni dia ada risiko neural tube defect ha yang keempat adalah paroxetine ha paroxetine ni adalah antidepressant dan digunakan untuk depression dan juga anxiety ha dia dikaitkan dengan risiko kecacatan jantung bayi juga",
                            "ha ubat ni dia ada risiko neural tube defect ha yang keempat adalah paroxetine ha paroxetine ni adalah antidepressant yang digunakan untuk depression dan juga anxiety ha dia dikaitkan dengan risiko kecacatan jantung bayi juga"]),
    "P11": (110.90, 132.30, ["yang kelima adalah alprazolam ataupun xanax selalunya digunakan dalam kes anxiety ataupun panic attack ubat ni dia ada risiko bayi boleh jadi lemah ataupun ada withdrawal effect selepas melahirkan bayi yang keenam adalah diazepam ataupun valium ubat ni dia bantu untuk anxiety muscle relax",
                             "yang kelima adalah alprazolam ataupun xanax selalunya digunakan dalam kes anxiety ataupun panic attack ubat ni dia ada risiko * bayi boleh jadi lemah ataupun ada withdrawal effect selepas melahirkan bayi yang keenam adalah diazepam ataupun valium ubat ni dia * bantu untuk anxiety muscle relax"]),
    "P12": (132.45, 147.20, ["dia muscle relaxant dan juga sawan ubat ni dia ada risiko baby floppy syndrome yang ketujuh adalah clonazepam clonazepam ni ubat digunakan untuk anxiety ataupun sawan dia ada risiko sedation kepada bayi",
                             "muscle relaxant dan juga sawan ubat ni dia ada risiko baby floppy syndrome yang ketujuh adalah clonazepam clonazepam ni ubat digunakan untuk anxiety ataupun sawan dia ada risiko sedation kepada bayi",
                             "dia muscle relaxation dan juga sawan ubat ni dia ada risiko baby floppy syndrome yang ketujuh adalah clonazepam clonazepam ni ubat digunakan untuk anxiety ataupun sawan dia ada risiko sedation kepada bayi"]),
    "P13": (147.40, 155.50, ["yang kelapan adalah topiramate topiramate ni adalah sejenis mood stabilizer * dan kadang kadang digunakan dalam kes migraine juga",
                             "yang ke lapan adalah topiramate topiramate ni adalah sejenis mood stabilizer * dan kadang kadang digunakan dalam kes migraine juga",
                             "yang kelapan adalah topiramate topiramate ni adalah sejenis mood stabilizer dan kadang kadang digunakan dalam kes migraine juga"]),
    "P14": (155.50, 170.20, ["ubat ni dia ada risiko cleft lip dan juga cleft palate kepada bayi yang kesembilan adalah risperidone ubat ni digunakan dalam kes seperti skizofrenia bipolar ataupun aggression dia ada risiko hormonal dan metabolik effect kepada baby"]),
    "P15": (170.90, 189.35, ["perlu dia bukan tak boleh bagi boleh tapi kena monitor betul betul oleh kena ada pemantauan rapi oleh doktor yang kesepuluh adalah olanzapine olanzapine ni ubat untuk skizofrenia dan juga bipolar lah dia ada risiko berat bayi jadi besar dan juga masalah metabolik side effect kepada bayi itu",
                             "dia bukan tak boleh bagi boleh tapi kena monitor betul betul oleh kena ada pemantauan rapi oleh doktor yang kesepuluh adalah olanzapine olanzapine ni ubat untuk skizofrenia dan juga bipolar lah dia ada risiko berat bayi jadi besar dan juga masalah metabolik side effect kepada bayi itu"]),
    "P16": (189.45, 207.20, ["ha jadi ubat yang saya senarai ni bukan tak boleh tapi tapi ubat ubat yang saya senarai ni bukanlah kata seratus peratus tak boleh ha tapi kena betul betul kena betul betul kena betul betul",
                             "ha jadi ubat yang saya senarai ni bukan tak boleh tapi bukan yang saya senarai ubat yang ubat yang saya senarai ni bukanlah kata seratus peratus tak boleh ha tapi kena betul betul kena betul betul kena betul betul",
                             "ha jadi ubat yang saya senarai ni bukan tak boleh tapi * ubat yang ubat yang saya senarai ni bukanlah kata seratus peratus tak boleh ha tapi kena betul betul kena betul betul kena betul betul"]),
    "P17": (208.60, 227.15, ["kalau anda ada ambik kalau ada anda ada ambik kalau anda ada ambik sepuluh ubat yang saya sebut tadi itu dan anda ada plan nak pregnant ataupun tengah pregnant kena beritahu dekat doktor supaya pemantauan rapi dapat dilakukanlah apa apa soalan boleh tanya di ruangan komen",
                             "kalau anda ada ambik kalau ada anda ada ambik kalau anda ada ambik sepuluh ubat yang saya sebut tadi tu dan anda ada plan nak pregnant ataupun tengah pregnant kena bagitahu dekat doktor supaya pemantauan rapi dapat dilakukanlah apa apa soalan boleh tanya di ruangan komen",
                             "kalau anda ada ambik kalau ada anda ada ambik kalau anda ada ambik sepuluh ubat yang saya sebut tadi itu dan anda ada plan nak pregnant ataupun tengah pregnant kena beritahu dekat doktor supaya pemantauan rapi dapat dilakukanlah apa apa soalan boleh tanya di kolum komen",
                             "kalau anda ada ambik kalau ada anda ada ambik kalau anda ada ambik sepuluh ubat yang saya sebut tadi itu dan anda ada plan nak pregnant ataupun tengah pregnant kena beritahu dekat doktor supaya pemantauan rapi dapat dilakukanlah apa apa soalan boleh tanya dekat komen"]),
}


def main() -> None:
    only = set(sys.argv[1:])  # optional: re-align just these passages, merging into aligned.json
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
        alts = "" if len(hyps) == 1 else f"  picked {hyps.index(h) + 1}/{len(hyps)} {scores}"
        print(f"{iid} score={score:.3f}{alts}")
    out = dict(sorted(out.items(), key=lambda kv: kv[1]["words"][0]["start"]))
    (E / "aligned.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
