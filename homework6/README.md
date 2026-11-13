# 作业6：输出日历

输入 1900～2099 的年份、1～12 的月份，输出以星期日开头的月历。

- [实验报告](作业6_输出日历.md)：算法、三种传参方式、跨代码段调用、调试笔记和实验心得。
- [汇编源码](src/H6CAL.ASM) · [汇编 EXE](bin/H6CAL.EXE)
- [C 源码](src/H6CAL.C) · [C EXE](bin/H6CCAL.EXE) · [C 反汇编注释](C反汇编_注释.md)
- [跳转练习源码](src/H6JUMP.ASM) · [跳转 EXE](bin/H6JUMP.EXE)
- [远调用记录](logs/FAR.DBG) · [跳转记录](logs/JUMP.DBG) · [短跳转越界记录](logs/RANGE.LOG)
- [运行示例](output/) · [验证结果](验证结果.json) · [验证脚本](tests/verify.py)

在课程环境中输入 `h6cal` 或 `h6ccal`；输入年份后按回车，再输入月份。也可双击课程根目录的 `运行作业6.cmd`。

下载本目录后，在已有 DOSBox 环境中挂载目录，运行 `bin\h6cal` 或 `bin\h6ccal`。源码目录中的 `H6BUILD` 用 MASM、LINK 重新构建两个汇编程序。`tests/fixtures/H6RANGE.ASM` 是用于查看短跳转范围报错的练习文件，不参与正式月历程序构建。
