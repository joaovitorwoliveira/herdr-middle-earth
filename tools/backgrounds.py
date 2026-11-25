# Each realm's backdrop, behind the terminals: a 320x180 pixel scene per realm, in a Shire (light)
# and a Mordor (dark) version, drawn in the theme's own colors so the text on top stays readable.
import math, os, random
from PIL import Image, ImageDraw

W, H, SCALE = 320, 180, 2
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backgrounds", "middle-earth")
LIGHT_BG, DARK_BG = "#f4ecd8", "#2b2420"
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
INK, PAPER = (24, 16, 12), (255, 250, 236)


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def lt(c, a):
    return mix(c, PAPER, a)


def dk(c, a):
    return mix(c, INK, a)


def dith(x, y, t):
    return BAYER[y & 3][x & 3] < t * 16


class Scene:
    def __init__(self, dark, seed):
        self.dark = dark
        self.bg = rgb(DARK_BG if dark else LIGHT_BG)
        self.img = Image.new("RGB", (W, H), self.bg)
        self.d = ImageDraw.Draw(self.img)
        self.rnd = random.Random(seed)

    def c(self, hue, k):
        return mix(self.bg, rgb(hue), min(1, k * (1.4 if self.dark else 1)))

    def glow(self, hue, k):
        return mix(self.bg, rgb(hue), k)

    def px(self, x, y, col):
        if 0 <= x < W and 0 <= y < H:
            self.img.putpixel((int(x), int(y)), col)

    def get(self, x, y):
        return self.img.getpixel((min(W - 1, max(0, int(x))), min(H - 1, max(0, int(y)))))

    def vgrad(self, x0, y0, x1, y1, top, bot, steps=10):
        for y in range(y0, y1):
            f = (y - y0) / max(1, y1 - y0) * steps
            lvl, frac = int(f), f - int(f)
            a, b = mix(top, bot, lvl / steps), mix(top, bot, min(1, (lvl + 1) / steps))
            for x in range(x0, x1):
                self.px(x, y, b if dith(x, y, frac) else a)

    def sky(self, hue, k=0.14, stars=True, moon=None):
        if self.dark:
            self.vgrad(0, 0, W, H, mix(self.bg, (6, 6, 12), 0.55), self.bg)
            if stars:
                for _ in range(110):
                    x, y = self.rnd.randrange(W), self.rnd.randrange(int(H * 0.6))
                    b = self.rnd.choice([0.2, 0.3, 0.45, 0.7])
                    self.px(x, y, mix(self.bg, (240, 232, 214), b))
                    if b == 0.7 and self.rnd.random() < 0.3:
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            self.px(x + dx, y + dy, mix(self.bg, (240, 232, 214), 0.3))
            if moon:
                self.moon(*moon)
        else:
            self.vgrad(0, 0, W, H, self.c(hue, k), self.bg)

    def moon(self, x, y, r):
        for dy in range(-r - 4, r + 5):
            for dx in range(-r - 4, r + 5):
                dd = math.hypot(dx, dy)
                if dd <= r:
                    self.px(x + dx, y + dy, mix(self.bg, (244, 236, 216), 0.62 if (dx + dy) > -r // 2 or dd < r - 2 else 0.75))
                elif dd <= r + 4 and dith(x + dx, y + dy, 0.18 * (r + 4 - dd) / 4):
                    self.px(x + dx, y + dy, mix(self.bg, (244, 236, 216), 0.25))
        for cx, cy, cr in ((-2, -1, 1), (2, 2, 1), (1, -3, 0)):
            self.d.ellipse([x + cx - cr, y + cy - cr, x + cx + cr, y + cy + cr], fill=mix(self.bg, (244, 236, 216), 0.5))

    def clouds(self, x, y, w, col):
        for i in range(0, w, 7):
            r = 4 + int(3 * math.sin(i / w * math.pi))
            self.d.ellipse([x + i - r, y - r, x + i + r, y + r // 2], fill=col)
        self.d.rectangle([x - 4, y, x + w, y + 1], fill=col)
        for i in range(0, w, 7):
            r = 4 + int(3 * math.sin(i / w * math.pi))
            self.d.arc([x + i - r, y - r, x + i + r, y + r // 2], 200, 300, fill=lt(col, 0.4))

    def ridge(self, base, amps, col, jag=0.0, rim=None, tex=None, texp=0.0, x0=0, x1=W):
        ph = [self.rnd.random() * 6 for _ in amps]
        walk, tops = 0, {}
        for x in range(x0, x1):
            walk = max(-7, min(7, walk + self.rnd.uniform(-jag, jag)))
            y = int(base + sum(a * math.sin(x * f + p) for (a, f), p in zip(amps, ph)) + walk)
            tops[x] = y
            self.d.line([(x, y), (x, H)], fill=col)
            if tex:
                for yy in range(y + 2, H):
                    if self.rnd.random() < texp:
                        self.px(x, yy, tex)
        if rim:
            for x, y in tops.items():
                if x > x0 and tops[x - 1] >= y:
                    self.px(x, y, rim)
        return tops

    def blob(self, cx, cy, r, col, hi=None, lo=None):
        lo = lo or dk(col, 0.18)
        hi = hi or lt(col, 0.22)
        self.d.ellipse([cx - r + 1, cy - r + 1, cx + r + 1, cy + r + 1], fill=lo)
        self.d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        hr = max(1, r // 2)
        hx, hy = cx - r // 3, cy - r // 3
        for y in range(hy - hr, hy + hr + 1):
            for x in range(hx - hr, hx + hr + 1):
                if math.hypot(x - hx, y - hy) <= hr and dith(x, y, 0.5):
                    self.px(x, y, hi)

    def tree(self, x, ground, h, leaf, bark):
        self.d.rectangle([x - 1, ground - h // 2, x + 1, ground], fill=bark)
        self.d.line([(x, ground - h // 2), (x - 4, ground - h // 2 - 4)], fill=bark)
        self.d.line([(x, ground - h // 2 + 2), (x + 4, ground - h // 2 - 2)], fill=bark)
        r = max(3, h // 4)
        for dx, dy, rr in ((0, -h + r, r), (-r, -h + r * 2, r - 1), (r, -h + r * 2, r - 1), (0, -h + r * 2 + 2, r)):
            self.blob(x + dx, ground + dy, rr, leaf)

    def pine(self, x, ground, h, col):
        tiers = max(2, h // 6)
        for i in range(tiers):
            ty = ground - h + i * h // tiers
            w = 2 + (i + 1) * h // (tiers * 2)
            self.d.polygon([(x, ty), (x - w, ty + h // tiers + 2), (x + w, ty + h // tiers + 2)], fill=col)
            self.d.line([(x, ty), (x - w, ty + h // tiers + 2)], fill=lt(col, 0.18))
        self.d.line([(x, ground - 2), (x, ground)], fill=dk(col, 0.3))

    def smoke(self, x, y, n, col, drift=1):
        for i in range(n):
            r = 1 + i // 2
            cx, cy = x + int(drift * i * 1.6 + math.sin(i) * 2), y - i * 4
            t = 0.9 - i / n * 0.7
            for yy in range(cy - r, cy + r + 1):
                for xx in range(cx - r, cx + r + 1):
                    if math.hypot(xx - cx, yy - cy) <= r and dith(xx, yy, t):
                        self.px(xx, yy, col)

    def halo(self, x, y, r, col, strength=0.5):
        for yy in range(y - r, y + r + 1):
            for xx in range(x - r, x + r + 1):
                dd = math.hypot(xx - x, yy - y)
                if dd <= r and dith(xx, yy, strength * (1 - dd / r)):
                    self.px(xx, yy, col)

    def grass(self, y0, y1, col, n):
        for _ in range(n):
            x, y = self.rnd.randrange(W), self.rnd.randrange(y0, y1)
            self.px(x, y, col)
            self.px(x + self.rnd.choice((-1, 1)), y - 1, col)

    def mist(self, y0, y1, col, t=0.35):
        for y in range(y0, y1):
            f = t * (1 - abs((y - (y0 + y1) / 2) / ((y1 - y0) / 2)))
            for x in range(W):
                if dith(x, y, f):
                    self.px(x, y, col)


def shire(s):
    s.sky("#7aa0c0", 0.16, moon=(262, 26, 6))
    if not s.dark:
        s.clouds(40, 30, 40, lt(s.bg, 0.5))
        s.clouds(190, 18, 30, lt(s.bg, 0.5))
    green = "#4e7a32"
    s.ridge(108, [(5, 0.025), (3, 0.06)], s.c("#5a7a6a", 0.12), rim=s.c("#5a7a6a", 0.08))
    mid = s.c(green, 0.18)
    tops = s.ridge(120, [(7, 0.018), (4, 0.05)], mid, rim=lt(mid, 0.25))
    hedge = dk(mid, 0.22)
    for x in range(0, W, 3):
        s.px(x, tops[x] + 10 + int(3 * math.sin(x / 17)), hedge)
    for x in range(0, W, 2):
        if x % 76 < 30:
            for y in range(tops[x] + 3, 150, 3):
                s.px(x, y, lt(mid, 0.18))
    water = s.c("#3d6f8a", 0.32) if not s.dark else s.c("#3d6f8a", 0.28)
    river = [(150, 162), (180, 152), (220, 150), (260, 146), (320, 142)]
    s.d.line(river, fill=water, width=6)
    for x, y in river[1:]:
        s.d.line([(x - 6, y - 1), (x - 2, y - 1)], fill=lt(water, 0.4))
    stone = s.c("#8a7a5c", 0.42)
    s.d.rectangle([214, 144, 234, 147], fill=stone)
    s.d.arc([217, 145, 231, 157], 180, 360, fill=dk(stone, 0.2))
    s.d.rectangle([272, 128, 288, 142], fill=s.c("#b8a888", 0.45))
    s.d.polygon([(270, 128), (280, 120), (290, 128)], fill=s.c("#8a4a2a", 0.4))
    s.d.ellipse([287, 130, 299, 142], outline=s.c("#5a4a32", 0.55))
    s.d.line([(293, 130), (293, 142)], fill=s.c("#5a4a32", 0.55))
    s.d.line([(287, 136), (299, 136)], fill=s.c("#5a4a32", 0.55))
    hill = s.c(green, 0.28)
    s.d.ellipse([-10, 112, 160, 214], fill=hill)
    s.d.arc([-10, 112, 160, 214], 200, 300, fill=lt(hill, 0.3))
    s.grass(118, 170, dk(hill, 0.15), 160)
    s.d.rectangle([100, 110, 104, 122], fill=s.c("#8a5a3a", 0.5))
    s.smoke(102, 106, 9, lt(s.bg, 0.2) if not s.dark else mix(s.bg, (200, 190, 175), 0.3))
    frame = s.c("#5a4a32", 0.55)
    door = s.glow("#e0a640", 0.8) if s.dark else s.c(green, 0.62)
    s.d.ellipse([62, 132, 84, 154], fill=frame)
    s.d.ellipse([64, 134, 82, 152], fill=door)
    s.d.rectangle([62, 146, 84, 160], fill=hill)
    s.d.rectangle([64, 143, 82, 158], fill=door)
    s.d.rectangle([62, 143, 63, 158], fill=frame)
    s.d.rectangle([83, 143, 84, 158], fill=frame)
    for vx in range(67, 82, 4):
        s.d.line([(vx, 136), (vx, 157)], fill=dk(door, 0.12))
    s.d.rectangle([72, 145, 74, 147], fill=s.c("#e0a640", 0.9))
    win = s.glow("#e0a640", 0.7) if s.dark else s.c("#9ab0c0", 0.45)
    for wx in (40, 98):
        s.d.ellipse([wx, 138, wx + 10, 148], fill=frame)
        s.d.ellipse([wx + 1, 139, wx + 9, 147], fill=win)
        s.d.line([(wx + 5, 139), (wx + 5, 147)], fill=frame)
        s.d.line([(wx + 1, 143), (wx + 9, 143)], fill=frame)
        if s.dark:
            s.halo(wx + 5, 143, 10, s.glow("#e0a640", 0.3), 0.35)
    if s.dark:
        s.halo(73, 148, 16, s.glow("#e0a640", 0.3), 0.3)
    path = s.c("#b8a070", 0.38)
    for i in range(30):
        t = i / 29
        x = 73 + math.sin(t * 3) * 18 * t
        y = 159 + t * 22
        s.d.line([(x - 2 - t * 5, y), (x + 2 + t * 5, y)], fill=path)
    for fx in range(20, 130, 5):
        s.d.line([(fx, 162), (fx, 167)], fill=frame)
    s.d.line([(20, 163), (60, 163)], fill=frame)
    s.d.line([(88, 163), (128, 163)], fill=frame)
    for _ in range(40):
        x, y = s.rnd.randrange(12, 140), s.rnd.randrange(158, 172)
        s.px(x, y, s.glow(s.rnd.choice(["#c0563a", "#e0a640", "#8f5a8f", "#f4ead8"]), 0.6 if not s.dark else 0.35))
    rh = s.c(green, 0.26)
    s.d.ellipse([200, 118, 360, 220], fill=rh)
    s.grass(124, 170, dk(rh, 0.15), 120)
    s.d.ellipse([292, 136, 302, 146], fill=frame)
    s.d.ellipse([293, 137, 301, 145], fill=s.glow("#e0a640", 0.7) if s.dark else s.c("#3d5f8a", 0.5))
    s.d.rectangle([291, 142, 303, 150], fill=rh)
    s.d.rectangle([293, 141, 301, 149], fill=s.glow("#e0a640", 0.7) if s.dark else s.c("#3d5f8a", 0.5))
    bark = s.c("#5a4a32", 0.5)
    s.d.rectangle([248, 86, 253, 124], fill=bark)
    for bx, by, ex, ey in ((250, 100, 236, 88), (251, 96, 266, 84), (250, 92, 250, 74)):
        s.d.line([(bx, by), (ex, ey)], fill=bark, width=2)
    leaf = s.c(green, 0.36)
    for dx, dy, r in ((-14, -32, 11), (14, -34, 11), (0, -46, 12), (-20, -18, 9), (20, -20, 9), (0, -26, 13)):
        s.blob(250 + dx, 120 + dy, r, leaf)
    if s.dark:
        for i in range(14):
            x = 228 + i * 3.4
            y = 108 + int(4 * math.sin(i / 13 * math.pi))
            s.px(x, y, s.glow(["#e0a640", "#d9502e", "#8fa05a"][i % 3], 0.85))
    s.ridge(172, [(2, 0.03)], s.c(green, 0.34))
    s.grass(172, 180, dk(s.c(green, 0.34), 0.15), 60)


def rivendell(s):
    s.sky("#6a90a8", 0.16, moon=(160, 22, 5))
    s.ridge(96, [(14, 0.03), (6, 0.08)], s.c("#6a7a8a", 0.10), jag=1.2, rim=s.c("#6a7a8a", 0.05))
    s.ridge(112, [(10, 0.04), (4, 0.1)], s.c("#4a6a6a", 0.16), jag=1.2)
    s.mist(108, 126, lt(s.bg, 0.3) if not s.dark else mix(s.bg, (180, 190, 200), 0.2), 0.45)
    for x in range(60, 260, 9):
        s.pine(x, 128 + (x % 5), 12 + x % 7, s.c("#3d5a3a", 0.26))
    rock = s.c("#5a6470", 0.30)
    for side in (0, 1):
        pts = [(0, 10), (26, 18), (46, 40), (60, 70), (72, 110), (84, 180), (0, 180)]
        if side:
            pts = [(W - x, y) for x, y in pts]
        s.d.polygon(pts, fill=rock)
        for _ in range(260):
            y = s.rnd.randrange(12, 180)
            x = s.rnd.randrange(0, 84)
            x = W - x if side else x
            if s.get(x, y) == rock:
                s.px(x, y, dk(rock, 0.12) if s.rnd.random() < 0.7 else lt(rock, 0.12))
        for ly in (48, 82, 120):
            lx = 22 if not side else W - 40
            s.d.line([(lx, ly), (lx + 18, ly)], fill=lt(rock, 0.2))
            s.pine(lx + 6, ly, 10, s.c("#3d5a3a", 0.34))
    fall = s.glow("#d8e8f0", 0.75 if not s.dark else 0.5)
    for fx, top in ((54, 46), (60, 58), (268, 40), (262, 70)):
        for y in range(top, 160):
            for k in range(3):
                if (y * 3 + k * 5 + fx) % 9 > 2:
                    s.px(fx + k, y, fall if k != 2 else lt(rock, 0.3))
        s.halo(fx + 1, 160, 9, fall, 0.6)
    stone = s.c("#c8b898", 0.48) if not s.dark else s.c("#c8b898", 0.32)
    roof = s.c("#3d6f7a", 0.42)
    win = s.glow("#e0c070", 0.8) if s.dark else s.c("#3d6f7a", 0.5)
    s.d.rectangle([104, 134, 220, 140], fill=dk(stone, 0.12))
    for bx, by, bw, bh in ((110, 112, 40, 22), (152, 104, 50, 30), (204, 118, 26, 16)):
        s.d.rectangle([bx, by, bx + bw, by + bh], fill=stone)
        s.d.line([(bx + bw, by), (bx + bw, by + bh)], fill=dk(stone, 0.15))
        s.d.polygon([(bx - 4, by), (bx + bw // 2, by - 10), (bx + bw + 4, by)], fill=roof)
        s.d.line([(bx - 4, by), (bx + bw // 2, by - 10)], fill=lt(roof, 0.25))
        for wx in range(bx + 4, bx + bw - 3, 7):
            s.d.rectangle([wx, by + 6, wx + 3, by + bh - 5], fill=win)
            s.d.ellipse([wx, by + 4, wx + 3, by + 8], fill=win)
        s.d.line([(bx, by + bh - 2), (bx + bw, by + bh - 2)], fill=lt(stone, 0.25))
    s.d.rectangle([176, 70, 186, 104], fill=stone)
    s.d.line([(186, 70), (186, 104)], fill=dk(stone, 0.15))
    s.d.polygon([(173, 70), (181, 52), (189, 70)], fill=roof)
    s.d.rectangle([179, 78, 182, 86], fill=win)
    for col in range(114, 150, 6):
        s.d.line([(col, 134), (col, 140)], fill=lt(stone, 0.2))
    for tx, ty, r in ((96, 140, 8), (100, 128, 6), (232, 138, 8), (240, 128, 6), (140, 146, 5)):
        s.blob(tx, ty, r, s.c("#c87a30", 0.40) if not s.dark else s.c("#c87a30", 0.32))
    water = s.c("#3d6f8a", 0.30)
    s.d.rectangle([0, 158, W, H], fill=water)
    for _ in range(70):
        x, y = s.rnd.randrange(W), s.rnd.randrange(160, 180)
        s.d.line([(x, y), (x + s.rnd.randrange(2, 7), y)], fill=lt(water, 0.3))
    s.d.arc([134, 146, 186, 176], 180, 360, fill=stone, width=3)
    s.d.line([(134, 160), (186, 160)], fill=stone)
    if s.dark:
        for lx, ly in ((118, 130), (206, 130), (160, 98), (226, 132)):
            s.halo(lx, ly, 7, s.glow("#e0c070", 0.35), 0.4)


def gondor(s):
    s.sky("#8aa0b8", 0.16, moon=(60, 24, 5))
    if not s.dark:
        s.clouds(30, 34, 50, lt(s.bg, 0.5))
    tops = s.ridge(104, [(16, 0.025), (6, 0.07)], s.c("#6a7480", 0.12), jag=1.2)
    for bx in (24, 62, 100):
        by = tops[bx]
        s.d.rectangle([bx - 1, by - 3, bx + 1, by], fill=s.glow("#f0663a", 0.85 if s.dark else 0.6))
        s.smoke(bx, by - 5, 7, s.c("#6e6058", 0.25))
        if s.dark:
            s.halo(bx, by - 1, 6, s.glow("#f0663a", 0.4), 0.5)
    mtn = s.c("#5a6470", 0.22)
    s.d.polygon([(140, 160), (230, 36), (250, 30), (276, 44), (320, 70), (320, 160)], fill=mtn)
    s.d.polygon([(230, 36), (250, 30), (276, 44), (262, 50), (246, 42), (236, 52)], fill=lt(mtn, 0.55))
    for _ in range(200):
        x, y = s.rnd.randrange(150, 320), s.rnd.randrange(40, 160)
        if s.get(x, y) == mtn:
            s.px(x, y, dk(mtn, 0.1))
    s.ridge(150, [(2, 0.02)], s.c("#7a8a5a", 0.22))
    for fx in range(0, W, 22):
        s.d.line([(fx, 152), (fx - 10, 180)], fill=s.c("#7a8a5a", 0.3))
    s.d.line([(0, 160), (W, 156)], fill=s.c("#8a8f98", 0.35))
    stone = s.c("#d8dce0", 0.55) if not s.dark else s.c("#d8dce0", 0.34)
    wall = dk(stone, 0.12)
    cx = 224
    for i in range(7):
        y0 = 158 - i * 12
        half = 74 - i * 9
        s.d.rectangle([cx - half, y0 - 12, cx + half, y0], fill=stone)
        s.d.rectangle([cx - half, y0 - 3, cx + half, y0], fill=wall)
        for bx in range(cx - half, cx + half, 3):
            s.px(bx, y0 - 13, stone)
        for _ in range(half // 3):
            hx = s.rnd.randrange(cx - half + 2, cx + half - 4)
            s.d.rectangle([hx, y0 - 9, hx + 3, y0 - 5], fill=lt(stone, 0.2))
            s.px(hx + 1, y0 - 7, s.glow("#e0a640", 0.8) if s.dark else dk(stone, 0.3))
    s.d.polygon([(206, 158), (224, 70), (242, 158)], fill=mix(stone, s.c("#8a8f98", 0.5), 0.45))
    s.d.line([(224, 70), (206, 158)], fill=lt(stone, 0.2))
    s.d.rectangle([219, 152, 229, 158], fill=dk(stone, 0.5))
    s.d.rectangle([220, 26, 228, 76], fill=lt(stone, 0.15))
    s.d.line([(228, 26), (228, 76)], fill=dk(stone, 0.15))
    s.d.polygon([(219, 26), (224, 14), (229, 26)], fill=stone)
    s.d.line([(224, 14), (224, 6)], fill=dk(stone, 0.3))
    s.d.rectangle([225, 6, 231, 9], fill=s.c("#3a3a3a", 0.5))
    for wy in range(32, 72, 8):
        s.px(224, wy, s.glow("#e0a640", 0.8) if s.dark else dk(stone, 0.3))
    s.d.line([(208, 76), (208, 70)], fill=s.c("#5a4a32", 0.5))
    s.blob(208, 68, 3, lt(stone, 0.3))
    s.d.line([(0, 170), (220, 158)], fill=s.c("#b8a888", 0.35))


def rohan(s):
    s.sky("#90a8c0", 0.16, moon=(262, 24, 7))
    if not s.dark:
        s.clouds(200, 24, 60, lt(s.bg, 0.5))
        s.clouds(30, 40, 30, lt(s.bg, 0.5))
    mt = s.c("#6a7a8a", 0.18)
    tops = s.ridge(86, [(18, 0.022), (7, 0.07)], mt, jag=1.6)
    snow = s.glow("#ffffff", 0.7) if not s.dark else s.glow("#e8e0d0", 0.35)
    for x, y in tops.items():
        if y < 84:
            depth = (84 - y) // 2 + 1
            for k in range(depth):
                if k < depth - 2 or dith(x, y + k, 0.5):
                    s.px(x, y + k, snow)
        if x % 9 == 0:
            s.d.line([(x, y + 4), (x + 6, y + 20)], fill=dk(mt, 0.1))
    s.ridge(110, [(6, 0.03), (3, 0.08)], s.c("#6a7a5a", 0.20), rim=s.c("#6a7a5a", 0.12))
    gold = s.c("#b08a20", 0.24)
    s.ridge(128, [(2, 0.012)], gold)
    hill = s.c("#7a8a40", 0.32)
    s.d.ellipse([36, 104, 164, 176], fill=hill)
    s.d.arc([36, 104, 164, 176], 200, 300, fill=lt(hill, 0.25))
    s.grass(110, 150, dk(hill, 0.15), 120)
    wood = s.c("#5a4a32", 0.5)
    for px_ in range(44, 158, 3):
        dy = int(18 * math.sqrt(max(0, 1 - ((px_ - 100) / 62) ** 2)))
        s.d.line([(px_, 140 - dy + 8), (px_, 140 - dy + 13)], fill=wood)
    thatch = s.glow("#c8a040", 0.55 if not s.dark else 0.42)
    for hx, hy in ((60, 128), (76, 120), (126, 122), (140, 130), (110, 134), (52, 136)):
        s.d.rectangle([hx, hy, hx + 9, hy + 5], fill=s.c("#8a7a5c", 0.45))
        s.d.polygon([(hx - 2, hy), (hx + 4, hy - 5), (hx + 11, hy)], fill=thatch)
        s.px(hx + 4, hy + 2, s.glow("#e0a640", 0.85) if s.dark else dk(wood, 0.2))
    s.d.rectangle([84, 98, 120, 110], fill=wood)
    s.d.polygon([(80, 100), (102, 86), (124, 100)], fill=s.glow("#e0b040", 0.85 if s.dark else 0.7))
    s.d.line([(80, 100), (102, 86)], fill=lt(s.glow("#e0b040", 0.7), 0.4))
    s.d.line([(80, 98), (76, 94)], fill=thatch)
    s.d.line([(124, 98), (128, 94)], fill=thatch)
    for wx in range(88, 118, 6):
        s.d.line([(wx, 101), (wx, 108)], fill=s.glow("#e0a640", 0.9) if s.dark else dk(wood, 0.25))
    for k in range(6):
        s.d.line([(98 + k, 110 + k * 2), (106 - k, 110 + k * 2)], fill=s.c("#b8a888", 0.4))
    s.d.line([(122, 98), (122, 84)], fill=wood)
    s.d.rectangle([123, 84, 130, 88], fill=s.glow("#4e7a32", 0.7))
    s.px(126, 86, s.glow("#f4ead8", 0.9))
    if s.dark:
        s.halo(102, 104, 14, s.glow("#e0a640", 0.3), 0.3)
    road = s.c("#b8a070", 0.36)
    pts = [(100, 150), (130, 156), (190, 160), (250, 168), (330, 176)]
    s.d.line(pts, fill=road, width=3)
    for mx in (168, 186, 204):
        s.d.ellipse([mx - 6, 146, mx + 6, 156], fill=s.c("#7a8a40", 0.36))
        for _ in range(6):
            s.px(mx + s.rnd.randrange(-4, 5), 148 + s.rnd.randrange(0, 4), s.glow("#f4ead8", 0.75))
    grass = s.c("#b08a20", 0.38)
    for _ in range(260):
        x, y = s.rnd.randrange(W), s.rnd.randrange(150, 180)
        s.d.line([(x, y), (x + 2, y - 3)], fill=grass if s.rnd.random() < 0.7 else lt(grass, 0.25))
    horse = s.c("#3a2a22", 0.55)
    for hx, hy in ((240, 150), (256, 152), (272, 149)):
        s.d.rectangle([hx, hy, hx + 7, hy + 3], fill=horse)
        s.d.line([(hx + 7, hy), (hx + 10, hy - 3)], fill=horse, width=2)
        for lx in (hx, hx + 2, hx + 5, hx + 7):
            s.d.line([(lx, hy + 3), (lx + (1 if lx % 2 else -1), hy + 6)], fill=horse)
        s.d.line([(hx + 3, hy - 1), (hx + 3, hy - 4)], fill=horse)
        s.d.line([(hx, hy + 1), (hx - 3, hy + 3)], fill=horse)


def lorien(s):
    s.sky("#c8b060", 0.14, stars=False)
    if s.dark:
        s.vgrad(0, 0, W, H, mix(s.bg, (10, 14, 18), 0.4), s.bg)
    far = s.c("#c0c8c8", 0.16) if not s.dark else s.c("#d0dce0", 0.10)
    for x in range(4, W, 23):
        s.d.rectangle([x, 0, x + 3, H], fill=far)
    s.mist(100, 150, lt(s.bg, 0.35) if not s.dark else mix(s.bg, (160, 180, 200), 0.18), 0.5)
    mid = s.c("#c0c8c8", 0.28) if not s.dark else s.c("#d0dce0", 0.18)
    for x in (44, 104, 176, 228, 284):
        s.d.rectangle([x, 0, x + 6, H], fill=mid)
        s.d.line([(x + 6, 0), (x + 6, H)], fill=dk(mid, 0.12))
    for _ in range(60):
        cx, cy, r = s.rnd.randrange(-10, W + 10), s.rnd.randrange(-6, 30), s.rnd.randrange(10, 22)
        col = s.c("#c8a030", s.rnd.choice([0.26, 0.32, 0.38, 0.44]))
        s.d.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2], fill=col)
        for _ in range(r):
            s.px(cx + s.rnd.randrange(-r, r), cy + s.rnd.randrange(-r // 2, r // 2), lt(col, 0.3))
    for _ in range(30):
        x = s.rnd.randrange(W)
        y = s.rnd.randrange(14, 34)
        s.d.line([(x, y), (x, y + s.rnd.randrange(4, 12))], fill=s.c("#c8a030", 0.4))
    trunk = s.c("#c8d0d0", 0.48) if not s.dark else s.c("#d8e4e8", 0.30)
    for x, w in ((6, 20), (130, 14), (252, 22)):
        s.d.rectangle([x, 20, x + w, H], fill=trunk)
        s.d.line([(x, 20), (x, H)], fill=lt(trunk, 0.4))
        s.d.rectangle([x + w - 3, 20, x + w, H], fill=dk(trunk, 0.12))
        for _ in range(70):
            bx, by = s.rnd.randrange(x + 2, x + w - 3), s.rnd.randrange(24, H)
            s.d.line([(bx, by), (bx, by + 3)], fill=dk(trunk, 0.08))
        for root in (-1, 1):
            rx = x if root < 0 else x + w
            s.d.polygon([(rx, H - 16), (rx + root * 8, H), (rx, H)], fill=trunk)
        fy = 60 + (x * 7) % 40
        plank = s.c("#8a7a5c", 0.5)
        s.d.rectangle([x - 16, fy, x + w + 16, fy + 2], fill=plank)
        s.d.line([(x - 16, fy + 3), (x + w + 16, fy + 3)], fill=dk(plank, 0.2))
        for rx in range(x - 16, x + w + 17, 4):
            s.d.line([(rx, fy - 4), (rx, fy)], fill=plank)
        s.d.line([(x - 16, fy - 4), (x + w + 16, fy - 4)], fill=plank)
        for ly in range(fy + 3, H - 10, 3):
            s.px(x + w + 12, ly, plank)
        lamp = s.glow("#e8f0ff", 0.9) if s.dark else s.c("#c8a030", 0.6)
        for lx in (x - 12, x + w + 8):
            s.d.line([(lx, fy + 3), (lx, fy + 6)], fill=plank)
            s.d.rectangle([lx - 1, fy + 6, lx + 1, fy + 8], fill=lamp)
            if s.dark:
                s.halo(lx, fy + 7, 8, s.glow("#c8dcff", 0.4), 0.5)
    for _ in range(70):
        x, y = s.rnd.randrange(W), s.rnd.randrange(36, 160)
        s.px(x, y, s.glow("#e0b030", 0.75) if not s.dark else s.glow("#c8dcff", s.rnd.choice([0.4, 0.7])))
        if s.rnd.random() < 0.4:
            s.px(x + 1, y + 1, s.glow("#e0b030", 0.6) if not s.dark else s.glow("#c8dcff", 0.3))
    ground = s.c("#c8a030", 0.34)
    s.ridge(164, [(3, 0.04)], ground)
    for _ in range(140):
        x, y = s.rnd.randrange(W), s.rnd.randrange(166, 180)
        s.px(x, y, s.c("#c8a030", s.rnd.choice([0.25, 0.45, 0.55])))
    for fx in range(30, W, 41):
        for k in range(-3, 4):
            s.d.line([(fx, 168), (fx + k * 3, 160 + abs(k))], fill=s.c("#5a7a3a", 0.4))
    for _ in range(18):
        x, y = s.rnd.randrange(W), s.rnd.randrange(166, 178)
        col = s.glow(s.rnd.choice(["#f4ead8", "#f5c255"]), 0.8)
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            s.px(x + dx, y + dy, col if (dx, dy) != (0, 0) else s.glow("#e0a640", 0.9))


def moria(s):
    s.sky("#7a8a9a", 0.14, moon=(46, 18, 7))
    rock = s.c("#6e6a66", 0.34 if not s.dark else 0.16)
    tops = s.ridge(34, [(5, 0.03), (4, 0.09)], rock, jag=1.6, rim=lt(rock, 0.2))
    for _ in range(500):
        x, y = s.rnd.randrange(W), s.rnd.randrange(40, 140)
        if y > tops[x] + 2:
            s.px(x, y, dk(rock, 0.1) if s.rnd.random() < 0.6 else lt(rock, 0.08))
    for _ in range(14):
        x, y = s.rnd.randrange(W), s.rnd.randrange(50, 130)
        for k in range(s.rnd.randrange(6, 18)):
            x += s.rnd.choice((-1, 0, 1))
            s.px(x, y + k, dk(rock, 0.25))
    for sy in (70, 100, 124):
        s.d.line([(0, sy), (W, sy + 4)], fill=dk(rock, 0.06))
    glow = s.dark
    line = s.glow("#d8e4f4", 0.65) if glow else s.c("#6e6a66", 0.62)
    soft = s.glow("#c8d8f0", 0.35) if glow else None
    ax, top, base, half = 196, 58, 136, 34
    s.d.rectangle([ax - half - 4, top + half, ax - half - 1, base], fill=dk(rock, 0.15))
    s.d.rectangle([ax + half + 1, top + half, ax + half + 4, base], fill=dk(rock, 0.15))
    s.d.arc([ax - half, top, ax + half, top + 2 * half], 180, 360, fill=line)
    s.d.arc([ax - half + 3, top + 3, ax + half - 3, top + 2 * half - 3], 180, 360, fill=line)
    for i in range(0, 180, 9):
        a = math.radians(180 + i)
        s.px(ax + (half - 1.5) * math.cos(a), top + half + (half - 1.5) * math.sin(a), line)
    for side in (-1, 1):
        x = ax + side * half
        s.d.line([(x, top + half), (x, base)], fill=line)
        s.d.line([(x - side * 3, top + half), (x - side * 3, base)], fill=line)
        s.d.rectangle([x - side * 3 - 1 if side > 0 else x, top + half - 2, x if side > 0 else x + 3, top + half], fill=line)
    s.d.line([(ax, top + half + 6), (ax, base)], fill=line)
    for side in (-1, 1):
        tx = ax + side * 20
        s.d.line([(tx, base), (tx, top + 40)], fill=line)
        for k in range(5):
            y = top + 44 + k * 7
            s.d.line([(tx, y), (tx + side * (8 - k), y - 4)], fill=line)
            s.d.line([(tx, y + 2), (tx - side * 3, y - 1)], fill=line)
        s.px(tx, top + 38, line)
    sx, sy = ax, top + 44
    for a in range(0, 360, 45):
        r = 6 if a % 90 == 0 else 4
        s.d.line([(sx, sy), (sx + round(r * math.cos(math.radians(a))), sy + round(r * math.sin(math.radians(a))))], fill=line)
    s.d.polygon([(ax - 5, top + 20), (ax - 3, top + 14), (ax, top + 18), (ax + 3, top + 14), (ax + 5, top + 20)], outline=line)
    for i in range(7):
        a = math.radians(200 + i * 23)
        s.px(ax + 22 * math.cos(a), top + 34 + 22 * math.sin(a), line)
    s.d.rectangle([ax - 3, base - 12, ax + 3, base - 10], outline=line)
    s.d.line([(ax, base - 10), (ax, base - 6)], fill=line)
    if glow:
        s.halo(ax, top + 44, 30, soft, 0.18)
    holly = s.c("#2f5a3a", 0.42)
    for hx in (ax - half - 22, ax + half + 22):
        s.d.rectangle([hx - 1, 112, hx + 1, 138], fill=s.c("#5a4a32", 0.5))
        for dx, dy, r in ((0, -40, 8), (-6, -32, 7), (6, -30, 7), (0, -24, 8)):
            s.blob(hx + dx, 138 + dy, r, holly)
        for _ in range(10):
            s.px(hx + s.rnd.randrange(-9, 10), 102 + s.rnd.randrange(0, 18), s.glow("#c0302a", 0.7 if not s.dark else 0.5))
    step = s.c("#8a8680", 0.40)
    for k in range(4):
        s.d.rectangle([ax - 22 - k * 4, base + k * 2, ax + 22 + k * 4, base + k * 2 + 1], fill=step if k % 2 == 0 else dk(step, 0.1))
    s.d.rectangle([0, 142, W, 146], fill=s.c("#6e6a66", 0.42))
    for bx in (20, 60, 270, 300, 120):
        s.blob(bx, 143, 4, s.c("#8a8680", 0.42))
    water = s.c("#2f4a6a", 0.30) if not s.dark else s.c("#1a2a40", 0.6)
    s.d.rectangle([0, 147, W, H], fill=water)
    for y in range(148, H, 2):
        for x in range(ax - half, ax + half + 1):
            sy_ = 147 - (y - 147) * 3
            if 0 <= sy_ < H and s.get(x, top + (147 - y) * -1 + 60) == line and dith(x, y, 0.5):
                s.px(x, y, mix(water, line, 0.4))
    for _ in range(80):
        x, y = s.rnd.randrange(W), s.rnd.randrange(150, 180)
        s.d.line([(x, y), (x + s.rnd.randrange(3, 10), y)], fill=lt(water, 0.15))
    if s.dark:
        s.d.line([(40, 152), (54, 152)], fill=mix(water, (244, 236, 216), 0.4))
        s.d.line([(43, 156), (51, 156)], fill=mix(water, (244, 236, 216), 0.3))
        tent = s.c("#3a4a3a", 0.6)
        pts = [(282, 180), (284, 170), (288, 162), (292, 158), (295, 160)]
        s.d.line(pts, fill=tent, width=3)
        s.d.line([(295, 160), (297, 163)], fill=tent, width=2)


def mordor(s):
    if s.dark:
        s.vgrad(0, 0, W, 150, mix(s.bg, (10, 6, 6), 0.5), mix(s.bg, (120, 40, 20), 0.35), 12)
    else:
        s.vgrad(0, 0, W, 150, s.c("#a08070", 0.22), s.c("#d07a4a", 0.18), 12)
    ash = s.c("#6e6058", 0.22) if not s.dark else mix(s.bg, (60, 40, 36), 0.6)
    for cy in (18, 34, 52):
        for x in range(-20, W, 26):
            r = s.rnd.randrange(10, 18)
            s.d.ellipse([x, cy - r // 3, x + r * 2, cy + r // 3], fill=ash)
        for x in range(0, W):
            if dith(x, cy + 6, 0.4):
                s.px(x, cy + 6, ash)
    s.ridge(108, [(10, 0.05), (6, 0.13)], s.c("#3a2a22", 0.20) if not s.dark else mix(s.bg, (20, 12, 10), 0.4), jag=3)
    cone = s.c("#3a2a22", 0.40) if not s.dark else mix(s.bg, (14, 8, 6), 0.55)
    lit = s.c("#8a3a1a", 0.45) if not s.dark else mix(cone, rgb("#d9502e"), 0.25)
    s.d.polygon([(150, 152), (216, 60), (240, 60), (316, 152)], fill=cone)
    s.d.polygon([(216, 60), (228, 60), (198, 152), (150, 152)], fill=lit)
    for _ in range(220):
        x, y = s.rnd.randrange(150, 316), s.rnd.randrange(62, 152)
        if s.get(x, y) in (cone, lit):
            s.px(x, y, dk(s.get(x, y), 0.15))
    lava = s.glow("#f0663a", 0.9 if s.dark else 0.7)
    hot = s.glow("#f5c255", 0.9 if s.dark else 0.75)
    s.d.rectangle([216, 58, 240, 61], fill=lava)
    s.d.line([(220, 58), (236, 58)], fill=hot)
    s.halo(228, 54, 18, s.glow("#f0663a", 0.4), 0.45)
    for pts in ([(222, 62), (218, 80), (224, 96), (212, 118), (216, 150)], [(234, 62), (240, 84), (236, 104), (248, 130), (252, 150)]):
        s.d.line(pts, fill=lava, width=2)
        s.d.line(pts, fill=hot)
    road = s.c("#6e6058", 0.4) if not s.dark else mix(s.bg, (90, 70, 60), 0.4)
    for i in range(60):
        t = i / 59
        x = 228 + math.cos(t * 9) * (12 + t * 60)
        y = 66 + t * 84
        if i % 2:
            s.px(x, y, road)
    s.d.rectangle([258, 98, 262, 102], fill=lava)
    s.smoke(230, 46, 16, s.c("#5a4a40", 0.35) if not s.dark else mix(s.bg, (70, 56, 50), 0.5), drift=2)
    tower = s.c("#2a1e1a", 0.48) if not s.dark else mix(s.bg, (6, 4, 4), 0.75)
    edge = lt(tower, 0.12)
    s.d.polygon([(30, 156), (46, 110), (52, 60), (58, 40), (90, 40), (96, 60), (102, 110), (118, 156)], fill=tower)
    s.d.polygon([(20, 156), (36, 120), (46, 120), (40, 156)], fill=tower)
    s.d.polygon([(128, 156), (112, 120), (102, 120), (108, 156)], fill=tower)
    for yy in (60, 84, 110):
        s.d.line([(50, yy), (98, yy)], fill=edge)
    for sx_ in (52, 62, 72, 86, 96):
        s.d.polygon([(sx_ - 2, 40), (sx_, 30 + (sx_ % 3) * 2), (sx_ + 2, 40)], fill=tower)
    s.d.polygon([(56, 40), (60, 14), (66, 40)], fill=tower)
    s.d.polygon([(82, 40), (88, 14), (92, 40)], fill=tower)
    for _ in range(16):
        s.px(s.rnd.randrange(52, 96), s.rnd.randrange(50, 150), s.glow("#d9502e", 0.75))
    eye = s.glow("#f07a3a", 0.95 if s.dark else 0.75)
    s.halo(74, 26, 18, s.glow("#f07a3a", 0.5), 0.55)
    s.d.ellipse([64, 21, 84, 31], fill=eye)
    s.d.ellipse([68, 23, 80, 29], fill=s.glow("#f5c255", 0.95 if s.dark else 0.8))
    s.d.rectangle([73, 21, 75, 31], fill=s.glow("#140804", 0.9))
    s.ridge(154, [(6, 0.06), (4, 0.15)], s.c("#2a1e1a", 0.36) if not s.dark else mix(s.bg, (8, 4, 4), 0.6), jag=3)
    for _ in range(12):
        x, y = s.rnd.randrange(W), s.rnd.randrange(160, 178)
        for k in range(s.rnd.randrange(4, 12)):
            s.px(x + k, y + s.rnd.choice((-1, 0, 1)), s.glow("#e0662e", 0.55 if s.dark else 0.45))
    for fx, fy in ((140, 166), (176, 172), (290, 168)):
        s.d.rectangle([fx, fy, fx + 1, fy + 1], fill=s.glow("#f5c255", 0.9))
        if s.dark:
            s.halo(fx, fy, 5, s.glow("#f0663a", 0.45), 0.5)
    for _ in range(80):
        s.px(s.rnd.randrange(W), s.rnd.randrange(60, 180), s.glow("#e0662e", 0.45) if s.dark else s.c("#6e6058", 0.4))


REALMS = [("Shire", shire), ("Rivendell", rivendell), ("Gondor", gondor), ("Rohan", rohan), ("Lorien", lorien), ("Moria", moria), ("Mordor", mordor)]


def render(fn, dark, seed):
    s = Scene(dark, seed)
    fn(s)
    return s.img.resize((W * SCALE, H * SCALE), Image.NEAREST)


for name, fn in REALMS:
    for appearance in ("light", "dark"):
        folder = os.path.join(OUT, appearance)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"{name.lower()}.png")
        render(fn, appearance == "dark", sum(map(ord, name))).save(path, optimize=True)
        print("wrote", os.path.relpath(path))
