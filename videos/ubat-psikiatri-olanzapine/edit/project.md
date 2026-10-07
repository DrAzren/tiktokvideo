# Ubat Psikiatri Olanzapine — edit notes

Source: `raw/Olanzapine.mp4` (Drive, 2:26, 1080×1920 @ 30, single take in a car, Malay/Manglish; CapCut
export with the voice boosted: −6 LUFS, true peak +0.6 dBTP, car-noise floor ~−30 dB).
Deliverables: `final.mp4` (1080×1920 @ 30, ~1:25.5, −14 LUFS) and `final_tiktok.mp4` (same, < 30 MB).
Pipeline and scripts follow `videos/ward-psikiatri` (templates noted in each script's docstring).

## Session 1 — 2026-10-07

**Strategy (user-approved):** cut every filler sound and filler word incl. the optional ones, drop the
abandoned first plug take, move the plug (retake, 0:36) to the end before the CTA, punch-ins cycling
1.0/1.06/1.02/1.07 on jump cuts; 8 compact cream/teal cards in the small headroom; 4 full-screen motion
graphics + 6 Canva AI stills; `loud` captions one line above the hair with "OLANZAPINE" slammed in teal
behind the head; ambient bed ducked under the voice; prominent transition SFX; −14 LUFS master.

**Decisions**
- Transcription: no ElevenLabs key → faster-whisper medium (ms) + large-v3 unprompted (fills the windows
  medium skipped, settles wording), torchaudio MMS forced alignment for edges (`edit/align.py`, 13 islands).
  `tools/transcribe_fw.py` now loads 16 kHz WAVs with soundfile (PyAV 15+ broke faster-whisper's decoder).
- Hook: "Ada patient panggil…" (3.8 s) is never finished — 5.5 s of closed-lip silence follows. User chose
  to drop the line; the hero word became OLANZAPINE.
- Hesitations found by `edit/gap_scan.py` (voicing in gaps) and confirmed on spectrograms: after delusi, bila,
  "ubat ni", bagus, ini, masa, kalau, sendiri, cakap; held tails after skizofrenia, juga, ketiga (HESITATE).
- Filler words dropped (DROP): sebenarnya ×3, itu, lah ×3, "dia dah", "jadi apa yang saya bagi tahu
  selalunya", "ada" ×2, the false-start "boleh"; plug's "tapi jangan risau" and its own "tekan di bio untuk
  book slot anda" (the CTA right after says it with "atau DM").
- "Ubat ini sangat bagus…" (87.4 s) kept after "makan ubat ni": the joint I08/I09 alignment showed the
  hesitation + "sebenarnya" between them; reads as two sentences.
- Car noise floor: edge snapping uses QUIET_DB −26 (ward used −40).
- `tools/render_edl.py`: ranges are now trimmed to an exact frame/sample count. `-ss/-t` input seeking
  emitted one extra frame on two short ranges and concat padded the audio → 33 / 67 ms drift against the
  EDL timeline. Sync now ≤ 0.2 ms at every stage.
- PUNCH_MIN 0.45 s (ward 0.8): at this pace 0.8 left six jump cuts with no zoom change.
- Layout: hair top y ~460-520 (423 on 1.07 punch-ins) → cards y 130-372 (asserted per page from
  `graphics/measure_pages.cjs` real-browser heights), caption line y ~392-480, MG titles end ~y350.
- B-roll (Canva, design DAHXTxIEafo, exported 1080×1920): lake (quote "Dunia kembali senyap"), tablets in a
  palm, balanced meal, morning bedroom, clinic desk, and a generic blister of yellow tablets for the
  "Olanzapine" beat. User asked for an AI version of a real brand's packaging (Olanza); declined to recreate a
  real product's trade dress — the still is unbranded with no text, "OLANZAPINE · Ubat psikiatri" is our own
  type on top. The Canva auto-generated cover page (with "B-ROLL" text and a labelled bottle) is not used.
- Captions: `loud`, 0.046·h, ≤ 23 chars, forced breaks at clause ends large-v3 left unpunctuated, a
  rebalance pass so short lines borrow a word; 4 lines remain 0.42-0.49 s (fast speech, no clean merge).
  Hero lockup patched (`captions/patch_apex.py`): plane 9 %, hero under the kicker, tail takes the
  kicker's slot. Matte only for frames 1-111 (hero window); the rest of `frames_fg/` are hard links to one
  transparent PNG. Gates: inject-fonts, check-timing --strict, check-occlusion --strict all pass.
- Audio: synthesized bed (`tools/ambient_bed.py`, D, 64 bpm) at −20 LUFS undocked; SFX
  (`audio/make_sfx.py`) from `graphics/sfx_events.json` + the hero impact, mixed after the ducking via the
  new `tools/mix_music.py --sfx`. Test mix: SFX peaks 5-7 dB under voice peaks — clear, never masking words.

**Outstanding**
- Switch on TikTok's "AI-generated content" label (six AI stills, tagged "Ilustrasi AI" on screen).
- Optionally swap the bed for a licensed track in the TikTok app.
- Source audio is clipped in places (true peak +0.6 dBTP in the CapCut export) — not recoverable.
