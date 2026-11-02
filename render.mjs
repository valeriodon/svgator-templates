// usage: node render.mjs input.(html|svg) out.png W H [dpr] [transparent]
import { chromium } from 'playwright';
const [inp, out, w, h, dpr = '1', transp] = process.argv.slice(2);
const b = await chromium.launch({ args: ['--no-sandbox', '--allow-file-access-from-files'] });
const p = await b.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: +dpr });
await p.goto('file://' + (inp.startsWith('/') ? inp : process.cwd() + '/' + inp), { waitUntil: 'networkidle' });
await p.evaluate(() => document.fonts && document.fonts.ready);
await p.waitForTimeout(400);
await p.screenshot({ path: out, omitBackground: !!transp, clip: { x: 0, y: 0, width: +w, height: +h } });
await b.close(); console.log('ok', out);
