"""Corrected subtitle file (SRT) of the cleaned narration on the final-cut timeline.

Same words, spellings and sentence-aware line breaks as the burned-in captions (build_graphics.py),
but complete: it also covers the kinetic hook and the hero word, which the video draws as graphics.
Sentence case, Malay as spoken; drug names spelled correctly.
"""
import sys
from pathlib import Path

C = Path(__file__).parent
sys.path.insert(0, str(C.parent / "graphics"))
import build_graphics as g  # noqa: E402

PROPER = {"dayvigo": "Dayvigo", "alprazolam": "alprazolam", "azren": "Azren", "nilai": "Nilai", "doktor": "Doktor"}


def ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


lines = g.group(g.CW)
out, cap_next = [], True
for i, ln in enumerate(lines):
    words = [PROPER.get(w["text"].lower(), w["text"]) if w["text"].lower() in PROPER else w["text"] for w in ln]
    if ln[0]["sent"] or i == 0:
        words[0] = words[0][:1].upper() + words[0][1:]
    t0 = ln[0]["start"] - 0.05
    t1 = min(lines[i + 1][0]["start"] - 0.05 if i + 1 < len(lines) else g.DUR, ln[-1]["end"] + 0.4)
    out.append(f"{len(out) + 1}\n{ts(t0)} --> {ts(t1)}\n{' '.join(words)}\n")
(C / "dayvigo_ms.srt").write_text("\n".join(out))
print(len(out), "cues →", C / "dayvigo_ms.srt")
