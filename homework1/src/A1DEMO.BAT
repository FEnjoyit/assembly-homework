@echo off
echo [1] Traditional assembly: LEA
A1LEA.EXE
echo.
echo [2] Traditional assembly: MOV OFFSET
A1OFF.EXE
echo.
echo [3] Direct memory entry using DEBUG E commands
debug < A1MEM.DBG
echo.
echo Assignment 1 demonstration complete.
