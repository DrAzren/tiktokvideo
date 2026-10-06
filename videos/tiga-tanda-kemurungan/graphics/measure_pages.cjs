// Measure every card page's laid-out height in a real browser → page_heights.json
// (build_graphics.py sizes the panel per page from it). Also fails if any page is wider than
// its panel or if a panel would cross into the caption line.
//   node measure_pages.cjs            (after build_graphics.py; re-run build_graphics.py afterwards)
const fs = require("fs");
const path = require("path");

function findPuppeteer() {
  const root = process.env.HYPERFRAMES_ROOT || path.join(process.env.HOME, "hyperframes");
  const store = path.join(root, "node_modules", ".bun");
  for (const d of fs.readdirSync(store)) {
    if (d.startsWith("puppeteer@")) return require(path.join(store, d, "node_modules", "puppeteer"));
  }
  throw new Error("puppeteer not found under " + store);
}

(async () => {
  const puppeteer = findPuppeteer();
  const browser = await puppeteer.launch({
    executablePath: process.env.PUPPETEER_EXECUTABLE_PATH,
    args: ["--no-sandbox", "--allow-file-access-from-files"],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1080, height: 1920 });
  await page.goto("file://" + path.join(__dirname, "public", "index.html"), { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  const res = await page.evaluate(() => {
    const out = {}, problems = [];
    const fontsOk = document.fonts.check('800 40px "Plus Jakarta Sans"');
    document.querySelectorAll(".card-host").forEach((h) => (h.style.visibility = "visible"));
    document.querySelectorAll(".page").forEach((pg) => {
      pg.style.opacity = 1;
      out[pg.id] = Math.ceil(pg.getBoundingClientRect().height);
      const panel = pg.closest(".panel");
      const inner = panel.clientWidth - 72;
      pg.querySelectorAll(".title, .sub, .row, .chip").forEach((el) => {
        if (el.scrollWidth > inner + 1) problems.push(`${pg.id}: "${el.textContent.trim()}" ${el.scrollWidth}px > ${inner}px`);
      });
    });
    return { out, problems, fontsOk };
  });
  await browser.close();
  if (!res.fontsOk) throw new Error("Plus Jakarta Sans did not load — refusing to measure fallback fonts");
  fs.writeFileSync(path.join(__dirname, "page_heights.json"), JSON.stringify(res.out, null, 1));
  for (const [k, v] of Object.entries(res.out)) console.log(k.padEnd(24), v);
  if (res.problems.length) {
    console.error("TOO WIDE:\n  " + res.problems.join("\n  "));
    process.exit(1);
  }
})();
