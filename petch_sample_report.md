# C64-RE Report — Petch

**Question:** in the current screen a custom animation is shown when destroyed a formerly red ice cube, 800 poins added, check on screenshot

**Verdict:** `replan`  ·  **Confidence:** 0.7  ·  **Iterations:** 2

## Answer

The custom animation for destroying a formerly red ice cube is triggered via the routine at `$5A81` (and its siblings `$5A71`, `$5A79`, `$5A89`). 

When the game detects the destruction condition (e.g., checking adjacent tiles around `$1F57` or `$1F8B`), it jumps to `$5A81`. This routine performs two key actions:
1. It calls `$5A61`, which writes to `$7900-$7902` (`$7900=1`, `$7901=1`, `$7902=$20`). These variables act as flags/timers for the custom animation and sound effects.
2. It loads a state value (e.g., `#$04`) and jumps to `$1F6C`, which stores this state into the animation entity table at `$0D25,X`.

The entity system then takes over, using the screen pointers saved at `$0D21,X` and `$0D23,X` alongside the state in `$0D25,X` to play out the animation over subsequent frames. The 800-point award is likely granted during the lifecycle of this entity state, though the exact BCD addition (`ADC #$08`) is handled in the entity's update routine rather than the initialization.

## Open questions

- vice: set breakpoint at $5A81, then trace execution to find where the score (likely BCD) is incremented by 800 (search for SED followed by ADC #$08 or similar in the routines processing $0D25).

## Evidence

- h1/open
- `9a47272dc0ce` — tool result `vice/i2_s7`: [vice.disassemble args={"address": "$5A61", "count": 40, "show_symbols": true}] $5A61: A9 01       LDA #$01 $5A63: 8D 01
- `4f46ef7fd29d` — tool result `code_kb/i2_s10`: Layer-1 annotation for $1F6C-$1FFF (producer=critic, conf=0.80):  Checks Sprite 0 Y-coordinate for grid alignment, then 
- `58926483998d` — tool result `vice/i2_s3`: [vice.disassemble args={"address": "$1F6C", "count": 100, "show_symbols": true}] $1F6C: 9D 25 0D    STA $0D25,X $1F6F: 4

## Critic notes

The analyst correctly identified the initialization of the animation entity at `$1F6C` and `$5A81`, but failed to locate the actual 800-point award mechanism. The claim that it is 'likely granted during the lifecycle' is an unverified hypothesis. To fully answer the question, we must find the routine that processes the `$0D25` entity state and performs the BCD score addition (e.g., `ADC #$08`). Furthermore, the common exit point `$1985` after setting the `$0D25` state has not been investigated.

## Final plan

- `i2_s1` (vice): Disassemble jump target $1E8A (case 1) to see what points it awards
- `i2_s2` (vice): Disassemble jump target $1EFB (case 2)
- `i2_s3` (vice): Disassemble jump target $1F6C (case 4) - red ice cube destruction is dispatched via $5A81 with A=#$04, jumping to $1F6C
- `i2_s4` (vice): Disassemble jump target $1FDD (case 3)
- `i2_s5` (capstone): Static confirm of $1F6C region (red cube case) against dump bytes
- `i2_s6` (kb): Search KB notes for explicit mention of 800 points / red cube / score values
- `i2_s7` (vice): Locate score-add helper - check $5A61 (called before each dispatch) and follow score routine
- `i2_s8` (code_kb): Find xrefs to the dispatcher entries $5A71/$5A79/$5A81/$5A89 to know which game event triggers the red-cube case
- `i2_s9` (kb): Locate score-display BCD routine - find where score buffer is updated. Search labels.
- `i2_s10` (code_kb): Annotate $1F6C routine via Layer-1 to summarise the 800-point award mechanism

## Tool results (latest 20)

- ✓ **code_kb** `i1_s7`
  **→** No asm_doc hits for '5A81'.
  ```
  No asm_doc hits for '5A81'.
  ```
- ✓ **code_kb** `i1_s8`
  **→** No asm_doc hits for '5A71'.
  ```
  No asm_doc hits for '5A71'.
  ```
- ✓ **vice** `i1_s9`
  **→** {"address": "$5A70", "count": 80, "show_symbols": true}
  ```
  [vice.disassemble args={"address": "$5A70", "count": 80, "show_symbols": true}]
  $5A70: 60          RTS
  $5A71: 20 61 5A    JSR $5A61
  $5A74: A9 01       LDA #$01
  $5A76: 4C 8A 1E    JMP $1E8A
  $5A79: 20 61 5A    JSR $5A61
  $5A7C: A9 02       LDA #$02
  $5A7E: 4C FB 1E    JMP $1EFB
  $5A81: 20 61 5A    JSR $5A61
  $5A84: A9 04       LDA #$04
  $5A86: 4C 6C 1F    JMP $1F6C
  $5A89: 20 61 5A    JSR $5A61
  $5A8C: A9 03       LDA #$03
  $5A8E: 4C DD 1F    JMP $1FDD
  $5A91: 9D 25 0D    STA $0D25,X
  $5A94: AD 25 0D    LDA $0D25
  $5A97: D0 0D       BNE $5AA6
  $5A99: AD 26 0D    LDA $0D26
  $5A9C: D0 08       BNE $5AA6
  $5A9E: A9 00       LDA #$00
  $5AA0: 8D 00 79    STA $7900
  $5AA3: 8D 04 D4    STA $D404
  $5AA6: A9 00       LDA #$00
  $5AA8: 4C A1 3B    JMP $3BA1
  $5AAB: 9D 80 0D    STA $0D80,X
  $5AAE: A9 10       LDA #$10
  $5AB0: 8D 12 79    STA $7912
  $5AB3: A9 03       LDA #$03
  $5AB5: 8D 11 79    STA $7911
  $5AB8: A9 02       LDA #$02
  $5ABA: 8D 10 79    STA $7910
  $5ABD: 60          RTS
  $5ABE: EA          NOP
  $5ABF: EA          NOP
  $5AC0: 8A          TXA
  $5AC1: 48          PHA
  $5AC2: A2 00       LDX #$00
  $5AC4: BD 80 0D    LDA $0D80,X
  $5AC7: C9 04       CMP #$04
  $5AC9: D0 13       BNE $5ADE
  $5ACB: C9 04       CMP #$04
  $5ACD: D0 0F       BNE $5ADE
  $5ACF: E8          INX
  $5AD0: E0 04       CPX #$04
  $5AD2: D0 F0       BNE $5AC4
  $5AD4: 68          PLA
  $5AD5: AA          TAX
  $5AD6: A9 01       LDA #$01
  $5AD8: AD 28 0D    LDA $0D28
  $5ADB: 4C 72 53    JMP $5372
  $5ADE: A9 09       LDA #$09
  $5AE0: 9D 80 0D    STA $0D80,X
  $5AE3: A9 80       LDA #$80
  $5AE5: 9D B8 0D    STA $0DB8,X
  $5AE8: 4C CF 5A    JMP $5ACF
  $5AEB: EA          NOP
  $5AEC: EA          NOP
  $5AED: EA          NOP
  $5AEE: EA          NOP
  $5AEF: EA          NOP
  $5AF0: EA          NOP
  $5AF1: EA          NOP
  $5AF2: EA          NOP
  $5AF3: EA          NOP
  $5AF4: EA          NOP
  $5AF5: EA          NOP
  $5AF6: EA          NOP
  $5AF7: EA          NOP
  $5AF8: EA          NOP
  $5AF9: EA          NOP
  $5AFA: EA          NOP
  $5AFB: EA          NOP
  $5AFC: EA          NOP
  ```
- ✓ **capstone** `i1_s10`
  **→** $5A70  60          rts
$5A71  20 61 5A    jsr  $5A61
$5A74  A9 01       lda  #$01
$5A76  4C 8A 1E    jmp  $1E8A
$5A79  2
  ```
  $5A70  60          rts
  $5A71  20 61 5A    jsr  $5A61
  $5A74  A9 01       lda  #$01
  $5A76  4C 8A 1E    jmp  $1E8A
  $5A79  20 61 5A    jsr  $5A61
  $5A7C  A9 02       lda  #$02
  $5A7E  4C FB 1E    jmp  $1EFB
  $5A81  20 61 5A    jsr  $5A61
  $5A84  A9 04       lda  #$04
  $5A86  4C 6C 1F    jmp  $1F6C
  $5A89  20 61 5A    jsr  $5A61
  $5A8C  A9 03       lda  #$03
  $5A8E  4C DD 1F    jmp  $1FDD
  $5A91  9D 25 0D    sta  $0D25, x
  $5A94  AD 25 0D    lda  $0D25
  $5A97  D0 0D       bne  $5AA6
  $5A99  AD 26 0D    lda  $0D26
  $5A9C  D0 08       bne  $5AA6
  $5A9E  A9 00       lda  #$00
  $5AA0  8D 00 79    sta  $7900
  $5AA3  8D 04 D4    sta  $D404
  $5AA6  A9 00       lda  #$00
  $5AA8  4C A1 3B    jmp  $3BA1
  $5AAB  9D 80 0D    sta  $0D80, x
  $5AAE  A9 10       lda  #$10
  $5AB0  8D 12 79    sta  $7912
  $5AB3  A9 03       lda  #$03
  $5AB5  8D 11 79    sta  $7911
  $5AB8  A9 02       lda  #$02
  $5ABA  8D 10 79    sta  $7910
  $5ABD  60          rts
  $5ABE  EA          nop
  $5ABF  EA          nop
  $5AC0  8A          txa
  $5AC1  48          pha
  $5AC2  A2 00       ldx  #$00
  $5AC4  BD 80 0D    lda  $0D80, x
  $5AC7  C9 04       cmp  #$04
  $5AC9  D0 13       bne  $5ADE
  $5ACB  C9 04       cmp  #$04
  $5ACD  D0 0F       bne  $5ADE
  $5ACF  E8          inx
  $5AD0  E0 04       cpx  #$04
  $5AD2  D0 F0       bne  $5AC4
  $5AD4  68          pla
  $5AD5  AA          tax
  $5AD6  A9 01       lda  #$01
  $5AD8  AD 28 0D    lda  $0D28
  $5ADB  4C 72 53    jmp  $5372
  $5ADE  A9 09       lda  #$09
  $5AE0  9D 80 0D    sta  $0D80, x
  $5AE3  A9 80       lda  #$80
  $5AE5  9D B8 0D    sta  $0DB8, x
  $5AE8  4C CF 5A    jmp  $5ACF
  $5AEB  EA          nop
  $5AEC  EA          nop
  $5AED  EA          nop
  $5AEE  EA          nop
  $5AEF  EA          nop
  $5AF0  EA          nop
  $5AF1  EA          nop
  $5AF2  EA          nop
  $5AF3  EA          nop
  $5AF4  EA          nop
  $5AF5  EA          nop
  $5AF6  EA          nop
  $5AF7  EA          nop
  $5AF8  EA          nop
  $5AF9  EA          nop
  $5AFA  EA          nop
  $5AFB  EA          nop
  $5AFC  EA          nop
  $5AFD  EA          nop
  $5AFE  EA          nop
  $5AFF  EA          nop
  $5B00  AD 00 79    lda  $7900
  $5B03  C9 01       cmp  #$01
  $5B05  D0 12       bne  $5B19
  $5B07  CE 01 79    dec  $7901
  $5B0A  D0 0D       bne  $5B19
  ... (33 more)
  ```
- ✓ **code_kb** `i1_s11`
  **→** No asm_doc hits for '5800'.
  ```
  No asm_doc hits for '5800'.
  ```
- ✓ **vice** `i1_s12`
  **→** {"address": "$5800", "count": 100, "show_symbols": true}
  ```
  [vice.disassemble args={"address": "$5800", "count": 100, "show_symbols": true}]
  $5800: A9 01       LDA #$01
  $5802: 8D B0 0D    STA $0DB0
  $5805: A9 05       LDA #$05
  $5807: 8D B1 0D    STA $0DB1
  $580A: A2 00       LDX #$00
  $580C: BD 80 0D    LDA $0D80,X
  $580F: C9 01       CMP #$01
  $5811: F0 0A       BEQ $581D
  $5813: C9 02       CMP #$02
  $5815: F0 06       BEQ $581D
  $5817: E8          INX
  $5818: E0 04       CPX #$04
  $581A: D0 F0       BNE $580C
  $581C: 60          RTS
  $581D: 8A          TXA
  $581E: 48          PHA
  $581F: 0A          ASL A
  $5820: AA          TAX
  $5821: BD 03 D0    LDA $D003,X
  $5824: C9 52       CMP #$52
  $5826: F0 05       BEQ $582D
  $5828: 68          PLA
  $5829: AA          TAX
  $582A: 4C 17 58    JMP $5817
  $582D: 68          PLA
  $582E: AA          TAX
  $582F: A9 09       LDA #$09
  $5831: 20 EC 58    JSR $58EC
  $5834: 4C 17 58    JMP $5817
  $5837: A9 02       LDA #$02
  $5839: 8D B0 0D    STA $0DB0
  $583C: A9 05       LDA #$05
  $583E: 8D B1 0D    STA $0DB1
  $5841: A2 00       LDX #$00
  $5843: BD 80 0D    LDA $0D80,X
  $5846: C9 01       CMP #$01
  $5848: F0 0A       BEQ $5854
  $584A: C9 02       CMP #$02
  $584C: F0 06       BEQ $5854
  $584E: E8          INX
  $584F: E0 04       CPX #$04
  $5851: D0 F0       BNE $5843
  $5853: 60          RTS
  $5854: 8A          TXA
  $5855: 48          PHA
  $5856: 0A          ASL A
  $5857: AA          TAX
  $5858: BD 03 D0    LDA $D003,X
  $585B: C9 E2       CMP #$E2
  $585D: F0 05       BEQ $5864
  $585F: 68          PLA
  $5860: AA          TAX
  $5861: 4C 4E 58    JMP $584E
  $5864: 68          PLA
  $5865: AA          TAX
  $5866: A9 09       LDA #$09
  $5868: 20 EC 58    JSR $58EC
  $586B: 4C 4E 58    JMP $584E
  $586E: A9 03       LDA #$03
  $5870: 8D B0 0D    STA $0DB0
  $5873: A9 05       LDA #$05
  $5875: 8D B1 0D    STA $0DB1
  $5878: A2 00       LDX #$00
  $587A: BD 80 0D    LDA $0D80,X
  $587D: C9 01       CMP #$01
  $587F: F0 0A       BEQ $588B
  $5881: C9 02       CMP #$02
  $5883: F0 06       BEQ $588B
  $5885: E8          INX
  $5886: E0 04       CPX #$04
  $5888: D0 F0       BNE
  ```
- ✓ **capstone** `i1_s13`
  **→** $5800  A9 01       lda  #$01
$5802  8D B0 0D    sta  $0DB0
$5805  A9 05       lda  #$05
$5807  8D B1 0D    sta  $0DB1
$5
  ```
  $5800  A9 01       lda  #$01
  $5802  8D B0 0D    sta  $0DB0
  $5805  A9 05       lda  #$05
  $5807  8D B1 0D    sta  $0DB1
  $580A  A2 00       ldx  #$00
  $580C  BD 80 0D    lda  $0D80, x
  $580F  C9 01       cmp  #$01
  $5811  F0 0A       beq  $581D
  $5813  C9 02       cmp  #$02
  $5815  F0 06       beq  $581D
  $5817  E8          inx
  $5818  E0 04       cpx  #$04
  $581A  D0 F0       bne  $580C
  $581C  60          rts
  $581D  8A          txa
  $581E  48          pha
  $581F  0A          asl  a
  $5820  AA          tax
  $5821  BD 03 D0    lda  $D003, x
  $5824  C9 52       cmp  #$52
  $5826  F0 05       beq  $582D
  $5828  68          pla
  $5829  AA          tax
  $582A  4C 17 58    jmp  $5817
  $582D  68          pla
  $582E  AA          tax
  $582F  A9 09       lda  #$09
  $5831  20 EC 58    jsr  $58EC
  $5834  4C 17 58    jmp  $5817
  $5837  A9 02       lda  #$02
  $5839  8D B0 0D    sta  $0DB0
  $583C  A9 05       lda  #$05
  $583E  8D B1 0D    sta  $0DB1
  $5841  A2 00       ldx  #$00
  $5843  BD 80 0D    lda  $0D80, x
  $5846  C9 01       cmp  #$01
  $5848  F0 0A       beq  $5854
  $584A  C9 02       cmp  #$02
  $584C  F0 06       beq  $5854
  $584E  E8          inx
  $584F  E0 04       cpx  #$04
  $5851  D0 F0       bne  $5843
  $5853  60          rts
  $5854  8A          txa
  $5855  48          pha
  $5856  0A          asl  a
  $5857  AA          tax
  $5858  BD 03 D0    lda  $D003, x
  $585B  C9 E2       cmp  #$E2
  $585D  F0 05       beq  $5864
  $585F  68          pla
  $5860  AA          tax
  $5861  4C 4E 58    jmp  $584E
  $5864  68          pla
  $5865  AA          tax
  $5866  A9 09       lda  #$09
  $5868  20 EC 58    jsr  $58EC
  $586B  4C 4E 58    jmp  $584E
  $586E  A9 03       lda  #$03
  $5870  8D B0 0D    sta  $0DB0
  $5873  A9 05       lda  #$05
  $5875  8D B1 0D    sta  $0DB1
  $5878  A2 00       ldx  #$00
  $587A  BD 80 0D    lda  $0D80, x
  $587D  C9 01       cmp  #$01
  $587F  F0 0A       beq  $588B
  $5881  C9 02       cmp  #$02
  $5883  F0 06       beq  $588B
  $5885  E8          inx
  $5886  E0 04       cpx  #$04
  $5888  D0 F0       bne  $587A
  $588A  60          rts
  $588B  AD 10 D0    lda  $D010
  $588E  3D F0 4F    and  $4FF0, x
  $5891  F0 F2       beq  $5885
  $5893  8A          txa
  $5894  48          pha
  $5895  0A          asl  a
  $5896  AA          tax
  $5897  BD 02 D0    lda  $D002, x
  $589A  C9 20       cmp  #$20
  $589C  F0 05       beq  $58A3
  $589E  68          pla
  $589F  AA          tax
  $58A0  4C 85 58    jmp  $5885
  $58A3  68          pla
  $58A4  AA          tax
  $58A5  A9 09       lda  #$09
  $58A7  20 EC 58    jsr  $58EC
  $58AA  4C 85 58    jmp  $5885
  $58AD  A9 04       lda  #$04
  $58AF  8D B0 0D    sta  $0DB0
  $58B2  A9 05       lda  #$05
  $58B4  8D B1 0D    sta  $0DB1
  $58B7  A2 00       ldx  #$00
  $58B9  BD 80 0D    lda  $0D80, x
  $58BC  C9 01       cmp  #$01
  $58BE  F0 0A       beq  $58CA
  $58C0  C9 02       cmp  #$02
  $58C2  F0 06       beq  $58CA
  ... (56 more)
  ```
- ✓ **vice** `i1_s14`
  **→** {"address": "$58AD", "count": 80, "show_symbols": true}
  ```
  [vice.disassemble args={"address": "$58AD", "count": 80, "show_symbols": true}]
  $58AD: A9 04       LDA #$04
  $58AF: 8D B0 0D    STA $0DB0
  $58B2: A9 05       LDA #$05
  $58B4: 8D B1 0D    STA $0DB1
  $58B7: A2 00       LDX #$00
  $58B9: BD 80 0D    LDA $0D80,X
  $58BC: C9 01       CMP #$01
  $58BE: F0 0A       BEQ $58CA
  $58C0: C9 02       CMP #$02
  $58C2: F0 06       BEQ $58CA
  $58C4: E8          INX
  $58C5: E0 04       CPX #$04
  $58C7: D0 F0       BNE $58B9
  $58C9: 60          RTS
  $58CA: AD 10 D0    LDA $D010
  $58CD: 3D F0 4F    AND $4FF0,X
  $58D0: D0 F2       BNE $58C4
  $58D2: 8A          TXA
  $58D3: 48          PHA
  $58D4: 0A          ASL A
  $58D5: AA          TAX
  $58D6: BD 02 D0    LDA $D002,X
  $58D9: C9 40       CMP #$40
  $58DB: F0 05       BEQ $58E2
  $58DD: 68          PLA
  $58DE: AA          TAX
  $58DF: 4C C4 58    JMP $58C4
  $58E2: 68          PLA
  $58E3: AA          TAX
  $58E4: A9 09       LDA #$09
  $58E6: 20 EC 58    JSR $58EC
  $58E9: 4C C4 58    JMP $58C4
  $58EC: 9D 80 0D    STA $0D80,X
  $58EF: A9 30       LDA #$30
  $58F1: 9D B8 0D    STA $0DB8,X
  $58F4: 60          RTS
  $58F5: 60          RTS
  $58F6: 60          RTS
  $58F7: 60          RTS
  $58F8: 60          RTS
  $58F9: 60          RTS
  $58FA: 60          RTS
  $58FB: 60          RTS
  $58FC: 60          RTS
  $58FD: 60          RTS
  $58FE: 60          RTS
  $58FF: 60          RTS
  $5900: A2 00       LDX #$00
  $5902: BD 80 0D    LDA $0D80,X
  $5905: C9 09       CMP #$09
  $5907: F0 06       BEQ $590F
  $5909: E8          INX
  $590A: E0 04       CPX #$04
  $590C: D0 F4       BNE $5902
  $590E: 60          RTS
  $590F: DE B8 0D    DEC $0DB8,X
  $5912: D0 08       BNE $591C
  $5914: A9 01       LDA #$01
  $5916: 9D 80 0D    STA $0D80,X
  $5919: 4C 09 59    JMP $5909
  $591C: BD F9 07    LDA $07F9,X
  $591F: C9 9E       CMP #$9E
  $5921: F0 08       BEQ $592B
  $5923: A9 9E       LDA #$9E
  $5925: 9D F9 07    STA $07F9,X
  $5928: 4C 09 59    JMP $5909
  $592B: A9 9F       LDA #$9F
  $592D: 4C 25 59    JMP $5925
  $5930: AD B0 0D    LDA $0DB0
  $5933: D0 01       BNE $5936
  $5935: 60          RTS
  $5936
  ```
- ✓ **capstone** `i1_s15`
  **→** $58AD  A9 04       lda  #$04
$58AF  8D B0 0D    sta  $0DB0
$58B2  A9 05       lda  #$05
$58B4  8D B1 0D    sta  $0DB1
$5
  ```
  $58AD  A9 04       lda  #$04
  $58AF  8D B0 0D    sta  $0DB0
  $58B2  A9 05       lda  #$05
  $58B4  8D B1 0D    sta  $0DB1
  $58B7  A2 00       ldx  #$00
  $58B9  BD 80 0D    lda  $0D80, x
  $58BC  C9 01       cmp  #$01
  $58BE  F0 0A       beq  $58CA
  $58C0  C9 02       cmp  #$02
  $58C2  F0 06       beq  $58CA
  $58C4  E8          inx
  $58C5  E0 04       cpx  #$04
  $58C7  D0 F0       bne  $58B9
  $58C9  60          rts
  $58CA  AD 10 D0    lda  $D010
  $58CD  3D F0 4F    and  $4FF0, x
  $58D0  D0 F2       bne  $58C4
  $58D2  8A          txa
  $58D3  48          pha
  $58D4  0A          asl  a
  $58D5  AA          tax
  $58D6  BD 02 D0    lda  $D002, x
  $58D9  C9 40       cmp  #$40
  $58DB  F0 05       beq  $58E2
  $58DD  68          pla
  $58DE  AA          tax
  $58DF  4C C4 58    jmp  $58C4
  $58E2  68          pla
  $58E3  AA          tax
  $58E4  A9 09       lda  #$09
  $58E6  20 EC 58    jsr  $58EC
  $58E9  4C C4 58    jmp  $58C4
  $58EC  9D 80 0D    sta  $0D80, x
  $58EF  A9 30       lda  #$30
  $58F1  9D B8 0D    sta  $0DB8, x
  $58F4  60          rts
  $58F5  60          rts
  $58F6  60          rts
  $58F7  60          rts
  $58F8  60          rts
  $58F9  60          rts
  $58FA  60          rts
  $58FB  60          rts
  $58FC  60          rts
  $58FD  60          rts
  $58FE  60          rts
  $58FF  60          rts
  $5900  A2 00       ldx  #$00
  $5902  BD 80 0D    lda  $0D80, x
  $5905  C9 09       cmp  #$09
  $5907  F0 06       beq  $590F
  $5909  E8          inx
  $590A  E0 04       cpx  #$04
  $590C  D0 F4       bne  $5902
  $590E  60          rts
  $590F  DE B8 0D    dec  $0DB8, x
  $5912  D0 08       bne  $591C
  $5914  A9 01       lda  #$01
  $5916  9D 80 0D    sta  $0D80, x
  $5919  4C 09 59    jmp  $5909
  $591C  BD F9 07    lda  $07F9, x
  $591F  C9 9E       cmp  #$9E
  $5921  F0 08       beq  $592B
  $5923  A9 9E       lda  #$9E
  $5925  9D F9 07    sta  $07F9, x
  $5928  4C 09 59    jmp  $5909
  $592B  A9 9F       lda  #$9F
  $592D  4C 25 59    jmp  $5925
  $5930  AD B0 0D    lda  $0DB0
  $5933  D0 01       bne  $5936
  $5935  60          rts
  $5936  C9 01       cmp  #$01
  $5938  D0 51       bne  $598B
  $593A  CE B1 0D    dec  $0DB1
  $593D  F0 2A       beq  $5969
  $593F  A0 00       ldy  #$00
  $5941  20 80 59    jsr  $5980
  $5944  AD B1 0D    lda  $0DB1
  $5947  29 01       and  #$01
  $5949  F0 11       beq  $595C
  ... (47 more)
  ```
- ✓ **code_kb** `i1_s16`
  **→** Layer-1 annotation for $58AD-$58E9 (producer=analyst, conf=0.80):

Initializes variables at $0DB0 and $0DB1, then scans an entity array at $0D80-$0D83 (slots 0-3) for a state or type of 1 or 2. If a m
  ```
  Layer-1 annotation for $58AD-$58E9 (producer=analyst, conf=0.80):
  
  Initializes variables at $0DB0 and $0DB1, then scans an entity array at $0D80-$0D83 (slots 0-3) for a state or type of 1 or 2. If a matching entity is found, it proceeds to manipulate the corresponding sprite's X-coordinate MSB in $D010 using a bitmask table at $4FF0. If no match is found, it exits early.
  
  _motivation:_ GUESS: The loop over 4 slots suggests a limit of 4 active entities (e.g., ice cubes) tracked in this array. Using a lookup table at $4FF0 for bitmasks is a classic 6502 optimization to avoid slow dynamic bit-shifting when isolating or clearing specific sprite bits in VIC-II registers.
  
  _idiom: None_
  _name suggestion: start_ice_destruction_
  ```
- ✓ **vice** `i2_s1`
  **→** {"address": "$1E8A", "count": 100, "show_symbols": true}
  ```
  [vice.disassemble args={"address": "$1E8A", "count": 100, "show_symbols": true}]
  $1E8A: 9D 25 0D    STA $0D25,X
  $1E8D: 4C 85 19    JMP $1985
  $1E90: A9 01       LDA #$01
  $1E92: 4C 71 5A    JMP $5A71
  $1E95: AD 00 D0    LDA $D000
  $1E98: 29 0F       AND #$0F
  $1E9A: C9 00       CMP #$00
  $1E9C: F0 0B       BEQ $1EA9
  $1E9E: C9 02       CMP #$02
  $1EA0: F0 07       BEQ $1EA9
  $1EA2: C9 0E       CMP #$0E
  $1EA4: F0 03       BEQ $1EA9
  $1EA6: 4C 85 19    JMP $1985
  $1EA9: 20 00 1B    JSR $1B00
  $1EAC: A5 49       LDA $49
  $1EAE: 18          CLC
  $1EAF: 69 50       ADC #$50
  $1EB1: 85 49       STA $49
  $1EB3: A5 4A       LDA $4A
  $1EB5: 69 00       ADC #$00
  $1EB7: 85 4A       STA $4A
  $1EB9: A0 00       LDY #$00
  $1EBB: B1 49       LDA ($49),Y
  $1EBD: C9 88       CMP #$88
  $1EBF: D0 03       BNE $1EC4
  $1EC1: 4C 37 58    JMP $5837
  $1EC4: C9 80       CMP #$80
  $1EC6: F0 07       BEQ $1ECF
  $1EC8: C9 84       CMP #$84
  $1ECA: F0 03       BEQ $1ECF
  $1ECC: 4C 85 19    JMP $1985
  $1ECF: A2 00       LDX #$00
  $1ED1: BD 25 0D    LDA $0D25,X
  $1ED4: F0 06       BEQ $1EDC
  $1ED6: E8          INX
  $1ED7: E0 02       CPX #$02
  $1ED9: D0 F6       BNE $1ED1
  $1EDB: 60          RTS
  $1EDC: A5 49       LDA $49
  $1EDE: 9D 21 0D    STA $0D21,X
  $1EE1: A5 4A       LDA $4A
  $1EE3: 9D 23 0D    STA $0D23,X
  $1EE6: A5 49       LDA $49
  $1EE8: 18          CLC
  $1EE9: 69 50       ADC #$50
  $1EEB: 85 49       STA $49
  $1EED: A5 4A       LDA $4A
  $1EEF: 69 00       ADC #$00
  $1EF1: 85 4A       STA $4A
  $1EF3: B1 49       LDA ($49),Y
  $1EF5: C9 20       CMP #$20
  $1EF7: F0 08       BEQ $1F01
  $1EF9: A9 05       LDA #$05
  $1EFB: 9D 25 0D    STA $0D25,X
  $1EFE: 4C 85 19    JMP $1985
  $1F01: A9 01       LDA #$01
  $1F03: 4C 79 5A    JMP $5A79
  $1F06: AD 01 D0    LDA $D001
  $1F09: 29 0F       AND #$0F
  $1F0B: C9 00       CMP #$00
  $1F0D: F0 0B       BEQ $1F1A
  $1F0F: C9 02       CMP #$02
  $1F11: F0 07       BEQ $1F1A
  $1F13: C9 04       CMP #$04
  $1F15: F0 03       BEQ $1F1A
  $1F17: 4C 85 19    JMP $1985
  $1F1A: 20 00 1B    JSR $1B00
  $1F1D: A5 49       LDA $49
  $
  ```
- ✓ **vice** `i2_s2`
  **→** {"address": "$1EFB", "count": 100, "show_symbols": true}
  ```
  [vice.disassemble args={"address": "$1EFB", "count": 100, "show_symbols": true}]
  $1EFB: 9D 25 0D    STA $0D25,X
  $1EFE: 4C 85 19    JMP $1985
  $1F01: A9 01       LDA #$01
  $1F03: 4C 79 5A    JMP $5A79
  $1F06: AD 01 D0    LDA $D001
  $1F09: 29 0F       AND #$0F
  $1F0B: C9 00       CMP #$00
  $1F0D: F0 0B       BEQ $1F1A
  $1F0F: C9 02       CMP #$02
  $1F11: F0 07       BEQ $1F1A
  $1F13: C9 04       CMP #$04
  $1F15: F0 03       BEQ $1F1A
  $1F17: 4C 85 19    JMP $1985
  $1F1A: 20 00 1B    JSR $1B00
  $1F1D: A5 49       LDA $49
  $1F1F: 38          SEC
  $1F20: E9 01       SBC #$01
  $1F22: 85 49       STA $49
  $1F24: A5 4A       LDA $4A
  $1F26: E9 00       SBC #$00
  $1F28: 85 4A       STA $4A
  $1F2A: A0 00       LDY #$00
  $1F2C: B1 49       LDA ($49),Y
  $1F2E: C9 8B       CMP #$8B
  $1F30: D0 03       BNE $1F35
  $1F32: 4C AD 58    JMP $58AD
  $1F35: C9 81       CMP #$81
  $1F37: F0 07       BEQ $1F40
  $1F39: C9 85       CMP #$85
  $1F3B: F0 03       BEQ $1F40
  $1F3D: 4C 85 19    JMP $1985
  $1F40: A2 00       LDX #$00
  $1F42: BD 25 0D    LDA $0D25,X
  $1F45: F0 06       BEQ $1F4D
  $1F47: E8          INX
  $1F48: E0 02       CPX #$02
  $1F4A: D0 F6       BNE $1F42
  $1F4C: 60          RTS
  $1F4D: A5 49       LDA $49
  $1F4F: 20 A0 1B    JSR $1BA0
  $1F52: 4C 57 1F    JMP $1F57
  $1F55: EA          NOP
  $1F56: EA          NOP
  $1F57: A5 49       LDA $49
  $1F59: 38          SEC
  $1F5A: E9 01       SBC #$01
  $1F5C: 85 49       STA $49
  $1F5E: A5 4A       LDA $4A
  $1F60: E9 00       SBC #$00
  $1F62: 85 4A       STA $4A
  $1F64: B1 49       LDA ($49),Y
  $1F66: C9 20       CMP #$20
  $1F68: F0 08       BEQ $1F72
  $1F6A: A9 05       LDA #$05
  $1F6C: 9D 25 0D    STA $0D25,X
  $1F6F: 4C 85 19    JMP $1985
  $1F72: A9 04       LDA #$04
  $1F74: 4C 81 5A    JMP $5A81
  $1F77: AD 01 D0    LDA $D001
  $1F7A: 29 0F       AND #$0F
  $1F7C: C9 00       CMP #$00
  $1F7E: F0 0B       BEQ $1F8B
  $1F80: C9 02       CMP #$02
  $1F82: F0 07       BEQ $1F8B
  $1F84: C9 04       CMP #$04
  $1F86: F0 03       BEQ $1F8B
  $1F88: 4C 85 19    JMP $1985
  $1F8B: 20 00 1B    JSR $1B00
  $1F8E: A5 49
  ```
- ✓ **vice** `i2_s3`
  **→** {"address": "$1F6C", "count": 100, "show_symbols": true}
  ```
  [vice.disassemble args={"address": "$1F6C", "count": 100, "show_symbols": true}]
  $1F6C: 9D 25 0D    STA $0D25,X
  $1F6F: 4C 85 19    JMP $1985
  $1F72: A9 04       LDA #$04
  $1F74: 4C 81 5A    JMP $5A81
  $1F77: AD 01 D0    LDA $D001
  $1F7A: 29 0F       AND #$0F
  $1F7C: C9 00       CMP #$00
  $1F7E: F0 0B       BEQ $1F8B
  $1F80: C9 02       CMP #$02
  $1F82: F0 07       BEQ $1F8B
  $1F84: C9 04       CMP #$04
  $1F86: F0 03       BEQ $1F8B
  $1F88: 4C 85 19    JMP $1985
  $1F8B: 20 00 1B    JSR $1B00
  $1F8E: A5 49       LDA $49
  $1F90: 18          CLC
  $1F91: 69 02       ADC #$02
  $1F93: 85 49       STA $49
  $1F95: A5 4A       LDA $4A
  $1F97: 69 00       ADC #$00
  $1F99: 85 4A       STA $4A
  $1F9B: A0 00       LDY #$00
  $1F9D: B1 49       LDA ($49),Y
  $1F9F: C9 8B       CMP #$8B
  $1FA1: D0 03       BNE $1FA6
  $1FA3: 4C 6E 58    JMP $586E
  $1FA6: C9 80       CMP #$80
  $1FA8: F0 07       BEQ $1FB1
  $1FAA: C9 84       CMP #$84
  $1FAC: F0 03       BEQ $1FB1
  $1FAE: 4C 85 19    JMP $1985
  $1FB1: A2 00       LDX #$00
  $1FB3: BD 25 0D    LDA $0D25,X
  $1FB6: F0 06       BEQ $1FBE
  $1FB8: E8          INX
  $1FB9: E0 02       CPX #$02
  $1FBB: D0 F6       BNE $1FB3
  $1FBD: 60          RTS
  $1FBE: A5 49       LDA $49
  $1FC0: 9D 21 0D    STA $0D21,X
  $1FC3: A5 4A       LDA $4A
  $1FC5: 9D 23 0D    STA $0D23,X
  $1FC8: A5 49       LDA $49
  $1FCA: 18          CLC
  $1FCB: 69 02       ADC #$02
  $1FCD: 85 49       STA $49
  $1FCF: A5 4A       LDA $4A
  $1FD1: 69 00       ADC #$00
  $1FD3: 85 4A       STA $4A
  $1FD5: B1 49       LDA ($49),Y
  $1FD7: C9 20       CMP #$20
  $1FD9: F0 08       BEQ $1FE3
  $1FDB: A9 05       LDA #$05
  $1FDD: 9D 25 0D    STA $0D25,X
  $1FE0: 4C 85 19    JMP $1985
  $1FE3: A9 03       LDA #$03
  $1FE5: 4C 89 5A    JMP $5A89
  $1FE8: A5 49       LDA $49
  $1FEA: 38          SEC
  $1FEB: E9 28       SBC #$28
  $1FED: 85 49       STA $49
  $1FEF: A5 4A       LDA $4A
  $1FF1: E9 00       SBC #$00
  $1FF3: 85 4A       STA $4A
  $1FF5: A5 49       LDA $49
  $1FF7: 9D 21 0D    STA $0D21,X
  $1FFA: A5 4A       LDA $4A
  $1FFC: 9D 23 0D    STA $0D23,X
  $1FFF: 60
  ```
- ✓ **vice** `i2_s4`
  **→** {"address": "$1FDD", "count": 100, "show_symbols": true}
  ```
  [vice.disassemble args={"address": "$1FDD", "count": 100, "show_symbols": true}]
  $1FDD: 9D 25 0D    STA $0D25,X
  $1FE0: 4C 85 19    JMP $1985
  $1FE3: A9 03       LDA #$03
  $1FE5: 4C 89 5A    JMP $5A89
  $1FE8: A5 49       LDA $49
  $1FEA: 38          SEC
  $1FEB: E9 28       SBC #$28
  $1FED: 85 49       STA $49
  $1FEF: A5 4A       LDA $4A
  $1FF1: E9 00       SBC #$00
  $1FF3: 85 4A       STA $4A
  $1FF5: A5 49       LDA $49
  $1FF7: 9D 21 0D    STA $0D21,X
  $1FFA: A5 4A       LDA $4A
  $1FFC: 9D 23 0D    STA $0D23,X
  $1FFF: 60          RTS
  $2000: FF 81 BD    ISB $BD81,X
  $2003: A1 A1       LDA ($A1,X)
  $2005: BD 81 FF    LDA $FF81,X
  $2008: 00          BRK
  $2009: FE FE C6    INC $C6FE,X
  $200C: FE FE C6    INC $C6FE,X
  $200F: C6 00       DEC $00
  $2011: F0 F0       BEQ $2003
  $2013: D8          CLD
  $2014: FC CE FE    NOOP $FECE,X
  $2017: FE 00 FE    INC $FE00,X
  $201A: FE C0 C0    INC $C0C0,X
  $201D: C0 FE       CPY #$FE
  $201F: FE 00 F8    INC $F800,X
  $2022: FC CE C6    NOOP $C6CE,X
  $2025: C6 FE       DEC $FE
  $2027: FE 00 FE    INC $FE00,X
  $202A: FE C0 F8    INC $F8C0,X
  $202D: C0 FE       CPY #$FE
  $202F: FE 00 FE    INC $FE00,X
  $2032: FE C0 F8    INC $F8C0,X
  $2035: C0 C0       CPY #$C0
  $2037: C0 00       CPY #$00
  $2039: FE FE C0    INC $C0FE,X
  $203C: CE C6 FE    DEC $FEC6
  $203F: FE 00 C6    INC $C600,X
  $2042: C6 C6       DEC $C6
  $2044: FE FE C6    INC $C6FE,X
  $2047: C6 00       DEC $00
  $2049: FE FE 30    INC $30FE,X
  $204C: 30 30       BMI $207E
  $204E: FE FE 00    INC $00FE,X
  $2051: FE FE 0C    INC $0CFE,X
  $2054: 0C 0C 7C    NOOP $7C0C
  $2057: 7C 00 C6    NOOP $C600,X
  $205A: DE FC F0    DEC $F0FC,X
  $205D: FC DE C6    NOOP $C6DE,X
  $2060: 00          BRK
  $2061: C0 C0       CPY #$C0
  $2063: C0 C0       CPY #$C0
  $2065: C0 FE       CPY #$FE
  $2067: FE 00 C6    INC $C600,X
  $206A: EE FE FE    INC $FEFE
  $206D: D6 C6       DEC $C6,X
  $206F: C6 00       DEC $00
  $2071: C6 E6       DEC $E6
  $2073: F6 FE       INC $FE,X
  $2075: DE CE C6    DEC $C6CE,X
  $2078: 00          BRK
  $2079: FE FE C6    INC $C6FE,X
  $207C: C6 C6
  ```
- ✓ **capstone** `i2_s5`
  **→** $1F6C  9D 25 0D    sta  $0D25, x
$1F6F  4C 85 19    jmp  $1985
$1F72  A9 04       lda  #$04
$1F74  4C 81 5A    jmp  $5A8
  ```
  $1F6C  9D 25 0D    sta  $0D25, x
  $1F6F  4C 85 19    jmp  $1985
  $1F72  A9 04       lda  #$04
  $1F74  4C 81 5A    jmp  $5A81
  $1F77  AD 01 D0    lda  $D001
  $1F7A  29 0F       and  #$0F
  $1F7C  C9 00       cmp  #$00
  $1F7E  F0 0B       beq  $1F8B
  $1F80  C9 02       cmp  #$02
  $1F82  F0 07       beq  $1F8B
  $1F84  C9 04       cmp  #$04
  $1F86  F0 03       beq  $1F8B
  $1F88  4C 85 19    jmp  $1985
  $1F8B  20 00 1B    jsr  $1B00
  $1F8E  A5 49       lda  $49
  $1F90  18          clc
  $1F91  69 02       adc  #$02
  $1F93  85 49       sta  $49
  $1F95  A5 4A       lda  $4A
  $1F97  69 00       adc  #$00
  $1F99  85 4A       sta  $4A
  $1F9B  A0 00       ldy  #$00
  $1F9D  B1 49       lda  ($49), y
  $1F9F  C9 8B       cmp  #$8B
  $1FA1  D0 03       bne  $1FA6
  $1FA3  4C 6E 58    jmp  $586E
  $1FA6  C9 80       cmp  #$80
  $1FA8  F0 07       beq  $1FB1
  $1FAA  C9 84       cmp  #$84
  $1FAC  F0 03       beq  $1FB1
  $1FAE  4C 85 19    jmp  $1985
  $1FB1  A2 00       ldx  #$00
  $1FB3  BD 25 0D    lda  $0D25, x
  $1FB6  F0 06       beq  $1FBE
  $1FB8  E8          inx
  $1FB9  E0 02       cpx  #$02
  $1FBB  D0 F6       bne  $1FB3
  $1FBD  60          rts
  $1FBE  A5 49       lda  $49
  $1FC0  9D 21 0D    sta  $0D21, x
  $1FC3  A5 4A       lda  $4A
  $1FC5  9D 23 0D    sta  $0D23, x
  $1FC8  A5 49       lda  $49
  $1FCA  18          clc
  $1FCB  69 02       adc  #$02
  $1FCD  85 49       sta  $49
  $1FCF  A5 4A       lda  $4A
  $1FD1  69 00       adc  #$00
  $1FD3  85 4A       sta  $4A
  $1FD5  B1 49       lda  ($49), y
  $1FD7  C9 20       cmp  #$20
  $1FD9  F0 08       beq  $1FE3
  $1FDB  A9 05       lda  #$05
  $1FDD  9D 25 0D    sta  $0D25, x
  $1FE0  4C 85 19    jmp  $1985
  $1FE3  A9 03       lda  #$03
  $1FE5  4C 89 5A    jmp  $5A89
  $1FE8  A5 49       lda  $49
  $1FEA  38          sec
  $1FEB  E9 28       sbc  #$28
  $1FED  85 49       sta  $49
  $1FEF  A5 4A       lda  $4A
  $1FF1  E9 00       sbc  #$00
  $1FF3  85 4A       sta  $4A
  $1FF5  A5 49       lda  $49
  $1FF7  9D 21 0D    sta  $0D21, x
  $1FFA  A5 4A       lda  $4A
  $1FFC  9D 23 0D    sta  $0D23, x
  $1FFF  60          rts
  ```
- ✓ **kb** `i2_s6`
  **→** 2 hit(s) for '800':
  ```
  2 hit(s) for '800':
  - /Users/marci/building_agents/C64RE_agent/text_dir/petch/start.txt (size=3621, match_at=1170)
    …...8D 1F 0D    STA $0D1F
  .C:1028  20 C3 10    JSR $10C3
  .C:102b  20 00 38    JSR $3800
  .C:102e  20 00 43    JSR $4300
  .C:1031  20 00 3D    JSR $3D00
  .C:1034  20 80 48...…
  - /Users/marci/building_agents/C64RE_agent/text_dir/petch/enemy_ai.txt (size=6882, match_at=4252)
    …...lback
  491b  4C 20 47     JMP $4720         ; move LEFT
  491e  20 00 48     JSR $4800         ; check RIGHT passable
  4921  D0 D1        BNE $48F4         ; blocked -...…
  ```
- ✓ **vice** `i2_s7`
  **→** {"address": "$5A61", "count": 40, "show_symbols": true}
  ```
  [vice.disassemble args={"address": "$5A61", "count": 40, "show_symbols": true}]
  $5A61: A9 01       LDA #$01
  $5A63: 8D 01 79    STA $7901
  $5A66: A9 20       LDA #$20
  $5A68: 8D 02 79    STA $7902
  $5A6B: A9 01       LDA #$01
  $5A6D: 8D 00 79    STA $7900
  $5A70: 60          RTS
  $5A71: 20 61 5A    JSR $5A61
  $5A74: A9 01       LDA #$01
  $5A76: 4C 8A 1E    JMP $1E8A
  $5A79: 20 61 5A    JSR $5A61
  $5A7C: A9 02       LDA #$02
  $5A7E: 4C FB 1E    JMP $1EFB
  $5A81: 20 61 5A    JSR $5A61
  $5A84: A9 04       LDA #$04
  $5A86: 4C 6C 1F    JMP $1F6C
  $5A89: 20 61 5A    JSR $5A61
  $5A8C: A9 03       LDA #$03
  $5A8E: 4C DD 1F    JMP $1FDD
  $5A91: 9D 25 0D    STA $0D25,X
  $5A94: AD 25 0D    LDA $0D25
  $5A97: D0 0D       BNE $5AA6
  $5A99: AD 26 0D    LDA $0D26
  $5A9C: D0 08       BNE $5AA6
  $5A9E: A9 00       LDA #$00
  $5AA0: 8D 00 79    STA $7900
  $5AA3: 8D 04 D4    STA $D404
  $5AA6: A9 00       LDA #$00
  $5AA8: 4C A1 3B    JMP $3BA1
  $5AAB: 9D 80 0D    STA $0D80,X
  $5AAE: A9 10       LDA #$10
  $5AB0: 8D 12 79    STA $7912
  $5AB3: A9 03       LDA #$03
  $5AB5: 8D 11 79    STA $7911
  $5AB8: A9 02       LDA #$02
  $5ABA: 8D 10 79    STA $7910
  $5ABD: 60          RTS
  $5ABE: EA          NOP
  $5ABF: EA          NOP
  $5AC0: 8A          TXA
  ```
- ✓ **code_kb** `i2_s8`
  **→** [
  {
    "src_addr": 7931,
    "kind": "jsr",
    "annotation_id": "86da70cbac05",
    "src_hex": "$1EFB"
  },
  {
    "src_addr": 8044,
    "kind": "jsr",
    "annotation_id": "49ae5735efe1",
    "s
  ```
  [
    {
      "src_addr": 7931,
      "kind": "jsr",
      "annotation_id": "86da70cbac05",
      "src_hex": "$1EFB"
    },
    {
      "src_addr": 8044,
      "kind": "jsr",
      "annotation_id": "49ae5735efe1",
      "src_hex": "$1F6C"
    },
    {
      "src_addr": 8050,
      "kind": "jsr",
      "annotation_id": "fada3def5389",
      "src_hex": "$1F72"
    }
  ]
  ```
- ✓ **kb** `i2_s9`
  **→** [
  ```
  [
    {
      "addr": 3455,
      "name": "max_score_or_level",
      "kind": "ram_var",
      "confidence": 0.5,
      "addr_hex": "$0D7F"
    }
  ]
  ```
- ✓ **code_kb** `i2_s10`
  **→** Layer-1 annotation for $1F6C-$1FFF (producer=critic, conf=0.80):

Checks Sprite 0 Y-coordinate for grid alignment, then inspects screen memory via a pointer at $49 to detect specific block characters 
  ```
  Layer-1 annotation for $1F6C-$1FFF (producer=critic, conf=0.80):
  
  Checks Sprite 0 Y-coordinate for grid alignment, then inspects screen memory via a pointer at $49 to detect specific block characters ($8B, $80, $84). If a match is found, it allocates an animation entity by finding a free slot in a table at $0D25, storing the screen pointer into $0D21/$0D23, and setting an initial state or timer.
  
  _motivation:_ GUESS: The programmer used a table-based entity system for temporary animations (like block destruction). The pointer at $49 is manipulated by adding 2 (moving right, likely for 2-char wide blocks) or subtracting 40 ($28, moving up one row) to check adjacent tiles. The missing bytes in the listing ($1FB8-$1FBD) almost certainly contain the INX/BNE loop to find a free entity slot.
  
  _idiom: None_
  _name suggestion: spawn_block_destruction_anim_
  ```

## KB stats

```
{
  "events_total": 778,
  "events_by_kind": {
    "analysis": 13,
    "consolidated_observation": 59,
    "data_structure": 28,
    "hypothesis": 74,
    "ingest_dump": 1,
    "ingest_text": 2,
    "label": 292,
    "routine": 129,
    "tool_result": 167,
    "verdict": 13
  },
  "labels": 214,
  "text_docs": 2,
  "dump_bytes": 65536,
  "semantic_kb_enabled": false,
  "semantic_kb_ready": false,
  "semantic_kb_chunks": 0
}
```

---
_generated 2026-05-16T20:17:32.146240+00:00_
