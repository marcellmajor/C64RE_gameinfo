# Alien file 15 (bank P1) — planets 60-63: Blood's duplicates (clones)

Bank P1, virtual offset $1EFA, size up to about 1470 bytes (last file in the bank).
- Script at +$0053: 84 records (59 patterns, 16 actions, 7 conditions, 2 time
  conditions), 200 operands.
- Face image at +$0234.
- Raw decode: ../alien_script_file15_decoded.txt.
- Bank P2 has its own, different file 15 (not decoded).

See 00_index.md for the conventions.

## Characters

| Planet | Flag | Character | Present at start | Coordinates A / B |
|---|---|---|---|---|
| P60 | F1 | DUPLICATE 1 | yes | (195,85) / (43,4) |
| P61 | F2 | DUPLICATE 2 ("POP BLOOD") | yes | (143,74) / (221,54) |
| P62 | F3 | DUPLICATE 3 | yes | (56,13) / (198,5) |
| P63 | F4 | DUPLICATE 4 | yes | (105,34) / (69,15) |

No planet names are given.

## Script-wide

- The first record is an action that sets **F5**. Leading actions run on every fresh
  message ($4991 -> $4AB8).
- F5 is read when the alien is taken aboard ($47C1 -> $EB).
- When the alien aboard is then removed ($0A76 -> $47E5), $EB grants **+60 minutes** to
  the time limit ($EC/$ED) [V code].
- [I] This is the game's "absorb a clone for vital fluids" mechanic.
- If the alien removed is from P60 or P61, $FD is incremented. At $FD = 2 the game loads
  **bank P2** (the second half).
- **No keyword small talk.** Every line here is conditional.

## P60 — Duplicate 1 (needs P60 present and not F998)

1. ME DUPLICATE 1 / YOU WANT KILL ME (INSULT)(INSULT) / ME IDEA / YOU NOT KILL ME /
   ME GIVE YOU PLANET DUPLICATE 2 3 4 / **YOU WANT ?** (repeats).
   - Answer **YES** or **ME WANT** -> F10.
   - Answer **NO** or **NOT WANT** -> F11 (he repeats "NO").
2. **F10:** YOU GREAT / PLANET DUPLICATE 2 **COORD current P28** /
   PLANET DUPLICATE 3 **COORD current P36** / PLANET DUPLICATE 4 **COORD current P24** /
   PLANET DUPLICATE 5 **COORD current P60** (F6, teleport offered).
   - P24, P28 and P36 belong to bank-P2 files (6, 7, 9).
   - These do not match where duplicates 2-4 are in this bank (P61-P63). Either he is
     lying, or he means the bank-P2 positions [?].
3. **F11:** YOU NONSENSE YOU NOT BRAVE SMALL WARRIOR / YOU KILL ME (F12, F6) / BYE.
   Leaves.

## P61 — Duplicate 2 (needs P61 present)

HOWDY POP BLOOD / POP POP BLOOD (repeats) / ME DUPLICATE 2 /
YOU NOT KILL ME BLOOD (sometimes, repeats) / ME FEAR / YOU LIKE ME ? /
ME LIKE YOU BLOOD POP BLOOD (sometimes, repeats). Then F6: teleport offered.

## P62 — Duplicate 3 (needs P62 present; depends on the clock)

- **Clock <= 320 minutes:** ME DUPLICATE 3 / YOU NOT KILL ME FEAR FEAR /
  ME GREAT RENDEZ-VOUS / **HOUR** (current time) / YOU GIVE TIME /
  YOU NOT GIVE TIME = ME KILL ME / YOU GIVE TIME = ME NOT KILL ME (F6).
- **Clock > 320 minutes:** ME LIKE RENDEZ-VOUS / YOU DESTROY ME / BYE BLOOD (F6).

## P63 — Duplicate 4 (needs P63 present and not F998)

ME DUPLICATE 4 / KNOW LIKE RENDEZ-VOUS NOT / DESTROY FEAR FEAR BRAVE WARRIOR /
WARRIOR FEAR IDEA IDEA IDEA / 2 3 4 5 3 3 3.

Then:
- F6 (teleport offered)
- **F998** (saved)
- **sets P60+0..+3**: Duplicate 1's planet is "present at home" again

## P60 after Duplicate 4 (block F1, F998, and P61, P62, P63 all gone)

YOU SEARCH ME BLOOD / ME SAY YOU GREAT INFORMATION / YOU DESTROY ME YES BLOOD /
YOU GO SEARCH TORKA / TORKA LIKE YOU / YOU TELEPORT TORKA / YES BLOOD /
YOU GREAT WARRIOR / BYE BLOOD / TORKA LIKE YOU / TORKA PLANET CORPO /
**COORD home P27** / ME YOU LIKE TORKA / YOU = ME = GREAT GENETIC /
**COORD home P27** (F6).

All of these repeat. P27 is in bank P2 (file 6).

## Coordinates this file reveals

| Token | Planet | A | B | Who |
|---|---|---|---|---|
| current P28 | "Duplicate 2" | (238,23) | (115,117) | Duplicate 1 (YES) |
| current P36 | "Duplicate 3" | (170,109) | (88,98) | Duplicate 1 (YES) |
| current P24 | "Duplicate 4" | (170,105) | (215,42) | Duplicate 1 (YES) |
| current P60 | "Duplicate 5" | (195,85) | (43,4) | Duplicate 1 (YES) |
| home P27 | Torka, planet CORPO | (65,71) | (226,125) | Duplicate 1 after F998 |

"Current" coordinates are where that planet's alien is now ($0680/$06C0). At game start
they equal the home coordinates.

## Flags

- Reads: P60+0, P61+0, P62+0, P63+0, F998, the clock (320 minutes).
- Writes: F5, F6, F10-F12 (per encounter); F998 and P60+0..+3 (saved).

## Interpretation

These are Captain Blood's clones. Each takes Blood for his "Pop" or fears being killed.
Taking them aboard grants extra time, and removing Duplicates 1 and 2 opens the second
half of the game. Duplicate 1 points to clones in the P2 part of the galaxy, and
Duplicate 4's speech re-activates Duplicate 1. Once the others are gone, Duplicate 1
sends Blood to Torka on planet Corpo (P27).
