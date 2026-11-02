#!/usr/bin/env python3
"""Edits the Launch Heroes demo video: five clips with cursor + end card, short crossfades."""
import subprocess, os
D = os.path.dirname(os.path.abspath(__file__))
FF = os.path.expanduser('~/.local/bin/ffmpeg')
clips = [('ignition-lumen.mp4', 10.4), ('box-lumen.mp4', 8.2), ('pass-lumen.mp4', 8.6), ('deck-lumen.mp4', 7.2), ('ignition-harbor.mp4', 6.6)]
END = 4.5
inputs, fc = [], []
for i, (f, d) in enumerate(clips):
    inputs += ['-i', os.path.join(D, f)]
    fc.append(f'[{i}:v]trim=0:{d},setpts=PTS-STARTPTS,fps=30,format=yuv420p,settb=1/30[s{i}]')
n = len(clips)
inputs += ['-loop', '1', '-framerate', '30', '-t', str(END), '-i', os.path.join(D, 'end.png')]
fc.append(f'[{n}:v]trim=0:{END},setpts=PTS-STARTPTS,fps=30,format=yuv420p,settb=1/30[s{n}]')
durs = [d for _, d in clips] + [END]
X = 0.35
cur, acc = 's0', durs[0]
for i in range(1, len(durs)):
    off = acc - X
    fc.append(f'[{cur}][s{i}]xfade=transition=fade:duration={X}:offset={off:.3f},settb=1/30[x{i}]')
    cur, acc = f'x{i}', off + durs[i]
out = os.path.join(D, 'launch-heroes-demo.mp4')
r = subprocess.run([FF, '-y', '-v', 'error'] + inputs + ['-filter_complex', ';'.join(fc), '-map', f'[{cur}]', '-c:v', 'libx264', '-crf', '18', '-preset', 'slow',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], capture_output=True, text=True)
print(r.stderr[-500:] or 'ok', round(acc, 2), os.path.getsize(out) if os.path.exists(out) else 0)
