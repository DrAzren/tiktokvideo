"""Build edl.json for 'Ubat Psikiatri Olanzapine' from forced-aligned words.

Template: videos/ward-psikiatri/edit/build_edl.py. Segments reference aligned.json words as
(island, first_word, island, last_word).
Edge rules (CTC word ends run ~0.1s early, so edges snap to real audio energy):
  - OUT: first point after the word where energy stays below QUIET_DB, plus a
         short tail; never past the next word. IN mirrors this.
  - If the neighbouring (dropped) word is within TIGHT s, cut at the energy
    minimum between the two words instead.
  - Gaps longer than MAX_PAUSE between kept words are shrunk the same way.
Recorded in a car: the pause floor sits at -30..-25 dB (vs -50 in the ward clip), so QUIET_DB is -26.
"""

import json
from pathlib import Path

import numpy as np

E = Path(__file__).parent
SRC = "olanzapine"
SRC_PATH = str((E.parent / "raw" / "Olanzapine.mp4").resolve())

QUIET_DB = -26.0     # below this for QUIET_RUN frames = the word has really ended/not begun (car noise floor ~-30)
QUIET_RUN = 3        # 30ms
TAIL_OUT, LEAD_IN = 0.05, 0.04   # extra air kept after offset / before onset
MAX_SNAP = 0.35      # never move more than this from the aligned word edge
TIGHT = 0.16
MAX_PAUSE = 0.40     # gaps between kept words longer than this get shrunk (TikTok pace)
ZOOMS = [1.0, 1.06, 1.02, 1.07]  # punch-in levels cycled across jump cuts (user: 1.0 / 1.02 / 1.06 / 1.07)
PUNCH_MIN = 0.45     # ranges shorter than this keep the previous zoom (no flicker); 0.8 left 6 jump cuts undisguised
MICRO = 0.7          # a pause-shrink cut that leaves a range shorter than this is undone (no stutter)
TAIL_HOLD = 1.2      # freeze the last frame so the end card / CTA can land
FACE = [0.52, 0.40]  # zoom focus: face centre as a fraction of the frame

# (island_a, word_a, island_b, word_b, beat, note[, {"start"/"end": override s, "gain_db": dB}])
SEGMENTS = [
    ("I00", 1, "I00", 5, "HOOK", "Pernah dengar nama ubat olanzapine?"),
    # "Ada patient panggil…" (3.8-4.95) is never finished (5.5s silence after it): dropped, user's call
    ("I02", 1, "I02", 10, "HOOK", "Jom saya terangkan apa kebaikan dan keburukan ubat ni. — plug take 1 (16.9-29.5) + dead air dropped"),
    ("I05", 1, "I05", 29, "KEBAIKAN", "Pertama, kebaikan… gangguan psikosis."),
    ("I06", 0, "I06", 20, "KEBAIKAN", "Ia boleh kurangkan halusinasi… tidur seseorang."),
    ("I07", 1, "I07", 14, "KEBAIKAN", "Ia berguna kalau pesakit… insomnia."),
    ("I08", 1, "I08", 23, "KEBAIKAN", "Ada juga yang cakap dunia kembali senyap… penyakit-penyakit tertentu."),
    ("I09", 0, "I09", 55, "KEBURUKAN", "Tapi kita kena tahu juga kesan sampingan… start rawatan dulu."),
    ("I10", 0, "I10", 28, "KEBURUKAN", "Yang ketiga… ambil ubat olanzapine ni. — 9s pause after it cut"),
    ("I11", 1, "I11", 10, "PENUTUP", "Yang penting, kita jangan stop ubat sendiri. Jangan give up."),
    ("I04", 4, "I04", 41, "PLUG", "Kalau anda mula ambil ubat psikiatri… secara one on one. — moved from 0:37 to the end; "
                                  "'Tapi jangan risau' and 'boleh tekan di bio untuk book slot anda' (said again in the CTA) dropped"),
    ("I11", 11, "I12", 9, "CTA", "Kalau anda perlukan bantuan, boleh tekan di bio atau DM untuk buat appointment. — repeated 'boleh' cut"),
    ("I13", 0, "I13", 8, "CTA", "Kalau ada soalan, boleh tanya dalam komen. Take care."),
]

# filler words dropped from inside kept segments
DROP = {
    ("I02", 5),                                   # "apa sebenarnya kebaikan"
    ("I04", 6),                                   # "kalau anda ada mula ambil"
    ("I04", 32),                                  # breath between "kami ada buat" and "konsultasi"
    ("I05", 12),                                  # "sangat bagus sebenarnya tidak dinafikan"
    ("I06", 9),                                   # "otak seseorang itu jadi"
    ("I07", 3),                                   # "berguna lah"
    ("I08", 6), ("I08", 7),                       # "dunia dia dah kembali senyap"
    ("I08", 14), ("I08", 15),                     # "ubat ni [eee] sebenarnya ubat ini"
    ("I09", 19),                                  # "paling common lah"
    *[("I09", i) for i in range(29, 36)],         # "jadi apa yang saya bagi tahu selalunya"
    ("I09", 42),                                  # "seimbang lah"
    ("I10", 24),                                  # "kalau anda ada ambil"
    ("I11", 15),                                  # "bantuan, boleh — boleh tekan" (false start)
}
# voiced hesitations / held vowels filling short gaps: always cut, whatever the gap length.
# Given as the word BEFORE the gap (found by gap_scan.py, checked on spectrograms).
HESITATE = {("I05", 26), ("I06", 4), ("I06", 18), ("I08", 4), ("I08", 10), ("I08", 19),
            ("I09", 14), ("I09", 50), ("I10", 1), ("I10", 22), ("I11", 7)}


def main() -> None:
    db = np.load(E / "env_db.npy")
    dur = len(db) / 100
    al = json.loads((E / "aligned.json").read_text())
    flat = sorted(
        ({"iid": iid, "i": i, **w} for iid, v in al.items() for i, w in enumerate(v["words"])),
        key=lambda w: w["start"],
    )
    pos = {(w["iid"], w["i"]): k for k, w in enumerate(flat)}

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
        if i >= stop:  # never goes quiet (breath/hum follows): cut at the deepest dip
            return emin(t - 0.02, hi)
        return min(limit, i / 100 + TAIL_OUT)

    def snap_in(t: float, floor: float) -> float:
        lo = max(floor, t - MAX_SNAP)
        i, stop = int(t * 100), int(lo * 100)
        while i > stop and not quiet(i - QUIET_RUN):
            i -= 1
        if i <= stop:
            return emin(lo, t + 0.02)
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
            hes = (a["iid"], a["i"]) in HESITATE
            if dropped or hes:
                # the neighbour is a filler/voiced hesitation, so energy never goes quiet: cut at the
                # deepest dip right at each word's own edge
                seg.append([cur, emin(a["end"] - 0.02, a["end"] + 0.07)])
                cur = emin(b["start"] - 0.07, b["start"] + 0.02)
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
