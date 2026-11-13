@echo off
masm H5FIB.ASM,H5FIB.OBJ,H5FIB.LST;
if errorlevel 1 goto failed
link H5FIB.OBJ,H5FIB.EXE,H5FIB.MAP;
if errorlevel 1 goto failed
echo Homework 5 assembly build complete.
goto end
:failed
echo Build failed. Fix errors before running.
:end
