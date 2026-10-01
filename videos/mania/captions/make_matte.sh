#!/usr/bin/env bash
# Subject matte ONLY for the BIPOLAR hero window (cut frames 162-237 = 5.40-7.93 s), not all 3240 frames
# (CPU matting runs ~0.6 fps here). The window has no card or insert (graphics/inserts.py HERO), so the
# graphics frame there = cut.mp4 shifted down 180 px under the band: rebuild that, matte it, and fill the
# rest of project/frames_fg with one hard-linked transparent PNG (overlay = no-op there).
# safe-zones.cjs runs on a temp project that holds only the real frames.
set -euo pipefail
cd "$(dirname "$0")"
N=3240; F0=162; F1=237; SHIFT=180
export HYPERFRAMES_ROOT=~/hyperframes
mkdir -p matte && cd matte
ffmpeg -nostdin -v error -y -i ../../edit/cut.mp4 \
  -vf "select='between(n\,$F0\,$F1)',setpts=N/30/TB,pad=1080:1920+$SHIFT:0:$SHIFT:color=0x08323C,crop=1080:1920:0:0" \
  -an -r 30 -c:v libx264 -crf 10 -pix_fmt yuv420p hero_clip.mp4
[ -f hero_fg.mov ] || node ~/hyperframes/packages/cli/dist/cli.js remove-background hero_clip.mp4 -o hero_fg.mov --device cpu
rm -rf fg bg && mkdir fg bg
ffmpeg -nostdin -v error -y -i hero_fg.mov -pix_fmt rgba -start_number $((F0 + 1)) fg/f_%04d.png
ffmpeg -nostdin -v error -y -i hero_clip.mp4 -start_number $((F0 + 1)) bg/f_%04d.png
cd ..
P=project; mkdir -p $P && rm -rf $P/frames_fg && mkdir $P/frames_fg
ffmpeg -nostdin -v error -y -f lavfi -i color=c=black@0.0:s=1080x1920,format=rgba -frames:v 1 matte/blank.png
for i in $(seq 1 $N); do f=$(printf "f_%04d.png" $i)
  if [ -f matte/fg/$f ]; then cp matte/fg/$f $P/frames_fg/$f; else ln matte/blank.png $P/frames_fg/$f; fi; done
echo 30 > $P/matte.fps
# safe-zones on the real frames only
rm -rf _sz && mkdir -p _sz && cp -r matte/fg _sz/frames_fg && cp -r matte/bg _sz/frames_bg && echo 30 > _sz/matte.fps
cp matte/hero_clip.mp4 _sz/source.mp4 && cp transcript.json _sz/
node ../../../.claude/skills/embedded-captions/scripts/safe-zones.cjs _sz | tail -5
cp _sz/safe-zones.json $P/safe-zones.json
ls $P/frames_fg | wc -l
