#!/usr/bin/env python3
"""Departures, first (heavy) version, kept for comparison with board.py.
One animated flap per cell and text changed by animated clip paths: about 350 layers
and 4,400 keyframes per board, too heavy for the SVGator editor. board.py replaced it.

usage:
  board_heavy.py board/sets/aurora.json --out build/board.json
  board_heavy.py board/sets/aurora.json --create "Title"
  board_heavy.py board/sets/aurora.json --replace pi_xxx

The reusable trick: the text uses a monospaced font with letter-spacing equal to
the flap pitch, so whatever word you type, each letter lands in its own
cell. The spinning flaps and the wipes that change the text are locked
layers; template users only touch the texts, the logo, the QR and two colors.
"""
import argparse, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, '.mcp'))
import gen
from gen import col, bez, k, ch, O, S, tf, node, rect, circle, text, image, group, data_uri

W, H, T = 1920, 1080, 24000
U = [600, 12600]                 # updates: B -> A, then A -> B (B is shown at t=0)
P, CW, CH, ROWP = 50, 46, 76, 92  # flap pitch, width, height, row pitch
FONT, FS = 'Chivo Mono', 64
ADV = 0.6 * FS                    # monospaced advance
LS = round(P - ADV, 2)            # letter-spacing = pitch - advance
CAP = 0.69 * FS
CS, RS = 15, 105                  # delay per flap and per row (ms)
SWITCH = 80                       # the text changes mid-flutter
FLIP = 62                         # duration of one flap flip
NFLIPS = 2

BG, BG2, INK, MUTED, DIM = '#0E0F11', '#16181B', '#F1ECE2', '#8B8E95', '#5F6269'
AMBER = '#F2B33D'
TILE = [(0, '#2C2F35'), (0.499, '#25282D'), (0.5, '#1E2024'), (1, '#1A1C1F')]
FLAP = [(0, '#30333A'), (1, '#26292E')]

GAP = 40
RY0 = 252
CAT_N = 8

# layouts: same mechanics, different columns for different businesses
LAYOUTS = {
    'list': {'cols': [dict(key='name', n=18), dict(key='price', n=5, align='right'), dict(key='status', n=9, color='amber', blink=True)],
             'labels': ['DESTINATION', 'FARE', 'STATUS'], 'header': 'PARTENZE · DEPARTURES'},
    'schedule': {'cols': [dict(key='time', n=5), dict(key='event', n=15), dict(key='room', n=4), dict(key='status', n=8, color='amber', blink=True)],
                 'labels': ['TIME', 'CLASS', 'ROOM', 'STATUS'], 'header': 'OGGI · TODAY'},
    'queue': {'cols': [dict(key='ticket', n=4, color='amber'), dict(key='name', n=15), dict(key='desk', n=7), dict(key='wait', n=6, align='right', color='amber', blink=True)],
              'labels': ['TICKET', 'CLIENT', 'CHAIR', 'WAIT'], 'header': 'ORA SERVIAMO · NOW SERVING'},
}
COLS, XS, NX, ROW_R = [], {}, 0, 0


def configure(layout):
    """compute column positions, board centered"""
    global COLS, XS, NX, ROW_R
    COLS = LAYOUTS[layout]['cols']
    total = sum(c['n'] * P - 4 for c in COLS) + GAP * (len(COLS) - 1)
    NX = round((W - total) / 2)
    XS, x = {}, NX
    for c in COLS:
        XS[c['key']] = x
        x += c['n'] * P - 4 + GAP
    ROW_R = NX + total

configure('list')

gen.EASE['fall'] = bez(0.55, 0, 1, 0.55)
gen.EASE['step'] = {"type": "steps", "value": {"steps": 1, "jump": 0}}


def grad(stops, vertical=True):
    return {"type": "linear-gradient", "value": {"from": {"x": 0, "y": 0}, "to": {"x": 0, "y": 1} if vertical else {"x": 1, "y": 0},
            "stops": [{"color": col(c)["value"], "offset": o} for o, c in stops], "spread": "pad", "fixed": False}}


def cells_for_row(y):
    out = []
    for c in COLS:
        out += [(XS[c['key']] + i * P, y) for i in range(c['n'])]
    return out


def rr_nodes(x, y, w, h, r):
    kk = r * 0.5523
    return [
        {"x": x + r, "y": y, "type": "corner", "mode": 1},
        {"x": x + w - r, "y": y, "type": "cusp", "mode": 0, "end": {"x": x + w - r + kk, "y": y}},
        {"x": x + w, "y": y + r, "type": "cusp", "mode": 0, "start": {"x": x + w, "y": y + r - kk}},
        {"x": x + w, "y": y + h - r, "type": "cusp", "mode": 0, "end": {"x": x + w, "y": y + h - r + kk}},
        {"x": x + w - r, "y": y + h, "type": "cusp", "mode": 0, "start": {"x": x + w - r + kk, "y": y + h}},
        {"x": x + r, "y": y + h, "type": "cusp", "mode": 0, "end": {"x": x + r - kk, "y": y + h}},
        {"x": x, "y": y + h - r, "type": "cusp", "mode": 0, "start": {"x": x, "y": y + h - r + kk}},
        {"x": x, "y": y + r, "type": "cusp", "mode": 0, "end": {"x": x, "y": y + r - kk}},
        {"x": x + r, "y": y, "type": "cusp", "mode": -1, "start": {"x": x + r - kk, "y": y}},
    ]


def compound(id_, title, nodes, fill=None, stroke=None, sw=0, locked=True):
    props = {"shape": {"path": nodes}, "transform": tf(0, 0),
             "fill": {"paint": fill or {"type": "none"}, "opacity": 1}}
    if stroke: props["stroke"] = {"paint": stroke, "width": sw, "opacity": 1, "lineCap": "butt", "lineJoin": "miter"}
    n = node("path", id_, title, props)
    n["locked"] = locked
    return n


def tiles(id_, cells):
    nodes = []
    for x, y in cells: nodes += rr_nodes(x, y, CW, CH, 5)
    return compound(id_, id_, nodes, fill=grad(TILE))


def hinges(id_, cells):
    nodes = []
    for x, y in cells:
        nodes += [{"x": x + 1, "y": y + CH / 2, "type": "corner", "mode": 1}, {"x": x + CW - 1, "y": y + CH / 2, "type": "corner", "mode": -1}]
    return compound(id_, id_, nodes, stroke=col('#0A0B0C'), sw=3)


def flap(id_, x, y, times):
    """upper half-flap that rotates on the hinge (scaleY 1 -> -1) at every update"""
    sk, ok = [k(0, {"x": 1, "y": 1}, 'lin')], [k(0, 0, 'lin')]
    for tc in times:
        t = tc
        ok += [k(t - 1, 0, 'lin'), k(t, 1, 'lin')]
        for f in range(NFLIPS):
            sk += [k(t, {"x": 1, "y": 1}, 'fall'), k(t + FLIP, {"x": 1, "y": -1}, 'lin')]
            t += FLIP + 1
        sk += [k(t, {"x": 1, "y": 1}, 'lin')]
        ok += [k(t - 1, 1, 'lin'), k(t, 0, 'lin')]
    props = {"shape": {"size": {"width": CW, "height": CH / 2}, "radius": {"x": 5, "y": 5}},
             "transform": tf(x + CW / 2, y + CH / 2, -CW / 2, -CH / 2),
             "fill": {"paint": grad(FLAP), "opacity": 1}, "compositing": {"opacity": 0}}
    return node("rect", id_, id_, props, {"transform": {"scale": ch(*sk)}, "compositing": {"opacity": ch(*ok)}})


def cell_time(u, x, row_delay):
    return int(u + row_delay + (x - NX) / P * CS)


def wipe_clip(id_, x0, x1, y, h, show_from_start, u_list, row_delay):
    """wipe: a page's text appears from left to right as the wave of flaps passes"""
    wd = x1 - x0
    dur = int(wd / P * CS)
    ok, sk = [], []
    hidden_r, hidden_l = (x1, 0), (x0, 0)
    # u_list[0]: B -> A, u_list[1]: A -> B
    for i, u in enumerate(u_list):
        t0 = int(u + row_delay + SWITCH)
        appearing = (i == 0) != show_from_start   # A appears at the first update, B at the second
        if appearing:
            ok += [k(t0 - 1, O(x1, y), 'lin'), k(t0, O(x0, y), 'lin')]
            sk += [k(t0, {"width": 0, "height": h}, 'lin'), k(t0 + dur, {"width": wd, "height": h}, 'lin')]
        else:
            ok += [k(t0, O(x0, y), 'lin'), k(t0 + dur, O(x1, y), 'lin')]
            sk += [k(t0, {"width": wd, "height": h}, 'lin'), k(t0 + dur, {"width": 0, "height": h}, 'lin')]
    start_w = wd if show_from_start else 0
    start_x = x0 if show_from_start else x1
    ok = [k(0, O(start_x, y), 'lin')] + ok + [k(T, O(start_x, y), 'lin')]
    sk = [k(0, {"width": start_w, "height": h}, 'lin')] + sk + [k(T, {"width": start_w, "height": h}, 'lin')]
    r = {"id": id_ + "-shape", "type": "rect", "title": id_ + " shape",
         "properties": {"shape": {"size": {"width": start_w, "height": h}, "radius": {"x": 0, "y": 0}},
                        "transform": {"origin": O(start_x, y), "translate": {"x": 0, "y": 0}, "scale": S(1), "skew": {"x": 0, "y": 0}, "rotate": 0},
                        "fill": {"paint": col('#000000'), "opacity": 1}},
         "animators": {"transform": {"origin": ch(*ok)}, "shape": {"size": ch(*sk)}}}
    c = {"id": id_, "type": "clipPath", "title": id_, "properties": {"transform": gen.T0}, "children": [r]}
    c["locked"] = True
    return c


def blink(u_list, row_delay, which):
    """the status blinks three times after its page has appeared"""
    keys = [k(0, 1, 'lin')]
    u = u_list[which]
    t = int(u + row_delay + SWITCH + (ROW_R - NX) / P * CS + 250)
    for _ in range(3):
        keys += [k(t, 1, 'lin'), k(t + 40, 0.18, 'lin'), k(t + 260, 0.18, 'lin'), k(t + 300, 1, 'lin')]
        t += 520
    keys.append(k(T, 1, 'lin'))
    return {"compositing": {"opacity": ch(*keys)}}


def text_x_left(c0):
    return round(c0 + CW / 2 - ADV / 2, 2)

def text_x_right(c0, n):
    return round(c0 + (n - 1) * P + CW / 2 - ADV / 2 + P, 2)

def baseline(y):
    return round(y + CH / 2 + CAP / 2, 2)


def mono(id_, s, x, y, colr, anchor='start', anim=None):
    return text(id_, id_, s, x, y, FONT, FS, 700, col(colr), anchor=anchor, ls=LS, anim=anim)


def build(c):
    layout = c.get('layout', 'list')
    configure(layout)
    L = LAYOUTS[layout]
    A = c['accent']
    kids = []
    # ---- background ----
    kids.append(rect("background", "background", 0, 0, W, H, fill={"type": "radial-gradient", "value": {
        "center": {"x": 0.5, "y": 0.42}, "radius": 0.75,
        "stops": [{"color": col(BG2)["value"], "offset": 0}, {"color": col(BG)["value"], "offset": 1}], "spread": "pad", "fixed": False}}))
    kids.append(rect("board-frame", "board-frame", 28, 28, W - 56, H - 56, 26, stroke=col('#1E2024'), sw=2))

    # ---- header ----
    kids.append(image("logo", "logo", data_uri(c['logo']), NX, 66, 96, 96))
    kids.append(text("brand-name", "brand-name", c['brand'], NX + 120, 118, gen.HEAD_FONT, 54, 700, col(INK), ls=-1.2))
    kids.append(text("brand-subline", "brand-subline", c['subline'], NX + 122, 156, gen.UI_FONT, 22, 500, col(MUTED)))
    # DEPARTURES label with a "live" dot
    lab_y = 92
    hl = c.get('header_label', L['header'])
    kids.append(text("departures-label", "departures-label", hl, ROW_R, lab_y, gen.UI_FONT, 18, 600, col(MUTED), anchor='end', ls=3.5))
    hl_w = gen.measure([{"t": hl, "f": gen.UI_FONT, "w": 600, "s": 18, "ls": 3.5}])[0]
    dot_keys = []
    for i in range(int(T / 1200) + 1):
        tt = min(i * 1200, T)
        dot_keys.append(k(tt, 1 if i % 2 == 0 else 0.3, 'sine'))
    kids.append(circle("live-dot", "live-dot", ROW_R - hl_w - 16, lab_y - 6, 6, fill=col(A), anim={"compositing": {"opacity": ch(*dot_keys)}}))

    # category (8 flaps at the top right)
    cat_y = 108
    cat_x0 = ROW_R - (CAT_N * P - 4)
    cat_cells = [(cat_x0 + i * P, cat_y) for i in range(CAT_N)]
    cat_delay = -260
    cat_parts = [tiles("category-tiles", cat_cells)]
    for pi_, (pg, show) in enumerate([('a', False), ('b', True)]):
        cid = f"clip-category-{pg}"
        cat_parts.append(wipe_clip(cid, cat_x0 - 4, cat_x0 + CAT_N * P, cat_y - 2, CH + 4, show, U, cat_delay))
        t_ = mono(f"page-{pg}-category", c['pages'][pi_]['category'], text_x_left(cat_x0), baseline(cat_y), INK)
        cat_parts.append(group(f"page-{pg}-category-reveal", f"page-{pg}-category-reveal", [t_], clip=cid))
    cat_parts.append(hinges("category-hinges", cat_cells))
    fl = [flap(f"category-flap-{i+1:02d}", x, y, [cell_time(u, x, cat_delay) for u in U]) for i, (x, y) in enumerate(cat_cells)]
    g_fl = group("category-flaps", "category-flaps (split-flap mechanics)", fl); g_fl["locked"] = True
    cat_parts.append(g_fl)
    kids.append(group("category", "category", cat_parts))

    # column headers
    lab2 = 230
    labels = c.get('labels', L['labels'])
    kids.append(group("column-labels", "column-labels", [
        text(f"label-{cc['key']}", f"label-{cc['key']}", lab, XS[cc['key']] + 2, lab2, gen.UI_FONT, 16, 600, col(DIM), ls=3)
        for cc, lab in zip(COLS, labels)]))

    # ---- rows ----
    rows = []
    for r in range(6):
        y = RY0 + r * ROWP
        cells = cells_for_row(y)
        rd = r * RS
        parts = [tiles(f"row-{r+1}-tiles", cells)]
        for pi_, (pg, show) in enumerate([('a', False), ('b', True)]):
            vals = (c['pages'][pi_]['rows'][r] + [""] * len(COLS))[:len(COLS)]
            cid = f"clip-row-{r+1}-{pg}"
            parts.append(wipe_clip(cid, NX - 4, ROW_R + 4, y - 2, CH + 4, show, U, rd))
            pre = f"page-{pg}-row-{r+1}"
            texts = []
            for cc, v in zip(COLS, vals):
                right = cc.get('align') == 'right'
                x = text_x_right(XS[cc['key']], cc['n']) if right else text_x_left(XS[cc['key']])
                texts.append(mono(f"{pre}-{cc['key']}", v, x, baseline(y), AMBER if cc.get('color') == 'amber' else INK,
                                  anchor='end' if right else 'start', anim=blink(U, rd, pi_) if cc.get('blink') else None))
            parts.append(group(pre, pre, texts, clip=cid))
        parts.append(hinges(f"row-{r+1}-hinges", cells))
        fl = [flap(f"row-{r+1}-flap-{i+1:02d}", x, yy, [cell_time(u, x, rd) for u in U]) for i, (x, yy) in enumerate(cells)]
        g_fl = group(f"row-{r+1}-flaps", f"row-{r+1}-flaps (split-flap mechanics)", fl); g_fl["locked"] = True
        parts.append(g_fl)
        rows.append(group(f"row-{r+1}", f"row-{r+1}", parts))
    kids.append(group("rows", "rows", rows))

    # ---- footer: scrolling ticker and QR ----
    qr_s = 170
    qx, qy = ROW_R - qr_s, 846
    band_x0, band_x1, band_y, band_h = NX, qx - 34, 868, 84
    kids.append(rect("ticker-band", "ticker-band", band_x0, band_y, band_x1 - band_x0, band_h, 14, fill=col(A)))
    tick_clip = {"id": "clip-ticker", "type": "clipPath", "title": "ticker-mask", "properties": {"transform": gen.T0},
                 "children": [rect("clip-ticker-shape", "ticker-mask shape", band_x0 + 18, band_y, band_x1 - band_x0 - 36, band_h, 0, fill=col('#000000'))]}
    # two copies in a row: the group scrolls exactly one length in 24 s, so the loop has no jumps
    tw = round(len(c['ticker'] + "  ") * (0.6 * 34 + 1), 2)   # monospaced: exact width, trailing spaces included
    ty = band_y + band_h / 2 + 0.69 * 34 / 2
    tx0 = band_x0 + 18
    t1 = text("ticker-text", "ticker-text", c['ticker'], tx0, ty, FONT, 34, 600, col('#121315'), ls=1)
    t2 = text("ticker-text-2", "ticker-text-2 (same text, starts where ticker-text ends)", c['ticker'], tx0 + tw, ty, FONT, 34, 600, col('#121315'), ls=1)
    loop = group("ticker-loop", "ticker-loop", [t1, t2], tx0, ty, anim={
        "transform": {"origin": ch(k(0, O(tx0, ty), 'lin'), k(T, O(tx0 - tw, ty), 'lin'))}})
    kids.append(tick_clip)
    kids.append(group("ticker", "ticker", [loop], clip="clip-ticker"))
    kids.append(rect("qr-card", "qr-card", qx, qy, qr_s, qr_s, 18, fill=col('#F6F2EA')))
    kids.append(image("qr-code", "qr-code", data_uri(c['qr']), qx + 14, qy + 14, qr_s - 28, qr_s - 28))
    kids.append(text("footer-left", "footer-left", c['footer_left'], NX + 2, 1000, gen.UI_FONT, 19, 500, col(DIM)))
    kids.append(text("footer-right", "footer-right", c['footer_right'], band_x1, 1000, gen.UI_FONT, 18, 600, col(MUTED), anchor='end', ls=3))

    # ---- note for template users, outside the canvas ----
    nx, ny = W + 80, 60
    lines = [("HOW TO MAKE IT YOURS", 600, 20, INK, 2.2, 0),
             ("1  Retype any text in page-a and page-b.", 500, 22, INK, 0, 18),
             ("    Max characters: " + ", ".join(f"{cc['key']} {cc['n']}" for cc in COLS[:2]) + ",", 400, 22, MUTED, 0, 0),
             ("    " + ", ".join(f"{cc['key']} {cc['n']}" for cc in COLS[2:]) + ". Letters drop into", 400, 22, MUTED, 0, 0),
             ("    the flaps by themselves. Empty = blank.", 400, 22, MUTED, 0, 0),
             ("2  Keep Chivo Mono and its letter spacing:", 500, 22, INK, 0, 14),
             ("    they set the flap grid.", 400, 22, MUTED, 0, 0),
             ("3  Replace logo and qr-code (square).", 500, 22, INK, 0, 14),
             ("4  Brand color: ticker-band and live-dot.", 500, 22, INK, 0, 14),
             ("5  ticker-text runs twice for a seamless loop:", 500, 22, INK, 0, 14),
             ("    retype both copies.", 400, 22, MUTED, 0, 0),
             ("6  The board flips at 0.6 s and 12.6 s.", 500, 22, INK, 0, 14),
             ("    Flaps and masks are locked layers.", 400, 22, MUTED, 0, 0),
             ("This note sits outside the canvas, so it", 400, 19, MUTED, 0, 22),
             ("never shows up in exports.", 400, 19, MUTED, 0, 0)]
    nk, yy = [], ny + 58
    for i, (s, wgt, sz, colr, lsp, gap) in enumerate(lines):
        yy += gap + (sz * 1.45 if i else 0)
        nk.append(text(f"how-to-line-{i+1}", f"how-to-line-{i+1}", s, nx + 36, yy, gen.UI_FONT, sz, wgt, col(colr), ls=lsp))
    nh = yy - ny + 44
    kids.append(group("how-to", "how-to (outside canvas, not exported)",
                      [rect("how-to-card", "how-to-card", nx, ny, 540, nh, 24, fill=col('#F6F2EA')), *nk]))

    doc = {"type": "svg", "id": "departures-board",
           "animation": {"duration": T, "direction": 1, "iterations": 0, "fill": 1, "alternate": False, "speed": 1},
           "properties": {"shape": {"position": {"x": 0, "y": 0}, "size": {"width": W, "height": H}, "bgColor": col(BG)}},
           "children": kids}
    return doc, []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('set'); ap.add_argument('--out'); ap.add_argument('--create'); ap.add_argument('--replace'); ap.add_argument('--title')
    a = ap.parse_args()
    c = json.load(open(a.set if os.path.isabs(a.set) else os.path.join(ROOT, a.set)))
    doc, defs = build(c)
    if a.out:
        json.dump({"document": doc, "definitions": defs}, open(a.out, 'w'))
        print('written', a.out, os.path.getsize(a.out))
    if a.create or a.replace:
        from svg import call
        args = {"document": doc, "definitions": defs}
        if a.create:
            args["title"] = a.create; r = call('create_project', args)
        else:
            args["project_id"] = a.replace
            if a.title: args["title"] = a.title
            r = call('replace_project', args)
        print(json.dumps({kk: r[kk] for kk in ('id', 'title', 'editor_url') if kk in r}))


if __name__ == '__main__':
    main()
