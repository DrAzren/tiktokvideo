# Ubat Psikiatri Dayvigo — edit notes

Source: `raw/Ubat Psikiatri Dayvigo.mp4` (Drive, 2:12.6, 1080×1920 @ 30, single take, Malay
with English terms). Speaker holds the Dayvigo 5 mg (lemborexant) box in the opening.

## Session 1 — 2026-10-19 — analysis

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

### Session 1, round 2 — approved and produced

**User decisions:** cut list OK as proposed; KEEP "otak jadi rosak" (shown with captions only, no
graphic emphasis); Higgsfield spend OK; NO end card, no clinic/drug promotion — education only.

**Cut:** 41 ranges, 1:35.2 + 0.6s hold (1:35.8). Retakes, dead air, filler words and pitch-detected
hesitations as approved. Edges snapped on a 2 ms envelope; spectrogram-checked spots: dalam|bahasa
(start in the b-closure, 34.98), malam|ke (k-closure), off|butang (fricative tail kept, no overlap).
Clinic line kept as spoken (approved list) but given no card.

**Picture:** the phone recorded in selfie-mirror mode ("DR AZREN", the box text read backwards) →
un-mirrored with EDL `hflip` (new render_edl.py option). Punch-ins 1.0/1.08/1.03/1.1/1.05, grade `subtle`.

**Voice (enhance_voice.sh):** declip → −9 dB headroom → HPF 75 → −7 dB @160 / −2 dB @340 (de-boom) →
+4 dB @3.2k / +2.5 dB @5.6k / +3 dB shelf 9k → de-ess → light FFT denoise → 2.5:1 comp. Chain latency
(24.7 ms) trimmed; residual < 0.25 ms. Clipping is baked into the recording: softened, not undone.

**Sync bugs fixed in tools/render_edl.py:** (1) µs source timestamps made the rounded `-ss` drop a first
frame on some ranges (+33 ms per affected cut, 200 ms by the end) → seek half a frame early, take exactly
n frames (`trim=end_frame`), sample-accurate `atrim`; (2) MKV's 1 ms timestamps → enhanced source is MOV.
check_sync worst |lag| 0.1 ms.

**Graphics (graphics/build_graphics.py, one HyperFrames composition):** 10 torn-paper cards in the
headroom (y150–410), 8 AI B-roll inserts (Kling 3.0 Pro, ~70 credits) with sticky notes / kinetic type,
5 paper/night motion-graphic scenes (benzodiazepine X-out, head + JAGA switch, addiction-risk balance —
qualitative as spoken, "Bukan untuk semua orang", "Jangan tunggu lagi"), INSOMNIA hero behind the head
(remove-background matte for 32 frames, composited in assemble.sh). Talking head on screen 50%, B-roll
35%, MG 15%. One current (LEFT); no idle loops. "Ilustrasi AI" tag on every B-roll.

**Captions:** burned in the same composition (top layer), y1292–1432, one line, karaoke reveal, orange
keywords, sentence-aware breaks (hand-listed sentence starts + Whisper punctuation), corrected spellings
(Dayvigo, alprazolam, clonazepam). SRT: captions/dayvigo_ms.srt.

**Audio:** 125 synthesized SFX cues on the animation clock (audio/build_sfx.py, varied per instance,
ambiences per B-roll scene); original ambient bed (tools/ambient_bed.py, F, 66 bpm); audio/mix.py →
music 26 dB under the voice in speech / 20 dB in pauses, SFX peaks ≈10 dB under voice peaks, −14 LUFS.

**Outstanding / for the user:** switch on TikTok's AI-generated label; optionally swap the bed for a
licensed track in-app; the source clipping can only be fully fixed by re-recording with lower mic gain.

### Session 1, round 3 — user feedback: Malay casting, clothed sleeper

"Model dalam video tukar ke bangsa Melayu. Klip perempuan tidur tu bagi dia pakai baju."
- Re-generated b3 (Malay woman, long-sleeved pyjamas + tudung sarung, fully clothed), b4 (Malay man;
  2 rolls — the first read South Asian), b7 (Malay woman in tudung, for gender variety; b1/b5 are Malay
  men), b8 (Malay woman in baju kurung + tudung). b1/b5/b6 were already Malay; b2 is a hand only.
  5 × 8.75 = 43.75 credits. (Five Seedance 2.5 charges at 03:35, 175 credits, are not from this session.)
- Re-placed overlays for the new framing: b3 notes in the skyline above her; b4 context line clears as
  ANXIETY lands, boxes above his hair; b7 one combined note bottom-left over her arm; b8 notes over the
  doctor's out-of-focus coat. Snapshots checked early + late in each clip (after the push-in).
