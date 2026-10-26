# 10 Ayat Yang Tidak Boleh Dicakap Pada Orang Yang Ada Masalah Mental — edit notes

Source: `raw/10 Ayat Dilarang Cakap.mp4` (Drive, Dr Azren; 2:33, 720×1280 @ 30, one take, Malay, filmed in
a car). Deliverable: `final.mp4`, 1080×1920 @ 30, H.264 + AAC stereo, ~2:00. Background: the user's
warm botanical podcast-studio image (`assets/studio_bg.webp`, used as is, softened for depth of field).

## Session 1 — 2026-10-26

**Brief (user's master prompt):** keep all 10 statements in order with their explanations; replace the
background with the supplied studio; aggressive filler/pause removal without clipped words; hook "10 AYAT /
JANGAN SESEKALI CAKAP!"; a "0N / 10" counter, the harmful line in large type with a red strike, supportive
takeaways in gold/ivory; Higgsfield B-roll capped at 30 credits; SFX on every transition; ambient piano;
Malay word-highlight captions; end card "Kata-Kata Kita Ada Kesan." + "Dr Azren | Spread Positivity".

**Approved strategy:** cut the first "Yang ke lapan" take, the "Ha" (0:42), the "eh… err" after "semudah",
"eee" after "proses" and "sembuh", the drawn "eee" before "Yang ke sepuluh", the "bukan being judgemental,
bukan… apa" false start, both "okey" around "Kesimpulan dia"; drop "dia/lah" padding only where the cut is
clean; keep "Okey, rehat penting" and "Betul, doa tu penting"; caption the last line "boleh tanya dalam komen".

**Decisions**
- Transcription: no ElevenLabs key → faster-whisper medium + large-v3; MMS forced alignment per island
  (`edit/align.py`, alternatives as `{a|b}`); fillers found by spectrogram (`edit/spec.py`).
- Padding words: of six proposed, only "tapi *dia* sebenarnya" (a drawn 0.4 s "diaaa") had a clean
  boundary. "ni dia bukan", "tapi dia melibatkan", "mental dia tu", "ni dia bukanlah", "lagi lah keadaan"
  are fused into the next word (no energy dip, `edit/verify/drops.png`) and stay.
- Cut 2:33 → 1:56.6 (+3 s end-card hold). Verified: large-v3 on the cut hears all 10 statements in order and
  none of the removed fillers (`captions_src/large_v3_cut.json`; its "Sebenarnya" after "Kesimpulan dia" is a
  hallucination in a 0.33 s gap).
- `tools/render_edl.py` fix: ranges are trimmed to exact frame/sample counts. A boundary frame had made concat
  pad audio by one frame per affected cut (167 ms late by the end); now worst lag 0.3 ms (`check_sync.py`).
- Background removal: hyperframes `remove-background` (u2net) glued the car-seat headrest and seatbelt to the
  head. RobustVideoMatting ResNet50 via its official ONNX export (`tools/rvm_matte.py`, onnxruntime; cloning
  and running the repo's Python was blocked as external code) matted the whole source (2.3 fps, 33 min), cut
  with the same EDL. `tools/refine_matte.py`: choke, roof-lining decontamination at the edge, and two fixed
  zones (`--zone 140,540,262,760 --zone 488,560,610,760`) where only skin survives near the edge — the
  driver-seat headrest wings behind the ears.
- Speaker layer: lanczos 720→1080 + light unsharp, warm grade to match the lamps, VP9 alpha WebM.
  Punch-ins 1.0/1.15/1.30 at cuts (1.30 on the hook; capped at 1.15 while a headroom card is up); the
  background scales a quarter as much (parallax).
- Higgsfield: Seedance 2.0 Mini, 9:16, 720p, 5 s, no audio — 5 credits each (preflighted), 5 clips =
  **25 credits** (cap 30). Window/invalidation, words→particles, clinic consultation, morning "keep going",
  two friends (support). Reused: slowed words clip behind the end card, a tight reframe of the support clip.
  All tagged "Ilustrasi AI".
- Motion graphics (HyperFrames, `graphics/build_graphics.py`): brain-chemistry network (#1), recovery path
  (#6), pressure vessel "pendam perasaan" (#8), Playfair quote card "Saya ada di sini…" (conclusion), end card.
  Ten different quote entrances (rise, blur-slide, type, pop, slam, wipe, tracking, split, drop, 3D flip).
- Voice: `tools/enhance_speech.py --car` (new: 4th-order 90 Hz high-pass + stronger afftdn for road rumble).
- Music: `tools/piano_bed.py` (new): original D-major ambient piano, 72 bpm soft pulse, resolves on the tonic.
- SFX: synthesized (`audio/build_audio.py`) on all 129 cues the composition emits; mix ducks the bed under the
  voice; music+SFX measured ~23 dB under the voice during speech; master -14 LUFS, -1.5 dBTP.

**Outstanding**
- Switch on TikTok's "AI-generated content" label (the B-roll is AI).
- Source is 720p (upscaled); the car recording's road noise is reduced, not removed.
