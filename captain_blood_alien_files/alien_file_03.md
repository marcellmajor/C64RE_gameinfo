# Alien file 3 — planets 12-15: the Croolis-Ulv

Bank P1, virtual offset $119D, 2113 bytes.
- Script at +$00BF: 174 records (124 patterns, 27 actions, 23 conditions), 487 operands.
- Face image at +$04D3.
- Raw decode: ../alien_script_file3_decoded.txt.
- Runtime check: the user's snapshot "lamded planet 2.vsf" was taken on P12 at
  (140,33), with this file at $6100.

See 00_index.md for the conventions.

## Characters (all four are Croolis-Ulv: "ME CROOLIS-ULV ...")

| Planet | Flag | Character | Planet name | Present at start | Coordinates A / B |
|---|---|---|---|---|---|
| P12 | F1 | DEAD GENETIC | TRAP 4 | yes | (140,33) / (171,53) |
| P13 | F2 | GREAT DESTROY | GREAT TRAP | yes | (172,41) / (181,120) |
| P14 | F3 | HOWDY PRISON | BAD TRAP | yes | (124,54) / (253,117) |
| P15 | F4 | (INSULT) 4 | (INSULT) 8 0 | yes | (69,11) / (129,101) |

Identity records ("ordered", which the player can never match): $6289, $63FA, $64B4,
$6560.

## Small talk (all planets): hostile, full of curses

- Opening: "HOWDY YOU" (F14).
- About 30 keyword lines, all repeatable. Examples:
  - KILL -> KILL YES YES (INSULT) (CURSE)
  - HOME -> ME NOT LIKE HOME ME DESTROY (LAUGH)
  - SHIP -> ME LIKE DESTROY SHIP
  - HOWDY -> ME NOT HOWDY
  - FRIEND FRIEND -> ME NOT FRIEND ME KILL FRIEND (CURSE)
  - FEAR (required) -> SMALL PEOPLE YOU POOR GENETIC
  - BYE -> BYE, **leaves**
- Knowledge any Croolis-Ulv shares:
  - PLANET+MAXON -> PLANET MAXON ME KNOW
  - IDENTITY+PLANET+MAXON -> IDENTITY PLANET MAXON RENDEZ-VOUS 6 7
  - RENDEZ-VOUS+6+7 -> **COORD home P3** (Maxon)

## P12 — Dead Genetic (wants the Croolis-Var destroyed)

1. **First talk (not F480):** ME CROOLIS-ULV DEAD GENETIC / PLANET = TRAP 4.
   YOKO (required) -> "ME KNOW SMALL YOKO" (F10).
2. **F10 and a long conversation (F7):** POP YOKO HELP ME / ME LIKE MAXON GREAT GENETIC /
   PLANET YOKO = BOW-BOW / **COORD home P0**.
3. **Long conversation (F7), not F480 — the quest:**
   ME CROOLIS-ULV DEAD GENETIC / ME WANT YOU DESTROY PLANET CROOLIS-VAR /
   PLANET TRAP 2 **COORD P16** / PLANET GREAT FEAR **COORD P17** /
   PLANET KILL YOU **COORD P18** / PLANET TRAP 1 **COORD P19** /
   KILL KILL (LAUGH)(LAUGH) / ME GIVE YOU GREAT INFORMATION / BYE GOOD BLOOD.
   Sets F480 (saved). Leaves.
4. **F480, while any Croolis-Var is still present:** "YOU NOT KILL CROOLIS-VAR ..." plus
   that planet's coordinates (P16 / P17 / P18 / P19). Sets F12. Then:
   YOU SMALL WARRIOR / YOU KILL KILL CROOLIS-VAR / curses. Leaves.
5. **All four gone (P16+0, P17+0, P18+0, P19+0 clear):** YOU GREAT WARRIOR ME LIKE YOU
   YOU KILL / ME GIVE YOU GREAT INFORMATION / INFORMATION = ME LIKE YOU REPRODUCTION /
   YOU ME REPRODUCTION ? / (LAUGH)x7.
   With F7: YOU GO / **COORD home P8** / BYE GREAT GOOD SPIRIT. Leaves.

## P13 — Great Destroy (bounty hunter, plays both sides)

1. **Not F485:** ME GREAT DESTROY / PLANET = GREAT TRAP / YOU WANT ?
   With F7: ME LIKE BOUNTY / ME GIVE INFORMATION CROOLIS-VAR /
   CROOLIS-VAR GIVE BOUNTY ME LIKE / YOU GIVE ME IDENTITY PLANET CROOLIS-ULV /
   ME WANT IDENTITY PLANET CROOLIS-ULV / YOU GO SEARCH PLANET CROOLIS-ULV / BYE.
   Sets F485 (saved). Leaves.
2. **F485, not F487:** "YOU GIVE ME IDENTITY PLANET CROOLIS-ULV". Name the other
   Croolis-Ulv planets:
   - TRAP+4 (P12) -> F10
   - BAD+TRAP (P14) -> F11
   - (INSULT)+8+0 (P15) -> F12

   All three can go in one message, e.g. "TRAP 4 BAD TRAP (INSULT) 8 0" (7 icons).
3. **With F10, F11 and F12:** YOU GREAT WARRIOR / ME SAY YOU GREAT INFORMATION /
   GREAT INFORMATION / (LAUGH)... / BYE. Sets F487 (saved). Leaves.
   **He gives nothing back.** He was buying the locations of his own people
   (interpretation).

## P14 — Howdy Prison (wants Great Destroy killed)

1. **Not F490:** ME CROOLIS-ULV HOWDY PRISON / PLANET ME BAD TRAP /
   YOU SMALL (INSULT)(CURSE).
   With F7: ME KNOW GREAT DESTROY LIKE BOUNTY / GREAT DESTROY FRIEND CROOLIS-VAR /
   YOU KILL GREAT DESTROY / GREAT DESTROY PLANET GREAT TRAP / **COORD home P13**.
   Then BYE (CURSE). Sets F490 (saved). Leaves.
2. **If Dead Genetic (P12) is away from home (P12+2 clear):** YOU TELEPORT GREAT DESTROY /
   **COORD current P13**. The script tests P12's flag here; [?] possibly meant to be
   P13's.
3. **F490, Great Destroy gone (P13+0 clear):** YOU KILL GREAT DESTROY / ME HELP YOU /
   YOU WANT ?
   - MIGRAX (required) -> MIGRAX YES ME KNOW / **COORD home P8**
   - BYE -> leaves
4. **F490, Great Destroy still alive:** YOU NOT KILL GREAT DESTROY / curses. Leaves.

## P15 — (Insult) 4 (knows Maxon's planet)

1. ME CROOLIS-ULV (INSULT) 4 / PLANET ME = (INSULT) 8 0 / **COORD home P15** (his own).
2. Keywords:
   - TELEPORT -> TELEPORT ME WANT (F6)
   - MAXON (required) -> YOU KNOW PEOPLE MAXON ? (F15)
   - IZWAL (required, silent) -> F16
3. **With F15 and F16:** PLANET MAXON = RENDEZ-VOUS 6 7 / **COORD home P3**. Sets F7.
   Then: ME RENDEZ-VOUS URGENT ME GO KILL (LAUGH)(LAUGH) / BYE GOOD WARRIOR. Leaves.

## Coordinates this file reveals

| Token | Planet | A | B | Who |
|---|---|---|---|---|
| home P3 | RENDEZ-VOUS 6 7 (Maxon) | (40,23) | (167,88) | any (IDENTITY PLANET MAXON...), P15 |
| home P0 | BOW-BOW (Yoko) | (145,69) | (232,125) | P12 after YOKO |
| home P16-P19 | Croolis-Var planets | see file 4 | | P12 quest |
| home P8 | REPRODUCTION 1 4 (Great Bounty) | (218,28) | (157,110) | P12 reward, P14 reward |
| home / current P13 | GREAT TRAP (Great Destroy) | (172,41) | (181,120) | P14 |
| home P15 | (INSULT) 8 0 | (69,11) | (129,101) | P15 itself |

## Flags

- Reads: P12+2, P13+0, P16+0, P17+0, P18+0, P19+0, F480, F485, F487, F490.
- Writes: F480, F485, F487, F490 (saved); F6, F7, F10-F16 (per encounter).

## Interpretation

The Croolis-Ulv are at war with the Croolis-Var (file 4). Dead Genetic hires Blood to
destroy the four Croolis-Var planets. Great Destroy is a traitor who collects the names
of Croolis-Ulv planets for a bounty. Howdy Prison wants him dead and pays with the Migrax
planet. (Insult) 4 tells Maxon's location to anyone who mentions Maxon and the Izwal.
