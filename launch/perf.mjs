// Records a "performance" of a Launch Hero: timeline position, cursor and captions for every frame.
// usage: node perf.mjs file.svg out.mp4 perf.json [fps]
// perf.json: [{t0,t1,p0,p1,loop?:[a,b],c0:[x,y],c1:[x,y],o0,o1,press,cap,ease}]  (times in ms, 1920x1080 coordinates)
import { chromium } from 'playwright';
import fs from 'fs';
import { spawn } from 'child_process';
const [svgPath, out, perfPath, fpsArg = '30'] = process.argv.slice(2);
const fps = +fpsArg;
const segs = JSON.parse(fs.readFileSync(perfPath, 'utf8'));
const src = fs.readFileSync(svgPath, 'utf8');
const W = 1920, H = 1080;
const cursor = `<svg id="cur" viewBox="0 0 40 52" width="46" height="60" style="position:absolute;left:0;top:0;transform-origin:0 0;filter:drop-shadow(0 4px 6px rgba(0,0,0,.35))"><path d="M2 2 L2 42 L12 33 L19.5 49 L27 45.5 L19.5 30 L32.5 30 Z" fill="#111315" stroke="#fff" stroke-width="3" stroke-linejoin="round"/></svg>`;
const html = `<html><head><link href="https://fonts.googleapis.com/css2?family=Geist:wght@600&display=block" rel="stylesheet"></head>
<body style="margin:0;overflow:hidden;width:${W}px;height:${H}px;position:relative;font-family:Geist">
${src.replace('<svg ', `<svg style="width:${W}px;height:${H}px;display:block;position:absolute;inset:0" `)}
<div id="ring" style="position:absolute;width:64px;height:64px;margin:-32px 0 0 -32px;border-radius:50%;border:4px solid #fff;box-shadow:0 0 0 3px rgba(17,19,21,.35);opacity:0"></div>
${cursor}
<div id="cap" style="position:absolute;left:64px;bottom:56px;padding:16px 26px 18px;border-radius:999px;background:rgba(17,19,21,.86);color:#fff;font:600 30px/1.2 Geist;letter-spacing:-.2px;opacity:0"></div>
</body></html>`;
const b = await chromium.launch({ args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: W, height: H } });
await p.setContent(html, { waitUntil: 'networkidle' });
await p.waitForFunction(() => { const s = document.querySelector('svg'); return s && s.svgatorPlayer && s.svgatorPlayer.seekTo; }, null, { timeout: 30000 });
await p.evaluate(() => document.fonts.ready);
await p.evaluate(() => document.querySelector('svg').svgatorPlayer.pause());
const total = segs[segs.length - 1].t1;
const ease = (e, x) => e === 'inout' ? (x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2) : e === 'out' ? 1 - Math.pow(1 - x, 3) : x;
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', out]);
const n = Math.round(total / 1000 * fps);
let lastCap = null;
for (let i = 0; i < n; i++) {
  const t = i * 1000 / fps;
  const s = segs.find(s => t >= s.t0 && t < s.t1) || segs[segs.length - 1];
  const x = Math.min(1, (t - s.t0) / (s.t1 - s.t0));
  let pos;
  if (s.loop) { const [a, b2] = s.loop; pos = a + (((s.p0 - a) + (t - s.t0)) % (b2 - a)); }
  else pos = s.p0 + (s.p1 - s.p0) * (s.pease ? ease(s.pease, x) : x);
  const ce = ease(s.ease || 'inout', x);
  const c0 = s.c0 || [W + 100, H + 100], c1 = s.c1 || c0;
  const cx = c0[0] + (c1[0] - c0[0]) * ce, cy = c0[1] + (c1[1] - c0[1]) * ce;
  const o = (s.o0 ?? 1) + ((s.o1 ?? s.o0 ?? 1) - (s.o0 ?? 1)) * x;
  const cap = s.cap || '';
  await p.evaluate(({ pos, cx, cy, o, press, cap, capChanged }) => {
    document.querySelector('svg').svgatorPlayer.seekTo(pos);
    const c = document.getElementById('cur'), r = document.getElementById('ring');
    c.style.opacity = o; c.style.transform = `translate(${cx}px,${cy}px) scale(${press ? .86 : 1})`;
    r.style.left = cx + 'px'; r.style.top = cy + 'px'; r.style.opacity = press ? o * .9 : 0;
    const k = document.getElementById('cap');
    if (capChanged) { k.textContent = cap; }
    k.style.opacity = cap ? 1 : 0;
  }, { pos, cx, cy, o, press: !!s.press, cap, capChanged: cap !== lastCap });
  lastCap = cap;
  ff.stdin.write(await p.screenshot({ type: 'png' }));
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await b.close(); console.log('ok', out, n, 'frames');
