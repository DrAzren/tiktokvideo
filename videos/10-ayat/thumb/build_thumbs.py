"""TikTok covers for '10 Ayat Dilarang Cakap' (1080x1920), two options.

  A  "10 AYAT" slammed in gold BEHIND the head (as in the hook), "JANGAN SESEKALI CAKAP!" in front,
     two struck-through harmful lines as speech bubbles at the sides (spk_0.9.png: eye contact)
  B  calmer: stacked headline at the top, the speaker below (spk_93.9.png: serious, mouth closed),
     one struck-through quote and the "Kata-kata kita ada kesan" line
Everything that matters sits inside the centre 3:4 band (y 240-1680) that TikTok's profile grid shows.
The speaker PNGs are frames of graphics/public/speaker.webm (matted, graded, ears fixed).

Run: ../../../.venv/bin/python build_thumbs.py && node shot.cjs
"""

from pathlib import Path

D = Path(__file__).parent
GOLD, IVORY, NAVY, RED = "#E9B44C", "#FFF5E4", "#0E1A2B", "#E5484D"

CSS = f"""
@font-face{{font-family:"PJS";src:url("fonts/PlusJakartaSans-800.woff2") format("woff2");font-weight:200 800;font-display:block}}
@font-face{{font-family:"Anton";src:url("fonts/Anton-400.woff2") format("woff2");font-weight:400;font-display:block}}
* {{ box-sizing:border-box; margin:0; padding:0; }}
html, body {{ width:1080px; height:1920px; overflow:hidden; background:{NAVY}; font-family:"PJS", sans-serif; }}
.stage {{ position:relative; width:1080px; height:1920px; overflow:hidden; }}
.bg {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; transform:scale(1.08); transform-origin:50% 40%; }}
.shade {{ position:absolute; inset:0; background:
  radial-gradient(70% 45% at 50% 42%, rgba(255,190,110,.16), rgba(14,26,43,0) 70%),
  linear-gradient(180deg, rgba(10,16,28,.55) 0%, rgba(10,16,28,.05) 30%, rgba(10,16,28,0) 55%, rgba(10,16,28,.75) 100%); }}
.spk {{ position:absolute; left:0; top:0; width:1080px; height:1920px; transform-origin:540px 760px;
  filter:drop-shadow(0 30px 50px rgba(0,0,0,.5)); }}
.gold {{ color:{GOLD}; }} .red {{ color:{RED}; }}
.big10 {{ position:absolute; left:0; right:0; text-align:center; font-family:"Anton"; line-height:.9; color:{GOLD};
  text-shadow:0 4px 0 #C99633, 0 9px 0 #A87A26, 0 14px 0 #8A6320, 0 34px 70px rgba(0,0,0,.6); }}
.head {{ position:absolute; left:40px; right:40px; text-align:center; font-family:"Anton"; line-height:.98; color:{IVORY};
  text-shadow:0 5px 0 rgba(0,0,0,.35), 0 16px 40px rgba(0,0,0,.75); }}
.chip {{ display:inline-block; font-weight:800; color:{NAVY}; background:{GOLD}; border-radius:16px; }}
.bubble {{ position:absolute; font-weight:800; color:{IVORY}; background:rgba(14,26,43,.80); border:3px solid rgba(229,72,77,.85);
  border-radius:26px; padding:16px 22px 18px; line-height:1.12; box-shadow:0 18px 40px rgba(0,0,0,.45); }}
.bubble s {{ text-decoration:none; background:linear-gradient({RED},{RED}) left 55%/100% 7px no-repeat; }}
.bubble .x {{ position:absolute; top:-24px; width:50px; height:50px; border-radius:50%; background:{RED}; color:#fff;
  font-size:28px; display:flex; align-items:center; justify-content:center; }}
.brand {{ position:absolute; left:0; right:0; text-align:center; font-weight:800; font-size:34px; color:{IVORY};
  letter-spacing:.02em; text-shadow:0 3px 12px rgba(0,0,0,.8); }}
.brand .bar {{ color:{GOLD}; padding:0 10px; }}
"""


def page(body: str) -> str:
    return f'<!doctype html><html lang="ms"><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="stage">{body}</div></body></html>'


A = page(f"""
<img class="bg" src="studio_soft.jpg"/><div class="shade"></div>
<div class="big10" style="top:250px;font-size:380px">10 AYAT</div>
<img class="spk" src="spk_0.9.png" style="transform:translateY(150px) scale(1.06)"/>
<div class="bubble" style="left:22px;top:1150px;width:240px;font-size:34px"><span class="x" style="right:-14px">✕</span><s>“Kau ni dah gila eh.”</s></div>
<div class="bubble" style="right:22px;top:1110px;width:236px;font-size:34px"><span class="x" style="left:-14px">✕</span><s>“Kau ni manja sangat.”</s></div>
<div class="head" style="top:1390px;font-size:106px">JANGAN <span class="red">SESEKALI</span><br/>CAKAP!</div>
<div style="position:absolute;left:0;right:0;top:1606px;text-align:center"><span class="chip" style="font-size:38px;padding:12px 24px 11px">Kepada Orang Yang Ada Masalah Mental</span></div>
<div class="brand" style="top:1730px">Dr Azren<span class="bar">|</span>Spread Positivity</div>
""")

B = page(f"""
<img class="bg" src="studio_soft.jpg"/><div class="shade"></div>
<img class="spk" src="spk_93.9.png" style="transform:translateY(215px) scale(1.0)"/>
<div class="head" style="top:240px;font-size:112px">JANGAN CAKAP</div>
<div class="big10" style="top:358px;font-size:290px">10 AYAT</div>
<div class="head" style="top:622px;font-size:96px">INI!</div>
<div class="bubble" style="left:50%;transform:translateX(-50%) rotate(-2deg);top:1440px;width:860px;font-size:50px;text-align:center"><span class="x" style="right:-14px">✕</span><s>“Kau ni terlalu fikir banyak sangat.”</s></div>
<div style="position:absolute;left:0;right:0;top:1580px;text-align:center"><span class="chip" style="font-size:40px;padding:14px 28px 13px">Kepada orang yang ada masalah mental</span></div>
<div class="brand" style="top:1700px">Dr Azren<span class="bar">|</span>Spread Positivity</div>
""")

(D / "cover_a.html").write_text(A)
(D / "cover_b.html").write_text(B)
print("wrote cover_a.html, cover_b.html")
