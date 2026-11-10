# 10 Ubat Psikiatri Dilarang Untuk Mengandung — edit notes

Source: `raw/10 Ubat Psikiatri Dilarang Untuk Mengandung.mp4` (Drive, 3:47, 1080×1920 @ 30 CFR,
single take, Malay). Deliverable: `final.mp4`, 1080×1920 @ 30, 2:17.7.

## Session 1 — 2026-11-10

**Strategy (approved):** cut every filler sound and filler word ("dia", "ha/uh", "sebenarnya",
"lah", "itu", "dekat"), every false start and retake (hook take 2, intro take 2 — take 1 says
"saya bukan doktor"), shrink all pauses; light denoise/sharpen + warm grade; punch-ins on jump cuts;
headroom cards #1–#10 (drug, brand, use → "Risiko kepada bayi" page with a red icon, each landing on
its word); 3 full-screen motion graphics (hook "berhati-hati / elakkan", recap grid with "BUKAN 100%
DILARANG", "Beritahu doktor anda → Pemantauan rapi"); 4 AI B-roll clips; `loud` captions with a
"10 UBAT" hero behind the head; "Tanya di komen" end card; music + SFX; −14 LUFS.

**Credits (user asked for the minimum and to be told first)**
- Higgsfield: 4 × Seedance 2.0 Mini (9:16, 720p, 4 s, silent) = 16 credits (cheapest native-9:16
  model; Seedance 2.5 = 28–35 each). The first ultrasound prompt (fetal scan) was blocked by the
  content filter and refunded; replaced by a clinic room with an ultrasound machine.
- Higgsfield Mirelo SFX: 5 clips, 1.5 credits — came back near-silent (−55 to −70 dB noise floor;
  stamp/chime only faint hits). Not used. SFX synthesized locally instead (`tools/sfx_synth.py`, 0 credits).
- Music: user chose the free option → `tools/ambient_bed.py` (F major, 64 bpm), 0 credits.
- Total spent: 17.5 Higgsfield credits (500.31 → ~482.8). ElevenLabs: only price estimates, nothing charged
  (5 empty estimate nodes left on flow EaH0kauELdTXD9EpkrCA).

**Decisions**
- No ElevenLabs Scribe key → faster-whisper medium (ms) + unprompted large-v3 for wording;
  torchaudio MMS forced alignment for edges (`align.py`, passages P01–P17).
- `build_edl.py` writes the cut as markup over each aligned passage (`[dropped words]`), so the
  approved filler list reads directly. Three aligner "slivers" were re-timed from spectrograms
  (`CUT_IN`: "ha" before "yang keempat", "ha dia" before "dikaitkan", "eee" after "mood stabilizer").
- Kept three sentence-final "lah" (bipolarlah ×2, doktorlah): fused to the word with no gap; cutting
  clips the word ("bipola–"). Told the user; drop on request.
- The source is heavily compressed (−6.9 LUFS, clipped at +0.4 dBFS), so fluent words have no energy
  dip between them: cuts inside voiced speech get 8 ms fades instead of 30 ms (a 60 ms dropout reads
  as a stutter).
- **render_edl.py frame-drift bug fixed:** printing -ss/-t to 6 decimals caught one extra frame on
  x.x6667 s frame phases; concat padded the audio and later cuts drifted to +200 ms. Now seeks half a
  frame early and trims to exact frame/sample counts → 0.5 ms worst case at every stage.
- Layout: head sits high (hair ~y420, chin ~y1280–1310), so cards are a compact band under TikTok's
  top tabs (y 140–376) and captions run one line on the chest (y ~1336–1470), not above the head.
- Hero "10 UBAT": the compiler's mass rule sizes it 0.40h (overflowed, head hid it all) →
  `patch_apex.py` sets 0.13h at 11.5% and moves its tail ("psikiatri yang perlu") into the chest band.
  Matte only for 0–2.4 s (72 frames); everything else is a transparent matte.
- Topiramate card says "Sawan · Migrain" (speaker said "mood stabilizer"; user approved).

**Outstanding**
- User review of final.mp4. Remind: switch on TikTok's AI-generated content label (B-roll is AI).
