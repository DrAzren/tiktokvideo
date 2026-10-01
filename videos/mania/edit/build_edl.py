"""Build edl.json for 'Fasa Mania dalam Bipolar Mood Disorder' from the global forced alignment.

Method as videos/ada-halusinasi-yang-normal/edit/build_edl.py (aligned.json has a '*' slot between
every word pair), with the self-intro deleted.
  - DROP: user-approved filler words, repeats, false starts and the abandoned retake, by (text, time)
  - every '*' slot >= GAP_CUT between kept words is removed (pauses, breaths), and every VOICED '*'
    slot >= VOICED_CUT ("aa/eee/mmm", drawn vowels; scan_gaps.py) — short hesitations inside pauses
    under 0.45s included
  - a jump between kept words (b != a + 1) is a cut

Edge rules: OUT after a word = first point where energy stays below QUIET_DB, + TAIL_OUT, never past
the next source word; if it never goes quiet (a voiced hesitation is glued on) cut at the deepest
energy dip right at the word's own edge. IN mirrors this. Words closer than TIGHT: cut at the dip.
"""

import json
from pathlib import Path

import numpy as np

E = Path(__file__).parent
SRC = "mania"
SRC_PATH = str((E / "source_1080_dc.mov").resolve())  # prep_source.sh: raw 720p30 -> 1080x1920@30, adeclip, PCM

QUIET_DB, QUIET_RUN = -40.0, 3
TAIL_OUT, LEAD_IN = 0.05, 0.04
MAX_SNAP_OUT = 0.12
MAX_SNAP_IN = 0.15
GAP_CUT = 0.20          # any '*' slot this long is cut (aggressive TikTok pace)
VOICED_CUT = 0.15       # a voiced '*' (hesitation sound) this long is cut even inside a short pause
TIGHT = 0.16
MIN_SAVE = 0.15         # a gap cut that saves less than this is undone (a jump for nothing)
ZOOMS = [1.0, 1.02, 1.06, 1.07]   # user: alternate 1.0 / 1.02 / 1.06 / 1.07 on jump cuts
PUNCH_MIN = 0.8
TAIL_HOLD = 1.0
FACE = [0.53, 0.44]     # zoom focus: face centre (fraction of frame), measured on src_20s.png

# (text, approx source start) — filler words, repeats and false starts, user-approved list
DROP = [
    ("okay", 12.2),                                   # "berubah-ubah. Okay, sebelumnya"
    ("dia", 15.5),                                    # "gangguan bipolar ni dia adalah" (large-v3 on the first cut heard it)
    ("okay", 27.4), ("ni", 28.4), ("dia", 28.6),      # "Okay, fasa mania ni dia ada beberapa gejala"
    ("at", 33.3), ("least", 33.6), ("satu", 34.0), ("minggu", 34.4),   # repeat: "at least satu minggu, sekurang-kurangnya satu minggu"
    ("dia", 36.0),                                    # "kalau dia berlaku"
    ("dia", 39.0),                                    # "kita tak panggil dia fasa mania"
    ("jadi", 40.4),                                   # "Jadi apa yang berlaku"
    ("ni", 46.7), ("dia", 46.9),                      # "mengalami mania ni dia akan"
    ("itu", 50.2),                                    # "individu itu akan rasa"
    ("mereka", 54.56), ("ni", 54.86), ("mungkin", 54.98), ("kalau", 56.1), ("kita", 56.26), ("tengok", 56.4),  # false start
    ("dia", 57.6), ("akan", 57.9), ("dia", 61.5),     # "bipolar dia akan, dia akan… dia akan jadi"
    ("dia", 65.3),                                    # "stop percakapan dia"
    ("ni", 71.4), ("tu", 72.9),                       # "dalam fasa mania ni individu tu"
    ("pun", 77.7),                                    # "tak memikirkan pun risiko"
    ("itu", 81.3),                                    # "yang mereka lakukan itu"
    ("ni", 92.3), ("dia", 92.6), ("dia", 94.6),       # "Mereka ni dia rasa dia memiliki"
    ("dia", 97.1), ("tu", 97.2),                      # "keperluan tidur dia tu"
    ("ni", 100.1), ("dia", 100.5),                    # "fasa mania ni tidur dia"
    ("and", 106.6), ("then", 106.8), ("dia", 107.5),  # "And then fikiran dia sangat laju"
    ("itu", 116.7),                                   # "seorang itu mengambil"
    ("tu", 135.8),                                    # "Ada yang saya jumpa tu, dia tak pergi kerja"
    ("penting", 145.8), ("untuk", 146.2), ("diingatkan", 146.4), ("bahawa", 146.8), ("gangguan", 147.4),
    ("bipolar", 147.8),                               # abandoned first take; 2nd "Penting untuk saya ingatkan…" kept
    ("dia", 151.6),                                   # "gangguan bipolar dia memerlukan"
]
# self-intro "Assalamualaikum, saya Doktor Azren, saya merupakan doktor di Jabatan Psikiatri" (0:02-0:05):
# deleted (user) — the video opens cold on the hook "Ramai yang salah faham"
INTRO = (0.0, 5.05)
# hand-checked edges: (word, approx start, "out"/"in") -> cut time
EDGE_AT = {}


def main() -> None:
    db = np.load(E / "env_db.npy")
    dur = len(db) / 100
    al = json.loads((E / "aligned.json").read_text())
    W = al["words"]
    for w in W:   # the CTC span can swallow neighbouring silence: trim it back to the word's energy
        while w["end"] - w["start"] > 0.1 and db[int(w["end"] * 100) - 1] < QUIET_DB:
            w["end"] = round(w["end"] - 0.01, 3)
        while w["end"] - w["start"] > 0.1 and db[int(w["start"] * 100)] < QUIET_DB:
            w["start"] = round(w["start"] + 0.01, 3)
    star_after = {s["after"]: s for s in al["stars"]}
    voiced = {g["after"] for g in json.loads((E / "gaps.json").read_text()) if g["kind"] == "voiced"}

    def find(text, t):
        k = min((w for w in W if w["text"] == text), key=lambda w: abs(w["start"] - t))
        assert abs(k["start"] - t) < 0.6, (text, t, k)
        return k["i"]

    drop = {find(t, s) for t, s in DROP}
    assert len(drop) == len(DROP), "two DROP entries resolved to the same word"
    drop |= {w["i"] for w in W if INTRO[0] <= w["start"] < INTRO[1]}
    order = [w["i"] for w in W if w["i"] not in drop]

    def emin(lo, hi):
        i0, i1 = int(lo * 100), max(int(lo * 100) + 1, int(hi * 100))
        return (i0 + int(np.argmin(db[i0:i1]))) / 100 + 0.005

    def quiet(i):
        return bool(np.all(db[i:i + QUIET_RUN] < QUIET_DB))

    def snap_out(t, limit):
        hi = min(limit, t + MAX_SNAP_OUT)
        i, stop = int(t * 100), int(hi * 100)
        while i < stop and not quiet(i):
            i += 1
        if i >= stop:
            return emin(t - 0.02, min(limit, t + 0.08))
        return min(limit, i / 100 + TAIL_OUT)

    def snap_in(t, floor):
        lo = max(floor, t - MAX_SNAP_IN)
        i, stop = int(t * 100), int(lo * 100)
        while i > stop and not quiet(i - QUIET_RUN):
            i -= 1
        if i <= stop:
            return emin(max(floor, t - 0.07), t + 0.02)
        return max(floor, i / 100 - LEAD_IN)

    def cut_out(a):
        wa = W[a]
        nb = W[a + 1] if a + 1 < len(W) else None
        if nb is None:
            return min(dur, wa["end"] + 0.25)
        if nb["start"] - wa["end"] < TIGHT:
            out = emin(wa["end"] - 0.02, nb["start"] + 0.02)
        else:
            out = snap_out(wa["end"], nb["start"] - 0.02)
        return EDGE_AT.get((wa["text"], round(wa["start"], 1), "out"), out)

    def cut_in(b, floor):
        wb = W[b]
        pb = W[b - 1] if b > 0 else None
        if pb is not None and wb["start"] - pb["end"] < TIGHT:
            t = max(floor, emin(pb["end"] - 0.02, wb["start"] + 0.02))
        else:
            t = snap_in(wb["start"], max(floor, pb["end"] + 0.01 if pb else 0.0))
        return EDGE_AT.get((wb["text"], round(wb["start"], 1), "in"), t)

    ranges, cur = [], cut_in(order[0], 0.0)
    for a, b in zip(order, order[1:]):
        gap = star_after.get(a)
        g = gap["end"] - gap["start"] if gap else 0.0
        jump = b != a + 1
        if jump or g >= GAP_CUT or (a in voiced and g >= VOICED_CUT):
            out = cut_out(a)
            floor = out + 0.01 if b == a + 1 or (b > a and W[b]["start"] > W[a]["end"]) else 0.0
            nxt = cut_in(b, floor if b > a else 0.0)
            if b > a:
                nxt = max(nxt, out + 0.01)
            if jump:
                why = "drop " + " ".join(W[k]["text"] for k in range(a + 1, b))
            else:
                why = f"{'hesitation' if a in voiced else 'gap'} {g:.2f}s"
            ranges.append({"source": SRC, "start": round(cur, 3), "end": round(out, 3), "reason": why})
            cur = nxt
    ranges.append({"source": SRC, "start": round(cur, 3), "end": round(cut_out(order[-1]), 3), "reason": "end"})

    # a gap cut that saves < MIN_SAVE is only a visible jump: undo it (filler/move cuts always stay)
    merged = [ranges[0]]
    for r in ranges[1:]:
        p = merged[-1]
        save = r["start"] - p["end"]
        if 0 <= save < MIN_SAVE and p["reason"].startswith("gap") or 0 <= save < 0.08 and p["reason"].startswith("hesitation"):
            p["end"], p["reason"] = r["end"], r["reason"]
        else:
            merged.append(r)
    ranges = merged

    # a range too short to read (< 0.3s) is merged into its contiguous neighbour
    i = 0
    while i < len(ranges):
        r = ranges[i]
        if r["end"] - r["start"] < 0.3 and len(ranges) > 1:
            cand = [j for j in (i - 1, i + 1) if 0 <= j < len(ranges)
                    and 0 <= (r["start"] - ranges[j]["end"] if j < i else ranges[j]["start"] - r["end"]) < 2.0]
            assert cand, ("short range with no contiguous neighbour", r)
            j = min(cand, key=lambda j: abs(r["start"] - ranges[j]["end"]) if j < i else abs(ranges[j]["start"] - r["end"]))
            lo, hi = sorted((i, j))
            ranges[lo:hi + 1] = [{**ranges[lo], "end": ranges[hi]["end"], "reason": ranges[hi]["reason"]}]
            i = max(0, lo - 1)
            continue
        i += 1

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
    print(f"{len(drop)} words dropped, {len(ranges)} ranges, total {total:.1f}s "
          f"({int(total // 60)}:{total % 60:04.1f}) + {TAIL_HOLD}s hold")
    print("kept text:", " ".join(W[i]["text"] for i in order))


if __name__ == "__main__":
    main()
