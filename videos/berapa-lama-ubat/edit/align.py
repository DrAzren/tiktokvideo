"""CTC forced alignment (torchaudio MMS_FA) of corrected Malay text per speech island.

Aligned on the demucs vocal stem (vocals16k.wav): the source is a CapCut export with a music
bed mixed under the voice, which smears word edges. Each island lists one or more text
hypotheses; the best-scoring one wins. '*' = unknown sound (hesitation, breath).
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
    "I00": (0.10, 0.90, ["assalamualaikum", "assalamu alaikum", "salamualaikum", "assalamualaikum warahmatullah"]),
    "I01": (1.30, 2.10, ["soalan", "soalan ni", "* soalan"]),
    "I02": (2.20, 4.18, ["doktor berapa lama saya kena makan ubat ni"]),
    "I03": (4.33, 6.50, ["adakah saya kena makan ubat ni seumur hidup saya"]),
    "I04": (6.80, 7.70, ["okay jom kita kupas", "ok jom kita kupas"]),
    "I05": (7.86, 17.84, ["pertama tempoh makan ubat ni bergantung kepada tahap gejala yang anda alami kalau kemurungan atau anxiety tu ringan biasanya enam hingga dua belas bulan approximately", "pertama tempoh makan ubat ni bergantung kepada tahap gejala yang anda alami kalau kemurungan atau anxiety tu ringan biasanya six hingga twelve bulan approximately"]),
    "I06": (17.94, 22.84, ["tapi kalau dah pernah relapse gejala berulang berlaku tempoh tu boleh jadi lama"]),
    "I07": (22.88, 23.80, ["kenapa sebab"]),
    "I08": (24.40, 34.58, ["doktor nak pastikan anda betul betul stabil dulu sebelum ubat tu diberhentikan kalau ubat tu stop terlalu awal risiko simptom datang balik tu tinggi",
                           "doktor nak pastikan anda betul betul stabil dulu sebelum ubat tu diberhentikan kalau ubat itu stop terlalu awal risiko simptom datang balik itu tinggi"]),
    "I09": (34.90, 44.16, ["tapi kalau anda ada penyakit mental yang kronik macam bipolar atau skizofrenia ubat mungkin perlu diambil untuk jangka masa yang panjang"]),
    "I10": (44.36, 50.74, ["sama juga macam pesakit darah tinggi kencing manis yang perlukan ubat untuk kawal tekanan darah kawal gula dalam badan mereka"]),
    "I11": (50.78, 58.36, ["dan yang paling penting sekali ubat ni tak boleh nak stop suka suka kalau dah sampai masa nak stop doktor akan buat proses tapering",
                           "dan yang paling penting sekali ubat ini tak boleh nak stop suka suka kalau dah sampai masa nak stop doktor akan buat proses tapering"]),
    "I12": (58.30, 64.92, ["iaitu kurangkan dos secara perlahan lahan untuk elakkan withdrawal symptom tu jadi jangan takut"]),
    "I13": (64.88, 71.36, ["nak mulakan ubat tu dia bukanlah kita kata hukuman seumur hidup tapi dia sebenarnya adalah satu peluang untuk"]),
    "I14": (71.60, 77.70, ["kita sembuh dapatkan semula kualiti hidup kita kalau ada apa apa soalan boleh tanya di dalam komen take care", "kita sembuh dapatkan semula kualiti hidup kita kalau ada apa apa soalan boleh tanya dalam komen take care"]),
}


def main() -> None:
    import sys
    stars = "--stars" in sys.argv   # diagnostic: a '*' slot between every word; prints the ones that absorb sound
    only = set(a for a in sys.argv[1:] if not a.startswith("--"))  # optional: re-align just these islands, merging into aligned.json
    bundle = torchaudio.pipelines.MMS_FA
    model = bundle.get_model(with_star=True).eval()
    tokenizer = bundle.get_tokenizer()
    aligner = bundle.get_aligner()
    audio, sr = sf.read(E / "vocals16k.wav", dtype="float32")
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
            if stars:
                words = [x for w in words for x in ("*", w)] + ["*"]
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
        if stars:
            for w in out[iid]["words"]:
                if w["text"] == "*" and w["end"] - w["start"] >= 0.08:
                    print(f"   * {w['start']:6.2f}-{w['end']:6.2f} ({w['end'] - w['start']:.2f}s)")
            continue
        alts = "" if len(hyps) == 1 else f"  (picked {hyps.index(h) + 1}/{len(hyps)})"
        print(f"{iid} score={score:.3f}{alts}")
    if stars:
        return
    out = dict(sorted(out.items(), key=lambda kv: kv[1]["words"][0]["start"]))
    (E / "aligned.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
