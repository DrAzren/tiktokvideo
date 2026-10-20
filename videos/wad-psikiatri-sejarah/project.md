# Sejarah Wad Psikiatri di Malaysia — Adakah Ia Menakutkan? (Borak Jiwa)

16:9, 24 fps, ~6:26. The narration is the user's own voice (Google Drive: "Sejarah Wad Psikiatri Di Malaysia.MP3").
Same concept as Episode 1: cinematic AI visuals + HyperFrames motion graphics + an original score and SFX.

## Session 1 — 2026-10-20

**Ask:** build a YouTube video from the user's voice in the same style as Episode 1, using Higgsfield for at most
75 credits, with sound effects.

**Voice edit** (`edit/`):
- Whisper large-v3 transcribed the recording. The first 30 s hallucinated "Terima kasih kerana menonton", so that
  stretch was re-transcribed alone.
- `align.py` re-times every word with MMS_FA, per speech island.
- `build_voice.py` cuts the recording from 7:53 to 6:19 of speech. It drops these retakes:
  - "Bayangkan." (the first one) and "Ha"
  - "dalam wad psikiatri", restated as "dalam hospital psikiatri"
  - "Dan satu perkara yang jelas", restated as "…yang penting"
  - "And then,"
  - the repeated "Malaysia."
  - the false start "pesakit yang sebelum ini"
  - the repeated "terus"
  - the false start "kalau tuan-tuan"
  - the "Rawatan, rawatan" stutter
- Pauses are shrunk to 0.22 s (0.28 after a comma, 0.42 at sentence end). Each join keeps the real room tone,
  with 20 ms equal-power fades.
- Verified: Whisper large-v3 on the cut hears none of the dropped words.
- Subtitle display fixes: Whisper's "sekretari", "buat" and "ward secretary" are corrected to "psikiatri" / "wad".
  Further corrections: "clopramazine" → chlorpromazine, "mode stabilizer" → mood stabilizer, "seringan" → saringan,
  "Azri / klinik saya dinilai" → "Dr. Azren di Klinik Nissa" (spelling confirmed by the user).
- Voice polished with `tools/enhance_speech.py`.

**Visuals:**
- 33 Higgsfield Nano Banana stills (1 credit each): Malaya 1911, Penang 1880s, Taiping 1890s, a colonial asylum,
  Tanjung Rambutan 1911 with the Kinta limestone hills, colonial wards, the 1970s hospital, Penang GH 1958, modern
  Malaysian wards, the multidisciplinary team, OT, the clinic room, and a horror-film set for the myth beat.
  Upscaled to 2304×1296 and animated with Ken Burns moves.
- 4 Kling 3.0 std clips (7.5 each): kampung in the rain, Tanjung Rambutan 1911, the modern ward, sunrise over Kinta.
- Episode 1 clips reused: room, corridor, asylum exterior, Retreat garden, brain morph, lab, glassware, neurons and
  family, some slowed with frame blending.
- Maps drawn from Natural Earth 10m (`doc/make_maps.py`).
- **Credits: 33 + 30 = 63 of the 75 allowed.**

**Motion graphics** (`doc/build_wad.py`, 64 shots):
- era bar (ABAD KE-19 → HARI INI)
- title
- Tanah Melayu map
- conditions card
- "FEDERAL LUNATIC ASYLUM" with the term struck through and explained
- 3 + 1 wards
- three names (1911 / 1928 / 1970-an)
- today's medicines vs 1911
- "Tidak semuanya sempurna"
- the growth of treatment options
- risks vs options
- specialist vs general hospital
- general-hospital departments
- psychiatric services spreading across Malaysia (illustrative dots)
- myth (horror film) vs reality
- reasons for admission and length of stay
- book card, using an *illustrated* cover
- end card with support lines

Subtitles are burned in, and there is an SRT: `sejarah-wad-psikiatri_ms.srt`.

**Audio:** `doc/score_wad.py`, with `doc/synth.py` shared with Episode 1. The voice-to-bed gap is 16.7 dB in speech.
Master: −14 LUFS, TP −1.2.

**Facts checked:**
- Federal Lunatic Asylum, Tanjung Rambutan: opened Nov 1911, with 3 male wards + 1 female ward at first.
- Renamed Hospital Bahagia Ulu Kinta in the early 1970s.
- First general-hospital psychiatric unit: Penang, 1958.
- **The "Central Mental Hospital" rename is dated 1922 by one source and 1928 by another.** The narration says 1928,
  and so do the on-screen labels.

**Outstanding:**
- Real book cover (the cover is illustrated, not the actual one).
- Verify the helplines (HEAL 15555, Befrienders KL 03-7627 2929).
- Turn on YouTube's AI-content disclosure.
