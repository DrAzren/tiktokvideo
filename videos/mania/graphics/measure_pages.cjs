// Real-browser layout of every card page -> page_heights.json {"<card>-page<n>": [bottom of element 1, 2, ...]}
// (cumulative height after each top-level element lands; build_graphics.py grows the panel step by step).
const path = require("path"), fs = require("fs");
const puppeteer = require(path.join(process.env.HOME, "hyperframes/node_modules/.bun/puppeteer@25.8.0/node_modules/puppeteer"));
(async () => {
  const browser = await puppeteer.launch({ executablePath: process.env.PUPPETEER_EXECUTABLE_PATH, args: ["--no-sandbox", "--allow-file-access-from-files"] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1080, height: 1920 });
  await page.goto("file://" + path.join(__dirname, "public/index.html"), { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  const ok = await page.evaluate(() => document.fonts.check('800 54px "Plus Jakarta Sans"'));
  if (!ok) throw new Error("Plus Jakarta Sans did not load");
  const out = await page.evaluate(() => {
    const res = {};
    document.querySelectorAll(".card-host").forEach(h => { h.style.visibility = "visible"; });
    document.querySelectorAll(".page").forEach(pg => {
      pg.style.opacity = 1;
      const hs = [];
      for (const el of pg.children) hs.push(Math.ceil(el.offsetTop + el.offsetHeight));
      res[pg.id] = hs;
    });
    return res;
  });
  fs.writeFileSync(path.join(__dirname, "page_heights.json"), JSON.stringify(out, null, 1));
  console.log(Object.entries(out).map(([k, v]) => `${k}: ${v.join(",")}`).join("\n"));
  await browser.close();
})();
