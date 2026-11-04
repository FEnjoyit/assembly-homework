/* Assignment 4, part 1: descending triangular multiplication table. */
#include <stdio.h>
#undef putchar

int main(void)
{
    unsigned int x, y, product;

    puts("The 9mul9 table:");
    for (x = 9; x != 0; --x) {
        for (y = 1; y <= x; ++y) {
            product = x * y;
            printf("%u*%u=%u", x, y, product);
            if (y != x)
                printf("%s", product < 10 ? "   " : "  ");
        }
        putchar('\n');
    }
    return 0;
}
