#!/usr/bin/env python3
"""Departures family video with voiceover: one soft bell at the first update, captions.
Reuses the segments and captioned videos produced by make_family_av.py.  usage: make_family_vo.py [VOICE]"""
import os, sys, subprocess, wave, json
import numpy as np, scipy.signal as ss
ROOT = os.path.dirname(os.path.abspath(__file__)); os.chdir(ROOT)
import make_family_av as av
VOICE = sys.argv[1] if len(sys.argv) > 1 else 'Achird'
FF = av.FF; SR = av.SR
CLOSE = av.CLOSE
SEGS = [('grid', 4.2)] + [(n, 2.8) for n in CLOSE] + [('chat', 4.3), ('casamare-chat', 4.4), ('end', 5.4)]
FADES = av.FADES
TARGET = [0.4, 5.0, 11.6, 14.8, 19.9, 22.4, 28.1, 30.6]   # desired start of each voiceover line


def load(path):
    w = wave.open(path); sr = w.getframerate()
    a = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float64) / 32768
    return ss.resample_poly(a, SR, sr) if sr != SR else a


def bell(level=0.32):
    """soft bell: inharmonic partials of a small bell, gentle attack, long tail"""
    n = int(2.2 * SR); t = np.arange(n) / SR
    f0 = 1046.5
    s = np.zeros(n)
    for ratio, a, d in [(0.5, 0.18, 1.0), (1.0, 1.0, 1.3), (2.0, 0.32, 0.75), (2.76, 0.22, 0.45), (4.07, 0.07, 0.22)]:
        s += a * np.sin(2 * np.pi * f0 * ratio * t + ratio) * np.exp(-t / d)
    s *= np.minimum(1, t / 0.004)
    return s / np.max(np.abs(s)) * level


def main():
    starts, acc = [0.0], SEGS[0][1]
    for i in range(1, len(SEGS)):
        starts.append(acc - FADES[i - 1]); acc = starts[-1] + SEGS[i][1]
    total = acc
    st = dict(zip([s[0] for s in SEGS], starts))
    fx = np.zeros((int((total + 0.5) * SR), 2))
    av.place(fx, bell(), st['aurora'] + 0.45, 0.0)              # a single bell, at the first close-up update
    fx = av.room(av.lowpass(fx), 0.14)
    vo = np.zeros(fx.shape[0])
    t_prev_end = 0
    placed = []
    for i, t in enumerate(TARGET):
        a = load(f'vo/{VOICE}/line{i + 1}.wav')
        t = max(t, t_prev_end + 0.2)
        j = int(t * SR); a = a[:len(vo) - j]
        vo[j:j + len(a)] += a
        t_prev_end = t + len(a) / SR
        placed.append((i + 1, round(t, 2), round(t_prev_end, 2)))
    print('lines', placed, 'video', round(total, 2))
    # voice in the center, effects underneath
    vo_n = vo / (np.max(np.abs(vo)) + 1e-9) * 0.9
    fx_n = fx / (np.max(np.abs(fx)) + 1e-9) * 0.09
    mix = fx_n + np.stack([vo_n, vo_n], axis=1)
    mix = mix / np.max(np.abs(mix)) * 0.89
    w = wave.open('video/family-audio-vo.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes()); w.close()
    files = {'grid': 'video/fam-grid.mp4', 'chat': 'video/cm-chat.mp4', 'end': 'video/fam-end.mp4'}
    inputs, fc = [], []
    for i, (name, d) in enumerate(SEGS):
        src = files.get(name) or f'video/capd-{name}.mp4'
        inputs += ['-i', src]
        pad = ''
        if name == 'casamare-chat': pad = ',tpad=stop_mode=clone:stop_duration=0.9'
        if name == 'end': pad = ',tpad=stop_mode=clone:stop_duration=0.5'
        fc.append(f'[{i}:v]setpts=PTS-STARTPTS,format=yuv420p,fps=60{pad},trim=0:{d},setpts=PTS-STARTPTS,fps=60,settb=1/60[s{i}]')
    cur, acc = 's0', SEGS[0][1]
    for i in range(1, len(SEGS)):
        off = acc - FADES[i - 1]
        fc.append(f'[{cur}][s{i}]xfade=transition=fade:duration={FADES[i - 1]}:offset={off:.3f},settb=1/60[x{i}]'); cur = f'x{i}'; acc = off + SEGS[i][1]
    inputs += ['-i', 'video/family-audio-vo.wav']
    fc.append(f'[{len(SEGS)}:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[a]')
    r = subprocess.run([FF, '-y', '-v', 'error'] + inputs + ['-filter_complex', ';'.join(fc), '-map', f'[{cur}]', '-map', '[a]',
                        '-c:v', 'libx264', '-crf', '17', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                        '-shortest', '-movflags', '+faststart', f'video/departures-family-vo.mp4'], capture_output=True, text=True)
    print(r.stderr[:1500] or 'ok')


if __name__ == '__main__':
    main()
