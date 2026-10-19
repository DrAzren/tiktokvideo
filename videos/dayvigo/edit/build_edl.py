"""Build edl.json for 'Ubat Psikiatri Dayvigo' from forced-aligned words.

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
SRC = "dayvigo"
SRC_PATH = str((E / "source_enh.mov").resolve())   # original picture + enhance_voice.sh audio

QUIET_DB = -40.0     # below this for QUIET_RUN frames = the word has really ended/not begun
QUIET_RUN = 3        # 30ms
TAIL_OUT, LEAD_IN = 0.06, 0.04   # extra air kept after offset / before onset
MAX_SNAP = 0.35      # never move more than this from the aligned word edge
TIGHT = 0.16
MAX_PAUSE = 0.35     # gaps between kept words longer than this get shrunk (TikTok pace)
ZOOMS = [1.0, 1.08, 1.03, 1.1, 1.05]  # punch-in levels cycled across jump cuts (varied, not ping-pong)
PUNCH_MIN = 0.8      # ranges shorter than this keep the previous zoom (no flicker)
MICRO = 0.7          # a pause-shrink cut that leaves a range shorter than this is undone (no stutter)
TAIL_HOLD = 0.6      # no end card (educational only): a short hold so "take care" isn't clipped
FACE = [0.5, 0.45]   # zoom focus: face centre as a fraction of the frame
HFLIP = True         # the phone recorded in selfie-mirror mode: "DR AZREN" and the box text read backwards

# (island_a, word_a, island_b, word_b, beat, note[, {"start"/"end": override s, "gain_db": dB}])
SEGMENTS = [
    ("I00", 0, "I00", 18, "HOOK", "Badan penat ... Pernah tak? — 4s of breath/box handling after it cut"),
    ("I04", 0, "I04", 43, "WHAT", "Pernah tak dengar ubat nama dia Dayvigo? ... orexin reseptor antagonis. — first 'bahasa senang dia' take dropped"),
    # "dalam|bahasa" touch: start in the b-closure, 30ms before the burst at 35.01 (spectrogram)
    ("I05", 2, "I05", 22, "HOW", "Bahasa senang dia ... switch off butang jaga ... Dia tak paksa tidur pun. — 2nd take, 'dalam' and 'sebenarnya' cut", {"start": 34.98}),
    ("I07", 1, "I07", 73, "USES", "Antara fungsi utama ... kesan sampingan. Contohnya, — abandoned 'ubat ni dia boleh mengantuk pada' dropped"),
    ("I08", 1, "I08", 72, "SIDE", "ubat ni boleh menyebabkan mengantuk ... elakkan alkohol kalau ambil ubat ni. — restart take, 'macam dia' cut"),
    ("I10", 0, "I10", 31, "HELP", "Kalau insomnia dah lama sangat ... untuk cari punca sebenar. — kept 'otak jadi rosak' (user call)"),
    ("I12", 0, "I12", 24, "CLOSE", "Ataupun boleh buat saringan ... Take care. — superseded 'Ataupun boleh datang di klinik saya' dropped"),
]

# filler words dropped from inside kept segments (user-approved list, 2026-10-19)
DROP = {
    ("I00", 6),                                   # "terpejam-pejam dah"
    ("I04", 26), ("I04", 34), ("I04", 35),        # "klonazepam tu", "pengsan ke apa"
    ("I05", 17),                                  # "otak kita tu"
    ("I07", 11),                                  # "insomnia (eh) dia (eee) untuk kes"
    ("I07", 38),                                  # "tidur tu rasa"
    ("I07", 64), ("I07", 65),                     # "tapi of course setiap"
    ("I07", 72),                                  # "kesan sampingan dia"
    ("I08", 3),                                   # "ubat ni dia boleh"
    ("I08", 26),                                  # "ni sebenarnya ringan"
    ("I08", 35),                                  # "sesuai lah"
    ("I08", 38),                                  # "Dayvigo ni dia bukan"
    ("I08", 51), ("I08", 52),                     # "contohnya macam kerja, kena kerja"
    ("I08", 57),                                  # "shift malam ke tak sesuai"
    ("I08", 60),                                  # "dia perlu ambil"
}
# voiced hesitations (pitch-detected "eee/mmm") filling short gaps: always cut, whatever the gap length.
# Given as the word BEFORE the gap.
HESITATE = {("I05", 12), ("I08", 12), ("I10", 7), ("I10", 9), ("I10", 12)}


def env2ms() -> np.ndarray:
    """2 ms RMS envelope (dB) of audio.wav, for locating cut dips precisely."""
    import soundfile as sf
    a, sr = sf.read(E / "audio.wav", dtype="float32")
    hop = sr // 500
    n = len(a) // hop
    return 20 * np.log10(np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)


def main() -> None:
    db = np.load(E / "env_db.npy")
    db2 = env2ms()
    dur = len(db) / 100
    al = json.loads((E / "aligned.json").read_text())
    flat = sorted(
        ({"iid": iid, "i": i, **w} for iid, v in al.items() for i, w in enumerate(v["words"])),
        key=lambda w: w["start"],
    )
    pos = {(w["iid"], w["i"]): k for k, w in enumerate(flat)}

    def emin(lo: float, hi: float) -> float:
        """Time of the deepest energy dip in [lo, hi), on the 2 ms envelope."""
        i0, i1 = int(round(lo * 500)), max(int(round(lo * 500)) + 1, int(round(hi * 500)))
        return (i0 + int(np.argmin(db2[i0:i1]))) / 500 + 0.001

    def emin10(lo: float, hi: float) -> float:
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
                # deepest dip at each word's own edge. Next to a DROPPED word the window reaches toward
                # it (up to 0.15s) so a stop closure just past the aligned edge ("malam|ke") is found;
                # next to a hesitation it stays tight so no "eee" onset is kept.
                reach_o = min(a["end"] + 0.15, flat[k + 1]["start"] + 0.02) if dropped else 0.0
                reach_i = max(b["start"] - 0.15, flat[k2 - 1]["end"] - 0.02) if dropped else b["start"]
                seg.append([cur, emin(a["end"] - 0.02, max(a["end"] + 0.07, reach_o))])
                cur = emin(min(b["start"] - 0.07, reach_i), b["start"] + 0.02)
                forced.append(True)
            elif b["start"] - a["end"] > MAX_PAUSE:
                o, i = cut_out(k), cut_in(k2)
                if i < o + 0.03:  # both edges fell back to a dip in overlapping windows (fricative tail
                    i = snap_in(b["start"], o + 0.03)  # + breath): never start before the out point
                seg.append([cur, o])
                cur = i
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
        assert i == 0 or r["start"] >= ranges[i - 1]["end"] or r["start"] < ranges[i - 1]["start"], (ranges[i - 1], r)
        if i and r["end"] - r["start"] >= PUNCH_MIN:
            zi = (zi + 1) % len(ZOOMS)
            z = ZOOMS[zi]
        r["zoom"] = z
    total = sum(r["end"] - r["start"] for r in ranges)
    edl = {"version": 1, "sources": {SRC: SRC_PATH}, "ranges": ranges, "grade": "subtle",
           "zoom_focus": FACE, "hflip": HFLIP, "tail_hold": TAIL_HOLD, "overlays": [],
           "total_duration_s": round(total + TAIL_HOLD, 2)}
    (E / "edl.json").write_text(json.dumps(edl, indent=2, ensure_ascii=False))
    print(f"{len(SEGMENTS)} segments -> {len(ranges)} ranges, total {total:.1f}s ({int(total // 60)}:{total % 60:04.1f})")


if __name__ == "__main__":
    main()
