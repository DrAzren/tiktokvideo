"""Editable Bahasa Melayu captions (SRT) from the same subtitle segmentation the composition burns in."""
import json
from pathlib import Path

D = Path(__file__).parent
segs = json.loads((D / "subtitles.json").read_text())


def ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


out = []
for i, s in enumerate(segs):
    a = s["start"] - 0.08
    b = s["end"] + 0.35
    if i + 1 < len(segs):
        b = min(b, segs[i + 1]["start"] - 0.1)
    out.append(f"{i + 1}\n{ts(a)} --> {ts(b)}\n{s['text']}\n")
(D.parent / "sejarah-penyakit-mental_ms.srt").write_text("\n".join(out))
print(len(out), "cues")
