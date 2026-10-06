# Tiga Tanda Kemurungan Yang Anda Tak Perasan — edit notes

Source: `raw/Tiga Tanda Kemurungan.mp4` (Drive, 2:40, 1080×1920 @ 30, single take, Malay).
Topic: depression / anxiety — six easily-missed signs of depression. Deliverables: `final.mp4`
(master) and `final_tiktok.mp4` (1080p two-pass, 29.5 MB), 1080×1920 @ 30, 1:43.8.
Built from the `videos/ward-psikiatri` templates (build_edl, build_graphics, inserts, author_captions,
assemble).

## Session 1 — 2026-10-06

**Strategy (user-approved):** cut every filler sound and filler word (list approved before cutting),
false starts and retakes; move the mid-video clinic plug ("Iklan. Kalau anda rasa…", 0:48) to the end
before the CTA and keep the full original CTA (user picked option b); punch-ins cycling
1.0/1.06/1.02/1.07 on the face; 13 cream/teal headroom cards (chips "Tanda #1–#6", Mitos/Realiti,
"TIDAK BENAR" stamps); 4 full-screen motion graphics; 5 Canva AI B-roll stills + 1 still inside a
split-screen graphic; `loud` captions one line above the head with "KEMURUNGAN" slammed in teal
behind the head at the hook's answer; original ambient bed ducked under the voice; −14 LUFS.

**Content notes**
- The hook says "if THREE of these signs are in you…" but six signs are listed; sign #3 (reaching for
  the phone first thing) is called the most common → hook card "6 tanda kemurungan / Ada 3 pada
  anda?", teaser chip "Tanda #3 — Paling common".
- User confirmed: "klinik saya di Nilai" (the town), spelling "Dr Azren". No clinic/booking details
  supplied, so the end card says what is spoken: consultation with Dr Azren, link in bio, comment.

**Decisions**
- Transcription: no ElevenLabs key → faster-whisper `medium` (ms) + an unprompted large-v3 pass for
  wording; torchaudio MMS forced alignment per speech island for word edges (`align.py`).
  Unclear stretches settled by large-v3 on the snippet: 0:49.4 is a false start "Kalau anda rasa"
  (retaken at 0:52.2); the outro is "Apa persoalan boleh tanya di dalam komen".
- Hidden hesitations found with a voicing scan (`gap_scan.py`: pitch periodicity, not loudness, so
  breaths aren't mistaken for "aa"): 0:14.3, 0:23.6 ("ha"), 0:29.9, 0:53.2, 1:01.9, 1:14.6, 1:29.7,
  1:39.4, 1:51.0, 1:59.4, 2:04.0, 2:06.4, 2:09.3.
- Kept although on the generic list: "ni" (not a filler in "sekarang ni", "mental ni"), the second
  "macam" in "rasa macam nak menangis" (meaning: "feel like crying"); sub-0.1s sound tokens were
  left in place because cutting them only adds a jump.
- After the first render, large-v3 on the cut still heard three remnants; re-cut by hand from
  envelope + spectrogram plots: "nombor tiga **tu yang** paling" (one run, cut at the dip before
  "paling"), "emosi **tu** naik" (in-point on the nasal onset of "naik", 104.12), "fizikal **dia**
  letih" ("dia" starts under the tail of "fizikal": out 129.233, in 129.68, each auditioned with
  large-v3 on splices).
- `timeline_view` on the cut caught two breath pauses left in (0.7s "menangis | emosi" — a micro range
  had been merged back across the pause; 0.6s "Doktor Azren | boleh klik") → both removed.
- `tools/render_edl.py` fix: the source's frame times sit up to 10 µs off the 1/30 grid, so a range
  edge sometimes let one extra video frame in and concat padded the audio — 1 frame of drift per hit,
  133 ms by the end. Every range is now trimmed to an exact frame count/duration. Sync ≤ 0.1 ms at
  every stage.
- Layout: the speaker's head sits higher than in the ward video (hair top measured per frame:
  y ~460–530, ~405–420 in the hook and the last seconds; `hair_top.json`). Cards y 125–360 (heights
  measured in Chromium, asserted), captions one line at y ~370–460 inside x 6–82% (clear of TikTok's
  right-hand buttons); a raised caption line (y ~300–390) for the hook and the closing CTA.
- Graphics and B-roll are anchored to phrases on the cut (`inserts.T`), not to seconds.
  Full-screen MGs: (1) "Bukan sebab… nak diet / malas — TIDAK BENAR" vs "Tapi sebab… tak ada selera /
  badan rasa berat", (2) anhedonia list (game, drama, makan luar, lepak → "SEMUA RASA KOSONG"),
  (3) mood-swing day path pagi → tengah hari → malam, (4) recap of all six signs + "JANGAN BIARKAN
  MELARAT". B-roll (Canva design DAHXM1UREWM, exported 1080×1920): bed, phone at dawn, foggy desk,
  rainy window, empty consult room; breakfast still inside MG 1. No faces, nothing sensational.
- Captions: hand-broken hook lines; elsewhere lines never cross a sentence start and a DP picks the
  breaks (no orphans, phrases kept together, ≤ 21 chars). Apex patched (`patch_apex.py`): hero raised
  so the hair hides only its lower third (occlusion 18%), tail line takes the kicker's slot, and lines
  hand off cleanly between caption planes. Matte only for the hero window (5.9–9.5s).
- Bug caught in QA: `matte_window.sh` filled frames_fg with hard links to one clear PNG and then
  `cp -f`'d the real mattes through them — overwriting the shared inode, i.e. pasting a stale subject
  over every frame (freezedetect flagged talking-head "freezes"). Fixed with `--remove-destination`,
  plus guards: the clear frame must stay transparent, and assembly asserts the composite equals the
  caption layer outside the matte window.
- Music: HeyGen catalog needs sign-in → original bed from `tools/ambient_bed.py` (key F, 60 bpm),
  mixed at −20 LUFS undocked, ~21 dB under the voice during speech.

**Final QA** (`final_tiktok.mp4`)
- 1080×1920 @ 30, 3114 frames, 1:43.8 (2:40 → 1:42.6 of speech + 1.2s end hold); 29.5 MB.
- A/V sync ≤ 0.1 ms at every range (`tools/check_sync.py`); −14.0 LUFS integrated, true peak
  −5.3 dBTP, LRA 2.4 LU; music −20.6 dB under the voice during speech, +3.3 dB in pauses.
- No black frames; the only frozen spans ≥ 0.5s are the static end of the recap graphic and the end
  hold; no pause ≥ 0.5s except the end hold.
- Caption gates: check-timing --strict OK (306 words), check-occlusion --strict OK (hero 18%).
- Snapshots: every card page and insert at its fully built moment, plus a 24-frame sheet of the
  final (`edit/verify/`, local).
- Rebuild everything after an EDL change with `./rebuild.sh` (FROM=graphics|captions to resume).

**Outstanding**
- Switch on TikTok's "AI-generated content" label when posting (the B-roll stills are AI; each is
  tagged "Ilustrasi AI" on screen).
- Optional: swap the bed for a TikTok-library track in the app.
- Source audio is hot (−7.3 LUFS integrated, true peak +0.35 dBTP before normalisation) — any
  clipping in the original export is not recoverable.
