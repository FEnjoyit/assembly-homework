@echo off
masm A1LEA.ASM,A1LEA.OBJ,A1LEA.LST;
if errorlevel 1 goto fail
link A1LEA.OBJ,A1LEA.EXE,A1LEA.MAP;
if errorlevel 1 goto fail
masm A1OFF.ASM,A1OFF.OBJ,A1OFF.LST;
if errorlevel 1 goto fail
link A1OFF.OBJ,A1OFF.EXE,A1OFF.MAP;
if errorlevel 1 goto fail
echo Assignment 1 build complete.
goto end
:fail
echo Assignment 1 build failed. Fix the error before running.
:end
