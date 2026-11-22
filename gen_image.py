#!/usr/bin/env python3
"""Render a glossy molten dark-chocolate lava cake, 1024x1024.

One ingredient hero: DARK CHOCOLATE. Pillow only; drawn at 2x and
downscaled for smooth edges. Saves entry.png next to this file.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

SS = 2                      # supersample factor
W = 1024 * SS
H = 1024 * SS
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

random.seed(20261123)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(w, h, top, bottom):
    strip = Image.new("RGB", (1, h))
    px = strip.load()
    for y in range(h):
        px[0, y] = lerp(top, bottom, y / max(1, h - 1))
    return strip.resize((w, h))


def radial_glow(size, color, peak=255):
    """Soft radial light disc, RGBA."""
    s = 128
    img = Image.new("L", (s, s), 0)
    d = ImageDraw.Draw(img)
    for r in range(s // 2, 0, -1):
        a = int(peak * (1 - r / (s / 2)) ** 1.6)
        d.ellipse([s // 2 - r, s // 2 - r, s // 2 + r, s // 2 + r], fill=a)
    img = img.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), color + (0,))
    out.putalpha(img)
    return out


def soft_ellipse(base, box, fill, blur=6):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse(box, fill=fill)
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur * SS // 2))
    base.alpha_composite(layer)


# ---------------------------------------------------------------- scene
# Backdrop: warm near-black brown, lighter toward the top centre.
img = vgrad(W, H, (43, 26, 17), (16, 9, 6)).convert("RGBA")
img.alpha_composite(radial_glow(int(W * 1.15), (255, 196, 120), 120),
                    (int(W * 0.5 - W * 0.575), int(-H * 0.28)))

# Table: deep walnut band in the lower third.
table = Image.new("RGBA", (W, H), (0, 0, 0, 0))
td = ImageDraw.Draw(table)
td.rectangle([0, int(H * 0.66), W, H], fill=(30, 18, 11, 255))
for i in range(46):  # faint wood streaks
    y = random.uniform(H * 0.68, H * 0.99)
    td.line([0, y, W, y + random.uniform(-6, 6)],
            fill=(0, 0, 0, random.randint(14, 34)), width=random.randint(2, 5))
img.alpha_composite(table)

# Warm pool of light on the table under the plate.
img.alpha_composite(radial_glow(int(W * 0.95), (255, 178, 105), 88),
                    (int(W * 0.5 - W * 0.475), int(H * 0.60)))

draw = ImageDraw.Draw(img, "RGBA")

CX, CY = W // 2, int(H * 0.635)          # plate centre
PW, PH = int(W * 0.40), int(H * 0.115)    # plate radii

# Plate shadow, then the ceramic plate itself.
soft_ellipse(img, [CX - PW - 26, CY - PH + 30, CX + PW + 26, CY + PH + 58],
             (0, 0, 0, 150), blur=18)
draw.ellipse([CX - PW, CY - PH, CX + PW, CY + PH], fill=(216, 203, 186, 255))
draw.ellipse([CX - PW, CY - PH, CX + PW, CY + PH], outline=(150, 132, 112, 255),
             width=3 * SS)
draw.ellipse([CX - PW * 0.80, CY - PH * 0.72, CX + PW * 0.80, CY + PH * 0.72],
             fill=(198, 182, 163, 255))
draw.ellipse([CX - PW * 0.62, CY - PH * 0.50, CX + PW * 0.62, CY + PH * 0.50],
             fill=(208, 193, 174, 255))
# Plate sheen.
soft_ellipse(img, [CX - PW * 0.72, CY - PH * 0.86, CX - PW * 0.05, CY - PH * 0.30],
             (255, 255, 255, 60), blur=10)

# ------------------------------------------------------------- the cake
KW, KH = int(W * 0.235), int(H * 0.088)   # cake top radii
KT = int(H * 0.475)                        # cake top centre y
KB = int(H * 0.635)                        # cake base y

# Cake body: vertical gradient built from horizontal slices.
body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(body)
steps = 60
for i in range(steps):
    t = i / steps
    y0 = KT + (KB - KT) * t
    y1 = KT + (KB - KT) * (i + 1) + 2
    col = lerp((74, 44, 26), (38, 21, 12), t)
    bd.rectangle([CX - KW, y0, CX + KW, y1], fill=col + (255,))
# Round the silhouette: mask with a superellipse-ish shape.
mask = Image.new("L", (W, H), 0)
md = ImageDraw.Draw(mask)
md.rounded_rectangle([CX - KW, KT - KH, CX + KW, KB], radius=int(KW * 0.42), fill=255)
body.putalpha(Image.composite(body.getchannel("A"), Image.new("L", (W, H), 0), mask))
img.alpha_composite(body)
draw = ImageDraw.Draw(img, "RGBA")

# Ambient occlusion where cake meets plate.
soft_ellipse(img, [CX - KW * 0.98, KB - 16, CX + KW * 0.98, KB + 26],
             (0, 0, 0, 120), blur=8)

# Cake top: slightly domed, matte cocoa with a satin rim.
draw.ellipse([CX - KW, KT - KH, CX + KW, KT + KH], fill=(88, 54, 32, 255))
draw.ellipse([CX - KW * 0.93, KT - KH * 0.88, CX + KW * 0.93, KT + KH * 0.88],
             fill=(97, 60, 35, 255))
for i in range(260):  # cocoa dust speckle
    x = random.gauss(CX, KW * 0.55)
    y = random.gauss(KT, KH * 0.5)
    if ((x - CX) / KW) ** 2 + ((y - KT) / KH) ** 2 < 0.92:
        r = random.uniform(1.5, 4.5) * SS / 2
        draw.ellipse([x - r, y - r, x + r, y + r],
                     fill=(60, 35, 19, random.randint(50, 110)))

# ------------------------------------------------------ the cut & the lava
# A wedge is cut from the front-right; molten chocolate pours out.
WX, WY = CX + int(KW * 0.52), KB - int((KB - KT) * 0.16)
# Exposed molten face inside the cut.
draw.polygon([(CX + int(KW * 0.16), KT + int(KH * 0.55)),
              (CX + KW, KB - int((KB - KT) * 0.30)),
              (CX + KW, KB),
              (CX + int(KW * 0.20), KB)],
             fill=(52, 29, 15, 255))
draw.polygon([(CX + int(KW * 0.24), KT + int(KH * 0.72)),
              (CX + int(KW * 0.94), KB - int((KB - KT) * 0.26)),
              (CX + int(KW * 0.94), KB - 4),
              (CX + int(KW * 0.28), KB - 4)],
             fill=(140, 74, 28, 255))
# Glossy wet sheen sweeping across the molten face.
draw.polygon([(CX + int(KW * 0.30), KT + int(KH * 0.80)),
              (CX + int(KW * 0.62), KB - int((KB - KT) * 0.30)),
              (CX + int(KW * 0.70), KB - 6),
              (CX + int(KW * 0.38), KB - 6)],
             fill=(178, 104, 42, 255))
draw.line([CX + int(KW * 0.34), KB - 14, CX + int(KW * 0.60),
           KT + int(KH * 0.95)], fill=(255, 205, 150, 190), width=5 * SS // 2)

# The flowing lava: a wide, tapered glossy ribbon from the cut to the plate.
lava = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ld = ImageDraw.Draw(lava)
pts_left = [(WX - 92, WY - 66), (WX - 84, WY + 6), (WX - 62, WY + 62),
            (WX - 30, WY + 106)]
pts_right = [(WX + 76, WY - 60), (WX + 88, WY + 2), (WX + 80, WY + 56),
             (WX + 52, WY + 102)]
ld.polygon(pts_left + pts_right[::-1], fill=(104, 52, 20, 255))
# Inner, brighter core of the flow.
ld.polygon([(WX - 56, WY - 58), (WX - 46, WY + 8), (WX - 30, WY + 68),
            (WX - 6, WY + 98), (WX + 38, WY + 90), (WX + 50, WY + 40),
            (WX + 44, WY - 52)], fill=(150, 80, 30, 255))
# Bright wet streak down the middle of the flow.
ld.polygon([(WX - 22, WY - 54), (WX - 14, WY + 10), (WX - 8, WY + 66),
            (WX + 2, WY + 92), (WX + 16, WY + 60), (WX + 14, WY - 48)],
           fill=(196, 122, 52, 255))
img.alpha_composite(lava)
draw = ImageDraw.Draw(img, "RGBA")

# Lava pool spreading on the plate, glossy.
PX, PY = WX + 6, KB + int(H * 0.045)
PRX, PRY = int(W * 0.105), int(H * 0.030)
draw.ellipse([PX - PRX, PY - PRY, PX + PRX, PY + PRY], fill=(104, 52, 20, 255))
draw.ellipse([PX - PRX * 0.82, PY - PRY * 0.78, PX + PRX * 0.82, PY + PRY * 0.78],
             fill=(124, 64, 25, 255))
draw.ellipse([PX - PRX * 0.55, PY - PRY * 0.55, PX + PRX * 0.45, PY + PRY * 0.45],
             fill=(146, 78, 30, 255))
# Specular streaks on pool and flow.
soft_ellipse(img, [PX - PRX * 0.62, PY - PRY * 0.62, PX - PRX * 0.05, PY - PRY * 0.05],
             (255, 226, 180, 165), blur=5)
soft_ellipse(img, [WX - 30, WY - 46, WX - 6, WY + 52], (255, 214, 160, 120), blur=5)
soft_ellipse(img, [PX + PRX * 0.28, PY - PRY * 0.30, PX + PRX * 0.52, PY + PRY * 0.18],
             (255, 236, 200, 120), blur=4)

# ------------------------------------------------------------ drizzle
driz = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dd = ImageDraw.Draw(driz)
for k, off in enumerate([-0.52, -0.18, 0.16, 0.5]):
    pts = []
    for i in range(41):
        t = i / 40
        x = CX + (t - 0.5) * KW * 1.5
        y = KT + off * KH + math.sin(t * math.pi * 2.2 + k) * KH * 0.16
        pts.append((x, y))
    dd.line(pts, fill=(56, 30, 14, 235), width=int(7 * SS / 2))
    hi = [(x, y - 3 * SS / 2) for x, y in pts]
    dd.line(hi, fill=(150, 88, 40, 130), width=int(2.4 * SS / 2))
img.alpha_composite(driz)
draw = ImageDraw.Draw(img, "RGBA")


# ------------------------------------------------------------ truffles
def truffle(cx, cy, r):
    soft_ellipse(img, [cx - r, cy + r * 0.55, cx + r, cy + r * 1.05],
                 (0, 0, 0, 130), blur=7)
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(28):  # sphere shading, darker toward the base
        t = i / 28
        y0 = cy - r + 2 * r * t
        half = r * math.sqrt(max(0.0, 1 - (2 * t - 1) ** 2))
        col = lerp((104, 62, 32), (40, 22, 11), t ** 1.3)
        d.line([cx - half, y0, cx + half, y0], fill=col + (255,), width=int(2 * r / 28) + 2)
    for i in range(60):  # cocoa dust
        a = random.uniform(0, math.tau)
        rr = r * math.sqrt(random.uniform(0, 0.92))
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.96
        d.point((x, y), fill=(56, 32, 16, 160))
    soft_ellipse(img, [cx - r * 0.52, cy - r * 0.72, cx - r * 0.08, cy - r * 0.28],
                 (255, 220, 175, 150), blur=4)


truffle(CX - int(KW * 1.28), KB + int(H * 0.012), int(W * 0.037))
truffle(CX - int(KW * 1.02), KB + int(H * 0.034), int(W * 0.029))
truffle(CX + int(KW * 1.30), KB + int(H * 0.028), int(W * 0.026))

# Chocolate shards leaning by the cake.
for (sx, sy, ang, ln) in [(CX - KW * 0.92, KB - 6, -0.5, 120),
                          (CX - KW * 0.80, KB - 2, -0.28, 92),
                          (CX + KW * 1.06, KB - 2, 0.42, 84)]:
    x2 = sx + math.sin(ang) * ln * SS / 2
    y2 = sy - math.cos(ang) * ln * SS / 2
    draw.polygon([(sx - 13, sy), (sx + 13, sy), (x2 + 4, y2), (x2 - 9, y2)],
                 fill=(66, 38, 19, 255))
    draw.line([sx - 4, sy - 4, x2 - 4, y2 + 4], fill=(140, 84, 40, 200),
              width=3 * SS // 2)

# A few glossy drips on the plate rim.
for (dx, dy, dr) in [(CX - PW * 0.42, CY + PH * 0.30, 15),
                     (CX + PW * 0.55, CY + PH * 0.52, 11),
                     (CX + PW * 0.20, CY + PH * 0.78, 8)]:
    draw.ellipse([dx - dr, dy - dr * 0.6, dx + dr, dy + dr * 0.6],
                 fill=(110, 56, 22, 255))
    soft_ellipse(img, [dx - dr * 0.5, dy - dr * 0.4, dx, dy],
                 (255, 226, 180, 150), blur=3)

# ---------------------------------------------------------------- steam
steam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(steam)
for k, xoff in enumerate([-70, 6, 78]):
    pts = []
    for i in range(61):
        t = i / 60
        x = CX + xoff * SS / 2 + math.sin(t * 5.2 + k * 1.7) * 20 * SS / 2 * t
        y = KT - KH - 14 - t * H * 0.17
        pts.append((x, y))
    sd.line(pts, fill=(255, 244, 230, 46), width=int(15 * SS / 2))
steam = steam.filter(ImageFilter.GaussianBlur(9 * SS // 2))
img.alpha_composite(steam)

# -------------------------------------------------------------- vignette
vig = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse([-W * 0.22, -H * 0.22, W * 1.22, H * 1.22], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(90 * SS // 2))
black = Image.new("RGBA", (W, H), (5, 2, 1, 255))
img = Image.composite(img, black, vig.point(lambda v: 90 + v * 165 // 255))

img = img.convert("RGB").resize((1024, 1024), Image.LANCZOS)
img.save(OUT, "PNG", optimize=True)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
