@echo off
masm C1H2D.ASM,C1H2D.OBJ,C1H2D.LST;
if errorlevel 1 goto fail
link C1H2D.OBJ,C1H2D.EXE,C1H2D.MAP;
if errorlevel 1 goto fail
masm C1D2H.ASM,C1D2H.OBJ,C1D2H.LST;
if errorlevel 1 goto fail
link C1D2H.OBJ,C1D2H.EXE,C1D2H.MAP;
if errorlevel 1 goto fail
echo Classwork 1 build complete.
goto end
:fail
echo Classwork 1 build failed. Fix errors before running.
:end
