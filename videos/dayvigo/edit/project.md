# Ubat Psikiatri Dayvigo — edit notes

Source: `raw/Ubat Psikiatri Dayvigo.mp4` (Drive, 2:12.6, 1080×1920 @ 30, single take, Malay
with English terms). Speaker holds the Dayvigo 5 mg (lemborexant) box in the opening.

## Session 1 — 2026-10-19 (analysis; waiting for the user's OK before cutting)

**Transcription:** no ElevenLabs key → faster-whisper `medium` (filler prompt) + unprompted
`large-v3`; torchaudio MMS_FA forced alignment per island (`align.py`, scores 0.69–0.89).
`tools/transcribe_fw.py` now decodes .wav with soundfile (PyAV 19 rejects faster-whisper's
`metadata_errors` kwarg).

**Wording settled:** "Pernah tak?" (hook end), aprazolam/klonazepam as spoken, "orexin reseptor
antagonis", "dan dikawal", "kesihatan" (no "mental" at 111 s), "di klinik saya di Nilai".
Bursts at 8.9–11.4 s are non-speech (large-v3 hallucinates "terima kasih kerana menonton");
33.0–34.8 s and 43.2–46.6 s are unpitched breath/handling noise.

**Audio:** source is −6.1 LUFS integrated with ~32.6k clipped samples (16 kHz mono): baked
into the recording. Declip can soften it, not undo it.

**Framing:** head top ≈23% height, chin ≈63%; headroom band is small (cards must stay above
~22% or use full-screen inserts).

**Proposed (pending approval):** retakes → keep 2nd "bahasa senang dia" take and the clean
"ubat ni boleh menyebabkan mengantuk" restart; drop "Ataupun boleh datang di klinik saya"
(superseded); drop padding words (dah, tu, ke apa, sebenarnya, of course, lah, dia ×6, macam,
ke); cut pitch-detected hesitations at 40.1, 50.6–52.6, 84.8, 101.3, 110.5, 111.9, 113.5 s;
dead air at 8.3–12.2, 33.0–34.8, 43.2–46.6, 77.6–80.3 s. Estimate ≈1:31–1:35.
Medical flag: "Tidur yang terganggu boleh menyebabkan otak jadi rosak" (114.6–118.2), recommend cut.
B-roll: Kling 3.0 Pro 5 s 9:16 silent = 8.75 credits/clip (balance 1,250.5).

**Outstanding:** user approval of the cut list, the "otak jadi rosak" call, B-roll spend, clinic
name/booking line for the end card.
