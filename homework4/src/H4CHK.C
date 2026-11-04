/* Assignment 4, part 2: compile twice, with or without LOCAL_TABLE. */
#include <stdio.h>

#define TABLE_INIT { \
    {7,2,3,4,5,6,7,8,9}, \
    {2,4,7,8,10,12,14,16,18}, \
    {3,6,9,12,15,18,21,24,27}, \
    {4,8,12,16,7,24,28,32,36}, \
    {5,10,15,20,25,30,35,40,45}, \
    {6,12,18,24,30,7,42,48,54}, \
    {7,14,21,28,35,42,49,56,63}, \
    {8,16,24,32,40,48,56,7,72}, \
    {9,18,27,36,45,54,63,72,81} \
}

#ifndef LOCAL_TABLE
unsigned char table[9][9] = TABLE_INIT;
#endif

int main(void)
{
#ifdef LOCAL_TABLE
    unsigned char table[9][9] = TABLE_INIT;
#endif
    unsigned int x, y;

    puts("x y");
    for (x = 1; x <= 9; ++x) {
        for (y = 1; y <= 9; ++y) {
            if (table[x - 1][y - 1] != x * y)
                printf("%u %u   error\n", x, y);
        }
    }
    puts("\naccomplish!");
    return 0;
}
