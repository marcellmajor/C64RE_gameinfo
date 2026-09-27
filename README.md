# C64 game reverse-engineering notes

Working notes and small tools from reverse-engineering Commodore 64 games with VICE (live memory and disassembly) and static disassembly. Addresses are hexadecimal. Findings are only as strong as the session that produced them; each game section says what was confirmed and what was left open.

## Games

### Boulder Dash

Confirmed from live VICE reads and `asm_dir/boulderdash_unique.asm` on 2026-09-26. Behaviour comes from reading code and one-off memory reads. It was not checked with breakpoints or by stepping.

The playfield is a 40×22 tile map at `$0850`–`$0BBF` (`address = $0850 + row*40 + col`). Game logic scans that whole map; the screen matrix is separate, at `$0C00`. Each tile ID has a handler in the table at `$5F68`. The scan pointer `$32`/`$33` starts at `$084F`, and handlers index neighbours with `($32),Y` (`$29` current, `$01` up, `$28` left, `$2A` right, `$51` down).

Tiles seen live: `$00` empty, `$01` dirt, `$02` wall, `$07` steel border (explosions never overwrite it), `$10` boulder, `$14` diamond, `$30`–`$33` butterfly, `$38` player, `$3A` amoeba. Fireflies are `$08`–`$0B` (handler `$7172`: explode on contact, else turn left, else straight, else turn right). Butterflies are the mirror of that at `$7245` and leave a diamond when they explode.

Amoeba (`$7368`): a count of 200 or more turns every amoeba tile into a boulder; `$8C = 0` (suffocated) turns them into diamonds. Growth uses `rnd & $9A` (`$7F` slow, `$0F` fast) and writes `$3B` onto empty or dirt. Suffocation is detected once per pass at `$813B`.

The two Python scripts rebuild caves the way cave-start does (`$8AB9`: record copy, random fill, steel border, object list) from a 64 KB memory dump. They do not need third-party packages. Cave graphics in the PNG script come from the dump (2×2 multicolour chars, charset at `$3000`).

```
python3 boulderdash_cave_render.py DUMP
python3 boulderdash_cave_render.py DUMP --cave 13 --level 1
python3 boulderdash_cave_render.py DUMP --all
python3 bouldrdash_cave_png.py DUMP
```

### Petch

A Pengo-style maze game. Enemies chase only some of the time. Diamond ice awards 800 points. Walking into a border wall with the kick action stuns enemies that are on that same edge.

**Enemy AI** (`petch_enemy_ai.txt`). Update is `$4880`, called from the main loop at `$1034`. Up to four enemies. A decision happens only when the sprite is grid-aligned. Chase frequency is `$0D7F`, set at level start to `(level * 8) + $20`. Each frame the jiffy-clock low byte is compared with that threshold: below it, the enemy seeks the player on one axis (X or Y, chosen from the clock high byte); otherwise it keeps its current direction (`$0D84`). There is no pathfinding. If the chosen cell is blocked, it coasts. From level 4, enemy state 2/3 may pass cracking ice (`$84`/`$86`/`$88`/`$8B`) that state 1 cannot. Per-frame chase chance is about 16% on level 1 and about 38% on level 8; past about level 20 the 8-bit threshold wraps.

**Diamond destruction** (`petch_diamond_destruction.txt`). Clearing a normal ice block at `$39FA` always falls into `$6040`, which matches the erased screen pointer against four diamond slots (`$0D00`–`$0D03` low, `$0D04`–`$0D07` high minus `$D4`). A hit with `$0D10,X` still alive arms the animation at `$5E0D`. The per-frame machine at `$42CB` cycles sprite 5 (`$3A` → `$3B` → `$8F` → `$DF`) and on the last step calls `$439F`, which adds `8 * 100 = 800` via `$5300`.

**Freeze on wall** (`petch_freeze_on_wall.txt`). `$1E00` tests the facing tile for wall char `$88` (and `$82`/`$86`) and jumps to a per-direction stun routine: up `$5800`, down `$5837`, left `$586E`, right `$58AD`. Those mark an enemy state `$09` and a 48-frame timer at `$0DB8,X` only if that enemy sprite is on the same screen edge. Upstream, `$1903` uses bit 4 of `$0FFF` to split kick (wall stun) from a normal push. The notes did not find the call into `$1903`, so whether that gate runs in this build was left for a breakpoint on `$5800`–`$58FF`.

`petch_sample_report.md` is an earlier agent transcript (2026-05-16) about the red-ice animation and the 800-point award. Its own critic marked the score path as unproven. The diamond note above is the later trace that locates `$439F`.

### Vultures

Early C64 shooter (player at the bottom, enemies at the top). Code sits in RAM at `$0073`–`$20ED`. Analysis is from OGhidra sessions (gemma4 and grok-4). Where they disagreed, the grok-4 reading was kept: lives are zero-page `$8B` (init 3), not sprite register `$D009`, and `$0C7A` is score display math. There is no dedicated PRNG; enemy left/right uses the raster register `$D012`, and `$66` is only a sound-pitch counter.

Screen RAM is the enemy list. Sleeping enemies are 2×2 characters `$40`–`$43`. `$0D17` scans for `$40`, moves them, and counts them into `$3B`. `$3B == 0` is level clear (`$1148` increments `$8C`). The player bullet walks a pointer at `$57`/`$58`; a hit on `$42`/`$43` explodes the block to spaces and adds BCD score at `$53`–`$55`.

The vulture is sprite 4 (`$D008`/`$D009`), spawned by `$0E3F` and moved by `$0EDF` (signed directions `$5A` vertical, `$5B` horizontal). It drops sprite 5 when it lines up with the player. Sprite collision `$D01F` bit 4 kills the player: `$1052` animates, `$113E` decrements `$8B`, and zero lives restarts. The lives digit at `$04EC` shows reserve lives (`$8B - 1`), so 3 lives displays as `2`.

Sound is computed, not table-driven. `$1320` is a one-shot SID voice (pitch in A). `$1392` sweeps voice 2 from `$66` every 3 frames. The IRQ vector stays at the KERNAL default `$EA31`. BASIC is switched off; KERNAL is used only for `GETIN` (`$FFE4`) and scan/IRQ setup (`$FF9F`).

The summary also describes a title-screen viewer (`vultures_viewer.py`) and a charset dump. That viewer is not in this folder. A later note in the same file says a title-screen dump had hardware sprites off (`$D015 = 0`) and the bird drawn as charset characters; the routine list above still describes the in-game sprite path.

### Bubble Bobble

Level layout and the draw pipeline, recovered with the VICE debugger in April 2026. The notes file header still says "C65 Game"; the game is Bubble Bobble. Per-level tables are read from `$FF30` and `$FF94` in a 64 KB dump.

Layout bits are packed at `$C5F2`, one bit per column, back to back:

| Kind | `$FF94` bit 7 | Size | Layout |
| --- | --- | --- | --- |
| Full | clear | 92 bytes (`$5C`) | 23 data rows × 4 bytes, right half stored |
| Compact | set | 46 bytes (`$2E`) | 23 data rows × 2 bytes, right half is a bit-reverse mirror |

`$FF94` bits 0–6 also pick the draw path: below 100 uses a nibble tilemap at `$0400` (path A, `$E3D9`); 100 and above uses the `$8B00` bitmask (path B, `$E000`). Decoded form is 25×32 bits at `$8B00`–`$8B63` (top and bottom borders from `$C58E`, left wall forced with `ORA #$C0`). Screen buffer 2 (`$5400`–`$57FF`) is the active display. Buffer 1 (`$5000`–`$53FF`) is a live snapshot, not a ROM picture. A second pass at `$E189` draws interior geometry from a variable-length command table at `$B695`.

Both scripts take a 65536-byte dump. `bubblebobble_print_levels.py` prints hex and a `*`/` ` grid (the `__main__` block is hard-wired to level 13). `bubblebobble_print_levels_2.py` mirrors compact levels with the same bit-reverse as `$E337` and prints levels 36–44 unless a level number is passed.

```
python3 bubblebobble_print_levels.py DUMP
python3 bubblebobble_print_levels_2.py DUMP [level]
```

### Captain Blood

Validated reference from 2026-09-27 for the RAM image `memdump_dir/landed_blood.bin`: the ship is on planet 0 and alien file 0 is loaded. The file tags each claim as code, executed in an isolated 6502 emulator, inferred gameplay, a story reading, or still open. The probes reproduced the file-0 decoder, all 187 pattern matches, both passwords, and all four coordinate replies. A read-only VICE check of `$4C00`–`$4DFF` matched the image. They did not emulate interrupts or a full playthrough, and only alien file 0 is decoded.

In that conversation screen, `$01 = $35` (BASIC and KERNAL banked out, I/O visible), the VIC bank is `$C000`, the screen matrix is `$C000`, and the bitmap is `$E000`. Sixty-four planet entries keep home coordinates at `$0600`/`$0640` and current coordinates at `$0680`/`$06C0`. Y bit 7 is a visited or departure marker; rendering masks it with `$7F`. Game flags are a bitset at `$9210` (`address = $9210 + floor(n/8)`, mask `1 << (n mod 8)`). The loaded alien file starts at `$6100`. File 0's script is `$621C`–`$67A0` and ends with `$FF`. Vocabulary strings, IDs 0–122, are at `$9418`. The player's eight icons are at `$5C80` (drawn on the right); the alien reply icons are at `$5C90` (drawn on the left).

Speech is pictogram words. A mouth click (`$4948`; screen hotspot x=144..175, y=107..126) walks the script from the start on a new phrase (`$E5 = 0`) or resumes the same phrase when `$E5` is nonzero. A useful line is often several mouth clicks after the phrase that triggered it. Record types in file 0 are PATTERN (`$00`), ACTION (`$40`), and CONDITION (`$80`). A COORDINATE token `[3,a,b]` prints a home position when `a` is nonzero (`$0600`/`$0640`, index `a-1`) and a current position otherwise. All four tokens in file 0 use home positions.

File 0 serves planet indices 0–3. Small Yoko (index 0, called BOW-BOW) accepts BLOOD, then a help trigger such as PLANET. Away from home he reveals home index 12, (140, 33) in this save. The planet-1 claimant's password is RENDEZ-VOUS 6 7, which reveals duplicate home index 60. Maxon's last stage accepts YOKO NOT DEAD IDEA 3 4 9 and reveals home indices 1 and 61. The ship-menu path `$0A76` calls removal at `$47E5`; alien index 60 or 61 in `$EA` increments `$FD`, and `$FD = 2` enters the end sequence at `$0A94`. Transport button sequences and the other alien files are still open. The planet-12 clue leads to file 3, which this reference does not contain.

## Files

| File | Game | What it is |
| --- | --- | --- |
| `boulderdash_memory_map_confirmed.txt` | Boulder Dash | Confirmed RAM map, tile handlers, zero page, amoeba and explosion rules. |
| `boulderdash_cave_render.py` | Boulder Dash | Console renderer. Live map at `$0850`, or rebuild caves 1–20 at a chosen difficulty from a 64 KB dump. |
| `bouldrdash_cave_png.py` | Boulder Dash | Same cave rebuild, written as PNGs (live map plus all 20 caves). Filename is missing the `e` in “boulder”. |
| `petch_enemy_ai.txt` | Petch | Probabilistic chase: threshold `$0D7F`, axis coin-flip, passability checks, coast fallback. |
| `petch_diamond_destruction.txt` | Petch | Ice clear → diamond-slot match at `$6040` → animation → +800 at `$439F`. |
| `petch_freeze_on_wall.txt` | Petch | Wall-kick stun at `$5800` / `$5837` / `$586E` / `$58AD`. Call into the `$1903` gate was not traced. |
| `petch_sample_report.md` | Petch | Agent report (May 2026) on the red-ice animation. Score award left open; see the diamond note. |
| `vultures_summary.txt` | Vultures | Memory map, loop, enemies, vulture, lives, and SID use. Includes the gemma4 / grok-4 disagreement. |
| `vultures_c64_disassembly.txt` | Vultures | Annotated disassembly of the same binary (`$0073` through the title screen). |
| `bubblebobble_level_data_notes.txt` | Bubble Bobble | 100-level format: `$C5F2` packing, `$8B00` decode, path A vs path B, subroutine list. |
| `bubblebobble_print_levels.py` | Bubble Bobble | Short dump tool: hex of one level plus an ASCII bitmask. |
| `bubblebobble_print_levels_2.py` | Bubble Bobble | Longer dump tool. The notes are embedded as a docstring, then a renderer that applies the mirror. |
| `captain_blood_validated_reference.txt` | Captain Blood | Validated memory map, conversation interpreter, and alien-file-0 quests and coordinate replies. |
