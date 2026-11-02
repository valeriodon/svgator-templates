// usage: node frames.mjs file.svg outdir t1,t2,... [scale]
// loads the animated SVG exported from SVGator, stops the player at the given times and saves PNGs
import { chromium } from 'playwright';
import fs from 'fs';
const [svg, outdir, times, scale = '0.5'] = process.argv.slice(2);
fs.mkdirSync(outdir, { recursive: true });
const src = fs.readFileSync(svg, 'utf8');
const vb = src.match(/viewBox="0 0 (\d+) (\d+)"/); const W = +vb[1], H = +vb[2];
const b = await chromium.launch({ args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: Math.round(W * +scale), height: Math.round(H * +scale) } });
await p.setContent(`<html><body style="margin:0">${src.replace('<svg ', `<svg style="width:${W * +scale}px;height:${H * +scale}px;display:block" `)}</body></html>`, { waitUntil: 'networkidle' });
await p.waitForFunction(() => { const s = document.querySelector('svg'); return s && s.svgatorPlayer && s.svgatorPlayer.seekTo; }, null, { timeout: 30000 });
await p.evaluate(() => document.fonts.ready);
for (const t of times.split(',').map(Number)) {
  await p.evaluate((t) => { const pl = document.querySelector('svg').svgatorPlayer; pl.pause(); pl.seekTo(t); }, t);
  await p.waitForTimeout(120);
  await p.screenshot({ path: `${outdir}/f${String(t).padStart(5, '0')}.png` });
}
await b.close(); console.log('ok');
