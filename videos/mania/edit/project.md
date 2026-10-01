# Fasa Mania dalam Bipolar Mood Disorder — edit notes

Source: Google Drive "MANIA.mp4" → `raw/MANIA.mp4`, 720×1280 @ 30, 2:44.9, Malay, one take filmed in a car
(VN/CapCut camera export, original_volume 500 → ~1.3% of samples at full scale). Audience: pesakit bipolar.
Deliverables: `final.mp4` (1080×1920 @ 30, 1:48.0, master) and `final_tiktok.mp4` (two-pass, 26.3 MB, to send).

## Session 1 — 2026-10-01

**Strategy:** style of `videos/ward-psikiatri` (templates: its edit/project.md, build_edl.py, graphics/build_graphics.py,
graphics/inserts.py, captions/author_captions.py, assemble.sh), built on the newest copy of that pipeline
(`videos/ada-halusinasi-yang-normal`, same 720p-source situation). Aggressive TikTok cut of every filler sound and
filler word; punch-ins 1.0/1.02/1.06/1.07; picture shifted under a teal header band; word-synced cream/teal cards
(Plus Jakarta Sans) in the headroom; 4 full-screen motion graphics + 4 AI B-roll stills (a 5th still sits behind
MG 3); `loud` captions, one line above the hair, hero "BIPOLAR" in teal behind the head; voice chain + soft
ambient bed ducked under the voice; −14 LUFS / ≤ −1 dBTP.

**User decisions (confirmation step)**
- Filler list approved as proposed (48 words + false starts/retakes + 24 voiced hesitations).
- Self-intro "Assalamualaikum, saya Doktor Azren, saya merupakan doktor di Jabatan Psikiatri" **deleted**;
  the video opens cold on the hook "Ramai yang salah faham…". No mid-video plug existed to move.
- Hero word: BIPOLAR. Scripts pushed to DrAzren/tiktokvideo (this repo), branch claude/sharp-feynman-t9jii8.

**Intake** (`edit/prep_source.sh`)
- 720p source upscaled once: lanczos to 1080×1920 + light luma unsharp, CFR 30 → `edit/source_1080_dc.mov`.
- Audio: L/R identical → mono, `adeclip`, −3.5 dB headroom, PCM 48 k. Everything downstream renders from it.
- No burned-in captions, no music bed in the source. No ElevenLabs key → faster-whisper medium (prompted, keeps
  fillers) + large-v3 (unprompted, wording).

**Alignment** (`edit/align.py`, `edit/scan_gaps.py`, `edit/burst_check.py`)
- Global MMS forced alignment with a `*` slot between every word (Halusinasi method); 386 words, mean score 0.835.
- Wording disputes scored (`align.py --variants` / `--global`): "sebelumnya nak tahu" (0.60 vs 0.46),
  "bercakap", "lakukan itu" (not "bukan itu"), single "idea yang", "seorang itu", "macam tu", "di ruang komen".
  "Puteri Gunung Ledang" kept for meaning ("putih" scored 0.01 higher). "Jabatan Psikiatri" confirmed by the user
  (the transcribers heard "Sekretari"; moot — intro deleted).
- `*` gaps classified voiced (pYIN) vs breath/silence; long gaps probed with unprompted large-v3: false-start
  "ramai" (0:04.9), "aa" (0:08.9), "dia akan… dia akan…" stall (0:57.6–1:01.5), 4.6 s pause (1:42),
  false start "Ada yang saya jumpa tu" (2:12.3, re-said at 2:14.7).

**Cut** (`edit/build_edl.py`; 2:44.9 → 1:47.0 + 1.0 s end hold; 71 ranges)
- DROP (by text + time): okay ×2, dia ×14 (topic-marker "dia", incl. "dia akan… dia"), ni ×6, itu/tu ×6, jadi, pun,
  "at least satu minggu"
  (repeat), "and then", false start "Mereka ni mungkin, kalau kita tengok", abandoned retake "Penting untuk
  diingatkan bahawa gangguan bi-" (2nd take kept), the whole self-intro.
- Kept for meaning: "berbual dengan dia", "kita nampak dia", the story's "dia", "sampai tahap macam tu sekali",
  "mungkin ubat-ubatan", "dua tiga jam je", "boleh jadi terlalu aktif".
- Every `*` ≥ 0.20 s cut, and every voiced `*` ≥ 0.15 s (hesitations inside pauses < 0.45 s); a gap cut saving
  < 0.15 s (hesitation < 0.08 s) is undone. Edges snap to silence or to the energy dip at the word's own edge.
- First render: unprompted large-v3 on the cut still heard "gangguan bipolar ni **dia** adalah" — the word had
  been left out of the alignment text (the first large-v3 pass skipped it). Re-added to the text, dropped,
  re-rendered; large-v3 on the new cut hears none of the removed words.
- Envelope plots of all edges: `edit/verify/edges_*.png`. Sync (tools/check_sync.py) 0.1 ms at every range.

**Graphics** (`graphics/build_graphics.py`, `graphics/inserts.py`, `graphics/measure_pages.cjs`)
- Face: hair y≈445, chin y≈1240, centre (0.53, 0.44) on the 1080 source → SHIFT 180 px (hair ≈ y600, chin ≈ y1450).
- 10 cards (y150–450, panel grows as each element lands, heights measured in Chromium): Mitos (+ strike + red
  TIDAK BENAR stamp) → Soalan #1 "Apa itu bipolar?" → Soalan #2 "Berapa lama?" (7-day pills → "≥ 1 minggu",
  "Kurang 1 minggu? Bukan fasa mania") → Soalan #3 "Apa berlaku dalam fasa mania?" → Gejala ×3 → Risiko →
  Kes sebenar → CTA "Tanya di komen / Take care!".
- Full-screen MGs (deep teal, cream + mint, icons, word-synced): m1 Mitos/Realiti split with the mood wave
  (Fasa tinggi MANIA ↑ / Fasa rendah DEPRESSION ↓); m2 Fikiran sangat laju (idea / berisiko / fokus);
  m3 six risk behaviours with icons over the dimmed shopping still; m4 treatment ladder Terapi → Ubat-ubatan →
  Urus gejala → Kualiti hidup ↑.
- B-roll: Canva AI stills (design DAHWvUcjQms, exported 1080×1920 → `graphics/public/broll/`): desk of unfinished
  projects, 3:00 AM bedroom ("2–3 jam tidur sehari"), empty misty mountain trail (Gunung Ledang story — no
  person shown), consultation hands ("rawatan yang sesuai"), shopping bags (behind m3). 2.8–4.6 s each, cubic
  Ken Burns, "Ilustrasi AI" tag, no faces. Voice runs under every insert.
- Snapshot fixes before rendering: panel-height events made monotonic (an element landing before the kicker
  shrank the panel and clipped the Soalan #3 title), dark radial backdrop under B-roll text (mint on the bright
  consult still), m3 AI tag moved out of the bottom UI zone.

**Captions** (`captions/build.sh`, `author_captions.py`, `patch_apex.py`, `make_matte.sh`, `make_fg_alpha.sh`)
- `loud` (Anton, uppercase, white + dark stroke), one line in y≈453–580 between the cards and the hair; 122 lines,
  pinned breaks where he talks fast (min ≈ 0.48 s on screen).
- Hero "BIPOLAR" (teal #0E5E6F) behind the head at "kita kena tahu BIPOLAR" (0:06.4). The block runs through
  "gangguan bipolar ni" so the hero holds ~1.3 s (0.59 s was too tight); `patch_apex.py` puts the tail line in the
  kicker's slot above the hero (the compiler had it across the eyes) and raises the lockup so the hair covers only
  the bottom of the middle letters: occlusion 15% (was 38%, read "BI…LAR"). No card or insert in 5.55–7.8 s.
- Matte only frames 162–237 (5.40–7.93 s) of 3240; the rest of `frames_fg/` is one hard-linked blank.
- Gates: inject-fonts (Anton), check-timing --strict (321 words OK), check-occlusion --strict (OK).

**Audio** (`tools/mix_music.py --voice-fx enhance --tp -1.5`): original ambient bed (`tools/ambient_bed.py`, key F,
60 bpm) at −26 LUFS undocked, sidechain-ducked; music sits 21.2 dB under the voice. Pause-ducking is only
+0.4 dB because the cut leaves almost no pauses. New `--tp` option: the first master at −1 dBTP measured
−0.7 dBTP after AAC, so the loudnorm ceiling is −1.5 dBTP for a hard −1.

**QA** (`qa.sh`, on `final.mp4` and `final_tiktok.mp4`): 1080×1920 @ 30, 3240 frames, 1:48.0; sync worst 0.5 ms;
−14.0 LUFS, true peak −1.4 dBTP, LRA 1.2 LU; no black frames (≥ 0.1 s), no frozen frames (≥ 1 s); contact sheets
`edit/verify/final_sheet.png`, `final_tiktok_sheet.png`. `final_tiktok.mp4` = two-pass x264 1850 kb/s, audio
copied → 26.3 MB.

**Outstanding**
- Switch on TikTok's "AI-generated content" label (AI B-roll stills).
- Swap the bed for a TikTok-library track in-app if preferred.
- If a 1080p/4K export of the take exists, swap `edit/source_1080_dc.mov` (prep_source.sh) and re-run from
  `render_edl.py` (timings unchanged).
