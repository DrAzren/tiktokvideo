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
