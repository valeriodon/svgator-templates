// usage: node measure.mjs '[{"t":"text","f":"Geist","w":600,"s":24,"ls":0}]'   (or @file.json)
import { chromium } from 'playwright';
import fs from 'fs';
const arg = process.argv[2];
const items = JSON.parse(arg.startsWith('@') ? fs.readFileSync(arg.slice(1), 'utf8') : arg);
const fams = [...new Set(items.map(i => i.f))];
const css = 'https://fonts.googleapis.com/css2?' + fams.map(f => 'family=' + f.replace(/ /g, '+') + ':wght@400;500;600;700;800').join('&') + '&display=block';
const b = await chromium.launch({ args: ['--no-sandbox'] });
const p = await b.newPage();
await p.setContent(`<html><head><link rel="stylesheet" href="${css}"></head><body></body></html>`, { waitUntil: 'networkidle' });
const out = await p.evaluate(async (items) => {
  await document.fonts.ready;
  const res = [];
  for (const i of items) {
    await document.fonts.load(`${i.w} ${i.s}px "${i.f}"`);
    const s = document.createElement('span');
    s.style.cssText = `font:${i.w} ${i.s}px "${i.f}";letter-spacing:${i.ls || 0}px;white-space:pre;position:absolute`;
    s.textContent = i.t; document.body.appendChild(s);
    res.push({ t: i.t, width: Math.round(s.getBoundingClientRect().width) }); s.remove();
  }
  return res;
}, items);
console.log(JSON.stringify(out));
await b.close();
