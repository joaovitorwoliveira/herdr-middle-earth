import os
import sys

# Writes into the repo next to this script, never into a live Herdr home.
HOME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mods")
SIZE = 16

SKIN = {"s": "#f1c9a0", "k": "#1b1b1b"}
HOBBIT = [
    "................",
    "................",
    "................",
    ".....hhhhhh.....",
    "....hhhhhhhh....",
    "....hssssssh....",
    "....hskssksh....",
    ".....ssssss.....",
    "....CCLLLLCC....",
    "...CCcLyLLcCC...",
    "...CCcVLLVcCC...",
    "...CccVVVVccC...",
    "....CcPPPPcC....",
    ".....cPPPPc.....",
    ".....PP..PP.....",
    "....ssh..hss....",
]


def hobbit(hair, cloak, cloak_dark, vest, ring=False):
    rows = HOBBIT if ring else [r.replace("y", "L") for r in HOBBIT]
    return rows, {**SKIN, "h": hair, "C": cloak, "c": cloak_dark, "V": vest,
                  "L": "#e8e2d0", "y": "#f2c230", "P": "#6b5235"}


SPRITES = {
    "gandalf": ([
        "......G.........",
        ".....GG.........",
        ".....GGG........",
        "....GGGG........",
        "....GGGGG....o..",
        "..GGGGGGGGGG.T..",
        "....ssssss...T..",
        "....skssks...T..",
        "....WWWWWW...T..",
        "...gWWWWWWg..T..",
        "..ggWWWWWWgg.T..",
        "..gggWWWWggg.s..",
        "..GgggWWgggG.T..",
        "..GGggggggGG.T..",
        "...GGggggGG..T..",
        "...kk....kk..T..",
    ], {**SKIN, "G": "#8d8f96", "g": "#6b6d74", "W": "#ececec", "T": "#7a5230", "o": "#f3f0d8"}),
    "frodo": hobbit("#4a2e1a", "#4c6b3a", "#3a5530", "#8a6a3a", ring=True),
    "sam": ([
        "................",
        "................",
        "................",
        ".....hhhhhh.....",
        "....hhhhhhhh.pp.",
        "....hssssssh.pp.",
        "....hskssksh..b.",
        ".....rssssr..bb.",
        "....LLVLLVLLbbb.",
        "...LLVVLLVVLLbb.",
        "...sVVVVVVVVsbb.",
        "....VVVVVVVV.b..",
        "....PPPPPPPP....",
        ".....PPPPPP.....",
        ".....PP..PP.....",
        "....ssh..hss....",
    ], {**SKIN, "h": "#8a5a2b", "r": "#e39a8a", "p": "#8c8c8c", "b": "#6b4a2a",
        "L": "#e8e2d0", "V": "#b5652b", "P": "#6b5235"}),
    "legolas": ([
        "................",
        ".....YYYYYY.....",
        "....YYYYYYYY.B..",
        "....YssssssY..B.",
        "...sYskssksYs.qB",
        "....YssssssY..qB",
        "....YYssssYY..qB",
        "....YEEEEEEY..qB",
        "...YEEeEEeEEY.qB",
        "...EEEeEEeEEE.qB",
        "...sEEeEEeEEs.qB",
        "....EEEEEEEE..B.",
        "....eeeeeeee.B..",
        "....eee..eee....",
        "....nnn..nnn....",
        "....nnn..nnn....",
    ], {**SKIN, "Y": "#e8d27a", "E": "#5f8a3e", "e": "#46682c", "B": "#8a5a2b",
        "q": "#d8d8d8", "n": "#5a3d24"}),
    "gimli": ([
        "................",
        "................",
        ".....MMMMMM.....",
        "....MMMMMMMM....",
        "...mMMMMMMMMm...",
        "....ssssssss.AA.",
        "....skssssks.AAA",
        "...RRssssssRR.T.",
        "..RRRRRRRRRRRRT.",
        "..DRRRRRRRRRRsT.",
        "..DDRRRrRRRRDDT.",
        "..DDDRrRRrRDDDT.",
        "..DDDDrRRrDDDDT.",
        "..DDDDDDDDDDDD..",
        "...nnnn..nnnn...",
        "...nnnn..nnnn...",
    ], {**SKIN, "M": "#9a9a9a", "m": "#6e6e6e", "R": "#c4512a", "r": "#9a3a1c",
        "D": "#6b3a2a", "A": "#c9c9c9", "T": "#7a5230", "n": "#4a3020"}),
    "sauron": ([
        "....S..SS..S....",
        "....SS.SS.SS....",
        "....HHHHHHHH....",
        "...HHHHHHHHHH.M.",
        "...HhhhhhhhhHMmM",
        "...HheehheehH.M.",
        "...HhhhhhhhhH.T.",
        "....HHhhhhHH..T.",
        "..PPPAAAAAAPPPT.",
        ".PPPPAAaaAAPPgT.",
        ".PP.AAAaaAAA.gT.",
        ".gg.AAAaaAAA..T.",
        "....CCCCCCCC..T.",
        "...CCCcCCcCCC...",
        "...CCCcCCcCCC...",
        "....AAA..AAA....",
    ], {"S": "#6a6a76", "H": "#45454f", "h": "#121216", "e": "#ff7a1a", "P": "#5a5a66",
        "A": "#3c3c46", "a": "#8a3a1e", "g": "#5a5a66", "C": "#2e2a30", "c": "#45454f",
        "M": "#6a6a76", "m": "#a0a0aa", "T": "#2a2a30"}),
}

def walk(rows):
    """Body up a pixel, legs and feet spread: the hobbits' second step."""
    return rows[1:14] + [rows[13], "....PP....PP....", "...ssh....hss..."]


def replace_rows(rows, changes):
    out = list(rows)
    for y, row in changes.items():
        out[y] = row
    return out


def second_frames():
    g_rows, g_pal = SPRITES["gandalf"]
    l_rows, l_pal = SPRITES["legolas"]
    gi_rows, gi_pal = SPRITES["gimli"]
    frames = {
        # Casting: sparks burst from the staff.
        "gandalf": (replace_rows(g_rows, {
            0: "......G......b..",
            1: ".....GG....b.o.b",
            2: ".....GGG....ooo.",
            3: "....GGGG...boOob",
            4: "....GGGGG...ooo.",
            5: "..GGGGGGGGGGbTb.",
        }), {**g_pal, "b": "#8fd0ff", "O": "#ffffff"}),
        # Drawing the bow, an arrow on the string.
        "legolas": (replace_rows(l_rows, {
            8: "...YEEeEEeEEYq.B",
            9: "...EEEeEEeEEsaaA",
            10: "...sEEeEEeEEsq.B",
        }), {**l_pal, "a": "#c9c9c9", "A": "#e8e8e8"}),
        # Axe raised overhead.
        "gimli": (replace_rows(gi_rows, {
            0: "................",
            1: "................",
            2: ".....MMMMMM..AA.",
            3: "....MMMMMMMM.AAA",
            4: "...mMMMMMMMMm.T.",
            5: "....ssssssss..T.",
            6: "....skssssks.sT.",
            7: "...RRssssssRR.T.",
            8: "..RRRRRRRRRRRR..",
            9: "..DRRRRRRRRRRD..",
            10: "..DDRRRrRRRRDD..",
            11: "..DDDRrRRrRDDD..",
            12: "..DDDDrRRrDDDD..",
        }), {**gi_pal}),
    }
    s_rows, s_pal = SPRITES["sauron"]
    # The Eye flares: flames on the crown, eyes white-hot, the mace burning.
    frames["sauron"] = (replace_rows(s_rows, {
        0: "...fSf.SS.fSf...",
        1: "....SSfSSfSS....",
        3: "...HHHHHHHHHHfMf",
        4: "...HhhhhhhhhHMFM",
        5: "...HhEEhhEEhH.M.",
    }), {**s_pal, "f": "#ff9a2a", "F": "#ffd04a", "E": "#ffe08a"})
    for hobbit_name in ("frodo", "sam"):
        rows, pal = SPRITES[hobbit_name]
        frames[hobbit_name] = (walk(rows), pal)
    return frames


EMBLEMS = {
    "shire": ([
        "................",
        ".....WWWWWW.....",
        "...WWWOOOOWWW...",
        "..WWOOOOOOOOWW..",
        "..WOOoOOOOoOOW..",
        ".WWOOoOOOOoOOWW.",
        ".WOOOoOOOOoOOOW.",
        ".WOOOoOyyOoOOOW.",
        ".WOOOoOyyOoOOOW.",
        ".WOOOoOOOOoOOOW.",
        ".WOOOoOOOOoOOOW.",
        ".WOOOoOOOOoOOOW.",
        ".WOOOoOOOOoOOOW.",
        "gWWWWWWWWWWWWWWg",
        "gggggggggggggggg",
        "................",
    ], {"W": "#7a5a3a", "O": "#3f7a3a", "o": "#2c5a28", "y": "#f2c230", "g": "#5aa04a"}),
    "rivendell": ([
        "................",
        "......aaaa......",
        "....aabbbbaa....",
        "...abbbbbbbba...",
        "..abbbbwwbbbba..",
        "..abbwwwwwwbba..",
        "..abbbwwwwbbba..",
        "..abbwwbbwwbba..",
        "..abbbbbbbbbba..",
        "..abbbbbbbbbba..",
        "..abccbbbbccba..",
        "..abccbbbbccba..",
        "..abccbbbbccba..",
        ".aaaaaaaaaaaaaa.",
        ".aaaaaaaaaaaaaa.",
        "................",
    ], {"a": "#c9a85a", "b": "#4a6aa0", "w": "#ffffff", "c": "#a8c8e8"}),
    "gondor": ([
        ".kkkkkkkkkkkkkk.",
        ".kkskkkkkkkkskk.",
        ".kkkkkkwwkkkkkk.",
        ".kkwkkwwwwkkwkk.",
        ".kkwwkkwwkkwwkk.",
        ".kkkwwkwwkwwkkk.",
        ".kwkkwwwwwwkkwk.",
        ".kkwwkkwwkkwwkk.",
        ".kkkwwwwwwwwkkk.",
        ".kkkkkkwwkkkkkk.",
        ".kkkkkkwwkkkkkk.",
        "..kkkkkwwkkkkk..",
        "..kkkkwwwwkkkk..",
        "...kkkkkkkkkk...",
        "....kkkkkkkk....",
        "......kkkk......",
    ], {"k": "#1c1c22", "w": "#f2f2f2", "s": "#c8cce0"}),
    "rohan": ([
        "yyyyyyyyyyyyyyyy",
        "yGGGGGGGGGGGGGGy",
        "yGGGGGwwGGGGGGGy",
        "yGGGGwwwwGGGGGGy",
        "yGGGwwwwwwGGGGGy",
        "yGGwwwkwwwwGGGGy",
        "yGwwwwwwwwwwGGGy",
        "yGwwwwGGwwwwwGGy",
        "yGGwwGGGGwwwwwGy",
        "yGGGGGGGGGwwwwGy",
        "yGGGGGGGGGwwwwGy",
        "yGGGGGGGGwwwwGGy",
        "yGGGGGGGwwwwGGGy",
        "yGGGGGGGGGGGGGGy",
        "yyyyyyyyyyyyyyyy",
        "................",
    ], {"y": "#d9b23a", "G": "#3f6a3a", "w": "#f2f2f2", "k": "#1b1b1b"}),
    "lorien": ([
        "........L.......",
        ".......LLL......",
        "......LLLLL.....",
        ".....LLLlLLL....",
        "....LLLLlLLLL...",
        "...LLlLLlLLlLL..",
        "...LLLlLlLlLLL..",
        "..LLLLLLlLLLLLL.",
        "..LLLLLlllLLLLL.",
        "...LLLLLlLLLLL..",
        "....LLLLlLLLL...",
        ".....LLLlLLL....",
        "......LLlLL.....",
        "........l.......",
        "........l.......",
        ".......l........",
    ], {"L": "#d9b23a", "l": "#a8862a"}),
    "moria": ([
        "................",
        ".....llllll.....",
        "...llddddddll...",
        "..lddddwwddddl..",
        "..ldddwwwwdddl..",
        ".lddddwwwwddddl.",
        ".ldddddwwdddddl.",
        ".ldldddddddddld.",
        ".ldldddlldddldl.",
        ".ldlddllllddldl.",
        ".ldldddlldddldl.",
        ".ldldddlldddldl.",
        ".ldldddlldddldl.",
        ".ldlddddddddldl.",
        ".llllllllllllll.",
        "................",
    ], {"d": "#3a3d45", "l": "#c8d0e0", "w": "#ffffff"}),
    "mordor": ([
        "................",
        "................",
        "................",
        "....ffffffff....",
        "..ffFFFFFFFFff..",
        ".fFFFyykkyyFFFf.",
        "fFFyyyykkyyyyFFf",
        "fFyyyyykkyyyyyFf",
        "fFyyyyykkyyyyyFf",
        "fFFyyyykkyyyyFFf",
        ".fFFFyykkyyFFFf.",
        "..ffFFFFFFFFff..",
        "....ffffffff....",
        "................",
        "................",
        "................",
    ], {"f": "#a8321a", "F": "#e0662e", "y": "#f5c242", "k": "#1b1b1b"}),
}


# Row of the eyes, the eye pixel, and the closed-lid color for the idle sprite.
EYES = {"gandalf": (7, "k", "#b07a52"), "frodo": (6, "k", "#b07a52"), "sam": (6, "k", "#b07a52"),
        "legolas": (4, "k", "#b07a52"), "gimli": (6, "k", "#b07a52"), "sauron": (5, "e", "#5a2414")}
# Drawn into the empty top-left corner; keys are chars no sprite palette uses.
BADGES = {
    "blocked": ([".!!.", ".!!.", ".!!.", "....", ".!!."], {"!": "#d9481f"}),
    "done": ([".@*.", "@..@", "@..@", ".@@."], {"@": "#d4a017", "*": "#fff4b0"}),
}


def asleep(name):
    rows, palette = SPRITES[name]
    y, eye, lid = EYES[name]
    assert eye in rows[y], f"{name} has no {eye!r} eyes on row {y}"
    return replace_rows(rows, {y: rows[y].replace(eye, "_")}), {**palette, "_": lid}


def badged(name, badge):
    rows, palette = SPRITES[name]
    mark, colors = BADGES[badge]
    out = list(rows)
    for y, line in enumerate(mark):
        for x, c in enumerate(line):
            if c == ".":
                continue
            assert out[y][x] == ".", f"{badge} badge covers {name} at {x},{y}"
            out[y] = out[y][:x] + c + out[y][x + 1:]
    return out, {**palette, **colors}


def svg(rows, palette):
    assert len(rows) == SIZE, f"{len(rows)} rows"
    rects = []
    for y, row in enumerate(rows):
        assert len(row) == SIZE, f"row {y} has {len(row)} cols: {row!r}"
        x = 0
        while x < SIZE:
            c = row[x]
            run = 1
            while x + run < SIZE and row[x + run] == c:
                run += 1
            if c != ".":
                rects.append(f'<rect x="{x}" y="{y}" width="{run}" height="1" fill="{palette[c]}"/>')
            x += run
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" '
            f'width="{SIZE}" height="{SIZE}" shape-rendering="crispEdges">' + "".join(rects) + "</svg>\n")


def write_all(table, folder):
    os.makedirs(folder, exist_ok=True)
    for name, (rows, palette) in table.items():
        with open(os.path.join(folder, f"{name}.svg"), "w") as f:
            f.write(svg(rows, palette))



# Gandalf rests with his pipe: ember on the bowl, a smoke ring rising up the left side.
GANDALF_SMOKE = {"r": "#9e978a", "w": "#b4ad9f", "e": "#e0662e", "E": "#ffb04a", "b": "#5a3a1e", "p": "#7a5230"}
GANDALF_IDLE = {
    "gandalf-idle": {
        2: ".r...GGG........",
        3: "r.r.GGGG........",
        4: ".r..GGGGG....o..",
        6: ".w..ssssss...T..",
        7: ".e..s_ss_s...T..",
        8: ".bppWWWWWW...T..",
        9: ".bsgWWWWWWg..T..",
    },
    "gandalf-idle-2": {
        0: ".r....G.........",
        1: "r.r..GG.........",
        2: ".r...GGG........",
        4: "w...GGGGG....o..",
        5: ".wGGGGGGGGGG.T..",
        7: ".E..s_ss_s...T..",
        8: ".bppWWWWWW...T..",
        9: ".bsgWWWWWWg..T..",
    },
}


def gandalf_idle():
    rows, palette = asleep("gandalf")
    return {name: (replace_rows(rows, changes), {**palette, **GANDALF_SMOKE}) for name, changes in GANDALF_IDLE.items()}


def put(rows, points):
    """Draws (x, y, char) points on empty pixels; char "." erases."""
    out = list(rows)
    for x, y, c in points:
        assert c == "." or out[y][x] == ".", f"pixel {x},{y} is taken by {out[y][x]!r}"
        out[y] = out[y][:x] + c + out[y][x + 1:]
    return out


def ring(cx, top, c="r"):
    return [(cx, top, c), (cx - 1, top + 1, c), (cx + 1, top + 1, c), (cx, top + 2, c)]


# Digit keys: no sprite palette uses them, so smoke never recolors a beard or a pack.
SMOKE = {"1": "#9e978a", "2": "#b4ad9f", "3": "#e0662e", "4": "#ffb04a", "5": "#5a3a1e", "6": "#7a5230"}


def smoker(name, pipe, ember, cx, wisps):
    """Two idle frames: the pipe lit, a smoke ring low then high."""
    rows, palette = asleep(name)
    pal = {**palette, **SMOKE}
    low = put(rows, pipe + [(*ember, "3")] + ring(cx, 2, "1"))
    high = put(rows, pipe + [(*ember, "4")] + ring(cx, 0, "1") + [(x, y, "2") for x, y in wisps])
    return {f"{name}-idle": (low, pal), f"{name}-idle-2": (high, pal)}


def animations():
    frames = dict(gandalf_idle())
    frames.update(smoker("frodo", [(13, 6, "5"), (13, 7, "5"), (11, 7, "6"), (12, 7, "6"), (13, 8, "s")], (13, 5), 13, [(14, 4)]))
    frames.update(smoker("sam", [(2, 6, "5"), (2, 7, "5"), (3, 7, "6"), (4, 7, "6"), (2, 8, "s")], (2, 5), 2, [(1, 4)]))
    frames.update(smoker("gimli", [(1, 7, "5"), (2, 7, "6"), (1, 8, "s")], (1, 6), 1, [(0, 4), (1, 5)]))

    # Legolas is an elf: no pipe, a lembas taken bite by bite.
    rows, pal = asleep("legolas")
    pal = {**pal, "L": "#eadbb0", "l": "#5f8a3e"}
    frames["legolas-idle"] = (put(rows, [(1, 8, "L"), (2, 8, "L"), (1, 9, "L"), (2, 9, "L"), (1, 10, "l"), (2, 10, "l")]), pal)
    frames["legolas-idle-2"] = (put(rows, [(3, 10, "."), (1, 5, "L"), (2, 5, "L"), (2, 6, "L"), (1, 7, "l"), (2, 7, "l"), (3, 6, "s"), (0, 9, "L")]), pal)

    # The Eye smoulders while Sauron waits.
    rows, pal = asleep("sauron")
    frames["sauron-idle"] = (rows, pal)
    frames["sauron-idle-2"] = (rows, {**pal, "_": "#a8401a"})

    # Battle: a wind-up frame and a strike frame.
    frames["gandalf-work"] = SPRITES["gandalf"]
    frames["gandalf-2"] = second_frames()["gandalf"]

    rows, pal = SPRITES["frodo"]
    sting = {**pal, "S": "#dfeeff", "G": "#6ab8ff", "g": "#c9a34a"}
    frames["frodo-work"] = (put(rows, [(13, y, "S") for y in range(2, 7)] + [(14, 3, "G"), (12, 5, "G"), (12, 7, "g"), (13, 7, "g"), (14, 7, "g"), (13, 8, "s")]), sting)
    frames["frodo-2"] = (put(rows, [(12, 8, "s"), (13, 7, "g"), (14, 6, "S"), (15, 5, "S"), (13, 2, "G"), (14, 2, "G"), (15, 3, "G"), (15, 4, "G")]), sting)

    rows, pal = SPRITES["sam"]
    rows = put(rows, [(13, 4, "."), (14, 4, "."), (13, 5, "."), (14, 5, ".")])
    pan = {**pal, "n": "#4a3020", "z": "#8aa0b8"}
    frames["sam-work"] = (put(rows, [(x, y, "p") for x in (12, 13, 14) for y in (0, 1)] + [(13, 2, "n"), (13, 3, "n"), (13, 4, "s")]), pan)
    frames["sam-2"] = (put(rows, [(12, 5, "s"), (13, 5, "n")] + [(x, y, "p") for x in (14, 15) for y in (3, 4, 5)] + [(12, 1, "z"), (13, 1, "z"), (14, 2, "z")]), pan)

    rows, pal = SPRITES["legolas"]
    frames["legolas-work"] = second_frames()["legolas"]
    frames["legolas-2"] = (put(rows, [(11, 1, "f"), (12, 1, "a"), (13, 1, "a"), (14, 1, "a"), (15, 1, "A")]), {**pal, "f": "#5f8a3e", "a": "#8a6a3a", "A": "#9aa0a8"})

    rows, pal = SPRITES["gimli"]
    frames["gimli-work"] = second_frames()["gimli"]
    swung = put(rows, [(13, 5, "."), (14, 5, "."), (13, 6, "."), (14, 6, "."), (15, 6, "."), (14, 7, "."), (14, 8, ".")])
    frames["gimli-2"] = (put(swung, [(15, 11, "A"), (15, 12, "A"), (14, 13, "A"), (15, 13, "A"), (13, 14, "w"), (15, 14, "w")]), {**pal, "w": "#f2c230"})

    rows, pal = SPRITES["sauron"]
    frames["sauron-work"] = second_frames()["sauron"]
    down = put(rows, [(14, 3, "."), (13, 4, "."), (14, 4, "."), (15, 4, "."), (14, 5, "."), (14, 6, "."), (14, 7, "."), (14, 8, ".")])
    down = replace_rows(down, {5: down[5].replace("e", "E")})
    frames["sauron-2"] = (put(down, [(15, 12, "M"), (14, 13, "M"), (15, 13, "F"), (15, 11, "f"), (13, 14, "f"), (15, 14, "f")]), {**pal, "E": "#ffe08a", "F": "#ffd04a", "f": "#ff9a2a"})
    return frames


def all_sprites():
    """Every agent sprite: base and second battle frame, then the animated poses, then the badges."""
    table = dict(SPRITES)
    table.update({f"{k}-2": v for k, v in second_frames().items()})
    table.update(animations())
    for name in SPRITES:
        for badge in BADGES:
            table[f"{name}-{badge}"] = badged(name, badge)
    return table


if __name__ == "__main__":
    sprites = all_sprites()
    write_all(sprites, os.path.join(HOME, "fellowship", "sprites"))
    write_all(EMBLEMS, os.path.join(HOME, "realms", "emblems"))
    print("ok", len(sprites), "sprites,", len(EMBLEMS), "emblems", file=sys.stderr)
