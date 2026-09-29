# Berapa Lama Makan Ubat Psikiatri — edit notes

Source: `raw/ubat.mp4` (Drive "Berapa Lama Makan Ubat Psikiatri", 2:30, 2160×3840 @ 60, Malay).
Template: `videos/ward-psikiatri` (same pipeline, palette, caption identity).

## Session 1 — 2026-09-29 (intake + filler scan; waiting on the user's OK before cutting)

**Source findings**
- CapCut ("vicut") export: burned-in CapCut captions (y≈1410–1560, on screen in 149/155 half-second
  samples), a music bed mixed under the voice (`music_volume 20`), and black frames + music only from
  77.77 s to the end. Usable take: 0–77.7 s, one continuous shot, no internal cuts.
- Framing: head top y≈385 (20% of height), chin y≈1180 — far less headroom than ward-psikiatri (~36%).
- Working copy `edit/src1080.mp4` (1080×1920 @ 30, CRF 14); raw is untouched.

**Transcription / alignment**
- No ElevenLabs key → faster-whisper `medium` (ms, filler prompt) + unprompted large-v3 (wording).
- demucs htdemucs `--two-stems=vocals` on the take: vocal stem floor ≈ −50 dB, music removed. Alignment,
  envelope (`envelope.py`) and filler scan run on the vocal stem (`vocals16k.wav`).
- MMS_FA per island (`align.py`); `align.py --stars` puts a `*` slot between every word to expose
  unlabelled sounds; `scan_fillers.py` + `cand_plot.py` classify them by spectrogram
  (broadband = breath, flat harmonics = held vowel / hum).

**Draft cut** (`build_edl.py`): 77.5 s → 61.3 s, 37 ranges; DROP / HESITATE / TRIM lists pending approval.

**Open questions for the user:** clean CapCut re-export (no captions/music) vs working around the burned
captions; caption position given the small headroom; B-roll source (no Gemini access here).
