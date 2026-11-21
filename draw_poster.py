#!/usr/bin/env python3
"""Draw the travel poster for LUMARIS, a place that does not exist.

LUMARIS is a lagoon town held in one long dusk. Its single landmark is
the Lantern Spire: a tower of stacked, glowing lantern tiers that rises
out of still water and is never lit and never put out - it simply burns,
amber against the teal evening, while small lantern boats drift below.

The poster is drawn from scratch with Pillow and the DejaVu fonts.
It saves poster.png (1024 x 1024) next to this script.
"""

import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 1024
HORIZON = 648  # where the lagoon meets the sky

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

CREAM = (247, 234, 208)
GOLD = (240, 201, 138)
AMBER = (232, 160, 76)
DEEP_AMBER = (198, 120, 44)
INK = (13, 32, 48)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vertical_gradient(size, stops):
    """stops: list of (y_fraction, rgb). Returns an RGB image."""
    img = Image.new("RGB", size)
    px = img.load()
    n = len(stops)
    for y in range(size[1]):
        f = y / (size[1] - 1)
        for i in range(n - 1):
            f0, c0 = stops[i]
            f1, c1 = stops[i + 1]
            if f0 <= f <= f1:
                t = 0.0 if f1 == f0 else (f - f0) / (f1 - f0)
                col = lerp(c0, c1, t)
                break
        else:
            col = stops[-1][1]
        for x in range(size[0]):
            px[x, y] = col
    return img


def draw_text_spaced(draw, cx, y, text, font, fill, spacing=0, shadow=None):
    """Draw text centred on cx at baseline y, with extra letter spacing."""
    widths = []
    total = 0
    for ch in text:
        w = draw.textlength(ch, font=font)
        widths.append(w)
        total += w
    total += spacing * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        if shadow is not None:
            draw.text((x + 3, y + 3), ch, font=font, fill=shadow)
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + spacing
    return total


def soft_circle(layer, cx, cy, r, color, blur):
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    return layer.filter(ImageFilter.GaussianBlur(blur))


def main():
    rng = random.Random(20261121)

    # ---- sky: deep indigo dusk melting into a warm amber band ----
    sky = vertical_gradient(
        (W, HORIZON + 2),
        [
            (0.00, (11, 22, 46)),
            (0.45, (18, 52, 78)),
            (0.78, (38, 94, 110)),
            (0.94, (214, 138, 66)),
            (1.00, (244, 197, 126)),
        ],
    )
    img = Image.new("RGB", (W, H))
    img.paste(sky, (0, 0))

    # ---- lagoon: dark teal water, warming toward the horizon ----
    water = vertical_gradient(
        (W, H - HORIZON),
        [
            (0.00, (196, 138, 74)),
            (0.06, (52, 96, 104)),
            (0.45, (16, 54, 72)),
            (1.00, (8, 30, 46)),
        ],
    )
    img.paste(water, (0, HORIZON))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # ---- stars, only in the upper dark sky ----
    for _ in range(150):
        x = rng.uniform(0, W)
        y = rng.uniform(0, 380)
        r = rng.uniform(0.6, 1.8)
        a = rng.randint(90, 220)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(240, 235, 215, a)[:3])
    for _ in range(12):
        x = rng.uniform(60, W - 60)
        y = rng.uniform(30, 300)
        s = rng.uniform(4, 9)
        d.line([x - s, y, x + s, y], fill=(250, 244, 220), width=1)
        d.line([x, y - s, x, y + s], fill=(250, 244, 220), width=1)

    # ---- the low amber moon, upper right, clear of the title ----
    moon_cx, moon_cy, moon_r = 862, 322, 58
    glow = Image.alpha_composite(
        glow, soft_circle(Image.new("RGBA", (W, H), (0, 0, 0, 0)),
                          moon_cx, moon_cy, moon_r + 46,
                          (244, 196, 120, 70), 34))
    d.ellipse([moon_cx - moon_r, moon_cy - moon_r,
               moon_cx + moon_r, moon_cy + moon_r], fill=(250, 228, 178))
    # a few soft craters so the moon reads as a moon, not a plain disc
    for dx, dy, r in [(-24, -18, 9), (20, 18, 11), (-12, 24, 6), (26, -24, 5)]:
        cx, cy = moon_cx + dx, moon_cy + dy
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(236, 208, 152))

    # ---- birds, small dark chevrons crossing the dusk ----
    for bx, by, s in [(180, 300, 14), (240, 268, 11), (300, 316, 9),
                      (930, 430, 11), (700, 120, 10)]:
        d.line([bx - s, by, bx, by - s * 0.55], fill=INK, width=3)
        d.line([bx, by - s * 0.55, bx + s, by], fill=INK, width=3)

    # ---- distant headlands along the horizon ----
    hills = [(0, 648), (120, 622), (260, 640), (400, 618), (540, 644),
             (700, 624), (860, 642), (1024, 628), (1024, 660), (0, 660)]
    d.polygon(hills, fill=(10, 38, 54))
    # a thin gold rim where the sun has just gone
    d.line([(0, 646), (1024, 646)], fill=(244, 197, 126), width=2)

    # ---- the Lantern Spire: stacked glowing tiers over still water ----
    # The spire's crown sits below the tagline so the finial never
    # collides with the lettering (first draft had it touching "LIGHT").
    cx = 512
    base_y = 668
    top_y = 338
    glow = Image.alpha_composite(
        glow, soft_circle(Image.new("RGBA", (W, H), (0, 0, 0, 0)),
                          cx, 480, 190, (232, 160, 76, 60), 60))

    tiers = 9
    for i in range(tiers):
        t = i / (tiers - 1)  # 0 at the base, 1 at the top
        y1 = base_y - t * (base_y - top_y)
        y0 = base_y - ((i + 1) / (tiers - 1)) * (base_y - top_y) - 4
        half_w = 96 - t * 62
        # warm lantern panel, brighter toward the middle of the spire
        warm = lerp((178, 96, 30), (252, 196, 110), 0.35 + 0.5 * math.sin(t * math.pi))
        d.polygon([(cx - half_w, y1), (cx + half_w, y1),
                   (cx + half_w - 8, y0), (cx - half_w + 8, y0)], fill=warm)
        # dark frame around each tier
        d.line([(cx - half_w, y1), (cx + half_w, y1)], fill=(58, 28, 10), width=4)
        d.line([(cx - half_w + 8, y0), (cx + half_w - 8, y0)], fill=(58, 28, 10), width=4)
        # glowing window slits on each tier
        win_w = half_w * 0.62
        win_y = (y0 + y1) / 2
        d.rectangle([cx - win_w, win_y - 7, cx + win_w, win_y + 7],
                    fill=(255, 226, 160))
        d.line([cx, win_y - 7, cx, win_y + 7], fill=(120, 66, 20), width=2)

    # spire crown: small dome and finial
    d.polygon([(cx - 30, top_y - 2), (cx + 30, top_y - 2),
               (cx + 12, top_y - 34), (cx - 12, top_y - 34)], fill=(58, 28, 10))
    d.ellipse([cx - 13, top_y - 52, cx + 13, top_y - 26], fill=(252, 196, 110))
    d.line([cx, top_y - 52, cx, top_y - 72], fill=(252, 196, 110), width=4)
    d.ellipse([cx - 5, top_y - 78, cx + 5, top_y - 68], fill=(255, 226, 160))
    glow = Image.alpha_composite(
        glow, soft_circle(Image.new("RGBA", (W, H), (0, 0, 0, 0)),
                          cx, top_y - 70, 26, (255, 226, 160, 110), 12))

    # spire base: a low stone quay where it meets the water
    d.polygon([(cx - 118, base_y), (cx + 118, base_y),
               (cx + 96, base_y + 22), (cx - 96, base_y + 22)], fill=(24, 46, 58))
    d.line([(cx - 118, base_y), (cx + 118, base_y)], fill=(244, 197, 126), width=2)

    # ---- reflection of the spire in the lagoon ----
    refl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(refl)
    for j in range(46):
        y = base_y + 26 + j * 7
        if y > 1000:
            break
        w = 92 * (1 - j / 60) + rng.uniform(-8, 8)
        alpha = int(150 * (1 - j / 46))
        rd.line([cx - w, y, cx + w, y],
                fill=(232, 160, 76, max(alpha, 0)), width=3)
    refl = refl.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img.convert("RGBA"), refl)

    # ---- moon path on the water, right of the spire ----
    mpath = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mpath)
    for j in range(30):
        y = HORIZON + 14 + j * 11
        w = 34 + rng.uniform(-14, 14) + j * 0.8
        alpha = int(110 * (1 - j / 34))
        md.line([moon_cx - w, y, moon_cx + w, y],
                fill=(250, 228, 178, max(alpha, 0)), width=3)
    mpath = mpath.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, mpath)

    # ---- two small lantern boats drifting on the lagoon ----
    for bx, by, s in [(212, 792, 1.0), (836, 856, 0.8)]:
        hull_w, hull_h = int(58 * s), int(14 * s)
        d = ImageDraw.Draw(img)
        d.polygon([(bx - hull_w, by), (bx + hull_w, by),
                   (bx + hull_w - 12, by + hull_h),
                   (bx - hull_w + 12, by + hull_h)], fill=(20, 34, 44))
        d.ellipse([bx - 9 * s, by - 26 * s, bx + 9 * s, by - 8 * s],
                  fill=(255, 210, 130))
        d.line([bx, by - 26 * s, bx, by - 40 * s], fill=(60, 40, 16), width=2)
        # boat's own little glow on the water
        glow = Image.alpha_composite(
            glow, soft_circle(Image.new("RGBA", (W, H), (0, 0, 0, 0)),
                              bx, by + 8, int(26 * s),
                              (255, 210, 130, 70), 10))

    img = Image.alpha_composite(img, glow)
    d = ImageDraw.Draw(img)

    # ---- water shimmer: faint horizontal strokes across the lagoon ----
    for _ in range(90):
        x = rng.uniform(0, W - 120)
        y = rng.uniform(HORIZON + 20, 990)
        ln = rng.uniform(24, 110)
        a = rng.randint(18, 60)
        col = (200, 220, 225) if rng.random() < 0.5 else (240, 190, 120)
        d.line([x, y, x + ln, y], fill=col, width=1)

    # ---- the name, set large across the top of the dusk ----
    title_font = ImageFont.truetype(SERIF_BOLD, 116)
    draw_text_spaced(d, W // 2, 78, "LUMARIS", title_font, CREAM,
                     spacing=26, shadow=(8, 18, 38))

    # ---- the tagline, small, beneath the name ----
    tag_font = ImageFont.truetype(SANS_BOLD, 27)
    tag = "WHERE THE LIGHT NEVER GOES OUT"
    tw = draw_text_spaced(d, W // 2, 218, tag, tag_font, GOLD, spacing=7)
    # thin rules flanking the tagline, kept well inside the frame
    rule_y = 232
    d.line([W // 2 - tw / 2 - 82, rule_y, W // 2 - tw / 2 - 26, rule_y],
           fill=GOLD, width=2)
    d.line([W // 2 + tw / 2 + 26, rule_y, W // 2 + tw / 2 + 82, rule_y],
           fill=GOLD, width=2)

    # ---- thin cream frame, the vintage poster edge ----
    d.rectangle([26, 26, W - 27, H - 27], outline=CREAM, width=3)
    d.rectangle([34, 34, W - 35, H - 35], outline=(247, 234, 208, 90), width=1)

    img.convert("RGB").save("poster.png", optimize=True)
    print("saved poster.png")


if __name__ == "__main__":
    main()
