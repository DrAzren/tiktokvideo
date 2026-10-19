# Sejarah Penyakit Mental — Dari Zaman Purba ke Era Moden (Borak Jiwa, Episod 1)

Faceless 120 s historical documentary, Bahasa Melayu, 16:9, 24 fps. 4K master (3840×2160) plus a 1080p copy.

## Session 1 — 2026-10-19

**Brief:** a 120 s faceless cinematic documentary using the narration supplied (Scenes 1–6), with Higgsfield for the
AI scenes, motion graphics, music/SFX and Malay subtitles. The narration text must not be rewritten.

**Narration:** ElevenLabs v4 via Higgsfield, preset voice "Xavier" (`43173c95-…`, chosen by the user), one take
per scene (`audio/vo_s1..6.mp3`, 109.8 s of speech). Whisper large-v3 transcribes every take word-for-word (numbers
spoken as words). Whisper's language-ID leans *Indonesian* on s1/s3/s4 (ms ≥ 0.87 on s2, s5, s6). Two more
takes of s1/s3/s4 at different stability scored the same, so the originals stay. **A native listener should check the
accent**; one scene can be re-voiced for ~0.3 credit. Word times come from torchaudio MMS_FA forced
alignment of the exact script (`doc/align_vo.py` → `doc/vo_words.json`). Pauses inside takes are 0.45–0.6 s, all at
sentence ends; there are no fillers.

**Visuals:**
- 24 Nano Banana Pro start frames (2K). Three were redone: a profile face at the window, legible fake Greek text, and
  a visible face in the counselling room.
- 22 Kling 3.0 Pro image-to-video clips (1080p, 24 fps, 5 s, silent, 8.75 credits each). Kling recommends the preset
  "IN THE DARK" instead of submitting a job; pass `declined_preset_id` to get the job submitted.
- Counselling-room clip rejected: the man turns his head into profile. Replaced by the still with a 2.5D push-in.
- Final window shot slowed 1.3× with frame blending (`doc/public/broll/23_window_sun.mp4`) to hold the ending.
- Archival portraits (real, not AI): Philippe Pinel and William Tuke, etchings by C. Callet, Wellcome Collection,
  CC BY 4.0. They are credited on screen.
- Light per-era grade in `doc/prep_broll.sh`: warm for ancient eras, desaturated cold blue for institutions,
  sepia→teal for science, teal/warm for modern scenes.

**Composition:** `doc/build_doc.py` → `doc/public/index.html`, with 29 shots (22 AI, 1 still, 7 motion graphics):
- title card emerging from darkness, with an animated timeline
- a persistent era timeline (ZAMAN PURBA → ± 400 SM → AKHIR ABAD KE-18 → 1952 → HARI INI)
- an ink-bleed reveal at chapter seams and a paper-tear wipe into the parchment and archival cards
- cultures card (Yunani, Mesir Purba, Mesopotamia, India, China)
- four-humours card with a "TIDAK LAGI DITERIMA" stamp
- Hippocrates lower third; portraits card; "1952 / CHLORPROMAZINE"
- modern-era timeline, the treatment list, STIGMA, a recap timeline and the end screen

On-screen honesty tags read "Dramatisasi · visual dijana AI" and "Rekaan semula …". Subtitles are burned in
(Plus Jakarta Sans, cream, with gold/teal keywords, 104 px above the bottom). An editable SRT is in
`sejarah-penyakit-mental_ms.srt`.

**Audio:** original synthesized score and SFX (`doc/score.py`): impact, drone, rain, clock ticks, rising strings,
paper, wind, frame drum, ink, harp plucks, whooshes, footsteps, glass, electronic pulses and warm piano, with a
C-major resolution. Higgsfield's music/SFX models are reserved for its game pipeline, so they were not used.
The music is sidechain-ducked 9 dB under the voice. Master: two-pass loudnorm, −14 LUFS, TP ≤ −1.2 dBFS.

**Facts checked:**
- Hippocrates (c. 460–370 SM, Kos).
- Pinel (1745–1826, Bicêtre/Salpêtrière, Paris).
- William Tuke (1732–1822), who founded The Retreat, York, in 1796.
- Chlorpromazine was first used in psychiatry in 1952 in Paris (Hamon et al.; Delay & Deniker).
- The four humours: darah, kahak, hempedu kuning, hempedu hitam.

The end screen adds support lines: Talian HEAL 15555 and Befrienders KL 03-7627 2929. Verify both before publishing.

**Credits used:** ~2 (voice tests and takes) + ~54 (27 stills) + 192.5 (22 Kling clips) ≈ 269 of 786 (balance 517 after this session).

**Outstanding:**
- Native-speaker check of the narrator's accent; re-voice individual scenes if needed.
- Turn on YouTube's "altered or synthetic content" disclosure.
- Verify the helplines.
- Optionally swap in a licensed orchestral track; the stems are in `audio/`.
