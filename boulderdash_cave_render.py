#!/usr/bin/env python3
"""Render Boulder Dash (C64) caves on the console from a 64 KB VICE memory dump.

Two modes:
  live   - print the cave map exactly as it is in RAM ($0850-$0BBF, 40x22),
           i.e. the running game's current state, plus the status values.
  decode - rebuild any of the 20 caves at any level (1-5) the way the game
           does it at cave start ($8AB9):
             $8226 copy the cave record to $2400 and seed the RNG
             $8043 random fill of rows 1-21 (RNG $7085, tables $2418/$241C)
             $85A7 steel border (tile $07, 40x22 outline)
             $8518 draw the object list at $2420 (point/line/box/outline)
           All tables (cave offsets, row table, direction table) are read from
           the dump itself, so nothing game-specific is hard-coded except
           addresses.

Usage:
  bd_cave_render.py DUMP                      # live map of the running game
  bd_cave_render.py DUMP --cave 13 --level 1  # decode cave M, level 1
  bd_cave_render.py DUMP --all                # decode all 20 caves, level 1
  bd_cave_render.py DUMP --diff               # decode the current cave and
                                              # compare it with the live map
Options: --color (ANSI colours), --legend, --hex (tile IDs instead of chars)
"""

import argparse
import sys

# --- addresses (see sessions/boulderdash/*.txt) ------------------------------
MAP_BASE = 0x0850          # live cave map, 40 x 22, row-major
MAP_W, MAP_H = 40, 22
DECODE_BASE = 0x0800       # decoder y coordinates are map row + 2 ($8406 table)
ROW_TABLE = 0x8406         # 2-byte row addresses used by the object decoder
DIR_TABLE = 0x8454         # 8 x 2-byte signed deltas for line directions
CAVE_OFFSETS = 0x5804      # word per cave number: offset from CAVE_DATA
CAVE_DATA = 0x582E
RECORD_LEN = 240           # bytes copied to $2400 by $8246
CAVE_COUNT = 20

# tile ID -> (char, ansi colour, description)
TILES = {
    0x00: (" ", "0", "empty"),
    0x01: (".", "33", "dirt"),
    0x02: ("=", "37", "brick wall"),
    0x03: ("M", "36", "magic wall"),
    0x04: ("X", "90", "exit (closed)"),
    0x05: ("E", "92", "exit (open)"),
    0x07: ("#", "90", "steel wall"),
    0x10: ("o", "97", "boulder"),
    0x14: ("*", "96", "diamond"),
    0x25: ("I", "95", "entrance"),
    0x38: ("@", "93", "player"),
    0x3A: ("a", "32", "amoeba"),
}
RANGES = [  # (lo, hi, char, colour, description)
    (0x08, 0x0F, "F", "91", "firefly (+moved)"),
    (0x11, 0x13, "o", "97", "boulder (moved/falling)"),
    (0x15, 0x17, "*", "96", "diamond (moved/falling)"),
    (0x1B, 0x1F, "%", "31", "explosion -> space"),
    (0x20, 0x24, "$", "94", "explosion -> diamond"),
    (0x26, 0x28, "I", "95", "entrance animation"),
    (0x30, 0x37, "B", "35", "butterfly (+moved)"),
    (0x39, 0x39, "@", "93", "player (moved)"),
    (0x3B, 0x3B, "a", "32", "amoeba (new)"),
]


def tile_info(t):
    if t in TILES:
        return TILES[t]
    for lo, hi, ch, col, desc in RANGES:
        if lo <= t <= hi:
            return ch, col, desc
    return "?", "0", "unknown"


def cave_name(n):
    if 1 <= n <= 16:
        return "Cave " + chr(ord("A") + n - 1)
    if 17 <= n <= 20:
        return "Intermission %d" % (n - 16)
    return "cave #%d" % n


def load_dump(path):
    data = open(path, "rb").read()
    if len(data) != 0x10000:
        sys.exit("%s: expected a 65536-byte RAM dump, got %d bytes" % (path, len(data)))
    return data


def word(mem, addr):
    return mem[addr] | (mem[addr + 1] << 8)


# --- game algorithms ---------------------------------------------------------
def next_random(s1, s2):
    """$7085: s1 = $3F, s2 = $3E. Returns (s1, s2); the game uses s1."""
    t1 = (s1 & 1) << 7
    t2 = (s2 >> 1) & 0x7F
    r = s2 + ((s2 & 1) << 7)
    c = r >> 8
    r = (r & 0xFF) + c + 0x13
    c = r >> 8
    s2 = r & 0xFF
    r = s1 + c + t1
    c = r >> 8
    r = (r & 0xFF) + c + t2
    s1 = r & 0xFF
    return s1, s2


def cave_record(mem, n):
    """$8226: 240 bytes from $582E + word[$5804 + 2n]."""
    start = CAVE_DATA + word(mem, CAVE_OFFSETS + 2 * n)
    return bytes(mem[(start + i) & 0xFFFF] for i in range(RECORD_LEN))


class Decoder:
    def __init__(self, mem):
        self.mem = mem
        # buffer covers $0800-$0BBF (decoder rows 0..23, map rows = y - 2)
        self.buf = bytearray(MAP_W * (MAP_H + 2))
        self.dirs = []
        for i in range(8):
            d = word(mem, DIR_TABLE + 2 * i)
            self.dirs.append(d - 0x10000 if d & 0x8000 else d)

    def addr(self, x, y):
        """$8436: row_table[y] + x, as an offset into buf."""
        return (word(self.mem, ROW_TABLE + 2 * y) + x - DECODE_BASE) & 0xFFFF

    def put(self, a, tile):
        if 0 <= a < len(self.buf):
            self.buf[a] = tile

    def line_from(self, a, count, direction, tile):
        """$8464: draw `count` cells (8-bit DEC/BMI loop), return end pointer."""
        c = count & 0xFF
        delta = self.dirs[direction & 7]
        while True:
            c = (c - 1) & 0xFF
            if c & 0x80:
                return a
            self.put(a, tile)
            a = (a + delta) & 0xFFFF

    def fill_rect(self, x, y, w, h, tile):
        """$8498: h rows of w cells."""
        a = self.addr(x, y)
        rows = h & 0xFF
        while True:
            rows = (rows - 1) & 0xFF
            if rows & 0x80:
                return
            col = w & 0xFF
            while True:
                col = (col - 1) & 0xFF
                if col & 0x80:
                    break
                self.put(a + col, tile)
            a += MAP_W

    def outline(self, x, y, w, h, tile):
        """$84D7: right w-1, down h-1, left w-1, up h-1."""
        a = self.addr(x, y)
        a = self.line_from(a, w - 1, 2, tile)
        a = self.line_from(a, h - 1, 4, tile)
        a = self.line_from(a, w - 1, 6, tile)
        self.line_from(a, h - 1, 0, tile)

    def build(self, rec, level):
        # $8226: seeds  ($3E = seed[level], $3F = 0)
        s2, s1 = rec[0x04 + level], 0
        objs, probs = rec[0x18:0x1C], rec[0x1C:0x20]
        # $8043: random fill, map rows 1..21, cols 0..39
        for row in range(1, MAP_H):
            for col in range(MAP_W):
                s1, s2 = next_random(s1, s2)
                tile = 0x01
                for i in range(4):
                    if s1 < probs[i]:
                        tile = objs[i]
                self.buf[(row + 2) * MAP_W + col] = tile
        # $85A7: steel border
        self.outline(0, 2, 40, 22, 0x07)
        # $8518: object list at $2420 ($FF-terminated, 8-bit index)
        y = 0x20
        while y < RECORD_LEN:
            code = rec[y]
            if code == 0xFF:
                break
            tile = code & 0x3F
            args = [rec[(y + k) & 0xFF] if y + k < RECORD_LEN else 0 for k in range(1, 6)]
            x0, y0, w, h, inner = args
            kind = code & 0xC0
            if kind == 0x00:                      # point, 3 bytes
                self.put(self.addr(x0, y0), tile)
                y += 3
            elif kind == 0x40:                    # line: len, dir, 5 bytes
                self.line_from(self.addr(x0, y0), w, h, tile)
                y += 5
            elif kind == 0x80:                    # filled box + inner, 6 bytes
                self.fill_rect(x0, y0, w, h, tile)
                self.fill_rect(x0 + 1, y0 + 1, w - 2, h - 2, inner)
                y += 6
            else:                                 # outline box, 5 bytes
                self.outline(x0, y0, w, h, tile)
                y += 5
        return [list(self.buf[(r + 2) * MAP_W:(r + 3) * MAP_W]) for r in range(MAP_H)]


def decode_cave(mem, n, level):
    rec = cave_record(mem, n)
    return rec, Decoder(mem).build(rec, level - 1)


def live_map(mem):
    return [list(mem[MAP_BASE + r * MAP_W:MAP_BASE + (r + 1) * MAP_W]) for r in range(MAP_H)]


# --- output ------------------------------------------------------------------
def render(grid, color=False, hexmode=False):
    lines = []
    for r, row in enumerate(grid):
        if hexmode:
            cells = " ".join("%02X" % t for t in row)
        elif color:
            cells = "".join("\x1b[%sm%s\x1b[0m" % (tile_info(t)[1], tile_info(t)[0]) for t in row)
        else:
            cells = "".join(tile_info(t)[0] for t in row)
        lines.append("%2d %s" % (r, cells))
    return "\n".join(lines)


def header(rec, level):
    lv = level - 1
    return ("%s  level %d  |  need %d diamonds  value %d (extra %d)  time %d  |  "
            "amoeba/magic time %d" % (cave_name(rec[0]), level, rec[0x09 + lv], rec[0x02],
                                      rec[0x03], rec[0x0E + lv], rec[0x01]))


def digits(mem, addr, n):
    return "".join(str(mem[addr + i]) for i in range(n))


def legend(grids):
    seen = sorted({t for g in grids for row in g for t in row})
    out = ["legend:"]
    for t in seen:
        ch, _, desc = tile_info(t)
        out.append("  %s  $%02X  %s" % (ch, t, desc))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dump", help="64 KB RAM dump ($0000-$FFFF) of the running game")
    ap.add_argument("--cave", type=int, help="decode cave 1-20 (A-P = 1-16, intermissions 17-20)")
    ap.add_argument("--level", type=int, default=None, help="difficulty level 1-5 (default: level in dump, $5E)")
    ap.add_argument("--all", action="store_true", help="decode all 20 caves")
    ap.add_argument("--diff", action="store_true", help="compare decoded current cave with the live map")
    ap.add_argument("--color", action="store_true", help="ANSI colours")
    ap.add_argument("--hex", action="store_true", help="print tile IDs in hex")
    ap.add_argument("--legend", action="store_true", help="print the tile legend")
    a = ap.parse_args()

    mem = load_dump(a.dump)
    level = a.level if a.level else mem[0x5E] + 1
    if not 1 <= level <= 5:
        sys.exit("level must be 1-5")
    shown = []

    if a.all or a.cave:
        caves = range(1, CAVE_COUNT + 1) if a.all else [a.cave]
        for n in caves:
            if not 1 <= n <= CAVE_COUNT:
                sys.exit("cave must be 1-20")
            rec, grid = decode_cave(mem, n, level)
            print(header(rec, level))
            print(render(grid, a.color, a.hex))
            print()
            shown.append(grid)
    else:
        n = mem[0x5D]
        grid = live_map(mem)
        print("LIVE  %s  level %d  |  time %s  diamonds %s/%s  value %s  |  cave in $2400: %s"
              % (cave_name(n), mem[0x5E] + 1, digits(mem, 0xAB, 3), digits(mem, 0xB0, 2),
                 digits(mem, 0xB2, 2), digits(mem, 0x51, 3), cave_name(mem[0x2400])))
        print(render(grid, a.color, a.hex))
        shown.append(grid)
        if a.diff and 1 <= n <= CAVE_COUNT:
            _, dec = decode_cave(mem, n, mem[0x5E] + 1)
            print("\nDECODED (cave start state)")
            print(render(dec, a.color, a.hex))
            same = sum(1 for r in range(MAP_H) for c in range(MAP_W) if dec[r][c] == grid[r][c])
            print("\n%d / %d cells identical to the live map (%.1f%%)"
                  % (same, MAP_W * MAP_H, 100.0 * same / (MAP_W * MAP_H)))
            shown.append(dec)

    if a.legend:
        print(legend(shown))


if __name__ == "__main__":
    main()
