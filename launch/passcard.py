#!/usr/bin/env python3
"""EVENT PASS · 16:9 launch hero: a backstage pass hanging from a lanyard.
Hover = it tilts (scrub of the tilt segment), click = it flips, click on the stub = it tears off.

Segments (ms): intro 0-1100, tilt 1100-3100 (1600 left, 2100 center, 2600 right), flip 3100-4250,
tear 4300-5800, live 5800-7800 (loop).
"""
import random
from kit import *

T = 7800
INTRO, TILT0, TL, TC, TR, TILT1 = 1100, 1100, 1600, 2100, 2600, 3100
FLIP0, FLIPM, FLIP1 = 3100, 3650, 4250
TEAR0, TEAR1, LIVE0 = 4300, 5800, 5800
PCX, PW, PH = 1380, 500, 760
PX, PY = PCX - PW // 2, 210
PERF = PY + PH - 150
PCY = PY + PH // 2
HOOK = (PCX, 180)
PASS, PASS_LINE, CREAM, PMUTED = '#151517', '#2C2C31', '#F3EFE7', '#8E8B85'
INK, MUTED = '#17181C', '#5C5E66'
SERIF = 'Instrument Serif'


def holo(A, fx, fy, tx, ty):
    # metallic foil in the brand hue: light and dark bands that slide with the tilt
    return lin_grad([(0, mix(A, '#000000', 0.22)), (0.3, mix(A, '#FFFFFF', 0.5)), (0.5, A), (0.68, mix(A, '#FFFFFF', 0.72)), (1, mix(A, '#000000', 0.12))], fx, fy, tx, ty)


def build(c):
    A = c['accent']; g = c['pass']
    kids, defs = [], []
    kids.append(rect("background", "background", 0, 0, W, H, fill=rad_grad([(0, '#F8F5EF'), (1, '#E3DCD0')], 0.7, 0.42, 0.85)))

    # shadow on the background (follows tilt and flip)
    shadow = ellipse("pass-shadow", "pass-shadow", PCX + 10, PY + PH + 40, 240, 22, col('#2A2118'), opacity=0.32,
                     filt=[{"type": "blur", "value": {"x": 18, "y": 18}}], anim={
        "transform": {"origin": pos([(0, (PCX + 10, PY + PH + 40), 'lin'), (TILT0, (PCX + 10, PY + PH + 40), 'lin'), (TL, (PCX + 48, PY + PH + 40), 'lin'),
                                     (TC, (PCX + 10, PY + PH + 40), 'lin'), (TR, (PCX - 28, PY + PH + 40), 'lin'), (TILT1, (PCX + 10, PY + PH + 40), 'lin'),
                                     (TEAR0 + 450, (PCX + 10, PY + PH + 40), 'sine'), (TEAR1 - 300, (PCX + 10, PERF + 50), 'lin')], 'lin'),
                      "scale": scl([(0, 0.2, 'snap'), (600, 1, 'lin'), (FLIP0, (1, 1), 'in'), (FLIPM, (0.35, 1), 'out'), (FLIP1, (1, 1), 'lin')])}})
    kids.append(shadow)

    # ---------- text column ----------
    def rise(n_, t0, dy=26):
        x0, y0 = n_["properties"]["transform"]["origin"]["x"], n_["properties"]["transform"]["origin"]["y"]
        n_["animators"] = {"transform": {"origin": pos([(t0, (x0, y0 + dy), 'glide'), (t0 + 650, (x0, y0), 'lin')])},
                           "compositing": {"opacity": chan([(t0, 0, 'soft'), (t0 + 380, 1, 'lin')])}}
        n_["properties"]["compositing"] = {"opacity": 0}
        return n_
    copy = [rise(image("logo", "logo", data_uri(c['logo']), 150, 116, 56, 56), 100),
            rise(text("brand-name", "brand-name", c['brand'], 222, 156, 'Geist', 28, 600, col(INK), ls=-0.3), 160),
]
    for i, (s, colr) in enumerate(zip(g['headline'], [INK, A, INK])):
        title = f"headline-line-{i+1}" + (" (brand color)" if i == 1 else "")
        copy.append(rise(text(f"headline-line-{i+1}", title, s, 144, 424 + i * 112, SERIF, 124, 400, col(colr), ls=-1.5), 340 + i * 80, 40))
    copy.append(rise(mono("details-1", "details-1", g['details'][0], 152, 744, 21, col(INK), weight=600, ls=2.5), 620))
    copy.append(rise(mono("details-2", "details-2", g['details'][1], 152, 782, 21, col(MUTED), ls=2.5), 680))
    hint = text("hint-text", "hint-text", g['hint'], 152, 902, 'Geist', 22, 500, col(MUTED), opacity=0, anim={
        "compositing": {"opacity": chan([(0, 0, 'lin'), (800, 0, 'soft'), (1100, 1, 'lin'), (TEAR0 + 600, 1, 'soft'), (TEAR0 + 800, 0, 'lin')])}})
    done = text("hint-done", "hint-done (brand color)", g['hint_done'], 152, 902, 'Geist', 22, 600, col(A), opacity=0, anim={
        "compositing": {"opacity": chan([(0, 0, 'lin'), (TEAR0 + 800, 0, 'soft'), (TEAR0 + 1000, 1, 'lin')])}})
    copy += [hint, done]
    kids.append(group("copy", "copy", copy, 520, 540))

    # ---------- pass ----------
    defs.append(clip_def("clip-pass-front", "pass-front-mask", PX, PY, PW, PERF - PY, 26))
    defs.append(clip_def("clip-pass-back", "pass-back-mask", PX, PY, PW, PERF - PY, 26))
    tilt_paint = lambda: chan([(0, holo(A, 0, 0, 1, 1), 'lin'), (TILT0, holo(A, 0, 0, 1, 1), 'lin'), (TL, holo(A, -0.4, 0.1, 0.6, 1.1), 'lin'),
                               (TC, holo(A, 0, 0, 1, 1), 'lin'), (TR, holo(A, 0.4, -0.1, 1.4, 0.9), 'lin'), (TILT1, holo(A, 0, 0, 1, 1), 'lin'),
                               (LIVE0, holo(A, 0, 0, 1, 1), 'sine'), (LIVE0 + 1000, holo(A, 0.45, -0.1, 1.45, 0.9), 'sine'), (T, holo(A, 0, 0, 1, 1), 'lin')], 'lin')

    def highlight(side, clip_id):
        band = rect(f"{side}-gleam", f"{side}-gleam", PCX - 80, PY - 260, 160, PH + 520, 0,
                    fill=lin_grad([(0, '#FFFFFF', 0), (0.5, '#FFFFFF', 0.2), (1, '#FFFFFF', 0)], 0, 0, 1, 0))
        band["properties"]["transform"]["rotate"] = 16
        band["animators"] = {"transform": {"origin": pos([(0, (PCX, PCY), 'lin'), (TILT0, (PCX, PCY), 'lin'), (TL, (PX + 30, PCY), 'lin'), (TC, (PCX, PCY), 'lin'),
                                                          (TR, (PX + PW - 30, PCY), 'lin'), (TILT1, (PCX, PCY), 'lin'),
                                                          (LIVE0, (PCX, PCY), 'sine'), (LIVE0 + 1000, (PX + PW + 200, PCY), 'lin'), (LIVE0 + 1001, (PX - 200, PCY), 'sine'), (T, (PCX, PCY), 'lin')], 'lin')}}
        return group(f"{side}-gleam-clip", f"{side}-gleam-clip", [band], PCX, PCY, clip=clip_id)

    def barcode(prefix, x0, x1, y, h):
        rb = random.Random(9); x = x0; out = []
        while x < x1:
            w_ = rb.choice([2, 2, 3, 4, 6])
            out.append(rect(f"{prefix}-bar-{len(out)+1}", f"{prefix}-bar-{len(out)+1}", x, y, w_, h, 0, fill=col(CREAM, 0.85)))
            x += w_ + rb.choice([3, 4, 5])
        return group(f"{prefix}-barcode", f"{prefix}-barcode", out, (x0 + x1) / 2, y + h / 2)

    def stub(side):
        kids_ = [rect(f"{side}-stub-paper", f"{side}-stub-paper", PX, PERF, PW, PY + PH - PERF, 26, fill=col(PASS), stroke=col(PASS_LINE), sw=1.5),
                 path(f"{side}-perforation", f"{side}-perforation", [(0, 0), (PW - 52, 0)], PX + 26, PERF + 1, stroke=col('#55555C'), sw=2),
                 mono(f"{side}-admit", f"{side}-admit", g['admit'], PX + 36, PERF + 50, 15, col(PMUTED), ls=4),
                 mono(f"{side}-stub-cta", f"{side}-stub-cta (brand color)", g['stub_cta'], PX + 36, PERF + 104, 21, col(A), weight=700, ls=2.5),
                 path(f"{side}-stub-arrow", f"{side}-stub-arrow", [(-10, 0), (10, 0), (2, -8), (10, 0), (2, 8)], PX + 312, PERF + 97, stroke=col(A), sw=3),
                 barcode(f"{side}-stub", PX + PW - 150, PX + PW - 36, PERF + 30, 86)]
        kids_[1]["properties"]["stroke"].update({"dashArray": [8, 7], "dashOffset": 0, "lineCap": "butt"})
        return kids_

    # front
    front = [rect("front-body", "front-body", PX, PY, PW, PERF - PY, 26, fill=col(PASS), stroke=col(PASS_LINE), sw=1.5),
             group("front-foil-clip", "front-foil-clip", [rect("front-foil", "front-foil (brand + holo)", PX, PY, PW, 216, 0, fill=holo(A, 0, 0, 1, 1),
                                                                 anim={"fill": {"paint": tilt_paint()}})], PCX, PY + 108, clip="clip-pass-front"),
             rect("front-slot", "front-slot", PCX - 36, PY + 24, 72, 16, 8, fill=col('#2A2620')),
             mono("pass-label", "pass-label", g['pass_label'], PX + 36, PY + 96, 18, col(PASS), weight=700, ls=4),
             mono("pass-number", "pass-number", g['number'], PX + PW - 36, PY + 96, 18, col(PASS), weight=700, anchor='end', ls=2),
             image("pass-logo", "pass-logo", data_uri(c['logo']), PX + 36, PY + 124, 52, 52),
             text("pass-brand", "pass-brand", c['brand'], PX + 102, PY + 160, 'Geist', 24, 600, col(PASS)),
             text("pass-product-1", "pass-product-1", g['product'][0], PX + 32, PY + 332, SERIF, 132, 400, col(CREAM), ls=-2),
             text("pass-product-2", "pass-product-2 (brand color)", g['product'][1], PX + 32, PY + 440, SERIF, 132, 400, col(A), ls=-2)]
    for i, (lab, val) in enumerate(g['grid']):
        gx, gy = PX + 36 + (i % 2) * 230, PY + 488 + (i // 2) * 64
        front += [mono(f"grid-{i+1}-label", f"grid-{i+1}-label", lab, gx, gy, 13, col(PMUTED), ls=3),
                  mono(f"grid-{i+1}-value", f"grid-{i+1}-value", val, gx, gy + 27, 19, col(CREAM), weight=600, ls=1.5)]
    front += stub("front")
    front.append(highlight("front", "clip-pass-front"))
    front_g = group("pass-front", "pass-front", front, PCX, PCY, anim={
        "transform": {"scale": scl([(FLIP0, (1, 1), 'in'), (FLIPM, (0.01, 1), 'lin')]),
                      "skew": chan([(FLIP0, {"x": 0, "y": 0}, 'in'), (FLIPM, {"x": 0, "y": 7}, 'lin')])},
        "compositing": {"opacity": chan([(FLIPM - 10, 1, 'lin'), (FLIPM, 0, 'lin')])}})

    # back
    back = [rect("back-body", "back-body", PX, PY, PW, PERF - PY, 26, fill=col(PASS), stroke=col(PASS_LINE), sw=1.5),
            group("back-foil-clip", "back-foil-clip", [rect("back-foil", "back-foil (brand + holo)", PX, PY, PW, 14, 0, fill=holo(A, 0, 0, 1, 1),
                                                               anim={"fill": {"paint": tilt_paint()}})], PCX, PY + 7, clip="clip-pass-back"),
            rect("back-slot", "back-slot", PCX - 36, PY + 24, 72, 16, 8, fill=col('#2A2620')),
            mono("back-title", "back-title", g['back_title'], PX + 36, PY + 94, 17, col(CREAM), weight=700, ls=4)]
    for i, f in enumerate(c['features']):
        yy = PY + 164 + i * 66
        back += [text(f"feature-{i+1}-number", f"feature-{i+1}-number (brand color)", f"0{i+1}", PX + 34, yy + 6, SERIF, 54, 400, col(A)),
                 text(f"feature-{i+1}-label", f"feature-{i+1}-label", f, PX + 104, yy, 'Geist', 24, 600, col(CREAM), ls=-0.2)]
        if i < 2:
            back.append(path(f"feature-{i+1}-rule", f"feature-{i+1}-rule", [(0, 0), (PW - 72, 0)], PX + 36, yy + 26, stroke=col('#2E2E33'), sw=1.5))
    sw_, sh_ = 400, round(400 * 10 / 16)
    sx, sy = PCX - sw_ / 2, PY + 330
    defs.append(clip_def("clip-thumb", "product-image-mask", sx, sy, sw_, sh_, 12))
    back += [rect("thumb-frame", "thumb-frame", sx - 2, sy - 2, sw_ + 4, sh_ + 4, 14, fill=col('#26262B')),
             group("product-image-reveal", "product-image-reveal", [image("product-image", "product-image", data_uri(c['screenshot']), sx, sy, sw_, sh_, fit="xMidYMid slice")],
                   PCX, sy + sh_ / 2, clip="clip-thumb")]
    back.append(highlight("back", "clip-pass-back"))
    # stamp after the tear
    stc = (PCX - 46, PY + 470)        # on the light part of the screenshot: the ink stays legible
    stamp = group("stamp", "stamp (brand color)", [
        rect("stamp-frame", "stamp-frame", stc[0] - 190, stc[1] - 62, 380, 124, 18, stroke=col(A), sw=6),
        text("stamp-text", "stamp-text", g['stamp'], stc[0], stc[1] + 26, SERIF, 92, 400, col(A), anchor='middle', ls=-1)],
        *stc, anim={"transform": {"scale": scl([(TEAR0 + 650, 1.8, 'over'), (TEAR0 + 980, 1, 'lin')]), "rotate": rot([(TEAR0 + 650, 4, 'snap'), (TEAR0 + 980, -8, 'lin')])},
                    "compositing": {"opacity": chan([(0, 0, 'lin'), (TEAR0 + 650, 0, 'lin'), (TEAR0 + 700, 1, 'lin')])}})
    stamp["properties"]["transform"]["rotate"] = -8
    stamp["properties"]["compositing"] = {"opacity": 0}
    back.append(stamp)
    stub_b = group("back-stub", "back-stub (tears off)", stub("back"), PX + 24, PERF, anim={
        "transform": {"rotate": rot([(TEAR0, 0, 'in'), (TEAR0 + 380, 7, 'snap'), (TEAR0 + 460, 5, 'drop'), (TEAR1 - 300, 46, 'lin')]),
                      "origin": pos([(TEAR0 + 420, (PX + 24, PERF), 'drop'), (TEAR1 - 300, (PX + 150, PERF + 820), 'lin')])},
        "compositing": {"opacity": chan([(TEAR1 - 600, 1, 'in'), (TEAR1 - 300, 0, 'lin')])}})
    back.append(stub_b)
    back_g = group("pass-back", "pass-back", back, PCX, PCY, anim={
        "transform": {"scale": scl([(0, (0.01, 1), 'lin'), (FLIPM, (0.01, 1), 'out'), (FLIP1, (1, 1), 'lin')]),
                      "skew": chan([(FLIPM, {"x": 0, "y": -7}, 'out'), (FLIP1, {"x": 0, "y": 0}, 'lin')])},
        "compositing": {"opacity": chan([(0, 0, 'lin'), (FLIPM, 0, 'lin'), (FLIPM + 10, 1, 'lin')])}})
    back_g["properties"]["compositing"] = {"opacity": 0}
    back_g["properties"]["transform"]["scale"] = {"x": 0.01, "y": 1}

    tilt = group("pass-tilt", "pass-tilt", [front_g, back_g], PCX, PCY, anim={
        "transform": {"skew": chan([(0, {"x": 0, "y": 0}, 'lin'), (TILT0, {"x": 0, "y": 0}, 'lin'), (TL, {"x": 0, "y": 3.6}, 'lin'), (TC, {"x": 0, "y": 0}, 'lin'),
                                    (TR, {"x": 0, "y": -3.6}, 'lin'), (TILT1, {"x": 0, "y": 0}, 'lin')], 'lin'),
                      "scale": scl([(0, 1, 'lin'), (TILT0, 1, 'lin'), (TL, (0.965, 1), 'lin'), (TC, 1, 'lin'), (TR, (0.965, 1), 'lin'), (TILT1, 1, 'sine'),
                                    (FLIPM, 1.05, 'sine'), (FLIP1, 1, 'lin')], 'lin')}})

    # lanyard and clip
    straps = [path("lanyard-left", "lanyard-left (brand color)", [(1262, -40), (1306, -40), (1372, 168), (1346, 174), (1262, -40)], 0, 0, fill=col(A)),
              path("lanyard-right", "lanyard-right (brand color)", [(1454, -40), (1498, -40), (1414, 174), (1388, 168), (1454, -40)], 0, 0, fill=col(mix(A, '#000000', 0.18))),
              rect("clip-hardware", "clip-hardware", PCX - 26, 156, 52, 80, 12, fill=lin_grad([(0, '#D9D9DE'), (1, '#8C8C94')], 0, 0, 1, 0), stroke=col('#6E6E76'), sw=1.5),
              rect("clip-hardware-hole", "clip-hardware-hole", PCX - 10, 170, 20, 20, 10, fill=col('#5A5A62'))]
    swing = group("pass-swing", "pass-swing", [*straps[:2], tilt, *straps[2:]], *HOOK, anim={
        "transform": {"origin": pos([(0, (HOOK[0], HOOK[1] - 900), 'snap'), (560, HOOK, 'lin')]),
                      "rotate": rot([(0, -10, 'lin'), (300, -10, 'sine'), (560, 8, 'sine'), (800, -4, 'sine'), (980, 1.5, 'sine'), (INTRO, 0, 'lin')])}})
    kids.append(swing)

    kids.append(howto([
        "1  Retype the headline lines, details, pass texts",
        "    (pass-product-1/2, grid, stub), feature-1..3-label.",
        "2  Replace logo, pass-logo (square) and product-image (16:10).",
        "3  Brand color: lanyard, foil and every layer marked (brand color).",
        "4  Player API segments: tilt 1.1-3.1 s (1.6 left, 2.1 centre,",
        "    2.6 right: scrub it with the pointer), flip 3.1-4.25 s,",
        "    tear 4.3-5.8 s, live 5.8-7.8 s (loop).",
    ]))
    d = doc(kids, T, '#E9E3D9')
    meta = {"T": T, "segments": {"intro": [0, INTRO], "tilt": [TILT0, TILT1], "flip": [FLIP0, FLIP1], "tear": [TEAR0, TEAR1], "live": [LIVE0, T]},
            "tilt": {"left": TL, "center": TC, "right": TR},
            "hit": {"pass": [PX, PY, PX + PW, PY + PH], "stub": [PX, PERF, PX + PW, PY + PH]}}
    return d, defs, meta


if __name__ == '__main__':
    d, defs, meta = cli(build, 'passcard')
    print('layers, animated, keyframes:', count(d))
