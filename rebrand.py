#!/usr/bin/env python3
"""Rebrand Launch Card via the SVGator MCP, layer by layer, looking elements up by NAME.

usage: rebrand.py TEMPLATE_PROJECT_ID sets/harbor.json [--title "Launch Card · Harbor"] [--in-place]

1. duplicates the project (duplicate_project), unless --in-place
2. reads the structure (get_skeleton) and maps title -> id
3. changes texts, images, colors, underline and zoom point with edit_part
No project file downloaded or rewritten: only targeted edits to the named layers.
"""
import argparse, json, os, sys, time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, '.mcp'))
sys.path.insert(0, ROOT)
from svg import call
import gen

C = {'dim': '\033[2m', 'ok': '\033[38;5;114m', 'acc': '\033[38;5;216m', 'b': '\033[1m', 'r': '\033[0m'}


def log(msg, kind='ok'):
    print(f"{C[kind]}{msg}{C['r']}", flush=True)


def titles(tree, out):
    if isinstance(tree, dict):
        if tree.get('title'): out[tree['title']] = tree['id']
        for ch in tree.get('children', []) or []: titles(ch, out)
    return out


def short(v, n=34):
    s = v if isinstance(v, str) else json.dumps(v)
    if s.startswith('data:'): return s[:22] + '…'
    return (s[:n] + '…') if len(s) > n else s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('template'); ap.add_argument('set')
    ap.add_argument('--title'); ap.add_argument('--in-place', action='store_true')
    a = ap.parse_args()
    c = json.load(open(os.path.join(ROOT, a.set) if not os.path.isabs(a.set) else a.set))
    t_start = time.time()

    if a.in_place:
        pid = a.template
    else:
        title = a.title or f"Launch Card · {c['brand']}"
        log(f"duplicate_project  →  {title}", 'b')
        pid = call('duplicate_project', {"project_id": a.template, "title": title})['id']
    sk = call('get_skeleton', {"project_id": pid, "fields": "title"})
    ids = titles(sk['tree'], {})
    for d in sk.get('definitions', []): titles(d, ids)
    root_id = sk['tree']['id']
    log(f"get_skeleton       →  {len(ids)} named layers", 'dim')

    def edit(layer, sub, value, label=None):
        iid = ids.get(layer, layer)
        r = call('edit_part', {"project_id": pid, "item": f"#{iid}{sub}", "value": value})
        if r.get('result') != 'success' and 'element' not in r:
            raise SystemExit(f"edit failed on {layer}{sub}: {json.dumps(r)[:400]}")
        log(f"  ✓ {layer:<20} {C['dim']}{sub.split('/')[-1]:<10}{C['r']}{C['ok']} {short(label or value)}")

    log("text", 'acc')
    texts = {'brand-name': c['brand'], 'eyebrow-text': c['eyebrow'],
             'headline-line-1': c['headline'][0], 'headline-line-2': c['headline'][1],
             'subhead': c['subhead'], 'cta-label': c['cta'], 'window-url': c['url']}
    for i, f in enumerate(c['features'][:3]): texts[f'feature-{i+1}-label'] = f
    for layer, v in texts.items():
        edit(layer, '/properties/shape/text', v)

    log("images", 'acc')
    edit('logo', '/properties/shape/href', gen.data_uri(c['logo']), os.path.basename(c['logo']))
    edit('product-image', '/properties/shape/href', gen.data_uri(c['screenshot']), os.path.basename(c['screenshot']))

    log("color", "acc")
    acc, paper = gen.col(c['accent']), gen.col(c['paper'])
    edit('background', '/properties/fill/paint', paper, c['paper'])
    edit(root_id, '/properties/shape/bgColor', paper, c['paper'])
    for layer, sub in [('bg-glow', '/properties/fill/paint'), ('eyebrow-dot', '/properties/fill/paint'),
                       ('headline-underline', '/properties/stroke/paint'), ('cta-button', '/properties/fill/paint'),
                       ('cta-ripple', '/properties/stroke/paint')]:
        edit(layer, sub, acc, c['accent'])

    log("layout", 'acc')
    # underline: measure the key word with the real font and redraw the stroke
    l2 = c['headline'][1]
    word = c.get('underline_word') or l2.split()[-1]
    idx = max(l2.find(word), 0)
    pre, wd = gen.measure([{"t": l2[:idx], "f": gen.HEAD_FONT, "w": 700, "s": 104, "ls": -3.2},
                           {"t": word, "f": gen.HEAD_FONT, "w": 700, "s": 104, "ls": -3.2}])
    uw = wd - 4
    ulen = int(uw * 1.04 + 20)
    nodes = [{"x": 0, "y": 6, "type": "cusp", "mode": 0, "end": {"x": round(uw * 0.3, 1), "y": 10}},
             {"x": uw, "y": -4, "type": "cusp", "mode": 0, "start": {"x": round(uw * 0.7, 1), "y": 2}}]
    edit('headline-underline', '/properties/shape/path', nodes, f'under "{word}", {uw}px')
    edit('headline-underline', '/properties/transform/origin', gen.O(72 - 4 + pre + 2, 442 + 26), f'x {72 - 4 + pre + 2}')
    edit('headline-underline', '/properties/stroke/dashArray', [ulen], f'[{ulen}]')
    edit('headline-underline', '/animators/stroke/dashOffset/keys/0/value', ulen, f'draw from {ulen}')
    # zoom point = anchor point of product-image
    wx, iy, ww, ih = gen.WIN['x'], gen.WIN['iy'], gen.WIN['w'], gen.WIN['ih']
    fx, fy = c.get('zoom_focus', [0.5, 0.5])
    zx, zy = wx + ww * fx, iy + ih * fy
    edit('product-image', '/properties/transform/origin', gen.O(zx, zy), f'zoom focus {fx:.2f}, {fy:.2f}')
    edit('product-image', '/properties/transform/translate', {"x": round(wx - zx, 2), "y": round(iy - zy, 2)}, 'keeps image in place')

    meta = call('get_project', {"project_id": pid})
    log(f"done in {time.time() - t_start:.0f}s  →  {meta.get('editor_url')}", 'b')
    os.makedirs(os.path.join(ROOT, 'build'), exist_ok=True)
    json.dump({"id": pid, "editor_url": meta.get('editor_url')}, open(os.path.join(ROOT, 'build', f"rebrand-{c['brand'].lower()}.json"), 'w'))


if __name__ == '__main__':
    main()
