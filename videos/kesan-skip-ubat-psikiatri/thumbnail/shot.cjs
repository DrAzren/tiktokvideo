// Screenshot an HTML page at 1080x1920 after its fonts load (refuses to shoot fallback fonts).
const path = require("path");
const puppeteer = require(path.join(process.env.HOME, "hyperframes/packages/engine/node_modules/puppeteer-core"));
(async () => {
  const [src, out] = process.argv.slice(2);
  const b = await puppeteer.launch({ executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || path.join(process.env.HOME, "bin/headless_shell_nosandbox"), args: ["--no-sandbox"] });
  const p = await b.newPage();
  await p.setViewport({ width: 1080, height: 1920 });
  await p.goto("file://" + path.resolve(src), { waitUntil: "load" });
  await p.evaluate(() => document.fonts.ready);
  const ok = await p.evaluate(() => document.fonts.check("100px Anton") && document.fonts.check("800 50px 'Plus Jakarta Sans'"));
  if (!ok) throw new Error("fonts not loaded — refusing to render fallback type");
  await p.screenshot({ path: out });
  await b.close();
})();
