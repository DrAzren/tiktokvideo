# TikTok Video Studio

This repo is a conversation-driven editing studio. The user drops a raw video in,
and Claude runs the full pipeline: **transcribe → cut fillers/dead air → grade →
motion graphics → captions → final render**, checking its own output before
showing it.

Everything is built from two vendored skill sets in `.claude/skills/` (see
`.claude/skills/VENDORED.md`; refresh with `scripts/sync-skills.sh`, never hand-edit them):

| Stage | Skill | Why |
|---|---|---|
| Cut, filler removal, grade, EDL render | `video-use` | Word-level transcript → EDL → per-segment render with 30ms fades |
| Motion graphics over the talking head | `talking-head-recut` | Kinetic titles, lower-thirds, callouts, PiP synced to the transcript |
| Captions (TikTok-style) | `embedded-captions` (+ `captions-overlay`) | 35 caption styles, incl. cinematic "behind the subject" |
| Standalone graphics (hook card, stat, logo sting, CTA) | `motion-graphics` | Short design-led HTML/GSAP clips, MP4 or transparent overlay |
| Anything custom / longer | `general-video` | Freeform HyperFrames composition |
| Music, SFX, voice, LUTs | `media-use`, `hyperframes-audio` | Source assets, then mix/duck under speech |
| Framework reference | `hyperframes`, `hyperframes-core`, `-cli`, `-animation`, `-keyframes`, `-creative`, `-registry`, `motion-doctrine`, `cut-the-curve`, `seam-craft` | Load on demand when writing compositions |

`hyperframes` (router) mentions other workflows (product-launch-video, faceless-explainer,
music-to-video, …) that are not vendored here; install one with
`npx hyperframes skills update <name>` only if the user actually needs it.

## Setup (per container)

```bash
scripts/setup.sh          # ffmpeg, .venv with video-use deps, hyperframes CLI check, .env
```

- Use `.venv/bin/python` for every video-use helper.
- HyperFrames runs via `npx --yes hyperframes …` (needs Node 22+). `embedded-captions` additionally
  needs a **built checkout**: `scripts/setup.sh --captions` clones + builds it at `~/hyperframes`.
  Export before any HyperFrames render/snapshot/caption script:
  ```bash
  export HYPERFRAMES_ROOT=~/hyperframes
  export HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell  # cloud container
  export PUPPETEER_EXECUTABLE_PATH=~/bin/headless_shell_nosandbox   # root needs --no-sandbox
  ```
- `ELEVENLABS_API_KEY` in `.env` (repo root) enables Scribe transcription. If it's
  missing, ask the user once for it; if they decline, use the Whisper fallback below.
  Never echo or commit the key.
- Skip the "keep this skill fresh — run `npx hyperframes skills update`" prompts at the top
  of the vendored hyperframes skills; this repo pins them via `scripts/sync-skills.sh`.

## Project layout

One folder per video under `videos/`. Footage and renders are git-ignored; only
`project.md` and `edl.json` are committed.

```
videos/<project>/
├── raw/                 ← user's source file(s), never modified
├── edit/                ← video-use working dir (its Hard Rule 12)
│   ├── transcripts/  takes_packed.md  edl.json  project.md  verify/
│   └── cut.mp4          ← stage-1 output: cut + graded, NO captions/overlays
├── graphics/            ← talking-head-recut / motion-graphics work dir
├── captions/            ← embedded-captions work dir
└── final.mp4
```

The hyperframes skills default their work dir to `videos/<basename>`; override it to
the `graphics/` or `captions/` subfolder above so projects don't collide.

## The pipeline

Follow the vendored SKILL.md for each stage — this section only says how they chain.
Default target is **1080×1920 @ 30fps vertical** unless the source or the user says otherwise.

### 0. Intake
- Move/copy the raw file into `videos/<project>/raw/`. `ffprobe` it (duration, res, fps, orientation, audio tracks).
- If `edit/project.md` exists, summarize the last session in one sentence and ask whether to continue.

### 1. Transcribe (video-use)
- With Scribe: `.venv/bin/python .claude/skills/video-use/helpers/transcribe.py videos/<p>/raw/<file> --edit-dir videos/<p>/edit`
- Whisper fallback (no key; weaker on "um/uh" because Whisper normalizes fillers):
  ```bash
  ffmpeg -i videos/<p>/raw/<file> -vn -ac 1 -ar 16000 videos/<p>/edit/audio.wav
  # any language (detect first); prompts fillers so Whisper keeps them:
  .venv/bin/python tools/transcribe_fw.py videos/<p>/edit/audio.wav --edit-dir videos/<p>/edit --name <file-stem> --language ms --model medium
  # English-only alternative: npx hyperframes transcribe … --model small.en, then tools/whisper_to_scribe.py
  ```
  `hyperframes transcribe` only ships English models + large-v3 — never use `*.en` on non-English speech.
  Tell the user filler detection is reduced, and lean harder on `timeline_view` + silence gaps.
- **Whisper word times drift 0.1–0.9s** (they swallow pauses). Before cutting, forced-align the
  corrected text with torchaudio MMS_FA (multilingual, ~20ms edges) per speech island, testing
  alternative wordings and keeping the best-scoring one — see `videos/ward-psikiatri/edit/align.py`
  + `build_edl.py` for the worked pattern (edges snapped to the energy envelope, tight pairs cut at
  the energy minimum, '*' for unknown sounds). Check every edge with an envelope plot before rendering.
- **Short sound bursts between words are not always breaths.** Ask large-v3 about any ambiguous
  burst *without* an initial prompt (a vocabulary prompt biases it) before cutting it.
- Then `pack_transcripts.py --edit-dir videos/<p>/edit` → read `takes_packed.md`.

### 2. Strategy (stop and confirm)
Pre-scan for fillers ("um", "uh", "like", "you know", false starts, repeated phrases,
retakes) and dead air. Propose in 4–8 sentences: what gets cut, target length, hook,
grade, the motion-graphics plan (which cards at which lines), caption style, music/SFX.
**Wait for the user's OK** before cutting (video-use Hard Rule 11). Propose a palette/font
if the user hasn't given a brand.

### 3. Cut + grade (video-use)
- Write `edit/edl.json`: cut every filler/false start/dead gap, snap to word boundaries, pad 30–200ms (tighter for TikTok pace).
- Leave `overlays` empty and omit `subtitles` — graphics and captions happen in HyperFrames.
- Render with **`tools/render_edl.py edit/edl.json -o edit/cut.mp4`**, not video-use's `render.py`:
  render.py's per-segment AAC + `-c copy` concat drifts the audio ~21ms later per cut (measured
  ~0.6s by 2 min). render_edl.py joins A/V in one concat filter, supports per-range `"zoom"`
  punch-ins (alternate 1.0/1.08 around `"zoom_focus"` to disguise jump cuts), writes a dense GOP.
- **Always** run `tools/check_sync.py edit/edl.json edit/cut.mp4` (fails if any range lags >25ms).
- Self-eval with `timeline_view.py` on `cut.mp4` at every cut boundary (max 3 passes), per video-use step 7.

### 4. Motion graphics (talking-head-recut, optionally motion-graphics)
- Input: `edit/cut.mp4`. Work dir: `videos/<p>/graphics/`. Don't re-transcribe: map the aligned
  source words through the EDL (exact output times) and time cards from those — see
  `videos/ward-psikiatri/edit/map_words.py` and `graphics/build_graphics.py` (cards authored against
  a word list re-map themselves when the cut changes).
- **Layout for vertical talking heads:** measure where the face sits first. Text goes in the headroom
  above the head (cards) and in a one-line band just above the hair (captions); the bottom ~20% is
  TikTok UI. Snapshot every card at its fully-built moment and fix overlap/clipping before rendering.
- For standalone pieces (intro hook card, stat count-up, CTA end card), build each with `motion-graphics` in its own folder under `graphics/`. When there are several, spawn them as parallel sub-agents (video-use Hard Rule 10).
- Output: `graphics/output.mp4`.

### 5. Captions (embedded-captions)
- Input: `graphics/output.mp4` (or `edit/cut.mp4` if no graphics). Work dir: `videos/<p>/captions/`.
- `hyperframes init --video` runs English whisper `small` and writes its own transcript.json —
  replace it with the verified word-level transcript (`{language_code, words:[{text,start,end}]}`).
- Matting is CPU-bound (~0.5–2 fps here, i.e. 1h+ for a 2.5-min clip). Only captions drawn
  BEHIND the subject need it. Matte just those windows (`remove-background` on a trimmed clip),
  fill the rest of `frames_fg/` with transparent PNGs, and run `safe-zones.cjs` on a temp
  project holding only the real frames. Worked example: `videos/ward-psikiatri/captions/`.
- The stock `render-and-composite.sh` screen-blends front captions over black, which strips
  dark strokes/shadows (white text washes out on light walls). Its bg render (`index.html`)
  already draws every caption with normal blending, so composite yourself: bg render →
  matte overlay → a transparent WebM of `index_fg.html` (background/cover made transparent,
  `--format webm`) enabled only where a front caption crosses the subject. See
  `videos/ward-psikiatri/assemble.sh`. Still run the gates: `inject-fonts`, `check-timing
  --strict`, `check-occlusion --strict`, and `preview-frames.cjs` before rendering.
- Chromium in the cloud container runs as root: point `PUPPETEER_EXECUTABLE_PATH` at a wrapper
  that adds `--no-sandbox` (`~/bin/headless_shell_nosandbox`, created by `setup.sh --captions`).
- Never pass `-shortest` when the streams are already equal length — with encoder buffering
  it silently drops the last frames.
- For TikTok, keep captions inside the safe zone: clear of the bottom ~20% (caption/UI bar) and the right ~15% (action buttons). Captions go on top of everything else (video-use Hard Rule 1).
- If the user prefers simple burned subtitles instead, use video-use's `render.py --build-subtitles` in stage 3 and skip this stage.

### 6. Audio + final
- Music: `media-use` BGM needs a signed-in HeyGen account. Without one, synthesize an original,
  licence-free bed with `tools/ambient_bed.py`, then `tools/mix_music.py <video> <bed.wav> -o <out>`
  (EQ out of the voice band, sidechain-duck, two-pass loudnorm, reports measured music-vs-voice dB).
  Also tell the user they can add a licensed track in the TikTok app instead.
- Loudness target −14 LUFS, true peak ≤ −1 dBTP; measure with `ffmpeg -i final.mp4 -af ebur128=peak=true -f null -` and report numbers (you can't listen).
- Copy the result to `videos/<p>/final.mp4`, ffprobe it, sample first/last 2s and a few midpoints with `timeline_view`, then show the user.
- Append a session entry to `edit/project.md` (strategy, decisions, outstanding).

## Rules of thumb
- Ask → confirm → execute → self-eval → show. Never skip the confirmation before cutting.
- Never re-transcribe a source that hasn't changed (cached in `edit/transcripts/`).
- Never modify files in `raw/`.
- Assert web fonts loaded in HyperFrames compositions; never ship fallback Arial.
- Cubic easing, never linear. One new element on screen at a time.
