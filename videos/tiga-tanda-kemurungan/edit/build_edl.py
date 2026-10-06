"""Build edl.json for 'Tiga Tanda Kemurungan Yang Anda Tak Perasan' from forced-aligned words.

Template: videos/ward-psikiatri/edit/build_edl.py (same edge rules, same DROP/HESITATE mechanics).
Segments reference aligned.json words as (island, first_word, island, last_word).
Edge rules (CTC word ends run ~0.1s early, so edges snap to real audio energy):
  - OUT: first point after the word where energy stays below QUIET_DB, plus a
         short tail; never past the next word. IN mirrors this.
  - If the neighbouring (dropped) word is within TIGHT s, cut at the energy
    minimum between the two words instead.
  - Gaps longer than MAX_PAUSE between kept words are shrunk the same way.
"""

import json
import sys
from pathlib import Path

import numpy as np

E = Path(__file__).parent
SRC = "tiga"
SRC_PATH = str((E.parent / "raw" / "Tiga Tanda Kemurungan.mp4").resolve())

QUIET_DB = -40.0     # below this for QUIET_RUN frames = the word has really ended/not begun
QUIET_RUN = 3        # 30ms
TAIL_OUT, LEAD_IN = 0.06, 0.04   # extra air kept after offset / before onset
MAX_SNAP = 0.35      # never move more than this from the aligned word edge
TIGHT = 0.16
MAX_PAUSE = 0.40     # gaps between kept words longer than this get shrunk (TikTok pace)
ZOOMS = [1.0, 1.06, 1.02, 1.07]  # punch-in levels cycled across jump cuts (user: 1.0/1.02/1.06/1.07, varied order)
PUNCH_MIN = 0.8      # ranges shorter than this keep the previous zoom (no flicker)
MICRO = 0.7          # a pause-shrink cut that leaves a range shorter than this is undone (no stutter)
TAIL_HOLD = 1.2      # freeze the last frame so the end card / CTA can land
FACE = [0.49, 0.45]  # zoom focus: face centre as a fraction of the frame (measured on the contact sheet)

# CTA: the moved clinic plug and the original CTA both offer "konsultasi dan saringan".
#   "short": plug + "Boleh klik di bio." + outro (drops the duplicate "Kalau perlukan bantuan untuk
#            mendapatkan konsultasi dan saringan kesihatan mental bersama saya, Doktor Azren")
#   "full":  plug + the whole original CTA + outro
CTA = "short"

# (island_a, word_a, island_b, word_b, beat, note[, {"start"/"end": override s, "gain_db": dB}])
HOOK_TO_SIGN6 = [
    ("I00", 1, "I00", 11, "HOOK", "Kalau tiga tanda-tanda yang saya sebut ni ada pada anda,"),
    ("I01", 0, "I01", 14, "HOOK", "ini mungkin bukan penat yang biasa. Ini mungkin tanda kemurungan yang ramai orang tak perasan."),
    ("I02", 0, "I02", 6, "HOOK", "Yang nombor tiga yang paling common. — 'tu', 'sebenarnya' cut"),
    ("I02", 8, "I02", 57, "SIGN1", "Nombor satu ... nak bangun pun tak ada tenaga. — 'ha dia', 'ke apa', 'dia', 'ha', 'ke', 'tu', 4x 'dah' cut"),
    ("I03", 0, "I03", 36, "SIGN2", "Yang kedua ... sekarang semua rasa kosong. — 'eee', 3x 'dah', 'macam', 2x 'ke', 'ni', 'tu' cut"),
    ("I04", 0, "I04", 16, "SIGN2", "Yang ni yang kita panggil sebagai anhedonia ... menggembirakan anda. — 'Iklan' + clinic plug (48.5-64.7) moved to the end"),
    ("I07", 3, "I07", 4, "SIGN3", "Nombor tiga. — 3x 'Okey kita sambung' + false start 'Bangun' cut"),
    ("I09", 3, "I09", 13, "SIGN3", "Bila bangun pagi, benda pertama yang kita capai adalah telefon."),
    ("I10", 1, "I10", 25, "SIGN3", "bukan nak scroll pun ... hati ataupun mood yang tak stabil. — 'sebenarnya', first 'hati … tak stabil', 'tu' cut"),
    ("I11", 0, "I11", 6, "SIGN4", "Yang keempat, mood swing yang teruk. — hesitation cut; 'Bukan macam apa panggil? Mood swing yang teruk' retake dropped"),
    ("I13", 4, "I13", 27, "SIGN4", "Kejap pagi rasa okey ... tanpa sebab yang jelas. — 2x 'macam', 'tu' cut"),
    ("I14", 0, "I14", 7, "SIGN5", "Yang kelima, mudah lupa dan susah fokus."),
    ("I15", 0, "I15", 14, "SIGN5", "Baca satu benda sampai tiga kali pun tak boleh nak ingat. Otak jadi serabut — 'atau orang otak jadi serabut' retake dropped"),
    ("I18", 0, "I18", 6, "SIGN5", "atau kita panggil sebagai brain fog."),
    ("I19", 0, "I20", 14, "SIGN6", "Nombor enam ... membuatkan kita rasa frustrated. — 'dia' + hesitations cut"),
    ("I20", 15, "I20", 33, "CLOSE", "Kalau tanda-tanda ni makin kerap ... sama penting dengan kesihatan fizikal. — 'ni sebenarnya' cut"),
]
PLUG = [("I06", 4, "I06", 47, "PLUG", "Kalau anda rasa banyak tanda-tanda ni ... rawatan apa yang sesuai untuk anda. — moved from 0:49; false start 'Kalau anda rasa' (49.4s) cut")]
CTA_LINES = {
    "short": [("I22", 12, "I22", 15, "CTA", "Boleh klik di bio.")],
    "full": [("I21", 0, "I21", 2, "CTA", "Kalau perlukan bantuan"),
             ("I22", 0, "I22", 15, "CTA", "untuk mendapatkan konsultasi ... Doktor Azren, boleh klik di bio.")],
}
OUTRO = [("I23", 0, "I23", 7, "CTA", "Apa persoalan boleh tanya di dalam komen. Take care.", {"end": 160.10})]
SEGMENTS = HOOK_TO_SIGN6 + PLUG + CTA_LINES[CTA] + OUTRO

# filler words dropped from inside kept segments (listed to the user before cutting)
DROP = {
    ("I02", 3),                                           # "nombor tiga tu yang"
    ("I02", 17), ("I02", 25), ("I02", 26), ("I02", 27),   # "ha dia bukan", "diet ke apa", "dia skip"
    ("I02", 31), ("I02", 40), ("I02", 43),                # "sebab dah tak ada", "malas ke tapi", "badan dah rasa"
    ("I02", 47), ("I02", 48), ("I02", 54),                # "minda tu dah rasa", "pun dah tak ada"
    ("I03", 2),                                           # "eee" after "yang kedua"
    ("I03", 9), ("I03", 14), ("I03", 16),                 # "sekarang dah tak", "apa-apa dah", "kalau macam dulu"
    ("I03", 23), ("I03", 27),                             # "drama ke", "luar ke"
    ("I03", 31), ("I03", 33), ("I03", 34),                # "sekarang ni semua tu dah rasa kosong"
    ("I06", 7), ("I06", 9), ("I06", 40),                  # hesitations "rasa * banyak * tanda", "kita * bincangkan"
    ("I09", 6),                                           # sound after "bila bangun pagi"
    ("I10", 16), ("I10", 17), ("I10", 18), ("I10", 19),   # first "hati … tak stabil" (restarted as "hati ataupun mood")
    ("I11", 2),                                           # hesitation after "yang keempat"
    ("I13", 8), ("I13", 13),                              # sounds after "okey", "murung"
    ("I13", 15), ("I13", 17), ("I13", 21),                # "malam macam rasa macam", "emosi tu"
    ("I14", 2),                                           # sound after "yang kelima"
    ("I15", 12),                                          # sound inside "otak * jadi"
    ("I18", 1),                                           # hesitation "atau * kita"
    ("I20", 27), ("I20", 28),                             # "kesihatan mental ni sebenarnya sama penting"
}
# voiced hesitations ("aa", "mmm", drawn-out vowels) filling short gaps (gap_scan.py): always cut,
# whatever the gap length. Given as the word BEFORE the gap.
HESITATE = {("I02", 9), ("I02", 36), ("I06", 38), ("I15", 2), ("I19", 3), ("I19", 9), ("I20", 4)}

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
