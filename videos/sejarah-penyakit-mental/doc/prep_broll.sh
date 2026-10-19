#!/usr/bin/env bash
# Normalise Kling clips to 1920x1080@24 (cover-crop), apply a light per-era grade, dense GOP for seeking.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=doc/public/broll; mkdir -p "$OUT"
warm="colorbalance=rs=.04:gs=.01:bs=-.05:rm=.03:bm=-.04,eq=saturation=0.92:contrast=1.04"
cold="colorbalance=rs=-.03:bs=.05:rm=-.02:bm=.03,eq=saturation=0.72:contrast=1.05:brightness=-0.01"
sci="colorbalance=rs=.02:bs=.02:rh=.03:bh=-.02,eq=saturation=0.95:contrast=1.04"
modern="colorbalance=rs=-.02:gs=0:bs=.03:rh=.04:gh=.01:bh=-.03,eq=saturation=1.02:contrast=1.04"
declare -A G=( [01_window]=$warm [02_clock]=$warm [03_globe]=$warm [04_scroll]=$warm [05_mesopotamia]=$warm [06_healer]=$warm
  [08_stoa]=$warm [09_physician]=$warm [10_writing]=$warm [11_brain_morph]=null
  [13_asylum_ext]=$cold [14_corridor]=$cold [15_room]=$cold [16_garden]=$sci
  [17_lab]=$sci [18_glassware]=$sci [19_neurons]=null
  [21_family]=$modern [22_community]=$modern [23_window_sun]=$modern [24_street]=$modern )
for n in "${!G[@]}"; do
  ffmpeg -nostdin -loglevel error -y -i broll/$n.mp4 -an \
    -vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,${G[$n]},format=yuv420p" \
    -r 24 -c:v libx264 -preset slow -crf 15 -g 12 -bf 0 "$OUT/$n.mp4"
done
ls "$OUT" | wc -l
