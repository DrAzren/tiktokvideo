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

**Deliverables:**
- `final_1080.mp4`: 1920×1080, 24 fps, 6:26.4, AAC 320k, 606 MB.
- `final_share_720p.mp4`: 73 MB.
- `sejarah-wad-psikiatri_ms.srt`.

**QA:**
- 9274 frames. The only black is 0–0.125 s, the fade-in.
- −14.0 LUFS, peak −1.1 dBFS.
- 27 frames sampled across every chapter, transition and card.
- The 1080p render takes 27 min here.

## Session 2 — 2026-10-20 (revisions)

**Asks:**
- Put the real book cover (supplied as an image) into the video as a 3D book.
- Remove the repeated phrases (e.g. at 3:24) and all filler words.
- Drop the helplines.
- Spend no Higgsfield credits.

**Voice** (`edit/realign.py` → `realign.json`, then `build_voice.py`):
- **Hidden retakes.** These were swallowed by over-long aligned words (519 "penting" 4.3 s, 672 "pada" 1.5 s).
  Found with large-v3 on the cut voice, then re-aligned with MMS_FA and cut:
  - "Dan penting untuk kita faham, amalan rawatan berbeza mengikut" was said twice. This was the 3:24 repeat.
  - "pada tahun, pada tahun 1958"
  - "filem, filem barat"
- **Filler sounds.** Located on a 10 ms energy/voicing envelope and cut by hand (`MANUAL` in `realign.py`):
  - "Ha," after "gangguan pemikiran." and after "semakin berkembang."
  - "lah" after "rawatan perubatan"
  - "Ha," before "Kalau anda"
- **Lexical fillers dropped** (`FILLERS`): dah/dah macam, sentence-final lah/je/ni/sebenarnya, the doubled "seperti",
  "dia" in "nama (asal) dia", "suasana dia", "lunatik ni", "sejarah psikiatri ini".
- **Fillers kept:** "ni"/"tu" fused into the next word (mental ni masih, kemurungan ni, seseorang tu, filem barat tu,
  seram tu). A cut there clipped both words; large-v3 heard the remains and heard "filem-filem" as "bukannya".
- **Gaps from dropped words** are filled with real room tone (the quietest 0.5 s of the take), not digital silence.
- **Verified:** large-v3 (plain and filler-prompted) on the new cut hears no repeat, and none of the cut fillers. The
  filler-prompted model also reports "Ha" at spots that are word onsets ("pa" of pada, "me" of mereka); those were
  checked on the envelope and left alone.
- **Result:** 6:09 of speech, down from 6:19. Video 6:16.

**Visuals:**
- Book card: a CSS 3D book built from the real cover (`doc/public/img/book_cover.jpg`, from
  `stills/book_cover_src.jpg`). It has a yellow spine with the title, page block, contact shadow and a sheen sweep.
  The card text uses the real title "Dr, Saya Boleh Sembuh Ke?" and subtitle "Manual Survival Kesihatan Mental".
- End card: helpline line removed.

**Credits:** none spent this session.

**Session 2 deliverables / QA:**
- `final_1080.mp4`: 1920×1080, 24 fps, 6:16.4 (9033 frames), 585 MB. `final_share_720p.mp4`: 72 MB.
- −14.0 LUFS, peak −1.1 dBFS; the only black is 0–0.125 s, the fade-in.
- 14 frames sampled, including 3:23–3:25 (the old repeat), the book card and the end card.

## Session 3 — TikTok 9:16 (no Higgsfield credits)
- **Source:** `NOSUBS=1 build_wad.py` → `doc/render_nosub.mp4`. This is the 16:9 film with no burned subtitles. Afterwards
  `build_wad.py` was re-run so `index.html` holds the normal build again.
- **Layer:** `tiktok/make_ass.py` → `captions.ass`.
  - Header: BORAK JIWA + title.
  - Chapter chips at the YouTube chapter times.
  - Captions: two lines of at most 20 chars, the spoken word in yellow, gold/teal keywords as in the 16:9 version.
  - Captions centre on x=490, clear of TikTok's right-hand buttons. Nothing sits below y≈1330.
- **Compose:** `tiktok/compose.sh`.
  - Blurred backdrop of the same film, darkened (black@0.5) so cream text stays readable over parchment scenes.
  - The film as a 1080×608 band at y 470.
  - The ASS layer is drawn with the composition's fonts, converted from woff2 to ttf in `tiktok/fonts/`.
- **Cover:** `tiktok/tiktok_cover.jpg` (1080×1920) uses the Dr. Azren cutout. Post copy is in `tiktok/tiktok_post.md`.
- **Output:** `final_tiktok_9x16.mp4`: 1080×1920, 24 fps, 6:16, 74 MB, −14.0 LUFS, peak −1.1 dBFS.
