int a;
int b;
int program(int a, int b, int c)
{
    int i;
    int j;
    float m;
    i = 0;
    //j = m;
    //m = i;
    //i = m;
    //i = j * m;
    if (a > (b + c))
    {
        j = a + (b * c + 1);
    }
    else
    {
        j = a;
    }
    while (i <= 100)
    {
        i = j * 2;
    }
    return i;
}
int demo(int a)
{
    a = a + 2;
    return a * 2;
}
int main(void)
{
    int a;
    int b;
    int c;
    a = 3;
    b = 4;
    c = 2;
    a = pr(a, b, demo(c));
    return 0;
}