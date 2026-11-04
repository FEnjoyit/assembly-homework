; Assignment 4, part 2: scan all 81 bytes, report wrong coordinates.
.MODEL SMALL
.STACK 100H
.DATA
    HEADER_MSG DB 'x y',13,10,'$'
    ERROR_MSG  DB '   error',13,10,'$'
    DONE_MSG   DB 13,10,'accomplish!',13,10,'$'
    TABLE_DATA DB 7,2,3,4,5,6,7,8,9
               DB 2,4,7,8,10,12,14,16,18
               DB 3,6,9,12,15,18,21,24,27
               DB 4,8,12,16,7,24,28,32,36
               DB 5,10,15,20,25,30,35,40,45
               DB 6,12,18,24,30,7,42,48,54
               DB 7,14,21,28,35,42,49,56,63
               DB 8,16,24,32,40,48,56,7,72
               DB 9,18,27,36,45,54,63,72,81
.CODE
START:
    MOV AX,@DATA
    MOV DS,AX
    LEA DX,HEADER_MSG
    MOV AH,09H
    INT 21H
    MOV BX,1
    XOR DI,DI
ROW_LOOP:
    MOV CX,9
    MOV SI,1
COL_LOOP:
    CALL CHECK_CELL
CELL_RETURN:
    INC DI
    INC SI
    LOOP COL_LOOP
    INC BX
    CMP BX,9
    JBE ROW_LOOP
    LEA DX,DONE_MSG
    MOV AH,09H
    INT 21H
    MOV AX,4C00H
    INT 21H

; BX = row, SI = column, DI = zero-based row-major index, CX = loop count.
CHECK_CELL PROC NEAR
    PUSH AX
    PUSH DX
    MOV AX,SI
    MUL BL
    CMP AL,TABLE_DATA[DI]
    JE CELL_DONE
    MOV AX,BX
    CALL PRINT_DEC
    MOV DL,' '
    CALL PUT_CHAR
    MOV AX,SI
    CALL PRINT_DEC
    LEA DX,ERROR_MSG
    MOV AH,09H
    INT 21H
CELL_DONE:
    POP DX
    POP AX
    RET
CHECK_CELL ENDP
INCLUDE H4IO.INC
END START
