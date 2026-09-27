#!/usr/bin/env python3
"""Draw Boulder Dash (C64) caves as PNG files from a 64 KB VICE memory dump.

Usage:  bd_cave_png.py DUMP

Writes into the current folder:
  bd_live_<cave>.png                  the cave map as it is in RAM right now
  bd_cave<NN>_<name>_level<L>.png     all 20 caves rebuilt at cave-start state,
                                      at the difficulty level found in the dump

Graphics come from the dump itself, exactly as the game draws them:
  tile T -> 2x2 characters starting at $5F28[T]: c, c+1 / c+16, c+17 ($7018)
  charset at $3000, multicolour characters
  colours: background $D021, multicolour 1/2 = cave bytes $13/$14 ($D022/$D023),
           character colour = cave byte $15 (written to colour RAM by $6E7B)
Scale: one C64 pixel = 4x4 image pixels (a multicolour pixel = 8x4).
Caves are rebuilt like the game does at cave start ($8AB9): cave record copy
($8226), random fill ($8043, RNG $7085), steel border ($85A7), object list ($8518).
No third-party packages needed.
"""

import os
import struct
import sys
import zlib

SCALE = 4

MAP_BASE = 0x0850
MAP_W, MAP_H = 40, 22
DECODE_BASE = 0x0800
ROW_TABLE = 0x8406
DIR_TABLE = 0x8454
CAVE_OFFSETS = 0x5804
CAVE_DATA = 0x582E
RECORD_LEN = 240
CAVE_COUNT = 20
TILE_CHARS = 0x5F28
CHARSET = 0x3000

# VICE "pepto-pal" palette
PALETTE = [
    (0x00, 0x00, 0x00), (0xFF, 0xFF, 0xFF), (0x68, 0x37, 0x2B), (0x70, 0xA4, 0xB2),
    (0x6F, 0x3D, 0x86), (0x58, 0x8D, 0x43), (0x35, 0x28, 0x79), (0xB8, 0xC7, 0x6F),
    (0x6F, 0x4F, 0x25), (0x43, 0x39, 0x00), (0x9A, 0x67, 0x59), (0x44, 0x44, 0x44),
    (0x6C, 0x6C, 0x6C), (0x9A, 0xD2, 0x84), (0x6C, 0x5E, 0xB5), (0x95, 0x95, 0x95),
]


def cave_name(n):
    if 1 <= n <= 16:
        return "Cave_" + chr(ord("A") + n - 1)
    if 17 <= n <= 20:
        return "Intermission_%d" % (n - 16)
    return "cave%d" % n


def word(mem, addr):
    return mem[addr] | (mem[addr + 1] << 8)


# --- cave construction (same algorithm as the game) ---------------------------
def next_random(s1, s2):
    """$7085: s1 = $3F, s2 = $3E."""
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
    return r & 0xFF, s2


def cave_record(mem, n):
    start = CAVE_DATA + word(mem, CAVE_OFFSETS + 2 * n)
    return bytes(mem[(start + i) & 0xFFFF] for i in range(RECORD_LEN))


class Decoder:
    def __init__(self, mem):
        self.mem = mem
        self.buf = bytearray(MAP_W * (MAP_H + 2))
        self.dirs = []
        for i in range(8):
            d = word(mem, DIR_TABLE + 2 * i)
            self.dirs.append(d - 0x10000 if d & 0x8000 else d)

    def addr(self, x, y):
        return (word(self.mem, ROW_TABLE + 2 * y) + x - DECODE_BASE) & 0xFFFF

    def put(self, a, tile):
        if 0 <= a < len(self.buf):
            self.buf[a] = tile

    def line_from(self, a, count, direction, tile):
        c = count & 0xFF
        delta = self.dirs[direction & 7]
        while True:
            c = (c - 1) & 0xFF
            if c & 0x80:
                return a
            self.put(a, tile)
            a = (a + delta) & 0xFFFF

    def fill_rect(self, x, y, w, h, tile):
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
        a = self.addr(x, y)
        a = self.line_from(a, w - 1, 2, tile)
        a = self.line_from(a, h - 1, 4, tile)
        a = self.line_from(a, w - 1, 6, tile)
        self.line_from(a, h - 1, 0, tile)

    def build(self, rec, level_index):
        s2, s1 = rec[0x04 + level_index], 0
        objs, probs = rec[0x18:0x1C], rec[0x1C:0x20]
        for row in range(1, MAP_H):
            for col in range(MAP_W):
                s1, s2 = next_random(s1, s2)
                tile = 0x01
                for i in range(4):
                    if s1 < probs[i]:
                        tile = objs[i]
                self.buf[(row + 2) * MAP_W + col] = tile
        self.outline(0, 2, 40, 22, 0x07)
        y = 0x20
        while y < RECORD_LEN:
            code = rec[y]
            if code == 0xFF:
                break
            tile = code & 0x3F
            x0, y0, w, h, inner = [rec[y + k] if y + k < RECORD_LEN else 0 for k in range(1, 6)]
            kind = code & 0xC0
            if kind == 0x00:
                self.put(self.addr(x0, y0), tile)
                y += 3
            elif kind == 0x40:
                self.line_from(self.addr(x0, y0), w, h, tile)
                y += 5
            elif kind == 0x80:
                self.fill_rect(x0, y0, w, h, tile)
                self.fill_rect(x0 + 1, y0 + 1, w - 2, h - 2, inner)
                y += 6
            else:
                self.outline(x0, y0, w, h, tile)
                y += 5
        return [list(self.buf[(r + 2) * MAP_W:(r + 3) * MAP_W]) for r in range(MAP_H)]


# --- graphics ---------------------------------------------------------------
def char_rows(mem, code, colors):
    """8 rows of 8 palette indices for one character."""
    bg, mc1, mc2, cram = colors
    fg = cram & 7
    rows = []
    for line in range(8):
        b = mem[CHARSET + code * 8 + line]
        px = []
        if cram & 8:                          # multicolour: 4 double-wide pixels
            for shift in (6, 4, 2, 0):
                pair = (b >> shift) & 3
                col = (bg, mc1, mc2, fg)[pair]
                px += [col, col]
        else:                                 # hires
            for bit in range(7, -1, -1):
                px.append(fg if (b >> bit) & 1 else bg)
        rows.append(px)
    return rows


def render(mem, grid, colors):
    """Return a list of image rows (palette indices), already scaled."""
    cache = {}
    image = []
    for trow in grid:
        tile_lines = [[] for _ in range(16)]
        for t in trow:
            if t not in cache:
                c = mem[TILE_CHARS + (t & 0x3F)]
                tl, tr = char_rows(mem, c, colors), char_rows(mem, (c + 1) & 0xFF, colors)
                bl, br = char_rows(mem, (c + 16) & 0xFF, colors), char_rows(mem, (c + 17) & 0xFF, colors)
                cache[t] = [tl[i] + tr[i] for i in range(8)] + [bl[i] + br[i] for i in range(8)]
            for i, line in enumerate(cache[t]):
                tile_lines[i].extend(line)
        for line in tile_lines:
            scaled = bytes(p for p in line for _ in range(SCALE))
            image.extend([scaled] * SCALE)
    return image


def write_png(path, rows):
    height, width = len(rows), len(rows[0])

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + r for r in rows)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 3, 0, 0, 0))
    png += chunk(b"PLTE", b"".join(bytes(c) for c in PALETTE))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: %s MEMDUMP" % os.path.basename(sys.argv[0]))
    mem = open(sys.argv[1], "rb").read()
    if len(mem) != 0x10000:
        sys.exit("expected a 65536-byte RAM dump, got %d bytes" % len(mem))

    bg = mem[0xD021] & 0x0F               # background from the dump's VIC registers
    level_index = min(mem[0x5E], 4)
    written = []

    # current cave, as it is in RAM
    cur = mem[0x2400:0x2416]
    grid = [list(mem[MAP_BASE + r * MAP_W:MAP_BASE + (r + 1) * MAP_W]) for r in range(MAP_H)]
    name = "bd_live_%s.png" % cave_name(mem[0x5D])
    write_png(name, render(mem, grid, (bg, cur[0x13] & 0x0F, cur[0x14] & 0x0F, cur[0x15] & 0x0F)))
    written.append(name)

    # all caves, rebuilt at cave start
    for n in range(1, CAVE_COUNT + 1):
        rec = cave_record(mem, n)
        grid = Decoder(mem).build(rec, level_index)
        colors = (bg, rec[0x13] & 0x0F, rec[0x14] & 0x0F, rec[0x15] & 0x0F)
        name = "bd_cave%02d_%s_level%d.png" % (n, cave_name(n), level_index + 1)
        write_png(name, render(mem, grid, colors))
        written.append(name)

    for name in written:
        print(os.path.abspath(name))


if __name__ == "__main__":
    main()
