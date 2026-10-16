@echo off
masm A2LOOP.ASM,A2LOOP.OBJ,A2LOOP.LST;
if errorlevel 1 goto fail
link A2LOOP.OBJ,A2LOOP.EXE,A2LOOP.MAP;
if errorlevel 1 goto fail
masm A2JUMP.ASM,A2JUMP.OBJ,A2JUMP.LST;
if errorlevel 1 goto fail
link A2JUMP.OBJ,A2JUMP.EXE,A2JUMP.MAP;
if errorlevel 1 goto fail
echo Both assembly programs built successfully.
goto end
:fail
echo Build failed. Fix the displayed error before running.
:end
