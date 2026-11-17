import os
import sprites
from PIL import Image

# The README's header: the cast side by side on a transparent background, so it reads on
# GitHub's light and dark pages alike.
CAST = ["gandalf", "frodo", "sam", "legolas", "gimli", "sauron"]
SCALE = 8
GAP = 4
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "header.png")

size = sprites.SIZE
img = Image.new("RGBA", (len(CAST) * size + (len(CAST) - 1) * GAP, size), (0, 0, 0, 0))
for i, name in enumerate(CAST):
    rows, palette = sprites.SPRITES[name]
    ox = i * (size + GAP)
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c != ".":
                img.putpixel((ox + x, y), Image.new("RGB", (1, 1), palette[c]).getpixel((0, 0)) + (255,))
img.resize((img.width * SCALE, img.height * SCALE), Image.NEAREST).save(OUT)
print("wrote", OUT)
