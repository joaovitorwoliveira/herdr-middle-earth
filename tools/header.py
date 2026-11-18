import os
import sprites
from PIL import Image

# The README's cast strips: the heroes side by side on a transparent background, so they read on
# GitHub's light and dark pages alike: the cast, its rare editions, and Epic Sax Gandalf mid-riff.
CAST = ["gandalf", "aragorn", "frodo", "sam", "legolas", "gimli", "sauron"]
SCALE = 8
GAP = 4
DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")
TABLE = sprites.all_sprites()


def strip(names, out):
    size = sprites.SIZE
    img = Image.new("RGBA", (len(names) * size + (len(names) - 1) * GAP, size), (0, 0, 0, 0))
    for i, name in enumerate(names):
        rows, palette = TABLE[name]
        ox = i * (size + GAP)
        for y, row in enumerate(rows):
            for x, c in enumerate(row):
                if c != ".":
                    img.putpixel((ox + x, y), Image.new("RGB", (1, 1), palette[c]).getpixel((0, 0)) + (255,))
    img.resize((img.width * SCALE, img.height * SCALE), Image.NEAREST).save(out)
    print("wrote", out)


strip(CAST, os.path.join(DOCS, "header.png"))
strip([f"{name}-rare" for name in CAST], os.path.join(DOCS, "rare.png"))
strip(["gandalf-sax-work", "gandalf-sax-2"], os.path.join(DOCS, "sax.png"))
