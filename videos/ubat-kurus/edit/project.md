# 3 Ubat Psikiatri Kuruskan Badan — edit notes

Source: `raw/3 Ubat Psikiatri Kuruskan Badan.mp4` (Google Drive, 2:12, 720×1280 @ 30, single take in a car,
Malay with English drug/clinical terms). `raw/ubat.mp4` is a symlink to it.
Deliverable: `final.mp4`, 1080×1920 @ 30, 1:24.2 (1:23.0 of speech + 1.2 s end hold).

## Session 1 — 2026-10-31

**Strategy (approved):** cut the fluoxetine retakes and Malay padding words, open on an on-screen hook
title, subtle grade with 1.0/1.06/1.02/1.07/1.035 punch-ins at jump cuts, teal/cream cards in the car-roof
headroom (same system as `ward-psikiatri`), three full-screen inserts, `loud` captions on one line across
the chest, original ambient bed, −14 LUFS.

**User decisions:** cut the back-reference "Sebelum ni saya pernah buat satu video… kenaikan berat badan";
Higgsfield budget capped at **35 credits** → exactly one Seedance 2.5 clip (preflight cost: 35); captions on
the chest band.

**Cut** (`edit/build_edl.py`, 13 segments → 28 ranges)
- Fluoxetine: kept take 1 "Yang ketiga adalah fluoxetine" + the clean take at 88.5 s; dropped 64.0–88.3 s
  ("SSRI ni", "…SSRI yang popular, yang commonly used for", "Ehm", "Ni adalah SSRI yang commonly used for", "Ehm").
- Dropped: "Ok", "Tapi … pula" around the hook, "sebenarnya" ×3, the trailing "merokok *juga*", padding "dia"
  in "ada orang *dia* hilang" and "setiap ubat *dia* ada", the "* dia ada" false start at 45.3–46.6 s.
- Tried and restored: "kesan sampingan *dia* ada". large-v3 heard the cut as "kesan-kesan pingat dia"
  (tight connected speech).
- Kept as said: "boleh menyebabkan **kenaikan** berat badan pada setengah orang" (both Whisper models agree;
  reads as intended: the three drugs can even raise weight in some people).
- No voiced hesitations hide in short gaps (no gap > 0.3 s carries voice).

**Transcription:** no ElevenLabs key → faster-whisper `medium` (ms) + unprompted large-v3 for wording
("doktor di Jabatan Psikiatri", not "Reja Butang"); torchaudio MMS forced alignment for edges (I07 re-aligned
from 45.25 s to separate the false start). `tools/transcribe_fw.py` now decodes with ffmpeg itself (PyAV in
the venv rejected faster-whisper's `metadata_errors` kwarg).

**Render fixes (tools/render_edl.py)**
- New EDL `output_size` (720p source → 1080×1920 once, lanczos).
- Frame-exact ranges: `-t` formatted to 6 dp pulled in one extra frame whenever a range ended on a ⅔-frame
  pts, and concat padded that range's audio with silence → +33 ms per hit (+100 ms by the end). Each range now
  reads half a frame long and is trimmed to exactly n frames / d seconds. Sync 0.1 ms worst at every stage.

**Graphics** (`graphics/build_graphics.py`, anchored to phrases in `edit/cut_words.json`)
- Cards: hook (frame 0, name row at "doktor"), #1 Bupropion, #2 Topiramate, #3 Fluoxetine, takeaway, CTA with
  "Info pendidikan · bukan nasihat perubatan". Panel heights measured in Chromium (`measure_pages.cjs`);
  every page asserted to end at or above y 560 (hair top; never the face).
- Inserts: `b1-pil` Seedance 2.5 (pharmacy blister pack, 9:16 720p 5 s, no audio, "Ilustrasi AI" tag, job
  b1b462df), `m1-kurva` fluoxetine weight curve (dip early, back up long-term, PERLU MONITOR), `m2-jangan`.
- Lint: the video is timed, its wrapper is not (`video_nested_in_timed_element`); cards exiting behind an
  insert are intentional (`data-layout-allow-occlusion` on the video). `hyperframes check` passes.
- Fonts: Plus Jakarta Sans 500/700/800 from @fontsource (OFL), staged in `graphics/public/fonts`.

**Captions** (`captions/`): `loud`, Anton 0.046 h, one line in the chest band (top 68 %, width 80 %, left of
the action buttons); 87 lines from a DP line-breaker (≤ 21 chars, never across a sentence end, ≥ 0.5 s where
possible). Display fixes: Azren, topiramate, joined reduplications. All captions in front of the subject →
no matte; the plain `index.html` render is the captioned video. Gates: inject-fonts, check-timing --strict,
check-overflow.

**Audio:** source is very hot (decoded peaks 1.47, 7.6 % of samples over full scale, mostly AAC overshoot of a
hot wireless-mic level; any capture clipping is unrecoverable). Bed: `tools/ambient_bed.py` F / 72 bpm, mixed
with `tools/mix_music.py --bed-lufs -20`.

**Container notes:** this image ships `chromium_headless_shell-1243/chrome-headless-shell-linux64/` (setup.sh
and CLAUDE.md now find either layout).

**Outstanding**
- User review. Switch on TikTok's "AI-generated content" label (the pharmacy clip is AI).
- Optionally swap the bed for a TikTok-library track in-app.
- Next recording: lower the wireless-mic gain a few dB.
