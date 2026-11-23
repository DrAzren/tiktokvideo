# Self Diagnose — project notes

## Session 1 (2026-11-23)

**Source:** `raw/Self Diagnose.mp4` from Google Drive (3:19, 720×1280, 30 fps VFR, car interior). Raw untouched.
`edit/source_cfr.mov` is a constant-30fps working copy: cutting the VFR file directly drifted audio up to 134 ms.

**Transcript:** local Whisper medium (no Scribe key), then MMS_FA forced alignment (`align.py` → `aligned.json`).

**Cut (`build_edl.py` → `edl.json` → `cut.mp4`):** 1:36.6, 43 ranges, sync 0.1 ms worst, −14.0 LUFS.
- Hook: "Dia rasa macam jantung dia nak meletup, dan dia yakin yang dia akan mati" moved from 1:17 to the open.
- Dropped: three retakes, dead air, "setelah ditenangkan / sesi soal jawab", the parents' quote (repeats the hook),
  "crying non-stop", "mengelakkan diri daripada socialise", "itulah sebab ... hospital", "tak pernah dapat bantuan",
  "kesihatan mental adalah isu penting ... bantuan profesional boleh buat perubahan", fillers (sebenarnya, lah, jadi).
- Two aligner word starts were wrong and are overridden (144.90 "Dia", 173.57 "Sokongan").

**Plan agreed so far:** 1080×1920 final; HyperFrames motion graphics + one-line Malay captions; locally
synthesised music/SFX; AI B-roll via Higgsfield, hard cap 40 credits, user chose Gemini Omni Flash 1.2 at 1080p.

**Outstanding**
- User approval of the revised Gemini cost table before any paid generation (0 credits spent so far).
- User to confirm: patient-identity disclaimer; wording at 0:50 ("dapatkan ___ profesional" — aligner best match
  "rawatan"); "sesak nafas, sakit dada".
- Voice clean-up (source peaks at +0.7 dBTP, some clipping), graphics, captions, SRT, music, final render.

## Session 1, continued — graphics, captions, audio, final

**Approved by user:** 3 Gemini Omni Flash 1.2 clips (3 s, 1080p, 9.75 credits each) + 3 Z Image stills (0.15 each);
identity disclaimer on screen; caption wording "rawatan profesional" at 0:34.
**Higgsfield spend:** 29.70 credits (balance 2,509.18 → 2,479.48), no retries. Cap was 40.

**Graphics + captions (`graphics/build.py` → `public/index.html`, one HyperFrames composition):**
16 headroom cards, 6 B-roll inserts (ER arrival, hands, phone, room, supplements, consultation — all tagged
"Ilustrasi AI"), 4 full-screen motion graphics (symptoms, the three self-applied labels, diagnosis reveal,
internet vs professional assessment), 90 one-line captions at y≈1420, `captions_ms.srt` (45 cues).
The reveal dims the three labels with "?" rather than striking them out: the recording never says they were ruled out.
Hook title fix was rendered as a 4.5 s segment and spliced into `output.mp4` (first 135 frames).

**Audio (`assemble.sh`):** `tools/enhance_speech.py` voice, synthesized SFX (`audio/make_sfx.py`, 74 cues, −9 dB),
`tools/ambient_bed.py` bed in D at 60 bpm ducked to −21.8 dB under speech. Final −14.0 LUFS / −1.0 dBTP, sync 0.4 ms.
The source was recorded hot but is not clipped (astats flat factor 0).

**Outputs:** `final.mp4` (master, 1080×1920, 30 fps, 1:36.7), `deliverables/` (upload copy at CRF 19, SRT, clean
dialogue, B-roll, project source, bed + SFX stems).

**Outstanding**
- User has not yet listened: cuts were checked by re-transcription and envelope plots only.
- Runs 1:36.7 against a 90 s target; candidates to drop are listed in the session notes above.
- Switch on TikTok's "AI-generated" label when posting.
