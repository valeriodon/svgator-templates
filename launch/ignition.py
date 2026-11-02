#!/usr/bin/env python3
"""IGNITION · 16:9 launch hero: hold the button, the ring charges, at full charge the product launches.

Segments (ms) for the Player API (see meta): intro 0-900, idle 900-1400 (loop), charge 1400-3400
(reversible: if you let go, the page plays back), launch 3400-6000, live 6000-9000 (loop).
"""
import math, random
from kit import *

T = 9000
INTRO, IDLE0, IDLE1, CH0, CH1, LIVE0 = 900, 900, 1400, 1400, 3400, 6000
CX, CY = 1400, 540
BG0, BG1 = '#211C17', '#100E0C'
PANEL, LINE, DIM = '#1E1A16', '#3B342D', '#2B2520'
CREAM, MUTED = '#F4EDE2', '#A39A8F'
R_ARC = 232
L_ARC = round(2 * math.pi * R_ARC, 1)


def build(c):
    A = c['accent']; g = c['ignition']
    LIGHT, DARK = mix(A, '#FFFFFF', 0.28), mix(A, '#000000', 0.38)
    kids, defs = [], []

    # ---------- background ----------
    kids.append(rect("background", "background", 0, 0, W, H, fill=rad_grad([(0, BG0), (1, BG1)], 0.72, 0.5, 0.78)))
    gl = ellipse("glow", "glow (brand color)", CX, CY, 400, 400, col(A), filt=[{"type": "blur", "value": {"x": 110, "y": 110}}], anim={
        "compositing": {"opacity": chan([(0, 0), (INTRO, 0.10, 'sine'), ((IDLE0 + IDLE1) / 2, 0.16, 'sine'), (IDLE1, 0.10, 'lin'),
                                          (CH1, 0.55, 'snap'), (CH1 + 100, 0.85, 'out'), (4300, 0.24, 'sine'),
                                          (LIVE0, 0.24, 'sine'), (7500, 0.32, 'sine'), (T, 0.24, 'lin')], 'lin')}}, opacity=0)
    kids.append(gl)
    # dial guides (drawn on at startup)
    gh = path("guide-h", "guide-h", [(0, 0), (880, 0)], 960, CY, stroke=col(DIM), sw=1.5, dash=900,
              anim={"stroke": {"dashOffset": chan([(0, 900, 'glide'), (800, 0)])}})
    gv = path("guide-v", "guide-v", [(0, 0), (0, 880)], CX, 100, stroke=col(DIM), sw=1.5, dash=900,
              anim={"stroke": {"dashOffset": chan([(100, 900, 'glide'), (900, 0)])}})
    guides = group("guides", "guides", [gh, gv], CX, CY, anim={"compositing": {"opacity": chan([(CH1, 1, 'in'), (CH1 + 300, 0, 'lin')])}})
    kids.append(guides)

    # ---------- dial ----------
    ticks_c = 2 * math.pi * 300
    ticks = circle("tick-ring", "tick-ring", CX, CY, 300, stroke=col(LINE), sw=16)
    ticks["properties"]["stroke"].update({"dashArray": [2.4, round(ticks_c / 120 - 2.4, 3)], "dashOffset": 0, "lineCap": "butt"})
    ticks["animators"] = {"transform": {"rotate": rot([(0, -40, 'glide'), (INTRO, 0, 'sine'), ((IDLE0 + IDLE1) / 2, 2, 'sine'), (IDLE1, 0, 'in'),
                                                      (CH1, 120, 'lin')])}}
    bezel = circle("bezel", "bezel", CX, CY, 262, fill=rad_grad([(0, '#2C2620'), (1, '#181512')], 0.4, 0.32, 0.72), stroke=col(LINE), sw=2)
    track = circle("charge-track", "charge-track", CX, CY, R_ARC, stroke=col(DIM), sw=24)
    arc = circle("charge-arc", "charge-arc (brand color)", CX, CY, R_ARC, stroke=col(A), sw=24)
    arc["properties"]["stroke"].update({"dashArray": [L_ARC], "dashOffset": L_ARC, "lineCap": "butt"})
    arc["properties"]["transform"]["rotate"] = -90
    arc["animators"] = {"stroke": {"dashOffset": chan([(0, L_ARC, 'lin'), (CH0, L_ARC, 'lin'), (CH1, 0, 'lin')])}}
    seps = circle("charge-segments", "charge-segments", CX, CY, R_ARC, stroke=col('#1B1714'), sw=27)
    seps["properties"]["stroke"].update({"dashArray": [3, round(L_ARC / 36 - 3, 3)], "dashOffset": 1.5, "lineCap": "butt"})
    seps["properties"]["transform"]["rotate"] = -90
    inner = circle("bezel-inner", "bezel-inner", CX, CY, 206, stroke=col('#0D0B09'), sw=6, opacity=0.7)

    # button
    shadow = ellipse("button-shadow", "button-shadow", CX, CY + 26, 170, 160, col('#000000'), opacity=0.55,
                     filt=[{"type": "blur", "value": {"x": 26, "y": 26}}])
    cap = circle("button-cap", "button-cap (brand color)", CX, CY, 176, fill=rad_grad([(0, LIGHT), (0.55, A), (1, DARK)], 0.36, 0.28, 0.78))
    rim = circle("button-rim", "button-rim", CX, CY, 175, stroke=col('#FFFFFF', 0.24), sw=2)
    ring = circle("button-ring", "button-ring", CX, CY, 147, stroke=col('#000000', 0.22), sw=2)
    lab = text("button-label", "button-label", "HOLD", CX, CY + 16, 'Bricolage Grotesque', 70, 800, col(CREAM), anchor='middle', ls=1, anim={
        "compositing": {"opacity": chan([(CH0, 1, 'soft'), (CH0 + 120, 0, 'lin')])}})
    sub = mono("button-sub", "button-sub", "TO LAUNCH", CX, CY + 60, 17, col(CREAM, 0.82), anchor='middle', ls=4.5, anim={
        "compositing": {"opacity": chan([(CH0, 1, 'soft'), (CH0 + 120, 0, 'lin')])}})
    digits = []
    step = (CH1 - (CH0 + 120)) / 3
    for i, d in enumerate("321"):
        t0 = CH0 + 120 + i * step; t1 = t0 + step
        anim = {"compositing": {"opacity": chan([(0, 0, 'lin'), (t0, 0, 'snap'), (t0 + 90, 1, 'lin'), (t1 - 40, 1, 'in'), (t1, 0, 'lin')])},
                "transform": {"scale": scl([(t0, 1.45, 'snap'), (t0 + 260, 1, 'lin')])}}
        dg = text(f"countdown-{d}", f"countdown-{d}", d, CX, CY, 'Bricolage Grotesque', 156, 800, col(CREAM), anchor='middle', anim=anim, opacity=0)
        dg["properties"]["transform"]["translate"] = {"x": 0, "y": 54}     # pivot at the digit's center, baseline 54 px below
        digits.append(dg)
    button = group("button", "button", [shadow, cap, rim, ring, lab, sub, *digits], CX, CY, anim={
        "transform": {"scale": scl([(IDLE0, 1, 'sine'), ((IDLE0 + IDLE1) / 2, 1.014, 'sine'), (IDLE1, 1, 'press'), (CH0 + 130, 0.93, 'lin'),
                                    (CH1, 0.93, 'snap'), (CH1 + 90, 1.07, 'whip'), (CH1 + 420, 0.2, 'lin')])}})

    # growing shake in the last second of charge (deterministic)
    rnd = random.Random(7)
    shake = [(0, (CX, CY), 'lin'), (CH1 - 1100, (CX, CY), 'lin')]
    tt = CH1 - 1100
    while tt < CH1 - 40:
        tt += 45
        amp = 1 + 6.5 * ((tt - (CH1 - 1100)) / 1100) ** 1.6
        shake.append((tt, (CX + rnd.uniform(-amp, amp), CY + rnd.uniform(-amp, amp)), 'lin'))
    shake.append((CH1, (CX, CY), 'lin'))
    dial = group("dial", "dial", [ticks, bezel, track, arc, seps, inner, button], CX, CY, anim={
        "transform": {"origin": pos(shake, 'lin'),
                      "scale": scl([(0, 0.86, 'glide'), (INTRO, 1, 'lin'), (CH1, 1, 'snap'), (CH1 + 100, 1.06, 'whip'), (CH1 + 460, 0.3, 'lin')])},
        "compositing": {"opacity": chan([(0, 0, 'soft'), (500, 1, 'lin'), (CH1 + 100, 1, 'in'), (CH1 + 460, 0, 'lin')])}}, )
    dial["properties"]["compositing"] = {"opacity": 0}
    kids.append(dial)

    # ---------- explosion ----------
    for i, (cc, sw_, d0) in enumerate([(A, 12, 0), (CREAM, 3, 110)]):
        sw = circle(f"shockwave-{i+1}", f"shockwave-{i+1}" + (" (brand color)" if i == 0 else ""), CX, CY, 190, stroke=col(cc), sw=sw_, opacity=0, anim={
            "transform": {"scale": scl([(CH1 + d0, 1, 'out'), (CH1 + d0 + 900, 5.4, 'lin')])},
            "compositing": {"opacity": chan([(0, 0, 'lin'), (CH1 + d0, 0, 'lin'), (CH1 + d0 + 20, 0.95, 'out'), (CH1 + d0 + 900, 0, 'lin')])}})
        kids.append(sw)
    prt = []
    rnd = random.Random(11)
    for i in range(16):
        ang = math.radians(i * 22.5 + rnd.uniform(-8, 8))
        dist = rnd.uniform(430, 780)
        tx, ty = CX + dist * math.cos(ang), CY + dist * math.sin(ang)
        cc = A if i % 3 else CREAM
        t0 = CH1 + 10 + rnd.randint(0, 60)
        anim = {"transform": {"origin": pos([(t0, (CX, CY), 'snap'), (t0 + 900, (tx, ty), 'lin')]),
                              "rotate": rot([(t0, 0, 'out'), (t0 + 900, rnd.choice([-1, 1]) * rnd.uniform(140, 300), 'lin')])},
                "compositing": {"opacity": chan([(0, 0, 'lin'), (t0, 0, 'lin'), (t0 + 20, 1, 'lin'), (t0 + 650, 1, 'in'), (t0 + 900, 0, 'lin')])}}
        if i % 2:
            pr = rect(f"spark-{i+1}", f"spark-{i+1}", CX - 11, CY - 4, 22, 8, 4, fill=col(cc), anim=anim, opacity=0)
        else:
            pr = circle(f"spark-{i+1}", f"spark-{i+1}", CX, CY, 6, fill=col(cc), anim=anim, opacity=0)
        prt.append(pr)
    kids.append(group("sparks", "sparks", prt, CX, CY))

    # ---------- product ----------
    wx, wy, ww, bar = 1020, 300, 760, 50
    ih = round(ww * 10 / 16); wh = bar + ih
    wcx, wcy = wx + ww / 2, wy + wh / 2
    defs.append(gen.clip_def_bottom_round("clip-window", "product-image-mask", wx, wy + bar, ww, ih, 20))
    wshadow = ellipse("window-shadow", "window-shadow", wcx, wy + wh + 10, 360, 40, col('#000000'), opacity=0.6,
                      filt=[{"type": "blur", "value": {"x": 30, "y": 30}}])
    frame = rect("window-frame", "window-frame", wx, wy, ww, wh, 20, fill=col(PANEL), stroke=col(LINE), sw=1.5)
    dots = [circle(f"window-dot-{i+1}", f"window-dot-{i+1}", wx + 28 + i * 20, wy + bar / 2, 6, fill=col('#3A332C')) for i in range(3)]
    pill = rect("url-pill", "url-pill", wcx - 170, wy + 11, 340, 28, 14, fill=col('#2A241F'))
    url = mono("window-url", "window-url", c['url'], wcx, wy + 31, 15, col(MUTED), anchor='middle', ls=0.5)
    shot = image("product-image", "product-image", data_uri(c['screenshot']), wx, wy + bar, ww, ih, fit="xMidYMid slice")
    shot_g = group("product-image-reveal", "product-image-reveal", [shot], wcx, wy + bar + ih / 2, clip="clip-window")
    t_w = CH1 + 200
    window = group("product-window", "product-window", [wshadow, frame, *dots, pill, url, shot_g], wcx, wcy, anim={
        "transform": {"origin": pos([(t_w, (wcx, 1300), 'over'), (t_w + 760, (wcx, wcy), 'sine'),
                                     (LIVE0, (wcx, wcy), 'sine'), (7500, (wcx, wcy - 10), 'sine'), (T, (wcx, wcy), 'lin')]),
                      "scale": scl([(t_w, 0.74, 'snap'), (t_w + 760, 1, 'lin')]),
                      "rotate": rot([(t_w, 9, 'snap'), (t_w + 700, -2.2, 'soft'), (t_w + 1250, 0, 'lin')])},
        "compositing": {"opacity": chan([(0, 0, 'lin'), (t_w, 0, 'soft'), (t_w + 200, 1, 'lin')])}})
    window["properties"]["compositing"] = {"opacity": 0}
    kids.append(window)

    chip_pos = [(1000, 640), (1700, 256), (1650, 846)]
    chips = []
    for i, (fx, fy) in enumerate(chip_pos):
        n = i + 1; cw, chh = 380, 68
        t0 = 4250 + i * 130
        bob = [(LIVE0, (fx, fy), 'sine'), (LIVE0 + 900 + i * 300, (fx, fy - 7), 'sine'), (T, (fx, fy), 'lin')]
        body = rect(f"feature-{n}-card", f"feature-{n}-card", fx - cw / 2, fy - chh / 2, cw, chh, chh / 2, fill=col('#231E1A'), stroke=col(LINE), sw=1.5,
                    filt=[{"type": "drop-shadow", "value": {"blur": {"x": 18, "y": 18}, "offset": {"x": 0, "y": 12}, "color": {"r": 0, "g": 0, "b": 0, "a": 0.45}}}])
        dot = circle(f"feature-{n}-dot", f"feature-{n}-dot (brand color)", fx - cw / 2 + 34, fy, 7, fill=col(A))
        lab = text(f"feature-{n}-label", f"feature-{n}-label", c['features'][i], fx - cw / 2 + 56, fy + 8, 'Geist', 22, 600, col(CREAM), ls=-0.1)
        chips.append(group(f"feature-{n}", f"feature-{n}", [body, dot, lab], fx, fy, anim={
            "transform": {"origin": pos([(t0, (CX, CY), 'over'), (t0 + 560, (fx, fy), 'lin')] + bob),
                          "scale": scl([(t0, 0.3, 'snap'), (t0 + 560, 1, 'lin')])},
            "compositing": {"opacity": chan([(0, 0, 'lin'), (t0, 0, 'soft'), (t0 + 160, 1, 'lin')])}}))
        chips[-1]["properties"]["compositing"] = {"opacity": 0}
    kids.append(group("features", "features", chips, CX, CY))

    # ---------- text column ----------
    def rise(n_, t0, dy=26):
        x0, y0 = n_["properties"]["transform"]["origin"]["x"], n_["properties"]["transform"]["origin"]["y"]
        n_["animators"] = {"transform": {"origin": pos([(t0, (x0, y0 + dy), 'glide'), (t0 + 650, (x0, y0), 'lin')])},
                           "compositing": {"opacity": chan([(t0, 0, 'soft'), (t0 + 380, 1, 'lin')])}}
        n_["properties"]["compositing"] = {"opacity": 0}
        return n_
    logo = rise(image("logo", "logo", data_uri(c['logo']), 140, 112, 64, 64), 80)
    brand = rise(text("brand-name", "brand-name", c['brand'], 222, 156, 'Bricolage Grotesque', 34, 700, col(CREAM), ls=-0.6), 140)
    h1 = rise(text("headline-line-1", "headline-line-1", g['headline'][0], 128, 470, 'Bricolage Grotesque', 148, 800, col(CREAM), ls=-4.5), 320, 60)
    defs.append(clip_def("clip-headline-2", "headline-line-2-mask", 110, 486, 1000, 168))
    ready = text("headline-line-2", "headline-line-2", g['headline'][1], 128, 626, 'Bricolage Grotesque', 148, 800, col(CREAM), ls=-4.5, anim={
        "transform": {"origin": pos([(420, (128, 690), 'glide'), (1050, (128, 626), 'lin'), (3700, (128, 626), 'in'), (4100, (128, 400), 'lin')])}})
    live = text("headline-live", "headline-live (brand color)", g['live'], 128, 790, 'Bricolage Grotesque', 148, 800, col(A), ls=-4.5, anim={
        "transform": {"origin": pos([(3880, (128, 790), 'snap'), (4400, (128, 626), 'lin')])}})
    line2 = group("headline-line-2-reveal", "headline-line-2-reveal", [ready, live], 128, 626, clip="clip-headline-2")
    s1 = rise(text("subhead-1", "subhead-1", g['subhead'][0], 134, 712, 'Geist', 30, 400, col(MUTED), ls=-0.2), 520)
    s2 = rise(text("subhead-2", "subhead-2", g['subhead'][1], 134, 754, 'Geist', 30, 400, col(MUTED), ls=-0.2), 580)

    sy = 842
    sdot = circle("status-dot", "status-dot (brand color)", 142, sy - 6, 6, fill=col(A), opacity=0, anim={
        "compositing": {"opacity": chan([(0, 0, 'lin'), (640, 0, 'soft'), (900, 1, 'lin'), (3900, 1, 'step'),
                                          (LIVE0, 1, 'step'), (LIVE0 + 500, 0.25, 'step'), (LIVE0 + 1000, 1, 'step'), (LIVE0 + 1500, 0.25, 'step'),
                                          (LIVE0 + 2000, 1, 'step'), (LIVE0 + 2500, 0.25, 'step'), (T, 1, 'lin')])}})
    slab = mono("status-label", "status-label", "STATUS", 160, sy, 17, col(MUTED), ls=3, opacity=0,
                anim={"compositing": {"opacity": opa((640, 0), (900, 1))}})
    def sval(id_, s, colr, t_in, t_out=None):
        keys = [(0, 0, 'lin'), (t_in, 0, 'soft'), (t_in + 80, 1, 'lin')]
        if t_out: keys += [(t_out, 1, 'soft'), (t_out + 80, 0, 'lin')]
        return mono(id_, id_, s, 262, sy, 17, col(colr), weight=700, ls=3, opacity=0, anim={"compositing": {"opacity": chan(keys)}})
    st = [sval("status-armed", "ARMED", CREAM, 640, CH0), sval("status-charging", "CHARGING", A, CH0, CH1), sval("status-live", "LIVE", A, 3900)]
    st[0]["animators"]["compositing"]["opacity"] = chan([(0, 0, 'lin'), (640, 0, 'soft'), (900, 1, 'lin'), (CH0, 1, 'soft'), (CH0 + 80, 0, 'lin')])
    hint = text("hint-text", "hint-text", g['hint'], 136, 944, 'Geist', 22, 500, col(MUTED), opacity=0, anim={
        "compositing": {"opacity": chan([(0, 0, 'lin'), (700, 0, 'soft'), (IDLE0, 0.9, 'sine'), ((IDLE0 + IDLE1) / 2, 0.45, 'sine'), (IDLE1, 0.9, 'soft'),
                                          (CH0 + 150, 0, 'lin')])}})

    bx, by, bw, bh = 136, 896, 400, 84
    cta_btn = rect("cta-button", "cta-button (brand color)", bx, by, bw, bh, bh / 2, fill=col(A))
    cta_lab = text("cta-label", "cta-label", c['cta'], bx + 46, by + 53, 'Geist', 28, 600, col('#FFFFFF'), ls=-0.2)
    arrow = path("cta-arrow", "cta-arrow", [(-11, 0), (11, 0), (2, -9), (11, 0), (2, 9)], bx + bw - 48, by + bh / 2, stroke=col('#FFFFFF'), sw=3.4)
    cta2 = text("cta-secondary", "cta-secondary", g['cta2'], bx + bw + 44, by + 52, 'Geist', 26, 500, col(CREAM))
    cta = group("cta", "cta", [cta_btn, cta_lab, arrow, cta2], bx + bw / 2, by + bh / 2, anim={
        "transform": {"origin": pos([(4650, (bx + bw / 2, by + bh / 2 + 34), 'glide'), (5250, (bx + bw / 2, by + bh / 2), 'lin')])},
        "compositing": {"opacity": chan([(0, 0, 'lin'), (4650, 0, 'soft'), (4980, 1, 'lin')])}})
    cta["properties"]["compositing"] = {"opacity": 0}

    kids.append(group("copy", "copy", [logo, brand, h1, line2, s1, s2, sdot, slab, *st, hint, cta], 560, 540))

    flash = rect("flash", "flash", 0, 0, W, H, fill=col('#FFF6EA'), opacity=0, anim={
        "compositing": {"opacity": chan([(0, 0, 'lin'), (CH1, 0, 'lin'), (CH1 + 40, 0.82, 'out'), (CH1 + 520, 0, 'lin')])}})
    kids.append(flash)

    kids.append(howto([
        "1  Retype any text: headline-line-1, headline-line-2,",
        "    headline-live, subhead-1/2, feature-1..3-label, cta-label.",
        "2  Replace logo (square) and product-image",
        "    (16:10 screenshot, 1600 x 1000).",
        "3  Brand color: every layer marked (brand color).",
        "4  Player API segments: idle 0.9-1.4 s (loop),",
        "    charge 1.4-3.4 s, launch 3.4-6 s, live 6-9 s (loop).",
        "5  Hold to launch = play the charge, release = reverse.",
        "    The page script ignition.js does it for you.",
    ], card='#FFFDF9'))

    d = doc(kids, T, BG1)
    meta = {"T": T, "segments": {"intro": [0, INTRO], "idle": [IDLE0, IDLE1], "charge": [CH0, CH1], "launch": [CH1, LIVE0], "live": [LIVE0, T]},
            "hit": {"button": {"cx": CX, "cy": CY, "r": 262}}}
    return d, defs, meta


if __name__ == '__main__':
    d, defs, meta = cli(build, 'ignition')
    print('layers, animated, keyframes:', count(d))
