#!/usr/bin/env python3
"""Render the entry picture: a glossy dark-chocolate lava cake.

One ingredient hero — dark chocolate — drawn with Pillow at 2x
supersampling: gradients, alpha layers and Gaussian blur for a rich,
appetizing look. Saves entry.png (1024x1024) beside this file.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
S = 2  # supersampling factor
W = 1024 * S

random.seed(20261123)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(size, top, bottom):
    img = Image.new("RGB", (size, size))
    px = img.load()
    for y in range(size):
        c = lerp(top, bottom, y / size)
        for x in range(size):
            px[x, y] = c
    return img


def paste_glow(base, cx, cy, radius, color, peak):
    mask = Image.new("L", base.size, 0)
    d = ImageDraw.Draw(mask)
    steps = 40
    for i in range(steps, 0, -1):
        r = radius * i / steps
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  fill=int(peak * (1 - i / steps) ** 1.5))
    mask = mask.filter(ImageFilter.GaussianBlur(30 * S))
    tint = Image.new("RGB", base.size, color)
    base.paste(Image.composite(tint, base.convert("RGB"), mask), (0, 0), mask)


def soft_ellipse(layer, box, fill, blur):
    tmp = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    ImageDraw.Draw(tmp).ellipse(box, fill=fill)
    tmp = tmp.filter(ImageFilter.GaussianBlur(blur))
    layer.alpha_composite(tmp)


def main():
    # ---- backdrop: deep warm brown gradient + spotlight ----
    img = vgrad(W, (46, 26, 18), (16, 9, 6)).convert("RGBA")
    paste_glow(img, W // 2, int(W * 0.42), int(W * 0.52), (255, 176, 96), 120)
    paste_glow(img, W // 2, int(W * 0.40), int(W * 0.30), (255, 214, 150), 90)

    cx, cy = W // 2, int(W * 0.60)          # cake centre
    plate_y = int(W * 0.70)

    # ---- table shadow ----
    sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    soft_ellipse(sh, [cx - int(W * 0.40), plate_y - int(W * 0.05),
                      cx + int(W * 0.40), plate_y + int(W * 0.11)],
                 (0, 0, 0, 150), 26 * S)
    img.alpha_composite(sh)

    # ---- plate ----
    pl = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pl)
    pd.ellipse([cx - int(W * 0.37), plate_y - int(W * 0.085),
                cx + int(W * 0.37), plate_y + int(W * 0.085)],
               fill=(232, 214, 190, 255))
    pd.ellipse([cx - int(W * 0.315), plate_y - int(W * 0.062),
                cx + int(W * 0.315), plate_y + int(W * 0.062)],
               fill=(203, 178, 148, 255))
    pd.ellipse([cx - int(W * 0.27), plate_y - int(W * 0.048),
                cx + int(W * 0.27), plate_y + int(W * 0.048)],
               fill=(226, 205, 175, 255))
    img.alpha_composite(pl)

    # ---- cake body: squat cylinder with a domed top ----
    cake = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cake)
    rw, rh = int(W * 0.235), int(W * 0.165)   # half width / height
    top_y, bot_y = cy - rh, cy + rh
    cd.rounded_rectangle([cx - rw, top_y, cx + rw, bot_y + int(W * 0.02)],
                         radius=int(W * 0.045), fill=(46, 24, 13, 255))
    # soft cylindrical shading: warm glow centre-front, shade at the base
    soft_ellipse(cake, [cx - int(rw * 0.85), top_y + int(W * 0.02),
                        cx + int(rw * 0.45), bot_y - int(W * 0.01)],
                 (122, 70, 36, 110), 30 * S)
    soft_ellipse(cake, [cx - rw, bot_y - int(W * 0.055),
                        cx + rw, bot_y + int(W * 0.03)],
                 (12, 6, 3, 130), 16 * S)
    cd.rounded_rectangle([cx - rw, top_y, cx + rw, bot_y + int(W * 0.02)],
                         radius=int(W * 0.045), outline=(24, 12, 5, 255),
                         width=3 * S)
    cd.ellipse([cx - rw, top_y - int(W * 0.055), cx + rw, top_y + int(W * 0.075)],
               fill=(64, 33, 17, 255))
    cd.ellipse([cx - rw, top_y - int(W * 0.055), cx + rw, top_y + int(W * 0.075)],
               outline=(30, 16, 8, 255), width=3 * S)
    img.alpha_composite(cake)

    # ---- cut wedge: warm molten interior face, front-right ----
    wedge = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wedge)
    wx, wy = cx + int(rw * 0.18), top_y + int(W * 0.045)
    wd.polygon([(wx, wy), (cx + rw - 4 * S, wy + int(W * 0.012)),
                (cx + rw - int(W * 0.03), bot_y - int(W * 0.01)),
                (wx + int(W * 0.03), bot_y + int(W * 0.005))],
               fill=(92, 50, 24, 255))
    img.alpha_composite(wedge)

    # ---- molten flow: tapered glossy pour from the wedge to a puddle ----
    flow = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    fd = ImageDraw.Draw(flow)
    fx = cx + int(rw * 0.52)
    pts = []
    for i in range(41):
        t = i / 40
        y = wy + int(W * 0.01) + t * (plate_y - wy - int(W * 0.005))
        half = (0.028 + 0.05 * t ** 1.6) * W
        wob = math.sin(t * 9.0) * W * 0.004
        pts.append((fx + wob - half, y))
    for i in range(40, -1, -1):
        t = i / 40
        y = wy + int(W * 0.01) + t * (plate_y - wy - int(W * 0.005))
        half = (0.028 + 0.05 * t ** 1.6) * W
        wob = math.sin(t * 9.0) * W * 0.004
        pts.append((fx + wob + half, y))
    fd.polygon(pts, fill=(56, 27, 12, 255))
    fd.ellipse([fx - int(W * 0.085), plate_y - int(W * 0.016),
                fx + int(W * 0.10), plate_y + int(W * 0.030)],
               fill=(56, 27, 12, 255))
    flow = flow.filter(ImageFilter.GaussianBlur(1.2 * S))
    img.alpha_composite(flow)
    # gloss streaks on the flow and puddle
    gl = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    gd.line([fx - int(W * 0.016), wy + int(W * 0.03),
             fx - int(W * 0.010), plate_y - int(W * 0.03)],
            fill=(255, 205, 150, 150), width=5 * S)
    gd.arc([fx - int(W * 0.07), plate_y - int(W * 0.014),
            fx + int(W * 0.05), plate_y + int(W * 0.026)],
           start=200, end=320, fill=(255, 220, 175, 170), width=3 * S)
    gl = gl.filter(ImageFilter.GaussianBlur(2 * S))
    img.alpha_composite(gl)

    # ---- drizzle arcs over the dome ----
    dr = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dr)
    for k in range(5):
        yy = top_y - int(W * 0.035) + k * int(W * 0.020)
        dd.arc([cx - rw + int(W * 0.05), yy - int(W * 0.02),
                cx + rw - int(W * 0.05), yy + int(W * 0.03)],
               start=15, end=165, fill=(30, 15, 7, 220), width=4 * S)
    img.alpha_composite(dr)

    # ---- truffles beside the cake ----
    spots = [(cx - int(W * 0.335), plate_y - int(W * 0.012), int(W * 0.030)),
             (cx - int(W * 0.285), plate_y + int(W * 0.016), int(W * 0.024)),
             (cx + int(W * 0.315), plate_y + int(W * 0.006), int(W * 0.027))]
    tr = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    td = ImageDraw.Draw(tr)
    for tx, ty, tr_r in spots:
        td.ellipse([tx - tr_r, ty + tr_r // 2, tx + tr_r, ty + tr_r],
                   fill=(0, 0, 0, 90))
        td.ellipse([tx - tr_r, ty - tr_r, tx + tr_r, ty + tr_r],
                   fill=(50, 26, 13, 255))
        td.ellipse([tx - tr_r // 2, ty - tr_r // 2,
                    tx + tr_r // 3, ty + tr_r // 4],
                   fill=(112, 66, 34, 255))
    img.alpha_composite(tr.filter(ImageFilter.GaussianBlur(0.8 * S)))
    hl = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    for tx, ty, tr_r in spots:
        hd.ellipse([tx - tr_r // 2, ty - tr_r * 3 // 4,
                    tx - tr_r // 6, ty - tr_r // 3],
                   fill=(255, 226, 185, 200))
    img.alpha_composite(hl.filter(ImageFilter.GaussianBlur(2 * S)))

    # ---- chocolate shards leaning on the cake ----
    sh2 = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh2)
    bx, by = cx - int(rw * 0.55), bot_y - int(W * 0.01)
    sd.polygon([(bx, by), (bx - int(W * 0.016), by - int(W * 0.085)),
                (bx + int(W * 0.020), by - int(W * 0.062))],
               fill=(36, 18, 9, 255))
    sd.polygon([(bx + int(W * 0.045), by), (bx + int(W * 0.038), by - int(W * 0.068)),
                (bx + int(W * 0.070), by - int(W * 0.045))],
               fill=(44, 23, 11, 255))
    img.alpha_composite(sh2)

    # ---- steam wisps ----
    st = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    std = ImageDraw.Draw(st)
    for k, xoff in enumerate((-0.09, 0.0, 0.09)):
        x0 = cx + int(W * xoff)
        wave = []
        for i in range(31):
            t = i / 30
            y = top_y - int(W * 0.06) - t * W * 0.17
            x = x0 + math.sin(t * 5.2 + k * 1.7) * W * 0.018
            wave.append((x, y))
        std.line(wave, fill=(255, 240, 220, 90), width=7 * S)
    st = st.filter(ImageFilter.GaussianBlur(7 * S))
    img.alpha_composite(st)

    # ---- dome gloss + vignette ----
    soft_ellipse(img, [cx - int(W * 0.13), top_y - int(W * 0.045),
                       cx + int(W * 0.02), top_y + int(W * 0.005)],
                 (255, 214, 160, 70), 8 * S)
    vig = Image.new("L", (W, W), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-int(W * 0.22), -int(W * 0.22), int(W * 1.22), int(W * 1.22)],
               fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(90 * S))
    dark = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    img = Image.composite(img, Image.blend(img, dark, 0.55), vig)

    out = img.convert("RGB").resize((1024, 1024), Image.LANCZOS)
    out.save(os.path.join(HERE, "entry.png"))
    print("wrote entry.png", out.size)


if __name__ == "__main__":
    main()
