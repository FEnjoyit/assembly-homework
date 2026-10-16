; Assignment 2, part 1: lowercase ASCII, 13 letters per line.
; MASM 5.0, 8086, 16-bit DOS. Save as ASCII or GBK without BOM.
; Both row and column loops use LOOP. PUSH/POP preserve outer CX.

STACKSEG SEGMENT STACK
    DW 128 DUP (?)
STACKSEG ENDS

CODESEG SEGMENT
    ASSUME CS:CODESEG, SS:STACKSEG
START:
    MOV BL, 'a'             ; BL = next lowercase ASCII character.
    MOV CX, 2               ; Outer loop: two rows.
ROW_LOOP:
    PUSH CX                 ; Save the outer counter before reusing CX.
    MOV CX, 13              ; Inner loop: thirteen letters in this row.
COL_LOOP:
    MOV DL, BL
    MOV AH, 02H             ; DOS function 02H: print character in DL.
    INT 21H
    INC BL                  ; Next ASCII letter, a through z.
    CMP CX, 1               ; The last letter needs no following space.
    JE ROW_END              ; Formatting only; not a loop-control jump.
    MOV DL, ' '
    MOV AH, 02H
    INT 21H
ROW_END:
    LOOP COL_LOOP           ; CX = CX - 1; repeat while CX is nonzero.
    MOV DL, 0DH             ; DOS line ending: CR followed by LF.
    MOV AH, 02H
    INT 21H
    MOV DL, 0AH
    MOV AH, 02H
    INT 21H
    POP CX                  ; Restore the outer counter (2, then 1).
    LOOP ROW_LOOP           ; Next row; stops after exactly two rows.
    MOV AX, 4C00H           ; Return to DOS with exit code zero.
    INT 21H
CODESEG ENDS
END START
