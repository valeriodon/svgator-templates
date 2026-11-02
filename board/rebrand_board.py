#!/usr/bin/env python3
"""Rebrand the Departures board via the SVGator MCP, by layer name.

usage:
  rebrand_board.py TEMPLATE_ID board/sets/lasttrain.json [--title "..."]     duplicate and change everything
  rebrand_board.py PROJECT_ID --in-place --edit page-b-row-3-status="SOLD OUT" --edit ...   targeted edits
"""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, '.mcp')); sys.path.insert(0, HERE)
from svg import call
import gen, board

C = {'dim': '\033[2m', 'ok': '\033[38;5;114m', 'acc': '\033[38;5;216m', 'b': '\033[1m', 'r': '\033[0m'}
def log(m, kind='ok'): print(f"{C[kind]}{m}{C['r']}", flush=True)


def titles(tree, out):
    if isinstance(tree, dict):
        t = tree.get('title')
        if t:
            out[t] = tree['id']
            out.setdefault(t.split(' (')[0], tree['id'])
        for c in tree.get('children', []) or []: titles(c, out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project'); ap.add_argument('set', nargs='?')
    ap.add_argument('--title'); ap.add_argument('--in-place', action='store_true')
    ap.add_argument('--target', help='resume on an already duplicated project')
    ap.add_argument('--edit', action='append', default=[], help='layer=text')
    a = ap.parse_args()
    t0 = time.time()
    pid = a.project
    if not a.in_place:
        c = json.load(open(a.set if os.path.isabs(a.set) else os.path.join(ROOT, a.set)))
        title = a.title or f"Departures · {c['brand']}"
        if a.target:
            pid = a.target
        else:
            log(f"duplicate_project  →  {title}", 'b')
            pid = call('duplicate_project', {"project_id": a.project, "title": title})['id']
    sk = call('get_skeleton', {"project_id": pid, "fields": "title"})
    ids = titles(sk['tree'], {})
    log(f"get_skeleton       →  {len(ids)} named layers", 'dim')
    n = 0

    def edit(layer, sub, value, label=None):
        nonlocal n
        r = call('edit_part', {"project_id": pid, "item": f"#{ids.get(layer, layer)}{sub}", "value": value})
        if r.get('result') != 'success':
            raise SystemExit(f"edit failed on {layer}{sub}: {json.dumps(r)[:300]}")
        n += 1
        s = label if label is not None else (value if isinstance(value, str) else json.dumps(value))
        log(f"  ✓ {layer:<22} {C['dim']}{sub.split('/')[-1]:<8}{C['r']}{C['ok']} {s[:40]}")

    if a.in_place:
        log("edits", 'acc')
        for e in a.edit:
            layer, v = e.split('=', 1)
            edit(layer, '/properties/shape/text', v)
    else:
        log("brand", 'acc')
        for layer, key in [('brand-name', 'brand'), ('brand-subline', 'subline'), ('footer-left', 'footer_left'), ('footer-right', 'footer_right')]:
            edit(layer, '/properties/shape/text', c[key])
        edit('logo', '/properties/shape/href', gen.data_uri(c['logo']), os.path.basename(c['logo']))
        edit('qr-code', '/properties/shape/href', gen.data_uri(c['qr']), os.path.basename(c['qr']))
        for layer in ('info-tab', 'live-dot'):
            edit(layer, '/properties/fill/paint', gen.col(c['accent']), c['accent'])
        layout = c.get('layout', 'list')
        L = board.LAYOUTS[layout]
        board.configure(layout)
        cols = L['cols']
        log("labels", 'acc')
        hl = c.get('header_label', L['header'])
        edit('departures-label', '/properties/shape/text', hl)
        hl_w = gen.measure([{"t": hl, "f": gen.UI_FONT, "w": 600, "s": 18, "ls": 3.5}])[0]
        edit('live-dot', '/properties/transform/origin', gen.O(board.ROW_R - hl_w - 16, 92 - 6), 'next to the label')
        for cc, lab in zip(cols, c.get('labels', L['labels'])):
            edit(f"label-{cc['key']}", '/properties/shape/text', lab)
        log("board", 'acc')
        for pi_, pg in enumerate('ab'):
            page = c['pages'][pi_]
            edit(f'page-{pg}-category', '/properties/shape/text', page['category'])
            for r, row in enumerate(page['rows'][:6]):
                vals = (row + [""] * len(cols))[:len(cols)]
                for cc, v in zip(cols, vals):
                    edit(f"page-{pg}-row-{r+1}-{cc['key']}", '/properties/shape/text', v, v or '(blank)')
        log("ticker", 'acc')
        edit('ticker-text', '/properties/shape/text', c['ticker'])
        if c.get('info_label'): edit('info-label', '/properties/shape/text', c['info_label'])
        if c.get('qr_url'):
            import segno, tempfile
            q = segno.make(c['qr_url'], error='m'); f = tempfile.NamedTemporaryFile(suffix='.png', delete=False).name
            q.save(f, scale=12, border=2, dark='#141518', light='#F6F2EA')
            edit('qr-code', '/properties/shape/href', gen.data_uri(f), c['qr_url'])

    meta = call('get_project', {"project_id": pid})
    log(f"{n} edits in {time.time() - t0:.0f}s  →  {meta.get('editor_url')}", 'b')
    tag = 'edit' if a.in_place else os.path.splitext(os.path.basename(a.set))[0]
    os.makedirs(os.path.join(ROOT, 'build'), exist_ok=True)
    json.dump({"id": pid, "editor_url": meta.get('editor_url')}, open(os.path.join(ROOT, 'build', f"board-{tag}.json"), 'w'))


if __name__ == '__main__':
    main()
