import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont

# The README's overview: the Shire and Mordor screenshots side by side in one dark frame, so the
# cards stay readable at README width. Takes the two shots as arguments, else docs/shire.png and docs/mordor.png.
# Both shots must have the same height; each is cropped to its left part, CROP_WIDTH_PER_HEIGHT times its height wide.
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DOCS = os.path.join(ROOT, "docs")
FONT = "/System/Library/Fonts/SFNS.ttf"
WIDTH = 2000
# The crop's width as a share of the shot's height, so it holds for the full-size and the docs shots alike.
CROP_WIDTH_PER_HEIGHT = 0.92
PAD = 64
GAP = 36
FRAME_RADIUS = 40
SHOT_RADIUS = 22
FRAME = (24, 20, 17)
SHOT_BORDER = (255, 255, 255, 36)
KICKER = "YOUR AGENTS. THEIR QUEST."
TITLE = "One layout to rule your agents."
KICKER_TRACKING = 4
PANELS = [
    ("shire", "THE SHIRE", "Light mode. Green hills, warm parchment."),
    ("mordor", "MORDOR", "Dark mode. Ash and fire. Sauron joins the cast."),
]


def theme(name):
    with open(os.path.join(ROOT, "themes", f"{name}.json")) as f:
        return json.load(f)


def font(size, weight):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_name(weight)
    return f


def rgb(hex_color):
    return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))


def tracked(draw, xy, text, fnt, fill, tracking):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking


def rounded(img, radius):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, img.width - 1, img.height - 1), radius, fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def main(shots):
    mordor = theme("mordor")
    accents = {"shire": rgb(theme("shire")["colors"]["accent"]), "mordor": rgb(mordor["colors"]["accent"])}
    text = rgb(mordor["foreground"])
    muted = rgb(mordor["colors"]["muted"])

    kicker_font, title_font = font(26, "Semibold"), font(64, "Bold")
    label_font, caption_font = font(30, "Bold"), font(28, "Regular")

    panel_w = (WIDTH - 2 * PAD - GAP) // 2
    images = [Image.open(path).convert("RGBA") for path in shots]
    if len({img.height for img in images}) != 1:
        sys.exit(f"overview.py: the shots differ in height ({[img.height for img in images]}); take them in windows of the same height.")
    images = [img.crop((0, 0, round(img.height * CROP_WIDTH_PER_HEIGHT), img.height)) for img in images]
    images = [img.resize((panel_w, round(img.height * panel_w / img.width)), Image.LANCZOS) for img in images]
    panel_h = max(img.height for img in images)

    top = PAD + 36 + 18 + 78 + 44
    height = top + panel_h + 30 + 40 + 44 + PAD
    canvas = Image.new("RGBA", (WIDTH, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((0, 0, WIDTH - 1, height - 1), FRAME_RADIUS, fill=FRAME)

    tracked(draw, (PAD, PAD), KICKER, kicker_font, accents["mordor"], KICKER_TRACKING)
    draw.text((PAD, PAD + 36 + 18), TITLE, font=title_font, fill=text)

    for i, ((key, label, caption), img) in enumerate(zip(PANELS, images)):
        x = PAD + i * (panel_w + GAP)
        canvas.alpha_composite(rounded(img, SHOT_RADIUS), (x, top))
        draw.rounded_rectangle((x, top, x + img.width - 1, top + img.height - 1), SHOT_RADIUS, outline=SHOT_BORDER, width=2)
        y = top + panel_h + 30
        draw.rounded_rectangle((x, y + 6, x + 6, y + 30), 3, fill=accents[key])
        tracked(draw, (x + 20, y), label, label_font, accents[key], KICKER_TRACKING)
        draw.text((x + 20, y + 44), caption, font=caption_font, fill=muted)

    out = os.path.join(DOCS, "overview.png")
    canvas.quantize(colors=256, method=Image.Quantize.FASTOCTREE).save(out, optimize=True)
    print("wrote", out)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and len(args) != 2:
        sys.exit("usage: python3 tools/overview.py [shire.png mordor.png]")
    main(args or [os.path.join(DOCS, "shire.png"), os.path.join(DOCS, "mordor.png")])
