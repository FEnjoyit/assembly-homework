# 作业5：C 反汇编逐行注释

[H5CFIB.C](src/H5CFIB.C) 由 Open Watcom C16 以 8086、16 位 DOS、small 模型编译。编译参数 `-od` 关闭优化。下表来自 [链接后 EXE 的 DEBUG 记录](logs/CDIS.DBG)，代码地址为 CS 内偏移；[WDIS 列表](logs/H5CFIB.TXT) 还包含输入、输出辅助过程及其 C 源码行。

`fib_` 从 `0010H` 开始，占 203 字节。两个递归点 `0040H`、`004CH` 都调用 `0010H`。参数 `n` 在 AX，返回值 AX 是 `DS` 中 21 个数位的起始偏移。注意 `CALL` 由 CPU 压入的返回 IP 与 C 函数返回的数组指针是两种不同的值。

`[BP-10H]` 保存 n，`[BP-0CH]` 保存 out，`[BP-0AH]` 和 `[BP-08H]` 保存左右结果指针，`[BP-06H]` 保存数位下标，`[BP-04H]` 保存 sum，`[BP-02H]` 保存 carry。当前编译结果还有若干临时槽，整体以 `SUB SP,0014` 分配 20 字节。主程序 `main_` 位于 `0212H`，占 93 字节。

复现命令：`debug H5CFIB.EXE`，随后输入 `u cs:10 lcb` 和 `u cs:212 l5d`。DEBUG 的数字按十六进制解析。

## fib_：递归、缓存和逐位加法（78 条指令）

```asm
0010  53           PUSH BX                       ; 保存 BX
0011  51           PUSH CX                       ; 保存 CX
0012  52           PUSH DX                       ; 保存 DX
0013  56           PUSH SI                       ; 保存 SI
0014  57           PUSH DI                       ; 保存 DI
0015  55           PUSH BP                       ; 保存 BP
0016  89E5         MOV BP,SP                     ; 建立当前栈帧
0018  81EC1400     SUB SP,0014                   ; 分配 14H 字节局部空间
001C  8946F0       MOV [BP-10],AX                ; 保存 AX 传入的 n
001F  8B46F0       MOV AX,[BP-10]                ; 取 n
0022  BB1500       MOV BX,0015                   ; 取每项宽度 21
0025  F7EB         IMUL BX                       ; 计算数位区偏移 n×21，范围内乘积可放入 AX
0027  BBF700       MOV BX,00F7                   ; 取 cache 基址
002A  01C3         ADD BX,AX                     ; BX = cache[n] 的首地址
002C  895EF4       MOV [BP-0C],BX                ; 保存 out 指针
002F  8B5EF0       MOV BX,[BP-10]                ; 用 n 作索引
0032  80BF920000   CMP BYTE PTR [BX+0092],00     ; 检查 ready[n]
0037  7403         JZ 003C                       ; 未缓存时进入递归分支
0039  E98D00       JMP 00C9                      ; 命中缓存，直接到返回路径
003C  8B46F0       MOV AX,[BP-10]                ; 重新取 n
003F  48           DEC AX                        ; AX = n-1
0040  E8CDFF       CALL 0010                     ; 递归计算 F(n-1)
0043  8946F6       MOV [BP-0A],AX                ; 保存左结果指针
0046  8B46F0       MOV AX,[BP-10]                ; 重新取 n
0049  2D0200       SUB AX,0002                   ; AX = n-2
004C  E8C1FF       CALL 0010                     ; 递归计算 F(n-2)
004F  8946F8       MOV [BP-08],AX                ; 保存右结果指针
0052  C746FE0000   MOV WORD PTR [BP-02],0000     ; carry = 0
0057  C746FA0000   MOV WORD PTR [BP-06],0000     ; i = 0
005C  837EFA15     CMP WORD PTR [BP-06],+15      ; 比较 i 与 21
0060  735F         JAE 00C1                      ; 处理完 21 位后结束循环
0062  8B5EF6       MOV BX,[BP-0A]                ; 读取左结果指针
0065  035EFA       ADD BX,[BP-06]                ; 定位 left[i]
0068  8A07         MOV AL,[BX]                   ; 取左数位
006A  30E4         XOR AH,AH                     ; 将 AL 零扩展到 AX
006C  89C2         MOV DX,AX                     ; 暂存左数位
006E  8B5EF8       MOV BX,[BP-08]                ; 读取右结果指针
0071  035EFA       ADD BX,[BP-06]                ; 定位 right[i]
0074  8A07         MOV AL,[BX]                   ; 取右数位
0076  30E4         XOR AH,AH                     ; 将 AL 零扩展到 AX
0078  01D0         ADD AX,DX                     ; 相加两个数位
007A  8B56FE       MOV DX,[BP-02]                ; 取上一位的进位
007D  01C2         ADD DX,AX                     ; 加入进位
007F  8956FC       MOV [BP-04],DX                ; 保存本位的和 sum
0082  837EFC0A     CMP WORD PTR [BP-04],+0A      ; 比较 sum 与 10
0086  7207         JB 008F                       ; 小于 10 时进位为 0
0088  C746EC0100   MOV WORD PTR [BP-14],0001     ; 将进位临时量置 1
008D  EB05         JMP 0094                      ; 跳过清零分支
008F  C746EC0000   MOV WORD PTR [BP-14],0000     ; 将进位临时量置 0
0094  8B46EC       MOV AX,[BP-14]                ; 取新的进位
0097  8946FE       MOV [BP-02],AX                ; 写回 carry
009A  837EFE00     CMP WORD PTR [BP-02],+00      ; 判断是否发生进位
009E  740B         JZ 00AB                       ; 无进位则直接使用 sum
00A0  8B46FC       MOV AX,[BP-04]                ; 读取 sum
00A3  2D0A00       SUB AX,000A                   ; 有进位时减 10
00A6  8946EE       MOV [BP-12],AX                ; 保存取舍后的数位临时值
00A9  EB06         JMP 00B1                      ; 跳到写回路径
00AB  8B46FC       MOV AX,[BP-04]                ; 读取无进位时的 sum
00AE  8946EE       MOV [BP-12],AX                ; 保存未减 10 的数位临时值
00B1  8A46EE       MOV AL,[BP-12]                ; 取结果的低字节
00B4  8B5EF4       MOV BX,[BP-0C]                ; 读取 out 指针
00B7  035EFA       ADD BX,[BP-06]                ; 定位 out[i]
00BA  8807         MOV [BX],AL                   ; 写回当前数位
00BC  FF46FA       INC WORD PTR [BP-06]          ; i 自增
00BF  EB9B         JMP 005C                      ; 回到数位循环判断
00C1  8B5EF0       MOV BX,[BP-10]                ; 重新取 n
00C4  C687920001   MOV BYTE PTR [BX+0092],01     ; 置 ready[n] 为 1
00C9  8B5EF4       MOV BX,[BP-0C]                ; 取 out 指针
00CC  895EF2       MOV [BP-0E],BX                ; 写入指针返回值临时槽
00CF  8B46F2       MOV AX,[BP-0E]                ; 用 AX 返回近指针
00D2  89EC         MOV SP,BP                     ; 释放本层局部空间
00D4  5D           POP BP                        ; 恢复 BP
00D5  5F           POP DI                        ; 恢复 DI
00D6  5E           POP SI                        ; 恢复 SI
00D7  5A           POP DX                        ; 恢复 DX
00D8  59           POP CX                        ; 恢复 CX
00D9  5B           POP BX                        ; 恢复 BX
00DA  C3           RET                           ; 弹出返回 IP，回到调用者
```

## main_：输入检查、调用与输出（39 条指令）

```asm
0212  53           PUSH BX                       ; 保存 BX
0213  51           PUSH CX                       ; 保存 CX
0214  52           PUSH DX                       ; 保存 DX
0215  56           PUSH SI                       ; 保存 SI
0216  57           PUSH DI                       ; 保存 DI
0217  55           PUSH BP                       ; 保存 BP
0218  89E5         MOV BP,SP                     ; 建立当前栈帧
021A  81EC0600     SUB SP,0006                   ; 分配 6 字节局部空间
021E  B82200       MOV AX,0022                   ; 将输入提示地址放入 AX
0221  E8C301       CALL 03E7                     ; 调用 puts
0224  E8B4FE       CALL 00DB                     ; 调用 read_index
0227  8946FC       MOV [BP-04],AX                ; 保存返回的 n
022A  837EFC00     CMP WORD PTR [BP-04],+00      ; 判断 n 是否小于 0
022E  7D07         JGE 0237                      ; 非负时继续检查
0230  C746FA0100   MOV WORD PTR [BP-06],0001     ; EOF：设置返回值为 1
0235  EB2C         JMP 0263                      ; 转到返回路径
0237  837EFC00     CMP WORD PTR [BP-04],+00      ; 检查 n 是否为 0
023B  7506         JNZ 0243                      ; 合法输入跳过报错
023D  B83300       MOV AX,0033                   ; 取错误提示地址
0240  E8A401       CALL 03E7                     ; 调用 puts 输出错误提示
0243  837EFC00     CMP WORD PTR [BP-04],+00      ; 再次检查 n 是否为 0
0247  74D5         JZ 021E                       ; 无效输入时回到读取
0249  8B46FC       MOV AX,[BP-04]                ; 用 AX 传入 n
024C  E8C1FD       CALL 0010                     ; 调用 fib_
024F  8946FE       MOV [BP-02],AX                ; 保存返回的数位数组指针
0252  B85200       MOV AX,0052                   ; 取结果标题地址
0255  E88F01       CALL 03E7                     ; 调用 puts 输出结果标题
0258  8B46FE       MOV AX,[BP-02]                ; 取数组指针作参数
025B  E85CFF       CALL 01BA                     ; 调用 print_digits
025E  C746FA0000   MOV WORD PTR [BP-06],0000     ; 正常返回值设为 0
0263  8B46FA       MOV AX,[BP-06]                ; 将退出值放入 AX
0266  89EC         MOV SP,BP                     ; 释放局部空间
0268  5D           POP BP                        ; 恢复 BP
0269  5F           POP DI                        ; 恢复 DI
026A  5E           POP SI                        ; 恢复 SI
026B  5A           POP DX                        ; 恢复 DX
026C  59           POP CX                        ; 恢复 CX
026D  5B           POP BX                        ; 恢复 BX
026E  C3           RET                           ; 弹出返回 IP，回到调用者
```
