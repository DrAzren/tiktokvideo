# Keadaan Dalam Wad Psikiatri — edit notes

Source: `raw/Keadaan Dalam Wad Psikiatri.mp4` (Drive, 3:51, 1080×1920 @ 30, single take,
Malay). Deliverable: `final.mp4`, 1080×1920 @ 30, ~2:29.

## Session 1 — 2026-09-27

**Strategy:** Cut every filler, false start, retake and long pause; move the clinic
screening plug from 0:18 to the end CTA; light contrast grade; alternate 1.0/1.08 punch-ins
at jump cuts; 10 teal/cream graphic cards in the headroom above the speaker, each element
landing on its spoken word; `loud` captions (Anton, one line above the head) with one apex
— "TIDAK" slamming in behind the head at 0:08; original ambient music bed ducked under the
voice; −14 LUFS master.

**Decisions**
- Transcription: no ElevenLabs key → faster-whisper `medium` (ms) for the transcript,
  torchaudio MMS forced alignment for word edges (Whisper edges drifted 0.1–0.9s),
  large-v3 for wording checks. 12 wording disputes settled by alignment scoring.
- Retakes kept: "Sebenarnya, tidak" (2nd), staff list take 2 (75.5s), "Jangan takut…" (2nd),
  clinic line's clean retake "Kita bincang dahulu… paling sesuai" (43.1s) — the first take's
  "aa" runs into "diagnosis" with no gap.
- "kaunselor" (86.9–87.6s) was first mistaken for a breath and cut; caught by an unprompted
  large-v3 pass and restored; the hesitation sound at 88.3s is cut instead.
- Captions say "penyakit" at 1:21 where the speaker said "pesakit" (slip; meaning fix).
- Rendering: video-use `render.py` drifted audio ~21ms per cut (0.6s by the end) →
  wrote `tools/render_edl.py` (single concat filter). Sync verified ≤0.3ms at every stage.
- Captions: stock composite screen-blends front captions (washes out white-on-grey) and
  mattes all 4477 frames (~1h+ on this CPU). Only the hero is behind the subject, so the
  matte covers frames 211–435 only; front captions rendered with real alpha and composited
  normally (`assemble.sh`).
- Music: HeyGen catalog needs sign-in → synthesized D-major ambient bed
  (`tools/ambient_bed.py`), −24 LUFS undocked, sits ≈24 dB under the voice.

**Reasoning log**
- Plug moved to the end: an ad at 0:18 loses TikTok retention; it pairs with the CTA.
- Captions above the head, not below: the chin is at 81% height; the bottom ~20% is TikTok UI.
- Hero tail trimmed to one line: a longer lockup tail ran over the mouth and into the UI zone.

**Outstanding**
- User review of the cut, cards, captions and music; swap the bed for a TikTok-library
  track in-app if preferred.
- Source audio has ~1.6k clipped samples (peak 1.0) from the original export — not recoverable.
