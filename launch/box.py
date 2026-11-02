#!/usr/bin/env python3
"""TEAR-OPEN BOX · 16:9 launch hero: pull the tab, the strip tears at the pace of your finger, the box opens.

Segments (ms) for the Player API: intro 0-1000, idle 1000-1800 (loop), tear 1800-3800 (scrub by dragging),
open 3800-6800, live 6800-9800 (loop).
"""
import math, random
from kit import *

T = 9800
INTRO, IDLE0, IDLE1, TEAR0, TEAR1, LIVE0 = 1000, 1000, 1800, 1800, 3800, 6800
X0, Y0, BW, BH = 260, 150, 1400, 840
SEAM = Y0 + BH // 2            # 570
SH = 56                        # strip height
SY = SEAM - SH // 2            # 542
TABLE, INK = '#E8E0D2', '#2B2118'
KRAFT_T = [(0, '#D3AE83'), (1, '#C79D6F')]
KRAFT_B = [(0, '#C99F71'), (1, '#BD9264')]
EDGE = '#A27850'
STENCIL = 'Big Shoulders Stencil'


def build(c):
    A = c['accent']; g = c['box']
    kids, defs = [], []
    kids.append(rect("background", "background", 0, 0, W, H, fill=rad_grad([(0, '#F1EBE0'), (1, '#DDD3C3')], 0.5, 0.45, 0.8)))

    box_kids = []
    box_kids.append(rect("box-shadow", "box-shadow", X0 + 6, Y0 + 34, BW, BH, 18, fill=col('#3B2A18'), opacity=0.32,
                         filt=[{"type": "blur", "value": {"x": 34, "y": 34}}]))

    # ---------- interior (visible when the flaps open) ----------
    inner = [rect("box-interior", "box-interior", X0, Y0, BW, BH, 14, fill=lin_grad([(0, '#3E2C1C'), (1, '#251910')])),
             rect("box-interior-shade", "box-interior-shade", X0, Y0, BW, 160, 14, fill=lin_grad([(0, '#000000', 0.45), (1, '#000000', 0)]))]
    CXI, CYI = X0 + BW / 2, Y0 + BH / 2 + 20
    defs.append(clip_def("clip-interior", "box-interior-mask", X0, Y0, BW, BH, 14))
    rays = []
    for i in range(8):
        a0 = math.radians(i * 45)
        L, hw = 1000, math.radians(5.5)
        pts = [(0, 0), (L * math.cos(a0 - hw), L * math.sin(a0 - hw)), (L * math.cos(a0 + hw), L * math.sin(a0 + hw)), (0, 0)]
        rays.append(path(f"ray-{i+1}", f"ray-{i+1}", pts, CXI, CYI, fill=col(mix(A, '#FFF3DF', 0.55), 0.16)))
    ray_g = group("light-rays", "light-rays", rays, CXI, CYI, anim={
        "transform": {"rotate": rot([(TEAR1 + 300, -40, 'lin'), (LIVE0, 0, 'lin'), (T, 45, 'lin')], 'lin'),
                      "scale": scl([(TEAR1 + 300, 0.4, 'glide'), (TEAR1 + 1400, 1, 'lin')])},
        "compositing": {"opacity": chan([(0, 0, 'lin'), (TEAR1 + 300, 0, 'soft'), (TEAR1 + 1100, 1, 'lin')])}})
    ray_g["properties"]["compositing"] = {"opacity": 0}
    glow = ellipse("glow", "glow (brand color)", CXI, CYI, 520, 360, col(A), opacity=0, filt=[{"type": "blur", "value": {"x": 120, "y": 120}}], anim={
        "compositing": {"opacity": chan([(0, 0, 'lin'), (TEAR1 + 200, 0, 'soft'), (TEAR1 + 900, 0.55, 'sine'), (LIVE0, 0.38, 'sine'),
                                          (LIVE0 + 1500, 0.5, 'sine'), (T, 0.38, 'lin')])}})
    inner.append(group("interior-light", "interior-light", [glow, ray_g], CXI, CYI, clip="clip-interior"))
    inner.append(rect("box-walls", "box-walls", X0, Y0, BW, BH, 14, stroke=col('#9E7650'), sw=10))

    # product
    ww, bar = 880, 50
    ih = round(ww * 10 / 16); wh = bar + ih
    wx, wy = CXI - ww / 2, Y0 + 110
    wcx, wcy = wx + ww / 2, wy + wh / 2
    defs.append(gen.clip_def_bottom_round("clip-window", "product-image-mask", wx, wy + bar, ww, ih, 18))
    wsh = rect("window-shadow", "window-shadow", wx + 20, wy + 40, ww - 40, wh - 20, 20, fill=col('#000000'), opacity=0.5,
               filt=[{"type": "blur", "value": {"x": 30, "y": 30}}])
    frame = rect("window-frame", "window-frame", wx, wy, ww, wh, 18, fill=col('#FBF8F2'), stroke=col('#E3D9CA'), sw=1.5)
    dots = [circle(f"window-dot-{i+1}", f"window-dot-{i+1}", wx + 28 + i * 20, wy + bar / 2, 6, fill=col('#E2D9CC')) for i in range(3)]
    pill = rect("url-pill", "url-pill", wcx - 180, wy + 11, 360, 28, 14, fill=col('#F0EAE0'))
    url = mono("window-url", "window-url", c['url'], wcx, wy + 31, 15, col('#6B6D74'), anchor='middle', ls=0.5)
    shot = image("product-image", "product-image", data_uri(c['screenshot']), wx, wy + bar, ww, ih, fit="xMidYMid slice")
    shot_g = group("product-image-reveal", "product-image-reveal", [shot], wcx, wy + bar + ih / 2, clip="clip-window")
    t_w = TEAR1 + 500
    win = group("product-window", "product-window", [wsh, frame, *dots, pill, url, shot_g], wcx, wcy, anim={
        "transform": {"origin": pos([(t_w, (wcx, wcy + 180), 'over'), (t_w + 800, (wcx, wcy), 'sine'),
                                     (LIVE0, (wcx, wcy), 'sine'), (LIVE0 + 1500, (wcx, wcy - 8), 'sine'), (T, (wcx, wcy), 'lin')]),
                      "scale": scl([(t_w, 0.5, 'snap'), (t_w + 800, 1, 'lin')]),
                      "rotate": rot([(t_w, -4, 'soft'), (t_w + 900, 0, 'lin')])},
        "compositing": {"opacity": chan([(0, 0, 'lin'), (t_w, 0, 'soft'), (t_w + 250, 1, 'lin')])}})
    win["properties"]["compositing"] = {"opacity": 0}
    inner.append(win)
    box_kids.append(group("box-inside", "box-inside", inner, CXI, CYI))

    # ---------- strip, torn edges, light in the gap ----------
    box_kids.append(rect("strip-gap", "strip-gap", X0, SY, BW, SH, 0, fill=col('#22170E'), anim={
        "compositing": {"opacity": chan([(TEAR1 + 150, 1, 'soft'), (TEAR1 + 450, 0, 'lin')])}}))
    box_kids.append(rect("strip-light", "strip-light (brand color)", X0, SEAM - 7, BW, 14, 7, fill=col(A), opacity=0,
                         filt=[{"type": "blur", "value": {"x": 6, "y": 6}}], anim={
        "compositing": {"opacity": chan([(0, 0, 'lin'), (TEAR0, 0.25, 'lin'), (TEAR1, 0.95, 'soft'), (TEAR1 + 450, 0, 'lin')])}}))

    def mask(id_, x_from, x_to, w_from, w_to, y, h):
        r = {"id": id_ + "-shape", "type": "rect", "title": id_ + " shape",
             "properties": {"shape": {"size": {"width": w_from, "height": h}, "radius": {"x": 0, "y": 0}},
                            "transform": {"origin": O(x_from, y), "translate": {"x": 0, "y": 0}, "scale": S(1), "skew": {"x": 0, "y": 0}, "rotate": 0},
                            "fill": {"paint": col('#000000'), "opacity": 1}},
             "animators": {"transform": {"origin": pos([(0, (x_from, y), 'lin'), (TEAR0, (x_from, y), 'lin'), (TEAR1, (x_to, y), 'lin')])},
                           "shape": {"size": ch(k(0, {"width": w_from, "height": h}, 'lin'), k(TEAR0, {"width": w_from, "height": h}, 'lin'),
                                                k(TEAR1, {"width": w_to, "height": h}, 'lin'))}}}
        m = {"id": id_, "type": "clipPath", "title": id_, "properties": {"transform": gen.T0}, "children": [r]}
        m["locked"] = True
        return m

    box_kids.append(mask("strip-mask", X0, X0 + BW, BW, 0.01, SY - 6, SH + 12))
    rnd = random.Random(5)
    def ragged(y0, sgn):
        pts, x = [], 0
        while x <= BW:
            pts.append((x, sgn * rnd.uniform(0, 5)))
            x += rnd.uniform(7, 13)
        return pts
    box_kids.append(mask("torn-mask", X0 - 10, X0 - 10, 0.01, BW + 20, SY - 12, SH + 24))
    torn = group("torn-edges", "torn-edges", [
        path("torn-edge-top", "torn-edge-top", ragged(SY, 1), X0, SY + 2, stroke=col('#ECD7B6'), sw=4, cap='round'),
        path("torn-edge-bottom", "torn-edge-bottom", ragged(SY + SH, -1), X0, SY + SH - 2, stroke=col('#ECD7B6'), sw=4, cap='round')],
        X0 + BW / 2, SEAM, clip="torn-mask", anim={"compositing": {"opacity": chan([(TEAR1 + 100, 1, 'soft'), (TEAR1 + 400, 0, 'lin')])}})

    strip = group("tear-strip", "tear-strip", [
        rect("strip-paper", "strip-paper", X0, SY, BW, SH, 0, fill=col('#DFC198')),
        path("strip-perf-top", "strip-perf-top", [(0, 0), (BW, 0)], X0, SY + 3, stroke=col('#8F6A45'), sw=2.2),
        path("strip-perf-bottom", "strip-perf-bottom", [(0, 0), (BW, 0)], X0, SY + SH - 3, stroke=col('#8F6A45'), sw=2.2),
        mono("strip-text", "strip-text (repeats: keep it short)", ("      ".join([g['strip']] * 9)), X0 + 160, SEAM + 6, 16, col('#6E5134'), weight=600, ls=3),
    ], X0 + BW / 2, SEAM, clip="strip-mask")
    for p_ in strip["children"][1:3]:
        p_["properties"]["stroke"].update({"dashArray": [9, 6], "dashOffset": 0, "lineCap": "butt"})

    # ---------- flaps ----------
    fold_t = TEAR1 + 120
    # top flap: print
    top_print = []
    h1 = text("headline", "headline (stencil print, up to 9 characters)", g['headline'], 326, 446, STENCIL, 190, 800, col(INK, 0.9), ls=2)
    sub = mono("subline", "subline", g['subline'], 334, 500, 18, col(INK, 0.68), weight=600, ls=3.2)
    top_print += [h1, sub]
    # shipping label
    lx, ly, lw, lh = 1200, 196, 390, 300
    lab_kids = [rect("label-paper", "label-paper", lx, ly, lw, lh, 8, fill=col('#F8F3EA'), stroke=col('#DCCFBC'), sw=1.5,
                     filt=[{"type": "drop-shadow", "value": {"blur": {"x": 6, "y": 6}, "offset": {"x": 0, "y": 4}, "color": {"r": 60, "g": 40, "b": 20, "a": 0.18}}}]),
                image("logo", "logo", data_uri(c['logo']), lx + 26, ly + 26, 56, 56),
                text("brand-name", "brand-name", c['brand'], lx + 96, ly + 66, 'Bricolage Grotesque', 30, 700, col(INK), ls=-0.5),
                mono("label-title", "label-title (brand color)", g['label_title'], lx + 26, ly + 122, 15, col(A), weight=700, ls=3),
                path("label-rule", "label-rule", [(0, 0), (lw - 52, 0)], lx + 26, ly + 140, stroke=col('#DCCFBC'), sw=1.5),
                mono("label-ship-to", "label-ship-to", "SHIP TO", lx + 26, ly + 172, 13, col('#8A7F70'), ls=2.5),
                text("label-ship-to-value", "label-ship-to-value", g['ship_to'], lx + 26, ly + 202, 'Geist', 22, 600, col(INK))]
    rb = random.Random(3); bxx = lx + 26
    bars = []
    while bxx < lx + lw - 40:
        wbar = rb.choice([2, 3, 3, 5, 7])
        bars.append(rect(f"barcode-{len(bars)+1}", f"barcode-{len(bars)+1}", bxx, ly + 226, wbar, 46, 0, fill=col(INK)))
        bxx += wbar + rb.choice([3, 4, 6])
    lab_kids.append(group("label-barcode", "label-barcode", bars, lx + lw / 2, ly + 249))
    lab_kids.append(mono("label-count", "label-count", "1 OF 1", lx + lw - 26, ly + 122, 13, col('#8A7F70'), anchor='end', ls=2.5))
    label = group("shipping-label", "shipping-label", lab_kids, lx + lw / 2, ly + lh / 2, anim={
        "transform": {"scale": scl([(620, 1.35, 'snap'), (880, 1, 'lin')]), "rotate": rot([(620, -8, 'snap'), (880, -2.5, 'lin')])},
        "compositing": {"opacity": chan([(0, 0, 'lin'), (620, 0, 'lin'), (660, 1, 'lin')])}})
    label["properties"]["transform"]["rotate"] = -2.5
    label["properties"]["compositing"] = {"opacity": 0}
    top_print.append(label)
    # bottom flap: stamp, arrows, instruction
    stamp = group("fragile-stamp", "fragile-stamp (brand color)", [
        rect("stamp-frame", "stamp-frame", 330, 650, 610, 112, 10, stroke=col(A), sw=5),
        text("stamp-text", "stamp-text", g['stamp'], 362, 734, STENCIL, 76, 800, col(A), ls=3),
        mono("stamp-sub", "stamp-sub", g['stamp_sub'], 646, 713, 17, col(A), weight=700, ls=2.2),
    ], 635, 706)
    stamp["properties"]["transform"]["rotate"] = -4
    stamp["properties"]["compositing"] = {"opacity": 0.92}
    arrows = []
    for i in range(2):
        ax = 1420 + i * 52
        arrows.append(path(f"up-arrow-{i+1}", f"up-arrow-{i+1}", [(0, 34), (0, -30), (-16, -12), (0, -30), (16, -12)], ax, 710, stroke=col(INK, 0.75), sw=6, cap='round'))
    side = mono("this-side-up", "this-side-up", "THIS SIDE UP", 1380, 790, 16, col(INK, 0.7), weight=600, ls=3)
    hint = text("hint-text", "hint-text", g['hint'], 334, 902, 'Geist', 24, 600, col(INK, 0.62), anim={
        "compositing": {"opacity": chan([(IDLE0, 0.6, 'sine'), ((IDLE0 + IDLE1) / 2, 0.25, 'sine'), (IDLE1, 0.6, 'lin')])}})
    bot_print = [stamp, *arrows, side, hint]

    def build_flap(name, y, h, grad_, hinge, prints, t0, dy_sep):
        face = group(f"{name}-face", f"{name}-face", [rect(f"{name}-paper", f"{name}-paper", X0, y, BW, h, 0, fill=lin_grad(grad_)), *prints,
                                                      rect(f"{name}-edge", f"{name}-edge", X0, y, BW, h, 0, stroke=col(EDGE), sw=2)],
                     X0 + BW / 2, hinge, anim={"compositing": {"opacity": chan([(t0 + 430, 1, 'step'), (t0 + 440, 0, 'lin')])}})
        shade = rect(f"{name}-shade", f"{name}-shade", X0, y, BW, h, 0, fill=col('#1A0F06'), opacity=0, anim={
            "compositing": {"opacity": chan([(0, 0, 'lin'), (t0, 0, 'in'), (t0 + 430, 0.55, 'lin'), (t0 + 440, 0, 'lin')])}})
        fy0, fy1 = (0, 1) if hinge == Y0 else (1, 0)
        under = rect(f"{name}-underside", f"{name}-underside", X0, y, BW, h, 0, fill=lin_grad([(0, '#8C6440'), (0.55, '#B08659'), (1, '#C59D70')], 0, fy0, 0, fy1), stroke=col('#D9BC93'), sw=3, opacity=0, anim={
            "compositing": {"opacity": chan([(0, 0, 'lin'), (t0 + 430, 0, 'step'), (t0 + 440, 1, 'lin')])}})
        return group(name, name, [face, shade, under], X0 + BW / 2, hinge, anim={
            "transform": {"origin": pos([(0, (X0 + BW / 2, hinge), 'lin'), (TEAR0, (X0 + BW / 2, hinge), 'lin'), (TEAR1, (X0 + BW / 2, hinge + dy_sep), 'lin')]),
                          "scale": scl([(t0, (1, 1), 'in'), (t0 + 440, (1, 0.02), 'out'), (t0 + 900, (1, -0.3), 'lin')])}})
    flap_top = build_flap("flap-top", Y0, BH // 2 - SH // 2 + 0, KRAFT_T, Y0, top_print, fold_t, -6)
    flap_bot = build_flap("flap-bottom", SEAM + SH // 2, BH // 2 - SH // 2, KRAFT_B, Y0 + BH, bot_print, fold_t + 90, 6)
    # the flaps cover half the box minus half the strip: the strip sits in the gap
    box_kids += [flap_top, flap_bot, torn, strip]

    # ---------- tab that follows the tear ----------
    tab_kids = [
        path("strip-curl", "strip-curl", [(0, -28), (0, 28), (-30, 22), (-26, -22), (0, -28)], X0, SEAM, fill=col('#B89064')),
        rect("tab", "tab (brand color)", X0 - 150, SEAM - 38, 160, 76, 16, fill=col(A),
             filt=[{"type": "drop-shadow", "value": {"blur": {"x": 10, "y": 10}, "offset": {"x": 0, "y": 6}, "color": {"r": 40, "g": 20, "b": 5, "a": 0.3}}}]),
        mono("tab-label", "tab-label", "PULL", X0 - 116, SEAM + 8, 22, col('#FFFFFF'), weight=700, ls=3),
        path("tab-arrow", "tab-arrow", [(-10, 0), (10, 0), (2, -8), (10, 0), (2, 8)], X0 - 26, SEAM, stroke=col('#FFFFFF'), sw=3.4),
    ]
    tab = group("pull-tab", "pull-tab", tab_kids, X0, SEAM, anim={
        "transform": {"origin": pos([(0, (X0 - 220, SEAM), 'lin'), (700, (X0 - 220, SEAM), 'over'), (INTRO, (X0, SEAM), 'sine'),
                                     ((IDLE0 + IDLE1) / 2, (X0 + 16, SEAM), 'sine'), (IDLE1, (X0, SEAM), 'lin'),
                                     (TEAR1, (X0 + BW, SEAM), 'whip'), (TEAR1 + 520, (X0 + BW + 260, SEAM + 240), 'lin')]),
                      "rotate": rot([(IDLE0, 0, 'sine'), ((IDLE0 + IDLE1) / 2, -3, 'sine'), (IDLE1, 0, 'lin'), (TEAR1, 0, 'in'), (TEAR1 + 520, 38, 'lin')])},
        "compositing": {"opacity": chan([(0, 0, 'lin'), (700, 0, 'soft'), (820, 1, 'lin'), (TEAR1 + 250, 1, 'in'), (TEAR1 + 520, 0, 'lin')])}})
    tab["properties"]["compositing"] = {"opacity": 0}
    box_kids.append(tab)

    # ---------- stickers ----------
    def sticker_anim(t0, x, y, r_end):
        return {"transform": {"scale": scl([(t0, 1.9, 'over'), (t0 + 330, 1, 'lin')]),
                              "rotate": rot([(t0, r_end + 14, 'snap'), (t0 + 330, r_end, 'lin')])},
                "compositing": {"opacity": chan([(0, 0, 'lin'), (t0, 0, 'lin'), (t0 + 60, 1, 'lin')])}}
    st = []
    bcx, bcy, br = wx + 60, wy + 30, 118
    t_b = t_w + 700
    badge = group("badge", "badge (brand color)", [
        circle("badge-disc", "badge-disc", bcx, bcy, br, fill=col(A), stroke=col('#FFFFFF'), sw=7),
        mono("badge-line-1", "badge-line-1", g['badge'][0], bcx, bcy - 46, 17, col('#FFFFFF'), weight=700, anchor='middle', ls=4),
        text("badge-line-2", "badge-line-2", g['badge'][1], bcx, bcy + 34, 'Bricolage Grotesque', 92, 800, col('#FFFFFF'), anchor='middle', ls=-3),
        mono("badge-line-3", "badge-line-3", g['badge'][2], bcx, bcy + 72, 15, col('#FFFFFF'), weight=700, anchor='middle', ls=3.5),
    ], bcx, bcy, anim=sticker_anim(t_b, bcx, bcy, -10))
    badge["properties"]["transform"]["rotate"] = -10
    badge["properties"]["compositing"] = {"opacity": 0}
    st.append(badge)
    spots = [(wx + ww - 10, wy + 120, 4), (wx + 30, wy + wh * 0.62, -4), (wx + ww - 40, wy + wh - 70, 3)]
    for i, (sx, sy_, rr) in enumerate(spots):
        n = i + 1; sw_, sh_ = 420, 84
        t0 = t_b + 150 + i * 130
        s = group(f"feature-{n}", f"feature-{n}", [
            rect(f"feature-{n}-card", f"feature-{n}-card", sx - sw_ / 2, sy_ - sh_ / 2, sw_, sh_, 16, fill=col('#FFFDF8'), stroke=col('#FFFFFF'), sw=6,
                 filt=[{"type": "drop-shadow", "value": {"blur": {"x": 14, "y": 14}, "offset": {"x": 0, "y": 8}, "color": {"r": 30, "g": 18, "b": 6, "a": 0.35}}}]),
            circle(f"feature-{n}-dot", f"feature-{n}-dot (brand color)", sx - sw_ / 2 + 38, sy_, 15, fill=col(A)),
            path(f"feature-{n}-check", f"feature-{n}-check", [(-6, 0.5), (-2, 5), (6.5, -5)], sx - sw_ / 2 + 38, sy_, stroke=col('#FFFFFF'), sw=3),
            text(f"feature-{n}-label", f"feature-{n}-label", c['features'][i], sx - sw_ / 2 + 66, sy_ + 9, 'Geist', 25, 600, col(INK), ls=-0.2),
        ], sx, sy_, anim=sticker_anim(t0, sx, sy_, rr))
        s["properties"]["transform"]["rotate"] = rr
        s["properties"]["compositing"] = {"opacity": 0}
        st.append(s)
    ccx, ccy, cw, chh = wcx, wy + wh + 6, 440, 92
    t_c = t_b + 650
    cta = group("cta", "cta", [
        rect("cta-button", "cta-button (brand color)", ccx - cw / 2, ccy - chh / 2, cw, chh, chh / 2, fill=col(A), stroke=col('#FFFFFF'), sw=6,
             filt=[{"type": "drop-shadow", "value": {"blur": {"x": 16, "y": 16}, "offset": {"x": 0, "y": 10}, "color": {"r": 30, "g": 18, "b": 6, "a": 0.4}}}]),
        text("cta-label", "cta-label", c['cta'], ccx - cw / 2 + 50, ccy + 10, 'Geist', 29, 600, col('#FFFFFF'), ls=-0.2),
        path("cta-arrow", "cta-arrow", [(-11, 0), (11, 0), (2, -9), (11, 0), (2, 9)], ccx + cw / 2 - 50, ccy, stroke=col('#FFFFFF'), sw=3.6),
    ], ccx, ccy, anim={"transform": {"scale": scl([(t_c, 0.6, 'over'), (t_c + 420, 1, 'lin'),
                                                   (LIVE0, 1, 'sine'), (LIVE0 + 750, 1.04, 'sine'), (LIVE0 + 1500, 1, 'sine'), (T, 1, 'lin')])},
                       "compositing": {"opacity": chan([(0, 0, 'lin'), (t_c, 0, 'lin'), (t_c + 120, 1, 'lin')])}})
    cta["properties"]["compositing"] = {"opacity": 0}
    st.append(cta)
    box_kids.append(group("stickers", "stickers", st, CXI, CYI))

    kids.append(group("box", "box", box_kids, X0 + BW / 2, SEAM, anim={
        "transform": {"origin": pos([(0, (X0 + BW / 2, SEAM + 90), 'glide'), (800, (X0 + BW / 2, SEAM), 'lin')]),
                      "scale": scl([(0, 0.96, 'glide'), (800, 1, 'lin')])},
        "compositing": {"opacity": chan([(0, 0, 'soft'), (380, 1, 'lin')])}}))
    kids[-1]["properties"]["compositing"] = {"opacity": 0}

    kids.append(howto([
        "1  Retype the stencil headline, subline, label texts,",
        "    stamp, badge-line-1..3, feature-1..3-label, cta-label.",
        "2  Replace logo (square) and product-image",
        "    (16:10 screenshot, 1600 x 1000).",
        "3  Brand color: every layer marked (brand color).",
        "4  Player API segments: idle 1-1.8 s (loop), tear 1.8-3.8 s",
        "    (scrub it with the pointer), open 3.8-6.8 s, live 6.8-9.8 s.",
        "5  strip-mask and torn-mask follow the tear: leave them as they are.",
    ]))
    d = doc(kids, T, '#E4DBCC')
    meta = {"T": T, "segments": {"intro": [0, INTRO], "idle": [IDLE0, IDLE1], "tear": [TEAR0, TEAR1], "open": [TEAR1, LIVE0], "live": [LIVE0, T]},
            "strip": {"x0": X0, "x1": X0 + BW, "y0": SY - 50, "y1": SY + SH + 50, "tab_x0": X0 - 160}, "commit": 0.8}
    return d, defs, meta


if __name__ == '__main__':
    d, defs, meta = cli(build, 'box')
    print('layers, animated, keyframes:', count(d))
