#!/usr/bin/env python3
"""Launch Card: generates the SVGator template (4:5) from a content set.

usage:
  gen.py sets/lumen.json --out build/lumen.json            document only
  gen.py sets/lumen.json --create "Title"                  creates the project via MCP
  gen.py sets/lumen.json --replace pi_xxx [--title "T"]    overwrites the project

Every element has a stable id and a readable title (the one shown in
SVGator's layers panel). Times in milliseconds.
"""
import json, base64, os, sys, subprocess, mimetypes, argparse

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, '.mcp'))

W, H = 1080, 1350
# timeline (ms): the one place to tune the pacing
TL = dict(logo=150, brand=260, eyebrow=430, h1=600, h2=730, sub=1050, underline=1450,
          win=1450, shot=1950, zoom_in=2900, zoom_hold=3750, zoom_out=4650, zoom_end=5450,
          feat=5050, cta=5750, cursor=6100, press=7150, exit=8350)
T = 9600
INK, MUTED, CARD, LINE = '#17181C', '#55575E', '#FFFDF9', '#E4DDD1'
# product window: whole, right margin equal to the pills' left margin, full 16:10 screenshot
WIN = dict(x=248, y=650, w=W - 248 - 48, bar=50)
WIN['ih'] = round(WIN['w'] * 10 / 16); WIN['iy'] = WIN['y'] + WIN['bar']
FEAT_Y = WIN['iy'] + 40              # first pill: 40 px below the screenshot's edge
HEAD_FONT, UI_FONT = 'Bricolage Grotesque', 'Geist'


# ---------- basic values ----------
def col(h, a=1.0):
    h = h.lstrip('#')
    return {"type": "color", "value": {"r": int(h[0:2], 16), "g": int(h[2:4], 16), "b": int(h[4:6], 16), "a": a}}

def bez(a, b, c, d):
    return {"type": "cubic-bezier", "value": {"from": {"x": a, "y": b}, "to": {"x": c, "y": d}}}

EASE = {
    'out': bez(0.23, 1, 0.32, 1),      # firm arrival
    'soft': bez(0.2, 0, 0, 1),         # soft arrival
    'glide': bez(0.32, 0.72, 0, 1),    # long glide
    'inout': bez(0.45, 0, 0.55, 1),
    'sine': bez(0.37, 0, 0.63, 1),     # ambient breathing
    'in': bez(0.4, 0, 1, 1),           # exit
    'back': bez(0.3, 1.18, 0.3, 1),    # small bounce (corporate-friendly personality)
    'press': bez(0.3, 0, 0.2, 1),
    'mouse': bez(0.55, 0.05, 0.2, 1),  # pointer movement
    'lin': {"type": "linear", "value": None},
}

def k(t, v, e='out'):
    return {"time": int(t), "value": v, "easing": EASE[e]}

def ch(*keys):
    return {"keys": sorted(keys, key=lambda x: x['time'])}

def O(x, y, start=None, end=None):
    o = {"x": round(x, 2), "y": round(y, 2), "type": "corner"}
    if start: o["start"] = {"x": start[0], "y": start[1]}
    if end: o["end"] = {"x": end[0], "y": end[1]}
    return o

def S(s):
    return {"x": s, "y": s}

def tf(ox, oy, tx=0, ty=0, s=1):
    return {"origin": O(ox, oy), "translate": {"x": tx, "y": ty}, "scale": S(s),
            "skew": {"x": 0, "y": 0}, "rotate": 0}

T0 = tf(0, 0)


def data_uri(path):
    p = os.path.join(ROOT, path)
    mt = mimetypes.guess_type(p)[0] or 'image/png'
    return f"data:{mt};base64," + base64.b64encode(open(p, 'rb').read()).decode()


# ---------- element builders ----------
def node(typ, id_, title, props=None, anim=None, children=None):
    n = {"id": id_, "type": typ, "title": title}
    if props: n["properties"] = props
    if anim: n["animators"] = anim
    if children is not None: n["children"] = children
    return n

def group(id_, title, children, cx=0, cy=0, anim=None, clip=None):
    """Group with pivot at (cx, cy): origin = pivot, translate = -pivot (identity at rest)."""
    props = {"transform": tf(cx, cy, -cx, -cy)}
    if clip: props["compositing"] = {"clip": {"path": clip, "rule": False}}
    return node("g", id_, title, props, anim, children)

def rect(id_, title, x, y, w, h, r=0, fill=None, stroke=None, sw=0, anim=None, filt=None, opacity=None):
    props = {"shape": {"size": {"width": w, "height": h}, "radius": {"x": r, "y": r}},
             "transform": tf(x + w / 2, y + h / 2, -w / 2, -h / 2),
             "fill": {"paint": fill or {"type": "none"}, "opacity": 1}}
    if stroke: props["stroke"] = {"paint": stroke, "width": sw, "opacity": 1}
    if filt: props["filter"] = {"list": filt}
    if opacity is not None: props["compositing"] = {"opacity": opacity}
    return node("rect", id_, title, props, anim)

def circle(id_, title, cx, cy, r, fill=None, stroke=None, sw=0, anim=None, opacity=None):
    props = {"shape": {"radius": r}, "transform": tf(cx, cy),
             "fill": {"paint": fill or {"type": "none"}, "opacity": 1}}
    if stroke: props["stroke"] = {"paint": stroke, "width": sw, "opacity": 1}
    if opacity is not None: props["compositing"] = {"opacity": opacity}
    return node("circle", id_, title, props, anim)

def ellipse(id_, title, cx, cy, rx, ry, fill, anim=None, filt=None, opacity=None):
    props = {"shape": {"radius": {"x": rx, "y": ry}}, "transform": tf(cx, cy), "fill": {"paint": fill, "opacity": 1}}
    if filt: props["filter"] = {"list": filt}
    if opacity is not None: props["compositing"] = {"opacity": opacity}
    return node("ellipse", id_, title, props, anim)

def text(id_, title, s, x, y, font, size, weight, fill, anchor='start', ls=0, anim=None, opacity=None):
    props = {"shape": {"text": s, "fontFamily": font, "fontSize": size,
                       "fontStyle": {"bold": False, "italic": False, "weight": weight},
                       "letterSpacing": ls, "textAnchor": anchor, "wrap": False},
             "transform": tf(x, y), "fill": {"paint": fill, "opacity": 1}}
    if opacity is not None: props["compositing"] = {"opacity": opacity}
    return node("text", id_, title, props, anim)

def image(id_, title, href, x, y, w, h, fit="xMidYMid meet", anim=None, opacity=None):
    props = {"shape": {"size": {"width": w, "height": h}, "href": href, "aspectRatio": fit},
             "transform": tf(x + w / 2, y + h / 2, -w / 2, -h / 2)}
    if opacity is not None: props["compositing"] = {"opacity": opacity}
    return node("image", id_, title, props, anim)

def path(id_, title, pts, x, y, fill=None, stroke=None, sw=0, cap='round', join='round', anim=None, dash=None):
    """pts: list of nodes in local coordinates; (x, y) = position of the local (0, 0) point."""
    nodes = []
    for p in pts:
        n = {"x": p[0], "y": p[1], "type": p[2] if len(p) > 2 and isinstance(p[2], str) else "corner", "mode": 0}
        if len(p) > 3:
            n["start"] = {"x": p[3][0], "y": p[3][1]} if p[3] else None
            n["end"] = {"x": p[4][0], "y": p[4][1]} if len(p) > 4 and p[4] else None
            n = {kk: vv for kk, vv in n.items() if vv is not None}
        nodes.append(n)
    props = {"shape": {"path": nodes}, "transform": tf(x, y),
             "fill": {"paint": fill or {"type": "none"}, "opacity": 1}}
    if stroke:
        props["stroke"] = {"paint": stroke, "width": sw, "opacity": 1, "lineCap": cap, "lineJoin": join}
        if dash: props["stroke"]["dashArray"] = [dash]; props["stroke"]["dashOffset"] = 0
    return node("path", id_, title, props, anim)

def clip_def(id_, title, x, y, w, h, r=0):
    return {"id": id_, "type": "clipPath", "title": title, "properties": {"transform": T0},
            "children": [rect(id_ + "-shape", title + " shape", x, y, w, h, r, fill=col('#000000'))]}

def clip_def_bottom_round(id_, title, x, y, w, h, r):
    """Mask with only the bottom corners rounded (the image area below the browser bar)."""
    kr = r * 0.5523
    pts = [(x, y), (x + w, y),
           (x + w, y + h - r, "cusp", None, (x + w, y + h - r + kr)),
           (x + w - r, y + h, "cusp", (x + w - r + kr, y + h), None),
           (x + r, y + h, "cusp", None, (x + r - kr, y + h)),
           (x, y + h - r, "cusp", (x, y + h - r + kr), None),
           (x, y)]
    return {"id": id_, "type": "clipPath", "title": title, "properties": {"transform": T0},
            "children": [path(id_ + "-shape", title + " shape", pts, 0, 0, fill=col('#000000'))]}


# ---------- text measurement (real fonts via Playwright) ----------
def measure(items):
    import tempfile
    # optional shell script that puts node and Playwright on PATH (missing file: plain `node` is used)
    env = os.path.expanduser(os.environ.get('PW_ENV', '~/.android-toolchain/pw/env.sh'))
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
        json.dump(items, f); fn = f.name
    cmd = f"source {env} >/dev/null 2>&1; node {ROOT}/measure.mjs @{fn}; rm -f {fn}"
    out = subprocess.run(['bash', '-c', cmd], capture_output=True, text=True).stdout
    line = [l for l in out.splitlines() if l.startswith('[')][-1]
    return [r['width'] for r in json.loads(line)]


# ---------- the scene ----------
def build(c):
    A = c['accent']
    defs, kids = [], []
    M = 72
    t = TL

    def exit_anim(i, cx, cy, extra_origin=(), extra_opacity=()):
        """staggered exit (rises 24 px and fades out) for a clean loop"""
        t0 = t['exit'] + i * 55
        t1 = t0 + 420
        return {"transform": {"origin": ch(*(extra_origin or (k(0, O(cx, cy), 'lin'),)), k(t0, O(cx, cy), 'in'), k(t1, O(cx, cy - 24), 'lin'))},
                "compositing": {"opacity": ch(*(extra_opacity or (k(0, 1, 'lin'),)), k(t0, 1, 'in'), k(t1, 0, 'lin'))}}

    # ---- background + ambient glow in the brand color ----
    kids.append(rect("background", "background", 0, 0, W, H, fill=col(c['paper'])))
    gx, gy = 800, 930
    kids.append(ellipse("bg-glow", "bg-glow", gx, gy, 470, 360, col(A), opacity=0.13,
        filt=[{"type": "blur", "value": {"x": 110, "y": 110}}],
        anim={"transform": {
            "origin": ch(k(0, O(gx, gy), 'sine'), k(T / 2, O(gx - 70, gy - 60), 'sine'), k(T, O(gx, gy), 'lin')),
            "scale": ch(k(0, S(1), 'sine'), k(T / 2, S(1.1), 'sine'), k(T, S(1), 'lin'))}}))

    # ---- header: logo + name ----
    lx, ly, lsz = M, 62, 76
    logo = image("logo", "logo", data_uri(c['logo']), lx, ly, lsz, lsz, anim={
        "transform": {"scale": ch(k(t['logo'], S(0.82), 'back'), k(t['logo'] + 550, S(1), 'lin'))},
        "compositing": {"opacity": ch(k(t['logo'], 0, 'soft'), k(t['logo'] + 270, 1, 'lin'))}})
    bn_x, bn_y = lx + lsz + 18, 114
    brand = text("brand-name", "brand-name", c['brand'], bn_x, bn_y, HEAD_FONT, 40, 700, col(INK), ls=-0.8, anim={
        "transform": {"origin": ch(k(t['brand'], O(bn_x - 16, bn_y), 'out'), k(t['brand'] + 560, O(bn_x, bn_y), 'lin'))},
        "compositing": {"opacity": ch(k(t['brand'], 0, 'soft'), k(t['brand'] + 300, 1, 'lin'))}})
    hc = (W / 2, 100)
    kids.append(group("header", "header", [logo, brand], *hc, anim=exit_anim(0, *hc)))

    # ---- copy: eyebrow, two-line headline, underline, subhead ----
    ey = 224
    eyebrow_dot = circle("eyebrow-dot", "eyebrow-dot", M + 7, ey - 8, 7, fill=col(A), anim={
        "transform": {"scale": ch(k(t['eyebrow'], S(0.4), 'back'), k(t['eyebrow'] + 370, S(1), 'lin'))},
        "compositing": {"opacity": ch(k(t['eyebrow'], 0, 'soft'), k(t['eyebrow'] + 170, 1, 'lin'))}})
    te = t['eyebrow'] + 70
    eyebrow_text = text("eyebrow-text", "eyebrow-text", c['eyebrow'], M + 26, ey, UI_FONT, 21, 600, col(INK), ls=2.4, anim={
        "transform": {"origin": ch(k(te, O(M + 12, ey), 'out'), k(te + 500, O(M + 26, ey), 'lin'))},
        "compositing": {"opacity": ch(k(te, 0, 'soft'), k(te + 300, 1, 'lin'))}})
    eyebrow = group("eyebrow", "eyebrow", [eyebrow_dot, eyebrow_text], M, ey)

    HS, HLS = 104, -3.2
    l1y, l2y = 338, 442
    lines = []
    for i, (s, by, t_in) in enumerate([(c['headline'][0], l1y, t['h1']), (c['headline'][1], l2y, t['h2'])]):
        n = i + 1
        cid = f"clip-headline-{n}"
        defs.append(clip_def(cid, f"headline-line-{n}-mask", M - 12, by - HS - 6, W - 2 * M + 24, HS + 6 + 34))
        tx = text(f"headline-line-{n}", f"headline-line-{n}", s, M - 4, by, HEAD_FONT, HS, 700, col(INK), ls=HLS, anim={
            "transform": {"origin": ch(k(t_in, O(M - 4, by + 136), 'out'), k(t_in + 760, O(M - 4, by), 'lin'))}})
        lines.append(group(f"headline-line-{n}-reveal", f"headline-line-{n}-reveal", [tx], M, by, clip=cid))

    # underline drawn under the key word of the second line
    l2 = c['headline'][1]
    word = c.get('underline_word') or l2.split()[-1]
    idx = max(l2.find(word), 0)
    pre, wd = measure([{"t": l2[:idx], "f": HEAD_FONT, "w": 700, "s": HS, "ls": HLS},
                       {"t": word, "f": HEAD_FONT, "w": 700, "s": HS, "ls": HLS}])
    ux0, uw, uy = M - 4 + pre + 2, wd - 4, l2y + 26
    upts = [(0, 6, "cusp", None, (uw * 0.3, 10)), (uw, -4, "cusp", (uw * 0.7, 2), None)]
    ulen = int(uw * 1.04 + 20)
    underline = path("headline-underline", "headline-underline", upts, ux0, uy, stroke=col(A), sw=11, dash=ulen, anim={
        "stroke": {"dashOffset": ch(k(t['underline'], ulen, 'soft'), k(t['underline'] + 700, 0, 'lin'))}})

    sub_y = 524
    subhead = text("subhead", "subhead", c['subhead'], M, sub_y, UI_FONT, 29, 400, col(MUTED), ls=-0.2, anim={
        "transform": {"origin": ch(k(t['sub'], O(M, sub_y + 18), 'out'), k(t['sub'] + 600, O(M, sub_y), 'lin'))},
        "compositing": {"opacity": ch(k(t['sub'], 0, 'soft'), k(t['sub'] + 400, 1, 'lin'))}})

    cc = (W / 2, 380)
    kids.append(group("copy", "copy", [eyebrow, *lines, underline, subhead], *cc, anim=exit_anim(1, *cc)))

    # ---- product window (rises from below, whole window inside the canvas) ----
    wx, wy, ww, bar = WIN['x'], WIN['y'], WIN['w'], WIN['bar']
    ih = WIN['ih']                      # 16:10 slot for the screenshot
    wh = bar + ih
    iy = wy + bar
    defs.append(clip_def_bottom_round("clip-window", "product-image-mask", wx, iy, ww, ih, 22))
    # product-image's anchor point is the zoom center: move it onto the feature to show
    fx, fy = c.get('zoom_focus', [0.5, 0.5])
    zx, zy = wx + ww * fx, iy + ih * fy
    Z = c.get('zoom', 1.7)
    shot = image("product-image", "product-image", data_uri(c['screenshot']), wx, iy, ww, ih, fit="xMinYMin slice", anim={
        "transform": {"scale": ch(k(t['shot'], S(1.04), 'glide'), k(t['shot'] + 950, S(1), 'lin'),
                                  k(t['zoom_in'], S(1), 'glide'), k(t['zoom_hold'], S(Z), 'lin'),
                                  k(t['zoom_out'], S(Z), 'inout'), k(t['zoom_end'], S(1), 'lin'))},
        "compositing": {"opacity": ch(k(t['shot'], 0, 'soft'), k(t['shot'] + 400, 1, 'lin'))}})
    shot["properties"]["transform"] = tf(zx, zy, wx - zx, iy - zy)
    shot_g = group("product-image-reveal", "product-image-reveal", [shot], wx + ww / 2, iy + ih / 2, clip="clip-window")
    vis_cx = wx + ww / 2                # window center
    sh_cx, sh_cy = wx + 12 + ww / 2, wy + wh / 2
    win_shadow = rect("window-shadow", "window-shadow", wx + 24, wy + 40, ww - 24, wh - 30, 26, fill=col('#2A2118'),
        filt=[{"type": "blur", "value": {"x": 34, "y": 34}}], anim={
        "compositing": {"opacity": ch(k(t['win'] + 100, 0, 'soft'), k(t['win'] + 1000, 0.28, 'lin'))},
        "transform": {"origin": ch(k(t['win'] + 100, O(sh_cx, sh_cy + 26), 'glide'), k(t['win'] + 1100, O(sh_cx, sh_cy + 40), 'lin'))}})
    frame = rect("window-frame", "window-frame", wx, wy, ww, wh, 22, fill=col(CARD), stroke=col(LINE), sw=1.5)
    dots = [circle(f"window-dot-{i+1}", f"window-dot-{i+1}", wx + 30 + i * 22, wy + bar / 2, 6.5, fill=col('#E3DBCE')) for i in range(3)]
    pill_w = 360
    url_pill = rect("url-pill", "url-pill", vis_cx - pill_w / 2, wy + 10, pill_w, 30, 15, fill=col('#F1ECE3'))
    url = text("window-url", "window-url", c['url'], vis_cx, wy + 31, UI_FONT, 17, 500, col(MUTED), anchor='middle')
    win_bar = group("window-bar", "window-bar", [*dots, url_pill, url], vis_cx, wy + bar / 2)
    wcx, wcy = vis_cx, wy + wh / 2
    t0 = t['exit'] + 2 * 55
    kids.append(group("product-window", "product-window", [win_shadow, frame, shot_g, win_bar], wcx, wcy, anim={
        "transform": {
            "origin": ch(k(t['win'], O(wcx, wcy + 170), 'glide'), k(t['win'] + 1000, O(wcx, wcy), 'sine'),
                         k((t['win'] + 1000 + t0) / 2, O(wcx, wcy - 9), 'sine'), k(t0, O(wcx, wcy), 'in'), k(t0 + 420, O(wcx, wcy - 30), 'lin')),
            "scale": ch(k(t['win'], S(0.95), 'glide'), k(t['win'] + 1000, S(1), 'lin'))},
        "compositing": {"opacity": ch(k(t['win'], 0, 'soft'), k(t['win'] + 350, 1, 'lin'), k(t0, 1, 'in'), k(t0 + 420, 0, 'lin'))}}))

    # ---- three features (pill cards over the window edge) ----
    fx0, fw, fh = 48, 410, 80          # 410: the pills don't cover the screenshot's numbers
    feats = []
    for i, label in enumerate(c['features'][:3]):
        n = i + 1
        fyy = FEAT_Y + i * 96
        tin = t['feat'] + i * 150
        fcx, fcy = fx0 + fw / 2, fyy + fh / 2
        card = rect(f"feature-{n}-card", f"feature-{n}-card", fx0, fyy, fw, fh, fh / 2, fill=col(CARD), stroke=col(LINE), sw=1.2,
                    filt=[{"type": "drop-shadow", "value": {"blur": {"x": 18, "y": 18}, "offset": {"x": 0, "y": 12}, "color": {"r": 42, "g": 33, "b": 24, "a": 0.13}}}])
        icx, icy = fx0 + 42, fcy
        icon_bg = circle(f"feature-{n}-icon-bg", f"feature-{n}-icon-bg", icx, icy, 21, fill=col(INK))
        check = path(f"feature-{n}-check", f"feature-{n}-check", [(-8, 0.5), (-2.5, 6.5), (8.5, -6)], icx, icy,
                     stroke=col(CARD), sw=3.6, dash=30, anim={"stroke": {"dashOffset": ch(k(tin + 260, 30, 'soft'), k(tin + 620, 0, 'lin'))}})
        lab = text(f"feature-{n}-label", f"feature-{n}-label", label, fx0 + 80, fcy + 8.5, UI_FONT, 24, 600, col(INK), ls=-0.2)
        feats.append(group(f"feature-{n}", f"feature-{n}", [card, group(f"feature-{n}-icon", f"feature-{n}-icon", [icon_bg, check], icx, icy), lab], fcx, fcy, anim={
            "transform": {"origin": ch(k(tin, O(fcx - 34, fcy), 'out'), k(tin + 560, O(fcx, fcy), 'lin')),
                          "scale": ch(k(tin, S(0.92), 'back'), k(tin + 560, S(1), 'lin'))},
            "compositing": {"opacity": ch(k(tin, 0, 'soft'), k(tin + 260, 1, 'lin'))}}))
    fc = (fx0 + fw / 2, FEAT_Y + 140)
    kids.append(group("features", "features", feats, *fc, anim=exit_anim(3, *fc)))

    # ---- call to action with click ----
    bx, by_, bw, bh = 48, 1116, 410, 96
    bcx, bcy = bx + bw / 2, by_ + bh / 2
    icx = bx + bw - bh / 2
    tin, press = t['cta'], t['press']
    ripple = circle("cta-ripple", "cta-ripple", icx, bcy, 34, stroke=col(A), sw=4, opacity=0, anim={
        "transform": {"scale": ch(k(press + 40, S(1), 'soft'), k(press + 760, S(2.5), 'lin'))},
        "compositing": {"opacity": ch(k(0, 0, 'lin'), k(press + 30, 0, 'lin'), k(press + 40, 0.7, 'soft'), k(press + 760, 0, 'lin'))}})
    button = rect("cta-button", "cta-button", bx, by_, bw, bh, bh / 2, fill=col(A),
                  filt=[{"type": "drop-shadow", "value": {"blur": {"x": 20, "y": 20}, "offset": {"x": 0, "y": 14}, "color": {"r": 42, "g": 33, "b": 24, "a": 0.18}}}])
    label_cx = bx + (bw - bh) / 2 + 18
    cta_label = text("cta-label", "cta-label", c['cta'], label_cx, bcy + 11, UI_FONT, 31, 700, col(CARD), anchor='middle', ls=-0.3)
    bub = circle("cta-icon-bg", "cta-icon-bg", icx, bcy, 34, fill=col(CARD))
    arrow = path("cta-arrow", "cta-arrow", [(-11, 0), (11, 0), (2, -9), (11, 0), (2, 9)], icx, bcy, stroke=col(INK), sw=3.6, anim={
        "transform": {"origin": ch(k(press + 60, O(icx, bcy), 'out'), k(press + 260, O(icx + 9, bcy), 'soft'), k(press + 700, O(icx, bcy), 'lin'))}})
    t0 = t['exit'] + 4 * 55
    kids.append(group("cta", "cta", [ripple, button, cta_label, group("cta-icon", "cta-icon", [bub, arrow], icx, bcy)], bcx, bcy, anim={
        "transform": {
            "origin": ch(k(tin, O(bcx, bcy + 40), 'out'), k(tin + 620, O(bcx, bcy), 'lin'), k(t0, O(bcx, bcy), 'in'), k(t0 + 420, O(bcx, bcy - 24), 'lin')),
            "scale": ch(k(tin, S(0.94), 'out'), k(tin + 620, S(1), 'lin'), k(press, S(1), 'press'), k(press + 90, S(0.95), 'back'), k(press + 420, S(1), 'lin'))},
        "compositing": {"opacity": ch(k(tin, 0, 'soft'), k(tin + 300, 1, 'lin'), k(t0, 1, 'in'), k(t0 + 420, 0, 'lin'))}}))

    # ---- pointer ----
    sc = 1.3
    arrow_pts = [(0, 0), (0, 41), (10, 32), (17.5, 48), (25, 44.5), (17.5, 29), (30.5, 29), (0, 0)]
    cur_pts = [(round(x * sc, 1), round(y * sc, 1)) for x, y in arrow_pts]
    tip = (icx + 6, bcy + 4)
    start = (W + 60, H + 30)
    c0 = t['cursor']
    cur = path("cursor", "cursor", cur_pts, *tip, fill=col(INK), stroke=col(CARD), sw=3, anim={
        "transform": {
            "origin": ch(k(c0, O(*start, end=(900, 1160)), 'mouse'), k(press - 60, O(*tip, start=(640, 1330)), 'lin'),
                         k(t['exit'] - 900, O(*tip), 'sine'), k(t['exit'] - 50, O(tip[0] + 26, tip[1] + 40), 'in'), k(t['exit'] + 450, O(tip[0] + 60, tip[1] + 110), 'lin')),
            "scale": ch(k(press - 20, S(1), 'press'), k(press + 70, S(0.84), 'out'), k(press + 330, S(1), 'lin'))},
        "compositing": {"opacity": ch(k(c0, 0, 'soft'), k(c0 + 200, 1, 'lin'), k(t['exit'] - 50, 1, 'in'), k(t['exit'] + 400, 0, 'lin'))}})
    kids.append(cur)

    # ---- note for template users: outside the canvas, so never visible in exports ----
    nx, ny = W + 80, 60
    note_lines = [
        ("HOW TO MAKE IT YOURS", 600, 20, INK, 2.2, 0),
        ("1  Retype any text layer. Headline lines", 500, 22, INK, 0, 18),
        ("    fit about 18 characters, features 26.", 400, 22, MUTED, 0, 0),
        ("2  Replace logo (square) and product-image", 500, 22, INK, 0, 14),
        ("    (16:10 screenshot, 1600 x 1000).", 400, 22, MUTED, 0, 0),
        ("3  Brand color lives in 5 layers: bg-glow,", 500, 22, INK, 0, 14),
        ("    eyebrow-dot, headline-underline,", 400, 22, MUTED, 0, 0),
        ("    cta-button, cta-ripple.", 400, 22, MUTED, 0, 0),
        ("4  Zoom: move the anchor point of", 500, 22, INK, 0, 14),
        ("    product-image onto your feature.", 400, 22, MUTED, 0, 0),
        ("5  Drag headline-underline under your", 500, 22, INK, 0, 14),
        ("    key word.", 400, 22, MUTED, 0, 0),
        ("This note sits outside the canvas, so it", 400, 19, MUTED, 0, 22),
        ("never shows up in exports.", 400, 19, MUTED, 0, 0),
    ]
    note_kids, yy = [], ny + 58
    for i, (s, wgt, sz, colr, lsp, gap) in enumerate(note_lines):
        yy += gap + (sz * 1.45 if i else 0)
        note_kids.append(text(f"how-to-line-{i+1}", f"how-to-line-{i+1}", s, nx + 36, yy, UI_FONT, sz, wgt, col(colr), ls=lsp))
    note_h = yy - ny + 44
    kids.append(group("how-to", "how-to (outside canvas, not exported)",
                      [rect("how-to-card", "how-to-card", nx, ny, 520, note_h, 24, fill=col(CARD), stroke=col(LINE), sw=1.5), *note_kids],
                      nx + 260, ny + note_h / 2))

    doc = {"type": "svg", "id": "launch-card",
           "animation": {"duration": T, "direction": 1, "iterations": 0, "fill": 1, "alternate": False, "speed": 1},
           "properties": {"shape": {"position": {"x": 0, "y": 0}, "size": {"width": W, "height": H}, "bgColor": col(c['paper'])}},
           "children": kids}
    return doc, defs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('set')
    ap.add_argument('--out')
    ap.add_argument('--create')
    ap.add_argument('--replace')
    ap.add_argument('--title')
    a = ap.parse_args()
    c = json.load(open(a.set))
    doc, defs = build(c)
    if a.out:
        json.dump({"document": doc, "definitions": defs}, open(a.out, 'w'))
        print('written', a.out, os.path.getsize(a.out))
    if a.create or a.replace:
        from svg import call
        args = {"document": doc, "definitions": defs}
        if a.create:
            args["title"] = a.create
            r = call('create_project', args)
        else:
            args["project_id"] = a.replace
            if a.title: args["title"] = a.title
            r = call('replace_project', args)
        print(json.dumps({kk: r[kk] for kk in ('id', 'title', 'editor_url') if kk in r}))


if __name__ == '__main__':
    main()
