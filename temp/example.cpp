
class ClassA {
public:
    int memberA;
    void methodA();
};

void ClassA::methodA() {
    // Implementation of methodA
}

class ClassB : public ClassA {
public:
    float memberB;
    void methodB();
};

void ClassB::methodB() {
    // Implementation of methodB
}
