import sys

def load_memory_dump(filename):
    """Load a 64KB C64 memory image ($0000-$FFFF)."""
    with open(filename, "rb") as f:
        data = f.read(0x10000)
    if len(data) != 0x10000:
        raise ValueError("File must be exactly 65536 bytes")
    return bytearray(data)


def get_level_offset(mem, level):
    """Calculate offset into the $C5F2 block for a given level (0-based)."""
    if level == 0:
        return 0
    offset = 0
    for i in range(level):
        flag = mem[0xFF94 + i]
        size = 0x2E if (flag & 0x80) != 0 else 0x5C   # sign bit test from ASM
        offset += size
    return offset


def extract_raw_level(mem, level):
    """Return the raw encoded bytes for a level."""
    base = 0xC5F2
    offset = get_level_offset(mem, level)
    flag = mem[0xFF94 + level]
    size = 0x2E if (flag & 0x80) != 0 else 0x5C
    return mem[base + offset : base + offset + size]


def print_level_hex(mem, level, max_bytes=96):
    """Print a simple hex dump of a level's encoded data."""
    data = extract_raw_level(mem, level)
    print(f"Level {level:2d} (offset 0x{get_level_offset(mem, level):04X}, "
          f"size 0x{len(data):02X}):")
    for i in range(0, min(len(data), max_bytes), 16):
        chunk = data[i:i+16]
        hex_str = ' '.join(f'{b:02X}' for b in chunk)
        print(f"  {i:04X}: {hex_str}")
    if len(data) > max_bytes:
        print("  ... (truncated)")
    print()


def simple_text_render_example(mem, level):
    """Render level as a 25×32 ASCII bitmap grid.
    Full levels (0x5C bytes) store 23 rows × 32 cols (4 bytes/row).
    Half levels (0x2E bytes) store 23 rows × 16 cols (2 bytes/row), mirrored.
    Rows 0 and 24 (top/bottom borders) are always solid."""
    data = extract_raw_level(mem, level)
    is_half = (len(data) == 0x2E)
    bytes_per_row = 2 if is_half else 4
    num_stored_rows = len(data) // bytes_per_row
    flag = mem[0xFF94 + level]
    print(f"  ({len(data)} bytes, flag=${flag:02X}, "
          f"{'half→mirrored' if is_half else 'full'} width)")

    border = '*' * 32

    def render_row(row_idx):
        line = ''
        for col_byte in range(bytes_per_row):
            byte = data[row_idx * bytes_per_row + col_byte]
            for bit in range(7, -1, -1):  # MSB first
                line += '*' if (byte >> bit) & 1 else ' '
        if is_half:
            # Mirror: reverse the 16-char left half to make right half
            line = line + line[::-1]
        # Force solid left and right border columns
        return '*' + line[1:-1] + '*'

    print(f"  {border}")  # Row 0: solid top border
    for row in range(num_stored_rows):
        print(f"  {render_row(row)}")
    print(f"  {border}")  # Row 24: solid bottom border
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python decode_c64_levels.py <memory_dump.bin>")
        sys.exit(1)

    mem = load_memory_dump(sys.argv[1])

    # Show the two metadata tables (first 0xA0 bytes)
    print("Level array 1 ($FF30):", ' '.join(f'{b:02X}' for b in mem[0xFF30:0xFF30+0xA0]))
    print("Level array 2 ($FF94):", ' '.join(f'{b:02X}' for b in mem[0xFF94:0xFF94+0xA0]))
    print()

    # Decode and print first 8 levels as an example
    for lvl in range(13,14):          # change to range(100) for all levels
        print_level_hex(mem, lvl)
        simple_text_render_example(mem, lvl)
