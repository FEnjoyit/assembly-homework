# 作业3：C 程序反汇编注释

源文件：[S3C.C](src/S3C.C)。编译器为 Open Watcom C16 2.0beta1 LA，目标为8086、16位 DOS、small 模型；使用 `-od` 关闭优化，使循环和变量保留清晰的对应关系。

## 一、C 源码

```c
#include <stdio.h>

int main(void)
{
    unsigned int i;
    unsigned int total = 0;

    for (i = 1; i <= 100; ++i) {
        total += i;
    }
    printf("%u\n", total);
    return 0;
}
```

`unsigned int` 在此16位目标下占2字节。`total` 的最大值为5050，`i` 在循环结束时为101，均可由16位无符号数保存。

## 二、main 的实际反汇编

链接后的 `main_` 位于 `CS:0010`，代码长度为 `0046H`，即70字节；`printf_` 位于 `CS:0056`。EXE 的启动入口为 `CS:0076`，C 运行库完成初始化后调用 `main_`。下列偏移和机器码取自 [DEBUG 记录](logs/C.DBG)，共32条指令。

```asm
; 偏移  机器码          指令                         注释
0010    53              PUSH BX                      ; 保存调用者的 BX
0011    51              PUSH CX                      ; 保存 CX
0012    52              PUSH DX                      ; 保存 DX
0013    56              PUSH SI                      ; 保存 SI
0014    57              PUSH DI                      ; 保存 DI
0015    55              PUSH BP                      ; 保存调用者的栈帧指针
0016    89E5            MOV BP,SP                    ; 建立当前函数的栈帧
0018    81EC0600        SUB SP,0006                  ; 分配6字节局部空间
001C    C746FE0000      MOV WORD PTR [BP-02],0000    ; total = 0
0021    C746FC0100      MOV WORD PTR [BP-04],0001    ; i = 1
0026    837EFC64        CMP WORD PTR [BP-04],+64     ; 比较 i 与100，64H = 100
002A    770B            JA 0037                      ; 无符号 i > 100 时退出循环
002C    8B46FC          MOV AX,[BP-04]               ; AX = i
002F    0146FE          ADD [BP-02],AX               ; total += i
0032    FF46FC          INC WORD PTR [BP-04]         ; ++i
0035    EBEF            JMP 0026                     ; 返回条件判断
0037    8B46FE          MOV AX,[BP-02]               ; AX = total，最终为13BAH
003A    50              PUSH AX                      ; 压入 printf 的数值参数
003B    B82200          MOV AX,0022                  ; 格式串 "%u\n" 的数据段偏移
003E    50              PUSH AX                      ; 压入 printf 的格式串参数
003F    E81400          CALL 0056                    ; 调用链接后确定的 printf_
0042    83C404          ADD SP,+04                   ; 调用者回收两个字参数
0045    C746FA0000      MOV WORD PTR [BP-06],0000    ; 设置 main 的返回值为0
004A    8B46FA          MOV AX,[BP-06]               ; AX = 返回值
004D    89EC            MOV SP,BP                    ; 释放局部变量空间
004F    5D              POP BP                       ; 恢复原 BP
0050    5F              POP DI                       ; 恢复 DI
0051    5E              POP SI                       ; 恢复 SI
0052    5A              POP DX                       ; 恢复 DX
0053    59              POP CX                       ; 恢复 CX
0054    5B              POP BX                       ; 恢复 BX
0055    C3              RET                          ; 返回 C 运行库
```

## 三、变量与控制流

| 栈位置 | C 对象 | 作用 |
| --- | --- | --- |
| `[BP-02]` | `total` | 保存累计和 |
| `[BP-04]` | `i` | 保存当前加数 |
| `[BP-06]` | 返回值临时槽 | 保存 `return 0` 的值 |

指令 `0026～0035` 对应整个 `for` 循环。每轮先判断 `i`，再执行累加和自增，随后跳回判断处。`i` 为无符号数，因此退出条件使用 `JA`。

`printf` 的两个参数按栈传递：先压入 `total`，再压入格式串偏移，调用返回后执行 `ADD SP,4` 回收参数。这里的调用约定与普通固定参数函数的寄存器传参形式不同，应按这段可变参数调用的实际指令解释。

格式串的4个字节为 `25 75 0A 00`，对应 `%u`、换行和零结束符。`%u` 将无符号数值5050转换为十进制字符，运行输出为 `5050` 加回车换行。

## 四、查看与重建

在 DOSBox 中逐行输入：

```text
debug S3C.EXE
u cs:10 l46
g 10
r
g
q
```

`g 10` 让程序先执行运行库初始化，停在 `main_` 的第一条指令；随后 `g` 继续执行并输出5050。重新运行时段地址可能变化，以上偏移对应本次构建。

编译和目标文件反汇编命令：

```text
wcl -0 -ms -bt=dos -l=dos -od -d2 -s -w=4 -we -fe=S3C.EXE -fo=S3C.OBJ -fm=S3C.MAP S3C.C
wdis -s=S3C.C -l=S3C_DIS.TXT S3C.OBJ
```

[WDIS 源码混合列表](logs/S3C_DIS.TXT) 中的 `CALL` 位移和数据地址带有待链接的重定位信息；上面的 DEBUG 结果来自链接后的 EXE，`CALL 0056` 和格式串偏移 `0022` 已经确定。`main_` 的70字节只包含该函数，完整 EXE 还包括启动代码和 C 运行库。
