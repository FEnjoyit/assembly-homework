# 共用课程环境

实验主机为 Windows 11 64 位，课程程序为 16 位 DOS 程序，使用独立的 DOSBox-X 环境运行。

| 工具 | 本次实际版本 | 用途 |
| --- | --- | --- |
| DOSBox-X | 2026.10.01 x64 SDL2 | 运行 DOS、MASM、LINK、DEBUG 及作业 EXE |
| MASM | Microsoft 5.00 | 汇编 ASM 为 OBJ，生成 LST |
| LINK | Microsoft 3.60 | 链接 OBJ 为 EXE，生成 MAP |
| DEBUG | FreeDOS 2.50 | `e` 写内存、`u` 反汇编、`r` 看寄存器、`t` 单步、`g` 执行 |
| Open Watcom C16 / WDIS | 2.0beta1 LA | 作业2、作业3的 8086 DOS C 编译与反汇编 |

MASM/LINK 使用课程提供的软件包。安装 DOSBox-X 后，将课程工具目录挂载为工具盘并加入 DOS PATH，再按根目录 README 挂载单次作业目录。

```text
mount c "C:\path\to\course-tools"
path c:\bin;z:\
mount d "C:\path\to\assembly-homework\homework1"
d:
bin\a1lea
debug < src\a1mem.dbg
```

其中 `course-tools\bin` 应含 MASM.EXE、LINK.EXE、DEBUG.COM。工具目录不同时，相应调整挂载路径。进入 `src` 后可以逐行汇编、链接：

```text
cd \src
masm a1lea.asm,a1lea.obj,a1lea.lst;
link a1lea.obj,a1lea.exe,a1lea.map;
a1lea
debug a1lea.exe
u cs:0 l12
q
```

程序运行前要确认汇编链接成功，避免误运行旧 EXE。DEBUG 输入的数字按十六进制解释；`tm 1` 使用本实验的中断跟踪模式。DEBUG.COM 是调试器本身的文件格式，可以调试 EXE。

运行时段地址以寄存器显示为准。作业1的直接写内存方案以当前 CS 为基准。

作业2 C 的实际编译和反汇编命令：

```text
wcl -0 -ms -bt=dos -l=dos -od -d2 -s -w=4 -we -fe=A2C.EXE -fo=A2C.OBJ -fm=A2C.MAP A2C.C
wdis -s=A2C.C -l=A2C_DIS.TXT A2C.OBJ
```

工具来源：

- [DOSBox-X 官方网站](https://dosbox-x.com/)
- [DOSBox-X 本次使用版本](https://github.com/joncampbell123/dosbox-x/releases/tag/dosbox-x-v2026.10.01)
- [FreeDOS DEBUG 作者项目](https://github.com/Baron-von-Riedesel/DOS-debug)
- [Open Watcom 官方网站](https://openwatcom.org/)
