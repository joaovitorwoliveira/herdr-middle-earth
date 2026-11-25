# The backdrop behind the terminals: a halftone glow, one per theme. A grid of round dots whose
# size and color follow a soft light field rising from the bottom-right corner, an ember over
# Mordor's dark and a field of gold and green over the Shire's parchment. The halftone look comes
# from realtonypark/herdr-factory.
import math, os
from PIL import Image, ImageDraw

W, H, PITCH = 2400, 1400, 12
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backgrounds", "middle-earth")
# Dots smaller than this would vanish once the image is scaled down.
MIN_RADIUS = 0.9
# Lighter than this, a dot is left out.
CUTOFF = 0.04

THEMES = {
    "dark": dict(
        paper="#0f0b09",
        ramp=[(0.00, "#1e120d"), (0.40, "#5a1c0c"), (0.70, "#a8360f"), (0.88, "#e0582a"), (1.00, "#ff9a52")],
        small=0.10, large=0.44,
    ),
    "light": dict(
        paper="#f4ecd8",
        ramp=[(0.00, "#e9dec2"), (0.40, "#dcc89a"), (0.70, "#c9b070"), (0.88, "#a9a95e"), (1.00, "#7f9a52")],
        small=0.08, large=0.40,
    ),
}


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def blob(x, y, cx, cy, sx, sy):
    return math.exp(-(((x - cx) / sx) ** 2 + ((y - cy) / sy) ** 2))


def light(x, y):
    v = (0.95 * blob(x, y, 1.00, 1.05, 0.30, 0.40)
         + 0.45 * blob(x, y, 0.80, 0.85, 0.30, 0.22)
         + 0.35 * blob(x, y, 0.97, 0.55, 0.12, 0.40)
         + 0.20 * blob(x, y, 0.04, 0.00, 0.18, 0.12))
    # A soft knee instead of a clamp, so the brightest corner keeps its gradient.
    return (1 - math.exp(-1.6 * v)) / (1 - math.exp(-1.6 * 1.3)) * 0.95 + 0.06


def colour(ramp, v):
    stops = [(level, rgb(c)) for level, c in ramp]
    for (lo, a), (hi, b) in zip(stops, stops[1:]):
        if v <= hi:
            return mix(a, b, (v - lo) / (hi - lo))
    return stops[-1][1]


# A fixed +/-2 nudge per dot, so the field dithers instead of banding.
def jitter(a, b):
    return ((a * 7 + b * 13) % 5) - 2


def draw(t):
    img = Image.new("RGB", (W, H), rgb(t["paper"]))
    d = ImageDraw.Draw(img)
    for row in range(H // PITCH):
        y = (row + 0.5) * PITCH
        for col in range(W // PITCH):
            x = (col + 0.5) * PITCH
            v = light(x / W, y / H) + jitter(col, row) * 0.014
            if v <= CUTOFF:
                continue
            r = max(MIN_RADIUS, (t["small"] + (t["large"] - t["small"]) * v ** 1.2) * PITCH)
            d.ellipse((x - r, y - r, x + r, y + r), fill=colour(t["ramp"], min(0.99, v)))
    return img


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, t in THEMES.items():
        path = os.path.join(OUT, f"{name}.png")
        draw(t).save(path)
        print("wrote", os.path.normpath(path))
