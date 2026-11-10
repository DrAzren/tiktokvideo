"""Build edl.json for '10 Ubat Psikiatri Dilarang Untuk Mengandung' from forced-aligned words.

Same edge engine as videos/ward-psikiatri/edit/build_edl.py, but the cut is written as markup
over each aligned passage, so the approved filler list reads directly:
    [word word]  dropped (filler word, false start, retake) -> forced cut at the energy dip
    word|        voiced hesitation follows this word -> forced cut even if the gap is short
Passages not listed in KEEP (take-1 hook, take-1 intro, "kalau anda" false start) are dropped whole.
Every markup line must reproduce aligned.json's hypothesis (or its start, for a passage split
across beats) once brackets/pipes are removed.

Edge rules (CTC word ends run ~0.1s early, so edges snap to real audio energy):
  - OUT: first point after the word where energy stays below QUIET_DB, plus a short tail;
         never past the next word. IN mirrors this.
  - If the neighbouring (dropped) word is within TIGHT s, cut at the energy minimum between them.
  - Gaps longer than MAX_PAUSE between kept words are shrunk the same way.
"""

import json
import re
from pathlib import Path

import numpy as np

E = Path(__file__).parent
SRC = "ubat"
SRC_PATH = str((E.parent / "raw" / "10 Ubat Psikiatri Dilarang Untuk Mengandung.mp4").resolve())

QUIET_DB = -40.0     # below this for QUIET_RUN frames = the word has really ended/not begun
QUIET_RUN = 3        # 30ms
TAIL_OUT, LEAD_IN = 0.05, 0.03   # extra air kept after offset / before onset (TikTok pace)
MAX_SNAP = 0.35      # never move more than this from the aligned word edge
TIGHT = 0.16
MAX_PAUSE = 0.40     # gaps between kept words longer than this get shrunk
ZOOMS = [1.0, 1.06, 1.02, 1.07, 1.035]  # punch-in levels cycled across jump cuts
PUNCH_MIN = 0.8      # ranges shorter than this keep the previous zoom (no flicker)
MICRO = 0.6          # a pause-shrink cut that leaves a range shorter than this is undone (no stutter)
TAIL_HOLD = 1.5      # freeze the last frame so the "Tanya di komen" end card can land
LOUD_DB = -25.0      # a cut point louder than this is inside voiced speech
FACE = [0.50, 0.46]  # zoom focus: face centre as a fraction of the frame

# (passage, beat, markup[, {"start"/"end": override s, "gain_db": dB}])
KEEP = [
    ("P01", "HOOK", "sepuluh ubat psikiatri yang perlu berhati hati atau kalau boleh elakkanlah ketika anda pregnant ataupun ada plan nak pregnant"),
    ("P03", "INTRO", "[*] assalamualaikum saya doktor azren saya doktor psikiatri"),
    ("P05", "WHY", "kalau anda tengah pregnant ataupun plan nak mengandung [sebenarnya] ada beberapa ubat psikiatri yang doktor akan sangat berhati hati kalau nak bagi sebab [dia] boleh bagi kesan dekat baby"),
    ("P05", "D1", "[kalau anda tengah pregnant ataupun plan nak mengandung sebenarnya ada beberapa ubat psikiatri yang doktor akan sangat berhati hati kalau nak bagi sebab dia boleh bagi kesan dekat baby] ubat yang pertama adalah sodium valproate ataupun epilim selalunya digunakan dalam kes sawan ataupun bipolar * lah"),  # 'lah' is fused into 'bipolarlah' (no gap): cutting clips the word
    ("P06", "D1", "[ha] ubat ni [dia] ada risiko tinggi boleh menyebabkan kecacatan otak dan juga sistem saraf bayi"),
    ("P06", "D2", "[ha ubat ni dia ada risiko tinggi boleh menyebabkan kecacatan otak dan juga sistem saraf bayi] yang kedua adalah litium [ha] ni pun ubat untuk bipolar juga [selalunya ubat ni risiko dia tinggi kalau ubat]"),
    ("P07", "D2", "ubat ni [dia] ada risiko untuk masalah jantung bayi [dia] boleh guna tapi [dia kena monitor dengan * tapi]"),
    ("P08", "D2", "kena monitor betul betul kena ada * pemantauan yang rapi oleh doktor lah [ha yang ketiga adalah carbamazepine]"),  # fused 'doktorlah', kept
    ("P09", "D3", "yang ketiga adalah carbamazepine [ha] ini pun ubat untuk bipolar dan kadang kadang digunakan untuk sawan juga [ha ni ubat ada risiko]"),
    ("P10", "D3", "ubat ni [dia] ada risiko neural tube defect"),
    ("P10", "D4", "[ubat ni dia ada risiko neural tube defect ha] yang keempat adalah paroxetine [ha] paroxetine ni adalah antidepressant yang digunakan untuk depression dan juga anxiety [ha dia] dikaitkan dengan risiko kecacatan jantung bayi juga"),
    ("P11", "D5", "yang kelima adalah alprazolam ataupun xanax selalunya digunakan dalam kes anxiety ataupun panic attack ubat ni [dia] ada risiko [*] bayi boleh jadi lemah ataupun ada withdrawal effect selepas melahirkan bayi"),
    ("P11", "D6", "[yang kelima adalah alprazolam ataupun xanax selalunya digunakan dalam kes anxiety ataupun panic attack ubat ni dia ada risiko * bayi boleh jadi lemah ataupun ada withdrawal effect selepas melahirkan bayi] yang keenam adalah diazepam ataupun valium ubat ni [dia *] bantu untuk anxiety [muscle relax]"),
    ("P12", "D6", "[dia] muscle relaxant dan juga sawan ubat ni [dia] ada risiko baby floppy syndrome"),
    ("P12", "D7", "[dia muscle relaxant dan juga sawan ubat ni dia ada risiko baby floppy syndrome] yang ketujuh adalah clonazepam clonazepam ni ubat digunakan untuk anxiety ataupun sawan [dia] ada risiko sedation kepada bayi"),
    ("P13", "D8", "yang kelapan adalah topiramate topiramate ni adalah sejenis mood stabilizer [*] dan kadang kadang digunakan dalam kes migraine juga"),
    ("P14", "D8", "ubat ni [dia] ada risiko cleft lip dan juga cleft palate kepada bayi"),
    ("P14", "D9", "[ubat ni dia ada risiko cleft lip dan juga cleft palate kepada bayi] yang kesembilan adalah risperidone ubat ni digunakan dalam kes seperti skizofrenia bipolar ataupun aggression [dia] ada risiko hormonal dan metabolik effect kepada baby"),
    ("P15", "D9", "[perlu dia] bukan tak boleh bagi boleh tapi [kena monitor betul betul oleh] kena ada pemantauan rapi oleh doktor"),
    ("P15", "D10", "[perlu dia bukan tak boleh bagi boleh tapi kena monitor betul betul oleh kena ada pemantauan rapi oleh doktor] yang kesepuluh adalah olanzapine olanzapine ni ubat untuk skizofrenia dan juga bipolar lah [dia] ada risiko berat bayi jadi besar dan juga masalah metabolik side effect kepada bayi [itu]"),
    ("P16", "CLOSE", "[ha] jadi [ubat yang saya senarai ni bukan tak boleh tapi * ubat yang] ubat yang saya senarai ni bukanlah kata seratus peratus tak boleh [ha] tapi [kena betul betul kena betul betul kena betul betul]"),
    ("P17", "CLOSE", "[kalau anda ada ambik kalau ada anda ada ambik] kalau anda ada ambik sepuluh ubat yang saya sebut tadi [tu] dan anda ada plan nak pregnant ataupun tengah pregnant kena bagitahu [dekat] doktor supaya pemantauan rapi dapat dilakukanlah"),
    ("P17", "CTA", "[kalau anda ada ambik kalau ada anda ada ambik kalau anda ada ambik sepuluh ubat yang saya sebut tadi tu dan anda ada plan nak pregnant ataupun tengah pregnant kena bagitahu dekat doktor supaya pemantauan rapi dapat dilakukanlah] apa apa soalan boleh tanya di ruangan komen"),
]

# exact in-points where the aligner squeezed a filler into a ~50 ms sliver (read off spectrograms,
# verify/spec_ha.png + spec_more.png): (passage, nth occurrence of word) -> source time
CUT_IN = {
    ("P10", "yang", 0): 101.065,      # "ha" (open /a/) runs 100.94-101.06; /j/ of "yang" starts 101.065
    ("P10", "dikaitkan", 0): 107.600,  # "ha" 107.40-107.50, "dia" 107.50-107.60, /d/ of "dikaitkan" 107.60
    ("P13", "dan", 0): 151.775,       # voiced "eee" after "stabilizer" ends ~151.75, "dan" at 151.80
}


def parse(markup: str) -> list[tuple[str, bool, bool]]:
    """-> [(word, kept, hesitate_after)]"""
    out, drop = [], False
    for tok in re.findall(r"\[|\]|[^\s\[\]]+", markup):
        if tok == "[":
            drop = True
        elif tok == "]":
            drop = False
        else:
            hes = tok.endswith("|")
            out.append((tok.rstrip("|"), not drop, hes))
    return out


def main() -> None:
    db = np.load(E / "env_db.npy")
    dur = len(db) / 100
    al = json.loads((E / "aligned.json").read_text())
    flat = sorted(
        ({"iid": iid, "i": i, **w} for iid, v in al.items() for i, w in enumerate(v["words"])),
        key=lambda w: w["start"],
    )
    pos = {(w["iid"], w["i"]): k for k, w in enumerate(flat)}
    fixed_in = {}
    for (iid, word, nth), t in CUT_IN.items():
        idx = [i for i, w in enumerate(al[iid]["words"]) if w["text"] == word][nth]
        fixed_in[pos[(iid, idx)]] = t

    # markup -> SEGMENTS / DROP / HESITATE in the ward-psikiatri form
    segments, drop, hesitate = [], set(), set()
    for iid, beat, markup, *opt in KEEP:
        toks = parse(markup)
        hyp = al[iid]["hyp"].split()
        # a passage split across beats lists only its first part; the rest must still match word for word
        assert [t[0] for t in toks] == hyp[:len(toks)], f"{iid}: markup does not match aligned hypothesis\n{hyp}"
        kept = [i for i, t in enumerate(toks) if t[1]]
        a, b = kept[0], kept[-1]
        drop |= {(iid, i) for i in range(a, b + 1) if not toks[i][1]}
        hesitate |= {(iid, i) for i, t in enumerate(toks) if t[2]}
        note = " ".join(w if k else f"[{w}]" for w, k, _ in toks[a:b + 1])
        segments.append((iid, a, iid, b, beat, note, *opt))

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
        back = 0.12 if a["text"] == "*" else 0.04  # '*' is unknown noise: allow reaching into it
        return emin(a["end"] - back, b["start"] + 0.04)

    def cut_in(k: int) -> float:
        if k in fixed_in:
            return fixed_in[k]
        w = flat[k]
        prev = flat[k - 1] if k > 0 else None
        if prev and w["start"] - prev["end"] < TIGHT:
            return between(prev, w)
        return snap_in(w["start"], prev["end"] + 0.02 if prev else 0.0)

    def cut_out(k: int) -> float:
        w = flat[k]
        nxt = flat[k + 1] if k + 1 < len(flat) else None
        if nxt and nxt["text"] == "*":
            nxt2 = next((x for x in flat[k + 2:] if x["text"] != "*"), None)
            return snap_out(w["end"], nxt2["start"] - 0.02 if nxt2 else dur)
        if nxt and nxt["start"] - w["end"] < TIGHT:
            return between(w, nxt)
        return snap_out(w["end"], nxt["start"] - 0.02 if nxt else dur)

    ranges = []
    for ia, wa, ib, wb, beat, note, *opt in segments:
        opt = opt[0] if opt else {}
        ka, kb = pos[(ia, wa)], pos[(ib, wb)]
        start, end = opt.get("start", cut_in(ka)), opt.get("end", cut_out(kb))
        seg, cur, forced = [], start, []
        keep = [k for k in range(ka, kb + 1) if (flat[k]["iid"], flat[k]["i"]) not in drop]
        for k, k2 in zip(keep, keep[1:]):
            a, b = flat[k], flat[k2]
            dropped = k2 != k + 1
            hes = (a["iid"], a["i"]) in hesitate
            if dropped or hes:
                seg.append([cur, emin(a["end"] - 0.02, a["end"] + 0.07)])
                cur = fixed_in.get(k2) or emin(b["start"] - 0.07, b["start"] + 0.02)
                forced.append(True)
            elif b["start"] - a["end"] > MAX_PAUSE:
                seg.append([cur, cut_out(k)])
                cur = cut_in(k2)
                forced.append(False)
        seg.append([cur, end])
        while len(seg) > 1:  # undo pause-shrinks that leave a micro range (stutter)
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

    # neighbouring segments of one passage can meet at the same point: merge touching ranges
    merged = []
    for r in ranges:
        if merged and abs(r["start"] - merged[-1]["end"]) < 0.005 and r["beat"] == merged[-1]["beat"]:
            merged[-1]["end"] = r["end"]
            if "reason" in r:
                merged[-1]["reason"] = r["reason"]
        else:
            merged.append(r)
    ranges = merged

    # cuts that land inside continuous voiced speech (the source is heavily compressed, so there is
    # no dip between fluent words) get 8 ms fades instead of 30 ms: a 60 ms dropout reads as a stutter
    for r in ranges:
        if db[int(r["start"] * 100)] > LOUD_DB:
            r["fade_in"] = 0.008
        if db[min(len(db) - 1, int(r["end"] * 100))] > LOUD_DB:
            r["fade_out"] = 0.008

    z, zi = ZOOMS[0], 0
    for i, r in enumerate(ranges):
        assert r["end"] - r["start"] > 0.12, r
        assert i == 0 or r["start"] >= ranges[i - 1]["end"] - 1e-6, (ranges[i - 1], r)
        if i and r["end"] - r["start"] >= PUNCH_MIN:
            zi = (zi + 1) % len(ZOOMS)
            z = ZOOMS[zi]
        r["zoom"] = z
    total = sum(r["end"] - r["start"] for r in ranges)
    edl = {"version": 1, "sources": {SRC: SRC_PATH}, "ranges": ranges, "grade": GRADE,
           "zoom_focus": FACE, "tail_hold": TAIL_HOLD, "overlays": [],
           "total_duration_s": round(total + TAIL_HOLD, 2)}
    (E / "edl.json").write_text(json.dumps(edl, indent=2, ensure_ascii=False))
    print(f"{len(KEEP)} passages -> {len(ranges)} ranges, total {total:.1f}s ({int(total // 60)}:{total % 60:04.1f})")


# picture: light temporal denoise (phone-camera grain), gentle sharpening, lifted contrast with
# soft highlight roll-off for the white walls, warmer skin, a touch more saturation, soft vignette
GRADE = ("hqdn3d=1.2:1.0:3.5:3.5,"
         "unsharp=5:5:0.55:5:5:0,"
         "curves=master='0/0.015 0.25/0.245 0.5/0.535 0.78/0.81 1/0.97',"
         "eq=contrast=1.05:saturation=1.12,"
         "colorbalance=rs=0.015:bs=-0.025:rm=0.02:gm=0.0:bm=-0.025:rh=0.01:bh=-0.015,"
         "vignette=angle=PI/7:mode=forward")

if __name__ == "__main__":
    main()
