"""Shared base for the interactive Launch Cards (16:9 hero in SVGator).

Reuses the builders from gen.py (same SVGator data model) and adds:
gradients, rotations, shortcuts for animated channels, off-canvas how-to note,
project creation/replacement and the segment manifest for the Player API.
"""
import json, os, sys, argparse, math
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, '.mcp'))
import gen
from gen import col, bez, EASE, k, ch, O, S, tf, node, group, rect, circle, ellipse, text, image, path, clip_def, measure

W, H = 1920, 1080
EASE.update({
    'snap': bez(0.16, 1, 0.3, 1),       # sharp arrival
    'drop': bez(0.55, 0, 1, 0.45),      # fall (gravity)
    'over': bez(0.34, 1.56, 0.64, 1),   # strong overshoot
    'whip': bez(0.7, 0, 0.84, 0),       # violent acceleration on exit
    'step': {"type": "steps", "value": {"steps": 1, "jump": 0}},   # hard jump to the next keyframe
    'fling': bez(0.35, 0.15, 0.75, 0.6),  # throw: starts already at speed and barely accelerates
    'settle': bez(0.25, 1.22, 0.5, 1),    # settle with a small bounce
    'swipe': bez(0.2, 0.55, 0.35, 1),     # push away: starts fast and slows as it fades
})


def data_uri(p):
    return gen.data_uri(p if os.path.isabs(p) else os.path.relpath(os.path.join(ROOT, p), ROOT))


def lin_grad(stops, fx=0, fy=0, tx=0, ty=1):
    return {"type": "linear-gradient", "value": {"from": {"x": fx, "y": fy}, "to": {"x": tx, "y": ty},
            "stops": [{"color": col(c, a)["value"], "offset": o} for o, c, a in [(s + (1,))[:3] for s in stops]],
            "spread": "pad", "fixed": False}}


def rad_grad(stops, cx=0.5, cy=0.5, r=0.5):
    return {"type": "radial-gradient", "value": {"center": {"x": cx, "y": cy}, "radius": r,
            "stops": [{"color": col(c, a)["value"], "offset": o} for o, c, a in [(s + (1,))[:3] for s in stops]],
            "spread": "pad", "fixed": False}}


def mix(a, b, t):
    a, b = a.lstrip('#'), b.lstrip('#')
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]; cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return '#' + ''.join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ca, cb))


def opa(*pairs, e='soft'):
    """opacity channel from (t, v) pairs"""
    return ch(*[k(t, v, e if i < len(pairs) - 1 else 'lin') for i, (t, v) in enumerate(pairs)])


def chan(pairs, e='out', conv=lambda v: v):
    """generic channel: pairs = [(t, v, easing?)]"""
    keys = []
    for p in pairs:
        t, v = p[0], p[1]; ee = p[2] if len(p) > 2 else e
        keys.append(k(t, conv(v), ee))
    return ch(*keys)


def pos(pairs, e='out'):
    return chan(pairs, e, lambda v: O(*v))


def scl(pairs, e='out'):
    return chan(pairs, e, lambda v: S(v) if not isinstance(v, (tuple, list)) else {"x": v[0], "y": v[1]})


def rot(pairs, e='out'):
    return chan(pairs, e)


def at(cx, cy):
    """static transform with pivot at (cx, cy) and unchanged position"""
    return tf(cx, cy, -cx, -cy)


def set_pivot(n, cx, cy):
    n.setdefault("properties", {})["transform"] = at(cx, cy)
    return n


def mono(id_, title, s, x, y, size, fill, weight=500, anchor='start', ls=1.5, anim=None, opacity=None, font='Geist Mono'):
    return text(id_, title, s, x, y, font, size, weight, fill, anchor=anchor, ls=ls, anim=anim, opacity=opacity)


def rr_path(x, y, w, h, r):
    """rounded rectangle as path nodes (absolute coordinates)"""
    kr = r * 0.5523
    return [(x + r, y, "cusp"), (x + w - r, y, "cusp", None, (x + w - r + kr, y)),
            (x + w, y + r, "cusp", (x + w, y + r - kr), None), (x + w, y + h - r, "cusp", None, (x + w, y + h - r + kr)),
            (x + w - r, y + h, "cusp", (x + w - r + kr, y + h), None), (x + r, y + h, "cusp", None, (x + r - kr, y + h)),
            (x, y + h - r, "cusp", (x, y + h - r + kr), None), (x, y + r, "cusp", None, (x, y + r - kr)),
            (x + r, y, "cusp", (x + r - kr, y), None)]


def howto(lines, x=W + 80, y=60, wdt=600, card='#FFFDF9', line='#E4DDD1', ink='#17181C', muted='#5C5E66'):
    """off-canvas note: shows in the editor, never in exports"""
    kids, yy = [], y + 62
    for i, l in enumerate(["HOW TO MAKE IT YOURS"] + lines):
        head = i == 0
        if not head: yy += 40 if not l.startswith('   ') else 30
        kids.append(text(f"how-to-line-{i+1}", f"how-to-line-{i+1}", l, x + 36, yy, 'Geist', 20 if head else 22,
                         600 if head or not l.startswith('   ') else 400, col(ink if (head or not l.startswith('   ')) else muted), ls=2 if head else 0))
    h = yy - y + 48
    return group("how-to", "how-to (outside canvas, not exported)",
                 [rect("how-to-card", "how-to-card", x, y, wdt, h, 24, fill=col(card), stroke=col(line), sw=1.5), *kids], x + wdt / 2, y + h / 2)


def doc(kids, T, bg, iterations=0):
    return {"type": "svg", "id": "launch-hero",
            "animation": {"duration": T, "direction": 1, "iterations": iterations, "fill": 1, "alternate": False, "speed": 1},
            "properties": {"shape": {"position": {"x": 0, "y": 0}, "size": {"width": W, "height": H}, "bgColor": col(bg)}},
            "children": kids}


def cli(build, name):
    """usage: concept.py sets/x.json [--out f] [--create title | --replace pid [--title T]]
    Always writes the segment manifest to build/launch/<name>-meta.json."""
    ap = argparse.ArgumentParser()
    ap.add_argument('set'); ap.add_argument('--out'); ap.add_argument('--create'); ap.add_argument('--replace'); ap.add_argument('--title')
    a = ap.parse_args()
    sp = a.set if os.path.isabs(a.set) or os.path.exists(a.set) else os.path.join(HERE, a.set)
    c = json.load(open(sp))
    d, defs, meta = build(c)
    os.makedirs(os.path.join(ROOT, 'build', 'launch'), exist_ok=True)
    json.dump(meta, open(os.path.join(ROOT, 'build', 'launch', f'{name}-meta.json'), 'w'), indent=1)
    if a.out:
        json.dump({"document": d, "definitions": defs}, open(a.out, 'w'))
        print('written', a.out, os.path.getsize(a.out))
    if a.create or a.replace:
        from svg import call
        args = {"document": d, "definitions": defs}
        if a.create: args["title"] = a.create; r = call('create_project', args)
        else:
            args["project_id"] = a.replace
            if a.title: args["title"] = a.title
            r = call('replace_project', args)
        print(json.dumps({kk: r[kk] for kk in ('id', 'title', 'editor_url') if kk in r}))
    return d, defs, meta


def count(d):
    n = a = kf = 0
    def walk(x):
        nonlocal n, a, kf
        if isinstance(x, dict):
            if 'type' in x and 'id' in x and x.get('type') != 'svg': n += 1
            if 'animators' in x:
                a += 1
                for g in x['animators'].values():
                    for c_ in g.values(): kf += len(c_.get('keys', []))
            for v in x.get('children', []) or []: walk(v)
    walk(d)
    return n, a, kf
