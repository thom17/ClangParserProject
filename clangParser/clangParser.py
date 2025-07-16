import clang.cindex
import os
import tempfile
from datetime import datetime
import platform

# Configure libclang library path based on platform
def setup_libclang():
    """Setup libclang library path based on the current platform."""
    system = platform.system()
    
    if system == "Windows":
        # Try common Windows paths
        common_paths = [
            r"C:\Program Files\LLVM\bin\libclang.dll",
            r"C:\Program Files (x86)\LLVM\bin\libclang.dll",
        ]
        for path in common_paths:
            if os.path.exists(path):
                try:
                    clang.cindex.Config.set_library_file(path)
                    print(f'libclang 설정 성공: {path}')
                    return True
                except Exception as e:
                    continue
    elif system == "Linux":
        # Try common Linux paths
        try:
            clang.cindex.Config.set_library_file("libclang.so")
            print('libclang 설정 성공 (Linux)')
            return True
        except Exception:
            pass
    elif system == "Darwin":  # macOS
        try:
            clang.cindex.Config.set_library_file("libclang.dylib")
            print('libclang 설정 성공 (macOS)')
            return True
        except Exception:
            pass
    
    print("libclang 설정 실패 - 기본 설정을 사용합니다")
    return False

# Initialize libclang
setup_libclang()

# Compiler arguments for cross-platform compatibility
args = [
    '-std=c++14',  # C++14 표준 사용
    '-x', 'c++',   # 처리할 파일의 언어를 C++로 지정
]

# Add platform-specific arguments
if platform.system() == "Windows":
    args.extend([
        '-D_MSC_VER=1929',
        '-D__MSVCRT__',
    ])

# Note: 헤더 인식 문제 (참고)
# include 파일을 추가하지 않아도 <vector> 와 같은 기본 헤더는 발견시 인식되는 것 같다.
# 또 오히려 추가할 경우 임시 파일의 vector 선언을 인식 못 하는거 봐서
# 일단은 경로 추가는 사용 x

def parse_context(context: str, file_path: str = None, file_remove: bool = True) -> clang.cindex.TranslationUnit:
    """
    문자열을 입력받아 임시파일을 생성하고
    생성된 파일을 파싱후 삭제
    
    :param context: 파싱할 C++ 코드 문자열
    :param file_path: 임시 파일명 prefix (optional)
    :param file_remove: 파싱 후 임시 파일 삭제 여부
    :return: Clang TranslationUnit 객체
    """
    temp_path = 'parse_context.cpp'
    if file_path is not None:
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_path = f"{file_path}_parse_context_{current_time}.cpp"

    # 임시 파일 생성
    # with tempfile.NamedTemporaryFile(delete=False, suffix='.cpp') as temp:
    with open(temp_path, 'w', encoding='utf-8') as temp:
        # 코드를 임시 파일에 쓰기
        temp.write(context)
    tu = parsing(temp_path)   #close 해야 save된다.

    if file_remove:
        os.remove(temp_path)

    return tu

def parsing(file_path: str):
    # Clang 라이브러리 파일 설정
    index = clang.cindex.Index.create()

    # compile_commands.json 파일 위치 지정
    # clang.cindex.CompilationDatabase.fromDirectory(target_compile_command)

    assert os.path.isfile(file_path), f"파일 없음 : {file_path}"

    # 파일 파싱
    translation_unit = index.parse(file_path, args=args)

    return translation_unit

def parsing_files(file_list: [str]):
    # Clang 라이브러리 파일 설정
    index = clang.cindex.Index.create()

    # compile_commands.json 파일 위치 지정
    # clang.cindex.CompilationDatabase.fromDirectory(target_compile_command)

    # 파일 파싱
    unit_list = []
    for file_path in file_list:
        translation_unit = index.parse(file_path, args=args)
        unit_list.append(translation_unit)

    return unit_list



def simple_visit(node: clang.cindex.Cursor, i: int = 0):
    """재귀적으로 AST 노드를 방문하며 출력하는 간단한 방문자 함수"""
    in_tab = '\t' * i
    print(f"{in_tab}{node.kind} : {node.spelling}")

    for child_node in node.get_children():
        simple_visit(child_node, i + 1)


def find_cpp_files(directory: str, add_h: bool = True):
    """
    디렉토리에서 C++ 파일들을 찾는 제너레이터
    
    :param directory: 검색할 디렉토리 경로
    :param add_h: .h 헤더 파일도 포함할지 여부
    :yield: C++ 파일 경로들
    """
    find_type = '.cpp'
    if add_h:
        find_type = ('.cpp', '.h')
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(find_type):
                yield os.path.join(root, file)





def parse_project(directory):
    # clang.cindex.Config.set_library_file(r"C:\Program Files\LLVM\bin\libclang.dll")
    index = clang.cindex.Index.create()

    # compile_commands.json 파일 위치 지정
    # clang.cindex.CompilationDatabase.fromDirectory(target_compile_command)

    # 프로젝트 디렉토리 내의 모든 C++ 파일을 찾음
    files = list(find_cpp_files(directory))

    # 각 파일을 파싱
    translation_units = []
    for file in files:
        print(f"parse {file}")
        tu = index.parse(file, args=args)
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
