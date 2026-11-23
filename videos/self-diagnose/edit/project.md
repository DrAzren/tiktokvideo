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
