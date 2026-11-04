; Assignment 4, part 1: descending triangular multiplication table.
.MODEL SMALL
.STACK 100H
.DATA
    TITLE_MSG DB 'The 9mul9 table:',13,10,'$'
.CODE
START:
    MOV AX,@DATA
    MOV DS,AX
    LEA DX,TITLE_MSG
    MOV AH,09H
    INT 21H
    MOV BX,9
ROW_LOOP:
    MOV CX,BX
    MOV SI,1
COL_LOOP:
    CALL PRINT_TERM
TERM_RETURN:
    INC SI
    LOOP COL_LOOP
    CALL NEWLINE
    DEC BX
    JNZ ROW_LOOP
    MOV AX,4C00H
    INT 21H

; BX = row, SI = column, CX = number of remaining terms in row.
; Borrow CX for the padding loop and restore it before RET.
PRINT_TERM PROC NEAR
    PUSH AX
    PUSH CX
    PUSH DX
    MOV AX,BX
    CALL PRINT_DEC
    MOV DL,'*'
    CALL PUT_CHAR
    MOV AX,SI
    CALL PRINT_DEC
    MOV DL,'='
    CALL PUT_CHAR
    MOV AX,SI
    MUL BL
    CALL PRINT_DEC
    CMP CX,1
    JE TERM_DONE
    MOV CX,2
    CMP AX,10
    JAE TERM_PAD
    INC CX
TERM_PAD:
    MOV DL,' '
    CALL PUT_CHAR
    LOOP TERM_PAD
TERM_DONE:
    POP DX
    POP CX
    POP AX
    RET
PRINT_TERM ENDP
INCLUDE H4IO.INC
END START
