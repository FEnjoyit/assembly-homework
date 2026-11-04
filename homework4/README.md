# 作业4：乘法指令和过程调用

| 程序 | 源码 | EXE |
| --- | --- | --- |
| 汇编乘法表 | [H4TAB.ASM](src/H4TAB.ASM) | [H4TAB.EXE](bin/H4TAB.EXE) |
| 汇编纠错 | [H4CHK.ASM](src/H4CHK.ASM) | [H4CHK.EXE](bin/H4CHK.EXE) |
| C 乘法表 | [H4TAB.C](src/H4TAB.C) | [H4CTAB.EXE](bin/H4CTAB.EXE) |
| C 全局数组纠错 | [H4CHK.C](src/H4CHK.C) | [H4CGLOB.EXE](bin/H4CGLOB.EXE) |
| C 局部数组纠错 | [H4CHK.C](src/H4CHK.C)，定义 `LOCAL_TABLE` | [H4CLOC.EXE](bin/H4CLOC.EXE) |

[实验报告](作业4_乘法指令和过程调用.md) · [C 反汇编逐行注释](C反汇编_逐行注释.md) · [实际输出](output/) · [验证结果](验证结果.json)

将本目录挂载到 DOSBox 后，可运行 `bin\h4tab`、`bin\h4chk` 等程序。在课程环境中输入 `h4demo` 可依次运行五份 EXE；双击课程根目录的 `运行作业4.cmd` 也可打开演示。

在 DOSBox 的 `src` 目录执行 `h4build` 可重新汇编两个 ASM 程序。在 Windows 的仓库根目录执行以下命令可重新构建五份 EXE，并运行输出核对和 DEBUG 验证：

```text
python homework4/tests/verify.py --course-root D:\Homework\6\HUI
```
