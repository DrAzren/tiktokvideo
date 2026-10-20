"""Shorts / TikTok cover for 'Kesan Skip Ubat Psikiatri' (1080x1920).

Built from cut frame 79 (0:02.6, eyes on camera) and its subject matte (captions/_matte), so the
headline can sit BEHIND the head like the "BERHENTI" hero in the video. Same identity as the edit:
Anton headline (cream + mint), deep-teal grade at the top, cream/teal/red chips in Plus Jakarta Sans.
Important type stays above y~1500 (Shorts/TikTok overlay the title and buttons on the bottom of the feed card).

Usage: python make_thumb.py [frame]   → thumbnail/thumbnail.png (+ thumbnail.jpg)
"""
import base64
import subprocess
import sys
from pathlib import Path

T = Path(__file__).parent
V = T.parent
FRAME = int(sys.argv[1]) if len(sys.argv) > 1 else 79
TEAL, DEEP, MINT, CREAM, INK, RED = "#0E5E6F", "#08323C", "#5EEAD4", "#FFF8EE", "#0B1F2A", "#E5484D"


def data_uri(p: Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


bg = data_uri(V / "captions" / "_matte" / "frames_bg" / f"f_{FRAME:04d}.png", "image/png")
fg = data_uri(V / "captions" / "_matte" / "frames_fg" / f"f_{FRAME:04d}.png", "image/png")
anton = (V.parents[1] / ".claude/skills/embedded-captions/modes/standard/fonts/fonts.css").read_text()
pjs = "".join(
    f'@font-face{{font-family:"Plus Jakarta Sans";src:url("{data_uri(V / "graphics/public/fonts" / f"PlusJakartaSans-{w}.woff2", "font/woff2")}") '
    f'format("woff2");font-weight:{w};}}' for w in (700, 800))
WARN = ('<svg viewBox="0 0 48 48" class="wi"><g fill="none" stroke="#fff" stroke-width="4.2" stroke-linecap="round" '
        'stroke-linejoin="round"><path d="M24 6L4 41h40z"/><path d="M24 19v10M24 35v.5"/></g></svg>')

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
{anton}
{pjs}
html,body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:#000}}
.l{{position:absolute;inset:0}}
.bg{{background:url({bg}) center/cover; filter:saturate(1.05) contrast(1.04)}}
.shade{{background:linear-gradient(180deg, rgba(8,50,60,.92) 0%, rgba(8,50,60,.70) 18%, rgba(8,50,60,.15) 34%, rgba(0,0,0,0) 46%,
  rgba(0,0,0,0) 58%, rgba(5,30,37,.55) 74%, rgba(5,30,37,.85) 100%)}}
.head{{position:absolute;left:0;right:0;text-align:center;font-family:Anton;text-transform:uppercase;line-height:.92;
  -webkit-text-stroke:5px rgba(0,0,0,.55);paint-order:stroke fill;text-shadow:0 10px 0 rgba(0,0,0,.28),0 18px 50px rgba(0,0,0,.5)}}
.h1{{top:150px;font-size:250px;color:{CREAM};letter-spacing:.01em}}
.h2{{top:378px;font-size:212px;color:{MINT};letter-spacing:.005em}}
.fg{{background:url({fg}) center/cover}}
.badge{{position:absolute;left:60px;top:1272px;display:flex;align-items:center;gap:22px;background:{RED};color:#fff;
  font-family:'Plus Jakarta Sans';font-weight:800;font-size:92px;letter-spacing:-.01em;padding:18px 40px 20px 30px;border-radius:30px;
  box-shadow:0 18px 50px rgba(0,0,0,.45);transform:rotate(-3deg)}}
.wi{{width:88px;height:88px}}
.panel{{position:absolute;left:60px;right:60px;top:1418px;background:{CREAM};border-radius:30px;padding:26px 36px 30px 48px;
  font-family:'Plus Jakarta Sans';color:{INK};box-shadow:0 22px 60px rgba(0,0,0,.45);overflow:hidden}}
.panel::before{{content:"";position:absolute;left:0;top:0;bottom:0;width:14px;background:{TEAL}}}
.p1{{font-weight:800;font-size:50px;line-height:1.08;letter-spacing:-.015em}}
.p1 b{{color:{RED}}}
.who{{position:absolute;left:50%;transform:translateX(-50%);white-space:nowrap;top:52px;font-family:'Plus Jakarta Sans';font-weight:800;font-size:34px;letter-spacing:.06em;
  text-transform:uppercase;color:#fff;background:{TEAL};padding:12px 24px 11px;border-radius:999px}}
</style></head><body>
<div class="l bg"></div><div class="l shade"></div>
<div class="head h1">Skip ubat</div>
<div class="head h2">psikiatri?</div>
<div class="l fg"></div>
<div class="badge">{WARN}3 KESAN</div>
<div class="panel"><div class="p1">Kalau stop ubat sendiri <b>tanpa bincang dengan doktor</b></div></div>
<div class="who">Dr Azren · Doktor Psikiatri</div>
</body></html>"""
(T / "thumbnail.html").write_text(html)
subprocess.run(["node", str(T / "shot.cjs"), str(T / "thumbnail.html"), str(T / "thumbnail.png")], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(T / "thumbnail.png"), "-q:v", "2", str(T / "thumbnail.jpg")], check=True)
print("→", T / "thumbnail.png", T / "thumbnail.jpg")
