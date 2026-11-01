// Screenshot the cover (fonts asserted) -> cover.png (1080x1920) + cover_3x4.png (profile-grid preview crop)
const path = require("path");
const { chromium } = require("playwright");
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto("file://" + path.join(__dirname, "index.html"), { waitUntil: "load" });
  await p.evaluate(() => document.fonts.ready);
  const ok = await p.evaluate(() => document.fonts.check('80px "Anton"') && document.fonts.check('800 30px "PJS"'));
  if (!ok) throw new Error("fonts not loaded");
  await p.evaluate(() => { for (const id of ["a","b"]) { const el=document.getElementById(id);
    const r=document.createRange(); r.selectNodeContents(el); const w=r.getBoundingClientRect().width;
    if (w>960) el.style.fontSize=(parseFloat(getComputedStyle(el).fontSize)*960/w)+"px"; } });
  await p.screenshot({ path: path.join(__dirname, "cover.png") });
  await p.screenshot({ path: path.join(__dirname, "cover_3x4.png"), clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  await b.close();
})();
