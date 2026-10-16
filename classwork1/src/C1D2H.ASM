; Classwork 1 extra: unsigned decimal (0..65535) -> hexadecimal.
; MASM 5.0 / 8086 / 16-bit DOS. ASCII source, no BOM.
.MODEL SMALL
.STACK 100H
.DATA
    PROMPT DB 'Please input a Dec number (0-65535):',13,10,'$'
    ANSWER DB 'The Hex number:',13,10,'$'
    BADMSG DB 'Invalid input. Enter a decimal number from 0 to 65535.',13,10,'$'
    CRLF   DB 13,10,'$'
    INPUT  DB 80,0,80 DUP (0)
    VALUE  DW 0
.CODE
START:
    MOV AX,@DATA
    MOV DS,AX
READ_AGAIN:
    LEA DX,PROMPT
    MOV AH,09H
    INT 21H
    MOV BYTE PTR INPUT[1],0
    LEA DX,INPUT
    MOV AH,0AH
    INT 21H
    CALL NEWLINE
    XOR CX,CX
    MOV CL,INPUT[1]
    CMP CX,1
    JB INVALID
    CMP CX,5
    JA INVALID
    LEA SI,INPUT[2]
    XOR AX,AX
    MOV BX,10
DEC_NEXT:
    MOV DL,[SI]
    CMP DL,'0'
    JB INVALID
    CMP DL,'9'
    JA INVALID
    SUB DL,'0'
    XOR DH,DH
    MOV DI,DX
    ; DX:AX = old_value * 10. Detect overflow before truncation.
    MUL BX
    OR DX,DX
    JNZ INVALID
    ADD AX,DI
    JC INVALID
    INC SI
    LOOP DEC_NEXT
    MOV VALUE,AX
    LEA DX,ANSWER
    MOV AH,09H
    INT 21H
    MOV AX,VALUE
    CALL PRINT_HEX
    CALL NEWLINE
    MOV AX,4C00H
    INT 21H
INVALID:
    LEA DX,BADMSG
    MOV AH,09H
    INT 21H
    JMP READ_AGAIN

; Input AX = unsigned value. Output uppercase, no leading zeroes.
PRINT_HEX PROC NEAR
    PUSH AX
    PUSH BX
    PUSH CX
    PUSH DX
    MOV BX,16
    XOR CX,CX
HEX_DIVIDE:
    XOR DX,DX
    DIV BX
    PUSH DX
    INC CX
    OR AX,AX
    JNZ HEX_DIVIDE
HEX_OUTPUT:
    POP DX
    CMP DL,9
    JBE HEX_NUMBER
    ADD DL,'A'-10
    JMP HEX_WRITE
HEX_NUMBER:
    ADD DL,'0'
HEX_WRITE:
    MOV AH,02H
    INT 21H
    LOOP HEX_OUTPUT
    POP DX
    POP CX
    POP BX
    POP AX
    RET
PRINT_HEX ENDP

NEWLINE PROC NEAR
    PUSH AX
    PUSH DX
    LEA DX,CRLF
    MOV AH,09H
    INT 21H
    POP DX
    POP AX
    RET
NEWLINE ENDP
END START
