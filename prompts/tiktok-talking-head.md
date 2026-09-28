# Prompt: edit a talking-head video in the "Ward Psikiatri" style

Copy everything in the box below into a new Claude Code session on this repo. Fill in the three
`[...]` lines first; delete any line you don't want.

---

```
Edit my new video in the same style as videos/ward-psikiatri (read its edit/project.md,
edit/build_edl.py, graphics/build_graphics.py, graphics/inserts.py, captions/author_captions.py
and assemble.sh first, and reuse them as templates).

Video: [Google Drive link, or the file name in my CapCut folder]
Project name: [short-name, e.g. kemurungan-remaja]
Topic / audience: [one line, e.g. "Malay explainer on teen depression for parents"]

Follow CLAUDE.md for the pipeline. What I want:

1. CUT — aggressive, TikTok pace
   - Remove every filler sound (aa, eee, mmm, drawn-out vowels), including short hesitations
     inside pauses under 0.45s.
   - Remove filler WORDS too: "dia", "dah", "ke apa", "kat sini (adalah)", "sebenarnya",
     "itu", "lah", "macam", "okay", repeated questions, false starts, retakes (keep the
     cleanest take).
   - Any plug / promo in the middle moves to the end, before the CTA.
   - Punch-in zooms on jump cuts (alternate 1.0 / 1.02 / 1.06 / 1.07).
   - Before cutting, list every filler you found, with timestamps, and wait for my OK.

2. MOTION GRAPHICS
   - Cards in the headroom above my head: cream panel, teal accent (#0E5E6F),
     Plus Jakarta Sans. Each item lands on the word I say. Chips for "Soalan #1/#2/#3",
     "Mitos", "Realiti"; a red "TIDAK BENAR" stamp for myths.
   - 3–5 FULL-SCREEN motion graphics at the key lists / comparisons (deep teal background,
     cream + mint type, icons, word-synced). E.g. myth vs reality split, a list with icons,
     a step ladder, a timeline or path.

3. B-ROLL
   - 4–6 AI-generated stills from Canva (9:16), animated with a slow Ken Burns move, 2–4 s
     each, with an "Ilustrasi AI" tag.
   - No patient faces; nothing sensational for sensitive topics.
   - My voice keeps playing under every insert.

4. CAPTIONS
   - `loud` style (Anton, uppercase, white with a dark stroke).
   - One line at a time, just above my head, clear of the TikTok UI (bottom 20%, right 15%).
   - One "hero" word slammed in big BEHIND my head at the hook's answer (teal).

5. AUDIO
   - Soft ambient music bed, ducked under my voice.
   - Master to -14 LUFS, true peak <= -1 dBTP.

6. DELIVERY
   - 1080x1920 @ 30fps.
   - Check sync, loudness, black/frozen frames and snapshots yourself before showing me.
   - Send me a 1080p file under 30 MB that I can download.
   - Commit and push the scripts; note decisions in edit/project.md.
   - Remind me to switch on TikTok's AI-generated content label.

Clinic / CTA details for the end card: [clinic name + how to book, or "none"]
```

---

## Why each rule is there (lessons from the first video)

- **Filler words, not just sounds.** The first pass of the Ward Psikiatri edit only cut
  "aa/eee" and long pauses. The viewer still heard "dia", "dah", "ke apa", "sebenarnya", plus
  "mmm" hidden in short gaps. They have to be listed and cut word by word.
- **Confirm before cutting.** Removing a word can change the meaning, so you approve the list first.
- **The plug moves to the end.** An ad in the first 20 seconds costs TikTok retention.
- **Captions above the head.** The bottom ~20% of the screen is TikTok's caption and button area.
- **"Ilustrasi AI" tag + TikTok AI label.** AI images in health content must be disclosed.
- **Download under 30 MB.** The chat can only send files up to 30 MB. A two-pass 1080p encode
  looks the same after TikTok re-compresses it.
