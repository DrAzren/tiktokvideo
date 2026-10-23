# Ubat Psikiatri Lamotrigine — edit notes

Source: `raw/Ubat Psikiatri Lamotrigine.mp4` (Google Drive, 2:29.3, 1080×1920 @ 30, H.264 + AAC 44.1k
stereo, single take, Malay/Manglish). Noise floor −68 dB. Face sits high (hair top ≈17%, eyes ≈40%,
chin ≈55% of height): text goes in the chest band (≈58–78%), not the headroom.

## Session 1 — 2026-10-23: analysis, plan, B-roll prompts

**Higgsfield (zero-credit policy):** connector reports `unlim.available: false` for Seedance 2.0 and
Nano Banana 2.1 → no generation through MCP. Balance at check 281.37 credits (Plus). Manual
Unlimited batch for higgsfield.ai: `broll/SEEDANCE_PROMPTS.md` (10 concepts + 3 variations).

**Transcription:** no ElevenLabs key → faster-whisper medium (ms) + unprompted large-v3; MMS forced
alignment per island (`align.py`, `aligned.json`). Wording settled: "iaitu Lamotrigine", "perlahan-lahan
kena titrate naik", "ruam kulit", "loya" (Whisper: "lawyer"), "susah tidur", "Dr Azren … di Nilai",
"Apa persoalan, boleh tanya di ruang komen" (large-v3 on the clip alone). `tools/transcribe_fw.py` now
decodes audio with ffmpeg (faster-whisper 1.2.1 passes an argument PyAV 19 removed).

**Proposed cut (option B, `build_edl.py`, awaiting OK):** 82.3 s + 1.5 s end card.
- Dropped: clinic ad 0:14–0:36 (the CTA at 2:17 says the same), "Okey, berbalik pada topik tadi",
  false start 57.1–58.5, "And ubat ni pula", "dan side effect" / repeated "side effect", first take
  "dia tak begitu kuat / dan ubat ni juga", "So Lamotrigine ni dia macam", recap "So Lamotrigine ni
  basically … fasa kemurungan" (repeats 0:13; option A keeps it → 1:32).
- Filler words: "sebenarnya" ×2 (WEIGHT, TITRATE), "ada" before "sama seperti". Hook "sebenarnya" kept
  (rhetorical). Four 0.2–0.3 s gaps tested for hidden hesitations (tapi/power, risiko/kenaikan,
  loya/ataupun, bantu/untuk): inconclusive, kept as natural micro-pauses.

**Medical review flags (for the doctor, words not changed):**
- 0:50 "terutamanya dalam episod kemurungan" can read as acute bipolar depression; lamotrigine's
  strongest evidence is maintenance (delaying depressive relapse), which 1:55 "nak elak kemurungan tu
  datang balik" states precisely.
- SJS section has no "if a rash appears, see a doctor immediately" — optional on-screen line, needs OK.
- On screen: "Stevens-Johnson syndrome" (spoken "Steven Johnson"), "Lamotrigine".

**Outstanding:** user OK on cut/ad/recap; Seedance clips from higgsfield.ai; then cut → voice → graphics
→ captions → mix → QC.

### Session 1, round 2 — cut, voice, graphics, captions, mix (user OK: option B, ad dropped, rash line added)

**Cut:** 83.0 s + 1.5 s end hold, 22 ranges (`edl.json`). Edge checks at 5 ms with zero-crossing rate:
MMS placed "tu" (57.0) and "sebenarnya" (10.93) late, and the energy-minimum rule lands inside /s/ onsets
(the hiss is quieter than the vowel), so "sebab" gets explicit cut points (CUT_IN / CUT_OUT). Lead-in raised to 70 ms
for soft f/s/h onsets. large-v3 on the cut hears every kept word and none of the removed ones.
**render_edl.py bug fixed:** sources with a microsecond time base drop each range's first frame at `-ss <frame time>`
(43.466666 stored vs 43.466667 asked) → +33 ms drift per occurrence. Now seeks half a frame early and takes exactly
n frames; sync 0.1–0.3 ms at every stage.
**Graphics (`graphics/build_graphics.py`, HyperFrames, lint 0 errors):** captions built into the same composition
(no behind-subject captions → no matte needed): 60 hand-split chunks, asserted equal to the cut words; 9 B-roll slots
that take Seedance clips from `public/broll/Bxx.mp4` when present (procedural fallbacks for B01/B02/B08 meanwhile);
3 full-screen infographics, 14 chest-band cards, 3D LAMOTRIGINE title docking into the chest band, end card.
Text sits in the chest band (y 1100–1370) and captions at y 1388–1535, x ≤ 910 (clear of TikTok's buttons and bottom UI).
Fixes from snapshots: background-clip text does not paint inline-block letters (title invisible); 150 px title
overflowed; "Titrate" crossed into the right-hand button zone.
**Audio:** voice.wav (enhance_speech) + 21 synthesized SFX (`audio/sfx_mix.py`) + original F-major bed, ducked
(−21.6 dB under speech). mix_music.py ceiling now −1.5 dBTP (AAC overshot to −0.9). Final −14.0 LUFS / −1.5 dBTP.
**Higgsfield:** 0 credits spent by this session (balance 281.37 before and after). Ledger shows two 0-credit Seedance 2.0
jobs + refunds at 04:35/04:40 UTC from the website.

**Outstanding:** Seedance clips (drop into `graphics/public/broll/`, rebuild, re-render, `./assemble.sh`); the user's
review of the edit; the AI-content label when posting; optional Adobe Podcast pass on voice.wav.

## Session 2 — 2026-10-23 (afternoon): more B-roll, varied transitions + SFX, speech fixes

**Ask (Malay):** use Higgsfield for AI B-roll (up to 30 credits), many more B-roll/animations, an SFX on every
transition, varied transitions (paper, 3D), paper-frame animations; fix delays between words and words cut before
they finish.

**Higgsfield:** preflight costs (9:16, no audio): Seedance 2.0 Mini 720p 5 s = 5, 4 s = 4, 480p 4 s = 2; Kling 3.0
std = 7.5; Wan 2.7 = 7.5; Seedance 2.0 fast 720p = 12.5. Generated 7 × Mini 720p 4 s = **28 credits**
(281.37 → 253.37, ledger-verified). Three batch items were bounced with a preset recommendation ("IN THE DARK"),
then resubmitted with `declined_preset_id` (bounces cost nothing). Clips: `broll/hf/S1–S7.mp4` (720×1280, 24 fps, 4.04 s).

**Speech:**
- Root cause of the clipped words: forced (filler) cuts searched only to aligned_end + 0.07 s, while CTC ends run
  about 0.1 s early. Now the search spans the aligned end to the next source word's start; QUIET_DB −46,
  TAIL_OUT 0.10, MAX_SNAP 0.45.
- Pins (CUT_IN/CUT_OUT): "lah" 73.475 (before the breathy "ha"), "rare" 90.91, "Lamotrigine" 43.585. MMS character
  peaks showed tadi's d/i at 43.45/43.51, so the earlier 43.42/43.48 starts kept "di"; the large-v3 check confirmed
  it ("Di"/"Jadi").
- Delays: new energy pass (SPEECH_DB −30) cuts every non-speech run > 0.17 s down to 0.13 s and caps quiet at joins
  (90 ms tail, 70 ms head). Gaps > 0.15 s: 22 (max 0.42 s) → max 0.16 s. 30 ranges, 82.0 s + 1.5 s hold. Sync 0.1 ms.
- large-v3 on the v2 cut: "Dia rare tapi", "loya" and "Lamotrigine ni dia famous" are all clean.

**Graphics (`graphics/scenes_v2.py`, exec'd into build_graphics):** 16 scenes, about 64% non-talking-head.
- Transitions: zoom, whip, paper tear (jagged clip-path + paper band), 3D page flip, 3D cube (with the speaker, or
  scene to scene with the speaker hidden so the navy shows), polaroid drop, iris.
- Paper-frame polaroids (Caveat handwritten labels, tape, ghost print).
- New animations: litium periodic tile that flips to "?", calendar pages, shield + check, settling mood wave.
- Kept heavy-overlay elements low: the lint warns that about 40 of them capture black frames, so tear bands and flip
  shades are only emitted where used, and the vignette is merged into .mg-bg.
- Lint 0 errors. Cards replaced by scenes: k01, k07, k15; k08 now sits over the S5 clip; k13 stays over S7.

**SFX:** 45 cues; new synthesized kinds swish, paper_rip, page_flip, cube, paper_drop, pop, each aligned to its
transition's landing time.

**Outstanding:** user review of v2; the AI-content label on posting.
