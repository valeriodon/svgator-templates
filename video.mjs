// usage: node video.mjs file.svg out.mp4 [fps] [scale] [duration_ms] [start_ms]
// captures the SVGator player frame by frame and encodes with ffmpeg
import { chromium } from 'playwright';
import fs from 'fs';
import { spawn } from 'child_process';
const [svg, out, fps = '30', scale = '0.5', durArg, startArg = '0'] = process.argv.slice(2);
const START = +startArg;
const src = fs.readFileSync(svg, 'utf8');
const vb = src.match(/viewBox="0 0 (\d+) (\d+)"/); const W = +vb[1], H = +vb[2];
const w = Math.round(W * +scale / 2) * 2, h = Math.round(H * +scale / 2) * 2;
const b = await chromium.launch({ args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: w, height: h } });
await p.setContent(`<html><body style="margin:0;overflow:hidden">${src.replace('<svg ', `<svg style="width:${w}px;height:${h}px;display:block" `)}</body></html>`, { waitUntil: 'networkidle' });
await p.waitForFunction(() => { const s = document.querySelector('svg'); return s && s.svgatorPlayer && s.svgatorPlayer.seekTo; }, null, { timeout: 30000 });
await p.evaluate(() => document.fonts.ready);
const dur = +durArg || await p.evaluate(() => document.querySelector('svg').svgatorPlayer.duration || 9000);
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', fps, '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', out]);
const n = Math.round(dur / 1000 * +fps);
await p.evaluate(() => document.querySelector('svg').svgatorPlayer.pause());
for (let i = 0; i < n; i++) {
  await p.evaluate((t) => document.querySelector('svg').svgatorPlayer.seekTo(t), START + i * 1000 / +fps);
  const buf = await p.screenshot({ type: 'png' });
  ff.stdin.write(buf);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await b.close(); console.log('ok', out, n, 'frames');
