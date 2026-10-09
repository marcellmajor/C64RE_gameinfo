# Alien file 2 — planets 8-11: the Migrax (Great Bounty, Missile Brave)

Bank P1, virtual offset $09CC, 2001 bytes.
- Script at +$00C5: 149 records (106 patterns, 20 actions, 23 conditions), 498 operands.
- Face image at +$046C.
- Raw decode: ../alien_script_file2_decoded.txt.

See 00_index.md for the conventions.

## Characters

| Planet | Flag | Character | Planet name | Present at start | Coordinates A / B |
|---|---|---|---|---|---|
| P8 | F1 | GREAT BOUNTY (Migrax) | REPRODUCTION 1 4 | yes | (218,28) / (157,110) |
| P9 | F2 | MISSILE BRAVE (Migrax) | REPRODUCTION 1 2 8 | yes | (3,70) / (128,101) |
| P10 | F3 | — (small talk only) | ? | yes | (39,105) / (133,28) |
| P11 | F4 | — (small talk only) | ? | yes | (78,55) / (235,83) |

Identity records: "GREAT BOUNTY <P8> REPRODUCTION 1 4" ($625C) and
"MISSILE BRAVE <P9> REPRODUCTION 1 2 8" ($63F9).
- $625C can be triggered by talking about GREAT / BOUNTY / REPRODUCTION 1 4. It answers
  with **COORD home P8** once per encounter.

## Small talk (all planets)

- Keyword lines (some answer once per encounter): BOUNTY -> ME LIKE BOUNTY;
  HOME -> MIGRAX NOT HOME; RENDEZ-VOUS -> RENDEZ-VOUS = TRAP (CURSE);
  KINGPAK -> ... ME NOT LIKE (CURSE); HELP -> ME WANT HELP YOU; KILL -> KILL NOT GOOD;
  CROOLIS-ULV/VAR -> CROOLIS-ULV NOT LIKE CROOLIS-VAR; TORKA -> TORKA GOOD ONDOYANTE;
  PLANET+TORKA -> CORPO PLANET TORKA GREAT HOME.
- ROBHEAD -> ME NOT LIKE ROBHEAD (F20). Then: ROBHEAD GREAT WARRIOR CRAZY / MIGRAX KILL
  KILL ROBHEAD / ROBHEAD GREAT DANGER / FRIEND YOU NOT SEARCH ROBHEAD.
- (INSULT) or (CURSE) lines -> the alien **leaves**.
- After a long conversation (F7): "YOU SMALL BRAIN YOU KILL TIME". With F7+F9 he also
  says "ME LIKE GREAT SCIENTIST / YOU KNOW PLANET SCIENTIST ?". Answering
  PLANET SCIENTIST MAXON gives **COORD home P16**, which is Good Nonsense's planet, not
  Maxon's (a wrong or misleading answer).

## P8 — Great Bounty

This section is gated by "P8 present AND F1". The $40 skip bit sends other planets
straight to P9's block.

1. **At home (P8+2), before Missile Brave's planet is known (not F460):**
   (LAUGH)(LAUGH)(LAUGH) / ME GREAT BOUNTY ME GREAT MIGRAX /
   ME NOT LIKE YOU KNOW REPRODUCTION 1 4 / REPRODUCTION 1 4 PLANET MIGRAX /
   ME SAY INFORMATION MIGRAX MISSILE BRAVE / MISSILE BRAVE KILL YOU.
   - Keywords:
     - MISSILE BRAVE KILL -> repeats the threat
     - PLANET+MISSILE -> ME KNOW ME NOT SAY (won't tell at home)
     - REPRODUCTION 1 4 -> COORD home P8
     - NO -> YOU SAY NO ? ?; YES -> YOU GREAT
     - (INSULT) -> leaves
   - TELEPORT -> F10. Then: ME LIKE GREAT SHIP / ME WANT KNOW PLANET /
     ME BRAVE YOU TELEPORT ME (F6, teleport offered).
2. **Away from home:** ME NOT KNOW PLANET / ME WANT GO REPRODUCTION 1 4 (SOB) /
   ME WANT GO HOME / YOU FREE ME / MISSILE BRAVE SEARCH ME.
   - **PLANET + MISSILE** (both required) -> "PLANET MISSILE BRAVE = REPRODUCTION 1 2 8"
     and **COORD home P9**. Sets F460 (saved). Leaves.
3. **F460, still away:** YOU TELEPORT ME PLANET REPRODUCTION 1 4 / COORD home P8 /
   ME WANT GO HOME (F6). He wants to be taken back.
4. **F460, but Missile Brave gone (P9+0 clear):** MISSILE BRAVE DEAD DEAD (SOB) / YOU BAD.
   Leaves.
5. **F460 and back home:** YOU GREAT WARRIOR / ME LIKE HOME PLANET REPRODUCTION 1 4 /
   YOU GOOD / ME GIVE YOU GREAT INFORMATION / ME KNOW PLANET IZWAL NO NO /
   **COORD home P1** / YES BLOOD / ME GO RENDEZ-VOUS URGENT FEMALE / BYE.
   Then P8+3 is cleared (Great Bounty leaves the map) and the conversation ends.

## P9 — Missile Brave (block F2; a barrier stops planets other than P9)

1. **First message:** if F9 fires (1 in 4) -> "PLANET REPRODUCTION 1 2 8 FORBIDDEN / BYE"
   and he leaves. Otherwise F10 is set (no more refusals this encounter) and he says
   "ME GREAT MIGRAX MISSILE BRAVE". TELEPORT -> ME NOT WANT TELEPORT.
2. **Great Bounty away from home and alive (and not F465):** YOU TELEPORT GREAT BOUNTY
   PLANET UNKNOWN / ME NOT LIKE YOU / YOU FREE MIGRAX GREAT BOUNTY / YOU TELEPORT GREAT
   BOUNTY PLANET REPRODUCTION 1 4 / ... (he wants Great Bounty brought home).
3. **Great Bounty gone (P8+0 clear):** YOU KILL MIGRAX GREAT BOUNTY / ... / YOU GREAT BAD.
   Leaves.
4. **Great Bounty home again and F460:** YOU GREAT YOU FREE MIGRAX GREAT BOUNTY / ... /
   YOU CONTACT FRIEND SINOX / FRIEND SINOX GREAT GREAT SCIENTIST /
   CODE SINOX = IMPOSSIBLE NOT SINOX / PLANET SINOX = ? / ME SMALL BRAIN ME NOT KNOW / BYE.
   Sets F465 (saved). Leaves.
5. **F465, next visit:** "YOU WANT GREAT INFORMATION".
   - CROOLIS-ULV (required) -> YOU GO / **COORD home P12** / CROOLIS-ULV GOOD FEMALE.
   - After a long conversation (F7): BYE GOOD GREAT WARRIOR / ME RENDEZ-VOUS FRIEND.
     F466 (saved), leaves.
6. **F466, next visit:** YOU GREAT GREAT FRIEND ME SAY INFORMATION / PLANET GOOD.
   - DUPLICATE (required) -> YOU GREAT FRIEND / ME KNOW / **COORD home P61** (Duplicate 2).
   - With F7: TIME = BOUNTY ME GO / BYE GREAT FRIEND. With F7+F9 he also clears P9+0
     (leaves the map). Ends.
7. At the very end of the script: a FREQUENCY token line (prints only the FREQUENCY icon).

## Coordinates this file reveals

| Token | Planet | A | B | Who / when |
|---|---|---|---|---|
| home P8 | REPRODUCTION 1 4 | (218,28) | (157,110) | Great Bounty, several places |
| home P9 | REPRODUCTION 1 2 8 | (3,70) | (128,101) | Great Bounty, away, after PLANET+MISSILE |
| home P1 | IDEA 3 4 9 (No-No) | (248,99) | (165,17) | Great Bounty, back home |
| home P12 | TRAP 4 (Dead Genetic) | (140,33) | (171,53) | Missile Brave, after F465, CROOLIS-ULV |
| home P61 | Duplicate 2 | (143,74) | (221,54) | Missile Brave, after F466, DUPLICATE |
| home P16 | TRAP 2 (Good Nonsense) | (144,86) | (46,28) | small talk, "PLANET SCIENTIST MAXON" (misleading) |

## Flags

- Reads: P8+0/+2, P9+0, F460, F465, F466, plus F1/F2, F7, F9, F10, F20.
- Writes: P8+3 (clear), P9+0 (clear), F460, F465, F466 (saved); F6, F10, F20
  (per encounter).

## Interpretation

Great Bounty fears his rival Missile Brave. Away from home he reveals Missile Brave's
planet and asks to be brought home; once home he rewards Blood with No-No's planet.
Missile Brave then becomes friendly, hints at the scientist Sinox, and over two more
visits gives the Croolis-Ulv planet and Duplicate 2.
