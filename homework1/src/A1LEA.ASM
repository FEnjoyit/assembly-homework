; Assignment 1: Hello world, using LEA (MASM 5.0 / 8086 DOS).
.MODEL SMALL
.STACK 100H
.DATA
Hello DB 'Hello world!',0DH,0AH,'$'
.CODE
START:
    MOV AX,@DATA
    MOV DS,AX
    LEA DX,Hello
    MOV AH,09H
    INT 21H
    MOV AX,4C00H
    INT 21H
END START
