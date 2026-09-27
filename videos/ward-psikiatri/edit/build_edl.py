"""Build edl.json for 'Keadaan Dalam Wad Psikiatri' from forced-aligned words.

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
SRC = "ward"
SRC_PATH = str((E.parent / "raw" / "ward.mp4").resolve())

QUIET_DB = -40.0     # below this for QUIET_RUN frames = the word has really ended/not begun
QUIET_RUN = 3        # 30ms
TAIL_OUT, LEAD_IN = 0.06, 0.04   # extra air kept after offset / before onset
MAX_SNAP = 0.35      # never move more than this from the aligned word edge
TIGHT = 0.16
MAX_PAUSE = 0.45     # gaps between kept words longer than this get shrunk
PUNCH = 1.08         # alternate 1.0 / PUNCH zoom at jump cuts (disguises them)
PUNCH_MIN = 0.8      # ranges shorter than this keep the previous zoom (no flicker)
FACE = [0.54, 0.60]  # zoom focus: face centre as a fraction of the frame

# (island_a, word_a, island_b, word_b, beat, note[, start_override])
SEGMENTS = [
    ("I00", 1, "I00", 4, "HOOK", "Saya pernah ada pesakit, — 'aa' cut"),
    ("I01", 1, "I01", 3, "HOOK", "tanya dekat saya, — false start 'Doktor, macam mana saya, masa' cut"),
    ("I02", 0, "I02", 11, "HOOK", "Doktor, macam mana keadaan dalam wad psikiatri, ya? Saya takutlah, saya tengok — 'aa' cut"),
    ("I02", 13, "I02", 21, "HOOK", "macam dalam filem-filem barat tu, nampak seram sangat. — first 'Okay, sebenarnya, tidak' take dropped"),
    ("I04", 1, "I04", 2, "ANSWER", "Sebenarnya, tidak."),
    ("I04", 3, "I04", 12, "ANSWER", "Wad psikiatri Malaysia jauh berbeza dengan apa yang anda bayangkan. — clinic plug moved to end"),
    ("I08", 5, "I09", 14, "MYTH", "Ramai orang bayangkan ... Tapi tidak sebenarnya. — 'Okey balik kepada topik tadi' dropped"),
    ("I13", 1, "I14", 2, "TEAM", "Di Malaysia wad psikiatri ... ahli psikologi, kaunselor — take 2 (take 1 at 57.3s dropped)"),
    ("I14", 4, "I18", 1, "ROUTINE", "terapi jurupulih kerja ... keselamatan akan dipantau. — hesitation sound at 88.3s cut", 89.08),
    ("I19", 0, "I21", 13, "ROUTINE", "Aktiviti terapi ... Bukan untuk menghukum pesakit."),
    ("I22", 0, "I22", 10, "Q2", "Datang pula soalan kedua. Adakah semua pesakit dalam wad ni agresif? — false-start 'Adakah,' cut"),
    ("I24", 0, "I24", 6, "Q2", "Jawapannya tidak. Pesakit dalam wad psikiatri ini,"),
    ("I24", 9, "I27", 6, "Q2", "mereka mungkin mengalami ... penyakit mereka. — repeated 'mereka mengalami' cut"),
    ("I31", 1, "I31", 98, "Q3", "Ada juga yang tanya saya ... gila ke apa. — false start 'Lepas itu ada juga lagi soalan' dropped"),
    ("I33", 0, "I33", 31, "RECOVERY", "Tidak. Ramai pesakit ... bukan tempat hukum ke apa."),
    ("I34", 0, "I35", 14, "RECOVERY", "Ia adalah tempat yang selamat ... kesihatan mental, — repeated 'Ia adalah tempat' cut"),
    ("I36", 0, "I36", 4, "CTA", "Jangan takut untuk mendapatkan bantuan. — cleaner second take"),
    ("I05", 0, "I05", 9, "CTA", "Boleh datang buat saringan konsultasi kesihatan mental di klinik saya. — moved from 0:31"),
    ("I07", 0, "I07", 9, "CTA", "Kita bincang dahulu pilihan rawatan yang paling sesuai untuk anda. — clean retake (first take's 'aa' runs into 'diagnosis')"),
    ("I36", 5, "I36", 11, "CTA", "Apa-apa soalan, minta anda komen. Take care."),
]


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
    for ia, wa, ib, wb, beat, note, *override in SEGMENTS:
        ka, kb = pos[(ia, wa)], pos[(ib, wb)]
        start, end = (override[0] if override else cut_in(ka)), cut_out(kb)
        cur = start
        for k in range(ka, kb):  # shrink long gaps between consecutive kept words (breaths, hesitations)
            a, b = flat[k], flat[k + 1]
            if b["start"] - a["end"] > MAX_PAUSE:
                ranges.append({"source": SRC, "start": round(cur, 3), "end": round(cut_out(k), 3), "beat": beat})
                cur = cut_in(k + 1)
        ranges.append({"source": SRC, "start": round(cur, 3), "end": round(end, 3), "beat": beat, "reason": note})

    z = 1.0
    for i, r in enumerate(ranges):
        assert r["end"] - r["start"] > 0.15, r
        if i and r["end"] - r["start"] >= PUNCH_MIN:
            z = PUNCH if z == 1.0 else 1.0
        r["zoom"] = z
    total = sum(r["end"] - r["start"] for r in ranges)
    edl = {"version": 1, "sources": {SRC: SRC_PATH}, "ranges": ranges, "grade": "subtle",
           "zoom_focus": FACE, "overlays": [], "total_duration_s": round(total, 2)}
    (E / "edl.json").write_text(json.dumps(edl, indent=2, ensure_ascii=False))
    print(f"{len(SEGMENTS)} segments -> {len(ranges)} ranges, total {total:.1f}s ({int(total // 60)}:{total % 60:04.1f})")


if __name__ == "__main__":
    main()
