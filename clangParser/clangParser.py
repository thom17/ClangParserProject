import clang.cindex
import os
import tempfile

clang.cindex.Config.set_library_file(r"C:\Program Files\LLVM\bin\libclang.dll")

def parse_context(context: str, file_remove = True) -> clang.cindex.TranslationUnit:
    """
    문자열을 입력받아 임시파일을 생성하고
    생선된 파일을 파싱후 삭제
    :param context:
    :return:
    """
    # 임시 파일 생성
    # with tempfile.NamedTemporaryFile(delete=False, suffix='.cpp') as temp:
    with open('parse_context.cpp', 'w', encoding='utf-8') as temp:
        # 코드를 임시 파일에 쓰기
        temp.write(context)
    tu = parsing('parse_context.cpp')   #close 해야 save된다.

    if file_remove:
        os.remove('parse_context.cpp')

    return tu

def parsing(file_path: str):
    # Clang 라이브러리 파일 설정
    index = clang.cindex.Index.create()
    return index.parse(file_path, args=['-std=c++14'])


def simple_visit(node: clang.cindex.Cursor, i=0):
    in_tab = '\t' * i
    print(f"{in_tab}{node.kind} : {node.spelling}")

    for child_node in node.get_children():
        simple_visit(child_node, i+1)



def find_cpp_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.cpp', '.h')):
                yield os.path.join(root, file)

def parse_project(directory):
    # clang.cindex.Config.set_library_file(r"C:\Program Files\LLVM\bin\libclang.dll")
    index = clang.cindex.Index.create()

    # 프로젝트 디렉토리 내의 모든 C++ 파일을 찾음
    files = list(find_cpp_files(directory))

    # 각 파일을 파싱
    translation_units = []
    for file in files:
        print(f"parse {file}")
        tu = index.parse(file, args=[
            '-x', 'c++', '-std=c++14',
            '-I', 'path/to/include',  # 추가 인클루드 경로
            '-D__CODE_GENERATOR__'   # 필요한 경우 매크로 정의
        ])
        translation_units.append(tu)

    return translation_units

if __name__ == "__main__":
    cpp_code = """
    #include <iostream>
    using namespace std;

    void hello() {
        cout << "Hello, world!" << endl;
    }

    int main() {
        hello();
        return 0;
    }
    """

    # 문자열 파싱 함수 호출
    tu = parse_context(cpp_code)
    print(tu)



    # import tkinter as tk
    # from tkinter import filedialog
    # import time
    #
    # root = tk.Tk()
    # root.withdraw()  # Hide the Tkinter window
    #
    # folder_path = filedialog.askdirectory()  # Folder dialog
    # # Use the selected folder path for further processing
    # print("Selected folder:", folder_path)
    #
    # start_time = time.time()
    # tus = parse_project(folder_path)
    #
    # # 결과 처리 및 출력
    # for tu in tus:
    #     print(tu.spelling, "contains", len(list(tu.cursor.get_children())), "elements")
    #
    # # Record the end time
    # end_time = time.time()
    #
    # # Calculate the elapsed time
    # elapsed_time = end_time - start_time
    # print("Elapsed time:", elapsed_time, "seconds")




# if __name__:
#     import tkinter as tk
#     from tkinter import filedialog
#
#     root = tk.Tk()
#     root.withdraw()  # Tkinter 창 숨기기
#
#     file_path = filedialog.askopenfilename()  # 파일 대화 상자 열기
#     unit = parsing(file_path)
#     simple_visit(unit.cursor)
#
#     print(unit.spelling)
