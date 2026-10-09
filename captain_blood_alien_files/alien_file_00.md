# Alien file 0 — planets 0-3: Small Yoko, No-No, Maxon

Bank P1, virtual offset $0000, 2508 bytes.
- Script at +$011C: 256 records (187 patterns, 39 actions, 30 conditions), 735 operands.
- Face image at +$06A2.
- Raw decode: ../alien_script_file0_decoded.txt.
- Longer walkthrough of this file: text_dir/captainblood/alien_script_file0_explained.md.
  Its section 7 calls planets 60/61 a "win"; that is corrected below.

See 00_index.md for the conventions (Pn, Pn+k, F-flags, planet names).

## Characters

| Planet | Flag | Character | Planet name | Present at start | Coordinates A / B |
|---|---|---|---|---|---|
| P0 | F1 | SMALL YOKO (Izwal child) | BOW-BOW | yes | (145,69) / (232,125) |
| P1 | F2 | NO-NO, claims "ME SMALL YOKO" | IDEA 3 4 9 | no (P1+3 clear) | (248,99) / (165,17) |
| P2 | F3 | — (no block: small talk only) | ? | yes | (103,14) / (138,106) |
| P3 | F4 | MAXON, Yoko's "POP" (scientist) | RENDEZ-VOUS 6 7 | no (P3+3 clear) | (40,23) / (167,88) |

The silent records "YOKO BOW-BOW" ($636A), "NO NO IDEA 3 4 9" ($652B) and
"MAXON RENDEZ-VOUS 6 7" ($65EF) are this file's identity records.

## Small talk (all four planets, checked first)

About 50 keyword lines, mostly "sometimes" (1 in 8 skip) and repeatable. Examples:
ENEMY -> ME LIKE ENEMY ME WANT PEACE; HOME -> ME WANT GREAT HOME;
YOKO -> YOKO SMALL MAXON; DUPLICATE -> 1 2 3 ME GREAT SCIENTIST (LAUGH).

- (CURSE) -> the alien curses and **leaves**.
- Not small-talk triggers (safe openers): BLOOD, ME, YOU, WANT, NOT, YES, NO, PLANET,
  POP, IDENTITY, CODE, IDEA, TELEPORT, MAXON.

## P0 — Small Yoko

### At home (block F1 + P0+2)

1. He introduces himself: ME SMALL YOKO / PLANET = BOW-BOW / ME LIKE PEACE. Then he
   asks "SMALL YOKO WANT KNOW IDENTITY ?" (F11).
   - Answer BLOOD -> introduced (F10). "HOWDY BLOOD" also sets the persistent F420, so
     later visits skip the introduction.
   - Any other answer -> "YOU NOT SAY NONSENSE" / "YOU BAD BYE", leaves.
2. Topics:
   - IDENTITY+POP -> "MAXON IDENTITY POP"
   - ME+SEARCH+POP, PLANET+CROOLIS-ULV, or DEAD+GENETIC -> F13
   - KILL+YOKO, (INSULT), PRISON, BYE -> leaves
3. F13 monologue: ... "YOU TELEPORT ME GOOD PLANET" (F6 = teleport offered).

### Taken away from home (block F1 + not P0+2)

Monologue (keep clicking): SOB SOB PLANET NOT HOME / ... / YOU GO URGENT PLANET TRAP 4 /
**COORD home P12** / HELP YOKO YOKO YOKO / DEAD DEAD DEAD / DEAD.

Actions: clear P0+3 (Yoko gone), set P1+3 (No-No appears), set P3+3 (Maxon appears).
Then leaves.

## P1 — No-No (block F2 + P0+0 + not P0+3, i.e. after Yoko's death)

1. "HOWDY BLOOD" / "ME KNOW YOU BLOOD" (F11). Then, one per click:
   YOU KILL ME (LAUGH) / ME NOT IZWAL NO NO / ME SMALL YOKO / YES BLOOD / ME NOT DEAD /
   DUPLICATE FREE ME / ME PRISONER DUPLICATE / ME FEAR DUPLICATE ME NOT GIVE IDENTITY YOKO /
   ME GIVE IDENTITY NO NO / DUPLICATE FREE ME PLANET IDEA 3 4 9.
2. Keyword replies:
   - TELEPORT -> ME NOT WANT TELEPORT
   - MAXON -> POP (SOB)(SOB)
   - DUPLICATE -> ME KNOW PLANET DUPLICATE
3. **RENDEZ-VOUS + 6 + 7** (the name of Maxon's planet) -> F10. Then: BLOOD YOU GREAT /
   ME GIVE YOU GREAT INFORMATION / ... / PLANET DUPLICATE = / **COORD home P60**
   (Duplicate 1) / ME NOT WANT DUPLICATE KILL YOU / BYE BLOOD -> leaves.

## P3 — Maxon (needs not P0+3; three stages saved in F435-F437)

1. **Quiz:**
   - "IDENTITY ?" -> BLOOD. A wrong answer gives "DANGER PLANET RENDEZ-VOUS 6 7
     FORBIDDEN", and he leaves.
   - "YOU KNOW CODE ?" -> YES.
   - "FRIEND ENEMY ?" -> FRIEND.
   Then a monologue about the duplicate (ME MAXON / ME PRISONER DUPLICATE /
   ME GIVE IDENTITY PLANET DUPLICATE = / YOU SEARCH YOKO ...). F435, leaves.
2. **Next visit:** "DUPLICATE SAY ME YOU KILL SMALL YOKO / ... ME WANT KILL YOU". F436,
   leaves.
3. **Next visit:** say **YOKO+NOT+DEAD** (F10) and **IDEA+3+4+9** (F11), the name of
   No-No's planet. One message can hold both. Then: ... SMALL YOKO NOT DEAD /
   PLANET IDEA 3 4 9 / **COORD home P1** / ME GIVE YOU PLANET DUPLICATE /
   **COORD home P61** (Duplicate 2) / YOU GO SEARCH DUPLICATE / ... / BYE BLOOD.
   Then P3+3 is cleared (Maxon leaves) and the conversation ends.

## Coordinates this file reveals

| Token | Planet | A | B | Who / when |
|---|---|---|---|---|
| home P12 | TRAP 4 (Dead Genetic) | (140,33) | (171,53) | Yoko, away from home |
| home P60 | Duplicate 1 | (195,85) | (43,4) | No-No, after RENDEZ-VOUS 6 7 |
| home P1 | IDEA 3 4 9 (No-No) | (248,99) | (165,17) | Maxon, stage 3 |
| home P61 | Duplicate 2 | (143,74) | (221,54) | Maxon, stage 3 |

## Flags

- Reads: P0+0/+2/+3, P1+3, P3+3, F420, F435-F437, F999.
- Writes: P0+3 (clear), P1+3, P3+3 (set, then clear), F420, F435, F436.
- Per-encounter: F6 (teleport offered), F10-F13, F20-F25 (quiz answers).
- Note: F437 is never set, so Maxon's stage 3 would replay on a later visit.

## Interpretation

Yoko wants to leave home. Taking him away kills him, and that brings No-No and Maxon
onto the map. Each of the two knows the other's planet name. Maxon only trusts Blood
once told that Yoko is "not dead". The file hands out the positions of Duplicates 1 and
2 (P60, P61). Dealing with those two switches the game to bank P2 (not a win).
