# 作业6：C 月历程序反汇编注释

源程序为 [H6CAL.C](src/H6CAL.C)，编译选项为 `-0 -ms -bt=dos -l=dos -od -d2 -s -k2048`。下面选取六个函数中与算法、参数和跳转有关的指令加注释；完整指令及机器码见 [最终 EXE 的 DEBUG 反汇编](logs/CDIS.DBG)，带 C 源码的目标文件反汇编见 [H6CCAL.TXT](logs/H6CCAL.TXT)。

以下偏移来自链接后的 EXE，CS 段内地址与 DEBUG 记录一致。本次 CS 为 `0E00H`，重新装入时段值可能改变。目标文件中的 `_TEXT` 从零开始，链接后放在 `CS:0010H`；例如目标文件的 `first_day_` 在 `009FH`，最终 EXE 中为 `00AFH`。目标文件里尚待链接的 `CALL` 位移也不能当作最终调用目标。

| 函数 | 最终入口 | 代码字节数 | 主要作用 |
| --- | --- | ---: | --- |
| `is_leap` | `0010H` | 86 | 判断闰年 |
| `month_days` | `0066H` | 73 | 查月长，处理二月 |
| `first_day` | `00AFH` | 127 | 按年、月累计星期 |
| `read_number` | `012EH` | 274 | 输入、检查和重试 |
| `print_calendar` | `0240H` | 176 | 格式化输出月历 |
| `main` | `02F0H` | 100 | 读取年、月并调用输出 |

## 一、函数入口与栈帧

以 `is_leap` 为例，输入年份由 AX 传入，进入函数后保存到栈帧。这里的 BP 寻址默认使用 SS。

```asm
0010  PUSH BX              ; 保存调用者的寄存器
0011  PUSH CX
0012  PUSH DX
0013  PUSH SI
0014  PUSH DI
0015  PUSH BP              ; 保存旧 BP
0016  MOV  BP,SP           ; BP 固定在当前栈帧基址
0018  SUB  SP,0006         ; 分配 6 字节局部空间
001C  MOV  [BP-06],AX      ; 保存参数 year
```

函数结束时通过 AX 返回结果。局部空间由 `MOV SP,BP` 一次释放，然后逆序恢复寄存器。

```asm
005A  MOV  AX,[BP-04]      ; AX = 返回值
005D  MOV  SP,BP           ; 释放局部变量空间
005F  POP  BP
0060  POP  DI
0061  POP  SI
0062  POP  DX
0063  POP  CX
0064  POP  BX
0065  RET                 ; C3：近返回，只弹出返回 IP
```

本次 C 版的函数处在同一个代码段，调用使用近 `CALL`，无需按汇编远过程那样额外保存返回 CS。

## 二、闰年判断：短路条件与余数

`is_leap` 对应 `year % 400 == 0 || (year % 4 == 0 && year % 100 != 0)`。

```asm
001F  MOV  CX,0190                 ; 除数 400
0022  MOV  BX,[BP-06]              ; BX = year
0025  XOR  DX,DX                   ; 被除数高字清零
0027  MOV  AX,BX                   ; DX:AX = year
0029  DIV  CX                      ; AX 为商，DX 为余数
002B  TEST DX,DX                   ; 检查 year % 400
002D  JZ   0048                    ; 余数为零，直接判闰年
002F  TEST WORD PTR [BP-06],0003    ; 检查低两位，等价于 year % 4
0034  JNZ  0046                    ; 不能被 4 整除，判平年
0036  MOV  CX,0064                 ; 除数 100
0039  MOV  BX,[BP-06]
003C  XOR  DX,DX
003E  MOV  AX,BX
0040  DIV  CX                      ; DX = year % 100
0042  TEST DX,DX
0044  JNZ  0048                    ; 非世纪年且能被 4 整除，判闰年
0046  JMP  004F                    ; 其余情况判平年
0048  MOV  WORD PTR [BP-02],0001    ; 布尔结果为 1
004D  JMP  0054
004F  MOV  WORD PTR [BP-02],0000    ; 布尔结果为 0
0054  MOV  AX,[BP-02]
0057  MOV  [BP-04],AX              ; 保存函数返回值
```

即使关闭优化，编译器仍将除以 4 的余数判断实现为位测试。`TEST` 不修改年份，只设置标志；后面的条件跳转据此选择分支。1900 年在除以 100 时余数为零，走平年路径；2000 年在第一次除以 400 时便确定为闰年。

## 三、月长：寄存器传参和数组寻址

`month_days` 的年份通过 AX 传入，月份通过 DX 传入，分别保存到 `[BP-08]`、`[BP-06]`。

```asm
0071  MOV  [BP-08],AX              ; 保存 year
0074  MOV  [BP-06],DX              ; 保存 month
0077  CMP  WORD PTR [BP-06],+02    ; 是不是二月
007B  JNZ  0087                    ; 非二月不必调用 is_leap
007D  MOV  AX,[BP-08]              ; AX 传递 year
0080  CALL 0010                    ; 调用 is_leap，AX 返回 0/1
0083  TEST AX,AX
0085  JNZ  0089                    ; 二月且闰年，需要加一天
0087  JMP  0090
0089  MOV  WORD PTR [BP-02],0001    ; 增量为 1
008E  JMP  0095
0090  MOV  WORD PTR [BP-02],0000    ; 增量为 0
0095  MOV  BX,[BP-06]              ; BX = month
0098  SHL  BX,1                    ; unsigned int 占两个字节
009A  MOV  AX,[BX+0174]            ; DS 中的 lengths[month-1]
009E  ADD  AX,[BP-02]              ; 普通月长加二月闰年增量
00A1  MOV  [BP-04],AX              ; 保存返回结果
```

本次 `lengths` 的起始偏移为 `0176H`。编译器把 `(month-1)×2` 改写成 `month×2−2`，于是指令里的常量为 `0174H`。例如月份为 1，BX 左移后等于 2，实际读取 `DS:0176H`，仍然是数组第一项。这里的数组元素是 16 位整数，不能照汇编版单字节月长表的方式直接把月份当字节偏移。

## 四、星期计算：两个循环和模 7

`first_day` 的局部变量对应关系为：`[BP-0C]` 是年份参数，`[BP-0A]` 是月份参数，`[BP-06]` 是循环年份 y，`[BP-04]` 是循环月份 m，`[BP-02]` 是 weekday。

```asm
00C0  MOV  WORD PTR [BP-02],0001   ; 初始星期为星期一
00C5  MOV  WORD PTR [BP-06],076C   ; y = 1900
00CA  MOV  AX,[BP-06]
00CD  CMP  AX,[BP-0C]             ; 比较 y 和目标年份
00D0  JAE  00F1                   ; y >= year，开始月循环
00D2  MOV  AX,[BP-06]             ; year 参数放入 AX
00D5  CALL 0010                   ; is_leap(y)
00D8  MOV  DX,[BP-02]             ; DX = weekday
00DB  INC  DX                     ; 平年多一天
00DC  ADD  DX,AX                  ; 闰年再加一天
00DE  MOV  BX,DX                  ; 暂存待取模的数
00E0  MOV  CX,0007
00E3  XOR  DX,DX
00E5  MOV  AX,BX                  ; DX:AX = weekday + 1 + leap
00E7  DIV  CX
00E9  MOV  [BP-02],DX             ; 保存除以 7 的余数
00EC  INC  WORD PTR [BP-06]        ; ++y
00EF  JMP  00CA                   ; 回到年循环条件

00F1  MOV  WORD PTR [BP-04],0001   ; m = 1
00F6  MOV  AX,[BP-04]
00F9  CMP  AX,[BP-0A]
00FC  JAE  011D                   ; m >= month，返回星期
00FE  MOV  DX,[BP-04]             ; DX 传月份 m
0101  MOV  AX,[BP-0C]             ; AX 传年份 year
0104  CALL 0066                   ; month_days(year,m)
0107  MOV  BX,[BP-02]
010A  ADD  BX,AX                  ; weekday + 当前月长
010C  MOV  CX,0007
010F  XOR  DX,DX
0111  MOV  AX,BX
0113  DIV  CX
0115  MOV  [BP-02],DX             ; 更新 weekday
0118  INC  WORD PTR [BP-04]        ; ++m
011B  JMP  00F6                   ; 回到月循环条件
011D  MOV  AX,[BP-02]             ; 取出最终星期
0120  MOV  [BP-08],AX             ; 暂存返回值
0123  MOV  AX,[BP-08]             ; AX 返回 0..6
```

这里没有把总天数一直累加到最后；每轮都取余，所以 16 位变量足以覆盖题目范围。C 的两个 `for` 循环在机器码中表现为比较、条件退出、循环体、自增和向后跳转。

## 五、输入：四个寄存器参数和错误重试

`read_number(prompt,low,high,digits)` 的四个参数分别通过 AX、DX、BX、CX 传入。函数入口将它们保存到栈帧，防止后续库函数调用覆盖参数。

```asm
0137  MOV  [BP-12],AX       ; prompt，DS 内的近指针
013A  MOV  [BP-10],DX       ; low
013D  MOV  [BP-0E],BX       ; high
0140  MOV  [BP-0C],CX       ; digits
0143  MOV  AX,[BP-12]
0146  PUSH AX              ; printf 的字符串参数
0147  MOV  AX,0078         ; "%s" 的地址
014A  PUSH AX              ; printf 的格式参数
014B  CALL 0354            ; printf
014E  ADD  SP,+04          ; 调用者清理两个字的参数
```

普通函数的寄存器传参与 `printf` 的栈传参出现在同一个程序里。`getchar` 在此编译器中包含对输入缓冲区的检查，必要时调用 `fgetc`；完整缓冲处理在 `0162H～019AH`，随后才进行行结束和数字范围判断。

```asm
019D  CMP  WORD PTR [BP-02],+0A    ; 是否换行
01A1  JZ   01A9                   ; 结束当前行
01A3  CMP  WORD PTR [BP-02],-01    ; 是否 EOF
01A7  JNZ  01AB                   ; 普通字符继续处理
01A9  JMP  01ED
01AB  CMP  WORD PTR [BP-02],+0D    ; 忽略回车字符
01AF  JNZ  01B3
01B1  JMP  01EA
01B3  INC  WORD PTR [BP-06]        ; count 增加
01B6  CMP  WORD PTR [BP-02],+30    ; 字符不能小于 '0'
01BA  JL   01C2
01BC  CMP  WORD PTR [BP-02],+39    ; 字符不能大于 '9'
01C0  JLE  01C4
01C2  JMP  01CC                   ; 非数字，置 bad
01C4  MOV  AX,[BP-06]
01C7  CMP  AX,[BP-0C]             ; count 与最大位数比较
01CA  JBE  01D1
01CC  MOV  WORD PTR [BP-04],0001   ; bad = 1
01D1  CMP  WORD PTR [BP-04],+00
01D5  JNZ  01EA                   ; 已出错时继续读完这一行
01D7  MOV  AX,[BP-08]             ; 原累计值 value
01DA  MOV  DX,000A
01DD  MUL  DX                     ; value * 10
01DF  MOV  DX,[BP-02]             ; 当前字符
01E2  SUB  DX,+30                 ; 字符转数位
01E5  ADD  AX,DX                  ; value * 10 + digit
01E7  MOV  [BP-08],AX             ; 保存新累计值
01EA  JMP  0162                   ; E9 75 FF：向后较远的近跳转
```

后面的 `01F3H～021BH` 检查 bad、输入非空及上下界；不合法时在 `021DH` 输出错误提示，`0234H` 的 `E9 0C FF` 跳回提示和重新初始化的位置。这里继续消费错误行的剩余字符，避免剩余字符被误当成下一次输入。

## 六、月历输出：数组、栈参数与换行分支

`print_calendar` 先通过 AX、DX 调用月长与星期函数，把结果分别保存在 `[BP-02]` 和 `[BP-06]`。

```asm
0251  MOV  DX,[BP-0C]             ; 月份
0254  MOV  AX,[BP-0E]             ; 年份
0257  CALL 0066                   ; month_days
025A  MOV  [BP-02],AX             ; days
025D  MOV  DX,[BP-0C]
0260  MOV  AX,[BP-0E]
0263  CALL 00AF                   ; first_day
0266  MOV  [BP-06],AX             ; col
0269  MOV  BX,[BP-0C]
026C  SHL  BX,1                   ; names 的近指针每项两字节
026E  PUSH WORD PTR [BX+018C]      ; 月名字符串指针
0272  MOV  AX,[BP-0E]
0275  PUSH AX                     ; 年份
0276  MOV  AX,009D                ; 标题和星期表头的格式字符串
0279  PUSH AX
027A  CALL 0354                   ; printf
027D  ADD  SP,+06                 ; 清理三个参数
```

前导空格在 `0280H～029AH` 的循环输出，随后日期从 1 开始。每次输出日期后，先判断是否完成一周，再判断是否已经到月底。

```asm
02A9  MOV  AX,[BP-08]             ; day
02AC  PUSH AX
02AD  MOV  AX,00BF                ; "%2u"，两列右对齐
02B0  PUSH AX
02B1  CALL 0354
02B4  ADD  SP,+04
02B7  INC  WORD PTR [BP-06]        ; ++col
02BA  CMP  WORD PTR [BP-06],+07
02BE  JNZ  02CD                   ; 未满一周，转查月底
02C0  MOV  AX,000A                ; 换行字符
02C3  CALL 04A8                   ; putchar
02C6  MOV  WORD PTR [BP-06],0000   ; 新一周从星期日列开始
02CB  JMP  02E3                   ; 直接推进日期，避免重复换行
02CD  MOV  AX,[BP-08]
02D0  CMP  AX,[BP-02]             ; day 是否等于 days
02D3  JNZ  02DD
02D5  MOV  AX,000A                ; 最后一天，结束这一行
02D8  CALL 04A8
02DB  JMP  02E3
02DD  MOV  AX,0020                ; 普通日期后输出一个空格
02E0  CALL 04A8
02E3  INC  WORD PTR [BP-08]        ; ++day
02E6  JMP  02A1                   ; 重新检查 day <= days
```

## 七、主函数：从调用点辨认参数

```asm
02FC  MOV  CX,0004         ; digits = 4
02FF  MOV  BX,0833         ; high = 2099
0302  MOV  DX,076C         ; low = 1900
0305  MOV  AX,00C3         ; 年份提示字符串地址
0308  CALL 012E            ; read_number
030B  MOV  [BP-04],AX      ; 保存年份
```

随后检查返回值。若返回零，说明输入已结束且没有有效年份，主函数返回 1；普通输入错误由 `read_number` 内部重试。月份的调用方式相同，只更换参数：

```asm
031B  MOV  CX,0002         ; 最多两位
031E  MOV  BX,000C         ; 上限 12
0321  MOV  DX,0001         ; 下限 1
0324  MOV  AX,00E3         ; 月份提示字符串地址
0327  CALL 012E
032A  MOV  [BP-02],AX      ; 保存月份
```

取得有效年、月后，主函数通过寄存器传给显示函数：

```asm
033A  MOV  DX,[BP-02]             ; month
033D  MOV  AX,[BP-04]             ; year
0340  CALL 0240                   ; print_calendar
0343  MOV  WORD PTR [BP-06],0000   ; main 返回 0
0348  MOV  AX,[BP-06]             ; 取返回状态
034B  MOV  SP,BP                  ; 释放局部空间
```

本次最直接的对照是：汇编版通过两条 `9A` 指令进入另一个代码段，C small 模型中的这些调用则都是 `E8` 段内近调用；汇编版的 FIRST_DAY 由栈传年、月，C 版 first_day 由 AX、DX 传参。源码中的“函数调用”在机器码上需要结合编译模型和调用约定具体判断。
