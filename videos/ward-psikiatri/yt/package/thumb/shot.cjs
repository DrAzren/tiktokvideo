const path = require("path");
const puppeteer = require(path.join(process.env.HYPERFRAMES_ROOT, "packages/engine/node_modules/puppeteer-core"));
(async () => {
  const b = await puppeteer.launch({ executablePath: process.env.PUPPETEER_EXECUTABLE_PATH, args: ["--no-sandbox"] });
  const p = await b.newPage();
  await p.setViewport({ width: 1280, height: 720 });
  await p.goto("file://" + path.join(__dirname, "index.html"), { waitUntil: "load" });
  await p.evaluate(() => document.fonts.ready);
  const ok = await p.evaluate(() => document.fonts.check('80px "Anton"') && document.fonts.check('800 30px "PJS"'));
  if (!ok) throw new Error("fonts not loaded");
  await p.screenshot({ path: path.join(__dirname, "thumb.png") });
  await b.close();
})();
