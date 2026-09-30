# Berapa Lama Makan Ubat Psikiatri — edit notes

Source: `raw/ubat.mp4` (Drive "Berapa Lama Makan Ubat Psikiatri", 2:30, 2160×3840 @ 60, Malay).
Template: `videos/ward-psikiatri` (same pipeline, palette, caption identity).

## Session 1 — 2026-09-29 (intake + filler scan)

**Source findings**
- CapCut ("vicut") export: burned-in CapCut captions (y≈1410–1560, on screen in 149/155 half-second
  samples), a music bed mixed under the voice (`music_volume 20`), and black frames + music only from
  77.77 s to the end. Usable take: 0–77.7 s, one continuous shot, no internal cuts.
- Framing: head top y≈385 (20% of height), chin y≈1180 — far less headroom than ward-psikiatri (~36%).
- Working copy `edit/src1080.mp4` (1080×1920 @ 30, CRF 14); raw is untouched.

**Transcription / alignment**
- No ElevenLabs key → faster-whisper `medium` (ms, filler prompt) + unprompted large-v3 (wording).
- demucs htdemucs `--two-stems=vocals` on the take: vocal stem floor ≈ −50 dB, music removed. Alignment,
  envelope (`envelope.py`) and filler scan run on the vocal stem (`vocals16k.wav`).
- MMS_FA per island (`align.py`); `align.py --stars` puts a `*` slot between every word to expose
  unlabelled sounds; `scan_fillers.py` + `cand_plot.py` classify them by spectrogram
  (broadband = breath, flat harmonics = held vowel / hum).

**Draft cut** (`build_edl.py`): 77.5 s → 61.3 s, 37 ranges; DROP / HESITATE / TRIM lists pending approval.

**Open questions for the user (answered in session 2):** clean CapCut re-export vs working around the
burned captions; caption position given the small headroom; B-roll source (no Gemini access here).

## Session 2 — 2026-09-30: cut, graphics, B-roll, captions, audio

**User picks:** use the file as sent (no re-export) → crop out the burned captions; captions just above
the head; Canva AI stills + Ken Burns (no Gemini access); hero "BERGANTUNG"; filler list approved as
proposed ("Adakah … seumur hidup saya?" kept; "sama juga macam" kept).

**Source / cut**
- `make_source.py`: crop 1580×2808 from the 4K frame at x=354, y=0 (bottom edge y=1404 on the 1080 grid;
  burned text never above 1421) → 1080×1920 @ 30, audio = demucs vocal stem (music removed). The crop is
  1.3675×, taken from 4K pixels (no upscale). Side effect: more headroom (hair top y≈470–520), mouth at
  y≈1520, chin inside the bottom-20% TikTok UI zone — accepted by the user as the price of option (b).
- `build_edl.py` (DROP/HESITATE/TRIM as approved): 77.5 s → 60.8 s (+1.0 s end hold), 35 ranges,
  punch-ins 1.0/1.06/1.02/1.07 at nose height (FACE 0.50, 0.62).
- Edge fixes found by the envelope plots: a breath that never drops below −40 dB made both edges fall
  back to the same mid-gap dip (kept the breath, 60 ms fade dip mid-speech) → fallback now searches near
  each word's own edge; short coarticulated drops ("ni", "tu") cut at their own edges; touching ranges merged.
- Verified: unprompted large-v3 on the cut reads back exactly the approved script; sync worst 0.1 ms;
  before/after frame pairs at all 34 cuts clean.

**Graphics** (`graphics/build_graphics.py`, `inserts.py`; Plus Jakarta Sans from Google Fonts, latin subset)
- Cards (compact, y 140–350): Soalan #1 / #2 (SEUMUR HIDUP?) hook, Soalan #3 "Kenapa lama?", "Stabil dulu,
  baru berhenti", penyakit kronik chips, "Paling penting: jangan stop suka-suka", Mitos "Hukuman seumur hidup"
  struck + TIDAK BENAR → Realiti "Peluang untuk sembuh", CTA "Ada soalan? Tanya di komen".
- Full-screen MG: M1 duration bars (ringan 6–12 bulan / pernah relapse lebih lama), M2 stop-too-early →
  symptoms back → risk gauge TINGGI, M3 chronic mental = darah tinggi / kencing manis, M4 tapering staircase
  100→75→50→25% + "Elak withdrawal symptom".
- B-roll (Canva design DAHWoZbdUAA pages 2–5, exported 1080×1920): consultation (hands only), pill
  organizer + calendar, pill cutter, park walk from behind; cubic Ken Burns; "Ilustrasi AI" tag.
- Fixes from snapshots: ward's card_end() rule also fired for a card starting after an insert (negative
  duration → card bled through later) → only cards already on screen; `.half` class collision (ward split
  CSS) made M3 boxes 950 px tall → `.pair`; GSAP needle needed `svgOrigin`; stamp resized / title shortened.

**Captions** (`captions/`): `loud` (Anton, uppercase, white + dark stroke), one line ≤21 chars at 0.047h in a
plane at y≈363–486 (just above the hair; smaller than the DNA's body tier because of the headroom).
Hero "BERGANTUNG" 0.10h teal behind the head (occlusion avg 13%, peak 20%); kicker/tail patched to one
centred line each (`patch_apex.py`). Matte only for 6.0–9.0 s (`build_matte_frames.py`); gates: timing
--strict OK (174 words), occlusion --strict OK. Punctuation from large-v3 on the cut (hyphenated
reduplications re-joined so "suka-suka." ends a line).

**Audio:** original bed `tools/ambient_bed.py --key F --bpm 70 --seed 23`, mixed with `mix_music.py --bed-lufs -20`.
