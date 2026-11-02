// usage: node htmlseq.mjs page.html out.mp4 duration_ms [fps] [W] [H]
// the page exposes window.render(t); captures frame by frame
import { chromium } from 'playwright';
import { spawn } from 'child_process';
import path from 'path';
const [page, out, dur, fps = '60', W = '1080', H = '1350'] = process.argv.slice(2);
const b = await chromium.launch({ args: ['--no-sandbox', '--allow-file-access-from-files'] });
const p = await b.newPage({ viewport: { width: +W, height: +H } });
await p.goto('file://' + path.resolve(page), { waitUntil: 'networkidle' });
await p.evaluate(() => document.fonts.ready);
await p.waitForTimeout(300);
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', fps, '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-r', fps, out]);
const n = Math.round(+dur / 1000 * +fps);
for (let i = 0; i < n; i++) {
  await p.evaluate((t) => window.render(t), i * 1000 / +fps);
  ff.stdin.write(await p.screenshot({ type: 'png' }));
}
ff.stdin.end(); await new Promise(r => ff.on('close', r));
await b.close(); console.log('ok', out, n);
