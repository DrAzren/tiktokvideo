// Measure every card page's real layout height (fonts loaded) -> page_heights.json
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 'public', 'index.html'));
  await p.evaluate(() => document.fonts.ready);
  const ok = await p.evaluate(() => document.fonts.check('800 40px "Plus Jakarta Sans"'));
  if (!ok) throw new Error('Plus Jakarta Sans not loaded');
  const h = await p.evaluate(() => {
    const out = {};
    document.querySelectorAll('.card-host').forEach(c => { c.style.visibility = 'visible'; });
    document.querySelectorAll('.page').forEach(pg => { pg.style.opacity = 1; out[pg.id] = Math.ceil(pg.getBoundingClientRect().height); });
    return out;
  });
  fs.writeFileSync(path.join(__dirname, 'page_heights.json'), JSON.stringify(h, null, 1));
  console.log(h);
  await b.close();
})();
