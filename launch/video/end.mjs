// Renders the end card of the Launch Heroes demo video (end.html -> end.png, next to this script).
// end.html expects four stills in capture/lhend/<concept>/ (frames.mjs output).
import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
const here = new URL('.', import.meta.url);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.goto(new URL('end.html', here).href, { waitUntil: 'networkidle' });
await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
await p.screenshot({ path: fileURLToPath(new URL('end.png', here)) });
await b.close();
