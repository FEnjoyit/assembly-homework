#include <stdio.h>
#undef putchar

#define WIDTH 21

static unsigned char ready[101] = {1, 1};
static unsigned char cache[101][WIDTH] = {{0}, {1}};

/* Digits are stored in ascending place order, one byte per digit. */
const unsigned char *fib(unsigned int n)
{
    unsigned char *out = cache[n];
    const unsigned char *left, *right;
    unsigned int i, sum, carry;

    if (!ready[n]) {
        left = fib(n - 1);
        right = fib(n - 2);
        carry = 0;
        for (i = 0; i < WIDTH; ++i) {
            sum = left[i] + right[i] + carry;
            carry = sum >= 10;
            out[i] = (unsigned char)(carry ? sum - 10 : sum);
        }
        ready[n] = 1;
    }
    return out;
}

/* Return -1 for EOF, 0 for an invalid line, or a valid index. */
static int read_index(void)
{
    int ch, n = 0, digits = 0, invalid = 0;

    while ((ch = getchar()) != '\n' && ch != EOF) {
        if (ch < '0' || ch > '9' || digits == 3) {
            invalid = 1;
        } else {
            n = n * 10 + ch - '0';
            ++digits;
        }
    }
    if (ch == EOF && digits == 0 && !invalid)
        return -1;
    if (invalid || n < 1 || n > 100)
        return 0;
    return n;
}

static void print_digits(const unsigned char *digits)
{
    int i = WIDTH - 1;
    while (i > 0 && digits[i] == 0)
        --i;
    for (; i >= 0; --i)
        putchar('0' + digits[i]);
    putchar('\n');
}

int main(void)
{
    int n;
    const unsigned char *digits;
    do {
        puts("Enter n (1-100):");
        n = read_index();
        if (n < 0)
            return 1;
        if (n == 0)
            puts("Invalid input. Enter 1 to 100.");
    } while (n == 0);

    digits = fib((unsigned int)n);
    puts("Fibonacci number:");
    print_digits(digits);
    return 0;
}
