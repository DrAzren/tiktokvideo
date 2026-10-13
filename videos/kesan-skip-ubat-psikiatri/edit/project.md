# Kesan Skip Ubat Psikiatri — edit notes

Source: `raw/skip.mp4` (Drive "Kesan Skip Ubat Psikiatri.mp4", 2:09, 720×1280 @ 30, one continuous take in a
car, Malay/Manglish; CapCut export with the voice boosted: −6 LUFS, true peak +0.9 dBTP; recorded MIRRORED
by the front camera — "DR AZREN" on the scrubs reads backwards).
Deliverables: `final.mp4` (1080×1920 @ 30, ~1:24, −14 LUFS) and `final_tiktok.mp4` (same, < 30 MB).
Pipeline and scripts follow `videos/ubat-psikiatri-olanzapine` (template named in each script's docstring).

## Session 1 — 2026-10-13

**Strategy (user-approved, all recommendations taken):** hook = the patient-voice question ("Doktor, saya dah
sihat sikit. Saya nak berhenti ubat sendiri. Takpe ke, doktor?") moved ahead of the greeting; greeting →
"Jom kita sembang sekejap. Apa jadi kalau kita skip ubat psikiatri tanpa bincang dengan doktor?" → three
risks → clinic plug (moved from 0:23) → CTA. Cut every filler sound and filler word on the approved list,
punch-ins cycling 1.0/1.06/1.02/1.07 on every jump cut; 8 compact cream/teal cards in the headroom;
4 full-screen motion graphics + 6 Canva AI stills; `loud` captions one line above the hair with
"BERHENTI" slammed in teal behind the head; ambient bed ducked under the voice; varied SFX; −14 LUFS master.

**Decisions**
- Transcription: no ElevenLabs key → faster-whisper medium (ms) + large-v3 unprompted, torchaudio MMS forced
  alignment for edges (`edit/align.py`, 13 islands). The silent "listening" stretches (0:03.7–0:09.5,
  0:14.8–0:23.2, 0:45.9–0:49.6) have no speech (large-v3 hallucinates "Terima kasih kerana menonton" there).
- Hesitations found by `edit/gap_scan.py` (voicing in gaps) and confirmed on spectrograms
  (`edit/spectro.py` → `verify/spectro.png`): nak, di, berulang (held "-ng"), otak kita, contohnya (0.55 s),
  rasa, menjadi-jadi, loya, kepala, tidur, start, dan, pasti, plus "ke [eee] anxiety" in the plug.
- Filler words dropped (DROP in `edit/build_edl.py`): sebelum tu, ok berbalik kepada topik tadi, the second
  "saya", ada (kami ada menyediakan), ke ×2, adalah ×2, dia ×7, jadi ×2, the first "boleh" (atau boleh
  sampai tahap boleh masuk wad), macam ×2 (rasa macam), bila, umpamanya, dan ×2, tu dah, sendiri.
  Kept for meaning: "saya dah sihat sikit", "ubat ni macam pelindung", "tak efektif macam dulu", "ada ubat",
  "saya ada berita baik".
- "dan lain-lain lagi lah" (×2) dropped whole, not just "lagi lah": "lain-lain|lagi" is one voiced run with
  no clean edge, and the first render kept a "la-" sliver (caught by mapping words through the EDL).
- Plug vs CTA: both ended "boleh datang klinik saya di Nilai"; the CTA's repeat is cut (the plug says it).
  The abandoned first "Saya ada berita baik" take (0:16.8) is dropped; the retake opens the plug.
- No unfinished sentences in this recording.
- The source is mirrored → `hflip` in the EDL; 720×1280 → `out_size` [1080, 1920] upscaled in the same
  lanczos pass as the punch-in crop, light unsharp (both new options in `tools/render_edl.py`).
- PUNCH_MIN 0 (user: a zoom change on EVERY jump cut, no two neighbouring ranges at one zoom); segment joins
  that are continuous in the source are merged so they don't count as cuts. TAIL_HOLD 2.0 s so the end card
  (clinic / bio / DM) has ~3 s.
- Sync: `check_sync.py` worst lag 0.1 ms on cut.mp4 and graphics/output.mp4.
- Layout: hair top y ~490–560 on the cut → cards y 130–372 (asserted per page from `measure_pages.cjs`
  real-browser heights), caption line y ~392–500, MG titles end ~y300.
- B-roll (Canva design DAHX3opdk74, pages 2–7 exported 1080×1920; the auto-generated cover page 1 is not
  used): umbrella in rain ("Ubat = pelindung"), empty calm ward ("Masuk wad balik"), generic unbranded
  weekly pill organiser — no box, label or lettering ("Bila berhenti secara mengejut"), stairs from the bottom
  step ("Mula balik dari bawah"), empty consultation room ("Klinik saya · Nilai"), blank signpost at a fork
  ("Keliru? Teruskan rawatan atau tidak?"). No faces; all tagged "Ilustrasi AI".
- Motion graphics: SKIP title (skip icon, "tanpa bincang dengan doktor?", 1-2-3 kesan), relapse escalation
  (mood swing → cemas, severity bar; the ward still takes the third step), withdrawal symptom rows with icons
  (loya, pening, tidur, emosi, serabut), STOP/START flip loop → RESET button. Red stamp "BUKAN SEMUA UBAT"
  on its own card page (it collided with the long "Withdrawal symptom" title).
- Captions: `loud`, 0.046·h, ≤ 24 chars (every line width-measured in Chromium: widest 964 px of the 994 px
  plane), forced breaks at clause ends, a no-orphans pass (single short words merge or borrow a word) and
  a few hand re-breaks (`REBREAK`). Remaining lines under ~0.55 s: "yang kedua", "yang ketiga", "boleh dapat",
  "ataupun tidak" (fast speech). "gejala penaikan" captioned "gejala penarikan" (user-approved).
  Hero lockup patched (`captions/patch_apex.py`); occlusion gate: hero 7 % covered (bottom edge only).
  Matte only for frames 1–138 (hero window); the rest of `frames_fg/` are hard links to one transparent PNG.
  Gates: inject-fonts, check-timing --strict (217 words), check-occlusion --strict all pass.
- Audio: synthesized bed (`tools/ambient_bed.py`, key F, 60 bpm, seed 23); SFX cue sheet
  (`audio/make_sfx.py` → `audio/sfx_cues.txt`): 56 cues / 21 sounds, mixed after the ducking.

**QA (final.mp4 / final_tiktok.mp4)**
- 1080×1920 @ 30, 83.97 s (2519 frames), −14.0 LUFS, true peak −3.4 dBTP; sync worst lag 0.1 ms.
- No black frames. Freezes ≥ 0.5 s only where intended: two still beats inside the withdrawal list (35.3 s,
  40.5 s) and the 2 s end-card hold.
- Music under speech −20.6 dB vs voice (+2.5 dB in pauses = ducking). SFX cue peaks a median 7 dB under the
  voice peaks (loudest: the hero impact, +2 dB).
- final_tiktok.mp4: two-pass x264 2.5 Mb/s, 28.4 MB.

**Outstanding**
- Switch on TikTok's "AI-generated content" label (six AI stills, tagged "Ilustrasi AI" on screen).
- Optionally swap the bed for a licensed track in the TikTok app.
- Source is a 720p CapCut export: upscaled to 1080×1920, slightly softer than a native 1080p recording.
