// Render GLB models to PNG with headless Chromium + three.js.
// Usage: node tools/render/render.mjs jobs.json
//   jobs.json: [{ "out": "path.png", "cfg": { ...viewer.html cfg } }, ...]
// Paths in cfg.models[].url are repo-relative ("/part3/cad/out/x.glb").
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.glb': 'model/gltf-binary', '.json': 'application/json' };
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!p.startsWith(ROOT) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const port = server.address().port;

const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
for (const job of jobs) {
  const w = job.cfg.w || 1600, h = job.cfg.h || 1100;
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('page error:', e.message));
  await page.goto(`http://127.0.0.1:${port}/tools/render/viewer.html?cfg=${encodeURIComponent(JSON.stringify(job.cfg))}`);
  await page.waitForFunction('window.__ready === true', null, { timeout: 180000 });
  const out = path.resolve(ROOT, job.out);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  await page.locator('canvas').screenshot({ path: out });
  console.log('wrote', job.out);
  await page.close();
}
await browser.close();
server.close();
