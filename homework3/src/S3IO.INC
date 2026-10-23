; Common 8086 decimal output routines. Input AX is preserved.
PRINT_DEC PROC NEAR
    PUSH AX
    PUSH BX
    PUSH CX
    PUSH DX
    MOV BX,10
    XOR CX,CX
PD_DIVIDE:
    XOR DX,DX
    DIV BX
    PUSH DX
    INC CX
    OR AX,AX
    JNZ PD_DIVIDE
PD_WRITE:
    POP DX
    ADD DL,'0'
    MOV AH,02H
    INT 21H
    LOOP PD_WRITE
    POP DX
    POP CX
    POP BX
    POP AX
    RET
PRINT_DEC ENDP

NEWLINE PROC NEAR
    PUSH AX
    PUSH DX
    MOV DL,13
    MOV AH,02H
    INT 21H
    MOV DL,10
    MOV AH,02H
    INT 21H
    POP DX
    POP AX
    RET
NEWLINE ENDP
