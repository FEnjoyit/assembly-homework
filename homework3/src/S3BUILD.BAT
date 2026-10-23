@echo off
masm S3REG.ASM,S3REG.OBJ,S3REG.LST;
if errorlevel 1 goto fail
link S3REG.OBJ,S3REG.EXE,S3REG.MAP;
if errorlevel 1 goto fail
masm S3DATA.ASM,S3DATA.OBJ,S3DATA.LST;
if errorlevel 1 goto fail
link S3DATA.OBJ,S3DATA.EXE,S3DATA.MAP;
if errorlevel 1 goto fail
masm S3STACK.ASM,S3STACK.OBJ,S3STACK.LST;
if errorlevel 1 goto fail
link S3STACK.OBJ,S3STACK.EXE,S3STACK.MAP;
if errorlevel 1 goto fail
masm S3INPUT.ASM,S3INPUT.OBJ,S3INPUT.LST;
if errorlevel 1 goto fail
link S3INPUT.OBJ,S3INPUT.EXE,S3INPUT.MAP;
if errorlevel 1 goto fail
echo Assignment 3 assembly build complete.
goto end
:fail
echo Build failed. Fix errors before running.
:end
