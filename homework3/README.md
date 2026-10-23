# 作业3：求和

计算 `1+2+…+100` 并输出十进制结果 `5050`；比较累计值放在寄存器、数据段、栈中的实现，支持输入 `n=1～100` 后计算 `1+2+…+n`，并给出 C 实现及反汇编注释。

- [完整实验报告](作业3_求和.md)
- 寄存器版：[S3REG.ASM](src/S3REG.ASM) · [S3REG.EXE](bin/S3REG.EXE)
- 数据段版：[S3DATA.ASM](src/S3DATA.ASM) · [S3DATA.EXE](bin/S3DATA.EXE)
- 栈版：[S3STACK.ASM](src/S3STACK.ASM) · [S3STACK.EXE](bin/S3STACK.EXE)
- 输入版：[S3INPUT.ASM](src/S3INPUT.ASM) · [S3INPUT.EXE](bin/S3INPUT.EXE)
- C 版：[S3C.C](src/S3C.C) · [S3C.EXE](bin/S3C.EXE) · [反汇编逐行注释](C反汇编_逐行注释.md)
- [公共十进制输出子程序](src/S3IO.INC) · [运行结果](output/) · [调试记录](logs/) · [验证结果](验证结果.json)

将本目录挂载为 DOSBox 的 D 盘后，可直接运行 `bin\s3reg`、`bin\s3data`、`bin\s3stack`、`bin\s3c` 或 `bin\s3input`。重新汇编时进入 `src` 并执行 `s3build`，保留同目录下的 `S3IO.INC`。

本机课程窗口中输入 `s3demo` 可依次演示，或双击课程根目录的 `运行作业3.cmd`。

在仓库根目录执行以下命令，可使用现有 Windows 课程工具重新编译全部程序、生成反汇编并运行测试：

```text
python homework3/tests/verify.py --course-root D:\Homework\6\HUI
```

测试包含全部100个合法上限、前导零、非法输入和连续错误后的重试，共122个输入用例及33项构建、输出和调试检查，155项全部通过。
