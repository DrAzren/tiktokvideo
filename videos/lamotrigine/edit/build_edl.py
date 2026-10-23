"""Build edl.json for 'Ubat Psikiatri Lamotrigine' from forced-aligned words.

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
SRC = "lamo"
SRC_PATH = str((E.parent / "raw" / "Ubat Psikiatri Lamotrigine.mp4").resolve())

QUIET_DB = -46.0     # below this for QUIET_RUN frames = the word has really ended/not begun
                     # (-40 cut audible decays: speech peaks near -6 dB here)
QUIET_RUN = 3        # 30ms
TAIL_OUT, LEAD_IN = 0.10, 0.07   # extra air kept after offset / before onset (soft f/s/h onsets sit
                                 # 20-40 ms before the -40 dB rise, e.g. 'fasa' at 113.155)
MIN_CUT = 0.06       # a pause-shrink that would remove less than this is skipped (jump + fade for nothing)
MAX_SNAP = 0.45      # never move more than this from the aligned word edge
TIGHT = 0.16
MAX_PAUSE = 0.20     # gaps between kept words longer than this get shrunk (round 2: user heard 0.3 s gaps as delays)
ZOOMS = [1.0, 1.07, 1.02, 1.08, 1.035]  # punch-in levels cycled across jump cuts (varied, not ping-pong)
PUNCH_MIN = 0.8      # ranges shorter than this keep the previous zoom (no flicker)
SPEECH_DB = -30.0    # energy pass: below this = not speech (silence, breath, decayed tail)
PAUSE_MAX = 0.17     # non-speech runs inside a range longer than this are cut down to KEEP_A + KEEP_B
KEEP_A, KEEP_B = 0.08, 0.05
TAIL_CAP, HEAD_CAP = 0.09, 0.07   # quiet kept after the last sound / before the first, at every join
MICRO = 0.4         # a pause-shrink cut that leaves a range shorter than this is undone (no stutter)
TAIL_HOLD = 1.5      # freeze the last frame so the SPREAD POSITIVITY end card can land
FACE = [0.50, 0.38]  # zoom focus: face centre as a fraction of the frame (face sits high in this shot)

# (island_a, word_a, island_b, word_b, beat, note[, {"start"/"end": override s, "gain_db": dB}])
SEGMENTS = [
    # 'Kalau' onset at 0.56: start earlier so the k stays clear of the 30ms fade
    ("HOOK", 0, "HOOK", 34, "HOOK", "Kalau cakap pasal ubat yang stabilkan mood ... Pernah dengar tak pasal ubat ni?",
     {"start": 0.50}),
    # clinic ad 14.0-35.8 ('Iklan, kalau anda ada masalah ...') dropped: the CTA at 2:17 says the same
    ("FAMOUS", 5, "EPISOD", 4, "WHAT", "Lamotrigine ni dia famous ... terutamanya dalam episod kemurunganlah. — 'Okey, berbalik pada topik tadi' dropped"),
    ("WEIGHT", 0, "WEIGHT", 18, "WHY", "Dan risiko kenaikan berat badan ... ramai pasien yang suka dengan ubat ni. — false start 57.1-58.5 cut"),
    ("DROWSY", 0, "DROWSY", 43, "WHY", "Ubat ni juga dia tak buat rasa mengantuk ... side effect dia juga. — 'And ubat ni pula' dropped"),
    ("TITRATE", 0, "TITRATE", 36, "SAFETY", "Ubat ni dia kena start dengan dos yang rendah ... boleh berlakulah dengan ubat ni."),
    ("SIDEFX", 3, "SIDEFX", 22, "SIDEFX", "Dan boleh menyebabkan side effect yang biasa ... susah tidur. — false starts around it cut"),
    ("RETAKE", 5, "MANIA", 22, "LIMITS", "Dan ubat ni juga dia tak begitu kuat ... tanpa advice doktor. — first take 'dia tak begitu kuat / dan ubat ni juga' cut"),
    ("SUMMARY", 22, "SUMMARY", 33, "RECAP", "Tapi kena ingat, ubat ni juga ada cara guna dia yang selamat. — recap 'So Lamotrigine ni basically ... fasa kemurungan' dropped (repeats 0:13)"),
    ("SUMMARY", 34, "BYE", 8, "CTA", "Kalau anda rasa struggle ... Take care.", {"end": None}),
]

# filler words dropped from inside kept segments
DROP = {
    ("WEIGHT", 8),                  # "sangat rendah sebenarnya"
    ("WEIGHT", 11),                 # '*' = false start "ramai pasien yang suka" (57.1-58.5), restarted at 59.4
    ("TITRATE", 30),                # "dia rare sebenarnya tapi"
    ("SIDEFX", 8), ("SIDEFX", 9),   # repeated "side effect side effect"
    ("MANIA", 12),                  # "ada sama seperti" -> "Sama seperti ubat lain"
}
# voiced hesitations ("mmm", drawn-out vowels) filling short gaps: always cut, whatever the gap length.
# Given as the word BEFORE the gap.
HESITATE = {("HOOK", 26)}   # "sebenarnya" -> loud "haa" burst 10.965-11.38 -> "iaitu"

# aligned word edges corrected from the 5 ms envelope / zero-crossing check (MMS placed these late)
WORD_FIX = {
    ("WEIGHT", 10): (56.90, 57.00),   # "tu": silence 57.01-57.035, then the false-start "ramai" from 57.04
    ("HOOK", 26): (10.50, 10.93),     # "sebenarnya": decays to -55 dB at 10.945; the burst starts at 10.965
}
# explicit cut points where an /s/ onset defeats the energy-minimum rule (the hiss is quieter than the
# vowel before it, so the minimum lands inside the s). Keyed by the kept word; from the 5 ms ZCR check.
CUT_OUT = {("WEIGHT", 7): 56.255,    # "rendah" | dropped "sebenarnya" (its s starts 56.26)
           ("DROWSY", 31): 73.475,   # "doktor lah" decays to -60 dB at 73.47; the breathy "ha" filler starts 73.485
           ("TITRATE", 29): 90.91}   # "rare" | dropped "sebenarnya": deepest dip (-27 dB) of the r->s transition
CUT_IN = {("WEIGHT", 9): 56.700,     # "sebab" (its s starts 56.708)
          ("FAMOUS", 5): 43.585}     # "Lamotrigine" after dropped "tadi": MMS character peaks put tadi's d/i at
                                     # 43.45/43.51 and the l at 43.63; the bright /i/ ends ~43.59 (spectral centroid),
                                     # so earlier starts (43.48, 43.42) kept "di" (large-v3 heard "Di"/"Jadi")


def main() -> None:
    db = np.load(E / "env_db.npy")
    dur = len(db) / 100
    al = json.loads((E / "aligned.json").read_text())
    for (iid, i), (s0, e0) in WORD_FIX.items():
        al[iid]["words"][i].update(start=s0, end=e0)
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
        if (w["iid"], w["i"]) in CUT_IN:
            return CUT_IN[(w["iid"], w["i"])]
        prev = flat[k - 1] if k > 0 else None
        if prev and w["start"] - prev["end"] < TIGHT:
            return between(prev, w)
        return snap_in(w["start"], prev["end"] + 0.02 if prev else 0.0)

    def cut_out(k: int) -> float:
        w = flat[k]
        if (w["iid"], w["i"]) in CUT_OUT:
            return CUT_OUT[(w["iid"], w["i"])]
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
        print(f"  {beat:7s} {flat[ka]['text']} ... {flat[kb]['text']}")  # eyeball: stale indices show up here
        start = opt.get("start") or cut_in(ka)
        end = opt.get("end") or cut_out(kb)
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
                # CTC ends run ~0.1 s early, so a fixed +0.07 s window cut word tails ("rare" heard as "red").
                # Search from the word's aligned end to the START of whatever follows it in the source (the
                # dropped word / hesitation), and mirror that for the next kept word.
                nxt, prv = flat[k + 1], flat[k2 - 1]
                out_hi = max(nxt["start"] + 0.03, a["end"] + 0.06)
                in_lo = min(prv["end"] - 0.03, b["start"] - 0.06)
                seg.append([cur, CUT_OUT.get((a["iid"], a["i"])) or emin(a["end"] - 0.02, out_hi)])
                cur = CUT_IN.get((b["iid"], b["i"])) or emin(max(in_lo, seg[-1][1] + 0.02), b["start"] + 0.02)
                forced.append(True)
            elif b["start"] - a["end"] > MAX_PAUSE:
                seg.append([cur, cut_out(k)])
                cur = cut_in(k2)
                forced.append(False)
        seg.append([cur, end])
        k = 0
        while k < len(seg) - 1:  # skip pause-shrinks that remove almost nothing
            if not forced[k] and seg[k + 1][0] - seg[k][1] < MIN_CUT:
                seg[k:k + 2] = [[seg[k][0], seg[k + 1][1]]]
                del forced[k]
            else:
                k += 1
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

    # ranges that touch in the source (one segment ending where the next begins) play as one: no fade dip
    merged = []
    for r in ranges:
        if merged and abs(r["start"] - merged[-1]["end"]) < 1 / 30:
            merged[-1]["end"] = r["end"]
            if "reason" in r:
                merged[-1]["reason"] = merged[-1].get("reason", "") + " | " + r["reason"]
        else:
            merged.append(r)
    ranges = merged

    # round 2: energy-based pause tightening (the aligner's early word ends hid real gaps). Non-speech is
    # < SPEECH_DB; every such run inside a range longer than PAUSE_MAX is cut to KEEP_A + KEEP_B, and at each
    # join the quiet tail / head is capped (TAIL_CAP after the last sound, HEAD_CAP before the first).
    tight = []
    for r in ranges:
        a0, b0 = int(round(r["start"] * 100)), int(round(r["end"] * 100))
        a, b = a0, b0
        loud = np.flatnonzero(db[a0:b0] >= SPEECH_DB)
        if len(loud):
            if r is not ranges[0]:
                a = max(a0, a0 + loud[0] - int(HEAD_CAP * 100))
            b = min(b0, a0 + loud[-1] + 1 + int(TAIL_CAP * 100))
        pieces, cur, i = [], a, a
        while i < b:
            if db[i] < SPEECH_DB:
                j = i
                while j < b and db[j] < SPEECH_DB:
                    j += 1
                if (j - i) / 100 >= PAUSE_MAX and i > a and j < b:
                    pieces.append((cur, i + int(KEEP_A * 100)))
                    cur = j - int(KEEP_B * 100)
                i = j
            else:
                i += 1
        pieces.append((cur, b))
        for n, (s0, e0) in enumerate(pieces):
            q = dict(r, start=round(s0 / 100, 3), end=round(e0 / 100, 3))
            if n < len(pieces) - 1:
                q.pop("reason", None)
            tight.append(q)
    ranges = tight

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
