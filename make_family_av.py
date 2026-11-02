#!/usr/bin/env python3
"""Adds captions and audio (synced flap clacks, chime, chat sounds)
to the Departures family video. Requires make_family_video.py to have already produced the segments."""
import json, os, subprocess, sys
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__)); os.chdir(ROOT)
sys.path.insert(0, 'board')
import board
FF = os.path.expanduser('~/.local/bin/ffmpeg')
ENV = f"source {os.path.expanduser('~/.android-toolchain/pw/env.sh')} >/dev/null 2>&1; export PATH=$HOME/.local/bin:$PATH; "
SR = 48000
rng = np.random.default_rng(7)

LAYOUT = {'aurora': 'list', 'lasttrain': 'list', 'ortovivo': 'list', 'casamare': 'list', 'casamare-chat': 'list',
          'studionove': 'schedule', 'odeon': 'schedule', 'barberiasette': 'queue', 'farmacia': 'queue'}
CAPTIONS = {'aurora': 'Café menu · list board', 'ortovivo': 'Greengrocer prices · list board', 'studionove': 'Gym classes · schedule board',
            'odeon': 'Cinema showtimes · schedule board', 'barberiasette': 'Barber queue · queue board', 'farmacia': 'Pharmacy tickets · queue board',
            'casamare': 'Holiday rental welcome · list board', 'casamare-chat': 'Updated by chat, live at the next flip'}
CLOSE = ['aurora', 'ortovivo', 'studionove', 'odeon', 'barberiasette', 'farmacia', 'casamare']
SEGS = [('grid', 4.2)] + [(n, 2.8) for n in CLOSE] + [('chat', 4.3), ('casamare-chat', 3.6), ('end', 5.0)]
FADES = [0.3, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.25, 0.25, 0.5]


def sh(cmd):
    r = subprocess.run(['bash', '-c', ENV + cmd], capture_output=True, text=True)
    if r.returncode: print(r.stderr[-600:])
    return r


# ---------- captions ----------
def caption_png(name, text):
    html = f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@600&display=block" rel="stylesheet">
<style>*{{margin:0;padding:0}}body{{width:1920px;height:1080px;background:transparent;position:relative;font-family:Geist,sans-serif;-webkit-font-smoothing:antialiased}}
.p{{position:absolute;left:50%;top:1000px;transform:translate(-50%,-50%);display:flex;align-items:center;gap:14px;padding:13px 26px 13px 22px;border-radius:99px;
background:rgba(10,11,13,.92);border:1.5px solid #34373D;color:#F1ECE2;font-size:27px;font-weight:600;letter-spacing:.2px;white-space:nowrap}}
.p i{{width:11px;height:11px;border-radius:50%;background:#F2B33D;display:block}}</style></head>
<body><div class="p"><i></i>{text}</div></body></html>'''
    open(f'video/cap-{name}.html', 'w').write(html)
    sh(f"node render.mjs video/cap-{name}.html video/cap-{name}.png 1920 1080 1 transparent")


def captioned(name, dur):
    src = f'capture/fam/{name}-close.mp4'
    out = f'video/capd-{name}.mp4'
    fc = (f"[1:v]format=rgba,fade=in:st=0.25:d=0.3:alpha=1,fade=out:st={dur - 0.45:.2f}:d=0.3:alpha=1[c];"
          f"[0:v]trim=0:{dur},setpts=PTS-STARTPTS[v];[v][c]overlay=0:0:shortest=1,format=yuv420p[o]")
    subprocess.run([FF, '-y', '-v', 'error', '-i', src, '-loop', '1', '-framerate', '60', '-t', str(dur), '-i', f'video/cap-{name}.png',
                    '-filter_complex', fc, '-map', '[o]', '-c:v', 'libx264', '-crf', '16', '-r', '60', out])
    return out


# ---------- sounds ----------
def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def clack(level=1.0, bright=1.0):
    """a plastic flap striking: a few damped midrange resonances + a small body thud"""
    n = int(0.06 * SR); t = np.arange(n) / SR
    s = 0.55 * np.sin(2 * np.pi * rng.uniform(150, 230) * t) * env_exp(n, 0.018)
    for f0, f1, a, d in [(800, 1100, 1.0, 0.009), (1500, 1900, 0.55, 0.006), (2400, 2900, 0.4, 0.004), (3500, 4200, 0.18, 0.0025)]:
        s += a * np.sin(2 * np.pi * rng.uniform(f0, f1) * bright * t + rng.uniform(0, 6.28)) * env_exp(n, d)
    att = rng.standard_normal(n) * env_exp(n, 0.0008) * 0.25
    att = np.convolve(att, np.ones(5) / 5, mode='same')
    return (s + att) * np.minimum(1, t / 0.0004) * level * 0.5


def rattle(n_cells, level):
    """a strip of flaps turning over: 3-5 regular hits, tr-r-r"""
    k = 3 + min(2, n_cells // 8)
    n = int(0.12 * SR)
    out = np.zeros(n)
    t = 0.0
    for i in range(k):
        c = clack(rng.uniform(0.7, 1.0) * (1 - 0.12 * i), rng.uniform(0.95, 1.05))
        st = int(t * SR)
        out[st:st + len(c)] += c[:n - st]
        t += rng.uniform(0.011, 0.016)
    return out * level


def lowpass(x, fc=7000, taps=63):
    m = np.arange(taps) - (taps - 1) / 2
    h = np.sinc(2 * fc / SR * m) * np.hamming(taps); h /= h.sum()
    return np.stack([np.convolve(x[:, c], h, mode='same') for c in range(x.shape[1])], axis=1)


def room(x, wet=0.12):
    n = int(0.16 * SR)
    ir = rng.standard_normal(n) * env_exp(n, 0.045)
    ir = np.convolve(ir, np.ones(12) / 12, mode='same'); ir /= np.sqrt((ir ** 2).sum())
    from numpy.fft import rfft, irfft
    L = x.shape[0] + n
    N = 1 << (L - 1).bit_length()
    H = rfft(ir, N)
    y = np.stack([irfft(rfft(x[:, c], N) * H, N)[:x.shape[0]] for c in range(x.shape[1])], axis=1)
    return x + y * wet


def chime(freq, dur=1.3):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * freq * k * t) * env_exp(n, d) for k, a, d in [(1, 1.0, 0.55), (2, 0.35, 0.3), (3, 0.12, 0.18), (4.2, 0.06, 0.08)])
    att = np.minimum(1, t / 0.006)
    return s * att


def tick(freq=1800, dur=0.03, level=0.25):
    n = int(dur * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * t) * env_exp(n, dur / 4) * level


def pop(level=0.35):
    n = int(0.09 * SR); t = np.arange(n) / SR
    f = 520 + 900 * np.exp(-t / 0.02)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.025) * level


def place(buf, s, t, pan=0.0):
    i = int(t * SR)
    if i >= buf.shape[0]: return
    s = s[:buf.shape[0] - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(s), 0] += s * l
    buf[i:i + len(s), 1] += s * r


def board_events(layout):
    board.configure(layout)
    ev = []
    for u in board.U:
        cx = board.ROW_R - (board.CAT_N * board.P) / 2
        ev.append((u - 260, board.CAT_N, cx))
        for r in range(6):
            for cc in board.COLS:
                x = board.XS[cc['key']] + cc['n'] * board.P / 2
                ev.append((board.cell_time(u, board.XS[cc['key']], r * board.RS), cc['n'], x))
    return ev


def add_board(buf, name, t0, dur, level, pan_center=None, offset=0.0):
    for tb, n, x in board_events(LAYOUT[name]):
        tb = tb / 1000 + offset
        if tb < 0 or tb > dur - 0.05: continue
        pan = (x / 1920 * 2 - 1) * 0.8 if pan_center is None else pan_center + (x / 1920 - 0.5) * 0.3
        for f in range(board.NFLIPS):
            place(buf, rattle(n, level), t0 + tb + f * (board.FLIP + 1) / 1000, pan)


def main():
    for k, txt in CAPTIONS.items(): caption_png(k, txt)
    caps = {k: captioned(k, 2.8 if k != 'casamare-chat' else 3.6) for k in CAPTIONS}
    # segment start times in the edit
    starts, acc = [0.0], SEGS[0][1]
    for i in range(1, len(SEGS)):
        starts.append(acc - FADES[i - 1]); acc = starts[-1] + SEGS[i][1]
    total = acc
    buf = np.zeros((int((total + 0.5) * SR), 2))
    # opening chime
    place(buf, chime(659.25) * 0.32, 0.05, -0.1)
    place(buf, chime(523.25) * 0.32, 0.55, 0.1)
    for (name, dur), t0 in zip(SEGS, starts):
        if name == 'grid':
            order = ['aurora', 'lasttrain', 'ortovivo', 'studionove', None, 'odeon', 'barberiasette', 'farmacia', 'casamare']
            for i, n in enumerate(order):
                if n: add_board(buf, n, t0, dur, 0.33, pan_center=[-0.6, 0, 0.6][i % 3], offset=0.11 * i)
        elif name == 'chat':
            place(buf, pop(0.35), t0 + 0.45)
            for i in range(3): place(buf, tick(1700 + 120 * i, 0.035, 0.22), t0 + 1.25 + i * 0.3)
            place(buf, tick(2350, 0.08, 0.2), t0 + 1.25 + 3 * 0.3 + 0.15); place(buf, tick(3130, 0.1, 0.16), t0 + 1.25 + 3 * 0.3 + 0.24)
        elif name == 'end':
            for i, n in enumerate(['aurora', 'studionove', 'barberiasette', 'casamare-chat']):
                add_board(buf, n, t0, 2.8, 0.18, pan_center=0.35, offset=0.15 * i)
        else:
            add_board(buf, name, t0, dur, 0.7)
    # barely audible room tone
    nz = rng.standard_normal(buf.shape)
    for ch in range(2):
        nz[:, ch] = np.convolve(nz[:, ch], np.ones(60) / 60, mode='same')
    buf += nz * 0.004
    buf = room(lowpass(buf), 0.14)
    peak = np.max(np.abs(buf)); buf = buf / peak * 0.89
    import wave
    w = wave.open('video/family-audio.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((buf * 32767).astype('<i2').tobytes()); w.close()
    # re-edit the video with the captions
    files = {'grid': 'video/fam-grid.mp4', 'chat': 'video/cm-chat.mp4', 'end': 'video/fam-end.mp4'}
    inputs, fc = [], []
    for i, (name, d) in enumerate(SEGS):
        inputs += ['-i', files.get(name) or caps[name]]
        fc.append(f'[{i}:v]trim=0:{d},setpts=PTS-STARTPTS,format=yuv420p,fps=60,settb=1/60[s{i}]')
    cur, acc = 's0', SEGS[0][1]
    for i in range(1, len(SEGS)):
        off = acc - FADES[i - 1]
        fc.append(f'[{cur}][s{i}]xfade=transition=fade:duration={FADES[i - 1]}:offset={off:.3f},settb=1/60[x{i}]'); cur = f'x{i}'; acc = off + SEGS[i][1]
    inputs += ['-i', 'video/family-audio.wav']
    fc.append(f'[{len(SEGS)}:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[a]')
    r = subprocess.run([FF, '-y', '-v', 'error'] + inputs + ['-filter_complex', ';'.join(fc), '-map', f'[{cur}]', '-map', '[a]',
                        '-c:v', 'libx264', '-crf', '17', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                        '-shortest', '-movflags', '+faststart', 'video/departures-family-av.mp4'], capture_output=True, text=True)
    print(r.stderr[-500:] or 'ok', round(total, 2))


if __name__ == '__main__':
    main()
