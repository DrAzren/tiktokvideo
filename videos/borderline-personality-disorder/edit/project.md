# Borderline Personality Disorder — edit notes

Source: `raw/bpd.mp4` (Google Drive "Borderline Personality Disorder.mp4", 2:04.5, 1080×1920 @ 30 CFR,
AAC stereo, Malay). Audience: female adolescents / young adults. Template: `videos/ward-psikiatri`.
Deliverable: `final.mp4`, 1080×1920 @ 30, ~1:24.

## Session 1 — 2026-10-03

**Strategy (user-approved):** cut every filler sound and filler word from the approved list,
the false starts and the broken first take of the reassurance line (1:26.8–1:40.4); the clinic
plug is already at the end before the CTA (nothing moved); punch-ins 1.0/1.06/1.02/1.07 on jump
cuts; compact teal/cream "Tanda #1–#6" cards in the headroom; 5 full-screen motion graphics and
6 AI stills; `loud` captions one line above the hair with **BPD** (user's pick) slammed in teal
behind the head at 0:09; ambient bed louder than ward-psikiatri, voice enhanced; −14 LUFS.

**Source facts that shaped decisions**
- Audio arrives limited to −7 LUFS (peaks +0.9 dBFS, LRA 3.3), with continuous sub-100 Hz rumble
  from the hand-held clip mic and a steady 1761 Hz whine (+30 dB over its neighbourhood).
- Headroom is tight: hair top at y ≈ 420–500 of 1920 (ward-psikiatri had ~560).

**Decisions**
- Transcription: no ElevenLabs key → faster-whisper `medium` (ms) + unprompted large-v3; word
  edges from torchaudio MMS forced alignment (`align.py`; loanwords spelled phonetically: mudi,
  eksplen, bipidi, wasap, perfek, hepi, syoping). large-v3 settled: "Betul ke?", "kesihatan
  mental" (not keselamatan), "Apa-apa soalan", "klinik saya di **Nilai**" (the town).
- Edge envelope measured on a 150 Hz–6 kHz band (`envelope.py`); QUIET_DB −27 dB (the rumble
  floor is ~−30 dB, so the template's −40 would never trigger).
- Hesitations found acoustically (`voicing.py` + `scan_fillers.py`: periodic, loud frames outside
  every aligned word): drawn-out "sekadaaar", "jeee", "contohnyaaa", "hepiii", "rasaaa",
  "difahamiii", "berbahayaaa", the "eee + i-" at 1:44.6, the half-said "yang…" at 0:53.3
  (the aligner had stretched "marah" over it → `WORD_FIX` end 53.2, applied in map_words too).
  The '*' insertion search in align.py never fired (star token scores too low) — acoustics did it.
- "jadi" after "Betul ke?" sits at 7.9–8.35 (not 11.4 as Whisper said; that was a breath).
- Most dropped "dia" are 60–100 ms and touch both neighbours: the cut windows are clamped to
  the dropped word's own edges (the template's ±70 ms windows squeezed together and removed
  almost nothing).
- Sync bug fixed in `tools/render_edl.py`: this source's 1 µs timebase puts frame timestamps
  exactly on the -ss/-t boundary, so some ranges gained/lost a frame (+66.7 ms by the end).
  Now seeks 0.5 ms early and trims each range to an exact frame count → worst 0.6 ms.
- Zoom focus [0.45, 0.27] (near the hairline): punch-ins grow the face downward instead of
  pushing the hair into the caption line.
- Cards: one compact page each (chip + headline), panel y 118–~300; multi-step content went
  into the full-screen inserts instead.
- Motion graphics: chat chain (lambat balas → diabaikan → panik), PERFECT ↔ JAHAT split, day
  timeline (pagi happy → tengah hari kosong → malam marah), impulsivity list (top half AI
  still), 6-sign recap → "BUKAN BERMAKNA ANDA GILA".
- Self-harm is shown only as text with a gentle care icon, plus "Ada fikiran mencederakan
  diri? Dapatkan bantuan segera — Talian HEAL 15555" (KKM's mental-health line — user to confirm).
- B-roll (Canva design DAHW6VWdB_E, exported 1080×1920): window (back view), two people walking
  apart, crowd, clenched hands, shopping bags, empty consultation room. No faces.
  User asked mid-session for the crowd still to be more Malaysian → regenerated: young woman in
  a tudung and baju kurung, back view, in a KL station crowd.
- Voice chain (`audio/voice_af.txt`, via `mix_music.py --voice-af`): 100 Hz 4th-order high-pass
  (−10.7 dB rumble), 1761 Hz notch, −2 dB @250 Hz, +3 dB @3.2 kHz, +2 dB air shelf, 2.5:1
  compression. afftdn was dropped: it delays the voice by 25 ms (sync tolerance).

- Captions: `loud` (Anton, uppercase, white + dark stroke), one line at y ~334–420 (plane x 4–85%,
  clear of the right-hand buttons and the bottom 20%). Line breaks use large-v3's punctuation AND
  its segment ends (it stops punctuating after ~0:31). Display spellings mapped back in
  `captions/build_transcript.py` (BPD, WhatsApp, moody, di Nilai, take care, reduplications).
- Apex: the compiler's width-fit raise made the 3-letter "BPD" 0.28h with the lockup running down
  the face → `patch_apex.py` sets 0.2h, letters at y ~250–540, lockup plane at 6% (no cards then).
  Occlusion gate: avg 23% / peak 26% (WARN, intended). Matte only for 7.9–10.95 s (`matte_hero.sh`,
  91 frames instead of 2518); preview needed a sparse `frames_bg/` (real frames only at samples).
- Music: −17 LUFS undocked (ward used −20; user asked for more music) → sits −13.2 dB under the
  voice. Master target TP −1.5 so the AAC encode lands at −1.4 dBTP (TP −1 measured −0.9).
- Sync check after the mix: `check_sync.py`'s 0.27 s snippet on the one-word range "walaupun"
  locked onto a false peak with the louder bed (−344 ms reported); real lag vs the pre-mix file
  is +4.3 ms median / 14.2 ms worst. `assemble.sh` now checks the EDL on the pre-mix file and the
  mix stage in 1 s windows.

**Results** — `final.mp4` (master, 161 MB) and `final_tiktok_1080p.mp4` (29.8 MB, sent to the user):
1080×1920 @ 30, 83.93 s (2518 frames), −14.0 / −14.1 LUFS, −1.4 dBTP, sync 0.6 ms pre-mix,
no black or frozen stretches; large-v3 on the cut hears none of the removed words.

**Outstanding**
- User review. Switch on TikTok's "AI-generated content" label (6 Canva AI stills).
- Confirm the helpline shown with "self-harm" (Talian HEAL 15555) is the one the clinic wants.
- The window still (woman by a window) is the original, non-Malaysian-looking one; only the crowd
  still was regenerated on request.
