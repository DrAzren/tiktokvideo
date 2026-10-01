"""Classify every '*' slot between aligned words: voiced hesitation ("aa/eee/mmm", drawn vowel) vs
breath / silence, from the 10ms energy envelope + pYIN voicing. -> gaps.json (used for the filler list)."""
import json
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

E = Path(__file__).parent
x, sr = sf.read(E / "audio.wav", dtype="float32")
db = np.load(E / "env_db.npy")
cache = E / "voicing.npy"
if cache.exists():
    vp = np.load(cache)
else:
    _, vflag, vprob = librosa.pyin(x, fmin=70, fmax=400, sr=sr, frame_length=1024, hop_length=160)
    vp = np.where(vflag, vprob, 0.0).astype(np.float32)
    np.save(cache, vp)
al = json.loads((E / "aligned.json").read_text())
W = al["words"]
out = []
for s in al["stars"]:
    d = s["end"] - s["start"]
    if d < 0.1 or s["after"] < 0 or s["after"] + 1 >= len(W):
        continue
    i0, i1 = int(s["start"] * 100), int(s["end"] * 100)
    seg_db, seg_v = db[i0:i1], vp[i0:i1]
    loud = seg_db > -32
    voiced = (seg_v > 0.5) & loud
    vt = round(float(voiced.sum()) / 100, 2)
    kind = "voiced" if vt >= 0.08 else ("breath" if (seg_db > -42).sum() >= 8 else "silence")
    out.append({"after": s["after"], "start": s["start"], "end": s["end"], "dur": round(d, 2), "kind": kind,
                "voiced_s": vt, "max_db": round(float(seg_db.max()), 1),
                "ctx": f"{W[s['after']]['text']} _ {W[s['after'] + 1]['text']}"})
(E / "gaps.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
for g in out:
    if g["kind"] == "voiced" or g["dur"] >= 0.3:
        print(f"{g['start']:7.2f} {g['dur']:.2f}s {g['kind']:7s} v={g['voiced_s']:.2f} max={g['max_db']:6.1f}  {g['ctx']}")
