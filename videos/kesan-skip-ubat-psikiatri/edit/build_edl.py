"""Build edl.json for 'Kesan Skip Ubat Psikiatri' from forced-aligned words.

Template: videos/ubat-psikiatri-olanzapine/edit/build_edl.py. Segments reference aligned.json words as
(island, first_word, island, last_word).
Edge rules (CTC word ends run ~0.1s early, so edges snap to real audio energy):
  - OUT: first point after the word where energy stays below QUIET_DB, plus a
         short tail; never past the next word. IN mirrors this.
  - If the neighbouring (dropped) word is within TIGHT s, cut at the energy
    minimum between the two words instead.
  - Gaps longer than MAX_PAUSE between kept words are shrunk the same way.
Recorded in a car, CapCut export with the voice boosted (-6 LUFS): pause floor -30..-36 dB, QUIET_DB -26.
The source is mirrored (front camera: 'DR AZREN' on the scrubs reads backwards) -> hflip.
The source is 720x1280; out_size upscales to 1080x1920 in the punch-in pass (tools/render_edl.py).

Order (user-approved): the patient's question is the hook, then the greeting, the topic question, the
three risks, the clinic plug (moved from 0:23) and the CTA. The CTA's own "atau boleh datang klinik saya
di Nilai" is dropped: the plug right before it ends with the same words.
"""

import json
from pathlib import Path

import numpy as np

E = Path(__file__).parent
SRC = "skip"
SRC_PATH = str((E.parent / "raw" / "skip.mp4").resolve())

QUIET_DB = -26.0     # below this for QUIET_RUN frames = the word has really ended/not begun (pause floor ~-30..-36)
QUIET_RUN = 3        # 30ms
TAIL_OUT, LEAD_IN = 0.05, 0.04   # extra air kept after offset / before onset
MAX_SNAP = 0.35      # never move more than this from the aligned word edge
TIGHT = 0.16
MAX_PAUSE = 0.40     # gaps between kept words longer than this get shrunk (TikTok pace)
ZOOMS = [1.0, 1.06, 1.02, 1.07]  # punch-in levels cycled across jump cuts (user: 1.0 / 1.06 / 1.02 / 1.07)
PUNCH_MIN = 0.0      # user: a zoom change on EVERY jump cut, never two neighbouring ranges at one zoom
MICRO = 0.7          # a pause-shrink cut that leaves a range shorter than this is undone (no stutter)
TAIL_HOLD = 2.0      # freeze the last frame so the end card (clinic / bio / DM) has ~3 s to be read
FACE = [0.50, 0.40]  # zoom focus: face centre as a fraction of the frame

# (island_a, word_a, island_b, word_b, beat, note[, {"start"/"end": override s, "gain_db": dB}])
SEGMENTS = [
    ("I01", 0, "I01", 12, "HOOK", "Doktor, saya dah sihat sikit. Saya nak berhenti ubat sendiri. Takpe ke, doktor? — moved ahead of the greeting"),
    ("I00", 0, "I00", 6, "INTRO", "Assalamualaikum, saya Dr Azren, doktor psikiatri. — pre-roll noise + 5.8s silent shot dropped"),
    ("I05", 5, "I05", 19, "TOPIK", "Jom kita sembang sekejap. Apa jadi kalau kita skip ubat psikiatri tanpa bincang dengan doktor? "
                                  "— 'Ok, berbalik kepada topik tadi' dropped (the plug moved to the end)"),
    ("I06", 0, "I06", 31, "KESAN1", "Yang pertama, risiko relapse… otak kita boleh jadi tak stabil semula."),
    ("I07", 0, "I07", 22, "KESAN1", "Contohnya boleh dapat mood swing balik… masuk wad balik."),
    ("I08", 0, "I08", 6, "KESAN2", "Yang kedua, withdrawal symptom, gejala penarikan."),
    ("I09", 1, "I09", 31, "KESAN2", "Bukan semua tapi ada ubat… otak jadi serabut."),
    ("I10", 0, "I10", 26, "KESAN3", "Yang ketiga, boleh merosakkan proses rawatan… macam kita tekan reset button balik."),
    ("I11", 1, "I11", 20, "KESAN3", "Lambat sembuhnya… ubat jadi tak efektif macam dulu lagi."),
    ("I04", 3, "I04", 60, "PLUG", "Saya ada berita baik. Di klinik saya di Nilai… boleh datang klinik saya di Nilai. — moved from 0:23; "
                                  "'Sebelum tu' and abandoned take 1 (0:16.8) dropped"),
    ("I12", 1, "I12", 27, "CTA", "Kalau anda tengah keliru… boleh jumpa dengan profesional kesihatan mental. "
                                 "— 'atau boleh datang klinik saya di Nilai' dropped (the plug just said it)"),
    ("I12", 36, "I12", 37, "CTA", "Take care."),
]

# filler words (and breath/hesitation '*' tokens) dropped from inside kept segments
DROP = {
    ("I00", 4),                                   # "saya Dr Azren, saya doktor psikiatri"
    ("I04", 13),                                  # "kami ada menyediakan"
    ("I04", 31), ("I04", 33),                     # "kemurungan ke, anxiety ke"
    *[("I04", i) for i in range(36, 41)],         # "dan lain-lain lagi lah": "lain-lain|lagi" is one voiced run with no
                                                  # clean edge (a "la-" survived), so the list ends at "masalah tidur"
    ("I06", 2),                                   # "yang pertama adalah"
    ("I06", 10),                                  # breath before "ubat psikiatri ni"
    ("I06", 14),                                  # "ubat psikiatri ni dia macam pelindung"
    ("I06", 19),                                  # "jadi bila kita stop"
    ("I07", 1), ("I07", 7), ("I07", 10),          # "contohnya dia boleh", "dia rasa", "cemas dia semakin"
    ("I07", 14),                                  # [eee] after "menjadi-jadi"
    ("I07", 16),                                  # "atau boleh sampai tahap boleh masuk wad"
    ("I08", 2),                                   # "yang kedua adalah"
    ("I09", 10), ("I09", 11),                     # breath + "dia boleh dapat"
    ("I09", 23),                                  # [eee] after "gangguan tidur"
    ("I09", 25),                                  # "rasa macam emosi"
    *[("I09", i) for i in range(32, 37)],         # "dan lain-lain lagi lah" (same reason: ends at "otak jadi serabut")
    ("I10", 2),                                   # "yang ketiga dia boleh"
    ("I10", 7), ("I10", 8),                       # breath + "bila setiap kali"
    ("I10", 18), ("I10", 19),                     # [eee] + "dia macam kita"
    ("I10", 22),                                  # "kita umpamanya tekan"
    ("I11", 8), ("I11", 9),                       # breath + "dan kadang-kadang"
    ("I11", 13), ("I11", 14),                     # "ubat tu dah jadi"
    ("I12", 3),                                   # "kalau anda sendiri tengah keliru"
    ("I12", 11),                                  # breath after "ataupun tidak"
    ("I12", 14),                                  # "rasa macam nak mulakan"
    ("I12", 21),                                  # [eee] after "tak pasti"
}
# voiced hesitations / held vowels filling short gaps: always cut, whatever the gap length.
# Given as the word BEFORE the gap (found by gap_scan.py, checked on spectrograms: verify/spectro.png).
HESITATE = {("I01", 6), ("I04", 7), ("I06", 7), ("I06", 26), ("I07", 0), ("I07", 8), ("I09", 18), ("I09", 20)}


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

    # segment boundaries that are continuous in the source (snap tails overlap) are not jump cuts: merge
    merged = [ranges[0]]
    for r in ranges[1:]:
        m = merged[-1]
        if r["source"] == m["source"] and -0.05 <= r["start"] - m["end"] < 0.06:
            m["end"] = r["end"]
            m["reason"] = " | ".join(x for x in (m.get("reason"), r.get("reason")) if x)
        else:
            merged.append(r)
    ranges[:] = merged

    z, zi = ZOOMS[0], 0
    for i, r in enumerate(ranges):
        assert r["end"] - r["start"] > 0.15, r
        if i and r["end"] - r["start"] >= PUNCH_MIN:
            zi = (zi + 1) % len(ZOOMS)
            z = ZOOMS[zi]
        r["zoom"] = z
    total = sum(r["end"] - r["start"] for r in ranges)
    edl = {"version": 1, "sources": {SRC: SRC_PATH}, "ranges": ranges, "grade": "subtle", "out_size": [1080, 1920], "hflip": True,
           "zoom_focus": FACE, "tail_hold": TAIL_HOLD, "overlays": [],
           "total_duration_s": round(total + TAIL_HOLD, 2)}
    (E / "edl.json").write_text(json.dumps(edl, indent=2, ensure_ascii=False))
    print(f"{len(SEGMENTS)} segments -> {len(ranges)} ranges, total {total:.1f}s ({int(total // 60)}:{total % 60:04.1f})")


if __name__ == "__main__":
    main()
