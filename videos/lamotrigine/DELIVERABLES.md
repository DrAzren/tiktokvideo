# Ubat Psikiatri Lamotrigine: deliverables, v2 (23 Oct 2026)

| # | Deliverable | File | Status |
|---|---|---|---|
| 1 | Final TikTok/Reel, 1080×1920 @ 30, H.264 + AAC | `final.mp4` | v2 rendered |
| 2 | Editable project | `graphics/build_graphics.py` + `graphics/scenes_v2.py` → `graphics/public/index.html` (HyperFrames); cut from `edit/build_edl.py` → `edit/edl.json` | Done |
| 3 | Captioned version | `final.mp4` | Done |
| 4 | Clean version, no captions | `final_clean.mp4` | Done |
| 5 | Timecoded transcripts | `transcript_source.md`, `transcript_final.md`, `captions_ms.srt` | Updated to the v2 cut |
| 6 | AI B-roll assets + prompts | `broll/hf/S1–S7.mp4` (generated), prompts in `broll/SEEDANCE_PROMPTS.md` | 7 clips generated |
| 7 | Motion graphics / transitions list | below | Done |
| 8 | Higgsfield credit report | below | **28 credits** (approved budget: 30) |

## Higgsfield credit report (verified from the account ledger)

| Item | Model | Settings | Credits |
|---|---|---|---|
| Round 1 (analysis, prompts) | — | read-only calls only | 0 |
| S1 brain · S2 tablet · S3 window light · S4 daytime · S5 consultation · S6 low-dose · S7 sunrise | Seedance 2.0 Mini | 9:16, 720p, 4 s, no audio | 7 × 4 = **28** |
| **Total** | | | **28** |

Balance: 281.37 → **253.37**. Cost preflight per model (9:16, 5 s, no audio): Seedance 2.0 Mini 720p = 5, Kling 3.0 std =
7.5, Wan 2.7 = 7.5, Seedance 2.0 fast 720p = 12.5. Mini at 4 s (4 credits) gave the most clips within 30, and each clip
is only on screen for 2–4 s. Three submissions were bounced with a preset suggestion ("IN THE DARK") and resubmitted
with that preset declined; bounced submissions cost nothing. The other 0-credit "Seedance 2.0" ledger lines are your
own website generations.

## What changed in v2

**Speech**
- Words were clipped at filler cuts: the cut point was searched only up to 70 ms after the aligner's word end, and
  the aligner places word ends ~0.1 s early. Now the search runs from the word's end to the start of whatever follows,
  with a −46 dB quiet threshold (was −40) and 100 ms of tail. large-v3 now hears "Dia rare tapi" (was "red") and "loya".
- Three joins were pinned by hand after 5 ms energy, zero-crossing and spectral checks:
  - "doktorlah", before the breathy "ha" filler;
  - "rare", before the dropped "sebenarnya";
  - "Lamotrigine", after the dropped "tadi". The old start kept "di", which large-v3 heard as "Di"/"Jadi".
- Delays between words: every non-speech gap (< −30 dB, incl. breaths) longer than 0.17 s is now cut to 0.13 s, and
  every join keeps at most 90 ms after the last sound and 70 ms before the next. Longest gap: 0.42 s → **0.16 s**
  (22 gaps over 0.15 s before; none over 0.16 s now). Cut length 82.0 s + 1.5 s end card.

**B-roll and animation:** coverage rose from about 35% to about **64%** of the runtime.

| Time | Scene | Kind | In / out transition |
|---|---|---|---|
| 0:01.5 | S1 brain, neural light | Seedance, full screen | zoom-through / under |
| 0:02.9 | Litium periodic tile → flips to "? Satu lagi ubat" | 3D animation | whip pan |
| 0:07.2 | S2 tablet + "UNDERRATED / TAPI POWER" | Seedance + kinetic type | **paper tear** / fade |
| 0:10.8 | LAMOTRIGINE 3D title, docks into chest band | title | slam |
| 0:14.1 | molecular lattice | animation | **3D cube** (speaker turns away) |
| 0:16.5 | S3 window light, "Bipolar disorder" | Seedance in a **paper polaroid** | polaroid drop / **page flip** |
| 0:21.3 | weight gauge "SANGAT RENDAH" | infographic | page flip / whip |
| 0:28.5 | S4 daytime, "Function macam biasa" | Seedance in polaroid | polaroid drop |
| 0:32.3 | calendar pages flipping, "Long-term use" | animation | whip |
| 0:34.8 | S5 consultation + "Dengan monitoring doktor" | Seedance, full screen | page flip / zoom |
| 0:40.4 | S6 low dose + "Mula dengan dos yang rendah" | Seedance, full screen | iris |
| 0:42.6 | rising steps "Perlahan-lahan naik · Titrate" | infographic | 3D cube (scene to scene) |
| 0:44.6 | Stevens-Johnson safety card (on your face, no imagery) | card | — |
| 0:53.3 | side effects: pening kepala / loya / susah tidur | infographic | paper tear / 3D cube back to you |
| 1:03.1 | S7 sunrise (comparison card stays on top) | Seedance, full screen | iris / whip |
| 1:08.5 | shield draws + check, "Cara guna yang selamat" | animation | zoom-through |
| 1:11.8 | mood wave that settles | animation | whip / page flip |
| 1:15.8 | S5 consultation, "Sembang santai dahulu" | Seedance in polaroid | polaroid drop / drop away |
| 1:22.0 | SPREAD POSITIVITY end card | end card | — |

On your face (about 36%): the hook, "Pernah dengar tak", "Terutamanya dalam episod kemurungan", "Tak buat rasa mengantuk",
"Setiap ubat ada side effect", the Stevens-Johnson card, the mania/relapse comparison, "Jangan stop sendiri", your name
strip and the comment chip. Safety lines stay on your face on purpose.

**Sound effects:** 45 cues. Every transition has its own synthesized sound: paper rip, page flip, 3D cube swoosh +
soft thump, swish for whip pans, paper drop for the polaroids, whoosh for zoom/iris. Pops/ticks mark list items, and
soft impacts mark key words. All are generated locally (no samples) and peak well under the voice.

## Swapping or adding clips later

Put a clip at `graphics/public/broll/S<n>.mp4`, point a scene at it in `graphics/scenes_v2.py` (`scenes()`), then run:

```bash
cd videos/lamotrigine/graphics && ../../../.venv/bin/python build_graphics.py && ../../../.venv/bin/python build_graphics.py --clean
npx hyperframes render public -o output.mp4 --fps 30 && npx hyperframes render public_clean -o output_clean.mp4 --fps 30
cd .. && ./assemble.sh
```

Clips longer than a slot use their middle (or `ms`); a slot longer than its clip slows the clip slightly
(`data-playback-rate`). Each AI clip carries an "Ilustrasi AI" tag; switch on TikTok's / Instagram's
**AI-generated content** label when you post.

## Audio, music, medical notes

Unchanged from v1: local voice polish chain, original F-major bed ducked about 21 dB under the voice, −14 LUFS /
≤ −1 dBTP master. Medical review notes are unchanged too: 0:19 "terutamanya dalam episod kemurungan" (maintenance
nuance), the approved line "Ruam baru? Jumpa doktor segera.", and the spellings "Lamotrigine" and "Stevens-Johnson
syndrome". On-screen text uses only your words (plus neutral labels such as "Jangka panjang" and "Kena ingat").
