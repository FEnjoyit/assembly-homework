# 8086 汇编课程作业

课后作业与课堂练习分别编号，每题独立放在一个子目录，包含源码、可执行程序、Markdown 报告和运行记录。

| 作业 / 练习 | 内容 | 报告 | 源码 | EXE |
| --- | --- | --- | --- | --- |
| [作业1](homework1/) | Hello world：传统汇编链接、DEBUG 反汇编、直接写内存执行、程序结构与寄存器 | [Markdown](homework1/作业1_报告.md) | [src](homework1/src/) | [bin](homework1/bin/) |
| [作业2](homework2/) | a–z 字母表，每行13个：LOOP、条件跳转、C 实现及真实反汇编注释 | [Markdown](homework2/作业2_报告.md) | [src](homework2/src/) | [bin](homework2/bin/) |
| [作业3](homework3/) | 求和：寄存器、数据段、栈保存结果，输入1～100及 C 反汇编 | [Markdown](homework3/作业3_求和.md) | [src](homework3/src/) | [bin](homework3/bin/) |
| [课堂练习1](classwork1/) | 进制转换：1至2位十六进制转十进制，追加十进制转十六进制 | [Markdown](classwork1/课堂练习1_进制转换.md) | [src](classwork1/src/) | [bin](classwork1/bin/) |

## 运行环境

目标为 **8086 指令、16 位 DOS**，在 DOSBox-X 中运行。汇编工具为 MASM 5.00 / LINK 3.60，调试器为 FreeDOS DEBUG 2.50；作业2、作业3的 C 版本使用 Open Watcom C16。版本、配置和安装方式见 [环境说明](environment/README.md)。

各次作业包含源码、16 位 DOS EXE 和 Markdown 报告。EXE 在 DOSBox 内运行；挂载路径和运行时段地址按实际环境确定。

以作业1为例，在 DOSBox 中把下载的 `homework1` 文件夹挂载为 D 盘：

```text
mount d "C:\path\to\assembly-homework\homework1"
d:
bin\a1lea
bin\a1off
debug < src\a1mem.dbg
```

`debug` 必须位于 DOSBox 的搜索路径中；若工具挂载在其他盘，请用它的完整 DOS 路径。传统方式重编译时，进入 `src` 后运行 `a1build`；作业2同理挂载 `homework2`，使用 `bin\a2loop`、`bin\a2jump`、`bin\a2c` 运行。

## 目录约定

```text
homework1/          第一次作业
  src/             ASM、DEBUG 命令文件、DOS 批处理
  bin/             链接后的 EXE
  logs/            真实汇编、链接、DEBUG 输出及 LST/MAP
  作业1_报告.md
homework2/          第二次作业
  src/             两份 ASM、一份 C 和 DOS 批处理
  bin/             三份 DOS EXE
  output/          三份实际输出
  logs/            编译与调试记录
  作业2_报告.md
homework3/          第三次作业：求和
  src/             四份 ASM、公共输出子程序和 C 源码
  bin/             五份 DOS EXE
  output/          固定输出和输入版运行记录
  logs/            编译、链接、DEBUG 和输入测试记录
  tests/           编译与验证脚本
  作业3_求和.md
  C反汇编_逐行注释.md
classwork1/         课堂练习1，独立编号
  src/             两份 ASM 和编译批处理
  bin/             两份 DOS EXE
  output/          实际运行示例
  logs/            汇编、链接及逐用例测试记录
  tests/           测试脚本
  课堂练习1_进制转换.md
environment/       共用环境说明
```

课后作业使用 `homework1`、`homework2`、`homework3` 等目录；课堂练习使用 `classwork1`、`classwork2`、`classwork3` 等目录，各自顺序编号，并在本页增加入口。

## 验证

- 作业1：[23/23 项通过](homework1/验证结果.json)，传统方式与直接写内存方式均输出 `Hello world!` 并正常退出。
- 作业2：[30/30 项通过](homework2/验证结果.json)，三个版本输出逐字节一致，每行13个字母。
- 作业3：[155/155 项通过](homework3/验证结果.json)，四个固定版本均输出5050，122个输入用例全部通过，并核对三种累计位置与栈恢复。
- 课堂练习1：[795/795 项通过](classwork1/验证结果.json)，787个输入用例通过，覆盖全部 `00～FF` 数值、十进制边界和非法输入重试。

运行和反汇编记录保留在各作业的 `logs` 中，包含对应源码和 EXE 的校验值。
