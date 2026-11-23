"""Build edl.json for 'Self Diagnose' from forced-aligned words.

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
# source_cfr.mov = constant-30fps copy of raw/Self Diagnose.mp4 (ffmpeg -vf fps=30 -crf 12, PCM audio).
# The phone file is VFR and cuts made straight from it drifted up to 134ms.
SRC = "selfdx"
SRC_PATH = str((E / "source_cfr.mov").resolve())

QUIET_DB = -40.0     # below this for QUIET_RUN frames = the word has really ended/not begun
QUIET_RUN = 3        # 30ms
TAIL_OUT, LEAD_IN = 0.06, 0.04   # extra air kept after offset / before onset
MAX_SNAP = 0.35      # never move more than this from the aligned word edge
TIGHT = 0.16
MAX_PAUSE = 0.45     # gaps between kept words longer than this get shrunk
ZOOMS = [1.0, 1.06, 1.02, 1.07, 1.035]  # punch-in levels cycled across jump cuts (varied, not ping-pong;
                                        # max 1.07 keeps the hair clear of the caption line)
PUNCH_MIN = 0.8      # ranges shorter than this keep the previous zoom (no flicker)
MICRO = 0.7          # a pause-shrink cut that leaves a range shorter than this is undone (no stutter)
TAIL_HOLD = 1.2      # freeze the last frame so the end card / CTA can land
FACE = [0.50, 0.45]  # zoom focus: face centre as a fraction of the frame

# (island_a, word_a, island_b, word_b, beat, note[, {"start"/"end": override s, "gain_db": dB}])
SEGMENTS = [
    ("I11", 11, "I11", 24, "HOOK", "Dia rasa macam jantung dia nak meletup, dan dia yakin yang dia akan mati. — cold open moved from 1:17"),
    ("I00", 4, "I00", 8, "STORY", "Ketika saya bertugas sebagai doktor — 'Teringat satu hari tu' and 'di atas panggilan, doktor' cut"),
    ("I00", 13, "I00", 30, "STORY", "on-call, ada seorang remaja umur 17 tahun yang dibawa oleh kedua ibu bapanya ke Jabatan Kecemasan."),
    ("I01", 0, "I01", 6, "STORY", "Dia kelihatan sangat pucat, menggigil tangan dia,"),
    ("I02", 0, "I02", 4, "STORY", "mengadu sesak nafas, sakit dada. — 'dan nampak dia macam crying non-stop' cut for length"),
    ("I03", 0, "I03", 5, "STORY", "Mak ayah dia pun nampak cemas. — their quote ('nak mati sangat-sangat') cut: it repeats the hook"),
    ("I06", 0, "I06", 22, "TWIST", "Remaja tersebut ada beritahu ... gejala yang dialami. — 'setelah ditenangkan, saya mulakan sesi soal jawab' cut"),
    ("I07", 0, "I07", 17, "TWIST", "Remaja itu yakin yang dia alami BPD, MDD dan ADHD."),
    ("I08", 0, "I08", 10, "TWIST", "Tapi dia tak pernah jumpa doktor pun untuk dapatkan rawatan profesional. — 'Sebaliknya' cut"),
    ("I09", 0, "I09", 3, "CONSEQUENCE", "Dia self-diagnose sendiri"),
    ("I09", 4, "I09", 14, "CONSEQUENCE", "dan cari solution sendiri, termasuklah dia tak keluar rumah langsung. — 'mengelakkan diri daripada... socialise' (hesitation) cut"),
    ("I10", 0, "I10", 14, "CONSEQUENCE", "Dia juga ada try untuk ambil supplement yang ada jual dekat media sosial"),
    ("I10", 15, "I10", 24, "CONSEQUENCE", "tapi tak ada perubahan yang positif pun yang berlaku."),
    ("I11", 0, "I11", 10, "CONSEQUENCE", "Jadi malam itu serangan yang dia alami itu semakin teruk. — hook line not repeated; 'itulah sebab ... hospital' cut"),
    ("I12", 2, "I12", 5, "REVEAL", "Selepas saya buat assessment, — 9.4s dead air and 'Jadi' cut"),
    ("I13", 0, "I13", 10, "REVEAL", "kita dapati yang remaja tersebut mengalami anxiety disorder yang sangat serius. — 'lah' cut"),
    ("I14", 9, "I14", 25, "REVEAL", "Tindakan dia yang mengasingkan diri atau bergantung kepada maklumat yang tak sahih itu burukkan lagi keadaan. — 'tapi dia tak pernah dapat bantuan' (said earlier) cut"),
    ("I15", 11, "I15", 17, "POINT", "Self-diagnose sangat bahaya untuk kita. — false start + 'Okay, point dia kat sini adalah' cut"),
    ("I16", 0, "I16", 10, "POINT", "Sebab baca symptom dekat internet ini tak sama dengan penilaian profesional. — failed take 'dan dia boleh menyebabkan kita salah faham lah dan dapat...' cut"),
    ("I17", 0, "I17", 13, "POINT", "Dia boleh menyebabkan salah faham dan rawatan yang salah dekat diri kita. — clean retake",
     {"start": 144.90}),  # "Dia" is drawn out from 144.94 (envelope + unprompted Whisper); the aligner put it at 145.56
    ("I18", 1, "I18", 5, "TAKEAWAY", "Rawatan yang awal itu penting."),
    ("I18", 6, "I18", 19, "TAKEAWAY", "Kalau remaja tersebut dapat rawatan awal, dia boleh mengelakkan serangan panik yang lebih teruk."),
    ("I20", 0, "I20", 6, "TAKEAWAY", "Keluarga memainkan peranan yang besar. — false start at 2:44 and 'tersebut dia' cut"),
    # second "sokongan" starts at 173.60 (envelope + unprompted Whisper), not the aligner's 173.81
    ("I20", 10, "I20", 25, "TAKEAWAY", "Sokongan ibu bapa bawa dia datang hospital adalah langkah penting dalam proses pemulihan dia.", {"start": 173.57}),
    # 'kesihatan mental adalah isu yang penting ... bantuan profesional boleh buat perubahan' cut for length (the close says it)
    ("I22", 0, "I22", 16, "CLOSE", "Jika anda atau orang terdekat mengalami gejala-gejala seperti ini, jangan takut untuk dapatkan bantuan yang sepatutnya."),
    ("I22", 17, "I22", 26, "CLOSE", "Apa-apa soalan, boleh tanya di ruangan komen. Take care."),
]

# filler words / hesitation sounds dropped from inside kept segments
DROP = {
    ("I09", 5), ("I10", 9), ("I11", 3), ("I17", 7), ("I20", 13),   # '*' hesitation sounds
    ("I10", 16), ("I14", 22), ("I15", 13),                        # "sebenarnya"
    ("I20", 1), ("I20", 2),                                       # "keluarga [tersebut dia] memainkan"
    ("I20", 7), ("I20", 8), ("I20", 9),                           # "sebenarnya adalah sokongan" (repeated)
    ("I20", 21),                                                  # "langkah penting [sebenarnya] dalam"
}
# voiced hesitations ("mmm", drawn-out vowels) filling short gaps: always cut, whatever the gap length.
# Given as the word BEFORE the gap.
HESITATE = set()


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
