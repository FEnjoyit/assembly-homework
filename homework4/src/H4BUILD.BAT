@echo off
masm H4TAB.ASM,H4TAB.OBJ,H4TAB.LST;
if errorlevel 1 goto fail
link H4TAB.OBJ,H4TAB.EXE,H4TAB.MAP;
if errorlevel 1 goto fail
masm H4CHK.ASM,H4CHK.OBJ,H4CHK.LST;
if errorlevel 1 goto fail
link H4CHK.OBJ,H4CHK.EXE,H4CHK.MAP;
if errorlevel 1 goto fail
echo Homework 4 assembly build complete.
goto end
:fail
echo Build failed. Fix errors before running.
:end
