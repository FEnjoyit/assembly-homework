; Classwork 1: one or two hexadecimal digits -> decimal (0..255).
; MASM 5.0 / 8086 / 16-bit DOS. ASCII source, no BOM.
.MODEL SMALL
.STACK 100H
.DATA
    PROMPT DB 'Please input a Hex number:',13,10,'$'
    ANSWER DB 'The Dec number:',13,10,'$'
    BADMSG DB 'Invalid input. Enter 1 or 2 hex digits (0-9, A-F).',13,10,'$'
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
    CMP CX,2
    JA INVALID
    LEA SI,INPUT[2]
    XOR BX,BX
HEX_NEXT:
    MOV AL,[SI]
    CALL HEX_DIGIT
    JC INVALID
    ; Four single-bit shifts are valid 8086 instructions.
    SHL BX,1
    SHL BX,1
    SHL BX,1
    SHL BX,1
    XOR AH,AH
    ADD BX,AX
    INC SI
    LOOP HEX_NEXT
    MOV VALUE,BX
    LEA DX,ANSWER
    MOV AH,09H
    INT 21H
    MOV AX,VALUE
    CALL PRINT_DEC
    CALL NEWLINE
    MOV AX,4C00H
    INT 21H
INVALID:
    LEA DX,BADMSG
    MOV AH,09H
    INT 21H
    JMP READ_AGAIN

; Input AL = ASCII digit; output AL = 0..15, CF=0 on success.
HEX_DIGIT PROC NEAR
    CMP AL,'0'
    JB HEX_BAD
    CMP AL,'9'
    JBE HEX_NUMBER
    CMP AL,'A'
    JB HEX_BAD
    CMP AL,'F'
    JBE HEX_UPPER
    CMP AL,'a'
    JB HEX_BAD
    CMP AL,'f'
    JA HEX_BAD
    SUB AL,'a'-10
    CLC
    RET
HEX_UPPER:
    SUB AL,'A'-10
    CLC
    RET
HEX_NUMBER:
    SUB AL,'0'
    CLC
    RET
HEX_BAD:
    STC
    RET
HEX_DIGIT ENDP

; Input AX = unsigned value. Repeated DIV 10, then reverse remainders.
PRINT_DEC PROC NEAR
    PUSH AX
    PUSH BX
    PUSH CX
    PUSH DX
    MOV BX,10
    XOR CX,CX
DEC_DIVIDE:
    XOR DX,DX
    DIV BX
    PUSH DX
    INC CX
    OR AX,AX
    JNZ DEC_DIVIDE
DEC_OUTPUT:
    POP DX
    ADD DL,'0'
    MOV AH,02H
    INT 21H
    LOOP DEC_OUTPUT
    POP DX
    POP CX
    POP BX
    POP AX
    RET
PRINT_DEC ENDP

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
