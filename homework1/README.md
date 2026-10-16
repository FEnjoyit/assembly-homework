# 作业1：Hello world

- [实验报告](作业1_报告.md)
- [src/A1LEA.ASM](src/A1LEA.ASM) → [bin/A1LEA.EXE](bin/A1LEA.EXE)：传统 LEA 版本。
- [src/A1OFF.ASM](src/A1OFF.ASM) → [bin/A1OFF.EXE](bin/A1OFF.EXE)：传统 MOV OFFSET 版本。
- [src/A1MEM.DBG](src/A1MEM.DBG)：DEBUG e 直接写代码和数据，再执行。
- [真实反汇编中文注释](反汇编_逐行注释.txt) · [原始日志](logs/) · [23/23 项验证](验证结果.json)

挂载本目录为 DOSBox 的 D 盘后，运行 `bin\a1lea`、`bin\a1off`；直接写入运行 `debug < src\a1mem.dbg`。环境配置见 [共用说明](../environment/README.md)。
