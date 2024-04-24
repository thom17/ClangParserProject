//#include <iostream>

// 함수 선언
void displayMessage();
int add(int a, int b);

int main() {
    //std::cout << "Hello, World!" << std::endl;
    displayMessage(); // 함수 호출
    int result = add(5, 3); // 함수 호출
    //std::cout << "Result of addition: " << result << std::endl;
    return 0;
}

// 함수 정의
void displayMessage() {
    //std::cout << "This is a display message function." << std::endl;
}

// 또 다른 함수 정의
int add(int a, int b) {
    return a + b;
}
