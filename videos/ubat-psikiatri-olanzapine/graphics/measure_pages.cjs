// Measure every card page's real layout height (fonts loaded) → page_heights.json.
// build_graphics.py reads it to size the panel per page (pages share one grid cell, so without
// this the panel takes the tallest page's height and short pages float in empty cream).
// Usage: node measure_pages.cjs   (then re-run build_graphics.py)
const path = require("path");
const fs = require("fs");
const puppeteer = require(path.join(process.env.HOME, "hyperframes/packages/engine/node_modules/puppeteer-core"));
(async () => {
  const browser = await puppeteer.launch({ executablePath: process.env.PUPPETEER_EXECUTABLE_PATH, args: ["--no-sandbox"] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1080, height: 1920 });
  await page.goto("file://" + path.join(__dirname, "public/index.html"), { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  const ok = await page.evaluate(() => [...document.fonts].filter(f => f.family.includes("Jakarta")).every(f => f.status === "loaded"));
  if (!ok) throw new Error("Plus Jakarta Sans not loaded — refusing to measure fallback metrics");
  const h = await page.evaluate(() => {
    const out = {};
    document.querySelectorAll(".card-host").forEach(h => { h.style.visibility = "visible"; });
    document.querySelectorAll(".page").forEach(p => { out[p.id] = Math.ceil(p.getBoundingClientRect().height); });
    return out;
  });
  fs.writeFileSync(path.join(__dirname, "page_heights.json"), JSON.stringify(h, null, 1));
  console.log(h);
  await browser.close();
})();
