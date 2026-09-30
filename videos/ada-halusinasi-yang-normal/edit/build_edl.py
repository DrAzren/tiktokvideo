"""Build edl.json for 'Ada Halusinasi Yang Normal' from the global forced alignment.

The CapCut draft is already one continuous, lightly-trimmed take, so there are no
retakes to choose between. The cut is driven by two user-approved lists:
  - DROP: filler words ("okay", "sebenarnya", "macam", "itu", "jadi"), found by (text, time)
  - every '*' slot >= GAP_CUT between kept words (voiced "eee/mmm", drawn-out vowels,
    breaths, pauses) is removed. aligned.json carries a '*' between every word pair.

Edge rules (as ward-psikiatri, adapted to '*' slots):
  - OUT after a word: first point where energy stays below QUIET_DB, + TAIL_OUT, never past
    the next kept word. If it never goes quiet (a voiced hesitation is glued on), cut at the
    deepest energy dip right at the word's own edge. IN mirrors this.
"""

import json
from pathlib import Path

import numpy as np

E = Path(__file__).parent
SRC = "halusinasi"
SRC_PATH = str((E / "source_1080_dc.mov").resolve())  # 720p60 clean CapCut export, upscaled to 1080x1920@30;
# audio declipped (ffmpeg adeclip: the export had ~4% of samples at full scale) -3.5 dB, PCM

QUIET_DB, QUIET_RUN = -40.0, 3
TAIL_OUT, LEAD_IN = 0.05, 0.04
MAX_SNAP_OUT = 0.12    # a word followed by 'eee'/a drawn vowel never goes quiet: don't keep its tail
MAX_SNAP_IN = 0.15
GAP_CUT = 0.20          # '*' slots at least this long are cut (user: aggressive TikTok pace)
TIGHT = 0.16            # neighbouring words closer than this run together
MIN_SAVE = 0.15         # ...unless the cut would save less than this
ZOOMS = [1.0, 1.06, 1.02, 1.07]
PUNCH_MIN = 0.8         # ranges shorter than this keep the previous zoom (no flicker)
TAIL_HOLD = 1.0
FACE = [0.51, 0.45]     # zoom focus (face centre, fraction of frame)

# user-approved filler words: (text, approximate start in source seconds)
DROP = [
    ("okay", 22.4),          # "Jom kita bincangkan. Okay, definisi"
    ("sebenarnya", 39.2),    # "yang tak wujud pun sebenarnya"
    ("sebenarnya", 40.3),    # "Sebenarnya, halusinasi ini bukannya ..."
    ("sebenarnya", 50.3),    # "sesiapa saja sebenarnya termasuklah"
    ("macam", 64.4),         # "Pernah tak rasa macam ada sesuatu"
    ("sebenarnya", 68.4),    # "tak ada apa-apa pun sebenarnya"
    ("itu", 81.4),           # "akibat seorang itu kurang tidur"
    ("sebenarnya", 92.6),    # "bunyi yang sebenarnya tak wujud pun"
    ("jadi", 94.0),          # "Jadi halusinasi ini boleh disebabkan"
    ("itu", 113.4),          # "paranoid, itu mungkin menjadi petanda"
    ("jadi", 120.3),         # "Jadi kesimpulannya"
]
# hand-checked out-points (word, approx start) -> cut time: where the aligner's boundary is wrong
OUT_AT = {
    ("paranoid", 112.7): 113.34,   # energy ends 113.29; CTC ran "paranoid" into the onset of the dropped "itu"
    ("seorang", 81.2): 81.49,      # "seorang|itu" run together; the dip cut kept ~20ms of "itu" (large-v3 heard "yang")
}
# kept on purpose (meaning): "Itu adalah halusinasi" (15.6), "Itu normal dan ..." (68.7);
# "without any external stimulation" kept (user).


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

    drop = set()
    for text, t in DROP:
        k = min((w for w in W if w["text"] == text), key=lambda w: abs(w["start"] - t))
        assert abs(k["start"] - t) < 0.6, (text, t, k)
        drop.add(k["i"])
    keep = [w["i"] for w in W if w["i"] not in drop]

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

    ranges, cur = [], snap_in(W[keep[0]]["start"], 0.0)
    for a, b in zip(keep, keep[1:]):
        wa, wb = W[a], W[b]
        dropped = b != a + 1
        gap = star_after.get(a)
        if dropped or (gap and gap["end"] - gap["start"] >= GAP_CUT):
            # never run into the next spoken word (the dropped one, or the next kept one)
            nb = W[a + 1]                       # the word right after wa in the source
            if nb["start"] - wa["end"] < TIGHT:  # words run together: cut at the dip between them
                out = emin(wa["end"] - 0.02, nb["start"] + 0.02)
            else:
                out = snap_out(wa["end"], nb["start"] - 0.02)
            for (txt, t0), t_out in OUT_AT.items():
                if wa["text"] == txt and abs(wa["start"] - t0) < 0.5:
                    out = t_out
            pb = W[b - 1]                       # the word right before wb in the source
            if dropped and wb["start"] - pb["end"] < TIGHT:
                nxt = max(out + 0.01, emin(pb["end"] - 0.02, wb["start"] + 0.02))
            else:
                nxt = snap_in(wb["start"], max(out, pb["end"]) + 0.01)
            why = ("drop " + " ".join(W[k]["text"] for k in range(a + 1, b))) if dropped else \
                  f"gap {gap['end'] - gap['start']:.2f}s"
            ranges.append({"source": SRC, "start": round(cur, 3), "end": round(out, 3), "reason": why})
            cur = nxt
    ranges.append({"source": SRC, "start": round(cur, 3), "end": round(min(dur, W[keep[-1]]["end"] + 0.25), 3),
                   "reason": "end"})

    # a gap cut that saves < MIN_SAVE is only a visible jump: undo it (filler-word cuts always stay)
    merged = [ranges[0]]
    for r in ranges[1:]:
        p = merged[-1]
        if r["start"] - p["end"] < MIN_SAVE and not p["reason"].startswith("drop"):
            p["end"], p["reason"] = r["end"], r["reason"]
        else:
            merged.append(r)
    ranges = merged

    # a range too short to read (< 0.3s) is merged into its shorter neighbouring gap
    i = 0
    while i < len(ranges):
        r = ranges[i]
        if r["end"] - r["start"] < 0.3 and len(ranges) > 1:
            j = i - 1 if i == len(ranges) - 1 or (i > 0 and r["start"] - ranges[i - 1]["end"]
                                                   <= ranges[i + 1]["start"] - r["end"]) else i + 1
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


if __name__ == "__main__":
    main()
