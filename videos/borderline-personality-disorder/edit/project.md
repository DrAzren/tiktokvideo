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

**Outstanding**
- (filled in at the end of the session)
