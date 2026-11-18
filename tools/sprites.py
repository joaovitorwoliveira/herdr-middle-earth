import os
import sys

# Writes into the repo next to this script, never into a live Herdr home.
HOME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mods")
# Agents are 24x24 grids, realm emblems 16x16. Each agent row is written as three 8-column chunks.
SIZE = 24
# Must match SPRITE_SIZE in fellowship/main.js. Herdr rasterizes an SVG from its width/height, so a
# 24pt sprite stretched to 36pt gets resampled and picks up faint lines from its neighbors at the edges.
AGENT_DISPLAY_SIZE = 36

OUT = "#2a1e18"
SKIN = {"o": OUT, "s": "#f2c9a0", "S": "#d9a07a", "k": "#1b1b1b", "m": "#a8604a", "r": "#e8968a"}


def stamp(rows, x0, y0, art):
    """Draws art at x0,y0. "." keeps a pixel, "," clears it, anything else paints."""
    out = [list(r) for r in rows]
    for dy, line in enumerate(art):
        for dx, c in enumerate(line):
            if c != ".":
                out[y0 + dy][x0 + dx] = "." if c == "," else c
    return ["".join(r) for r in out]


def put(rows, points):
    """Draws (x, y, char) points; char "," clears."""
    out = [list(r) for r in rows]
    for x, y, c in points:
        out[y][x] = "." if c == "," else c
    return ["".join(r) for r in out]


def under(back, front):
    """Lays front over back, both full grids."""
    return ["".join(f if f != "." else b for b, f in zip(br, fr)) for br, fr in zip(back, front)]


def shift_left(rows, n):
    return [r[n:] + "." * n for r in rows]


def col(x, ys, c):
    return [(x, y, c) for y in ys]


def ring(cx, top, c="1"):
    return [(cx, top, c), (cx - 1, top + 1, c), (cx + 1, top + 1, c), (cx, top + 2, c)]


HOBBIT_HEAD = [
    "........" "........" "........",
    "........" "........" "........",
    "........" "oooooooo" "........",
    ".......o" "hhHhhHhh" "o.......",
    "......oh" "HhhhhhhH" "ho......",
    "......oh" "hhhhhhhh" "ho......",
    "......oh" "shhsshhs" "ho......",
    "......oh" "ssssssss" "ho......",
    ".....oSh" "skssssks" "hSo.....",
    ".....oSh" "skssssks" "hSo.....",
    "......oh" "ssssssss" "ho......",
    "......oo" "sssmmsss" "oo......",
    ".......o" "osssssso" "o.......",
]
HOBBIT_LEGS = [
    "....osso" "cPPPPPPc" "osso....",
    ".....oo." "oPPPPPPo" ".oo.....",
    "........" "oPPooPPo" "........",
    "......os" "hho..ohh" "so......",
    "......oo" "ooo..ooo" "oo......",
]

FRODO = HOBBIT_HEAD + [
    ".....ooo" "CcLLLLcC" "ooo.....",
    "....oCCC" "cczLLzcc" "CCCo....",
    "....oCGC" "cVLyyLVc" "CGCo....",
    "....oCGC" "cVyLLyVc" "CGCo....",
    "....oCGC" "cVLyyLVc" "CGCo....",
    "....oCCC" "cVVVVVVc" "CCCo....",
] + HOBBIT_LEGS
FRODO_PAL = {**SKIN, "h": "#4a2e1a", "H": "#6e4628", "C": "#4f7038", "c": "#36522a", "G": "#6f9050",
             "L": "#ece6d4", "V": "#8a6a3a", "y": "#f2c230", "P": "#6b5235"}

SAM = HOBBIT_HEAD[:10] + [
    "......oh" "rssssssr" "ho......",
] + HOBBIT_HEAD[11:] + [
    ".....ooo" "LlLLLLlL" "ooo.....",
    "....oLLL" "VLLLLLLV" "LLLo....",
    "....oLlL" "VVVLLVVV" "LlLo....",
    "....oLlL" "VVVLLVVV" "LlLo....",
    "....oLLL" "VVVVVVVV" "LLLo....",
    "....oooo" "vVVVVVVv" "oooo....",
] + [r.replace("c", "o") if i == 0 else r for i, r in enumerate(HOBBIT_LEGS)]
SAM_PAL = {**SKIN, "h": "#94612e", "H": "#b47c40", "L": "#ece6d4", "l": "#c9c0a6", "V": "#c0662a", "v": "#94481c",
           "P": "#6b5235", "c": "#6b5235"}

LEGOLAS = [
    "........" "........" "........",
    "........" "........" "........",
    "........" "oooooooo" "........",
    ".......o" "YYYYYYYY" "o.......",
    "......oY" "YYYYYYYY" "Yo......",
    "......oY" "YYYYYYYY" "Yo......",
    "......oY" "YYYsssss" "Yo......",
    "....o.oY" "ssssssss" "Yo.o....",
    "....oSSY" "skssssks" "YSSo....",
    ".....oSY" "skssssks" "YSo.....",
    "......oY" "ssssssss" "Yo......",
    "......oY" "sssmmsss" "Yo......",
    "......oY" "osssssso" "Yo......",
    ".....oYY" "oEeEEeEo" "YYo.....",
    "....oEYY" "EEEEEEEE" "YYEo....",
    "....oEeE" "EEEEEEEE" "EeEo....",
    "....oEeE" "EEEEEEEE" "EeEo....",
    "....oEeE" "nnnynnnn" "EeEo....",
    "....oEEE" "EEEEEEEE" "EEEo....",
    "....osso" "EEEeeEEE" "osso....",
    ".....oo." "oeeeeeeo" ".oo.....",
    "........" "oDDooDDo" "........",
    ".......o" "nno..onn" "o.......",
    ".......o" "ooo..ooo" "o.......",
]
LEGOLAS_PAL = {**SKIN, "Y": "#ead47e", "w": "#fff2b8", "E": "#5f8a3e", "e": "#46682c", "n": "#6b4a2a",
               "y": "#d4a017", "D": "#4a5a3a"}

GIMLI = [
    "........" "........" "........",
    "........" "........" "........",
    "........" "........" "........",
    "........" "oooooooo" "........",
    ".......o" "MwwMMMMM" "o.......",
    "......oM" "wMMMMMMM" "Mo......",
    "......oM" "MMMyyMMM" "Mo......",
    ".....omm" "mmmmmmmm" "mmo.....",
    ".....oMR" "RRssssRR" "RMo.....",
    ".....oMR" "skssssks" "RMo.....",
    ".....oMR" "RssSSssR" "RMo.....",
    "...oDRRR" "RRRRRRRR" "RRRDo...",
    "..oDDRRR" "RrRRRRrR" "RRRDDo..",
    "..oDdDRR" "RrRRRRrR" "RRDdDo..",
    "..oDdDoR" "RrRRRRrR" "RoDdDo..",
    "..oDdDoR" "RrRRRRrR" "RoDdDo..",
    "..ossso." "nyRRRRyn" ".ossso..",
    "..ossso." "nnoRRonn" ".ossso..",
    "...ooo.o" "MMMooMMM" "o.ooo...",
    "......oM" "mMMoMMmM" "Mo......",
    "......oo" "PPPooPPP" "oo......",
    ".....onn" "nnno.onn" "nno.....",
    ".....onn" "nnno.onn" "nno.....",
    ".....ooo" "oooo.ooo" "ooo.....",
]
GIMLI_PAL = {**SKIN, "M": "#a3a3a8", "m": "#6e6e74", "w": "#e0e0e4", "y": "#d4a017", "R": "#c4512a", "r": "#8e3418",
             "D": "#6b4a2a", "d": "#4e341c", "P": "#5a4030", "n": "#3e2a1c"}

GANDALF = [
    "........" "....oo.." "........",
    "........" "...oGo.." "........",
    "........" "..oGGo.." "........",
    "........" "..oGgGo." "........",
    "........" ".oGGgGo." "........",
    "........" "oGGGgGGo" "........",
    "....ooGG" "GGGGGGGG" "GGoo....",
    "...oGGGG" "gggggggg" "GGGGo...",
    "....oooW" "ssssssss" "Wooo....",
    "......oW" "sWWssWWs" "Wo......",
    "......oW" "skssssks" "Wo......",
    "......oW" "sWWWWWWs" "Wo......",
    ".....oWW" "WWWWWWWW" "WWo.....",
    "....oGGw" "WWWWWWWW" "wGGo....",
    "...oGGGw" "WWWWWWWW" "wGGGo...",
    "...oGgGG" "wWWWWWWw" "GGgGo...",
    "...oGgGG" "GwWWWWwG" "GGgGo...",
    "...oGgGG" "GGwWWwGG" "GGgGo...",
    "...ossoG" "GGGwwGGG" "Gosso...",
    "....oooG" "GGGGGGGG" "Gooo....",
    "......oG" "GgGGGGgG" "Go......",
    "......oG" "gGGGGGGg" "Go......",
    "......ok" "kko..okk" "ko......",
    "......oo" "ooo..ooo" "oo......",
]
GANDALF_STAFF = [
    "........" "........" "........",
    "........" "........" "........",
    "........" "........" "..ooo...",
    "........" "........" ".oTTTo..",
    "........" "........" ".oTXTo..",
    "........" "........" ".ooTTo..",
    "........" "........" "..oTo...",
] + ["........" "........" "..oTo..."] * 15 + ["........" "........" "..ooo..."] + ["........" * 3]
GANDALF_PAL = {**SKIN, "G": "#8f9198", "g": "#6a6c74", "W": "#eeeeee", "w": "#c4c4c8", "T": "#7a5230",
               "x": "#cfe6ff", "X": "#ffffff", "k": "#3a3a40"}

ARAGORN = [
    "........" "........" "........",
    "........" "........" "........",
    "........" "oooooooo" "........",
    ".......o" "hhhHhhhh" "o.......",
    "......oh" "hHhhhhHh" "ho......",
    "......oh" "hhhhhhhh" "ho......",
    "......oh" "hsshhssh" "ho......",
    "......oh" "ssssssss" "ho......",
    ".....oSh" "skssssks" "hSo.....",
    ".....oSh" "skssssks" "hSo.....",
    "......oh" "ssssssss" "ho......",
    "......oh" "bssmmssb" "ho......",
    "......oh" "obbbbbbo" "ho......",
    ".....ohh" "oCwLLwCo" "hho.....",
    "....oCCC" "CcLLLLcC" "CCCo....",
    "....oCcC" "CcLlLLcC" "CcCo....",
    "....oCcC" "CcLlLLcC" "CcCo....",
    "....oCcC" "nnnynnnn" "CcCo....",
    "....oCCC" "CcLLLLcC" "CCCo....",
    "....osso" "CcPPPPcC" "osso....",
    ".....oo." "oCPPPPCo" ".oo.....",
    "........" "oPPooPPo" "........",
    ".......o" "nno..onn" "o.......",
    ".......o" "ooo..ooo" "o.......",
]
ARAGORN_PAL = {**SKIN, "h": "#2e2018", "H": "#4a3424", "b": "#8a5e44", "C": "#4a5a42", "c": "#36442f",
               "w": "#c8ccd4", "L": "#6b4a2a", "l": "#523620", "n": "#3e2a1c", "y": "#c9a34a", "P": "#4a4038",
               "g": "#c9a34a", "G": "#7a5230", "V": "#3a2a1e"}

SAURON = [
    "........" "...SS..." "........",
    "........" ".S.SS.S." "........",
    "........" "oSSSSSSo" "........",
    "........" "oHHHHHHo" "........",
    "........" "oHhhhhHo" "........",
    "........" "oeehheeo" "........",
    "........" "oHhHHhHo" "........",
    ".....S.." "oHhHHhHo" "..S.....",
    ".....oS." ".oHhhHo." ".So.....",
    "....ooSS" "PoAAAAoP" "SSoo....",
    "...oSPPP" "pAAAAAAp" "PPPSo...",
    "...opppo" "oAAaaAAo" "opppo...",
    "....oAAo" "oAehheAo" "oAAo....",
    "....oAgo" "oAAaaAAo" "ogAo....",
    "....oAAo" "oAAAAAAo" "oAAo....",
    "....oAgo" "oyyyyyyo" "ogAo....",
    "...oGGGo" "oCcCCcCo" "oGGGo...",
    "...oGGGo" "oCcCCcCo" "oGGGo...",
    "....ooo." "oACCCCAo" ".ooo....",
    "........" "oACcCCAo" "........",
    "........" "oACcCCAo" "........",
    "........" "oAAooAAo" "........",
    ".......o" "AAo..oAA" "o.......",
    "......oo" "ooo..ooo" "oo......",
]
SAURON_PAL = {"o": "#0e0e12", "S": "#8a8a96", "H": "#4e4e5a", "h": "#121216", "e": "#ff7a1a", "P": "#62626e",
              "p": "#3c3c46", "A": "#40404c", "a": "#a8401a", "g": "#6e6e7a", "C": "#2e2a32", "c": "#46404e",
              "y": "#9a6e22", "G": "#5a5a66", "T": "#3a3a40", "M": "#6e6e7a", "m": "#a0a0aa"}


# Digit keys: no character palette uses them, so smoke never recolors a beard or a cloak.
SMOKE = {"1": "#9e978a", "2": "#b8b1a3", "3": "#e0662e", "4": "#ffb04a", "5": "#5a3a1e", "6": "#8a6038",
         "z": "#7a4a30"}
# Drawn into the empty top-left corner.
BADGES = {
    "blocked": ([".oo.", "o!!o", "o!!o", "o!!o", "o!!o", ".oo.", "o!!o", ".oo."], {"!": "#e0461c"}),
    "done": ([".@@*.", "@...@", "@...@", "@...@", ".@@@."], {"@": "#d4a017", "*": "#fff4b0"}),
}


def asleep(rows, eye_rows):
    """Closes the eyes: the upper eye rows turn to skin, the lowest one to a lid line."""
    out = list(rows)
    *upper, lower = eye_rows
    for y in upper:
        out[y] = out[y].replace("k", "s")
    out[lower] = out[lower].replace("k", "z")
    return out


def smoke(rows, bowl, low):
    """Pipe ember and a smoke ring: low on the first idle frame, high on the second."""
    bx, by = bowl
    wisp = [] if low else [(bx + (1 if bx < SIZE // 2 else -1), by - 3, "2")]
    return put(rows, [(bx, by, "3")] + ring(bx, by - 4 if low else by - 8, "1") + wisp)


def hero(name):
    """A character's base pose and palette."""
    if name == "frodo":
        return FRODO, FRODO_PAL
    if name == "sam":
        return SAM, SAM_PAL
    if name == "legolas":
        return bow(LEGOLAS, "rest"), {**LEGOLAS_PAL, **BOW}
    if name == "gimli":
        return gimli_axe_low(GIMLI), GIMLI_PAL
    if name == "gandalf":
        return under(GANDALF_STAFF, GANDALF), GANDALF_PAL
    if name == "aragorn":
        return scabbard(ARAGORN, drawn=False), ARAGORN_PAL
    if name == "sauron":
        return sauron_mace_low(SAURON), SAURON_PAL
    raise KeyError(name)


def gimli_axe_low(rows):
    return stamp(rows, 18, 10, [
        "...o..",
        "..oTo.",
        "...To.",
        "...To.",
        "...To.",
        "...To.",
        "...so.",
        "...so.",
        "..oTo.",
        ".ooToo",
        "oAATAA",
        "oAwTAA",
        ".ooToo",
        "...o..",
    ])


def scabbard(rows, drawn):
    """The scabbard at the left hip, with the hilt in it or empty."""
    hilt = ["..o..", ".o,o.", ".o,o.", "ooooo"] if drawn else ["..o..", ".oGo.", ".oGo.", "ogggo"]
    return stamp(rows, 1, 13, hilt + [".oVo."] * 6 + ["..o.."])


def sauron_mace_low(rows):
    return stamp(rows, 17, 18, [
        ".oTo..",
        ".oTo..",
        ".omo..",
        "oMMMo.",
        "mMwMm.",
        "oMMMo.",
    ])


def frodo_frames():
    base, pal = hero("frodo")
    pal = {**pal, **SMOKE, "X": "#e4f3ff", "x": "#8cc8ff", "b": "#5ab0ff", "g": "#c9a34a", "p": "#6b4a2a"}
    body = shift_left(base, 2)
    body = stamp(body, 14, 19, ["oCCo"])
    up = stamp(body, 15, 0, [
        "..ooo.",
        "..oXo.",
        "..oXo.",
        "..oXo.",
        "..oXo.",
        "..oXo.",
        "..oXo.",
        "..oXo.",
        ".ogggo",
        "..oso.",
        "..oCo.",
        ".oCCo.",
        ".oCo..",
        "oCo...",
    ])
    up = put(up, [(20, 2, "b"), (16, 4, "b"), (20, 6, "b"), (21, 4, "x")])
    strike = stamp(body, 15, 12, [
        "..ooogoo.",
        ".CCCsgXXX",
        "..ooogooo",
    ])
    strike = put(strike, [(18, 2, "x"), (20, 3, "b"), (21, 4, "b"), (22, 6, "b"), (23, 8, "b"), (23, 10, "x"), (22, 11, "x")])
    pipe = [(13, 11, "p"), (14, 11, "p"), (15, 11, "p"), (16, 11, "p"), (17, 11, "p"), (18, 11, "5"), (19, 11, "5"),
            (18, 12, "o"), (19, 12, "o"), (20, 11, "o"), (20, 10, "o"), (17, 12, "s")]
    still = asleep(base, [8, 9])
    return pal, {
        "frodo": base, "frodo-work": up, "frodo-2": strike,
        "frodo-idle": smoke(put(still, pipe + [(19, 10, "5")]), (18, 10), True),
        "frodo-idle-2": put(smoke(put(still, pipe + [(19, 10, "5")]), (18, 10), False), [(18, 10, "4")]),
    }


def sam_frames():
    base, pal = hero("sam")
    pal = {**pal, **SMOKE, "N": "#3c3c44", "z": "#7a4a30", "w": "#9aa8bc", "*": "#ffd84a", "p": "#6b4a2a", "b": "#7a5230",
           "t": "#c8b89a"}
    body = stamp(base, 16, 19, ["o,,,"])
    body = put(body, [(16, 18, "o"), (17, 18, "o"), (18, 18, "o"), (19, 18, ".")])
    pan = ["...oooo.", "..oNNNNo", "..oNwNNo", "..oNNwNo", "..oNNNNo", "...oooo."]
    up = stamp(body, 16, 0, pan + [
        "...obo..",
        "...obo..",
        "...oso..",
        "..oLLo..",
        "..oLLo..",
        ".oLLo...",
        ".oLLo...",
        "oLLo....",
    ])
    strike = stamp(body, 16, 6, pan + [
        "....obo.",
        "..ooosoo",
        "LLLLLso.",
        "LLLooo..",
    ])
    strike = put(strike, [(23, 5, "*"), (22, 4, "*"), (23, 3, "*"), (21, 1, "t"), (23, 3, "*"), (19, 1, "t"), (22, 2, "t")])
    pipe = [(10, 11, "p"), (9, 11, "p"), (8, 11, "p"), (7, 11, "p"), (6, 11, "p"), (5, 11, "5"), (4, 11, "5"),
            (5, 12, "o"), (4, 12, "o"), (3, 11, "o"), (3, 10, "o"), (6, 12, "s")]
    still = asleep(base, [8, 9])
    return pal, {
        "sam": base, "sam-work": up, "sam-2": strike,
        "sam-idle": smoke(put(still, pipe + [(4, 10, "5")]), (5, 10), True),
        "sam-idle-2": put(smoke(put(still, pipe + [(4, 10, "5")]), (5, 10), False), [(5, 10, "4")]),
    }


BOW = {"B": "#6b3e1a", "j": "#9a9a9a", "a": "#8a6a3a", "A": "#b0b6c0", "w": "#c8b88a", "f": "#c94a2a"}


def bow(rows, mode):
    """The bow in the hand held out to the side: resting, drawn, or just loosed."""
    pts = [(20, 4, "B"), (21, 5, "B"), (22, 6, "B")] + col(22, range(7, 20), "B") + [(22, 20, "B"), (21, 21, "B"), (20, 22, "B")]
    pts += [(19, 12, "o"), (20, 12, "o"), (19, 13, "E"), (20, 13, "E"), (20, 14, "o"), (21, 12, "o"), (21, 13, "s"), (21, 14, "o"),
            (23, 12, "o"), (23, 13, "s"), (23, 14, "o")]
    if mode == "drawn":
        string = [(20, 5), (19, 6), (19, 7), (18, 8), (18, 9), (17, 10), (17, 11), (16, 12),
                  (16, 14), (17, 15), (17, 16), (18, 17), (18, 18), (19, 19), (19, 20), (20, 21)]
        pts += [(x, y, "j") for x, y in string]
        pts += [(x, 13, "a") for x in range(15, 21)] + [(22, 13, "a"), (23, 13, "A"), (13, 12, "f"), (13, 14, "f"), (14, 13, "f"),
                                                      (16, 13, "s"), (15, 13, "s")]
    else:
        pts += [(20, y, "j") for y in range(5, 22) if y not in (12, 13, 14)]
    if mode == "loose":
        pts += [(18, 2, "a"), (19, 2, "a"), (20, 2, "a"), (21, 2, "a"), (22, 2, "A"), (23, 1, "A"), (16, 2, "w"), (14, 2, "w"),
                (17, 1, "f"), (17, 3, "f"), (19, 9, "j"), (18, 16, "j")]
    return put(rows, pts)


def legolas_frames():
    base, pal = hero("legolas")
    pal = {**pal, "L": "#f0e2b8", "l": "#a8c45a", "z": "#8a5a40"}
    draw = bow(LEGOLAS, "drawn")
    loose = bow(LEGOLAS, "loose")
    still = asleep(base, [8, 9])
    hand_up = stamp(still, 4, 19, ["oEEo"])
    lembas_low = put(hand_up, [(6, 14, "o"), (7, 14, "o"), (8, 14, "o"), (9, 14, "o"), (6, 15, "o"), (7, 15, "L"), (8, 15, "L"), (9, 15, "o"),
                               (6, 16, "o"), (7, 16, "l"), (8, 16, "l"), (9, 16, "o"), (6, 17, "s"), (7, 17, "s"), (8, 17, "o")])
    lembas_high = put(hand_up, [(7, 10, "o"), (8, 10, "o"), (9, 10, "o"), (7, 11, "o"), (8, 11, "L"), (9, 11, "L"), (10, 11, "o"),
                                (7, 12, "o"), (8, 12, "l"), (9, 12, "l"), (10, 12, "o"), (7, 13, "s"), (8, 13, "s"), (9, 13, "o")])
    return pal, {"legolas": base, "legolas-work": draw, "legolas-2": loose,
                 "legolas-idle": lembas_low, "legolas-idle-2": lembas_high}


def gimli_frames():
    base, pal = hero("gimli")
    pal = {**pal, **SMOKE, "A": "#c9ccd2", "w": "#f2f2f4", "T": "#7a5230", "*": "#ffd84a", "z": "#8a5a40", "p": "#6b4a2a"}
    noarm = stamp(GIMLI, 16, 13, [
        "..o,,,,.",
        "..,,,,,.",
        "..,,,,,.",
        "o,,,,,,.",
        "o,,,,,,.",
    ])
    noarm = put(noarm, [(17, 13, "D"), (17, 14, "o"), (17, 15, "o"), (18, 13, "o")])
    up = stamp(noarm, 17, 0, [
        "..oo.oo",
        ".oAATAA",
        ".oAwTAA",
        "..ooToo",
        "...oTo.",
        "...oTo.",
        "...oTo.",
        "..ossso",
        "..ossso",
        "..oDDo.",
        "..oDDo.",
        "..DDo..",
    ])
    strike = stamp(gimli_axe_low(GIMLI), 18, 19, [
        "..oTo.",
        ".ooToo",
        "oAATAA",
        "oAwTAA",
        ".ooToo",
    ])
    strike = put(strike, [(18, 18, "*"), (17, 20, "*"), (17, 23, "*"), (22, 1, "w"), (23, 3, "w"), (23, 6, "w"), (23, 9, "w"), (22, 12, "w")])
    pipe = [(8, 11, "p"), (7, 11, "p"), (6, 11, "p"), (5, 11, "p"), (4, 11, "5"), (3, 11, "5"), (4, 12, "o"), (3, 12, "o"),
            (2, 11, "o"), (2, 10, "o"), (3, 10, "5"), (5, 12, "s")]
    still = asleep(base, [8])
    return pal, {"gimli": base, "gimli-work": up, "gimli-2": strike,
                 "gimli-idle": smoke(put(still, pipe), (4, 10), True),
                 "gimli-idle-2": put(smoke(put(still, pipe), (4, 10), False), [(4, 10, "4")])}


def gandalf_frames():
    base, pal = hero("gandalf")
    pal = {**pal, **SMOKE, "b": "#8fd0ff", "B": "#4aa8ff", "z": "#8a5a40", "p": "#6b4a2a", "X": "#ffffff", "x": "#cfe6ff"}
    charge = put(base, [(19, 3, "x"), (16, 1, "b"), (22, 0, "b"), (22, 5, "b"), (15, 4, "b")])
    rays = [(19, 0, "X"), (19, 1, "x"), (16, 3, "X"), (17, 3, "x"), (21, 3, "x"), (22, 3, "X"), (23, 3, "b"),
            (17, 1, "x"), (16, 0, "b"), (21, 1, "x"), (22, 0, "b"), (21, 5, "x"), (22, 6, "b"), (15, 3, "b"), (14, 3, "B"),
            (16, 5, "B"), (23, 7, "B"), (19, 3, "X"), (18, 2, "X"), (20, 2, "X"), (18, 4, "x"), (20, 4, "x"),
            (17, 23, "b"), (16, 22, "B"), (21, 23, "b"), (22, 22, "B"), (18, 22, "x"), (20, 22, "x")]
    burst = put(base, rays)
    pipe = [(8, 12, "p"), (7, 12, "p"), (6, 13, "p"), (5, 13, "p"), (4, 13, "5"), (3, 13, "5"), (4, 14, "o"), (3, 14, "o"),
            (2, 13, "o"), (2, 12, "o"), (3, 12, "5"), (6, 14, "s"), (5, 14, "s")]
    still = asleep(base, [10])
    return pal, {"gandalf": base, "gandalf-work": charge, "gandalf-2": burst,
                 "gandalf-idle": smoke(put(still, pipe), (4, 12), True),
                 "gandalf-idle-2": put(smoke(put(still, pipe), (4, 12), False), [(4, 12, "4")])}


def aragorn_frames():
    base, pal = hero("aragorn")
    pal = {**pal, **SMOKE, "X": "#eef2f8", "x": "#a8b0bc", "*": "#fff4b0", "z": "#8a5a40", "p": "#6b4a2a"}
    empty = scabbard(ARAGORN, drawn=True)
    up = stamp(empty, 16, 0, [
        "...o..",
        "..oXo.",
        "..oXo.",
        "..oXo.",
        "..oXo.",
        "..oXo.",
        "..oXo.",
        "..oXo.",
        ".ogggo",
        "..oGo.",
        "..oso.",
        ".oCCo.",
        ".oCo..",
        "oCo...",
    ])
    up = put(up, [(21, 1, "*"), (20, 0, "*"), (22, 2, "*"), (21, 2, "x")])
    strike = stamp(empty, 15, 12, [
        "..ooo.oo.",
        ".CCsgXXXX",
        "..ooo.oo.",
    ])
    strike = put(strike, [(19, 4, "x"), (21, 5, "x"), (22, 7, "x"), (23, 9, "x"), (23, 11, "x")])
    pipe = [(8, 11, "p"), (7, 11, "p"), (6, 11, "p"), (5, 11, "p"), (4, 11, "5"), (3, 11, "5"), (4, 12, "o"), (3, 12, "o"),
            (2, 11, "o"), (2, 10, "o"), (3, 10, "5"), (5, 12, "s")]
    still = asleep(base, [8, 9])
    return pal, {"aragorn": base, "aragorn-work": up, "aragorn-2": strike,
                 "aragorn-idle": smoke(put(still, pipe), (4, 10), True),
                 "aragorn-idle-2": put(smoke(put(still, pipe), (4, 10), False), [(4, 10, "4")])}


def sauron_frames():
    base, pal = hero("sauron")
    pal = {**pal, "E": "#ffe08a", "f": "#ff9a2a", "F": "#ffd04a", "d": "#7a2a10", "w": "#c8c8d0"}
    eyes = [(9, 5), (10, 5), (13, 5), (14, 5)]
    noarm = stamp(SAURON, 16, 12, [",,,,,"] * 7)
    up = stamp(noarm, 16, 0, [
        "....omo.",
        "...oMMMo",
        "...mMwMm",
        "...oMMMo",
        "....oTo.",
        "...oGGGo",
        "...oGGGo",
        "...oAAo.",
        "..oAAo..",
    ])
    up = put(up, [(x, y, "E") for x, y in eyes])
    strike = stamp(SAURON, 16, 18, [
        "..oTo..",
        "f.oTo.f",
        "..omo..",
        "FoMMMoF",
        ".mMwMm.",
        "foMMMof",
    ])
    strike = put(strike, [(x, y, "E") for x, y in eyes] + [(9, 0, "f"), (14, 0, "f"), (11, 0, "F"), (12, 0, "F"),
                                                          (22, 2, "w"), (23, 5, "w"), (23, 9, "w"), (23, 13, "w")])
    dim = put(base, [(x, y, "d") for x, y in eyes])
    return pal, {"sauron": base, "sauron-work": up, "sauron-2": strike, "sauron-idle": dim, "sauron-idle-2": base}


CAST = ["gandalf", "aragorn", "frodo", "sam", "legolas", "gimli", "sauron"]
FRAMES = (gandalf_frames, aragorn_frames, frodo_frames, sam_frames, legolas_frames, gimli_frames, sauron_frames)
POSES = dict(zip(CAST, (frames() for frames in FRAMES)))
# Base pose with the character's full palette, every pose's colors included.
SPRITES = {name: (poses[name], palette) for name, (palette, poses) in POSES.items()}


def badged(name, badge):
    rows, palette = SPRITES[name]
    mark, colors = BADGES[badge]
    for y, line in enumerate(mark):
        for x, c in enumerate(line):
            assert c == "." or rows[y][x] == ".", f"{badge} badge covers {name} at {x},{y}"
    return stamp(rows, 0, 0, mark), {**palette, **colors}


def all_sprites():
    """Every agent sprite: base, battle, idle and badge poses."""
    table = {}
    for palette, poses in POSES.values():
        for key, rows in poses.items():
            table[key] = (rows, palette)
    for name in CAST:
        for badge in BADGES:
            table[f"{name}-{badge}"] = badged(name, badge)
    return table


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


def svg(rows, palette, display_size):
    size = len(rows)
    rects = []
    for y, row in enumerate(rows):
        assert len(row) == size, f"row {y} has {len(row)} cols: {row!r}"
        x = 0
        while x < size:
            c = row[x]
            run = 1
            while x + run < size and row[x + run] == c:
                run += 1
            if c != ".":
                rects.append(f'<rect x="{x}" y="{y}" width="{run}" height="1" fill="{palette[c]}"/>')
            x += run
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
            f'width="{display_size}" height="{display_size}" shape-rendering="crispEdges">' + "".join(rects) + "</svg>\n")


def write_all(table, folder, display_size=None):
    os.makedirs(folder, exist_ok=True)
    for name, (rows, palette) in table.items():
        with open(os.path.join(folder, f"{name}.svg"), "w") as f:
            f.write(svg(rows, palette, display_size or len(rows)))


if __name__ == "__main__":
    sprites = all_sprites()
    for name, (rows, _) in sprites.items():
        assert len(rows) == SIZE, f"{name} has {len(rows)} rows"
    write_all(sprites, os.path.join(HOME, "fellowship", "sprites"), AGENT_DISPLAY_SIZE)
    write_all(EMBLEMS, os.path.join(HOME, "realms", "emblems"))
    print("ok", len(sprites), "sprites,", len(EMBLEMS), "emblems", file=sys.stderr)
