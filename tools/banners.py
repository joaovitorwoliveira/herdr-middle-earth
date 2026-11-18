import os
import sprites as pixels
from PIL import Image

# Notification Center takes PNG, not SVG; 8x keeps the pixels crisp.
SCALE = 8
OUT = os.path.join(pixels.HOME, "fellowship", "banners")
CAST = ["gandalf", "aragorn", "frodo", "sam", "legolas", "gimli", "sauron"]


def png(rows, palette, path):
    img = Image.new("RGBA", (pixels.SIZE, pixels.SIZE), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c != ".":
                img.putpixel((x, y), Image.new("RGB", (1, 1), palette[c]).getpixel((0, 0)) + (255,))
    img.resize((pixels.SIZE * SCALE, pixels.SIZE * SCALE), Image.NEAREST).save(path)


os.makedirs(OUT, exist_ok=True)
for name in CAST + pixels.RARE_CAST:
    for pose in ("blocked", "done"):
        png(*pixels.badged(name, pose), os.path.join(OUT, f"{name}-{pose}.png"))
print(len(os.listdir(OUT)), "banners")
