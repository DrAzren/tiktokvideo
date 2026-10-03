"""Build edl.json for 'Borderline Personality Disorder' from forced-aligned words.

Template: videos/ward-psikiatri/edit/build_edl.py. Segments reference aligned.json words as
(island, first_word, island, last_word).
Edge rules (CTC word ends run ~0.1s early, so edges snap to real audio energy):
  - OUT: first point after the word where energy stays below QUIET_DB, plus a
         short tail; never past the next word. IN mirrors this.
  - If the neighbouring (dropped) word is within TIGHT s, cut at the energy
    minimum between the two words instead.
  - Gaps longer than MAX_PAUSE between kept words are shrunk the same way.
This source has continuous handling rumble (~-30 dB on the 150 Hz-6 kHz envelope) under
every pause, so QUIET_DB sits just above that floor instead of at -40.
"""

import json
from pathlib import Path

import numpy as np

E = Path(__file__).parent
SRC = "bpd"
SRC_PATH = str((E.parent / "raw" / "bpd.mp4").resolve())

QUIET_DB = -27.0     # below this for QUIET_RUN frames = the word has really ended/not begun
QUIET_RUN = 3        # 30ms
TAIL_OUT, LEAD_IN = 0.06, 0.04   # extra air kept after offset / before onset
MAX_SNAP = 0.35      # never move more than this from the aligned word edge
TIGHT = 0.16
MAX_PAUSE = 0.45     # gaps between kept words longer than this get shrunk
ZOOMS = [1.0, 1.06, 1.02, 1.07]  # punch-in levels cycled across jump cuts (user's choice)
PUNCH_MIN = 0.6      # ranges shorter than this keep the previous zoom (no flicker); lower than ward: more short ranges here
MICRO = 0.7          # a pause-shrink cut that leaves a range shorter than this is undone (no stutter)
TAIL_HOLD = 1.2      # freeze the last frame so the end card / CTA can land
# zoom focus near the hairline (x of the head, y just below the hair top at ~0.23): punch-ins grow
# the face downward instead of pushing the hair up into the caption line
FACE = [0.45, 0.27]

# aligner fixes: (island, word) -> overrides. "marah" (0:52.8) was stretched over the half-said
# "yang..." that follows it (large-v3: "yang" 53.12-53.66, p=0.47); the word itself ends ~53.2.
WORD_FIX = {("I03", 12): {"end": 53.2}}

# (island_a, word_a, island_b, word_b, beat, note[, {"start"/"end": override s, "gain_db": dB}])
SEGMENTS = [
    ("I00", 0, "I00", 13, "HOOK", "Orang kata BPD ni sekadar moody je, mood swing. Betul ke? — 'dia', 'sekadaaar', 'jeee' cut"),
    ("I01", 0, "I01", 16, "INTRO", "Jom saya explain ... supaya kita lebih faham tentang penyakit ini. — pause + 'jadi' before it, false start 'kita mudah' cut"),
    ("I01", 17, "I01", 44, "T1", "Pertama, orang BPD ni takut ditinggalkan ... terus rasa panik. Yang kedua, — 'dia' x2, 'ke', 'macam', 'waktu tu' cut"),
    ("I01", 45, "I02", 37, "T2", "hubungan mereka ni tak stabil ... Yang ketiga, — 'dia' x2 cut"),
    ("I02", 38, "I03", 12, "T3", "emosi tak stabil ... malam tiba-tiba marah. — 'dia' x2, 'contohnyaaa', 'hepiii' cut"),
    ("I03", 13, "I03", 41, "T4T5", "Yang keempat ... susah nak kawal. — half-said 'yang', 'rasaaa', 'dia', 'dalam jiwa dia tu' cut"),
    ("I04", 3, "I04", 17, "T5", "Tiba-tiba marah yang melampau ... walaupun benda kecil je. — first 'tiba-tiba marah', 'benda tu', 'sebenarnya' cut"),
    ("I04", 19, "I04", 41, "T6", "Nombor enam ... atau self-harm bila stres. — 'ataupun buat sesuatu', 'berbahayaaa' cut"),
    ("I06", 0, "I06", 24, "REASSURE", "Kalau ada tanda-tanda ni bukanlah bermakna anda gila ... memang ada. — retake kept (first take 86.8-92.2s + 8s pause dropped); 'ke apa' + 'eee' cut"),
    ("I06", 25, "I06", 58, "PLUG", "Kalau anda nak buat konsultasi ... insyaAllah kami boleh bantu. — already at the end, before the CTA"),
    ("I06", 59, "I06", 68, "CTA", "Apa-apa soalan boleh tanya di ruang komen. Take care."),
]

# filler words dropped from inside kept segments (user-approved list, 2026-10-03)
DROP = {
    ("I00", 6),                                   # "BPD ni dia sekadar"
    ("I01", 9), ("I01", 10),                      # false start "supaya kita mudah, kita lebih faham"
    ("I01", 21),                                  # "orang BPD ni dia takut"
    ("I01", 31),                                  # "balas WhatsApp ke"
    ("I01", 35),                                  # "rasa macam diabaikan"
    ("I01", 37),                                  # "dia terus rasa panik"
    ("I01", 41), ("I01", 42),                     # "panik waktu tu"
    ("I02", 5),                                   # "dia sekejap rasa orang tu jahat"
    ("I02", 12),                                  # "hubungan dia jadi naik turun"
    ("I02", 42),                                  # "emosi dia turun naik"
    ("I03", 2),                                   # "pagi dia rasa happy"
    ("I03", 26),                                  # "jiwa dia rasa kosong"
    ("I03", 29), ("I03", 30), ("I03", 31), ("I03", 32),   # repeated "dalam jiwa dia tu"
    ("I04", 13), ("I04", 14),                     # "walaupun benda tu benda kecil"
    ("I04", 18),                                  # "sebenarnya" (also outside T5's end word, kept for the record)
    ("I04", 30), ("I04", 31), ("I04", 32),        # false start "ataupun buat sesuatu"
    ("I06", 9), ("I06", 10),                      # "anda gila ke apa"
}
# voiced hesitations / drawn-out word tails ("sekadaaar", "hepiii") filling the gap after a word:
# always cut at the word's own edge, whatever the gap length. Given as the word BEFORE the gap.
HESITATE = {("I00", 7), ("I00", 9), ("I03", 0), ("I03", 4), ("I03", 12), ("I03", 27),
            ("I04", 11), ("I04", 36)}


def main() -> None:
    db = np.load(E / "env_db.npy")
    dur = len(db) / 100
    al = json.loads((E / "aligned.json").read_text())
    flat = sorted(
        ({"iid": iid, "i": i, **w, **WORD_FIX.get((iid, i), {})} for iid, v in al.items() for i, w in enumerate(v["words"])),
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
        assert (ia, wa) not in DROP and (ib, wb) not in DROP, f"segment edge on a dropped word: {note}"
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
                # the cut windows may not reach into the kept neighbour, nor stop short of the dropped
                # word: these "dia"s are 60-100ms and often touch both neighbours
                hi = a["end"] + 0.07 if not dropped else min(a["end"] + 0.07, max(a["end"] + 0.01, flat[k + 1]["start"] + 0.02))
                lo = b["start"] - 0.07 if not dropped else max(b["start"] - 0.07, min(b["start"] - 0.01, flat[k2 - 1]["end"] - 0.02))
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

    # segments that touch in the source (a beat boundary, not a cut) become one range: a split there
    # would put two 30ms edge fades mid-sentence
    merged = []
    for r in ranges:
        if merged and 0 <= merged[-1]["end"] - r["start"] + 0.06 and r["start"] < merged[-1]["end"] + 0.06 \
                and r["start"] > merged[-1]["start"]:
            m = merged[-1]
            m["end"] = max(m["end"], r["end"])
            if "reason" in r:
                m["reason"] = (m.get("reason", "") + " + " + r["reason"]).lstrip(" +")
            continue
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
