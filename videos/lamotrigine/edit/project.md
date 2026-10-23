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
