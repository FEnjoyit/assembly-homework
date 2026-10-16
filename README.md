# 8086 汇编课程作业

每次作业独立放在一个子目录，包含源码、可执行程序、报告和实际运行记录。

| 作业 | 内容 | 报告 | 源码 | EXE |
| --- | --- | --- | --- | --- |
| [作业1](homework1/) | Hello world：传统汇编链接、DEBUG 反汇编、直接写内存执行、程序结构与寄存器 | [Markdown](homework1/作业1_报告.md) · [PDF](homework1/作业1_报告.pdf) | [src](homework1/src/) | [bin](homework1/bin/) |
| [作业2](homework2/) | a–z 字母表，每行13个：LOOP、条件跳转、C 实现及真实反汇编注释 | [Markdown](homework2/作业2_报告.md) | [src](homework2/src/) | [bin](homework2/bin/) |

## 运行环境

目标为 **8086 指令、16 位 DOS**，在 DOSBox-X 中运行。汇编工具为 MASM 5.00 / LINK 3.60，调试器为 FreeDOS DEBUG 2.50；作业2的 C 版本使用 Open Watcom C16。版本、配置和安装方式见 [环境说明](environment/README.md)。

源码与老师要求的 `.EXE` 均已提交。16 位 EXE 在 DOSBox 内运行。仓库中的报告记录了实验机的实际路径、段地址和操作；在其他机器上，挂载路径和运行时段地址按实际情况确定。

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
  作业1_报告.pdf
homework2/          第二次作业
  src/             两份 ASM、一份 C 和 DOS 批处理
  bin/             三份 DOS EXE
  output/          三份实际输出
  logs/            编译与调试记录
  作业2_报告.md
environment/       共用环境说明
```

后续每次作业新增 `homework3`、`homework4` 等同级目录，并在本页增加入口。

## 验证

- 作业1：[23/23 项通过](homework1/验证结果.json)，传统方式与直接写内存方式均输出 `Hello world!` 并正常退出。
- 作业2：[30/30 项通过](homework2/验证结果.json)，三个版本输出逐字节一致，每行13个字母。

运行和反汇编记录保留在各作业的 `logs` 中，包含对应源码和 EXE 的校验值。
