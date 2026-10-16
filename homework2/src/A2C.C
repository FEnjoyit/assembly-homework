/* Assignment 2, part 3: compile for 8086, 16-bit DOS. */
#include <stdio.h>
/* Keep putchar as a function call for readable disassembly. */
#undef putchar

int main(void)
{
    int row;
    int col;
    int ch = 'a';

    for (row = 0; row < 2; ++row) {
        for (col = 0; col < 13; ++col) {
            putchar(ch);
            ++ch;
            if (col < 12) {
                putchar(' ');
            }
        }
        putchar('\n');
    }
    return 0;
}
