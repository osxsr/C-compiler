int a = 0;
int b;

int add(int a, int b) {
    return a + b;
}

int test(int a, int b, int d) {
    int c = a + b + d;
    c += c + 1 * 5.2;
    return c / a + add(a, b);
}