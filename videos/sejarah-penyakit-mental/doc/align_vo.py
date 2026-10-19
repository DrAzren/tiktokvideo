"""Word timings for the six narration takes (torchaudio MMS_FA forced alignment of the exact script).

Output: vo_words.json = {"s1": [{"text": display word, "start", "end"}...], ...} in take-local seconds.
Run: ../../../.venv/bin/python align_vo.py
"""

import json
import re
import subprocess
from pathlib import Path

import numpy as np
import torch
import torchaudio

D = Path(__file__).parent
A = D.parent / "audio"
SCRIPT = {
    "s1": "Bayangkan hidup dua ratus tahun dahulu. Anda mengalami suara yang orang lain tak dengar, atau kesedihan yang terlalu berat. Adakah masyarakat ketika itu tahu cara membantu anda?",
    "s2": "Sebenarnya, gangguan mental bukan fenomena baharu. Sejak zaman purba, manusia cuba memahami perubahan emosi, pemikiran dan tingkah laku. Di sesetengah tempat, gejalanya dikaitkan dengan unsur ghaib. Tetapi pandangan berbeza mengikut budaya dan zaman.",
    "s3": "Lebih dua ribu tahun lalu, Hippocrates di Yunani mencadangkan bahawa gangguan mental ada punca semula jadi. Teorinya tentang keseimbangan cecair badan kini tidak lagi diterima, namun idea mengkaji keadaan mental melalui perubatan merupakan satu perubahan penting.",
    "s4": "Kemudian, sepanjang sejarah, sebahagian individu ditempatkan di institusi jagaan. Ada yang menerima bantuan, tetapi ada juga yang mengalami pengasingan dan layanan tidak berperikemanusiaan. Pada penghujung abad kelapan belas, tokoh seperti Philippe Pinel dan William Tuke memperjuangkan pendekatan yang lebih berperikemanusiaan.",
    "s5": "Menjelang tahun sembilan belas lima puluh dua, penggunaan chlorpromazine dalam psikiatri membuka lembaran baharu rawatan ubat untuk sesetengah gangguan mental. Penyelidikan terus berkembang, seiring usaha memperbaiki hak dan penjagaan pesakit.",
    "s6": "Hari ini, rawatan boleh melibatkan psikoterapi, ubat apabila sesuai, sokongan keluarga dan pemulihan dalam komuniti. Tetapi satu cabaran masih wujud: stigma. Sejarah mengajar kita bahawa pengetahuan berubah, namun maruah manusia tidak patut dikompromi. Penyakit mental bukan tanda lemah. Dan meminta bantuan bukan sesuatu yang memalukan. Mari ubah cara kita melihat kesihatan mental.",
}


def load(path: Path, sr: int) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def main() -> None:
    bundle = torchaudio.pipelines.MMS_FA
    model = bundle.get_model(with_star=False).eval()
    tok, aligner = bundle.get_tokenizer(), bundle.get_aligner()
    out = {}
    for sid, text in SCRIPT.items():
        disp = text.split()
        norm = [re.sub(r"[^a-z']", "", w.lower()) for w in disp]
        audio = load(A / f"vo_{sid}.mp3", bundle.sample_rate)
        wav = torch.from_numpy(audio).unsqueeze(0)
        with torch.inference_mode():
            em, _ = model(wav)
        ratio = wav.shape[1] / em.shape[1] / bundle.sample_rate
        spans = aligner(em[0], tok(norm))
        out[sid] = [{"text": d, "start": round(ws[0].start * ratio, 3), "end": round(ws[-1].end * ratio, 3),
                     "score": round(float(np.mean([s.score for s in ws])), 3)} for d, ws in zip(disp, spans)]
        low = [w["text"] for w in out[sid] if w["score"] < 0.5]
        print(sid, f"{len(disp)} words, {out[sid][0]['start']:.2f}-{out[sid][-1]['end']:.2f}s", "low:", low)
    (D / "vo_words.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
