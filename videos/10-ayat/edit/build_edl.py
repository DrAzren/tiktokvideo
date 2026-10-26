"""Build edl.json for '10 Ayat Dilarang Cakap' from forced-aligned words.

Same method as videos/ward-psikiatri/edit/build_edl.py. Differences for this clip:
  - Recorded in a car: the noise floor in pauses sits ~-35 dB, so edges snap on the
    band-passed (200-4000 Hz) envelope env_bp_db.npy, not the broadband one.
  - '*' tokens (hesitations, "Ha", "eee", breaths) are always cut: a '*' inside a segment
    forces a cut at each neighbour's own edge.
  - Punch-ins are NOT rendered into cut.mp4: the speaker is matted and composited over the
    studio background later, so each range carries "punch" (1.0/1.15/1.30) for the
    composition (the background zooms less than the speaker, for parallax).
"""

import json
from pathlib import Path

import numpy as np

E = Path(__file__).parent
SRC = "src"
SRC_PATH = str((E.parent / "raw" / "10 Ayat Dilarang Cakap.mp4").resolve())

QUIET_DB = -36.0     # band-passed envelope below this for QUIET_RUN frames = word really ended/not begun
QUIET_RUN = 3        # 30ms
TAIL_OUT, LEAD_IN = 0.06, 0.04   # extra air kept after offset / before onset
MAX_SNAP = 0.25      # never move more than this from the aligned word edge
TIGHT = 0.16
MAX_PAUSE = 0.30     # gaps between kept words longer than this get shrunk (TikTok pace)
PUNCH = [1.0, 1.15, 1.0, 1.30]  # punch-in levels cycled across jump cuts
PUNCH_MIN = 0.8      # ranges shorter than this keep the previous punch (no flicker)
MICRO = 0.7          # a pause-shrink cut that leaves a range shorter than this is undone (no stutter)
TAIL_HOLD = 3.0      # hold the last frame so the end card ("Kata-Kata Kita Ada Kesan") can land
FACE = [0.50, 0.40]  # punch focus: face centre as a fraction of the frame

# (island_a, word_a, island_b, word_b, beat, note[, {"start"/"end": override s, "gain_db": dB}])
SEGMENTS = [
    ("I01", 0, "I01", 13, "HOOK", "Sepuluh ayat yang tak patut kita cakap pada orang yang mengalami masalah kesihatan mental."),
    # "satu" runs 5.25-5.72 (the aligner clipped both ends)
    ("I02", 0, "I02", 7, "S01", "Satu, kau ni terlalu fikir banyak sangat.", {"start": 5.20}),
    ("I03", 0, "I03", 15, "S01", "Masalah mental ni dia bukan semata-mata overthinking ... di dalam otak."),
    ("I03", 16, "I04", 8, "S02", "Yang kedua, ramai lagi orang lain yang lagi teruk daripada kau."),
    ("I05", 0, "I05", 20, "S02", "Ini boleh buatkan seorang itu rasa perasaan dia tak valid ... masing-masing."),
    ("I05", 21, "I05", 34, "S03", "Yang ketiga, kau ni manja sangat, sebab tu boleh jadi sampai macam ni."),
    ("I06", 0, "I06", 21, "S03", "Ni pun boleh menambahkan perasaan malu ... masalah kesihatan mental dia tu."),
    ("I07", 0, "I08", 10, "S04", "Yang keempat, kau ni doa je lebih sikit, nanti baiklah tu. — 'Ha' cut"),
    ("I09", 0, "I09", 13, "S04", "Betul, doa tu penting, tapi ... sokongan daripada profesional."),
    ("I10", 0, "I11", 4, "S05", "Yang kelima, kau ni dah gila eh."),
    ("I11", 5, "I11", 27, "S05", "Yang ni stigma macam ni yang menyakitkan ... masalah kesihatan mental. — 'dia' cut"),
    ("I12", 1, "I13", 7, "S06", "Yang keenam, kau ambik je cuti, nanti okeylah tu."),
    # "sembuh" ends ~75.06, a voiced "mmm" runs 75.17-75.45 and "dia" starts ~75.47
    ("I13", 9, "I13", 22, "S06", "Okey, rehat penting, tapi ini bukan semudah ambik cuti dan terus sembuh. — 'eh… err' cut", {"end": 75.12}),
    ("I14", 0, "I14", 9, "S06", "Dia memerlukan satu proses untuk pemulihan masalah kesihatan mental ni. — 'eee' after 'proses' cut", {"start": 75.45}),
    ("I14", 10, "I15", 6, "S07", "Yang ketujuh, semua ni ada dalam kepala je."),
    ("I16", 0, "I16", 19, "S07", "Kesihatan mental ni dia bukanlah benda yang main-main ... fungsi harian seseorang."),
    ("I18", 0, "I18", 26, "S08", "Yang kelapan, jangan tunjuk sangatlah ... memperburukkan lagilah keadaan. — first 'Yang ke lapan' take dropped"),
    ("I18", 27, "I19", 4, "S09", "Yang kesembilan, kau kenalah kuat sikit."),
    ("I20", 0, "I20", 18, "S09", "Orang yang ada masalah mental ni pun dah kuat sebenarnya ... dalam kehidupan mereka."),
    ("I21", 1, "I22", 5, "S10", "Yang kesepuluh, kau ni macam cari perhatian je. — drawn 'eee' before it cut"),
    # "mereka" ends 127.85; the "bu-" of the dropped "bukan being judgemental" starts right after
    ("I22", 6, "I23", 7, "S10", "Sebenarnya mereka ni sedang cari bantuan. Kita ni yang patut tunjuk empati kepada mereka,", {"end": 127.88}),
    # one continuous phrase: the aligner split "judge" late; large-v3 hears it from 133.16
    ("I24", 2, "I24", 4, "S10", "bukan judge mereka. — 'bukan being judgemental, bukan… apa' false start cut", {"noshrink": True}),
    ("I25", 1, "I25", 2, "END", "Kesimpulan dia, — 'okey' before and after cut"),
    ("I26", 0, "I26", 31, "END", "Kalau kita tak tahu nak cakap apa ... masalah kesihatan mental ni."),
    ("I26", 32, "I26", 42, "CTA", "Kalau ada apa-apa soalan, boleh tanya dalam komen. Take care."),
]

# padding words dropped from inside kept segments (user-approved list); '*' tokens are added in main()
# Only drops with a clean boundary survive (spectrogram check, verify/drops.png): "ni dia bukan",
# "tapi dia melibatkan", "mental dia tu", "ni dia bukanlah" and "lagi lah keadaan" are fused into
# the next word with no energy dip, so cutting them would sound stitched; they stay.
DROP = {
    ("I11", 17),                     # "tapi dia sebenarnya" (a drawn 0.4s "diaaa")
}
# voiced hesitations ("eee", drawn vowels) filling gaps between two kept words: always cut.
# Given as the word BEFORE the gap.
HESITATE = {("I14", 3)}              # "proses ...eee... untuk"


def main() -> None:
    db = np.load(E / "env_bp_db.npy")
    dur = len(db) / 100
    al = json.loads((E / "aligned.json").read_text())
    flat = sorted(
        ({"iid": iid, "i": i, **w} for iid, v in al.items() for i, w in enumerate(v["words"])),
        key=lambda w: w["start"],
    )
    pos = {(w["iid"], w["i"]): k for k, w in enumerate(flat)}
    drop = DROP | {(w["iid"], w["i"]) for w in flat if w["text"] == "*"}

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
        keep = [k for k in range(ka, kb + 1) if (flat[k]["iid"], flat[k]["i"]) not in drop]
        for k, k2 in zip(keep, keep[1:]):  # shrink long gaps (breaths); cut dropped words and hesitations
            a, b = flat[k], flat[k2]
            dropped = k2 != k + 1
            hes = (a["iid"], a["i"]) in HESITATE
            only_noise = dropped and all(flat[j]["text"] == "*" for j in range(k + 1, k2))
            if only_noise and not hes:
                # only '*' between them (a pause, breath or "eee"): CTC word ends run ~0.1s early,
                # so let each edge follow its own word's energy a little past the aligned edge
                o = snap_out(a["end"], min(a["end"] + 0.12, b["start"] - 0.02))
                i_ = snap_in(b["start"], max(b["start"] - 0.10, a["end"] + 0.02))
                if o < i_:
                    seg.append([cur, o])
                    cur = i_
                    forced.append(True)
                    continue
            if dropped or hes:
                # the neighbour is a filler/voiced hesitation, so energy never goes quiet: cut at the
                # deepest dip right at each word's own edge
                seg.append([cur, emin(a["end"] - 0.02, a["end"] + 0.07)])
                cur = emin(b["start"] - 0.07, b["start"] + 0.02)
                forced.append(True)
            elif b["start"] - a["end"] > MAX_PAUSE and not opt.get("noshrink"):
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

    # touching/overlapping neighbours (two segments that meet in the source, or a cut around a
    # 40ms '*') play straight through: no cut, no repeated audio, no punch change
    merged = [ranges[0]]
    for r in ranges[1:]:
        if r["start"] <= merged[-1]["end"] + 0.08:
            merged[-1]["end"] = r["end"]
            if "reason" in r:
                merged[-1]["reason"] = (merged[-1].get("reason", "") + " / " + r["reason"]).lstrip(" /")
        else:
            merged.append(r)
    ranges = merged

    z, zi = PUNCH[0], 0
    for i, r in enumerate(ranges):
        assert r["end"] - r["start"] > 0.15, r
        if i and r["end"] - r["start"] >= PUNCH_MIN:
            zi = (zi + 1) % len(PUNCH)
            z = PUNCH[zi]
        r["punch"] = z
    total = sum(r["end"] - r["start"] for r in ranges)
    edl = {"version": 1, "sources": {SRC: SRC_PATH}, "ranges": ranges, "grade": "none",
           "punch_focus": FACE, "tail_hold": TAIL_HOLD, "overlays": [],
           "total_duration_s": round(total + TAIL_HOLD, 2)}
    (E / "edl.json").write_text(json.dumps(edl, indent=2, ensure_ascii=False))
    print(f"{len(SEGMENTS)} segments -> {len(ranges)} ranges, total {total:.1f}s ({int(total // 60)}:{total % 60:04.1f})")


if __name__ == "__main__":
    main()
