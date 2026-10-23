"""CTC forced alignment (torchaudio MMS_FA) of corrected Malay text per speech island.

Whisper word times drift on this clip, so cut edges come from here instead.
Each island lists one or more text hypotheses; the best-scoring one wins.
'*' = unknown sound (breath, click, unclear syllable). Output: aligned.json
"""

import itertools
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio

E = Path(__file__).parent


def variants(template: str) -> list[str]:
    """'a {b|c} d {|e}' -> every combination ('' = word absent)."""
    parts = template.replace("{", "\0{").replace("}", "}\0").split("\0")
    opts = [p[1:-1].split("|") if p.startswith("{") else [p] for p in parts]
    return [" ".join("".join(c).split()) for c in itertools.product(*opts)]


ISL = {  # island id: (start, end, hypothesis template)
    "HOOK": (0.20, 13.87, "kalau cakap pasal ubat yang stabilkan mood ramai yang tahu ubat litium {je|aje} tapi sebenarnya "
                          "ada satu lagi ubat yang kita boleh kata underrated {|ha} tapi power sebenarnya iaitu lamotrigine "
                          "{|ha} pernah dengar tak pasal ubat ni"),
    "AD": (14.05, 35.82, "iklan kalau anda ada masalah mood swing yang teruk cepat naik angin atau selalu mengalami fasa "
                         "depression jangan tunggu sampai ia mengganggu hidup anda {|anda} anda boleh dapatkan konsultasi dan "
                         "saringan kesihatan mental dengan saya doktor azren di klinik saya di nilai kita akan sama sama cek "
                         "apa rawatan yang sesuai untuk anda"),
    "FAMOUS": (41.75, 49.87, "okey berbalik pada topik tadi lamotrigine ni dia famous untuk stabilkan mood especially "
                             "dalam penyakit bipolar disorder"),
    "EPISOD": (50.30, 52.71, "{|ha} terutamanya dalam episod kemurungan lah {|dan}"),
    "WEIGHT": (53.03, 62.86, "dan risiko kenaikan berat badan dia sangat rendah sebenarnya sebab {tu|itu} {|*} ramai pasien "
                             "{|ramai pasien|* ramai pasien} yang suka dengan ubat ni {|ha} and ubat ni pula"),
    "DROWSY": (63.25, 79.41, "ubat ni juga dia tak buat rasa mengantuk sangat jadi ramai orang masih lagi boleh function macam "
                             "biasa pada siang hari dan sesuai untuk long term use {|ha} tapi dengan monitoring doktor lah {|ha} "
                             "seperti biasa setiap ubat pun ada keburukan dan side effect dia juga"),
    "TITRATE": (79.81, 93.66, "{|ha} {ubat ni dia kena start|buat ubat ni dia start|ubat ni dia start} dengan dos yang rendah "
                              "perlahan lahan kena titrate naik sebab ada risiko untuk ruam kulit yang serius kita panggil "
                              "sebagai steven johnson syndrome dia rare sebenarnya tapi boleh berlakulah dengan ubat ni"),
    "SIDEFX": (94.68, 105.22, "dan side effect dan boleh menyebabkan side effect side effect yang biasa lah seperti ubat lain "
                              "seperti pening kepala loya ataupun susah tidur dia tak begitu kuat"),
    "RETAKE": (106.50, 112.61, "dan ubat ni juga {|*} dan ubat ni juga dia tak begitu kuat untuk rawat"),
    "MANIA": (113.19, 123.88, "{fasa|pasal} mania tu dia lebih kepada nak elak kemurungan tu datang balik {dia|ada} sama seperti "
                              "ubat lain jangan stop sendiri tanpa advice doktor so lamotrigine ni dia macam"),
    "SUMMARY": (124.40, 143.80, "{|so} lamotrigine ni basically boleh bantu untuk mood kita especially dalam orang yang mengalami "
                                "bipolar disorder yang selalu berada di {fasa|pasal} kemurungan tapi kena ingat ubat ni juga ada "
                                "cara guna dia yang selamat kalau anda rasa struggle dengan mood swing boleh set appointment "
                                "dengan saya dekat nilai kita {sembang|memang} santai dahulu sebelum kita decide"),
    "PLAN": (143.85, 146.36, "plan terbaik untuk anda"),
    "BYE": (146.50, 149.20, "apa persoalan boleh tanya di ruang komen take care"),  # large-v3 on the clip alone
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
    for iid, (a, b, tpl) in ISL.items():
        if only and iid not in only:
            continue
        hyps = variants(tpl)
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
        print(f"{iid} score={score:.3f}{alts}: {h}")
    out = dict(sorted(out.items(), key=lambda kv: kv[1]["words"][0]["start"]))
    (E / "aligned.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
