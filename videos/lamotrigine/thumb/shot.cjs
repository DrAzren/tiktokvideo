// Render the TikTok cover variants to PNG (1080x1920). Fails if the web fonts did not load (never ship fallback type).
const path = require("path");
const puppeteer = require(path.join(process.env.HYPERFRAMES_ROOT, "packages/engine/node_modules/puppeteer-core"));
(async () => {
  // headless "shell": puppeteer 25 otherwise asks for --headless=new, which the headless_shell binary never answers
  const b = await puppeteer.launch({ executablePath: process.env.PUPPETEER_EXECUTABLE_PATH, headless: "shell",
    args: ["--no-sandbox", "--disable-gpu"], timeout: 90000 });
  for (const v of process.argv.slice(2)) {
    const p = await b.newPage();
    await p.setViewport({ width: 1080, height: 1920 });
    await p.goto("file://" + path.join(__dirname, `index_${v}.html`), { waitUntil: "load" });
    await p.evaluate(() => document.fonts.ready);
    const ok = await p.evaluate(() => document.fonts.check('800 60px "PJS"') && document.fonts.check('800 60px "Fraunces"'));
    if (!ok) throw new Error(`fonts not loaded in ${v}`);
    await p.screenshot({ path: path.join(__dirname, `thumb_${v}.png`) });
    console.log(`thumb_${v}.png`);
  }
  await b.close();
})();
