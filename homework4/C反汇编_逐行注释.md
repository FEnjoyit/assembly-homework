# 作业4：C 反汇编注释

以下三份反汇编来自链接后的 16 位 DOS EXE。目标为 8086，Open Watcom C16 使用 `-od` 关闭优化；程序由 C 运行库初始化后进入 `main_`，三个版本的 `main_` 均始于 `CS:0010`。表中只写段内偏移，段值可随装载环境变化。

| 程序 | 源码 | main 长度 | 调试命令 | 原始记录 |
| --- | --- | --- | --- | --- |
| 乘法表 | [H4TAB.C](src/H4TAB.C) | 146 字节 | `u cs:10 l92` | [DEBUG](logs/H4CTAB.DBG) · [WDIS](logs/H4CTAB.TXT) |
| 全局数组纠错 | [H4CHK.C](src/H4CHK.C) | 123 字节 | `u cs:10 l7b` | [DEBUG](logs/H4CGLOB.DBG) · [WDIS](logs/H4CGLOB.TXT) |
| 局部数组纠错 | [H4CHK.C](src/H4CHK.C)，定义 `LOCAL_TABLE` | 138 字节 | `u cs:10 l8a` | [DEBUG](logs/H4CLOC.DBG) · [WDIS](logs/H4CLOC.TXT) |

## 全局数组与局部数组的寻址

全局版在 `0046` 执行 `MOV AL,[BX+00B7]`，默认使用 DS。此时 BX 为 `(x-1)×9+y`，数组基址为 `DS:00B8`，指令中的 `00B7` 已计入减去 1 的列下标修正。

局部版在 `0018` 预留 `58H` 字节栈帧空间。数组从 `SS:[BP-58H]` 开始。进入函数时，`REP MOVSW` 复制 40 个字，再用 `MOVSB` 复制 1 字节，将 `DS:00B8` 的 81 字节模板复制到栈中。检查时在 `0056` 执行 `MOV AL,[BP+SI-59]`；含 BP 的寻址默认使用 SS，`-59H` 等于基址偏移 `-58H` 再减去 1。全局数组占静态数据空间，局部数组的运行时副本随本次函数调用建立和释放。

三种版本的 `printf` 调用都将参数从右到左压栈，并在返回后回收参数。这里的 `puts` 和 `putchar` 则使用 AX 传入参数。以下指令及注释以实际链接结果为准。

## 乘法表输出：59 条指令

```asm
0010  53            PUSH BX                         ; 保存 BX
0011  51            PUSH CX                         ; 保存 CX
0012  52            PUSH DX                         ; 保存 DX
0013  56            PUSH SI                         ; 保存 SI
0014  57            PUSH DI                         ; 保存 DI
0015  55            PUSH BP                         ; 保存 BP
0016  89E5          MOV BP,SP                       ; 建立栈帧
0018  81EC0A00      SUB SP,000A                     ; 分配 10 字节局部空间
001C  B82200        MOV AX,0022                     ; 标题字符串偏移放入 AX
001F  E88000        CALL 00A2                       ; 调用 puts，输出标题及换行
0022  C746FA0900    MOV WORD PTR [BP-06],0009       ; x = 9
0027  837EFA00      CMP WORD PTR [BP-06],+00        ; 判断 x 是否为 0
002B  7464          JZ 0091                         ; x = 0 时退出外循环
002D  C746FC0100    MOV WORD PTR [BP-04],0001       ; y = 1，开始新行
0032  8B46FC        MOV AX,[BP-04]                  ; 读入 y
0035  3B46FA        CMP AX,[BP-06]                  ; 比较 y 与 x
0038  774B          JA 0085                         ; y > x，结束当前行
003A  8B46FA        MOV AX,[BP-06]                  ; 取 x 到 AX
003D  F766FC        MUL WORD PTR [BP-04]            ; DX:AX = x × y
0040  8946FE        MOV [BP-02],AX                  ; 保存积的低 16 位到 product
0043  8B46FE        MOV AX,[BP-02]                  ; 读取 product
0046  50            PUSH AX                         ; 压入积
0047  8B46FC        MOV AX,[BP-04]                  ; 读取 y
004A  50            PUSH AX                         ; 压入列号
004B  8B46FA        MOV AX,[BP-06]                  ; 读取 x
004E  50            PUSH AX                         ; 压入行号
004F  B83300        MOV AX,0033                     ; 取表达式格式串的偏移
0052  50            PUSH AX                         ; 压入格式串偏移
0053  E87200        CALL 00C8                       ; 调用 printf 输出一项
0056  83C408        ADD SP,+08                      ; 回收 4 个字参数
0059  8B46FC        MOV AX,[BP-04]                  ; 取 y
005C  3B46FA        CMP AX,[BP-06]                  ; 比较 y 与 x
005F  741F          JZ 0080                         ; 末列跳过补空格
0061  837EFE0A      CMP WORD PTR [BP-02],+0A        ; 判断积是否小于 10
0065  7307          JAE 006E                        ; 两位数选择两个空格
0067  C746F63C00    MOV WORD PTR [BP-0A],003C       ; 一位数选择三个空格
006C  EB05          JMP 0073                        ; 跳过两空格的分支
006E  C746F64000    MOV WORD PTR [BP-0A],0040       ; 保存两空格串的偏移
0073  FF76F6        PUSH WORD PTR [BP-0A]           ; 压入选定的空格串偏移
0076  B84300        MOV AX,0043                     ; 取 %s 格式串偏移
0079  50            PUSH AX                         ; 压入 %s 格式串偏移
007A  E84B00        CALL 00C8                       ; 调用 printf 输出空格
007D  83C404        ADD SP,+04                      ; 回收 2 个字参数
0080  FF46FC        INC WORD PTR [BP-04]            ; ++y
0083  EBAD          JMP 0032                        ; 回到内循环判断
0085  B80A00        MOV AX,000A                     ; AX = LF 字符码
0088  E85D00        CALL 00E8                       ; 调用 putchar 换行
008B  8346FAFF      ADD WORD PTR [BP-06],-01        ; --x
008F  EB96          JMP 0027                        ; 回到外循环判断
0091  C746F80000    MOV WORD PTR [BP-08],0000       ; 将返回值临时槽清零
0096  8B46F8        MOV AX,[BP-08]                  ; 将返回值 0 放入 AX
0099  89EC          MOV SP,BP                       ; 释放局部空间
009B  5D            POP BP                          ; 恢复 BP
009C  5F            POP DI                          ; 恢复 DI
009D  5E            POP SI                          ; 恢复 SI
009E  5A            POP DX                          ; 恢复 DX
009F  59            POP CX                          ; 恢复 CX
00A0  5B            POP BX                          ; 恢复 BX
00A1  C3            RET                             ; 返回 C 运行库
```

## 全局数组纠错：53 条指令

```asm
0010  53            PUSH BX                         ; 保存 BX
0011  51            PUSH CX                         ; 保存 CX
0012  52            PUSH DX                         ; 保存 DX
0013  56            PUSH SI                         ; 保存 SI
0014  57            PUSH DI                         ; 保存 DI
0015  55            PUSH BP                         ; 保存 BP
0016  89E5          MOV BP,SP                       ; 建立栈帧
0018  81EC0600      SUB SP,0006                     ; 分配 6 字节局部空间，不含数组
001C  B82200        MOV AX,0022                     ; 取 x y 标题串偏移
001F  E86900        CALL 008B                       ; 调用 puts 输出标题
0022  C746FC0100    MOV WORD PTR [BP-04],0001       ; x = 1
0027  837EFC09      CMP WORD PTR [BP-04],+09        ; 比较 x 与 9
002B  7747          JA 0074                         ; x > 9 时结束扫描
002D  C746FE0100    MOV WORD PTR [BP-02],0001       ; y = 1
0032  837EFE09      CMP WORD PTR [BP-02],+09        ; 比较 y 与 9
0036  7737          JA 006F                         ; y > 9 时结束当前行
0038  8B46FC        MOV AX,[BP-04]                  ; 读取 x
003B  48            DEC AX                          ; 改为从 0 起算的行号
003C  BB0900        MOV BX,0009                     ; 取每行宽度 9
003F  F7EB          IMUL BX                         ; 计算行内存起点 (x-1)×9
0041  8B5EFE        MOV BX,[BP-02]                  ; BX = y
0044  01C3          ADD BX,AX                       ; BX = (x-1)×9+y
0046  8A87B700      MOV AL,[BX+00B7]                ; 从 DS:[BX+00B7] 取表值
004A  30E4          XOR AH,AH                       ; 无符号字节零扩展为字
004C  89C3          MOV BX,AX                       ; BX 保存表值
004E  8B46FC        MOV AX,[BP-04]                  ; 取 x 到 AX
0051  F766FE        MUL WORD PTR [BP-02]            ; DX:AX = x × y
0054  39C3          CMP BX,AX                       ; 比较表值和正确乘积
0056  7412          JZ 006A                         ; 值相等时跳过错误输出
0058  8B46FE        MOV AX,[BP-02]                  ; 读取 y
005B  50            PUSH AX                         ; 压入列号
005C  8B46FC        MOV AX,[BP-04]                  ; 读取 x
005F  50            PUSH AX                         ; 压入行号
0060  B82600        MOV AX,0026                     ; 取错误提示格式串偏移
0063  50            PUSH AX                         ; 压入格式串偏移
0064  E84A00        CALL 00B1                       ; 调用 printf 输出错误坐标
0067  83C406        ADD SP,+06                      ; 回收 3 个字参数
006A  FF46FE        INC WORD PTR [BP-02]            ; ++y
006D  EBC3          JMP 0032                        ; 回到内循环判断
006F  FF46FC        INC WORD PTR [BP-04]            ; ++x
0072  EBB3          JMP 0027                        ; 回到外循环判断
0074  B83500        MOV AX,0035                     ; 取结束字符串偏移
0077  E81100        CALL 008B                       ; 调用 puts 输出结束提示
007A  C746FA0000    MOV WORD PTR [BP-06],0000       ; 将返回值临时槽清零
007F  8B46FA        MOV AX,[BP-06]                  ; 将返回值 0 放入 AX
0082  89EC          MOV SP,BP                       ; 释放局部空间
0084  5D            POP BP                          ; 恢复 BP
0085  5F            POP DI                          ; 恢复 DI
0086  5E            POP SI                          ; 恢复 SI
0087  5A            POP DX                          ; 恢复 DX
0088  59            POP CX                          ; 恢复 CX
0089  5B            POP BX                          ; 恢复 BX
008A  C3            RET                             ; 返回 C 运行库
```

## 局部数组纠错：60 条指令

```asm
0010  53            PUSH BX                         ; 保存 BX
0011  51            PUSH CX                         ; 保存 CX
0012  52            PUSH DX                         ; 保存 DX
0013  56            PUSH SI                         ; 保存 SI
0014  57            PUSH DI                         ; 保存 DI
0015  55            PUSH BP                         ; 保存 BP
0016  89E5          MOV BP,SP                       ; 建立栈帧
0018  81EC5800      SUB SP,0058                     ; 分配 58H 字节局部空间，含 81 字节数组
001C  B92800        MOV CX,0028                     ; 设置复制计数 28H，即 40 个字
001F  8CD0          MOV AX,SS                       ; 把 SS 取入 AX
0021  8EC0          MOV ES,AX                       ; ES = SS，复制目标段为栈段
0023  8D7EA8        LEA DI,[BP-58]                  ; DI = 局部数组起始偏移 BP-58H
0026  BEB800        MOV SI,00B8                     ; SI = 初始化模板偏移 00B8H
0029  F3A5          REP MOVSW                       ; 从 DS:SI 到 ES:DI 复制 80 字节
002B  A4            MOVSB                           ; 再复制最后 1 字节
002C  B82200        MOV AX,0022                     ; 取 x y 标题串偏移
002F  E86800        CALL 009A                       ; 调用 puts 输出标题
0032  C746FC0100    MOV WORD PTR [BP-04],0001       ; x = 1
0037  837EFC09      CMP WORD PTR [BP-04],+09        ; 比较 x 与 9
003B  7746          JA 0083                         ; x > 9 时结束扫描
003D  C746FE0100    MOV WORD PTR [BP-02],0001       ; y = 1
0042  837EFE09      CMP WORD PTR [BP-02],+09        ; 比较 y 与 9
0046  7736          JA 007E                         ; y > 9 时结束当前行
0048  8B46FC        MOV AX,[BP-04]                  ; 读取 x
004B  48            DEC AX                          ; 改为从 0 起算的行号
004C  BE0900        MOV SI,0009                     ; 取每行宽度 9
004F  F7EE          IMUL SI                         ; 计算行内存起点 (x-1)×9
0051  8B76FE        MOV SI,[BP-02]                  ; SI = y
0054  01C6          ADD SI,AX                       ; SI = (x-1)×9+y
0056  8A42A7        MOV AL,[BP+SI-59]               ; 从 SS:[BP+SI-59H] 取表值
0059  30E4          XOR AH,AH                       ; 无符号字节零扩展为字
005B  89C6          MOV SI,AX                       ; SI 保存表值
005D  8B46FC        MOV AX,[BP-04]                  ; 取 x 到 AX
0060  F766FE        MUL WORD PTR [BP-02]            ; DX:AX = x × y
0063  39C6          CMP SI,AX                       ; 比较表值和正确乘积
0065  7412          JZ 0079                         ; 值相等时跳过错误输出
0067  8B46FE        MOV AX,[BP-02]                  ; 读取 y
006A  50            PUSH AX                         ; 压入列号
006B  8B46FC        MOV AX,[BP-04]                  ; 读取 x
006E  50            PUSH AX                         ; 压入行号
006F  B82600        MOV AX,0026                     ; 取错误提示格式串偏移
0072  50            PUSH AX                         ; 压入格式串偏移
0073  E84A00        CALL 00C0                       ; 调用 printf 输出错误坐标
0076  83C406        ADD SP,+06                      ; 回收 3 个字参数
0079  FF46FE        INC WORD PTR [BP-02]            ; ++y
007C  EBC4          JMP 0042                        ; 回到内循环判断
007E  FF46FC        INC WORD PTR [BP-04]            ; ++x
0081  EBB4          JMP 0037                        ; 回到外循环判断
0083  B83500        MOV AX,0035                     ; 取结束字符串偏移
0086  E81100        CALL 009A                       ; 调用 puts 输出结束提示
0089  C746FA0000    MOV WORD PTR [BP-06],0000       ; 将返回值临时槽清零
008E  8B46FA        MOV AX,[BP-06]                  ; 将返回值 0 放入 AX
0091  89EC          MOV SP,BP                       ; 释放局部空间
0093  5D            POP BP                          ; 恢复 BP
0094  5F            POP DI                          ; 恢复 DI
0095  5E            POP SI                          ; 恢复 SI
0096  5A            POP DX                          ; 恢复 DX
0097  59            POP CX                          ; 恢复 CX
0098  5B            POP BX                          ; 恢复 BX
0099  C3            RET                             ; 返回 C 运行库
```
