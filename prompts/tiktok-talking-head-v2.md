# Prompt: edit a talking-head video in the "Ubat Psikiatri Olanzapine" style (v2)

Copy everything in the box below into a new Claude Code session on this repo. Fill in the `[...]`
lines first; delete any line you don't want. v1 (`tiktok-talking-head.md`, Ward Psikiatri style) still
works; v2 adds everything learned on the Olanzapine video (varied SFX, compact layout for a high head,
unbranded medicine images, hook check).

---

```
Edit my new video in the same style as videos/ubat-psikiatri-olanzapine (read its edit/project.md,
edit/build_edl.py, edit/align.py, edit/gap_scan.py, graphics/build_graphics.py, graphics/inserts.py,
captions/author_captions.py, captions/patch_apex.py, audio/make_sfx.py and assemble.sh first, and
reuse them as templates).

Video: [Google Drive file name or link]
Project name: [short-name, e.g. ubat-psikiatri-sertraline]
Topic / audience: [one line, e.g. "Malay explainer on sertraline for patients and families"]

Follow CLAUDE.md for the pipeline. What I want:

1. CUT — aggressive, TikTok pace
   - Remove every filler sound (aa, eee, mmm, drawn-out vowels), including short hesitations
     inside pauses under 0.45s (scan the gaps for voicing and check them on spectrograms).
   - Remove filler WORDS too: "dia", "dah", "ke apa", "kat sini (adalah)", "sebenarnya",
     "itu", "lah", "macam", "okay", "ada" (kalau anda ada ambil), "jadi apa yang saya bagi tahu",
     repeated questions, false starts, retakes (keep the cleanest take).
   - Any plug / promo in the middle moves to the end, before the CTA. If the plug repeats
     what the CTA says ("tekan di bio…"), keep only one.
   - If I start a sentence and never finish it (e.g. a hook I forgot to complete), tell me and
     let me choose: drop it, or show the missing word on screen.
   - Punch-in zooms on EVERY jump cut (cycle 1.0 / 1.06 / 1.02 / 1.07), no two neighbouring
     ranges at the same zoom.
   - Before cutting, list every filler you found, with timestamps, and wait for my OK.

2. MOTION GRAPHICS
   - Measure where my head sits first. Cards go in the headroom above my head: cream panel,
     teal accent (#0E5E6F), Plus Jakarta Sans, sized per page so they never touch the caption
     line. Each item lands on the word I say. Chips like "Kebaikan", "Keburukan",
     "Kesan sampingan #1/#2/#3", "Mitos", "Realiti"; a red stamp for the key warning
     ("PALING COMMON", "TIDAK BENAR").
   - 3–5 FULL-SCREEN motion graphics at the key lists / comparisons (deep teal background,
     cream + mint type, icons, word-synced). E.g. a pros vs cons split, a list with icons,
     a row of risk gauges, a "the 2 rules" closer.
   - A card that ends where a full-screen insert starts must exit behind the insert.

3. B-ROLL
   - 4–6 AI-generated stills from Canva (9:16), animated with a slow Ken Burns move, 2–4 s
     each, with an "Ilustrasi AI" tag. Export them at full 1080x1920 through a Canva design;
     never use the auto-generated cover page Canva adds to that design.
   - Medicine images must be generic and unbranded (no real brand, box, logo or label, no
     AI lettering); put the drug name on as our own designed text instead.
   - No patient faces; nothing sensational for sensitive topics.
   - My voice keeps playing under every insert.

4. CAPTIONS
   - `loud` style (Anton, uppercase, white with a dark stroke).
   - One line at a time, just above my head, clear of the TikTok UI (bottom 20%, right 15%).
     No orphan words alone on a line; no line shorter than 0.5 s where it can be avoided.
   - One "hero" word slammed in big BEHIND my head at the hook (teal), readable — my head
     may only cover the bottom of the letters. Nothing else on screen during the hero.

5. AUDIO
   - Soft ambient music bed, ducked under my voice.
   - Prominent, VARIED sound effects (audio/make_sfx.py cue sheet): each full-screen graphic
     its own transition (riser / zip / deep whoosh / tape riser), photo inserts a shutter /
     polaroid / soft swell to suit the picture, card entries rotating paper / swipe / flick,
     list items as rising musical notes with a different instrument per card, one-off cues for
     checks, stamps, quotes and the CTA, an impact on the hero word. Never the same sound
     back-to-back; no stream of tings or whooshes. Send me the cue list.
   - Master to -14 LUFS, true peak <= -1 dBTP.

6. DELIVERY
   - 1080x1920 @ 30fps.
   - Check sync, loudness, black/frozen frames and snapshots yourself before showing me.
   - Send me a 1080p file under 30 MB that I can download.
   - Commit and push the scripts; note decisions in edit/project.md.
   - Remind me to switch on TikTok's AI-generated content label.

Clinic / CTA details for the end card: [e.g. "Klinik saya di Nilai — tekan link di bio atau DM untuk appointment", or "none"]
```

---

## Why each rule is there (lessons from Ward Psikiatri + Olanzapine)

- **Filler words, not just sounds.** Whisper drops "eee/mmm"; they hide in gaps under 0.45 s. The
  Olanzapine edit found 11 of them with `gap_scan.py` (voicing in the gaps) and confirmed each on a
  spectrogram. "ada", "lah", "itu" and stock phrases like "jadi apa yang saya bagi tahu" are cut word by word.
- **Confirm before cutting.** Removing a word can change the meaning, so you approve the list first.
- **Unfinished sentences.** The Olanzapine hook "Ada patient panggil…" was never finished (5.5 s of
  silence followed). It was caught by checking the gaps and the lip movement, then you chose to drop it.
- **The plug moves to the end, once.** An ad in the first 20 seconds costs retention; saying "tekan di
  bio" twice in a row sounds repetitive.
- **Punch-ins on every cut.** With a 0.8 s minimum, six jump cuts kept the same zoom and showed; 0.45 s fixed it.
- **Measure the head first.** In the car your hair top sat at y≈460 (vs ≈560 in the ward). Cards had to
  shrink to one line per page, and their height is now measured in a real browser so they never touch the captions.
- **Hero word readable.** The default lockup hid the middle letters and put a caption across the eyes;
  `patch_apex.py` raises it so the head covers only the bottom of the letters.
- **Unbranded medicine images.** An AI copy of a real brand's packaging is a trademark problem and can be
  mistaken for that exact product (with wrong details like the dose). Generic tablets + our own text is safe.
  If you want a specific brand on screen, use your own photo of it.
- **Varied SFX.** The first Olanzapine mix had 38 tings and 17 whooshes and felt repetitive; the cue
  sheet gives 23 different sounds over ~48 cues, matched to what is on screen.
- **Captions above the head.** The bottom ~20% of the screen is TikTok's caption and button area.
- **"Ilustrasi AI" tag + TikTok AI label.** AI images in health content must be disclosed.
- **Download under 30 MB.** The chat can only send files up to 30 MB. A two-pass 1080p encode
  looks the same after TikTok re-compresses it.
