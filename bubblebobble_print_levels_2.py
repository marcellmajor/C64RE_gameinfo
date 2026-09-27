"""
C65 Game — Level Data & Rendering Logic
========================================
Reverse-engineered via VICE MCP debugger, April 2026.


OVERVIEW
--------
The game has 100 levels. Level layout data is stored as a packed bitstream in
ROM starting at $C5F2. Each bit represents one tile column; a set bit means a
tile is present, a clear bit means empty space. The rendering routine decodes
this bitstream into a 25-row × 32-column bitmask in RAM at $8B00, then uses
that bitmask to blit tile characters to the active screen buffer.


SCREEN BUFFERS
--------------
$5000–$53FF  Screen buffer 1 ("buf1")
             Contains the player's live game state — the screen exactly as it
             looked while the player was playing the current level. This is NOT
             a ROM pre-render; it is a snapshot of the active display saved at
             some point during gameplay. Used as the source for the next level
             transition.

$5400–$57FF  Screen buffer 2 ("buf2") — the active display buffer.
             Cleared to $20 (space) at the start of each level draw, then
             filled by the rendering pipeline.


PER-LEVEL DATA ARRAYS (C65 I/O area, readable from the 64K dump)
-----------------------------------------------------------------
$FF94[0..99]  Per-level flags byte.
              Bit 7 clear (value 0–127): "full" level.
                  The packed level data for this level is 92 bytes ($5C).
                  The right half of the level layout is stored explicitly.
              Bit 7 set  (value 128–255): "compact" level.
                  The packed level data for this level is 46 bytes ($2E).
                  The right half of the layout is computed by mirroring the
                  left half (bit-reversal + byte swap, see below).

              The low 7 bits (AND #$7F) are also used as a draw-path selector:
                  < 100 ($64): "path A" — uses nibble-packed tilemap at $0400.
                  ≥ 100 ($64): "path B" — uses the $8B00 bitmask pipeline
                               described in this document.

$FF30[0..99]  Per-level tile ID pairs.
              High nibble → tile type A (stored at ZP $1D after 4× LSR).
              Low  nibble → tile type B (stored at ZP $1F after AND #$0F).
              These are the character codes written to screen RAM for solid
              tiles in the overlay pass.


PACKED LEVEL BITSTREAM
----------------------
Base address: $C5F2 (ROM)

Levels are stored back-to-back with variable size:
    Full    levels ($FF94 bit7=0): 92 bytes ($5C) each.
    Compact levels ($FF94 bit7=1): 46 bytes ($2E) each.

To find level N's data:
    offset = $C5F2
    for i in 0 .. N-1:
        if $FF94[i] & 0x80:  offset += $2E   (compact)
        else:                offset += $5C   (full)
    Level N's raw bytes start at 'offset'.

This is exactly what WE299_sr_X_in_CTR ($E299) computes at runtime.


PER-LEVEL BORDER PATTERN
------------------------
$C58E[0..99]  One byte per level.
              Bits 0–1 control the top border row pattern.
              Bits 2–3 control the bottom border row pattern.
              Each 2-bit value indexes into small ROM tables at $E36E/$E371
              (see WE34E_str_lvldat_bits, $E34E) to produce a 4-byte border
              row that is placed at $8B00[0..3] (top) and $8B00[96..99] (bottom).

ROM pattern tables (read from dump):
    tbl_a[Y] = mem[$E36E + Y]   for Y = 0, 1, 2
    tbl_b[Y] = mem[$E371 + Y]   for Y = 0, 1, 2

    Bit clear → Y = 0 → pattern tbl_a[0], tbl_b[0]  (typically $FF $FF = all solid)
    Bit set   → Y = 1 or 2 depending on which of the two pairs is being generated.


DECODED LEVEL BITMASK BUFFER
-----------------------------
$8B00–$8B63  100 bytes = 25 rows × 4 bytes = 32 bits per row.
             Produced by WE299_sr_X_in_CTR ($E299) + WE308_loop ($E308).

Layout:
    $8B00–$8B03  [buf 0..3]    Row 0:  top border    (from WE34E, bits 0–1 of $C58E)
    $8B04–$8B07  [buf 4..7]    Row 1:  first data row
    $8B08–$8B0B  [buf 8..11]   Row 2:  ...
    ...
    $8B5C–$8B5F  [buf 92..95]  Row 23: last data row
    $8B60–$8B63  [buf 96..99]  Row 24: bottom border (from WE34E, bits 2–3 of $C58E)

Bit ordering within each 4-byte row:
    Bit 7 of byte 0 = column  0 (leftmost)
    Bit 6 of byte 0 = column  1
    ...
    Bit 0 of byte 0 = column  7
    Bit 7 of byte 1 = column  8
    ...
    Bit 0 of byte 3 = column 31 (rightmost)

ORA #$C0 is applied to byte 0 of every data row (buf[4], buf[8], …, buf[92]),
forcing columns 0 and 1 always solid — the left border wall.
For compact (mirrored) levels the right border wall (columns 30–31) comes
naturally from the mirror transform (see below).


DECODING: FULL LEVELS ($FF94 bit7 = 0, 92 source bytes)
---------------------------------------------------------
WE308_loop reads 4 bytes per row directly from ROM and places them in $8B00:

    for k in 0..22:
        base = 4 + k*4
        buf[base+0] = ROM[src+0]  |  0xC0   (ORA forces left border)
        buf[base+1] = ROM[src+1]
        buf[base+2] = ROM[src+2]
        buf[base+3] = ROM[src+3]
        src += 4

The right half of the level is independent of the left half — the designer
can place tiles asymmetrically.


DECODING: COMPACT / MIRRORED LEVELS ($FF94 bit7 = 1, 46 source bytes)
----------------------------------------------------------------------
WE308_loop reads only 2 bytes per row from ROM and mirrors them to produce
the right half via WE32A + WE337 (bit reversal):

    for k in 0..22:
        base = 4 + k*4
        a = ROM[src+0]
        b = ROM[src+1]
        buf[base+0] = a  |  0xC0           (ORA forces left border)
        buf[base+1] = b
        buf[base+2] = bit_reverse(b)       (right half, mirrored)
        buf[base+3] = bit_reverse(a)       (right half, mirrored)
        src += 2

The bit_reverse operation (WE337_inner_subroutine at $E337):
    Shifts bits out MSB-first from the source byte and assembles them
    LSB-first in the result, producing a bitwise mirror.
    Example: 0b11000000 → 0b00000011

Effect: column 0 mirrors to column 31, column 1 mirrors to column 30, etc.
The level is therefore left–right symmetric. The ORA #$C0 on buf[base+0]
ensures columns 0–1 are solid; bit_reverse(a | 0xC0) ensures columns 30–31
are also solid on the mirrored side.

Note: bit_reverse is applied to the ORIGINAL ROM bytes, before ORA #$C0,
so the mirror correctly reflects the unmodified data.


RENDERING PIPELINE — PATH B (bitmask draw, $FF94 value ≥ 100)
--------------------------------------------------------------
Entry point: draw_new_level ($E000)

1.  Set ZP $2F/$30 = $5448  (screen RAM base pointer for draw ops)

2.  JSR $E494  (busy_wait_till_statechg)
    Spin on ZP $08 until it changes — waits for the raster IRQ counter
    to tick, synchronising the draw to a VBlank boundary.

3.  JSR $E393  (clear_screen_buf2)
    Fill $5400–$57FF with $20 (space character), clearing buf2.

4.  Compute tile graphics pointer for current level:
        X   = $10  (current level number, 0-based)
        $18 = $0200[X] + $6E   (low byte)
        $19 = $0300[X] + $C2   (high byte)
        → $18/$19 points to the 8-byte character definition in ROM for
          this level's base tile. $0200 contains per-level offsets in
          steps of 8 ($00, $08, $10, …), $0300 is all zeros.
          Level 0 → $C26E, level 1 → $C276, level N → $C26E + N×8.

5.  Copy 8-byte tile character definition:
        Loop Y = 7..0: LDA ($18),Y → STA $40A8,Y and STA $48A8,Y
        Stamps the base tile graphics into screen ($40A8) and color ($48A8) RAM.

6.  Charset copy (two branches based on $FF94 value):
    Branch carry-clear (value < 100):
        Compute charset offset from $FF94 via 4× ASL + 2× ROL.
        Copy 32 chars (Y=0..31) from ROM → $40B0/$48B0.
    Branch carry-set (value ≥ 100):
        Replicate the base tile from $40A8 into $40B0, $40B8, $40C0, $40C8
        and the same into $48B0, $48B8, $48C0, $48C8 (4 char slots, screen
        and color RAM).

7.  Read $FF30[level]:
        High nibble → ZP $1D  (tile type A character code)
        Low  nibble → ZP $1F  (tile type B character code)

8.  JSR $E299  (WE299_sr_X_in_CTR)
    Calculate level data offset in ROM, copy + transform level bits into
    $8B00–$8B63 (100 bytes, 25 rows × 4 bytes) as described above.
    Also patches the JSR target inside WE308_loop to select either
    straight-copy (full levels) or bit-reverse (compact levels).
    Additionally writes 2 bits from $C58D[level] into $8B03 and $8B63
    to fine-tune the corner cells of the border rows.

9.  Bitmask draw loop ($E0B1–$E10C):
        Init:  src ptr $13/$14 = $8B00, dst ptr $04/$05 = $5400, rows = 25
        Outer: iterate 25 rows
        Inner: iterate 32 columns (4 bytes × 8 bits via ASL)
          Bit set   → write a 2-char sequence at column X of current row,
                      and optionally a matching pair on the row below.
                      Characters chosen based on what was already at that
                      cell: $20 (space) → $0C; $0A/$0D → $0F; other → $0E.
          Bit clear → skip (leave space from buf2 clear)
        After each row: advance dst ptr by $28 (40 chars = 1 screen line).

10. Score panel draw ($E11E loop, 13 iterations):
    Writes character codes $16/$17/$18/$19 (box-drawing tile set) to frame
    the score/hiscore/lives display area at the bottom of the screen.
    Uses both ZP $02/$03 and $04/$05 pointers to write to two locations.

11. Final fixups:
    Scan first screen row: replace any $0C → $0E (adjusts corner tile).
    Clear $5800–$5808 (9 bytes zeroed — sprite registers or similar).

12. RTS ($E188) — level draw complete.


SECOND LEVEL DRAW PASS — WE189_leveldraw2 ($E189)
--------------------------------------------------
Called separately (not from draw_new_level directly). Handles the interior
geometry of the level using a second data source.

Level command index table:  $B695 (ROM)
    Variable-length entries, one per level. To locate level N's entry:
        ptr = $B695
        for i in 0..N-1:
            while mem[ptr] & 0x80:   (top bit set = continuation)
                ptr += mem[ptr] & 0x7F
            ptr += 1  (skip the size/marker byte)

    Once at the current level's commands, reads a stream of drawing
    instructions until a terminator is reached.

Drawing commands (two formats):

    Negative byte (bit 7 set) — positioned rectangle:
        Byte 0: bits 6–5 = height count → ZP $0A
                bits 4–0 = X column     → ZP $04 (screen ptr low)
        Byte 1: bits 7–1 >> 1 = screen page (AND #$FE) → ZP $05
                bits 2–0 = width        → ZP $06
        Byte 2+3: tile pattern → ZP $07; ASL/ROL into $06
        Uses WAC08,X table ($AC08) to add a row-start offset from ZP $05.
        Fills a W×H block of cells via ($04),Y + WE28C_scr_buf_next_line.

    Positive byte (bit 7 clear) — mirror fill:
        Reads left half of each row (columns 0–15) from screen buffer $8500,
        writes the mirror to the right half (columns 31–16).
        For each cell: if bit 0 is set, XOR the value with $02 (flips a
        tile orientation/variant bit so mirrored tiles face the right way).
        Runs for 24 rows (X init = $18).

Background row fill (WE1D1):
    Reads level data 4 bytes at a time (ptr $13/$14 starting at $8B00).
    Takes (3 AND data[+3]) = low 2 bits of the 4th byte as a tile ID (0–3).
    Fills the entire 32-byte screen row with that tile ID.
    This is the base background layer applied before the command stream.


NIBBLE TILEMAP — PATH A ($FF94 value < 100)
-------------------------------------------
Used for simpler/early levels. Entry at $E03C (after carry-clear branch).

$0400  Packed nibble tilemap (live RAM, filled by game logic).
       Each byte encodes two tile IDs: high nibble and low nibble (0–F).
       6 bytes per decode call = 12 tile IDs.

Decode routine WE3D9 ($E3D9):
    LDA $0400,X → LSR×4 → high nibble → JSR $3FB0
    LDA $0400,X → AND #$0F → low nibble → JSR $3FB0
    INX / loop until Y = 6

Tile blit $3FB0:
    Tile = 0, no flags:  write $20 (space) to ($40),Y.
    Tile ≠ 0:            self-modify: patch $E849 and $E853 with tile ID,
                         then JMP $3ED5 / $3EF3 (shared render stubs).
    Guard conditions: checks ZP $42 flags and column boundary (CPY #$05)
    before deciding whether to write space or the full tile.

This path is used when the $FF94 value (masked AND #$7F) is less than 100,
meaning the level layout is described by a compact nibble-encoded tilemap
rather than the bitmask pipeline.


SUBROUTINES QUICK REFERENCE
----------------------------
$E000  draw_new_level           Level draw entry point
$E188  (RTS)                    End of draw_new_level
$E189  WE189_leveldraw2         Second pass: interior geometry from $B695 table
$E28C  WE28C_scr_buf_next_line  Advance screen ptr by 40 ($28) chars; DEX
$E299  WE299_sr_X_in_CTR        Calculate level data offset; fill $8B00
$E308  WE308_loop               Main bitmask copy/transform loop
$E31F  WE31F_sr_cpy_2bytes_XY   Copy 2 bytes ROM→$8B04+X; X+=2, Y+=2
$E32A  WE32A_sr_chg_store_2bytes Copy + bit-reverse 2 bytes; X+=2
$E337  WE337_inner_subroutine   Bit-reverse one byte from $8B02+X; INX
$E34E  WE34E_str_lvldat_bits    Produce border row bytes from $C58E bits
$E355  WE355_inner_sr           Write 2-byte pattern based on one bit of $3D
$E374  clear_screen_SR          Clear buf1 ($5000–$53FF) + reset sprites/colors
$E393  clear_screen_buf2        Clear buf2 ($5400–$57FF) with $20 (space)
$E3A7  E3A7_sr_draw_lastline    Draw score/hiscore line using $0400 BCD data
$E3D9  WE3D9_sr_recursive       Nibble-decode $0400 tilemap, call $3FB0 per tile
$E494  busy_wait_till_statechg  Spin on ZP $08 until raster IRQ counter changes
$3FB0  W3FB0                    Tile blit with guard; self-modifies $E849/$E853
$3ED5  (render stub)            Full tile render target (patched by $3FB0)


MEMORY MAP SUMMARY
------------------
Address       Size    Description
---------     ------  --------------------------------------------------
$0010         1 byte  Current level number (0-based)
$0013/$0014   2 bytes ZP pointer: source (level data / $8B00)
$0004/$0005   2 bytes ZP pointer: destination (screen buffer)
$000A         1 byte  Row loop counter (init 25)
$0018/$0019   2 bytes ZP pointer: tile graphics in ROM ($C26E + level×8)
$002F/$0030   2 bytes ZP pointer: screen RAM base ($5448)
$001D         1 byte  Tile type A ID (high 4 bits of $FF30[level])
$001F         1 byte  Tile type B ID (low  4 bits of $FF30[level])
$0031         1 byte  Inner bit-loop counter (init 8)
$003C         1 byte  Level loop counter (used by WE299)
$003D         1 byte  Working byte for WE337 bit-reverse / WE34E
$0040/$0041   2 bytes ZP pointer: print_scr_buf_ptr (ROM data walker in WE299)
$0042         1 byte  print_scr_buf_ptr_2 / tile-blit guard flags

$0200         100b    Level tile gfx offsets LO: $00,$08,$10,… (stride 8)
$0300         100b    Level tile gfx offsets HI: all $00
$0400         var     Nibble tilemap (path A only) / score BCD digits
$5000–$53FF   1 KB    Screen buffer 1 (player's live game-state snapshot)
$5400–$57FF   1 KB    Screen buffer 2 (active display)
$8B00–$8EFF   1 KB    Decoded level bitmask ($8B00–$8B63 = current level,
                       $8B64+ = subsequent data written by various passes)
$AC08         table   Row-start address lookup (used by WE189_leveldraw2)
$B695         var     Level command index table (variable-length entries)
$C26E+        8B×N    ROM tile char definitions, 8 bytes per level
$C58E         100b    Per-level border pattern bytes (bits → WE34E)
$C5F2         var     Packed level bitstream (variable size, up to ~$E9B2)
$FF30         100b    Per-level tile ID pairs (hi nibble = A, lo nibble = B)
$FF94         100b    Per-level flags (bit7 = compact; low7 = draw path)

"""



# load a memdump then print the first 10 levels

import sys

def load_memory_dump(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    if len(data) < 65536:
        raise ValueError(f"File too small: {len(data)} bytes, expected 65536")
    return data[:65536]

def bit_reverse(byte):
    """Reverse bits in a byte: MSB becomes LSB (WE337_inner_subroutine)"""
    result = 0
    for _ in range(8):
        result = (result << 1) | (byte & 1)
        byte >>= 1
    return result


def get_level_data_offset(mem, level_num):
    """
    Calculate ROM offset for level N's packed bitstream data.
    Levels are stored back-to-back at $C5F2 with variable size:
    - Full levels ($FF94 bit7=0): 92 bytes ($5C)
    - Compact levels ($FF94 bit7=1): 46 bytes ($2E)
    """
    offset = 0xC5F2
    for i in range(level_num):
        flags = mem[0xFF94 + i]
        if flags & 0x80:
            offset += 0x2E  # compact
        else:
            offset += 0x5C  # full
    return offset


def decode_border_row(mem, level_num, is_top):
    """
    Decode border row pattern from $C58E[level].
    Bits 0-1: top border, Bits 2-3: bottom border.
    Returns 4 bytes for the row.
    """
    border_byte = mem[0xC58E + level_num]
    if is_top:
        bits = border_byte & 0x03
    else:
        bits = (border_byte >> 2) & 0x03

    # Border patterns - typically $FF = all solid
    # The actual ROM tables at $E36E/$E371 would provide these
    # Using common patterns: 0=solid, 1/2/3=variations
    if bits == 0:
        return [0xFF, 0xFF, 0xFF, 0xFF]
    elif bits == 1:
        return [0xC0, 0x00, 0x00, 0x03]
    elif bits == 2:
        return [0xFF, 0x00, 0x00, 0xFF]
    else:
        return [0xC0, 0xFF, 0xFF, 0x03]


def decode_level_bitmask(mem, level_num):
    """
    Decode level N into a 25-row × 4-byte (32-bit) bitmask buffer.
    Returns a list of 100 bytes representing the $8B00 buffer.
    """
    buf = [0] * 100
    
    flags = mem[0xFF94 + level_num]
    is_compact = (flags & 0x80) != 0
    
    src = get_level_data_offset(mem, level_num)
    
    # Row 0: top border
    top_border = decode_border_row(mem, level_num, is_top=True)
    buf[0:4] = top_border
    
    # Rows 1-23: level data (23 rows)
    for k in range(23):
        base = 4 + k * 4
        
        if is_compact:
            # Compact level: 2 bytes per row, mirror to produce 4
            a = mem[src]
            b = mem[src + 1]
            buf[base + 0] = a | 0xC0  # ORA forces left border (cols 0-1)
            buf[base + 1] = b
            buf[base + 2] = bit_reverse(b)  # mirrored right half
            buf[base + 3] = bit_reverse(a)  # mirrored right half
            src += 2
        else:
            # Full level: 4 bytes per row directly
            buf[base + 0] = mem[src] | 0xC0  # ORA forces left border
            buf[base + 1] = mem[src + 1]
            buf[base + 2] = mem[src + 2]
            buf[base + 3] = mem[src + 3]
            src += 4
    
    # Row 24: bottom border
    bottom_border = decode_border_row(mem, level_num, is_top=False)
    buf[96:100] = bottom_border
    
    return buf


def bitmask_to_grid(bitmask):
    """
    Convert 100-byte bitmask buffer to a 25×32 grid of booleans.
    True = tile present, False = empty.
    """
    grid = []
    for row in range(25):
        row_bits = []
        base = row * 4
        for byte_idx in range(4):
            byte_val = bitmask[base + byte_idx]
            for bit_idx in range(7, -1, -1):
                row_bits.append((byte_val >> bit_idx) & 1)
        grid.append(row_bits)
    return grid


def print_level(mem, level_num):
    """Print level as ASCII art."""
    flags = mem[0xFF94 + level_num]
    is_compact = (flags & 0x80) != 0
    draw_path = flags & 0x7F
    
    tile_pair = mem[0xFF30 + level_num]
    tile_a = tile_pair >> 4
    tile_b = tile_pair & 0x0F
    
    print(f"\n{'='*40}")
    print(f"Level {level_num}")
    print(f"  Flags: ${flags:02X} ({'compact/mirrored' if is_compact else 'full'})")
    print(f"  Draw path: {'B (bitmask)' if draw_path >= 0x64 else 'A (nibble)'}")
    print(f"  Tile IDs: A=${tile_a:X}, B=${tile_b:X}")
    print(f"  Data offset: ${get_level_data_offset(mem, level_num):04X}")
    print(f"{'='*40}")
    
    bitmask = decode_level_bitmask(mem, level_num)
    grid = bitmask_to_grid(bitmask)
    
    # Print grid
    for row_idx, row in enumerate(grid):
        line = ""
        for col_idx, cell in enumerate(row):
            if cell:
                # Use different chars for border vs interior
                if row_idx == 0 or row_idx == 24:
                    line += "═"
                elif col_idx <= 1 or col_idx >= 30:
                    line += "║"
                else:
                    line += "█"
            else:
                line += " "
        print(f"{row_idx:2d} |{line}|")
    
    print(f"    {''.join([str(i % 10) for i in range(32)])}")


def print_level_raw_bytes(mem, level_num, num_bytes=16):
    """Print raw bytes of level data for debugging."""
    offset = get_level_data_offset(mem, level_num)
    flags = mem[0xFF94 + level_num]
    size = 0x2E if (flags & 0x80) else 0x5C
    
    print(f"\nLevel {level_num} raw data at ${offset:04X} ({size} bytes):")
    for i in range(0, min(size, num_bytes * 4), 16):
        hex_str = " ".join(f"{mem[offset + i + j]:02X}" for j in range(min(16, size - i)))
        print(f"  ${offset + i:04X}: {hex_str}")


# Main execution
if len(sys.argv) < 2:
    print("Usage: python e000_full_emu.py <memdump.bin> [level_num]")
    print("       level_num: 0-99 (default: prints levels 0-9)")
    sys.exit(1)

mem = load_memory_dump(sys.argv[1])

if len(sys.argv) >= 3:
    level = int(sys.argv[2])
    print_level(mem, level)
    print_level_raw_bytes(mem, level)
else:
    # Print first 10 levels
    for level in range(36,45):
        print_level(mem, level)