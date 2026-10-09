# Captain Blood (C64) — Alien files: index and shared conventions

One description file per decoded alien file:
- alien_file_00.md
- alien_file_02.md
- alien_file_03.md
- alien_file_04.md
- alien_file_15.md

Raw decodes: ../alien_script_fileN_decoded.txt.
Storage / format / interpreter: ../alien_files_format.md.

Sources:
- memdump_dir/landed_blood.bin ("game A")
- ../dumps/blood_run2_ram.bin ("game B", from a VICE snapshot; includes the RAM under I/O)
- user snapshot "lamded planet 2.vsf", which confirms file 3 is loaded at planet 12

## 1. Coverage

| Bank | File | Planets | Status | Main characters |
|---|---|---|---|---|
| P1 | 0 | 0-3 | decoded | Small Yoko, No-No, Maxon |
| P1 | 2 | 8-11 | decoded | Great Bounty, Missile Brave (Migrax) |
| P1 | 3 | 12-15 | decoded | Croolis-Ulv: Dead Genetic, Great Destroy, Howdy Prison, (Insult) 4 |
| P1 | 4 | 16-19 | decoded | Croolis-Var: Good Nonsense, Male Warrior, Bad Crazy, Poor Genetic |
| P1 | 15 | 60-63 | decoded | Duplicates 1-4 (Blood's clones) |
| P2 | 6, 7, 9, 10, 11, 13, 14, 15 | 24-31, 36-47, 52-63 | not decoded | P2 is only in RAM after the bank switch |
| — | 1, 5, 8, 12 | 4-7, 20-23, 32-35, 48-51 | no file | nobody to talk to there |

Planets 4-7 also start with presence flag +0 clear.

## 2. Conventions used in the descriptions

### Planets

- Pn = planet index n (0-63). The file is n >> 2, and inside the file the planet is
  F((n & 3) + 1), i.e. F1..F4.
- Planet coordinates are random per game. Both recorded games are listed:
  "A (x,y) / B (x,y)".
- COORDINATE tokens name a planet by index. The game looks up the coordinates at the
  moment the alien speaks:
  - "home" = original position ($0600 / $0640)
  - "current" = where that alien is now ($0680 / $06C0)

### Per-planet flags

F100 + 5n + k, written Pn+k.

| k | Meaning | Evidence |
|---|---|---|
| +0 and +3 | the alien is present; both must be set to get a conversation | $3DF6 [V] |
| +0 and +3 cleared | the alien is gone | $47E5 [V]; scripts also clear them ("dies", "blows himself up") |
| +2 | the alien is at its home coordinates | recomputed on landing, $4DF8-$4E0B [V] |
| +1, +4 | [?] | +4 -> $DC on landing |

### Per-encounter flags (F1-F29, cleared at every encounter)

| Flag | Meaning |
|---|---|
| F1-F4 | which planet of the file |
| F5 | set by file 15 on every message; read when an alien is taken aboard ($47C1). [I] Marks "a duplicate": $47E5 then gives +60 minutes. |
| F6 | "alien agrees to be teleported": enables the teleport option ($413A-$4155 sets $E8 and draws it with $0FCA) [V] |
| F7 | "talked long enough": set on a 1 in 16 chance per message, always once 15 messages have been sent ($FB), or by a script action. Many story blocks need it, so keep talking. |
| F8 | home lead visited |
| F9 | set on a 1 in 4 chance per message |
| F10-F29 | script scratch flags for this encounter |

### Story flags

- F420 and up are persistent story flags (none are set at game start).
- F998 is set by Duplicate 4. F999 is never set (terminal barrier in file 0).

### Planet names

The script language names planets with word + digits. Every file has a record that ties
a character name, a COORDINATE token and a planet name together (in files 3 and 4 these
are "ordered" records that the player can never match, because player input drops the
COORDINATE word). Known names:

| Planet | Name | Planet | Name |
|---|---|---|---|
| P0 | BOW-BOW | P13 | GREAT TRAP |
| P1 | IDEA 3 4 9 | P14 | BAD TRAP |
| P3 | RENDEZ-VOUS 6 7 | P15 | (INSULT) 8 0 |
| P8 | REPRODUCTION 1 4 | P16 | TRAP 2 |
| P9 | REPRODUCTION 1 2 8 | P17 | GREAT FEAR |
| P12 | TRAP 4 | P18 | KILL YOU |
| | | P19 | TRAP 1 |

The "passwords" in file 0 (RENDEZ-VOUS 6 7, IDEA 3 4 9) are these planet names.

### Who is present at game start (identical in games A and B)

- P0, P2, P8-P19 and P60-P63 are present.
- P1 and P3 are absent until Yoko's story sets their +3 flag.
- P4-P7 are absent.

## 3. Cross-file story chain (P1 bank)

1. P0 Yoko (file 0): asks to be teleported. Away from home he gives P12, then dies.
   - Clears his own +3.
   - Sets P1+3 and P3+3, so No-No (P1) and Maxon (P3) appear.
2. P3 Maxon (file 0): an identity quiz.
   - Failing it reveals "RENDEZ-VOUS 6 7" (the name of his own planet).
   - Later, "YOKO NOT DEAD" + "IDEA 3 4 9" gets P1 and P61 (Duplicate 2).
3. P1 No-No (file 0): told "RENDEZ-VOUS 6 7", he gives P60 (Duplicate 1).
4. P12-P15 Croolis-Ulv (file 3) and P16-P19 Croolis-Var (file 4) are at war:
   - Dead Genetic (P12) wants the four Croolis-Var planets destroyed (gives P16-P19, then
     P8 as the reward).
   - Good Nonsense (P16) wants three Croolis-Ulv killed but their informant Great Destroy
     spared.
   - Howdy Prison (P14) wants Great Destroy killed (reward P8).
   - Any Croolis-Ulv gives Maxon's planet P3 when asked "IDENTITY PLANET MAXON".
5. P8 Great Bounty / P9 Missile Brave (file 2), the Migrax:
   - Great Bounty, taken away from home, reveals Missile Brave's planet (P9).
   - Brought back home, he gives P1 ("planet Izwal No-No").
   - Missile Brave then gives P12 and, on a later visit, P61 (Duplicate 2), and mentions
     the scientist Sinox.
   - The Croolis-Var Poor Genetic (P19) and Howdy Prison (P14) also give P8.
6. P60-P63 Duplicates (file 15):
   - Duplicate 1 gives the positions of duplicates 2-5 (P28, P36, P24 in the P2 bank,
     and P60).
   - Taking duplicates aboard sets F5 -> +60 minutes.
   - Removing the aliens of P60 and P61 ($FD = 2) loads bank P2 (the second half of the
     game).
   - After duplicates 2-4 are gone, P60 sends Blood to Torka on planet Corpo (P27, P2
     bank).

[I] "Kill / destroy" in the scripts means making a planet's alien disappear (its +0
cleared). The game paths that do this are $47E5 (an alien taken aboard, then the ship
action $0A76) and $4D1C (clears +0/+1 at the ship's position; [I] planet destruction).
Scripts can also do it themselves (Bad Crazy, Yoko).
