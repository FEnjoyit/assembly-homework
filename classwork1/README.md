# 课堂练习1：进制转换

- [实验报告](课堂练习1_进制转换.md)
- 十六进制转十进制：[源码](src/C1H2D.ASM) · [EXE](bin/C1H2D.EXE)
- 十进制转十六进制：[源码](src/C1D2H.ASM) · [EXE](bin/C1D2H.EXE)
- [运行示例](output/) · [编译与测试记录](logs/) · [验证结果](验证结果.json)

在 DOSBox 中挂载本目录后，运行 `bin\c1h2d` 或 `bin\c1d2h`；本机也可双击课程根目录的 `运行课堂练习1.cmd`，完成一次转换后，在 DOS 提示符下输入 `c1d2h` 运行追加部分。

课堂练习使用 `classwork1`、`classwork2` 等独立编号；课后作业继续使用 `homework1`、`homework2`。

环境配置见 [共用说明](../environment/README.md)。重新编译时进入 `src` 后执行 `c1build`。测试脚本位于 [tests/verify.py](tests/verify.py)，使用现有 Windows 课程环境执行：

```text
python classwork1/tests/verify.py --course-root D:\Homework\6\HUI
```
