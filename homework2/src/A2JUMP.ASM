; Assignment 2, part 2: the same output using conditional jumps.
; MASM 5.0, 8086, 16-bit DOS. No LOOP instruction is used.

STACKSEG SEGMENT STACK
    DW 128 DUP (?)
STACKSEG ENDS

CODESEG SEGMENT
    ASSUME CS:CODESEG, SS:STACKSEG
START:
    MOV BL, 'a'             ; ASCII 61H, the first lowercase letter.
    MOV SI, 2               ; SI counts the two rows.
ROW_LOOP:
    MOV DI, 13              ; DI counts thirteen letters in each row.
COL_LOOP:
    MOV DL, BL
    MOV AH, 02H
    INT 21H                 ; Print the current letter.
    INC BL
    CMP DI, 1
    JE ROW_END              ; Skip the space after the last letter.
    MOV DL, ' '
    MOV AH, 02H
    INT 21H
ROW_END:
    DEC DI                  ; DEC sets ZF according to the new count.
    JNZ COL_LOOP            ; ZF = 0 means more columns remain.
    MOV DL, 0DH
    MOV AH, 02H
    INT 21H
    MOV DL, 0AH
    MOV AH, 02H
    INT 21H
    DEC SI
    JNZ ROW_LOOP            ; Repeat while more rows remain.
    MOV AX, 4C00H
    INT 21H
CODESEG ENDS
END START
