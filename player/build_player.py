#!/usr/bin/env python3
"""Builds player/index.html: the TV player for Departures.
Three-step setup (Board, Sound, Depart) with a split-flap ticket strip; the SVG boards are embedded
and driven by the SVGator Player API, which plays the alert at every flip.
Needs the four board exports in player/boards/<key>.svg (not committed): SVGator SVG exports with the
player and fonts embedded and start set to programmatic. The built page is published in
github.com/valeriodon/departures-player."""
import base64, os
HERE = os.path.dirname(os.path.abspath(__file__))
BOARDS = [('aurora', 'Aurora Café', 'List board', 'menus and price lists', '#E35D3A'),
          ('studionine', 'Studio Nine', 'Schedule board', 'classes and showtimes', '#D9486F'),
          ('barberseven', 'Barber Seven', 'Queue board', 'now serving', '#B5452E'),
          ('seahouse', 'Sea House', 'Welcome board', 'holiday rentals', '#1F8FA8')]
SOUNDS = [('bell', 'Soft bell', 'One gentle ding'), ('dingdong', 'Ding-dong', 'Two notes, station style'),
          ('shop', 'Shop bell', 'Bright double ding'), ('chime', 'Chime', 'Three rising notes'),
          ('wood', 'Wood block', 'Short and soft'), ('none', 'Silent', 'No sound, flaps only')]

def thumb(k):
    return 'data:image/jpeg;base64,' + base64.b64encode(open(os.path.join(HERE, 'thumbs', k + '.jpg'), 'rb').read()).decode()

pool = ''.join(f'<div class="board" id="b-{k}" data-key="{k}">{open(os.path.join(HERE, "boards", k + ".svg")).read()}</div>\n' for k, *_ in BOARDS)
cards = ''.join(f'''<button type="button" class="card" role="radio" aria-checked="false" data-board="{k}" style="--brand:{c}">
  <span class="shot"><img src="{thumb(k)}" alt="" width="640" height="360"></span>
  <span class="meta"><span class="name">{n}</span><span class="kind">{t} · {d}</span><span class="live"><i></i>Live</span></span>
</button>''' for k, n, t, d, c in BOARDS)
SPEAKER = '<svg class="ico" viewBox="0 0 20 20" aria-hidden="true"><path d="M3 8h3l4-3.5v11L6 12H3z" fill="currentColor"/><path d="M13 7.2a4 4 0 0 1 0 5.6M15.2 5a7 7 0 0 1 0 10" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'
sounds = ''.join(f'<button type="button" class="opt" role="radio" aria-checked="false" data-sound="{k}"><span class="dot"></span><span class="txt"><b>{n}</b><small>{d}</small></span>{SPEAKER if k != "none" else ""}</button>' for k, n, d in SOUNDS)

html = '''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Departures TV player</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js"></script>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Chivo+Mono:wght@700&family=Geist:wght@400;500;600&display=swap">
<style>
:root{
  --ground:#0E0F11; --panel:#15171B; --raised:#1C1E23; --line:#2B2E34; --line2:#3A3E46;
  --ink:#F1ECE2; --muted:#A7AAB1; --amber:#F2B33D; --amber-ink:#17140C;
  --tile-top:#2C2F35; --tile-top2:#25282D; --tile-bot:#1E2024; --tile-bot2:#1A1C1F;
  --display:"Bricolage Grotesque","Avenir Next Condensed",system-ui,sans-serif;
  --ui:"Geist","Helvetica Neue",system-ui,sans-serif;
  --flap:"Chivo Mono","SF Mono",Menlo,monospace;
  color-scheme:dark;
}
*{box-sizing:border-box}
[hidden]{display:none!important}
html,body{height:100%}
body{margin:0;background:var(--ground);color:var(--ink);font:16px/1.5 var(--ui);-webkit-font-smoothing:antialiased}
::selection{background:var(--amber);color:var(--amber-ink)}
button,input{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--amber);outline-offset:3px}
.board{width:100%;height:100%}
.board svg{width:100%;height:100%;display:block}
#pool{display:none}

/* full-screen stage */
.stage{position:fixed;inset:0;display:grid;place-items:center;background:#060708}
.stage .holder{width:min(100vw,177.78vh);aspect-ratio:16/9}
.turn{position:fixed;top:calc(12px + env(safe-area-inset-top,0px));left:50%;transform:translateX(-50%);z-index:3;background:rgba(21,23,27,.94);border:1px solid var(--line2);border-radius:999px;padding:8px 14px;font-size:14px;white-space:nowrap;display:none}
@media (orientation:portrait) and (max-width:880px){.stage .turn{display:block}}
.gear{position:fixed;right:16px;bottom:calc(16px + env(safe-area-inset-bottom,0px));z-index:3;opacity:0;transition:opacity .35s cubic-bezier(.2,.8,.2,1);background:rgba(21,23,27,.94);border:1px solid var(--line2);border-radius:999px;padding:10px 16px;font-weight:600;font-size:14px;cursor:pointer}
body.awake .gear,.gear:focus-visible{opacity:1}

/* setup */
.setup{position:fixed;inset:0;display:grid;grid-template-rows:auto minmax(0,1fr) auto;grid-template-columns:minmax(0,1fr);background:var(--ground);z-index:5}
.setup>*{min-width:0}
.bar{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:24px;padding:14px clamp(16px,3vw,40px);border-bottom:1px solid var(--line)}
.bar .close{justify-self:end;grid-column:3}
.brand{display:flex;align-items:center;gap:12px;min-width:0}
.brand .mark{display:grid;grid-template-columns:repeat(2,13px);gap:2px}
.brand .mark i{display:block;height:18px;border-radius:2px;background:linear-gradient(var(--tile-top) 0 48%,#0A0B0C 48% 52%,var(--tile-bot) 52%)}
.brand b{font:800 22px/1 var(--display);letter-spacing:-.02em}
.brand span{color:var(--muted);font-size:14px;white-space:nowrap}
.steps{display:flex;gap:6px;grid-column:2}
.steps button{display:flex;align-items:center;gap:9px;background:none;border:1px solid transparent;border-radius:999px;padding:7px 14px 7px 8px;cursor:pointer;color:var(--muted);font-weight:500}
.steps button i{font-style:normal;display:grid;place-items:center;width:24px;height:24px;border-radius:50%;border:1px solid var(--line2);font:600 12px var(--ui);font-variant-numeric:tabular-nums}
.steps button[aria-current="step"]{color:var(--ink);border-color:var(--line2);background:var(--panel)}
.steps button[aria-current="step"] i{background:var(--amber);border-color:var(--amber);color:var(--amber-ink)}
.steps button.done i{border-color:var(--amber);color:var(--amber)}
.close{background:none;border:1px solid var(--line2);border-radius:999px;padding:8px 14px;cursor:pointer;font-weight:600;font-size:14px}

main{overflow:auto;scrollbar-color:var(--line2) transparent;scrollbar-width:thin;padding:clamp(20px,3.2vh,36px) clamp(16px,3vw,40px)}
.step{max-width:1180px;margin:0 auto}
.head{display:flex;align-items:baseline;justify-content:space-between;gap:16px 32px;flex-wrap:wrap;margin-bottom:clamp(16px,2.6vh,28px)}
h1{font:800 clamp(30px,3.3vw,46px)/1.02 var(--display);letter-spacing:-.025em;margin:0;text-wrap:balance}
.lead{margin:0;color:var(--muted);max-width:52ch}

/* step 1: cards */
.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:clamp(12px,1.6vw,20px);max-width:min(1000px,calc((100dvh - 430px) * 1.778 + 20px));min-width:min(100%,640px);margin:0 auto}
.step[data-step="1"] .head{max-width:min(1000px,calc((100dvh - 430px) * 1.778 + 20px));min-width:min(100%,640px);margin-left:auto;margin-right:auto}
.card{appearance:none;text-align:left;padding:0;cursor:pointer;background:var(--panel);border:1px solid var(--line);border-radius:16px;overflow:hidden;display:flex;flex-direction:column;transition:border-color .2s,transform .2s cubic-bezier(.2,.8,.2,1)}
.card:hover{border-color:var(--line2);transform:translateY(-2px)}
.card[aria-checked="true"]{border:2px solid var(--brand);margin:-1px}
.shot{position:relative;aspect-ratio:16/9;background:#060708;overflow:hidden}
.shot img{width:100%;height:100%;object-fit:cover;display:block}
.shot .board{position:absolute;inset:0}
.meta{display:grid;grid-template-columns:1fr auto;align-items:center;gap:2px 12px;padding:12px 16px 14px}
.name{font:800 21px/1.15 var(--display);letter-spacing:-.015em}
.kind{grid-column:1;color:var(--muted);font-size:14px}
.live{grid-column:2;grid-row:1/3;display:none;align-items:center;gap:7px;font:600 12px var(--ui);letter-spacing:.12em;text-transform:uppercase;color:var(--ink)}
.live i{width:9px;height:9px;border-radius:50%;background:var(--brand);display:block;animation:pulse 1.6s ease-in-out infinite}
.card[aria-checked="true"] .live{display:flex}
@keyframes pulse{50%{opacity:.35}}

/* steps 2 and 3: preview + controls */
.two{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(300px,1fr);grid-template-areas:"pv hd" "pv ct";grid-template-rows:auto 1fr;gap:0 clamp(18px,2.6vw,36px);align-items:start}
.two .pv{grid-area:pv}.two .hd{grid-area:hd}.two .ct{grid-area:ct}
.two .hd .lead{margin:-8px 0 20px}
.screen{aspect-ratio:16/9;border-radius:14px;overflow:hidden;background:#060708;border:1px solid var(--line)}
.under{display:flex;align-items:center;gap:14px;margin-top:14px;flex-wrap:wrap}
.under p{margin:0;color:var(--muted);font-size:14px}
.group{border:0;margin:0 0 22px;padding:0}
.group legend,.label{font-weight:600;margin-bottom:10px;padding:0;display:block}
.opts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}
.opt{appearance:none;display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:12px;text-align:left;cursor:pointer;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:10px 14px}
.opt:hover{border-color:var(--line2)}
.opt .dot{width:18px;height:18px;border-radius:50%;border:2px solid var(--line2);display:grid;place-items:center}
.opt[aria-checked="true"]{background:var(--raised);border-color:var(--line2)}
.opt[aria-checked="true"] .dot{border-color:var(--amber)}
.opt[aria-checked="true"] .dot::after{content:"";width:8px;height:8px;border-radius:50%;background:var(--amber)}
.opt b{font-weight:600}
.opt small{display:block;color:var(--muted);font-size:13px}
.ico{width:20px;height:20px;color:var(--muted)}
.upload{display:flex;align-items:center;gap:12px;margin-top:8px;flex-wrap:wrap}
.upload small{color:var(--muted);font-size:13px}
.upload:has(input:focus-visible) label{outline:2px solid var(--amber);outline-offset:3px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.seg{display:grid;grid-template-columns:1fr 1fr;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:4px;gap:4px}
.seg button{appearance:none;border:0;background:none;border-radius:9px;padding:9px 10px;cursor:pointer;font-weight:600;color:var(--muted)}
.seg button[aria-pressed="true"]{background:var(--raised);color:var(--ink);box-shadow:0 1px 2px rgba(0,0,0,.4)}
.vol{display:flex;align-items:center;gap:14px}
.vol input{flex:1;accent-color:var(--amber)}
.vol output{font:600 15px var(--ui);font-variant-numeric:tabular-nums;min-width:4ch;text-align:right}
.field-in{display:block;width:100%;background:var(--panel);border:1px solid var(--line2);border-radius:12px;padding:11px 14px;color:var(--ink);resize:vertical;min-height:46px}
.field-in::placeholder{color:#7D8088}
.field-in:focus-visible{outline:2px solid var(--amber);outline-offset:2px;border-color:var(--amber)}
textarea.field-in{font:500 15px/1.4 var(--ui);text-transform:uppercase}
.help{display:block;color:var(--muted);font-size:13px;margin-top:6px;font-variant-numeric:tabular-nums}
.check{display:flex;align-items:center;gap:10px;cursor:pointer;font-weight:500}
.check input{width:18px;height:18px;accent-color:var(--amber)}
.keys{color:var(--muted);font-size:14px;margin:16px 0 0}
kbd{font:600 12px var(--ui);border:1px solid var(--line2);border-bottom-width:2px;border-radius:5px;padding:1px 6px;color:var(--ink)}

.btn{appearance:none;border:1px solid var(--line2);background:none;border-radius:12px;padding:11px 18px;font-weight:600;cursor:pointer;display:inline-flex;align-items:center;gap:8px}
.btn:hover{border-color:var(--muted)}
.btn.primary{background:var(--amber);border-color:var(--amber);color:var(--amber-ink)}
.btn.primary:hover{filter:brightness(1.06)}
.btn:disabled{opacity:.4;cursor:default}

/* ticket: strip of flaps */
.ticket{display:flex;align-items:center;gap:20px 28px;padding:14px clamp(16px,3vw,40px) calc(14px + env(safe-area-inset-bottom,0px));border-top:1px solid var(--line);background:#09090B;overflow:hidden}
.strip{display:flex;gap:18px;flex-wrap:wrap;min-width:0;flex:1}
.field{display:flex;flex-direction:column;gap:5px}
.field small{font:600 11px var(--ui);letter-spacing:.14em;color:var(--muted)}
.cells{display:flex;gap:3px}
.cell{position:relative;width:1.18em;height:1.6em;font:700 clamp(15px,1.45vw,21px)/1 var(--flap);color:#F4EFE5;perspective:12em;border-radius:4px;box-shadow:0 1px 2px rgba(0,0,0,.8)}
.cell::before,.cell::after{content:"";position:absolute;top:calc(50% - 2px);width:2px;height:4px;background:#050506;z-index:4}
.cell::before{left:0}.cell::after{right:0}
.half,.leaf{position:absolute;left:0;right:0;height:50%;overflow:hidden;backface-visibility:hidden}
.half.t,.leaf.t{top:0;border-radius:4px 4px 0 0;background:linear-gradient(var(--tile-top),var(--tile-top2));border-bottom:1px solid #060607}
.half.b,.leaf.b{bottom:0;border-radius:0 0 4px 4px;background:linear-gradient(var(--tile-bot),var(--tile-bot2))}
.half i,.leaf i{position:absolute;left:0;right:0;height:200%;display:grid;place-items:center;font-style:normal}
.half.t i,.leaf.t i{top:0}.half.b i,.leaf.b i{bottom:0}
.leaf{z-index:3}
.leaf.t{transform-origin:50% 100%;animation:fall .14s cubic-bezier(.55,0,1,.6) forwards}
.leaf.b{transform-origin:50% 0;transform:rotateX(90deg);animation:land .14s cubic-bezier(0,.4,.4,1) .14s forwards}
@keyframes fall{to{transform:rotateX(-90deg);filter:brightness(.45)}}
@keyframes land{from{transform:rotateX(90deg);filter:brightness(.6)}to{transform:rotateX(0);filter:none}}
.field small{transition:color .3s}
.field.changed small{color:var(--amber);transition:none}
.nav{display:flex;gap:10px;margin-left:auto}

@media (max-width:880px){
  .bar{grid-template-columns:1fr auto;gap:10px 16px}
  .steps{grid-column:1/-1;grid-row:2;width:100%;justify-content:space-between}
  .bar .close{grid-column:2;grid-row:1}
  .under{margin:12px 0 28px}
  .steps button{padding:5px 9px 5px 5px;font-size:14px;gap:6px}
  .steps button i{width:22px;height:22px}
  .opts{grid-template-columns:1fr}
  .cards,.step[data-step="1"] .head{max-width:none;min-width:0}
  .two{grid-template-columns:1fr}
  .cards{grid-template-columns:1fr}
  .ticket{flex-direction:column;align-items:stretch}
  .strip{display:grid;grid-template-columns:1fr;gap:6px}
  .field{flex-direction:row;align-items:center;gap:10px}
  .field small{width:4.6em;flex:none}
  .field[data-f="vol"]{display:none}
  .cells{gap:2px}
  .cell{width:1.12em;height:1.5em;font-size:14px}
  .two{grid-template-areas:"hd" "pv" "ct"!important;grid-template-columns:1fr!important}
  .gear .k{display:none}
  .nav .btn{flex:1;justify-content:center}
}
@media (prefers-reduced-motion:reduce){.leaf,.live i{animation:none}.card,.gear,.field small{transition:none}}
</style>

<div id="pool">''' + pool + '''</div>
<div class="stage" id="stage" hidden><div class="holder" id="holder"></div><p class="turn">Turn your phone sideways for the full board</p></div>
<button type="button" class="gear" id="gear" hidden>Settings<span class="k"> (S)</span></button>

<div class="setup" id="setup">
  <header class="bar">
    <div class="brand"><span class="mark" aria-hidden="true"><i></i><i></i></span><b>Departures</b><span>TV player</span></div>
    <nav class="steps" aria-label="Setup steps">
      <button type="button" data-go="1"><i>1</i>Board</button>
      <button type="button" data-go="2"><i>2</i>Sound</button>
      <button type="button" data-go="3"><i>3</i>Depart</button>
    </nav>
    <button type="button" class="close" id="close" hidden>Back to the board</button>
  </header>

  <main id="main">
    <section class="step" data-step="1" aria-labelledby="h1">
      <div class="head"><h1 id="h1">Pick a board</h1><p class="lead">Four businesses on three layouts. Tap one and it comes alive.</p></div>
      <div class="cards" role="radiogroup" aria-labelledby="h1">''' + cards + '''</div>
    </section>

    <section class="step" data-step="2" aria-labelledby="h2" hidden>
      <div class="two">
        <div class="pv">
          <div class="screen" id="screen2"></div>
          <div class="under"><button type="button" class="btn" data-flip>Flip now</button><p>It also flips by itself every 12 seconds.</p></div>
        </div>
        <div class="hd"><div class="head"><h1 id="h2">Pick its alert</h1></div>
          <p class="lead">Played each time the board flips. SVGator exports carry no sound, so the player adds it.</p></div>
        <div class="ct">
          <div class="group" role="radiogroup" aria-label="Alert sound"><div class="opts" id="sounds">''' + sounds + '''</div>
            <div class="upload"><label class="btn" for="file">Upload your own</label><input class="sr" id="file" type="file" accept="audio/*"><small id="customName">mp3, wav or m4a, kept for this visit</small></div>
          </div>
          <div class="group"><span class="label" id="whenl">When</span>
            <div class="seg" role="group" aria-labelledby="whenl"><button type="button" data-when="every" aria-pressed="false">Every flip</button><button type="button" data-when="first" aria-pressed="false">First flip only</button></div>
          </div>
          <div class="group"><label class="label" for="vol">Volume</label><div class="vol"><input id="vol" type="range" min="0" max="1" step="0.05"><output id="volout" for="vol">50%</output></div></div>
        </div>
      </div>
    </section>

    <section class="step" data-step="3" aria-labelledby="h3" hidden>
      <div class="two">
        <div class="pv"><div class="screen" id="screen3"></div>
          <div class="under"><button type="button" class="btn" data-flip>Flip now</button><p>Hear your alert once more before you go.</p></div></div>
        <div class="hd"><div class="head"><h1 id="h3">Ready to depart</h1></div>
          <p class="lead">Your ticket is below. Depart and the board takes the whole screen; it rings with your alert when it flips.</p></div>
        <div class="ct">
          <div class="group"><label class="label" for="msg">Ticker message</label>
            <textarea class="field-in" id="msg" rows="2" maxlength="140" placeholder="Leave empty to keep the board's own message"></textarea>
            <span class="help"><span id="msgCount">0</span>/140 · scrolls on the amber LED strip</span></div>
          <div class="group"><label class="label" for="qr">Link for the QR code</label>
            <input class="field-in" id="qr" type="url" inputmode="url" autocomplete="url" placeholder="https://your-menu.example">
            <span class="help" id="qrHelp">Leave empty to keep the placeholder QR</span></div>
          <label class="check"><input type="checkbox" id="fsopt"> Open in full screen</label>
          <p class="keys">On the board: <kbd>S</kbd> settings · <kbd>F</kbd> full screen · <kbd>N</kbd> flip now</p>
        </div>
      </div>
    </section>
  </main>

  <footer class="ticket">
    <div class="strip" aria-label="Your ticket">
      <div class="field" data-f="board"><small>BOARD</small><span class="cells" data-field="board" data-n="12"></span></div>
      <div class="field" data-f="sound"><small>ALERT</small><span class="cells" data-field="sound" data-n="10"></span></div>
      <div class="field" data-f="when"><small>WHEN</small><span class="cells" data-field="when" data-n="10"></span></div>
      <div class="field" data-f="vol"><small>VOL</small><span class="cells" data-field="vol" data-n="4"></span></div>
      <span class="sr" id="ticketText" aria-live="polite"></span>
    </div>
    <div class="nav"><button type="button" class="btn" id="back">Back</button><button type="button" class="btn primary" id="next">Next</button></div>
  </footer>
</div>

<script>
(function () {
  var UPDATES = [340, 12340], LOOP = 24000;          // the board flips at 0.6 s and 12.6 s; the category starts 260 ms earlier
  var NAMES = {aurora:'AURORA CAFÉ', studionine:'STUDIO NINE', barberseven:'BARBER SEVEN', seahouse:'SEA HOUSE'};
  var SOUNDNAMES = {bell:'SOFT BELL', dingdong:'DING-DONG', shop:'SHOP BELL', chime:'CHIME', wood:'WOOD BLOCK', custom:'YOUR SOUND', none:'SILENT'};
  var S = {board:'aurora', sound:'bell', when:'every', volume:0.5, fs:true, msg:'', qr:''};
  try { Object.assign(S, JSON.parse(localStorage.getItem('departures-player') || '{}')); } catch (e) {}
  if (S.sound === 'custom') S.sound = 'bell';
  function save() { try { localStorage.setItem('departures-player', JSON.stringify(S)); } catch (e) {} }

  var ctx = null, custom = null, step = 1, departed = false, fired = false, alertsOn = false;
  window.__alerts = 0;
  function ac() { if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)(); if (ctx.state === 'suspended') ctx.resume(); return ctx; }
  function tone(c, out, f, t0, amp, decay) {
    var o = c.createOscillator(), g = c.createGain(); o.frequency.value = f;
    g.gain.setValueAtTime(0.0001, t0); g.gain.exponentialRampToValueAtTime(amp, t0 + 0.004);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + decay * 4); o.connect(g); g.connect(out); o.start(t0); o.stop(t0 + decay * 4 + 0.05);
  }
  function bell(c, out, f0, t0, amp) { [[0.5,.18,1],[1,1,1.3],[2,.32,.75],[2.76,.22,.45],[4.07,.07,.22]].forEach(function (p) { tone(c, out, f0 * p[0], t0, amp * p[1], p[2] / 2.2); }); }
  function play(name) {
    if (name === 'none') return;
    var c = ac(), out = c.createGain(), t = c.currentTime + 0.02; out.gain.value = S.volume * 0.6; out.connect(c.destination);
    if (name === 'bell') bell(c, out, 1046.5, t, .5);
    else if (name === 'dingdong') { bell(c, out, 659.25, t, .55); bell(c, out, 523.25, t + .45, .55); }
    else if (name === 'shop') { bell(c, out, 2093, t, .35); bell(c, out, 2637, t + .12, .3); }
    else if (name === 'chime') [523.25, 659.25, 783.99].forEach(function (f, i) { bell(c, out, f, t + i * .18, .4); });
    else if (name === 'wood') { tone(c, out, 880, t, .6, .03); tone(c, out, 3520, t, .12, .012); tone(c, out, 220, t, .25, .04); }
    else if (name === 'custom' && custom) { var s = c.createBufferSource(); s.buffer = custom; s.connect(out); s.start(t); }
  }
  function alertNow() {
    if (!alertsOn) return;
    if (departed && S.when === 'first' && fired) return;
    fired = true; window.__alerts++; play(S.sound);
  }

  // boards: only one live board at a time, moved where it is needed
  var pool = document.getElementById('pool');
  function boardEl(k) { return document.getElementById('b-' + k); }
  function player(k) { var s = boardEl(k).querySelector('svg'); return s && s.svgatorPlayer; }
  var hooked = {}, last = {}, expect = {};
  function hook(k) {
    var pl = player(k); if (!pl || hooked[k]) return;
    hooked[k] = true; last[k] = -1;
    pl.ready(function (p) {
      p.on('keyframe', function (off) {
        if (expect[k] != null) {                       // after a seek: ignore stale events until the timeline gets there
          if (Math.abs(off - expect[k]) > 400) return;
          last[k] = expect[k] - 1; expect[k] = null;
        }
        if (off < last[k] && last[k] - off > LOOP / 2) last[k] = -1;   // new pass of the loop
        UPDATES.forEach(function (u) { if (last[k] < u && off >= u && k === S.board) alertNow(); });
        last[k] = Math.max(last[k], off);
      });
    });
  }
  // ticker message and QR link, applied to the live board
  function tickerText(k) {
    var svg = boardEl(k).querySelector('svg'), found = null;
    svg.querySelectorAll('text').forEach(function (t) {
      var ff = t.getAttribute('font-family') || '';
      if (ff.indexOf('Doto') >= 0 && t.textContent.indexOf('ABCDEFGHIJ') !== 0) found = found || t;
    });
    return found;
  }
  function qrImage(k) {
    var best = null;
    boardEl(k).querySelectorAll('image').forEach(function (im) { if (+im.getAttribute('width') >= 120) best = best || im; });
    return best;
  }
  function qrData(url) {
    if (!window.qrcode) return null;
    var q = qrcode(0, 'M'); q.addData(url); q.make();
    var svg = q.createSvgTag({ cellSize: 8, margin: 2, scalable: true }).replace(/fill="white"/g, 'fill="#F6F2EA"').replace(/fill="black"/g, 'fill="#141518"');
    return 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svg)));
  }
  function applyOverrides(k) {
    var t = tickerText(k);
    if (t) {
      var span = t.querySelector('tspan') || t;
      if (span.dataset.orig == null) span.dataset.orig = span.textContent;
      span.textContent = S.msg ? S.msg.toUpperCase() : span.dataset.orig;
    }
    var im = qrImage(k), help = document.getElementById('qrHelp');
    if (im) {
      if (im.dataset.orig == null) im.dataset.orig = im.getAttribute('xlink:href') || im.getAttribute('href') || '';
      var src = im.dataset.orig;
      if (S.qr) {
        var url = /^https?:\\/\\//i.test(S.qr) ? S.qr : 'https://' + S.qr, d = qrData(url);
        if (d) { src = d; help.textContent = 'The QR now opens ' + url; } else help.textContent = 'The QR generator did not load. Check the connection and try again.';
      } else help.textContent = 'Leave empty to keep the placeholder QR';
      im.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', src); im.setAttribute('href', src);
    }
  }
  function stopAll() { Object.keys(NAMES).forEach(function (k) { var p = player(k); if (p) p.ready(function (q) { q.pause(); }); }); }
  function mount(container) {
    var el = boardEl(S.board);
    if (el.parentNode !== container) {
      Object.keys(NAMES).forEach(function (k) { if (k !== S.board) { var o = boardEl(k); if (o.parentNode !== pool) pool.appendChild(o); } });
      container.appendChild(el);
    }
    hook(S.board); applyOverrides(S.board);
    var p = player(S.board); if (p) p.ready(function (q) { q.play(); });
  }
  function flipNow() {
    var p = player(S.board); if (!p) return;
    p.ready(function (q) {
      var off = Math.max(0, last[S.board] || 0) % LOOP, next = off < 340 ? 340 : (off < 12340 ? 12340 : 340 + LOOP), target = (next - 280) % LOOP;
      expect[S.board] = target; q.seekTo(target); q.play();
    });
  }

  // ticket strip: each cell changes with a flap flip
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  function makeCell() {
    var c = document.createElement('span'); c.className = 'cell'; c.setAttribute('aria-hidden', 'true');
    c.innerHTML = '<span class="half t"><i></i></span><span class="half b"><i></i></span>'; c.dataset.ch = ' ';
    return c;
  }
  function flipCell(cell, ch) {
    var old = cell.dataset.ch || ' '; if (old === ch) return;
    cell.dataset.ch = ch;
    var t = cell.querySelector('.half.t i'), b = cell.querySelector('.half.b i'), show = function (x) { return x === ' ' ? '' : x; };
    if (reduce) { t.textContent = b.textContent = show(ch); return; }
    cell.querySelectorAll('.leaf').forEach(function (l) { l.remove(); });
    var lt = document.createElement('span'); lt.className = 'leaf t'; lt.innerHTML = '<i>' + show(old) + '</i>';
    var lb = document.createElement('span'); lb.className = 'leaf b'; lb.innerHTML = '<i>' + show(ch) + '</i>';
    t.textContent = show(ch);                       // the new letter is already under the falling leaf
    cell.appendChild(lt); cell.appendChild(lb);
    setTimeout(function () { b.textContent = show(ch); lt.remove(); lb.remove(); }, 300);
  }
  function setCells(field, text) {
    var box = document.querySelector('.cells[data-field="' + field + '"]'), n = +box.dataset.n, changed = false;
    text = (text || '').toUpperCase().slice(0, n);
    while (box.children.length < n) box.appendChild(makeCell());
    for (var i = 0; i < n; i++) (function (cell, ch, i) {
      ch = ch || ' '; if ((cell.dataset.ch || ' ') === ch) return; changed = true;
      setTimeout(function () { flipCell(cell, ch); }, i * 22);
    })(box.children[i], text[i], i);
    if (changed && box.dataset.init) {
      var f = box.closest('.field'); f.classList.add('changed'); clearTimeout(f._t); f._t = setTimeout(function () { f.classList.remove('changed'); }, 900);
    }
    box.dataset.init = '1';
  }
  function ticket() {
    setCells('board', NAMES[S.board]); setCells('sound', SOUNDNAMES[S.sound]);
    setCells('when', S.when === 'every' ? 'EVERY FLIP' : 'FIRST ONLY'); setCells('vol', Math.round(S.volume * 100) + '%');
    document.getElementById('ticketText').textContent = 'Ticket: ' + NAMES[S.board] + ', ' + SOUNDNAMES[S.sound] + ', ' + (S.when === 'every' ? 'every flip' : 'first flip only') + ', volume ' + Math.round(S.volume * 100) + '%';
  }

  function sync() {
    document.querySelectorAll('.card').forEach(function (c) { c.setAttribute('aria-checked', String(c.dataset.board === S.board)); });
    document.querySelectorAll('.opt').forEach(function (o) { o.setAttribute('aria-checked', String(o.dataset.sound === S.sound)); });
    document.querySelectorAll('[data-when]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.when === S.when)); });
    document.getElementById('vol').value = S.volume; document.getElementById('volout').textContent = Math.round(S.volume * 100) + '%';
    document.getElementById('fsopt').checked = !!S.fs;
    var m = document.getElementById('msg'); if (m.value !== S.msg) m.value = S.msg; document.getElementById('msgCount').textContent = S.msg.length;
    var q = document.getElementById('qr'); if (q.value !== S.qr) q.value = S.qr;
    ticket();
  }
  function go(n) {
    step = n;
    document.querySelectorAll('.step').forEach(function (s) { s.hidden = +s.dataset.step !== n; });
    document.querySelectorAll('[data-go]').forEach(function (b) {
      var k = +b.dataset.go; if (k === n) b.setAttribute('aria-current', 'step'); else b.removeAttribute('aria-current'); b.classList.toggle('done', k < n);
    });
    alertsOn = n >= 2;
    if (n === 1) mount(document.querySelector('.card[data-board="' + S.board + '"] .shot'));
    if (n === 2) mount(document.getElementById('screen2'));
    if (n === 3) mount(document.getElementById('screen3'));
    document.getElementById('back').disabled = n === 1;
    document.getElementById('next').textContent = n === 3 ? 'Depart' : 'Next';
    document.getElementById('main').scrollTop = 0;
  }
  var setupEl = document.getElementById('setup'), stage = document.getElementById('stage'), gear = document.getElementById('gear');
  function depart() {
    ac(); departed = true; fired = false; alertsOn = true;
    setupEl.hidden = true; stage.hidden = false; gear.hidden = false;
    mount(document.getElementById('holder'));
    var p = player(S.board); if (p) p.ready(function (q) { expect[S.board] = 0; q.restart(); });
    if (S.fs && document.documentElement.requestFullscreen) document.documentElement.requestFullscreen().then(function () {
      if (screen.orientation && screen.orientation.lock) return screen.orientation.lock('landscape');
    }).catch(function () {});
  }
  function openSetup() { setupEl.hidden = false; stage.hidden = true; gear.hidden = true; document.getElementById('close').hidden = false; departed = false; go(3); }
  function closeSetup() { if (document.getElementById('close').hidden) return; depart(); }

  document.querySelector('.cards').addEventListener('click', function (e) {
    var c = e.target.closest('.card'); if (!c) return; ac();
    var prev = S.board; S.board = c.dataset.board; save(); sync();
    mount(c.querySelector('.shot'));
  });
  document.getElementById('sounds').addEventListener('click', function (e) { var o = e.target.closest('.opt'); if (!o) return; S.sound = o.dataset.sound; save(); sync(); play(S.sound); });
  document.querySelectorAll('[data-when]').forEach(function (b) { b.addEventListener('click', function () { S.when = b.dataset.when; save(); sync(); }); });
  document.getElementById('vol').addEventListener('input', function (e) { S.volume = +e.target.value; save(); sync(); });
  document.getElementById('vol').addEventListener('change', function () { play(S.sound); });
  var ovT;
  function onOverride() { clearTimeout(ovT); ovT = setTimeout(function () { save(); applyOverrides(S.board); }, 250); }
  document.getElementById('msg').addEventListener('input', function (e) { S.msg = e.target.value.replace(/\\s+/g, ' ').slice(0, 140); document.getElementById('msgCount').textContent = S.msg.length; onOverride(); });
  document.getElementById('qr').addEventListener('input', function (e) { S.qr = e.target.value.trim(); onOverride(); });
  document.getElementById('fsopt').addEventListener('change', function (e) { S.fs = e.target.checked; save(); });
  document.getElementById('file').addEventListener('change', function (e) {
    var f = e.target.files[0]; if (!f) return; var label = document.getElementById('customName');
    f.arrayBuffer().then(function (b) { return ac().decodeAudioData(b); }).then(function (buf) {
      custom = buf; S.sound = 'custom'; sync(); label.textContent = f.name; play('custom');
      document.querySelectorAll('.opt').forEach(function (o) { o.setAttribute('aria-checked', 'false'); });
    }).catch(function () { label.textContent = 'That file could not be read. Try an mp3 or wav.'; });
  });
  document.querySelectorAll('[data-flip]').forEach(function (b) { b.addEventListener('click', function () { ac(); flipNow(); }); });
  document.querySelectorAll('[data-go]').forEach(function (b) { b.addEventListener('click', function () { ac(); go(+b.dataset.go); }); });
  document.getElementById('back').addEventListener('click', function () { if (step > 1) go(step - 1); });
  document.getElementById('next').addEventListener('click', function () { ac(); if (step < 3) go(step + 1); else depart(); });
  document.getElementById('close').addEventListener('click', closeSetup);
  gear.addEventListener('click', openSetup);
  document.addEventListener('keydown', function (e) {
    if (e.target.matches('input, textarea')) return;
    var k = e.key.toLowerCase();
    if (k === 's') { setupEl.hidden ? openSetup() : closeSetup(); }
    if (k === 'f' && document.documentElement.requestFullscreen) document.documentElement.requestFullscreen().catch(function () {});
    if (k === 'n') flipNow();
  });
  var t;
  document.addEventListener('pointermove', function () { document.body.classList.add('awake'); clearTimeout(t); t = setTimeout(function () { document.body.classList.remove('awake'); }, 2500); });
  sync(); go(1);
})();
</script>
'''
open(os.path.join(HERE, 'index.html'), 'w').write(html)
print('written', os.path.getsize(os.path.join(HERE, 'index.html')))
