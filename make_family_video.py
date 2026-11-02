#!/usr/bin/env python3
"""Rebuilds the Departures family video from the current SVGator projects."""
import json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.abspath(__file__)); os.chdir(ROOT)
sys.path.insert(0, '.mcp')
from svg import export_svg
FF = os.path.expanduser('~/.local/bin/ffmpeg')
ENV = f"source {os.path.expanduser('~/.android-toolchain/pw/env.sh')} >/dev/null 2>&1; export PATH=$HOME/.local/bin:$PATH; "
P = {'aurora': 'pi_2298b9724f0645a0a9cdab5ba6322226', 'studionove': 'pi_d38749ba302b4c58988d6cdb845e52c9', 'barberiasette': 'pi_32cec7439d5a45ac8a4615c5f13d282f',
     'lasttrain': 'pi_6d84d40491004074ab74a0a63be8c90b', 'ortovivo': 'pi_9b8e6e62a8f54738a13ea92568cc19c7', 'odeon': 'pi_2b8fd0771cb2468fa822c079ec7c5a3b',
     'farmacia': 'pi_e31cfbc9157a42d2b470377b4088e478', 'casamare': 'pi_5eb767e1552846bdb27af41d4198d504', 'casamare-chat': 'pi_394616018bc5429490edabb501fc8b70'}
def sh(cmd): return subprocess.run(['bash', '-c', ENV + cmd], capture_output=True, text=True)
os.makedirs('capture/fam', exist_ok=True)
for k, pid in P.items():
    open(f'build/v-{k}.svg', 'w').write(export_svg(pid)); print('export', k, flush=True)
# render in parallel (3 at a time)
jobs = []
for k in P:
    if k == 'casamare-chat':
        jobs.append(f"node video.mjs build/v-{k}.svg capture/fam/{k}-close.mp4 60 1 3600 0")
    else:
        jobs.append(f"node video.mjs build/v-{k}.svg capture/fam/{k}-close.mp4 60 1 2800 0 && node video.mjs build/v-{k}.svg capture/fam/{k}-grid.mp4 30 0.3229 4200 0")
for i in range(0, len(jobs), 3):
    procs = [subprocess.Popen(['bash', '-c', ENV + j], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for j in jobs[i:i + 3]]
    for p in procs: p.wait()
    print('render batch', i // 3 + 1, flush=True)
# chat insert
sh(f"{FF} -v error -y -sseof -0.05 -i capture/fam/casamare-close.mp4 -frames:v 1 video/cm-bg.png; {FF} -v error -y -ss 0 -i capture/fam/casamare-chat-close.mp4 -frames:v 1 video/cm-bg2.png")
rows = []
for l in re.sub(r'\x1b\[[0-9;]*m', '', open('build/casamare-chat.log').read()).splitlines():
    m = re.match(r'\s*✓ (\S+)\s+(\S+)\s+(.*)', l)
    if m: rows.append([m.group(1), m.group(3).strip()])
secs = re.search(r'edits in (\d+)s', open('build/casamare-chat.log').read())
cfg = {"rows": rows, "visible": 3, "listStart": 1250, "step": 300, "dur": 4300}
s = open('video/board-chat.html').read().replace('CONFIG', json.dumps(cfg, ensure_ascii=False)).replace('TITLE', 'Sea House') \
    .replace('MSG', 'New guests tomorrow: the Müller family. Check-out is Sunday at 11:00.').replace('DONE1', f'{len(rows)} edits') \
    .replace('DONE2', f"in {secs.group(1) if secs else '10'} s, live at the next flip").replace('"BG"', '"cm-bg.png"').replace('"BG2"', '"cm-bg2.png"').replace('Menu board · ', 'Welcome board · ')
open('video/cm-chat.built.html', 'w').write(s)
print(sh("node htmlseq.mjs video/cm-chat.built.html video/cm-chat.mp4 4300 60 1920 1080").stdout.strip().splitlines()[-1:])
# grid
order = ['aurora', 'lasttrain', 'ortovivo', 'studionove', None, 'odeon', 'barberiasette', 'farmacia', 'casamare']
inputs = ['-f', 'lavfi', '-i', 'color=c=0x0B0C0D:s=1920x1080:r=60:d=4.2']; fc = []; last = '0:v'; idx = 1
for i, n in enumerate(order):
    c, r = i % 3, i // 3; x = 20 + c * 630; y = 8 + r * 358
    if n is None:
        inputs += ['-loop', '1', '-framerate', '60', '-t', '4.2', '-i', 'video/fam-tile.png']; fc.append(f'[{idx}:v]format=rgba[t{idx}]')
    else:
        inputs += ['-i', f'capture/fam/{n}-grid.mp4']
        fc.append(f'[{idx}:v]fps=60,tpad=start_mode=clone:start_duration={round(0.11 * i, 2)},trim=0:4.2,setpts=PTS-STARTPTS,scale=620:348[t{idx}]')
    fc.append(f'[{last}][t{idx}]overlay={x}:{y}[o{idx}]'); last = f'o{idx}'; idx += 1
fc.append(f'[{last}]trim=0:4.2,format=yuv420p[out]')
subprocess.run([FF, '-y', '-v', 'error'] + inputs + ['-filter_complex', ';'.join(fc), '-map', '[out]', '-c:v', 'libx264', '-crf', '16', '-r', '60', 'video/fam-grid.mp4'])
# ending
thumbs = [('aurora', 980, 282), ('studionove', 1440, 282), ('barberiasette', 980, 550), ('casamare-chat', 1440, 550)]
inputs = ['-loop', '1', '-framerate', '60', '-t', '5', '-i', 'video/fam-end-bg.png']; fc = []; last = '0:v'
for i, (n, x, y) in enumerate(thumbs):
    inputs += ['-i', f'capture/fam/{n}-close.mp4']
    fc.append(f'[{i + 1}:v]trim=0:2.8,setpts=PTS-STARTPTS,fps=60,scale=440:248:flags=lanczos,tpad=start_mode=clone:start_duration={round(0.15 * i, 2)}:stop_mode=clone:stop_duration=3[t{i}]')
    fc.append(f'[{last}][t{i}]overlay={x}:{y}[o{i}]'); last = f'o{i}'
inputs += ['-loop', '1', '-framerate', '60', '-t', '5', '-i', 'video/fam-end-fg.png']
fc.append(f'[{last}][5:v]overlay=0:0,trim=0:5,setpts=PTS-STARTPTS,format=yuv420p[out]')
subprocess.run([FF, '-y', '-v', 'error'] + inputs + ['-filter_complex', ';'.join(fc), '-map', '[out]', '-c:v', 'libx264', '-crf', '16', '-r', '60', 'video/fam-end.mp4'])
# final edit
segs = [('video/fam-grid.mp4', 4.2)] + [(f'capture/fam/{n}-close.mp4', 2.8) for n in ['aurora', 'ortovivo', 'studionove', 'odeon', 'barberiasette', 'farmacia', 'casamare']] + \
       [('video/cm-chat.mp4', 4.3), ('capture/fam/casamare-chat-close.mp4', 3.6), ('video/fam-end.mp4', 5.0)]
fades = [0.3, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.25, 0.25, 0.5]
inputs = []; fc = []
for i, (f, d) in enumerate(segs):
    inputs += ['-i', f]; fc.append(f'[{i}:v]trim=0:{d},setpts=PTS-STARTPTS,format=yuv420p,fps=60,settb=1/60[s{i}]')
cur = 's0'; acc = segs[0][1]
for i in range(1, len(segs)):
    off = acc - fades[i - 1]; fc.append(f'[{cur}][s{i}]xfade=transition=fade:duration={fades[i - 1]}:offset={off:.3f},settb=1/60[x{i}]'); cur = f'x{i}'; acc = off + segs[i][1]
r = subprocess.run([FF, '-y', '-v', 'error'] + inputs + ['-filter_complex', ';'.join(fc), '-map', f'[{cur}]', '-c:v', 'libx264', '-crf', '17', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', 'video/departures-family.mp4'], capture_output=True, text=True)
print(r.stderr[-400:] or 'family ok', round(acc, 2))
