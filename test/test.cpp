#include "test.h"
#include <iostream>
TestClass::TestClass()
{
    std::cout<<"test\n";
}

void TestClass::run(int a, int b)
{
    for(int i =0; i<a; i++)
        std::cout<<b;
}