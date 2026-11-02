#!/usr/bin/env python3
"""FEATURE DECK · 16:9 launch hero: a deck of cards; each click flings away the top card and reveals the next feature.

Segments (ms): intro 0-1300, then one card per click: stops at 1300, 2200, 3100 (the page pauses there),
call-to-action reveal 3100-4800, live 4800-7800 (loop).
"""
from kit import *

T = 7800
STOPS = [1300, 2200, 3100]      # one card every 0.9 s: the motion ends just before the stop
LIVE0 = 4800
CW, CHT = 560, 700
DCX, DCY = 1390, 560
X0, Y0 = DCX - CW // 2, DCY - CHT // 2
INK, MUTED, PAPER = '#17181C', '#5C5E66', '#F4EFE8'
HEAD = 'Bricolage Grotesque'
ROT = [-1.5, 3.5, -4.5, 6.5]
DY = [0, 18, 36, 54]
DX = [0, 12, -10, 16]
SC = [1, 0.968, 0.936, 0.904]
# the card slides sideways and fades: short travel and little area to repaint each frame (Safari)
TARGET = [((DCX + 500, DCY - 110), 15), ((DCX + 540, DCY + 120), -13), ((DCX + 480, DCY - 150), 18)]


def pose(depth, j):
    sg = 1 if (depth == 0 or j % 2 == 0) else -1
    return (DCX + DX[depth] * sg, DCY + DY[depth]), ROT[depth] * sg, SC[depth]


def card_anim(j):
    o, r, s = [], [], []
    deal = 150 + (3 - j) * 140
    off = (DCX + 760, 1520)
    p0 = pose(j, j)
    for t, (pp, rr, ss), e in [(0, (off, 28, 1), 'lin'), (deal, (off, 28, 1), 'snap'), (deal + 650, p0, 'lin')]:
        o.append((t, pp, e)); r.append((t, rr, e)); s.append((t, ss, e))
    for kk in range(min(j, 3)):
        a, b = pose(j - kk, j), pose(j - kk - 1, j)
        e = 'settle' if j - kk - 1 == 0 else 'glide'
        t0 = STOPS[kk] + 200
        for t, (pp, rr, ss), ee in [(t0, a, e), (t0 + 560, b, 'lin')]:
            o.append((t, pp, ee)); r.append((t, rr, ee)); s.append((t, ss, ee))
    if j < 3:
        t0 = STOPS[j]
        (tx, ty), trot = TARGET[j]
        p = pose(0, j)
        ant = ((DCX - 8, DCY - 12), p[1] - 2, 1.025)
        for t, (pp, rr, ss), ee in [(t0, p, 'out'), (t0 + 90, ant, 'swipe'), (t0 + 480, ((tx, ty), trot, 0.97), 'lin')]:
            o.append((t, pp, ee)); r.append((t, rr, ee)); s.append((t, ss, ee))
        opac = chan([(t0 + 140, 1, 'soft'), (t0 + 480, 0, 'lin')])
    else:
        p = pose(0, j)
        for t, (pp, rr, ss), ee in [(LIVE0, p, 'sine'), (LIVE0 + 1500, ((DCX, DCY - 12), -0.5, 1.01), 'sine'), (T, p, 'lin')]:
            o.append((t, pp, ee)); r.append((t, rr, ee)); s.append((t, ss, ee))
        opac = None
    anim = {"transform": {"origin": pos(o), "rotate": rot(r), "scale": scl(s)}}
    if opac: anim["compositing"] = {"opacity": opac}
    return anim


def build(c):
    A = c['accent']; g = c['deck']
    PALE = mix(A, '#FFFFFF', 0.8)
    kids, defs = [], []
    kids.append(rect("background", "background", 0, 0, W, H, fill=col('#F4EFE8')))     # flat color: cheap to repaint
    kids.append(ellipse("deck-shadow", "deck-shadow", DCX + 20, Y0 + CHT + 36, 330, 46, rad_grad([(0, '#3A2A18', 0.24), (1, '#3A2A18', 0)])))

    # ---------- text column ----------
    def rise(n_, t0, dy=26):
        x0, y0 = n_["properties"]["transform"]["origin"]["x"], n_["properties"]["transform"]["origin"]["y"]
        n_["animators"] = {"transform": {"origin": pos([(t0, (x0, y0 + dy), 'glide'), (t0 + 650, (x0, y0), 'lin')])},
                           "compositing": {"opacity": chan([(t0, 0, 'soft'), (t0 + 380, 1, 'lin')])}}
        n_["properties"]["compositing"] = {"opacity": 0}
        return n_
    copy = [rise(image("logo", "logo", data_uri(c['logo']), 146, 114, 60, 60), 80),
            rise(text("brand-name", "brand-name", c['brand'], 224, 156, HEAD, 32, 700, col(INK), ls=-0.5), 140),
]
    for i, s in enumerate(g['headline']):
        title = f"headline-line-{i+1}" + (" (brand color)" if i == 2 else "")
        copy.append(rise(text(f"headline-line-{i+1}", title, s, 138, 420 + i * 112, HEAD, 118, 800, col(A if i == 2 else INK), ls=-4), 320 + i * 80, 44))
    copy.append(rise(text("subhead", "subhead", g['subhead'], 144, 742, 'Geist', 28, 400, col(MUTED), ls=-0.2), 600))
    # progress: 4 segments + counter
    prog = []
    top_from = [0, STOPS[0] + 560, STOPS[1] + 560, STOPS[2] + 560]
    for i in range(4):
        x = 146 + i * 58
        prog.append(rect(f"progress-{i+1}", f"progress-{i+1}", x, 830, 46, 8, 4, fill=col('#DDD4C7')))
        keys = [(0, 0, 'lin'), (max(top_from[i] - 1, 0), 0, 'lin'), (top_from[i], 1, 'lin')]
        if i < 3: keys += [(top_from[i + 1] - 1, 1, 'lin'), (top_from[i + 1], 0, 'lin')]
        prog.append(rect(f"progress-{i+1}-on", f"progress-{i+1}-on (brand color)", x, 830, 46, 8, 4, fill=col(A), opacity=1 if i == 0 else 0,
                         anim={"compositing": {"opacity": chan(keys) if i else chan([(0, 1, 'lin'), (top_from[1] - 1, 1, 'lin'), (top_from[1], 0, 'lin')])}}))
        cnt_keys = [(0, 1 if i == 0 else 0, 'lin')]
        if i: cnt_keys += [(top_from[i] - 1, 0, 'lin'), (top_from[i], 1, 'lin')]
        if i < 3: cnt_keys += [(top_from[i + 1] - 1, 1, 'lin'), (top_from[i + 1], 0, 'lin')]
        prog.append(mono(f"counter-{i+1}", f"counter-{i+1}", f"0{i+1}", 146 + 4 * 58 + 18, 840, 17, col(INK), weight=700, ls=2, opacity=1 if i == 0 else 0,
                         anim={"compositing": {"opacity": chan(cnt_keys)}}))
    prog.append(mono("counter-total", "counter-total", "/ 04", 146 + 4 * 58 + 50, 840, 17, col(MUTED), ls=2))
    pg = group("progress", "progress", prog, 300, 834, anim={"compositing": {"opacity": chan([(700, 0, 'soft'), (1000, 1, 'lin')])}})
    pg["properties"]["compositing"] = {"opacity": 0}
    copy.append(pg)
    copy.append(text("hint-text", "hint-text", g['hint'], 146, 924, 'Geist', 22, 500, col(MUTED), opacity=0, anim={
        "compositing": {"opacity": chan([(0, 0, 'lin'), (900, 0, 'soft'), (1200, 1, 'lin'), (STOPS[2], 1, 'soft'), (STOPS[2] + 300, 0, 'lin')])}}))
    kids.append(group("copy", "copy", copy, 520, 540))

    # ---------- cards ----------
    fills = [(A, '#FFFFFF', '#FFFFFF', 0.86), (INK, A, '#F4EFE6', 0.7), (PALE, INK, INK, 0.75)]
    cards = []
    def drawn(t0, dur, ln):
        return {"stroke": {"dashOffset": chan([(0, ln, 'lin'), (t0, ln, 'soft'), (t0 + dur, 0, 'lin')])}}
    for j in range(4):
        n = j + 1
        if j < 3:
            bg, numc, tc, bodya = fills[j]
            body_col = col(tc, bodya)
        else:
            bg = '#FFFDF9'
        base = rect(f"card-{n}-paper", f"card-{n}-paper" + (" (brand color)" if j == 0 else ""), X0, Y0, CW, CHT, 34, fill=col(bg),
                    stroke=col('#E6DED2') if j == 3 else None, sw=1.5 if j == 3 else 0)
        sh = [rect(f"card-{n}-shadow", f"card-{n}-shadow", X0 + 8, Y0 + 16, CW - 16, CHT, 38, fill=col('#3A2A18'), opacity=0.11)]
        ck = [*sh, base]
        t_draw = 640 if j == 0 else STOPS[j - 1] + 260
        if j < 3:
            cd = g['cards'][j]
            ck += [text(f"card-{n}-number", f"card-{n}-number", f"0{n}", X0 + 40, Y0 + 196, HEAD, 196, 800, col(numc, 0.96), ls=-8),
                   text(f"card-{n}-title-1", f"card-{n}-title-1", cd['title'][0], X0 + 48, Y0 + 440, HEAD, 56, 700, col(tc), ls=-1.5),
                   text(f"card-{n}-title-2", f"card-{n}-title-2", cd['title'][1], X0 + 48, Y0 + 500, HEAD, 56, 700, col(tc), ls=-1.5),
                   text(f"card-{n}-body", f"card-{n}-body", cd['body'], X0 + 50, Y0 + 568, 'Geist', 23, 400, body_col, ls=-0.2),
                   mono(f"card-{n}-footer", f"card-{n}-footer", f"{g['footer']} · 0{n}/03", X0 + 50, Y0 + 650, 14, col(tc, 0.62), ls=3),
                   path(f"card-{n}-next", f"card-{n}-next", [(-12, 0), (12, 0), (3, -9), (12, 0), (3, 9)], X0 + CW - 60, Y0 + 645, stroke=col(tc, 0.7), sw=3)]
            ix, iy = X0 + 300, Y0 + 60
            if j == 0:     # chart with dashed forecast
                solid = [(0, 160), (40, 150, "cusp", None, (60, 140)), (95, 112, "cusp", (75, 122), (110, 104)), (140, 90)]
                ck += [path("card-1-chart", "card-1-chart", solid, ix, iy, stroke=col('#FFFFFF'), sw=6, dash=230, anim=drawn(t_draw, 300, 230)),
                       path("card-1-forecast", "card-1-forecast", [(140, 90), (176, 66), (212, 30)], ix, iy, stroke=col('#FFFFFF', 0.85), sw=6,
                            anim={"compositing": {"opacity": chan([(0, 0, 'lin'), (t_draw + 260, 0, 'soft'), (t_draw + 430, 1, 'lin')])}}),
                       circle("card-1-dot", "card-1-dot", ix + 212, iy + 30, 11, fill=col('#FFFFFF'), anim={
                           "transform": {"scale": scl([(t_draw + 360, 0.01, 'over'), (t_draw + 580, 1, 'lin')])}})]
                ck[-2]["properties"]["stroke"].update({"dashArray": [1, 14], "dashOffset": 0})
                ck[-2]["properties"]["compositing"] = {"opacity": 0}
            elif j == 1:   # speech bubble with text lines
                bub = rr_path(0, 0, 212, 130, 24)
                ck.append(path("card-2-bubble", "card-2-bubble (brand color)", bub + [(40, 130), (24, 166), (76, 130)], ix, iy + 10, stroke=col(A), sw=5,
                               dash=720, anim=drawn(t_draw, 380, 720)))
                for li, wl in enumerate([150, 118, 70]):
                    ck.append(path(f"card-2-line-{li+1}", f"card-2-line-{li+1}", [(0, 0), (wl, 0)], ix + 30, iy + 48 + li * 30, stroke=col('#F4EFE6', 0.9), sw=7,
                                   dash=wl + 10, anim=drawn(t_draw + 260 + li * 80, 200, wl + 10)))
            else:          # paper plane with trail
                plane = [(0, 60), (150, 0), (96, 120), (70, 78), (0, 60)]
                ck += [path("card-3-trail", "card-3-trail (brand color)", [(-10, 160, "cusp", None, (40, 120)), (60, 150, "cusp", (30, 175), (90, 130)), (120, 110)],
                            ix - 40, iy + 30, stroke=col(A), sw=4,
                            anim={"compositing": {"opacity": chan([(0, 0, 'lin'), (t_draw + 220, 0, 'soft'), (t_draw + 420, 1, 'lin')])}}),
                       path("card-3-plane", "card-3-plane", plane, ix + 60, iy, stroke=col(INK), sw=5, fill=col('#FFFFFF', 0.6), dash=460, anim={
                           **drawn(t_draw, 340, 460),
                           "transform": {"origin": pos([(t_draw, (ix + 30, iy + 30), 'glide'), (t_draw + 560, (ix + 60, iy), 'lin')])}})]
                ck[-2]["properties"]["stroke"].update({"dashArray": [10, 10], "dashOffset": 0})
                ck[-2]["properties"]["compositing"] = {"opacity": 0}
        else:
            sw_, sh_ = 480, 300
            sx, sy = X0 + 40, Y0 + 40
            defs.append(clip_def("clip-cta-shot", "product-image-mask", sx, sy, sw_, sh_, 18))
            t_c = STOPS[2] + 820
            ck += [group("product-image-reveal", "product-image-reveal", [image("product-image", "product-image", data_uri(c['screenshot']), sx, sy, sw_, sh_, fit="xMidYMid slice")],
                         sx + sw_ / 2, sy + sh_ / 2, clip="clip-cta-shot"),
                   rect("cta-shot-frame", "cta-shot-frame", sx, sy, sw_, sh_, 18, stroke=col('#E6DED2'), sw=1.5),
                   text("cta-title-1", "cta-title-1", g['cta_title'][0], X0 + 44, Y0 + 440, HEAD, 62, 800, col(INK), ls=-2),
                   text("cta-title-2", "cta-title-2 (brand color)", g['cta_title'][1], X0 + 44, Y0 + 508, HEAD, 62, 800, col(A), ls=-2)]
            btn = group("cta", "cta", [
                rect("cta-button", "cta-button (brand color)", X0 + 44, Y0 + 568, 320, 84, 42, fill=col(A)),
                text("cta-label", "cta-label", g['cta'], X0 + 80, Y0 + 621, 'Geist', 27, 600, col('#FFFFFF'), ls=-0.2),
                path("cta-arrow", "cta-arrow", [(-10, 0), (10, 0), (2, -8), (10, 0), (2, 8)], X0 + 44 + 320 - 42, Y0 + 610, stroke=col('#FFFFFF'), sw=3.4)],
                X0 + 44 + 160, Y0 + 610, anim={"transform": {"scale": scl([(0, 0.01, 'lin'), (t_c, 0.01, 'over'), (t_c + 450, 1, 'lin'),
                                                                           (LIVE0, 1, 'sine'), (LIVE0 + 700, 1.05, 'sine'), (LIVE0 + 1400, 1, 'lin')])}})
            btn["properties"]["transform"]["scale"] = S(0.01)
            ck += [btn, mono("cta-url", "cta-url", g['cta_url'], X0 + CW - 44, Y0 + 618, 16, col(MUTED), anchor='end', ls=1.5)]
        cg = group(f"card-{n}", f"card-{n}", ck, DCX, DCY, anim=card_anim(j))
        cards.append(cg)
    kids.append(group("deck", "deck", list(reversed(cards)), DCX, DCY))

    kids.append(howto([
        "1  Retype headline, subhead, card-1..3 titles/body/footer,",
        "    cta-title-1/2, cta-label, cta-url.",
        "2  Replace logo (square) and product-image (16:10) on card 4.",
        "3  Brand color: card-1-paper and every layer marked (brand color).",
        "4  Player API: pause at 1.3, 2.2 and 3.1 s; each click plays to the",
        "    next stop. After the last card: 3.1-4.8 s, then loop 4.8-7.8 s.",
        "5  The card illustrations are paths: redraw them for your features.",
    ]))
    d = doc(kids, T, '#EFE9DF')
    meta = {"T": T, "stops": STOPS, "segments": {"intro": [0, STOPS[0]], "cta": [STOPS[2], LIVE0], "live": [LIVE0, T]},
            "hit": {"deck": [X0 - 40, Y0 - 40, X0 + CW + 40, Y0 + CHT + 60]}}
    return d, defs, meta


if __name__ == '__main__':
    d, defs, meta = cli(build, 'deck')
    print('layers, animated, keyframes:', count(d))
