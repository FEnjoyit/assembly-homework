/* Assignment 3: 8086, 16-bit DOS, unsigned 16-bit sum. */
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
