"""Build edl.json for '3 Ubat Psikiatri Kuruskan Badan' from forced-aligned words.

Segments reference aligned.json words as (island, first_word, island, last_word).
Edge rules (CTC word ends run ~0.1s early, so edges snap to real audio energy):
  - OUT: first point after the word where energy stays below QUIET_DB, plus a
         short tail; never past the next word. IN mirrors this.
  - If the neighbouring (dropped) word is within TIGHT s, cut at the energy
    minimum between the two words instead.
  - Gaps longer than MAX_PAUSE between kept words are shrunk the same way.
Same engine as videos/ward-psikiatri/edit/build_edl.py.
"""

import json
from pathlib import Path

import numpy as np

E = Path(__file__).parent
SRC = "ubat"
SRC_PATH = str((E.parent / "raw" / "ubat.mp4").resolve())

QUIET_DB = -40.0     # below this for QUIET_RUN frames = the word has really ended/not begun
QUIET_RUN = 3        # 30ms
TAIL_OUT, LEAD_IN = 0.06, 0.04   # extra air kept after offset / before onset
MAX_SNAP = 0.35      # never move more than this from the aligned word edge
TIGHT = 0.16
MAX_PAUSE = 0.40     # gaps between kept words longer than this get shrunk
ZOOMS = [1.0, 1.06, 1.02, 1.07, 1.035]  # punch-in levels cycled across jump cuts (varied, not ping-pong)
PUNCH_MIN = 0.8      # ranges shorter than this keep the previous zoom (no flicker)
MICRO = 0.7          # a pause-shrink cut that leaves a range shorter than this is undone (no stutter)
TAIL_HOLD = 1.2      # freeze the last frame so the end card / CTA can land
FACE = [0.57, 0.47]  # zoom focus: face centre as a fraction of the frame (measured at 5s/70s)
OUTPUT_SIZE = [1080, 1920]   # source is 720x1280: upscale once here (lanczos)

# (island_a, word_a, island_b, word_b, beat, note[, {"start"/"end": override s, "gain_db": dB}])
SEGMENTS = [
    ("I00", 0, "I00", 9, "INTRO", "Assalamualaikum, saya Dr Azren. Saya merupakan doktor di Jabatan Psikiatri."),
    ("I02", 1, "I02", 14, "HOOK", "Kali ni saya nak cerita ubat-ubat ... penurunan berat badan. — 'Sebelum ni ... kenaikan berat badan' (I01), 'Tapi' and 'pula' cut"),
    ("I03", 1, "I03", 15, "BUPROPION", "Ubat yang pertama adalah bupropion ... kurangkan selera makan. — 'Ok' and 'sebenarnya' cut"),
    ("I04", 0, "I04", 11, "BUPROPION", "Biasanya digunakan untuk merawat kemurungan dan juga bantu orang untuk berhenti merokok. — trailing 'juga' cut"),
    ("I05", 0, "I05", 12, "BUPROPION", "Tapi ingat, bukan semua orang akan turun berat, bergantung pada badan masing-masing."),
    ("I06", 0, "I06", 18, "TOPIRAMATE", "Yang kedua adalah topiramate. Ini asalnya adalah ubat sawan, tapi doktor ... mood juga. — 'sebenarnya' cut"),
    ("I07", 2, "I07", 15, "TOPIRAMATE", "Dia boleh turunkan berat badan ... kurang craving. — false start '* dia ada' (45.3-46.6) cut"),
    ("I08", 0, "I08", 19, "TOPIRAMATE", "Tapi kesan sampingan dia ada banyak sikit. Ada orang yang senang rasa semput ... dos yang tinggi."),
    ("I09", 0, "I09", 3, "FLUOXETINE", "Yang ketiga adalah fluoxetine. — take 1; retakes 64.0-88.3 ('SSRI ni', 'yang ketiga adalah fluoxetine, ini adalah SSRI yang popular, yang commonly used for', 'Ehm', 'Ni adalah SSRI yang commonly used for', 'Ehm') dropped"),
    ("I14", 0, "I14", 16, "FLUOXETINE", "Fluoxetine ni adalah SSRI yang commonly and widely used for antidepressant and also untuk masalah anxiety. — clean take"),
    ("I16", 0, "I16", 37, "FLUOXETINE", "Kadang-kadang boleh buat orang turun berat badan ... kena monitor. — 'dia', 'sebenarnya' cut"),
    ("I17", 0, "I17", 31, "TAKEAWAY", "Yang penting kita kena faham ... kenaikan berat badan pada setengah orang. — 'dia' cut; 'kenaikan' is as said (both Whisper models) and reads as intended"),
    ("I18", 0, "I18", 29, "CTA", "Jangan pilih ubat sebab nak kurus semata-mata ... Take care."),
]

# padding words dropped from inside kept segments (user-approved list)
DROP = {
    ("I06", 9),                      # "ubat sawan sebenarnya"
    # ("I08", 3) "kesan sampingan dia ada": tried, restored. The join "sampingan|ada" is inside tight
    # connected speech and large-v3 heard the cut as "kesan-kesan pingat dia".
    ("I14", 13),                     # '*' pause/sound between "also" and "untuk"
    ("I16", 16), ("I16", 24),        # "ada orang dia hilang", "jangka panjang sebenarnya"
    ("I17", 7),                      # "setiap ubat dia ada"
}
# voiced hesitations filling short gaps (word BEFORE the gap). None found: no gap > 0.3s carries voice.
HESITATE: set = set()


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
           "zoom_focus": FACE, "tail_hold": TAIL_HOLD, "output_size": OUTPUT_SIZE, "overlays": [],
           "total_duration_s": round(total + TAIL_HOLD, 2)}
    (E / "edl.json").write_text(json.dumps(edl, indent=2, ensure_ascii=False))
    print(f"{len(SEGMENTS)} segments -> {len(ranges)} ranges, total {total:.1f}s ({int(total // 60)}:{total % 60:04.1f})")


if __name__ == "__main__":
    main()
