#include <stdio.h>
#undef putchar

static const unsigned int lengths[12] =
    {31,28,31,30,31,30,31,31,30,31,30,31};
static const char *names[12] = {"January","February","March","April",
    "May","June","July","August","September","October","November","December"};

unsigned int is_leap(unsigned int year)
{
    return year % 400 == 0 || (year % 4 == 0 && year % 100 != 0);
}

unsigned int month_days(unsigned int year, unsigned int month)
{
    return lengths[month-1] + (month == 2 && is_leap(year));
}

unsigned int first_day(unsigned int year, unsigned int month)
{
    unsigned int y, m, weekday = 1;
    for (y = 1900; y < year; ++y)
        weekday = (weekday + 1 + is_leap(y)) % 7;
    for (m = 1; m < month; ++m)
        weekday = (weekday + month_days(year, m)) % 7;
    return weekday;
}

unsigned int read_number(const char *prompt, unsigned int low,
                         unsigned int high, unsigned int digits)
{
    unsigned int value, count, bad;
    int ch;
    for (;;) {
        printf("%s", prompt);
        value = count = bad = 0;
        while ((ch = getchar()) != '\n' && ch != EOF) {
            if (ch == '\r') continue;
            ++count;
            if (ch < '0' || ch > '9' || count > digits) bad = 1;
            if (!bad) value = value * 10 + (unsigned int)(ch - '0');
        }
        putchar('\n');
        if (!bad && count && value >= low && value <= high) return value;
        printf("Invalid input. Please try again.\n");
        if (ch == EOF) return 0;
    }
}

void print_calendar(unsigned int year, unsigned int month)
{
    unsigned int day, col, i, days;
    days = month_days(year, month);
    col = first_day(year, month);
    printf("\n%u  %s\nSu Mo Tu We Th Fr Sa\n", year, names[month-1]);
    for (i = 0; i < col; ++i) printf("   ");
    for (day = 1; day <= days; ++day) {
        printf("%2u", day);
        ++col;
        if (col == 7) {
            putchar('\n');
            col = 0;
        } else if (day == days) putchar('\n');
        else putchar(' ');
    }
}

int main(void)
{
    unsigned int year, month;
    year = read_number("Please input year (1900-2099): ",1900,2099,4);
    if (!year) return 1;
    month = read_number("Please input month (1-12): ",1,12,2);
    if (!month) return 1;
    print_calendar(year, month);
    return 0;
}
