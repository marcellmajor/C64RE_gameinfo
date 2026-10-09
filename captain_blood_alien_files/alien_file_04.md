# Alien file 4 — planets 16-19: the Croolis-Var

Bank P1, virtual offset $19DE, 1308 bytes.
- Script at +$006B: 93 records (69 patterns, 12 actions, 12 conditions), 264 operands.
- Face image at +$0288.
- Raw decode: ../alien_script_file4_decoded.txt.

See 00_index.md for the conventions.

## Characters (all four are Croolis-Var: "ME CROOLIS-VAR ...")

| Planet | Flag | Character | Planet name | Present at start | Coordinates A / B |
|---|---|---|---|---|---|
| P16 | F1 | GOOD NONSENSE | TRAP 2 | yes | (144,86) / (46,28) |
| P17 | F2 | MALE WARRIOR | GREAT FEAR | yes | (188,29) / (134,86) |
| P18 | F3 | BAD CRAZY | KILL YOU | yes | (34,113) / (251,36) |
| P19 | F4 | POOR GENETIC | TRAP 1 | yes | (247,56) / (142,19) |

Identity records ("ordered", which the player can never match): $61CA, $62B6, $62E9,
$6337. These four are the Croolis-Var planets that Dead Genetic (file 3) wants
destroyed.

## Small talk (all planets): hostile

- Opening: "YOU GREAT".
- Keyword lines, all repeatable. Examples:
  - FEAR RADIOACTIVITY -> ME NOT FEAR RADIOACTIVITY
  - IZWAL NONSENSE -> IZWAL SAY NONSENSE
  - IDEA -> IDEA ME NOT KNOW
  - CRAZY -> ME NOT CRAZY (INSULT)(CURSE)
  - TRAP -> ME LIKE TRAP KILL KILL
  - FRIEND (required) -> FRIEND ME NOT KNOW ME KILL
  - SCIENTIST (required) -> ME LIKE KILL SCIENTIST (LAUGH)(LAUGH)
  - TELEPORT -> TELEPORT (F6, teleport offered)

## P16 — Good Nonsense (counter-quest: kill the Croolis-Ulv, spare Great Destroy)

1. **Not F500:** ME CROOLIS-VAR GOOD NONSENSE / PLANET = TRAP 2 / **COORD home P16**.
2. **With a long conversation (F7) — the quest:** ME GIVE YOU GREAT INFORMATION /
   YOU KILL CROOLIS-ULV / YOU KILL DEAD GENETIC **COORD P12** /
   YOU NOT DESTROY GREAT DESTROY / GREAT DESTROY FRIEND ME GIVE BOUNTY /
   GREAT DESTROY GIVE INFORMATION / YOU KILL HOWDY PRISON **COORD P14** /
   YOU KILL (INSULT) 4 **COORD P15** / YOU KILL DESTROY ... / BYE BLOOD.
   Sets F500 (saved). Leaves.
3. **F500:** YOU DESTROY CROOLIS-ULV / ME GIVE INFORMATION. Then:
   - **Great Destroy gone (P13+0 clear):** YOU KILL FRIEND GREAT DESTROY / curses / BYE.
     Leaves.
   - **Long conversation (F7):** BYE BLOOD. Leaves. This comes before the reward, so the
     reward needs F7 still clear (early in the conversation).
   - **P12, P14 and P15 all gone:** YOU GREAT GREAT WARRIOR / ME LIKE YOU / INFORMATION /
     ONDOYANTE TORKA LIKE YOU / DUPLICATE SEARCH TORKA REPRODUCTION / GREAT DANGER / BYE.
     The reward is information (Torka, the duplicate), **no coordinates**.

## P17 — Male Warrior (minor)

ME MALE WARRIOR / PLANET ME = GREAT FEAR / **COORD home P17**.
With F7: ME NOT WANT (LAUGH) / ME SEARCH FEMALE (CURSE)(INSULT). Leaves.

## P18 — Bad Crazy (destroys himself)

ME BAD CRAZY / PLANET ME = KILL YOU / **COORD home P18**.
With F7: ME LIKE MISSILE (LAUGH) / MISSILE GREAT PLAY ME STRONG STRONG /
ME STRONG ME PLAY MISSILE (LAUGH)x3 / (CURSE)(INSULT)... Then **P18+0 and P18+1 are
cleared**: he is gone from the map. Leaves.

Just talking to him long enough removes one of the four Croolis-Var that Dead Genetic
(file 3) wants destroyed.

## P19 — Poor Genetic (knows the Migrax)

ME POOR GENETIC / PLANET ME TRAP 1.
- MIGRAX (required) -> "MIGRAX ME KNOW" (F10); PLANET -> "PLANET" (F10).
- With F7 and F10: ME KNOW MIGRAX GREAT BOUNTY / GREAT MIGRAX GREAT NONSENSE /
  PLANET = REPRODUCTION 1 4 / **COORD home P8** / BYE ME GO. Leaves.

## Coordinates this file reveals

| Token | Planet | A | B | Who |
|---|---|---|---|---|
| home P16 / P17 / P18 | own planets | (144,86) / (188,29) / (34,113) | (46,28) / (134,86) / (251,36) | P16 / P17 / P18 intro |
| home P12 | TRAP 4 (Dead Genetic) | (140,33) | (171,53) | P16 quest |
| home P14 | BAD TRAP (Howdy Prison) | (124,54) | (253,117) | P16 quest |
| home P15 | (INSULT) 8 0 | (69,11) | (129,101) | P16 quest |
| home P8 | REPRODUCTION 1 4 (Great Bounty) | (218,28) | (157,110) | P19 |

## Flags

- Reads: P12+0, P13+0, P14+0, P15+0, F500.
- Writes: F500 (saved); P18+0 and P18+1 (cleared); F6, F10 (per encounter).

## Interpretation

The other side of the Croolis war. Good Nonsense wants three Croolis-Ulv leaders killed
but protects Great Destroy, his paid informant (compare file 3). Bad Crazy blows himself
up playing with a missile. Poor Genetic is the easy route to the Migrax planet P8.
