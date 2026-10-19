"""Human-readable original-to-final edit decision list (EDL.md) from edl.json + cut_words.json."""
import json
from fractions import Fraction
from pathlib import Path

E = Path(__file__).parent
edl = json.loads((E / "edl.json").read_text())
al = json.loads((E / "aligned.json").read_text())
words = sorted((w for v in al.values() for w in v["words"] if w["text"] != "*"), key=lambda w: w["start"])


def tc(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


rows, t = [], 0.0
for i, r in enumerate(edl["ranges"]):
    s = float(Fraction(round(r["start"] * 30)) / 30)
    e = float(Fraction(round(r["end"] * 30)) / 30)
    txt = " ".join(w["text"] for w in words if s <= (w["start"] + w["end"]) / 2 < e)
    rows.append(f"| {i} | {tc(s)}–{tc(e)} | {tc(t)}–{tc(t + e - s)} | {r.get('zoom', 1.0):.2f} | {txt} | {r.get('reason', '')} |")
    t += e - s
md = ["# Dayvigo — original → final edit decision list", "",
      f"Source: `raw/Ubat Psikiatri Dayvigo.mp4` (2:12.6). Final cut: {tc(t)} + {edl.get('tail_hold', 0)}s hold. "
      "Picture un-mirrored (selfie-mode recording). Voice: `enhance_voice.sh`. Everything not listed was removed "
      "(fillers, hesitations, retakes, dead air — see project.md).", "",
      "| # | Source in–out | Final in–out | Zoom | Kept words (aligned, phonetic) | Segment note |", "|---|---|---|---|---|---|", *rows]
(E / "EDL.md").write_text("\n".join(md) + "\n")
print(len(rows), "ranges →", E / "EDL.md")
