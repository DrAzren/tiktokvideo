"""CTC forced alignment (torchaudio MMS_FA) of corrected Malay text per speech island.

Same method as videos/ward-psikiatri/edit/align.py: Whisper word times drift (they swallow
pauses), so cut edges come from here. Each island's text may hold alternatives as
{a|b|c}; every combination is aligned and the best-scoring one wins.
'*' = unknown sound (breath, "haa", hesitation). '~' in an alternative = nothing.
This clip was recorded in a car: the noise floor in pauses is only ~25 dB under the voice.
Output: aligned.json
"""

import itertools
import json
import re
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio

E = Path(__file__).parent
ISL = {  # island id: (start, end, text with {alt|alt})
    "I01": (0.00, 4.97, "sepuluh ayat yang tak patut kita cakap pada orang yang mengalami masalah {kesihatan|kesehatan} mental"),
    "I02": (4.95, 8.70, "satu {~|*} kau ni terlalu fikir banyak sangat"),
    "I03": (9.05, 15.32, "masalah mental ni dia bukan {semata mata|sebab sebab|semata mata sebab} overthinking tapi dia melibatkan perubahan kimia di dalam otak yang kedua"),
    "I04": (15.35, 18.15, "ramai lagi orang lain yang lagi teruk daripada kau"),
    "I05": (18.55, 30.82, "ini boleh buatkan seorang itu rasa perasaan dia tak valid sedangkan semua orang dia ada dia punya cabaran dia masing masing yang ketiga {~|*} kau ni manja sangat sebab tu boleh jadi sampai macam ni"),
    "I06": (30.80, 39.05, "ni pun boleh menambahkan perasaan malu dan rasa bersalah kepada dia sendiri walaupun dia sedang bergelut dengan masalah kesihatan mental dia tu"),
    "I07": (39.05, 40.85, "yang keempat"),
    "I08": (41.25, 43.88, "kau ni doa je lebih sikit {haa|*|~} nanti baik lah tu"),
    "I09": (44.65, 51.00, "betul doa tu penting tapi kesihatan mental juga perlukan rawatan dan sokongan daripada profesional"),
    "I10": (51.40, 52.90, "yang kelima"),
    "I11": (53.25, 62.80, "kau ni dah gila eh yang ni stigma macam ni yang menyakitkan sebab ni bukan gurauan tapi dia sebenarnya sangat menyakitkan untuk orang yang ada masalah kesihatan mental"),
    "I12": (62.75, 64.90, "{~|*} yang keenam"),
    "I13": (65.15, 75.30, "kau {ambil|ambik} je cuti nanti okey lah tu {~|*} okey {~|*} rehat penting tapi ini bukan semudah {~|*} {ambil|ambik} cuti dan terus sembuh"),
    "I14": (75.25, 81.45, "dia memerlukan satu proses untuk pemulihan masalah kesihatan mental ni yang ketujuh"),
    "I15": (81.55, 83.95, "{~|*} semua ni ada dalam kepala je"),
    "I16": (84.25, 91.40, "kesihatan mental ni dia bukanlah benda yang main main {~|*} bukanlah rekaan {~|*} sebab ia boleh menjejaskan fungsi harian seseorang"),
    "I17": (91.40, 93.10, "{~|*} yang ke lapan"),
    "I18": (95.50, 107.18, "yang ke lapan jangan tunjuk sangat lah nanti orang fikir kau lemah sebenarnya {~|*} kita menggalakkan mereka untuk pendam perasaan mereka {ini|ni} boleh memperburukkan lagi lah keadaan yang ke sembilan"),
    "I19": (107.15, 108.95, "kau {kena lah|kenalah} kuat sikit"),
    "I20": (109.55, 117.22, "orang yang ada masalah mental ni pun dah kuat sebenarnya sebab mereka masih berjuang setiap hari dalam kehidupan mereka"),
    "I21": (117.15, 119.20, "{~|*|okey|haa} yang ke sepuluh"),
    "I22": (119.90, 124.45, "kau ni macam cari perhatian je sebenarnya mereka ni sedang cari bantuan"),
    "I23": (124.55, 130.30, "kita ni yang patut tunjuk {empati|empathy} kepada mereka {~|*} bukan being judgemental"),
    "I24": (130.15, 134.70, "bukan * bukan judge mereka"),
    "I25": (135.40, 138.00, "okey kesimpulan dia okey"),
    "I26": (138.10, 153.05, "kalau kita tak tahu nak cakap apa cukuplah sekadar saya ada di sini kalau awak perlukan saya {itu pun|ataupun} dah cukup besar untuk seseorang yang sedang berjuang dengan masalah kesihatan mental ni kalau ada apa apa soalan boleh tanya {di dalam|dalam|orang|di} komen take care {~|*}"),
}


def expand(text: str) -> list[str]:
    parts = re.split(r"(\{[^}]*\})", text)
    opts = [p[1:-1].split("|") if p.startswith("{") else [p] for p in parts]
    out = []
    for combo in itertools.product(*opts):
        s = " ".join(" ".join(combo).replace("~", " ").split())
        out.append(s)
    return out


def main() -> None:
    import sys
    only = set(sys.argv[1:])
    bundle = torchaudio.pipelines.MMS_FA
    model = bundle.get_model(with_star=True).eval()
    tokenizer = bundle.get_tokenizer()
    aligner = bundle.get_aligner()
    audio, sr = sf.read(E / "audio.wav", dtype="float32")
    assert sr == bundle.sample_rate

    out = json.loads((E / "aligned.json").read_text()) if only and (E / "aligned.json").exists() else {}
    for iid, (a, b, text) in ISL.items():
        if only and iid not in only:
            continue
        wav = torch.from_numpy(audio[int(a * sr):int(b * sr)]).unsqueeze(0)
        with torch.inference_mode():
            emission, _ = model(wav)
        ratio = wav.shape[1] / emission.shape[1] / sr
        best = None
        hyps = expand(text)
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
        print(f"{iid} score={score:.3f} ({len(hyps)} hyps) {h}")
    out = dict(sorted(out.items(), key=lambda kv: kv[1]["words"][0]["start"]))
    (E / "aligned.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
