@echo off
masm H6CAL.ASM,H6CAL.OBJ,H6CAL.LST;
if errorlevel 1 goto end
link H6CAL.OBJ,H6CAL.EXE,H6CAL.MAP;
if errorlevel 1 goto end
masm H6JUMP.ASM,H6JUMP.OBJ,H6JUMP.LST;
if errorlevel 1 goto end
link H6JUMP.OBJ,H6JUMP.EXE,H6JUMP.MAP;
:end
