#!/usr/bin/env python3
"""Rebrand a Launch Hero via the SVGator MCP, layer by layer, looking up elements by NAME.

usage: rebrand.py CONCEPT TEMPLATE_PID sets/harbor.json [--base sets/lumen.json] [--title T] [--target PID] [--dry]

Builds the template document with the starting set (lumen) and with the new set, compares layers
with the same title and sends to edit_part only what changes: texts, images, colors (gradients too)
and the animated channels that depend on color. Duplicates the project, unless --target is given.
"""
import argparse, importlib, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(HERE), '.mcp'))
from svg import call

C = {'dim': '\033[2m', 'ok': '\033[38;5;114m', 'acc': '\033[38;5;216m', 'b': '\033[1m', 'r': '\033[0m'}
def log(m, k='ok'): print(f"{C[k]}{m}{C['r']}", flush=True)


def index(doc, defs):
    out = {}
    def walk(x):
        if isinstance(x, dict):
            if x.get('title'): out[x['title']] = x
            for c in x.get('children', []) or []: walk(c)
    walk(doc); [walk(d) for d in defs]
    return out


PROPS = [('shape', 'text'), ('shape', 'href'), ('fill', 'paint'), ('stroke', 'paint'), ('shape', 'bgColor')]


def diffs(a, b):
    out = []
    pa, pb = a.get('properties', {}), b.get('properties', {})
    for g, k in PROPS:
        va, vb = pa.get(g, {}).get(k), pb.get(g, {}).get(k)
        if vb is not None and va != vb: out.append((f"/properties/{g}/{k}", vb))
    aa, ab = a.get('animators', {}), b.get('animators', {})
    for g, chans in ab.items():
        for k, v in chans.items():
            if aa.get(g, {}).get(k) != v: out.append((f"/animators/{g}/{k}", v))
    return out


def short(v):
    if isinstance(v, str):
        return (v[:24] + '…') if v.startswith('data:') else (v if len(v) < 40 else v[:38] + '…')
    if isinstance(v, dict) and v.get('type') == 'color':
        c = v['value']; return f"#{c['r']:02X}{c['g']:02X}{c['b']:02X}"
    if isinstance(v, dict) and 'type' in v: return v['type']
    if isinstance(v, dict) and 'keys' in v: return f"{len(v['keys'])} keyframes"
    return json.dumps(v)[:40]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('concept'); ap.add_argument('template'); ap.add_argument('set')
    ap.add_argument('--base', default='sets/lumen.json'); ap.add_argument('--title'); ap.add_argument('--target'); ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    mod = importlib.import_module(a.concept)
    rel = lambda p: p if os.path.isabs(p) or os.path.exists(p) else os.path.join(HERE, p)
    ca, cb = json.load(open(rel(a.base))), json.load(open(rel(a.set)))
    da, fa, _ = mod.build(ca); db, fb, _ = mod.build(cb)
    ia, ib = index(da, fa), index(db, fb)
    edits = []
    for t, eb in ib.items():
        if t in ia:
            for p, v in diffs(ia[t], eb): edits.append((t, p, v))
    if da['properties']['shape'].get('bgColor') != db['properties']['shape'].get('bgColor'):
        edits.append(('__root__', '/properties/shape/bgColor', db['properties']['shape']['bgColor']))
    log(f"{a.concept}: {len(edits)} edits by layer name", 'b')
    if a.dry:
        for t, p, v in edits: print(f"  {t:<40} {p:<28} {short(v)}")
        return
    t0 = time.time()
    if a.target: pid = a.target
    else:
        title = a.title or f"{a.concept} · {cb['brand']}"
        pid = call('duplicate_project', {"project_id": a.template, "title": title})['id']
        log(f"duplicate_project  →  {title}", 'dim')
    sk = call('get_skeleton', {"project_id": pid, "fields": "title"})
    ids = {}
    def walk(x):
        if isinstance(x, dict):
            if x.get('title'): ids[x['title']] = x['id']
            for c in x.get('children', []) or []: walk(c)
    walk(sk['tree']); [walk(d) for d in sk.get('definitions', [])]
    ids['__root__'] = sk['tree']['id']
    log(f"get_skeleton       →  {len(ids)} named layers", 'dim')
    for t, p, v in edits:
        if t not in ids: log(f"  ? {t} not found", 'acc'); continue
        for tryn in range(3):
            r = call('edit_part', {"project_id": pid, "item": f"#{ids[t]}{p}", "value": v})
            if r.get('result') == 'success' or 'element' in r: break
            time.sleep(2)
        else:
            raise SystemExit(f"edit failed on {t}{p}: {json.dumps(r)[:300]}")
        log(f"  ✓ {t:<38} {C['dim']}{p.split('/')[-1]:<10}{C['r']}{C['ok']} {short(v)}")
    meta = call('get_project', {"project_id": pid})
    log(f"{len(edits)} edits in {time.time() - t0:.0f}s  →  {meta.get('editor_url')}", 'b')
    out = os.path.join(os.path.dirname(HERE), 'build', 'launch', f"rebrand-{a.concept}-{cb['brand'].lower()}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"id": pid, "editor_url": meta.get('editor_url'), "edits": len(edits), "seconds": round(time.time() - t0)}, open(out, 'w'))


if __name__ == '__main__':
    main()
