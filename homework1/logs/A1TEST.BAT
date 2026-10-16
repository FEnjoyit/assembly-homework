@echo off
cd \work
masm A1LEA.ASM,A1LEA.OBJ,A1LEA.LST; > d:\tests\A1ASM1.LOG
if errorlevel 1 goto fail
link A1LEA.OBJ,A1LEA.EXE,A1LEA.MAP; > d:\tests\A1LNK1.LOG
if errorlevel 1 goto fail
masm A1OFF.ASM,A1OFF.OBJ,A1OFF.LST; > d:\tests\A1ASM2.LOG
if errorlevel 1 goto fail
link A1OFF.OBJ,A1OFF.EXE,A1OFF.MAP; > d:\tests\A1LNK2.LOG
if errorlevel 1 goto fail
A1LEA.EXE > d:\tests\A1LEA.TXT
if errorlevel 1 goto fail
A1OFF.EXE > d:\tests\A1OFF.TXT
if errorlevel 1 goto fail
debug A1LEA.EXE < d:\tests\A1LEA.IN > d:\tests\A1LEA.OUT
debug A1OFF.EXE < d:\tests\A1OFF.IN > d:\tests\A1OFF.OUT
debug < d:\tests\A1MEM.IN > d:\tests\A1MEM.OUT
debug < A1MEM.DBG > d:\tests\A1MAN.OUT
echo A1_ALL_COMPLETE > d:\tests\A1RESULT.TXT
goto end
:fail
echo A1_FAILED > d:\tests\A1RESULT.TXT
:end
