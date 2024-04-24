#include "testA.h"
TestChildA::TestChildA()
:TestClass()
{
}

void TestChildA::run(int a, int b)
{
    __supper::run(a, b);
}