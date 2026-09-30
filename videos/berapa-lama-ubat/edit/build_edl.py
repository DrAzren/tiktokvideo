"""Build edl.json for 'Berapa Lama Makan Ubat Psikiatri' from forced-aligned words.

Template: videos/ward-psikiatri/edit/build_edl.py (same edge rules). Differences:
  - the source is a CapCut export with a music bed mixed under the voice, so audio comes from
    the demucs vocal stem (src_clean.mov = working video + vocals) and a new bed goes on in stage 6;
  - TRIM shortens drawn-out words ("kalauuu") to a natural length before the forced cut.

Segments reference aligned.json words as (island, first_word, island, last_word).
Edge rules (CTC word ends run ~0.1s early, so edges snap to real audio energy):
  - OUT: first point after the word where energy stays below QUIET_DB, plus a
         short tail; never past the next word. IN mirrors this.
  - If the neighbouring (dropped) word is within TIGHT s, cut at the energy
    minimum between the two words instead.
  - Gaps longer than MAX_PAUSE between kept words are shrunk the same way.
"""

import json
from pathlib import Path

import numpy as np

E = Path(__file__).parent
SRC = "ubat"
SRC_PATH = str((E / "src_clean.mov").resolve())

QUIET_DB = -40.0     # below this for QUIET_RUN frames = the word has really ended/not begun
QUIET_RUN = 3        # 30ms
TAIL_OUT, LEAD_IN = 0.06, 0.04   # extra air kept after offset / before onset
MAX_SNAP = 0.35      # never move more than this from the aligned word edge
TIGHT = 0.16
MAX_PAUSE = 0.40     # gaps between kept words longer than this get shrunk (TikTok pace)
ZOOMS = [1.0, 1.06, 1.02, 1.07]  # punch-in levels cycled across jump cuts (user-specified)
PUNCH_MIN = 0.8      # ranges shorter than this keep the previous zoom (no flicker)
MICRO = 0.7          # a pause-shrink cut that leaves a range shorter than this is undone (no stutter)
TAIL_HOLD = 1.0      # freeze the last frame so the end card / CTA can land
FACE = [0.50, 0.62]  # zoom focus (after the caption crop): nose height, so punch-ins push the mouth down as little as possible

# (island_a, word_a, island_b, word_b, beat, note[, {"start"/"end": override s, "gain_db": dB}])
SEGMENTS = [
    ("I02", 0, "I02", 7, "HOOK", "Doktor, berapa lama saya kena makan ubat ni? — 'Assalamualaikum. Soalan:' dropped"),
    ("I03", 0, "I03", 8, "HOOK", "Adakah saya kena makan ubat ni seumur hidup saya?"),
    ("I04", 1, "I04", 3, "HOOK", "Jom kita kupas. — 'Ok' dropped"),
    ("I05", 0, "I05", 23, "ANSWER", "Pertama, tempoh ... bergantung kepada tahap gejala ... 6 hingga 12 bulan. — 'approximately' dropped"),
    ("I06", 0, "I06", 12, "RELAPSE", "Tapi kalau pernah relapse ... tempoh boleh jadi lama."),
    ("I07", 0, "I07", 1, "WHY", "Kenapa? Sebab"),
    ("I08", 0, "I08", 23, "WHY", "doktor nak pastikan anda betul-betul stabil ... risiko simptom datang balik tinggi."),
    ("I09", 0, "I09", 20, "CHRONIC", "Tapi kalau anda ada penyakit mental yang kronik ... jangka masa yang panjang."),
    ("I10", 0, "I10", 19, "CHRONIC", "Sama juga macam pesakit darah tinggi, kencing manis ..."),
    ("I11", 0, "I11", 23, "TAPER", "Dan yang paling penting sekali, ubat tak boleh stop suka-suka ... proses tapering"),
    ("I12", 0, "I12", 13, "TAPER", "iaitu kurangkan dos secara perlahan-lahan ... jangan takut"),
    ("I13", 0, "I14", 6, "CLOSE", "nak mulakan ubat. Bukanlah hukuman seumur hidup, tapi satu peluang untuk kita sembuh ..."),
    ("I14", 7, "I14", 17, "CTA", "Kalau ada apa-apa soalan boleh tanya dalam komen. Take care."),
]

# filler words dropped from inside kept segments (strategy list, pending user OK)
DROP = {
    ("I05", 4), ("I05", 16),                 # "ubat *ni* bergantung", "anxiety *tu* ringan"
    ("I06", 2), ("I06", 9),                  # "kalau *dah* pernah", "tempoh *tu* boleh"
    ("I08", 10), ("I08", 14), ("I08", 22),   # "ubat *tu* diberhentikan", "ubat *tu* stop", "balik *tu* tinggi"
    ("I09", 8),                              # "kronik *macam* bipolar"
    ("I11", 6), ("I11", 9), ("I11", 14),     # "ubat *ni* tak boleh *nak* stop", "kalau *dah* sampai"
    ("I12", 10), ("I12", 11),                # "symptom *tu*", "*jadi* jangan takut"
    ("I13", 3), ("I13", 4), ("I13", 6), ("I13", 7),        # "ubat *tu* *dia* bukanlah *kita kata* hukuman"
    ("I13", 12), ("I13", 13), ("I13", 14),   # "tapi *dia sebenarnya adalah* satu peluang"
}
# voiced hesitations ("mmm", drawn-out vowels) filling short gaps: always cut, whatever the gap length.
# Given as the word BEFORE the gap.
HESITATE = {("I05", 0), ("I05", 6), ("I08", 8), ("I10", 5), ("I13", 5), ("I13", 17)}
# drawn-out words: keep only the first N seconds of the word, then force a cut (flat, steady harmonics
# in the spectrogram = a held vowel, not articulation)
TRIM = {("I06", 1): 0.30, ("I09", 1): 0.30, ("I11", 13): 0.28}


def main() -> None:
    db = np.load(E / "env_db.npy")
    dur = len(db) / 100
    al = json.loads((E / "aligned.json").read_text())
    flat = sorted(
        ({"iid": iid, "i": i, **w} for iid, v in al.items() for i, w in enumerate(v["words"])),
        key=lambda w: w["start"],
    )
    pos = {(w["iid"], w["i"]): k for k, w in enumerate(flat)}
    for key, keep in TRIM.items():
        w = flat[pos[key]]
        w["end"] = round(min(w["end"], w["start"] + keep), 3)

    def emin(lo: float, hi: float) -> float:
        i0, i1 = int(lo * 100), max(int(lo * 100) + 1, int(hi * 100))
        return (i0 + int(np.argmin(db[i0:i1]))) / 100 + 0.005

    def quiet(i: int) -> bool:
        return bool(np.all(db[i:i + QUIET_RUN] < QUIET_DB))

    def snap_out(t: float, limit: float) -> float:
        hi = min(limit, t + MAX_SNAP)
        i, stop = int(t * 100), int(hi * 100)
        while i < stop and not quiet(i):
            i += 1
        if i >= stop:  # never goes quiet (breath/hum follows): cut at the deepest dip near the word's own
            return emin(t - 0.02, min(hi, t + 0.12))   # edge (a mid-gap dip would keep half the breath)
        return min(limit, i / 100 + TAIL_OUT)

    def snap_in(t: float, floor: float) -> float:
        lo = max(floor, t - MAX_SNAP)
        i, stop = int(t * 100), int(lo * 100)
        while i > stop and not quiet(i - QUIET_RUN):
            i -= 1
        if i <= stop:
            return emin(max(lo, t - 0.12), t + 0.02)
        return max(floor, i / 100 - LEAD_IN)

    def between(a: dict, b: dict) -> float:
        """Cut point between two touching words; both edges of the pair use the same window."""
        back = 0.12 if a["text"] == "*" else 0.04  # '*' is unknown noise: allow reaching into it
        return emin(a["end"] - back, b["start"] + 0.04)

    def cut_in(k: int) -> float:
        w = flat[k]
        prev = flat[k - 1] if k > 0 else None
        if prev and w["start"] - prev["end"] < TIGHT:
            return between(prev, w)
        return snap_in(w["start"], prev["end"] + 0.02 if prev else 0.0)

    def cut_out(k: int) -> float:
        w = flat[k]
        nxt = flat[k + 1] if k + 1 < len(flat) else None
        if nxt and nxt["text"] == "*":  # unknown sound follows: end where the word's energy dies
            nxt2 = next((x for x in flat[k + 2:] if x["text"] != "*"), None)
            return snap_out(w["end"], nxt2["start"] - 0.02 if nxt2 else dur)
        if nxt and nxt["start"] - w["end"] < TIGHT:
            return between(w, nxt)
        return snap_out(w["end"], nxt["start"] - 0.02 if nxt else dur)

    ranges = []
    for ia, wa, ib, wb, beat, note, *opt in SEGMENTS:
        opt = opt[0] if opt else {}
        ka, kb = pos[(ia, wa)], pos[(ib, wb)]
        start, end = opt.get("start", cut_in(ka)), opt.get("end", cut_out(kb))
        seg, cur = [], start
        forced = []   # forced[i]: boundary between seg[i] and seg[i+1] is a filler cut (never merged back)
        keep = [k for k in range(ka, kb + 1) if (flat[k]["iid"], flat[k]["i"]) not in DROP]
        for k, k2 in zip(keep, keep[1:]):  # shrink long gaps (breaths); cut dropped words and hesitations
            a, b = flat[k], flat[k2]
            dropped = k2 != k + 1
            hes = (a["iid"], a["i"]) in HESITATE or (a["iid"], a["i"]) in TRIM
            if dropped or hes:
                # the neighbour is a filler/voiced hesitation, so energy never goes quiet: cut at the
                # deepest dip right at each word's own edge
                # the search windows stop at the dropped word's own edges: a short coarticulated "ni"/"tu"
                # would otherwise survive inside a window that reaches past it
                hi = a["end"] + 0.07 if not dropped else max(a["end"] + 0.01, min(a["end"] + 0.07, flat[k + 1]["start"] + 0.01))
                lo = b["start"] - 0.07 if not dropped else min(b["start"] - 0.01, max(b["start"] - 0.07, flat[k2 - 1]["end"] - 0.01))
                seg.append([cur, emin(a["end"] - 0.02, hi)])
                cur = emin(lo, b["start"] + 0.02)
                forced.append(True)
            elif b["start"] - a["end"] > MAX_PAUSE:
                seg.append([cur, cut_out(k)])
                cur = cut_in(k2)
                forced.append(False)
        seg.append([cur, end])
        # undo shrink-cuts that leave a micro range (a lone "dan" between two cuts reads as a stutter):
        # merge it into the neighbour it is closer to in the source, keeping that pause instead
        # (filler cuts are never undone; a micro range is only merged across a pause-shrink boundary)
        while len(seg) > 1:
            cand = [j for j in range(len(seg)) if seg[j][1] - seg[j][0] < MICRO
                    and ((j > 0 and not forced[j - 1]) or (j + 1 < len(seg) and not forced[j]))]
            if not cand:
                break
            i = min(cand, key=lambda j: seg[j][1] - seg[j][0])
            left = seg[i][0] - seg[i - 1][1] if i > 0 and not forced[i - 1] else float("inf")
            right = seg[i + 1][0] - seg[i][1] if i + 1 < len(seg) and not forced[i] else float("inf")
            j = i - 1 if left <= right else i + 1
            a, b = sorted((i, j))
            seg[a:b + 1] = [[seg[a][0], seg[b][1]]]
            del forced[a]
        for n, (s0, e0) in enumerate(seg):
            r = {"source": SRC, "start": round(s0, 3), "end": round(e0, 3), "beat": beat}
            if "gain_db" in opt:
                r["gain_db"] = opt["gain_db"]
            if n == len(seg) - 1:
                r["reason"] = note
            ranges.append(r)

    # ranges that touch in the source (island boundaries with no real gap) are one take: merge them,
    # or the renderer's 30ms edge fades would put an audible dip mid-word
    merged = []
    for r in ranges:
        if merged and merged[-1]["end"] >= r["start"] - 0.02 and merged[-1].get("gain_db") == r.get("gain_db"):
            merged[-1]["end"] = r["end"]
            if "reason" in r:
                merged[-1]["reason"] = r["reason"]
        else:
            merged.append(r)
    ranges = merged
    z, zi = ZOOMS[0], 0
    for i, r in enumerate(ranges):
        assert r["end"] - r["start"] > 0.15, r
        if i and r["end"] - r["start"] >= PUNCH_MIN:
            zi = (zi + 1) % len(ZOOMS)
            z = ZOOMS[zi]
        r["zoom"] = z
    total = sum(r["end"] - r["start"] for r in ranges)
    edl = {"version": 1, "sources": {SRC: SRC_PATH}, "ranges": ranges, "grade": "subtle",
           "zoom_focus": FACE, "tail_hold": TAIL_HOLD, "overlays": [],
           "total_duration_s": round(total + TAIL_HOLD, 2)}
    (E / "edl.json").write_text(json.dumps(edl, indent=2, ensure_ascii=False))
    print(f"{len(SEGMENTS)} segments -> {len(ranges)} ranges, total {total:.1f}s ({int(total // 60)}:{total % 60:04.1f})")


if __name__ == "__main__":
    main()
