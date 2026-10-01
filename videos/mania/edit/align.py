"""CTC forced alignment (torchaudio MMS_FA) of the corrected Malay text over the whole clip.

Same method as videos/ada-halusinasi-yang-normal/edit/align.py: emission in overlapping 30s windows,
stitched, the full text aligned once with a '*' (unknown-sound) slot between every word pair, so
voiced hesitations ("aa", "eee", "mmm") land in '*' spans with exact times.

Text = medium (prompted, keeps fillers) + unprompted large-v3, disputes settled by `--variants`
(alignment score of each candidate wording over its own window, see VARIANTS). Numbers spelled out.
Output: aligned.json {"words": [{text, start, end, score, i}], "stars": [{after, start, end}]}

    python align.py              # align TEXT -> aligned.json
    python align.py --variants   # score the disputed wordings
"""

import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio

E = Path(__file__).parent
WIN, HOP = 30.0, 20.0     # emission windows (s); the middle of each window is kept

TEXT = """
assalamualaikum saya doktor azren saya merupakan doktor di jabatan psikiatri
ramai yang salah faham yang ingat gangguan mania ni seperti gangguan personaliti atau identiti yang berubah ubah
okay sebelumnya nak tahu mania kita kena tahu bipolar
gangguan bipolar ni dia adalah salah satu penyakit mental yang menyebabkan perubahan mood yang drastik di antara
fasa tinggi atau kita panggil sebagai fasa mania dan juga fasa rendah kita panggil sebagai depression
okay fasa mania ni dia ada beberapa gejala dan gejala gejala ini mestilah berlaku hari hari
at least satu minggu sekurang kurangnya satu minggu kalau dia berlaku kurang dari satu minggu
kita tak panggil dia fasa mania jadi apa yang berlaku dalam fasa mania ni
orang yang mengalami mania ni dia akan ada mood yang berlebihan maksudnya individu itu akan rasa ada perasaan gairah
dan penuh semangat mereka ni mungkin kalau kita tengok orang yang ada bipolar dia akan dia akan jadi lebih banyak bercakap
susah nak stop percakapan dia kalau kita berbual dengan dia kita nampak dia sangat ceria dan optimistik yang berlebihan
dalam fasa mania ni individu tu cenderung untuk melakukan lebih banyak aktiviti
mereka tak memikirkan pun risiko atau kesan negatif terhadap perkara yang mereka lakukan itu
dan mereka boleh jadi terlalu aktif kurang tidur buat banyak projek tanpa dapat menyiapkannya
mereka ni dia rasa dia memiliki banyak tenaga dan keperluan tidur dia tu akan jadi berkurangan
tengok orang yang ada dalam fasa mania ni tidur dia dalam dua tiga jam je satu hari
and then fikiran dia sangat laju terlalu banyak idea yang melibatkan risiko dan kesukaran untuk menumpukan perhatian pada sesuatu
fasa mania ni boleh menyebabkan seorang itu mengambil risiko yang tidak masuk akal
seperti penggunaan dadah atau alkohol yang berlebihan pengeluaran wang yang tidak terkawal
berbelanja secara berlebihan kelakuan agresif rasa cepat marah impulsif dan lain lain lagi
ada yang saya jumpa tu dia tak pergi kerja sebab dia kata dia pergi panjat gunung
tanpa pakai baju tanpa pakai kasut sebab nak cari puteri gunung ledang di sana sampai tahap macam tu sekali
penting untuk diingatkan bahawa gangguan bipolar penting untuk saya ingatkan bahawa gangguan bipolar dia memerlukan rawatan yang sesuai
seperti terapi dan juga mungkin ubat ubatan untuk membantu menguruskan gejala
dan meningkatkan kualiti hidup individu yang menghidapnya
kalau ada apa apa soalan boleh tanya di ruang komen take care
"""

# disputed wordings: (window start, window end, [candidates]) — scored with '*' slots, best mean wins
VARIANTS = [
    (3.4, 5.0, ["saya merupakan doktor di jabatan psikiatri", "saya merupakan doktor di jabatan sekretari",
                "saya merupakan doktor pakar psikiatri"]),
    (11.4, 14.4, ["okay sebelumnya nak tahu mania kita kena tahu bipolar",
                  "okay sebelumnya nak tahu mania kita kena tahu bipolar"]),
    (53.5, 62.2, ["mereka ni mungkin kalau kita tengok orang yang ada bipolar dia akan dia akan jadi",
                  "mereka ni mungkin kalau kita orang yang ada bipolar dia akan dia akan jadi",
                  "mereka ni mungkin kalau kita tengok orang yang ada bipolar pola dia akan dia akan jadi",
                  "mereka ni mungkin kalau kita tengok orang yang ada bipolar dia akan dia akan dia akan jadi"]),
    (62.0, 64.2, ["lebih banyak bercakap susah", "lebih banyak percakap susah"]),
    (68.9, 72.9, ["berlebihan dalam fasa mania ni individu tu cenderung",
                  "berlebihan dalam fasa mania ini individu itu cenderung"]),
    (79.0, 83.6, ["perkara yang mereka lakukan itu dan mereka", "perkara yang mereka lakukan bukan itu dan mereka"]),
    (95.5, 99.5, ["akan jadi berkurangan kita tengok orang", "akan jadi berkurangan tengok orang"]),
    (108.4, 113.8, ["terlalu banyak idea yang melibatkan risiko", "terlalu banyak idea yang melibatkan risiko"]),
    (113.4, 118.0, ["fasa mania ni boleh menyebabkan seorang itu mengambil",
                    "fasa mania ini boleh menyebabkan seorang itu mengambil",
                    "fasa mania ni boleh menyebabkan seorang itu mengambil"]),
    (138.8, 143.4, ["tanpa pakai baju tanpa pakai kasut sebab nak cari puteri gunung ledang di sana",
                    "tanpa pakai baju tanpa pakai kasut sebab nak cari putih gunung ledang di sana"]),
    (143.0, 145.4, ["sampai tahap macam tu sekali", "sampai tahap macam itu sekali"]),
    (145.0, 153.0, ["penting untuk diingatkan bahawa gangguan bipolar penting untuk saya ingatkan bahawa gangguan bipolar dia memerlukan rawatan yang sesuai",
                    "penting untuk diingatkan bahawa gangguan bipolar dia memerlukan rawatan yang sesuai",
                    "penting untuk diingatkan bahawa gangguan bipolar penting untuk saya ingatkan bahawa gangguan bipolar dia memerlukan rawatannya sesuai"]),
    (152.6, 157.4, ["seperti terapi dan juga mungkin ubat ubatan untuk", "seperti terapi dan juga mungkin ubah batan untuk"]),
    (160.8, 164.4, ["kalau ada apa apa soalan boleh tanya di ruang komen take care",
                    "kalau ada apa apa soalan boleh tanya diorang komen take care"]),
]


# (phrase in TEXT, [alternatives]) — scored inside the full alignment (no window-edge bias)
GLOBAL_VARIANTS = [
    ("doktor di jabatan psikiatri", ["doktor di jabatan sekretari", "doktor pakar psikiatri", "doktor jabatan psikiatri"]),
    ("tahu bipolar gangguan bipolar ni dia adalah", ["tahu bipolar gangguan bipolar ni adalah"]),
    ("individu tu cenderung", ["individu itu cenderung"]),
    ("bipolar penting untuk saya ingatkan bahawa gangguan bipolar dia",
     ["bipolar dia"]),
    ("cari puteri gunung", ["cari putih gunung", "cari puteri di gunung"]),
]


def emissions(model, audio: np.ndarray, sr: int) -> tuple[torch.Tensor, float]:
    """Log-prob emission for the whole clip from overlapping windows (keep each window's middle)."""
    total = len(audio) / sr
    chunks, t = [], 0.0
    ratio = None
    while t < total:
        a, b = int(t * sr), int(min(total, t + WIN) * sr)
        with torch.inference_mode():
            em, _ = model(torch.from_numpy(audio[a:b]).unsqueeze(0))
        em = em[0]
        ratio = (b - a) / em.shape[0] / sr if ratio is None else ratio
        keep_from = 0 if t == 0 else int(((WIN - HOP) / 2) / ratio)
        keep_to = em.shape[0] if t + WIN >= total else int((WIN - (WIN - HOP) / 2) / ratio)
        chunks.append((t + keep_from * ratio, em[keep_from:keep_to]))
        if t + WIN >= total:
            break
        t += HOP
    n = int(round(total / ratio))
    out = torch.full((n, chunks[0][1].shape[1]), float("nan"))
    for t0, em in chunks:
        i0 = int(round(t0 / ratio))
        out[i0:i0 + em.shape[0]] = em[:max(0, min(em.shape[0], n - i0))]
    assert not torch.isnan(out).any(), "emission stitching left a hole"
    return out, ratio


def align(em, ratio, words, tokenizer, aligner, t0=0.0):
    seq = []
    for k, w in enumerate(words):
        seq.append(w)
        if k + 1 < len(words):
            seq.append("*")
    spans = aligner(em, tokenizer(seq))
    out_w, stars = [], []
    for tok, ws in zip(seq, spans):
        s, e = round(t0 + ws[0].start * ratio, 3), round(t0 + ws[-1].end * ratio, 3)
        if tok == "*":
            stars.append({"after": len(out_w) - 1, "start": s, "end": e})
        else:
            out_w.append({"i": len(out_w), "text": tok, "start": s, "end": e,
                          "score": round(float(np.mean([x.score for x in ws])), 3)})
    return out_w, stars


def main() -> None:
    bundle = torchaudio.pipelines.MMS_FA
    model = bundle.get_model(with_star=True).eval()
    tokenizer, aligner = bundle.get_tokenizer(), bundle.get_aligner()
    audio, sr = sf.read(E / "audio.wav", dtype="float32")
    assert sr == bundle.sample_rate

    if "--variants" in sys.argv:
        for a, b, cands in VARIANTS:
            clip = audio[int(a * sr):int(b * sr)]
            with torch.inference_mode():
                em, _ = model(torch.from_numpy(clip).unsqueeze(0))
            ratio = len(clip) / em.shape[1] / sr
            print(f"[{a:.1f}-{b:.1f}]")
            for c in cands:
                ws, _ = align(em[0], ratio, c.split(), tokenizer, aligner, a)
                weak = " ".join(f"{w['text']}({w['score']:.2f})" for w in ws if w["score"] < 0.4)
                print(f"   {np.mean([w['score'] for w in ws]):.3f}  {c}   {('weak: ' + weak) if weak else ''}")
        return

    em, ratio = emissions(model, audio, sr)
    if "--global" in sys.argv:
        base = re.sub(r"\s+", " ", TEXT).strip()
        for default, alts in GLOBAL_VARIANTS:
            assert default in base, default
            for c in [default] + alts:
                ws, _ = align(em, ratio, base.replace(default, c).split(), tokenizer, aligner)
                k0 = len(base[:base.index(default)].split())
                span = ws[max(0, k0 - 2):k0 + len(c.split()) + 2]
                print(f"   {np.mean([w['score'] for w in span]):.3f}  {c}  "
                      + " ".join(f"{w['text']}({w['score']:.2f})" for w in span))
        return
    words = re.sub(r"\s+", " ", TEXT).strip().split()
    out_w, stars = align(em, ratio, words, tokenizer, aligner)
    score = float(np.mean([w["score"] for w in out_w]))
    (E / "aligned.json").write_text(json.dumps({"score": round(score, 3), "words": out_w, "stars": stars},
                                               indent=1, ensure_ascii=False))
    low = [f"{w['text']}@{w['start']:.2f}({w['score']:.2f})" for w in out_w if w["score"] < 0.35]
    print(f"{len(out_w)} words, mean score {score:.3f}; low-score words: {' '.join(low) or 'none'}")


if __name__ == "__main__":
    main()
