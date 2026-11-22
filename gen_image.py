"""Paint a glossy dark-chocolate lava cake with Pillow, pixel by pixel.

The scene is built on an oversized canvas (twice the final size) and
shrunk at the end, which smooths every curve.  Layers, back to front:
warm backdrop, porcelain plate, the cake itself, a molten pour that
spills over the dome, truffles, drifting steam, and a soft vignette.
"""

import math
import random

from PIL import Image, ImageDraw, ImageFilter

SCALE = 2
SIDE = 1024 * SCALE
random.seed(20261123)

# palette: deep browns, caramel glints, cream porcelain
INK = (24, 12, 7)
CRUST = (52, 27, 15)
CRUST_LIGHT = (84, 46, 24)
LAVA = (96, 50, 22)
LAVA_HOT = (140, 78, 36)
PORCELAIN = (232, 222, 208)
PORCELAIN_SHADE = (196, 182, 160)
CREAM = (250, 244, 230)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vertical_wash(canvas, top, bottom):
    """Fill the canvas with a top-to-bottom colour blend."""
    pen = ImageDraw.Draw(canvas)
    height = canvas.height
    for row in range(height):
        pen.line([(0, row), (canvas.width, row)], fill=lerp(top, bottom, row / height))


def glow_spot(canvas, cx, cy, radius, colour, strength):
    """Composite a soft radial halo centred at (cx, cy)."""
    halo = Image.new("RGB", canvas.size, (0, 0, 0))
    pen = ImageDraw.Draw(halo)
    steps = 24
    for i in range(steps, 0, -1):
        r = radius * i / steps
        fade = (1 - i / steps) ** 2 * strength
        tint = tuple(int(c * fade) for c in colour)
        pen.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tint)
    halo = halo.filter(ImageFilter.GaussianBlur(radius / 3))
    from PIL import ImageChops

    return ImageChops.add(canvas, halo)


def plateware(pen):
    """Porcelain plate with a rim, seen at a shallow angle."""
    cx, cy = SIDE // 2, int(SIDE * 0.78)
    rx, ry = int(SIDE * 0.40), int(SIDE * 0.115)
    # drop shadow
    pen.ellipse([cx - rx, cy - ry + 26, cx + rx, cy + ry + 26], fill=(10, 5, 3))
    # outer body and inner well
    pen.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=PORCELAIN_SHADE)
    pen.ellipse(
        [cx - rx + 26, cy - ry + 10, cx + rx - 26, cy + ry - 10], fill=PORCELAIN
    )
    inner_rx, inner_ry = int(rx * 0.72), int(ry * 0.66)
    pen.ellipse(
        [cx - inner_rx, cy - inner_ry, cx + inner_rx, cy + inner_ry],
        fill=lerp(PORCELAIN, PORCELAIN_SHADE, 0.45),
    )
    # a bright arc on the rim
    pen.arc([cx - rx + 14, cy - ry + 6, cx + rx - 14, cy + ry - 6],
            start=140, end=320, fill=CREAM, width=7)


def cake_body(pen):
    """The cake: a squat cylinder with a domed, cracked top."""
    cx = SIDE // 2
    top_y = int(SIDE * 0.40)
    base_y = int(SIDE * 0.76)
    half_w = int(SIDE * 0.235)
    dome_h = int(SIDE * 0.085)
    # side wall with a vertical sheen gradient
    for i in range(half_w * 2):
        x = cx - half_w + i
        t = i / (half_w * 2)
        sheen = math.sin(t * math.pi) ** 1.5
        shade = lerp(CRUST, CRUST_LIGHT, sheen * 0.75)
        pen.line([(x, top_y + dome_h // 2), (x, base_y)], fill=shade, width=2)
    # base ellipse to close the bottom
    pen.ellipse([cx - half_w, base_y - dome_h // 2, cx + half_w, base_y + dome_h // 2],
                fill=CRUST)
    for i in range(half_w * 2):
        x = cx - half_w + i
        t = i / (half_w * 2)
        sheen = math.sin(t * math.pi) ** 1.5
        shade = lerp(CRUST, CRUST_LIGHT, sheen * 0.75)
        pen.line([(x, top_y + dome_h // 2), (x, base_y)], fill=shade, width=2)
    pen.ellipse([cx - half_w, base_y - dome_h // 2, cx + half_w, base_y + dome_h // 2],
                fill=lerp(CRUST, INK, 0.35))
    # domed top
    pen.ellipse([cx - half_w, top_y - dome_h, cx + half_w, top_y + dome_h],
                fill=lerp(CRUST, CRUST_LIGHT, 0.35))
    pen.ellipse([cx - half_w + 30, top_y - dome_h + 16, cx + half_w - 30,
                 top_y + dome_h - 16], fill=lerp(CRUST_LIGHT, LAVA, 0.25))
    return cx, top_y, half_w, dome_h


def molten_pour(pen, cx, top_y, half_w, dome_h):
    """Lava pool on the dome plus a glossy stream over the front edge."""
    pool_rx, pool_ry = int(half_w * 0.52), int(dome_h * 0.62)
    pen.ellipse([cx - pool_rx, top_y - pool_ry, cx + pool_rx, top_y + pool_ry],
                fill=LAVA)
    pen.ellipse([cx - pool_rx + 16, top_y - pool_ry + 8, cx + pool_rx - 30,
                 top_y + pool_ry - 10], fill=LAVA_HOT)
    # drips finding their way down the wall
    drip_xs = [cx - 150, cx - 60, cx + 34, cx + 128]
    drip_len = [210, 330, 268, 176]
    for x, length in zip(drip_xs, drip_len):
        w = 26
        pen.rounded_rectangle([x - w // 2, top_y + 20, x + w // 2,
                               top_y + 20 + length], radius=w // 2, fill=LAVA)
        pen.ellipse([x - w // 2, top_y + 14 + length, x + w // 2,
                     top_y + 30 + length], fill=LAVA)
    # the main glossy cascade, centre front
    w = 74
    pen.rounded_rectangle([cx - w // 2, top_y + 16, cx + w // 2,
                           top_y + 706], radius=34, fill=LAVA)
    pen.rounded_rectangle([cx - w // 2 + 12, top_y + 30, cx - w // 2 + 30,
                           top_y + 672], radius=9, fill=LAVA_HOT)
    # puddle gathering on the plate
    pen.ellipse([cx - 210, int(SIDE * 0.755), cx + 230, int(SIDE * 0.815)],
                fill=LAVA)
    pen.ellipse([cx - 150, int(SIDE * 0.762), cx + 120, int(SIDE * 0.80)],
                fill=LAVA_HOT)


def truffle_cluster(pen):
    """Three truffles resting on the plate, dusted and highlighted."""
    spots = [(int(SIDE * 0.235), int(SIDE * 0.735), 56),
             (int(SIDE * 0.775), int(SIDE * 0.72), 64),
             (int(SIDE * 0.815), int(SIDE * 0.775), 44)]
    for x, y, r in spots:
        pen.ellipse([x - r, y - r // 3, x + r, y + r // 3], fill=(12, 6, 3))
        pen.ellipse([x - r, y - r, x + r, y + r], fill=CRUST)
        pen.ellipse([x - r + 8, y - r + 6, x + r - 10, y + r - 14],
                    fill=lerp(CRUST, CRUST_LIGHT, 0.5))
        pen.ellipse([x - r // 3, y - r // 2, x - r // 8, y - r // 4],
                    fill=(235, 205, 170))
        for _ in range(26):
            dx = random.randint(-r + 6, r - 6)
            dy = random.randint(-r + 6, r - 6)
            if dx * dx + dy * dy < (r - 8) ** 2:
                pen.point((x + dx, y + dy), fill=(30, 16, 9))


def steam_curls(canvas):
    """Translucent ribbons of steam above the warm cake."""
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    pen = ImageDraw.Draw(layer)
    for base_x, phase in [(SIDE * 0.42, 0.0), (SIDE * 0.52, 1.7), (SIDE * 0.60, 3.1)]:
        pts = []
        for k in range(60):
            t = k / 59
            y = SIDE * 0.36 - t * SIDE * 0.20
            x = base_x + math.sin(t * 5.2 + phase) * 26 * (0.4 + t)
            pts.append((x, y))
        pen.line(pts, fill=(255, 250, 240, 90), width=13)
    layer = layer.filter(ImageFilter.GaussianBlur(9))
    canvas.paste(Image.alpha_composite(canvas.convert("RGBA"), layer).convert("RGB"),
                 (0, 0))
    return canvas


def vignette(canvas):
    """Darken the corners so the cake holds the spotlight."""
    shade = Image.new("L", canvas.size, 0)
    pen = ImageDraw.Draw(shade)
    pen.ellipse([-int(SIDE * 0.18), -int(SIDE * 0.22), int(SIDE * 1.18),
                 int(SIDE * 1.22)], fill=255)
    shade = shade.filter(ImageFilter.GaussianBlur(SIDE // 6))
    black = Image.new("RGB", canvas.size, (6, 3, 2))
    return Image.composite(canvas, black, shade)


def render():
    scene = Image.new("RGB", (SIDE, SIDE), INK)
    vertical_wash(scene, (74, 44, 26), (26, 14, 8))
    scene = glow_spot(scene, SIDE // 2, int(SIDE * 0.52), int(SIDE * 0.46),
                      (255, 176, 96), 0.5)
    pen = ImageDraw.Draw(scene)
    plateware(pen)
    cx, top_y, half_w, dome_h = cake_body(pen)
    molten_pour(pen, cx, top_y, half_w, dome_h)
    truffle_cluster(pen)
    scene = steam_curls(scene)
    scene = vignette(scene)
    scene = scene.resize((1024, 1024), Image.LANCZOS)
    scene.save("entry.png")


if __name__ == "__main__":
    render()
