# 作业5：递归调用

输入 `n`（1～100），输出 `F(n)`。汇编版和 C 版均使用带缓存的双分支递归与 21 位十进制数位数组。

- [实验报告：程序设计、单步调试和学习心得](作业5_递归调用.md)
- [8086 汇编源码](src/H5FIB.ASM) · [DOS EXE](bin/H5FIB.EXE)
- [C 源码](src/H5CFIB.C) · [DOS EXE](bin/H5CFIB.EXE) · [C 反汇编逐行注释](C反汇编_逐行注释.md)
- [F(5) 的 18 次 CALL/RET](logs/递归跟踪.csv) · [汇编版栈峰值](logs/MAX100.DBG) · [C 版栈峰值](logs/CMAX100.DBG)
- [运行示例](output/) · [验证结果](验证结果.json)

在课程窗口输入 `h5fib` 或 `h5cfib`，输入数字后回车；也可双击课程根目录的 `运行作业5.cmd` 启动汇编版。在 DOSBox 挂载本目录后，可运行 `bin\h5fib` 和 `bin\h5cfib`。编译与验证命令见实验报告。
