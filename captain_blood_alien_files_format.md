# Captain Blood (C64) — Alien files: storage, structure and interpretation

Last updated 2026-10-09. Legend: [V] verified in code/data, [I] inferred, [?] open.
All addresses are for the running tape version of the game.

Sources:
- memdump_dir/landed_blood.bin ("game A"; matches live VICE RAM)
- sessions/captain_blood/dumps/blood_run2_ram.bin ("game B", extracted from a VICE
  snapshot; includes the RAM under I/O)
- the user's VICE snapshot "lamded planet 2.vsf" (file 3 loaded at planet 12)

Related:
- per-file descriptions: sessions/captain_blood/alien_files/ (00_index.md +
  alien_file_NN.md)
- raw decodes: sessions/captain_blood/alien_script_fileN_decoded.txt
- decoder: text_dir/captainblood/decode_alien_script.py

## 1. What an "alien file" is

Every planet has an index 0..63 (current planet = $DB). Planets are grouped by four:
alien file number = planet index >> 2 ($DA, set by the landing classifier $4D99).
One alien file therefore serves four planets. Inside the file, the script tells them
apart with flags F1..F4 = (planet index & 3) + 1.

A file holds everything that is specific to that group of aliens:
- a small header
- a bitmap with 3 metadata bits per script word
- the conversation script (bytecode)
- the compressed face graphics

The vocabulary (word table, icons) is shared and is not part of a file.

## 2. Where the files are stored

### 2.1 On tape: two data banks [V]

File descriptors at $5120-$5163 have this layout: 14-byte name, 1 byte ($02, or $09 for
"BLOOD CPT"), load address.

| Descriptor | Name | Load addr | Loaded by | Purpose |
|---|---|---|---|---|
| $5131 | "B4" | $5C00 | $09F1 (new game) | alternative word tables (see 6.6) |
| $5142 | "P1" | $5C00 | $0A27 (new game) | alien bank, part 1 |
| $5153 | "P2" | $5C00 | $0A99 (mid-game) | alien bank, part 2 |
| $5120 | "BLOOD CPT" | $5C00 | [?] | [?] |

$0D36 is the load call:
- It writes the marker bytes $01 $23 at the load address and calls the loader at $085F.
- If the marker is still there afterwards, the load failed. It returns C=1 and the
  caller retries.

The disk release on the user's drive (/Users/marci/RevEng/C64/CaptainBlood/
CaptainBlood.d64, "IKARI" crack) is organised differently:
- 16 files PA-PP, each loaded at $6C00, one per alien file number
- the header layout is different
- none of the tape scripts appear in them byte for byte

It cannot be used as a substitute for the tape banks.

### 2.2 In RAM: a scattered "virtual bank" [V]

A loaded bank is 9400 bytes, $5C00-$80B7. $0B1C copies it into three free RAM areas,
listed as (start, end) pairs in the table at $5178:

| Segment | Size |
|---|---|
| $5A00-$5BFF | 512 |
| $8100-$8C3F | 2880 |
| $C700-$DFFF | 6400 (RAM under the I/O area) |

Together they form one continuous 9792-byte virtual address space: offset 0 = $5A00,
offset 512 = $8100, offset 3392 = $C700.

$0BFD waits for raster line $96, disables IRQs and sets $01=$30 (all RAM) for the
copy. $0C0A restores $01=$35.

$5C00-$7BFF is then free again and is reused as a work buffer. That is where the
active file and the conversation buffers live.

Reading a bank from a RAM image:
- Concatenate the three segments, then cut files out using the index (2.3).
- An image must contain the RAM under I/O for $D000-$DFFF. A VICE snapshot does;
  landed_blood.bin does not (it holds I/O registers there).

### 2.3 File index: table $584C [V]

13 entries of 4 bytes each: [id, pages, offset lo, offset hi].
- id bit 7 = bank (0 = P1, 1 = P2); id bits 0-6 = alien file number.
- pages = number of 256-byte pages to copy.
- offset = virtual-bank offset.

| Bank | File | Planets | Pages | Offset | Status |
|---|---|---|---|---|---|
| P1 | 0 | 0-3 | 10 | $0000 | decoded |
| P1 | 2 | 8-11 | 8 | $09CC | decoded |
| P1 | 3 | 12-15 | 9 | $119D | decoded |
| P1 | 4 | 16-19 | 6 | $19DE | decoded |
| P1 | 15 | 60-63 | 6 | $1EFA | decoded |
| P2 | 6 | 24-27 | 6 | $0000 | not in RAM yet |
| P2 | 7 | 28-31 | 5 | $05D2 | not in RAM yet |
| P2 | 9 | 36-39 | 7 | $0A63 | not in RAM yet |
| P2 | 10 | 40-43 | 3 | $10D5 | not in RAM yet |
| P2 | 13 | 52-55 | 4 | $1350 | not in RAM yet |
| P2 | 14 | 56-59 | 5 | $16D0 | not in RAM yet |
| P2 | 11 | 44-47 | 4 | $1B09 | not in RAM yet |
| P2 | 15 | 60-63 | 6 | $1E8D | not in RAM yet |

Files that are not in the index for the current bank (1, 5, 8, 12, and the other bank's
files) have no conversation: the lookup at $3E1E falls through to the "nobody here" path
$3DCF.

The copy is whole pages, so it can run past the end of a file. For example, file 0 is
2508 bytes, but 10 pages = 2560 bytes are copied. The extra bytes are never used.

### 2.4 Moving aliens, the time bonus and bank switching [V code, I meaning]

Three routines move an alien. All work on its per-planet flags (section 7):

- **$47C1, take aboard** (called at $41C9):
  - $E9 = 1 (alien aboard), $EA = $DB (which one)
  - $EB = F5 (set only by file 15, the duplicates)
  - clear its +2 flag (no longer at home)
- **$479F, put down** (called at $3DE6, from the "nobody here" screen with an alien
  aboard):
  - $E9 = 0
  - set +0 and +3 of $EA (present here)
  - move the alien's current coordinates ($0680/$06C0) to the ship's position
- **$47E5, remove** (called at $0A79, a ship-menu action, icon 1 -> $422F):
  - $E9 = 0
  - clear +0 and +3 of $EA (gone)
  - if $EB is set: $F6 = 1 and the time limit $EC/$ED grows by 60 minutes
  - [I] This is "absorbing" a duplicate for vital fluids.

Bank switching:
- $FC = current bank: 0 after "P1" is loaded ($0A33), 1 after "P2" is loaded ($0AA5).
- The lookup id = $DA, OR $80 if $FC != 0 ($3E06-$3E0F).
- After $47E5, if $EA is planet 60 or 61, $FD is incremented ($0A7C-$0A88).
- At $FD = 2, $0A94 loads "P2".
- So removing Duplicate 1 (P60) and Duplicate 2 (P61) switches the game to its second
  half.

### 2.5 The active copy: $6100 [V]

- $0B71 (A = pages, X/Y = virtual offset) walks the segment table to the offset.
- It then copies the pages to $6100 ($0BB5-$0BFA), crossing segment boundaries as needed.

## 3. Encounter sequence (load -> talk) [V]

1. $3DC3: conversation screen entry. Sets $E7 = 0.
2. $DA < 0 (no alien here):
   - If an alien is aboard ($E9), the player can put it down here: icon 0 -> $479F,
     then load continues at $3E06.
   - Otherwise wait for a click, then exit via $40A6.
3. $3DF6: alien present? Planet flags 100+5*$DB+0 and +3 must both be set ($4E7F tests).
   Otherwise go to $3DCF (nobody to talk to).
4. $3E06: look up the file in $584C. $3E2D: JSR $0B71 copies it to $6100.
5. $3E30: unpack the face. JSR $173D with X/Y = $6100 + word[$6104], destination $7400.
6. $3E48: JSR $4816, encounter init:
   - clear F1-F29
   - set F((DB&3)+1)
   - set F8 if this planet's home lead has the visited bit
   - $FB = 15
   - disable all icons
   - $4860-$4892: walk the script, enable every icon whose word occurs in any pattern,
     and clear every pattern's "used" bit
7. $3F4B: JSR $4934 (alien greets first). $3F4E: JSR $4370 (play the greeting).
8. $3F51-$4158: conversation loop.
   - A mouth click runs JSR $4948 ($40BF) and JSR $4370 ($40C2).
   - Each loop pass ends at $413A: if F6 is set, no alien is aboard, the conversation is
     still on and $E8 = 0, then $E8 = 1 and the teleport option is drawn
     (JSR $0FCA, X = $80).

Runtime confirmation: in "lamded planet 2.vsf" the ship is on planet 12 at (140,33)
($DB = 12), and file 3 (planet 12 >> 2) is at $6100.

## 4. File layout [V]

File 0 as the example:

| Offset | Address | Content |
|---|---|---|
| +$00 | $6100 | word: script offset ($011C -> $621C) |
| +$02 | $6102 | word: same value as +$04 in all five files [?] no reader found |
| +$04 | $6104 | word: face image offset ($06A2 -> $67A2) |
| +$06 | $6106 | $00 $00 in all five files [?] |
| +$08 | $6108-$621B | operand bitmap (276 bytes = 92 groups x 3 planes = exactly the 735 pattern operands) |
| +$11C | $621C-$67A1 | conversation script, 256 records + $FF end |
| +$6A2 | $67A2-~$6ACB | compressed face image |

All five P1 files, cut from the bank in game B, have the same layout:

| File | Planets | Size | Script | Face | Records (pat/act/cond/time) | Operands | Bitmap fits |
|---|---|---|---|---|---|---|---|
| 0 | 0-3 | 2508 | +$011C | +$06A2 | 256 (187/39/30/0) | 735 | yes |
| 2 | 8-11 | 2001 | +$00C5 | +$046C | 149 (106/20/23/0) | 498 | yes |
| 3 | 12-15 | 2113 | +$00BF | +$04D3 | 174 (124/27/23/0) | 487 | yes |
| 4 | 16-19 | 1308 | +$006B | +$0288 | 93 (69/12/12/0) | 264 | yes |
| 15 | 60-63 | <= 1470 | +$0053 | +$0234 | 84 (59/16/7/2) | 200 | yes |

In every file:
- the script's $FF end is the byte right before the face image
- the bitmap exactly fills the gap between +$08 and the script

The bank copy and the working copy at $6100 differ only in "used" bits. The interpreter
writes flags back into the working copy only. File 0 in game A differs by one byte: the
greeting record $621C.

The P1 bank is byte-identical in games A and B (section 8).

### 4.1 Operand bitmap

- Pattern operand number j (counted in script order, only in pattern records; a 3-byte
  token counts as one) has three bits:
  - byte $6108 + 3*(j/8) + plane
  - mask = $80 >> (j & 7) (mask table $593B)
- Plane 0 set = REQ: the word must be in the player's message.
- Plane 1 set = silent: the word is NOT spoken in the reply.
- Plane 2 set = not a trigger.
- Reader: $4E99 / $4E9D / $4EA1 (plane 0 / 1 / 2), using the operand counter in $07/$08.

### 4.2 Face image

- 5-byte header:
  - word: offset of the bit-flag stream
  - word: offset of the run-flag stream
  - byte: cell count ($91 = 145 in file 0)
  - data bytes follow
- $173D sets up the streams and $1821 decodes them. A flag bit of 1 means "take the next
  byte", 0 means "repeat the previous one", using the bit masks at $50D5. This happens
  on two levels: the flag stream decides when to advance the run-flag stream, and the
  run-flag bytes decide when to advance the data stream.
- Output: cells x 8 bytes to $7400.
- [I] The face renderer then uses these cells (mosaic set-up $1B54).

## 5. Script format [V]

### 5.1 Records

Each record is:
- byte 0: bits 7-5 = type, bits 4-0 = operand byte count
- byte 1: flags
- the operands

A single $FF ends the script.

| Type | Name | Operands | Handler |
|---|---|---|---|
| $00 | pattern | words / 3-byte tokens | match $4B63, reply copy $4A18-$4A42 |
| $40 | action | signed flag words; none = "end encounter" | $4A85/$4A88 |
| $80 | condition | signed flag words | $4AC0 / $4AF1 |
| $A0 | time: clock > threshold | first operand = 16-bit minutes vs clock $C1:$C0; further operands = flag tests | $4AF8 (then $4B40) |
| $C0 | time: clock <= threshold | same layout | $4B0F (then $4B40) |

Time records occur only in file 15 (Duplicate 3, threshold 320 minutes).

### 5.2 Pattern flags

| Bit | Meaning |
|---|---|
| $80 | used (set when matched) |
| $01 | repeatable |
| $08 | random skip, 1 in 8 |
| $04 | ordered match |
| $02 | always matches |

### 5.3 Condition flags

Directly consecutive condition records form one AND chain ($4AF1/$4B2E). When a chain
is evaluated:
- $05 starts at 0 ($4AC0). The flags of every condition in the chain are OR'ed into $05.
- On failure, the flags of the remaining conditions in the chain are OR'ed in as well
  ($4B51).

| Bit | Meaning when the chain fails ($4ACF-$4AEF) |
|---|---|
| $80 | barrier: stop the walk, no reply |
| $40 | skip ahead, evaluating only conditions that have $20 |
| $20 | marks a condition that still gets evaluated after a $40 skip (a block start) |
| none | skip ahead to the next condition and evaluate it |

Usage in the files:
- File 0 uses $60 block headers, $80 barriers and one $A0 terminal barrier (F999).
- File 2 uses one $40 (planet 8's section), one $20 block and one $80 barrier.
- Files 3, 4 and 15 use plain conditions, each naming its F1..F4 explicitly.

### 5.4 Action flags

$01 = run only once (then marked with $80). All actions in the five P1 files have flags
$00.

### 5.5 Operands

- Pattern operand byte 0 or >= 4: a word id, an index into the word table at $9418.
- Pattern operand byte 1..3: a 3-byte token [type, a, b]:
  - 1 HOUR: prints the 16-bit value a*256+b, or the current clock if both are 0.
  - 2 FREQUENCY: shows only the FREQUENCY icon; the value is not printed.
  - 3 COORDINATE: if a != 0, home of planet a-1 ($0600/$0640); else current position
    of planet b-1 ($0680/$06C0).
- Player messages cannot contain tokens. $4BFD drops word id 3 and keeps ids 1/2 as
  slots with leftover bytes. Patterns that need a COORDINATE token (such as the
  "ordered" identity records) can never be matched by the player.
- Flag operand: 2 bytes, high byte first.
  - Positive n = Fn set / set Fn.
  - Two's-complement negative = Fn clear / clear Fn ($4A67).
- Flag n lives at $9210 + n/8, bit (n & 7), mask table $5933. Routines: $4E57 clear,
  $4E70 set, $4E85 test.
- Per-planet variants: $4E1C indexes 100 + 5*Y + X. $4E51 clear, $4E6A set, $4E7F test.

## 6. Interpretation logic (routines)

### 6.1 Reader primitives

| Routine | Job |
|---|---|
| $4893 | rewind: $D8/$D9 = $6100 + word[$6100], $D6/$D7 = 0 |
| $48AB | read header: $06 = length, $04 = flags, A = type; Z/N set from the type; C=1 at $FF |
| $48D3 | step to the next operand (1 or 3 bytes); bumps the operand counter $07/$08 |
| $48EF | write the flags byte back (stores the "used" bit), advance $D8; for patterns also add the operand count to $D6 |
| $4AB8 | run all action records that directly follow |
| $4925 | scan the player's word list $5CA0 (skips 3-byte tokens) |
| $4A67 | decode a signed flag operand into X/Y |

### 6.2 Entry points

- $4934 greeting: empty word list ($5CA0 = $FF x 8), up to 8 attempts.
- $4948 mouth click:
  - $E5 = 0 (fresh message):
    - $4BFD converts the icons in $5C80 to word ids in $5CA0 through $9718. An empty
      message ends here.
    - $4331 / $434B clear and redraw the player row.
    - $4991 fresh start:
      - F7 is set when the $FB countdown (15 messages) runs out, or on a 1 in 16 chance.
      - F9 is set on a 1 in 4 chance (cleared otherwise).
      - Then $4893 rewind, $4AB8 leading actions (e.g. file 15's "set F5"), and the
        $49C1 walk.
  - $E5 != 0 (continuation): $49C1 resumes where the last walk stopped, with the same
    words. The player's new icons are not read yet.
  - Afterwards: if a reply was produced ($E6), $E5++. Otherwise $E5 = 0. Then $4C32.

### 6.3 The walk, $49C1

Records are read in order until one produces a reply.

- **Condition chain** ($4AC0 -> $4AF1): every operand must hold (flag tests, time tests).
  - Pass: the actions that follow the chain run ($4AB8) and the walk continues.
  - Fail: see 5.3.
- **Action** met during the walk without a match: skipped ($49D5 -> $48EF).
- **Pattern** ($4B63):
  - Reject if used and not repeatable.
  - Reject on the 1-in-8 random skip if $08 is set.
  - Reject if it has no operands.
  - $04 ordered: all words must appear in order.
  - $02 always: accept.
  - Otherwise: every REQ word must be present, and at least one REQ or TRIG word must
    be present.
- **On a match:**
  - $48EF marks the pattern used.
  - $4AB8 runs the following actions:
    - set/clear flags
    - an action with no operands sets $E7 = conversation over
    - $01 "once" actions are skipped if already used
  - $4A18-$4A42 copy every operand whose plane-1 bit is clear into $5CB0 (3-byte tokens
    kept whole).
  - If anything was copied: $FF-terminate, $E6++, stop. The stack is restored from $0B
    at $4BF9.
  - If nothing was copied (silent match): keep walking.

### 6.4 Output

- $4C32 builds the reply icons:
  - word id -> icon through the $5C00 map (built at $4851 from $9718)
  - HOUR / COORDINATE tokens -> digit icons ($4CBB -> $0F5D), with separator icon $6F
  - FREQUENCY tokens consume their bytes but print nothing
  - result in $5C90
- $4370 plays it, one icon per slot, with the beep $43BC.

### 6.5 Interpreter state (zero page)

| Address | Meaning |
|---|---|
| $D8/$D9 | record pointer |
| $D6/$D7 | operand counter |
| $06 | bytes left in the current record |
| $04 | current flags |
| $05 | condition-chain flags |
| $0B | saved stack pointer |
| $E5 | continuation pending |
| $E6 | reply produced |
| $E7 | conversation over |
| $E8 | teleport option shown |
| $0A | attempt count |

### 6.6 Shared vocabulary (not in the files)

- $9418-$9717 word table, 3 pages: 123 high-bit-terminated strings (ids 0-122), zero
  padded.
  - id 0 = blank; 1-3 = HOUR / FREQUENCY / COORDINATE; 111-120 = digits "0".."9".
- At new game, a byte saved on the stack at $09D1 ($FF) selects which word table to use
  ($09FB-$0A25):
  - '1' keeps the built-in table
  - '2' copies 3 pages from $5C00 (loaded "B4")
  - anything else copies from $5F00
  - [I] Probably the language choice.
- $9718: icon -> word id (bit 7 = icon disabled).
- $9798 / $9C58: icon graphics.

## 7. Flags the files use

### 7.1 Per encounter (F1-F29, cleared at $4816)

| Flag | Meaning |
|---|---|
| F1-F4 | which planet of the file [V] |
| F5 | set by file 15 on every message; $47C1 copies it to $EB, and $47E5 then adds 60 minutes [V]. [I] "This alien is a duplicate." |
| F6 | set by scripts right after "teleport" lines; makes the conversation loop offer the teleport ($413A-$4155) [V] |
| F7 | "talked long enough": 15 messages, a 1-in-16 chance per message, or set by a script. Many story speeches need it [V]. (Earlier notes called it "impatience".) |
| F8 | this planet's home lead is marked visited [V] |
| F9 | set on a 1 in 4 chance per message [V]. File 2 uses it as a random refusal. |
| F10-F29 | script scratch flags (answers given, topics raised) |

### 7.2 Per planet: F100 + 5n + k ("Pn+k"), saved

| k | Meaning | Changed by |
|---|---|---|
| +0 and +3 | alien present; both needed for a conversation ($3DF6) [V] | set: $479F; cleared: $47E5. Scripts also spawn (set +3) and remove (clear +0 or +3) aliens. |
| +2 | alien at its home coordinates (recomputed at $4DF8-$4E0B) [V] | cleared: $47C1 |
| +1 | [?] | cleared with +0 by $4D1C ([I] planet destruction) and by file 4's Bad Crazy |
| +4 | [?] copied to $DC on landing | |

At the start of both recorded games:
- P0, P2, P8-P19 and P60-P63 are present.
- P1 and P3 are absent (their +3 is clear) until Yoko's story sets it.
- P4-P7 are absent.

### 7.3 Story flags (F40 and up), saved

- F40-F49: set at new game; cleared one by one by the visit counter in $4D1C.
- Per file:

| File | Story flags |
|---|---|
| 0 | F420, F435, F436, F437 (F437 never set), F999 (never set, terminal barrier) |
| 2 | F460, F465, F466 |
| 3 | F480, F485, F487, F490 |
| 4 | F500 |
| 15 | F998 |

- Scripts also read and write other planets' Pn+k flags. This is how the stories link
  across files (see alien_files/00_index.md).

## 8. Script conventions found in the content [V data, I meaning]

- **Planet names.** Planets are named with word + digits. Known names: P0 BOW-BOW,
  P1 IDEA 3 4 9, P3 RENDEZ-VOUS 6 7, P8 REPRODUCTION 1 4, P9 REPRODUCTION 1 2 8,
  P12 TRAP 4, P13 GREAT TRAP, P14 BAD TRAP, P15 (INSULT) 8 0, P16 TRAP 2, P17 GREAT FEAR,
  P18 KILL YOU, P19 TRAP 1. The file-0 "passwords" are these names.
- **Identity records.** Each file has records that tie a character name, a COORDINATE
  token and a planet name together. Examples:
  - "MAXON RENDEZ-VOUS 6 7" (silent, file 0)
  - "GREAT BOUNTY <P8> REPRODUCTION 1 4" (file 2)
  - "DEAD GENETIC <P12> TRAP 4" (ordered, file 3)

  The ordered ones can never be matched by the player (5.5).
- **Character introductions.** Each character introduces itself with "ME <name>" and
  "PLANET (ME) = <planet name>", usually followed by its own COORDINATE.
- **Teleport offers.** "... TELEPORT ..." lines are followed by an action that sets F6.
- **Removal.** Story blocks test other planets' presence flags ("you killed X") and
  remove aliens by clearing +0 or +3.

## 9. What changes between games (run comparison) [V]

landed_blood.bin (game A, planet 0 at 145,69) was compared with blood_run2_ram.bin
(game B, planet 0 at 232,125). Both are at the start: $DB=0, $FC=0, $FD=0.

Identical in both:
- the whole P1 bank in all three segments (in game A, $D000-$DFFF could not be compared
  because the dump holds I/O registers there)
- the segment table $5178, the file index $584C, the tape descriptors
- the word table $9418, the icon table $9718
- every flag from F16 up, including all per-planet presence flags

Different:
- planet coordinates $0600-$06FF (254 of 256 bytes; random at new game, $46F5)
- ship position $E0/$E1, clock $C0
- per-encounter flags (F1-F15)
- face mosaic $54C2-$54D1 (random)
- self-modifying operands and the IRQ stage vector ($0F42, $0F4F, $1C1B, $1C3F, $36Ex,
  $4EE8, ...)
- the work buffer $5C00-$7BFF

So the alien files, and with them every script, planet name and story flag, are the
same in every game. COORDINATE tokens name planets by index, and the coordinates are
looked up in the per-game table at speaking time, so only the numbers differ.

## 10. Corrections to earlier notes

- $0A94 is the "P2" bank load, not an end/win sequence. Not yet fixed in:
  - memory_map_verified.md
  - conversation_coordinate_reveal.md
  - alien_script_file0_explained.md, section 7
  - captain_blood_validated_reference.txt ($FD / $0A94 lines)
- F7 is "talked long enough", not "impatience" (conversation_coordinate_reveal.md,
  memory_map_verified.md).
- The file-0 "passwords" RENDEZ-VOUS 6 7 and IDEA 3 4 9 are planet names (Maxon's and
  No-No's).
- The word table occupies $9418-$9717 (123 entries + zero padding). It does not end at
  $972C.
- Decoder fix (2026-10-09, text_dir/captainblood/decode_alien_script.py): in time
  records only the first operand is minutes; the rest are flags. The output for files
  without time records is unchanged.

## 11. Open

- The P2 files (6, 7, 9, 10, 11, 13, 14, 15) need a RAM image taken after "P2" is loaded.
  Plan: restore a landed snapshot in VICE, attach CaptainBlood_tape.tap, make the game
  run $0A94, then snapshot.
- What the ship-menu action at $0A76 / $422F is called in the game (inferred: absorb /
  remove the alien aboard).
- What $6102 (always equal to the face offset), $6106 and the "BLOOD CPT" tape file are.
- Exactly how the unpacked face at $7400 is drawn.
- Duplicate 1 (file 15) gives "current" positions of planets 28, 36 and 24 for
  duplicates 2-4. This bank has duplicates 2-4 on 61-63. Lying, or bank-P2 positions?
- File 3 tests P12+2 where P13+2 seems intended ($64FD).
- $4D1C (clears +0/+1 at the ship's position; event 7 of the $19E5 loop) is assumed to
  be planet destruction; not confirmed.
