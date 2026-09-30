# Ada Halusinasi Yang Normal — edit notes

Source: Google Drive "Halusinasi.mp4" (clean CapCut re-export: no captions, no music) →
`raw/Halusinasi_clean.mp4`, 720×1280 @ 60, 2:12.45, Malay, one take from a CapCut draft.
(`raw/Halusinasi.mp4` = the first upload, 4K, with CapCut captions burned in and a music bed mixed
into the voice — not usable; kept only for reference.) Deliverable: `final.mp4`, 1080×1920 @ 30, ~1:50,
plus `final_tiktok.mp4` (two-pass, < 30 MB) to send.

## Session 1 — 2026-09-30

**Strategy:** style of `videos/ward-psikiatri`. Cut every filler sound and filler word, TikTok pace;
punch-ins 1.0/1.06/1.02/1.07 at jump cuts; picture shifted down under a teal header band so cards +
one caption line fit above the head; 11 word-synced cream/teal cards (Plus Jakarta Sans), 5 full-screen
motion graphics, 4 AI B-roll stills; `loud` captions (Anton, one line above the hair) with one hero —
"HALUSINASI" slamming in teal BEHIND the head at "Itu adalah halusinasi" (0:14.8); voice chain +
soft ambient bed ducked under the voice; −14 LUFS / −1 dBTP.

**Intake decisions**
- First upload had burned-in CapCut captions (≈76–80% height) and a baked-in music bed (tonal lines
  at 345/390/780/1546 Hz through speech and pauses; quietest 1s window −22 dB). User re-exported clean.
- Clean export is 720p; user chose to upscale (lanczos + light unsharp → `edit/source_1080_dc.mov`)
  rather than wait for a 1080p re-export. Timing identical to the first upload (0 ms offset).
- Source audio clipped: ~4% of samples at full scale (CapCut export gain). `adeclip` at the source,
  −3.5 dB headroom, PCM in the working copy; the cut is rendered from that.
- No ElevenLabs key → faster-whisper medium (prompted, keeps fillers) + large-v3 (unprompted, wording),
  then MMS forced alignment of the corrected text over the whole clip with a `*` slot between every
  word pair (`align.py`), so hesitations land in `*` spans with exact times.

**Cut** (`build_edl.py`; 2:12 → 1:49.3 + 1 s end hold; 53 ranges)
- 11 filler words dropped (user-approved list): okay (0:22.4); sebenarnya ×5 (0:39.2, 0:40.3, 0:50.3,
  1:08.4, 1:32.6); macam (1:04.4); itu ×2 (1:21.4, 1:53.4); jadi ×2 (1:34.0, 2:00.3).
  Kept for meaning: "Itu adalah halusinasi", "Itu normal…". Kept (user): "without any external stimulation".
- Every `*` gap ≥ 0.2 s cut (55 found: 16 voiced "eee/mmm"/drawn vowels, the rest breaths/pauses),
  unless the cut would save < 0.15 s (a jump for nothing).
- Edges: word spans first trimmed of silence the aligner swallowed; out-points snap to silence within
  0.12 s, else the deepest dip at the word edge (so a glued-on "eee" isn't kept); tight pairs cut at
  the dip between the words. Hand-checked: "paranoid" out at 113.34 (aligner ran it into the dropped
  "itu"), "seorang" out at 81.49 (large-v3 heard the sliver of "itu" as "yang").
- Verified: large-v3 on the cut hears none of the removed words; sync 0.1 ms at every range and stage;
  envelope plots of all 104 edges (`edit/verify/edges_*.png`).

**Graphics** (`graphics/build_graphics.py`, `inserts.py`)
- Face measured: hair y≈280, chin y≈1190 on the source → picture shifted 320 px (hair ≈ y600, chin
  ≈ y1510, clear of TikTok's bottom UI); header band deep teal, video top edge feathered 120 px.
- Cards y150–450; panel grows as each element lands (heights measured in Chromium, `measure_pages.cjs`).
  Chips: Pernah alami?, Soalan, Definisi, Mitos (+ TIDAK BENAR stamp), Contoh #1 / #3, Realiti,
  Otak overload, Ingat, Kesimpulan, Follow. ("Contoh #n" instead of "Soalan #n": the talk is examples.)
- Full-screen MGs: 5 senses; myth-vs-reality split; before-sleep / after-waking split (AI stills,
  #1 hypnagogic / #2 hypnopompic); causes with icons; warning ladder → "Perlukan rawatan".
- B-roll (Canva AI stills, design DAHWpHUFMB8, exported 1080×1920): hallway shadow, dark bedroom,
  3:00 desk (+ "5 hari × 2–3 jam tidur"), doctor's hands (+ "Berterusan? Jumpa doktor"); morning
  still used inside MG 3. No faces; calm, not sensational. Stills (no AI-video key here), Ken Burns,
  "Ilustrasi AI" tag. Voice runs under every insert.

**Captions** (`captions/author_captions.py`)
- `loud`, Anton 0.046h, one line in y≈453–580. Hand-pinned breaks where he talks fast (no line
  < 0.51 s). Wording: "di ruang komen" (scored over "diorang"), "take care", "persepsi deria".
- Hero "HALUSINASI" (teal #0E5E6F) behind the head, occlusion ≈21%. Matte only 14.2–15.6 s
  (42 frames, 36 s) instead of all 3311 frames; the rest of `frames_fg/` is one hard-linked blank.
- Gates: inject-fonts, check-timing --strict (308 words OK), check-occlusion --strict (PASS).

**Audio** (`tools/mix_music.py --voice-fx enhance`, new): high-pass 80 Hz, −2.5 dB
at 250 Hz, +3 dB presence at 3.2 kHz, air shelf, de-esser, 3:1 compressor +5 dB makeup; original
D-major ambient bed (`tools/ambient_bed.py`) at −26 LUFS undocked, sidechain-ducked; music sits
19.6 dB under the voice. `afftdn` (de-noise) was dropped from the chain: it delays audio by a constant
25 ms (measured per filter) — the first mix read 25 ms lag at every range. The clean export's floor is
−70 dB anyway.

**QA** (`qa.sh`, on `final.mp4` and `final_tiktok.mp4`): 1080×1920 @ 30, 3311 frames, 1:50.4;
sync worst 0.9 ms; −14.0 LUFS, true peak −1.0 dBTP, LRA 1.1 LU; no black frames (≥0.1 s),
no frozen frames (≥1 s); contact sheet `edit/verify/final_sheet.png`. `final_tiktok.mp4` = two-pass
x264 1850 kb/s, audio copied → 28.4 MB.

**Outstanding**
- Switch on TikTok's "AI-generated content" label (AI B-roll stills).
- If a 1080p/4K clean export turns up, swap `edit/source_1080_dc.mov` and re-run from `render_edl.py`
  (timings unchanged).
- Swap the bed for a TikTok-library track in-app if preferred.
