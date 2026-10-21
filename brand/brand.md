# Borak Jiwa: brand kit (Dr. Azren)

Reuse these for every Borak Jiwa video, thumbnail and cover. Never print or commit secrets here.

## Identity
- **Channel:** BORAK JIWA. A mental-health channel in Bahasa Melayu.
- **Presenter / narrator:** Dr. Azren, doktor psikiatri. Write "Dr. Azren" on screen, not "Azrin".
- **Clinic:** Klinik Nissa. The on-screen lower third reads "DR. AZREN · Klinik Nissa · Saringan & konsultasi".
- **Book:** "Dr, Saya Boleh Sembuh Ke?" (Manual Survival Kesihatan Mental: Menjawab Persoalan & Menangkis Mitos).
  - Terbitan White Coat Books. The cover logo reads WHITECOAT NON-FICTION.
  - The cover is `book_cover.jpg`. Show it as a CSS 3D book; see `g_book` in
    `videos/wad-psikiatri-sejarah/doc/build_wad.py`.

## Links (descriptions, pinned comments, TikTok bio)
- **Tempah Konsultasi Bersama Dr Azren:**
  https://kliniknissa.yezza.co/appointment/kesihatan-mental-(konsultasi-dan-saringan)-129685
- **Buy the book:** https://docs.google.com/forms/d/e/1FAIpQLScl6Dvc4PyEMdOEO005c-mnDxJPLRIQ3NBbQOv3pt9-7GEXnw/viewform

## Faces and images
- `dr_azren_photo.webp`: the original photo, on a flat navy background (#052754).
- `dr_azren_cutout.png`: transparent cutout, head to chest, 1080×1015.
  - Colour-keyed from the photo.
  - Navy spill was removed from the hair.
  - The left and right edges are cut by the frame, so feather them with a CSS mask.
  - Use it for YouTube thumbnails and TikTok covers.

## Look
- **Palette:** ink #0B1418, navy #0A1A2F, teal #0E4F55, light teal #5CC8BE, gold #D9A441, cream #F4EBD8,
  sepia #3B2A1A, red #B3352B. Thumbnail headline yellow is #FFD21F with a black stroke.
- **Fonts** (`fonts/`):
  - Cinzel 600 for titles.
  - Cormorant Garamond 600 / 500 italic for quotes.
  - Plus Jakarta Sans 500/700/800 for UI, captions and thumbnails.
- **Style:** a premium cinematic documentary. Parchment and maps for history, teal and gold for the modern era.
  Use ink and paper-tear transitions. No horror, and no fabricated archival footage. Label historical visuals
  "Dramatisasi · visual dijana AI".

## Standing rules from Dr. Azren
- **Higgsfield credits:** do NOT spend them unless Dr. Azren approves the amount first. Quote the estimate and ask.
  Prefer reusing the clips and stills from earlier episodes and building graphics in HyperFrames.
- **Helplines:** don't put them on the end card or in descriptions.
- **Narration cleanup:** remove all repeated phrases, retakes and filler words ("ha", "emm", "lah", "je", "dah",
  sentence-final "ni"/"sebenarnya") from his voice. Verify the result with Whisper large-v3, both plain and
  filler-prompted.
- **Loudness:** −14 LUFS, true peak ≤ −1 dBTP. Keep music and SFX well under the voice (about 16 dB).
- **YouTube file:** the 1080p file must stay under 500 MB so it can be sent in chat. Re-encode with CRF 18 and a
  10 Mbps cap.
