import clang.cindex
import os
import tempfile
import platform
import shutil
from datetime import datetime

target_compile_command = r"D:\dev\AutoPlanning\trunk\AP-6979-TimeTask"

# Auto-detect libclang library path based on platform
try:
    import platform
    import shutil
    
    system = platform.system()
    if system == "Windows":
        # Try common Windows paths
        possible_paths = [
            r"C:\Program Files\LLVM\bin\libclang.dll",
            r"C:\Program Files (x86)\LLVM\bin\libclang.dll"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                clang.cindex.Config.set_library_file(path)
                print(f'libclang 설정 성공: {path}')
                break
    elif system in ["Linux", "Darwin"]:  # Linux or macOS
        # libclang should be auto-detected, but we can help it
        libclang_path = shutil.which("clang")
        if libclang_path:
            print(f'libclang 자동 검색됨: {libclang_path}')
        else:
            print('libclang가 시스템에 설치되어 있는지 확인해주세요')
    
except Exception as e:
    print("libclang 설정 실패 (하지만 시스템 기본값 사용 시도)")
    print(e)

# Platform-specific include paths
system = platform.system()
include_paths = []

if system == "Windows":
    msvc_include_path = r'C:/dev/VS2019 Professional/IDE/VC/Tools/MSVC/14.29.30133/include'
    windows_sdk_include_paths = [
        r'C:/Program Files (x86)/Windows Kits/8.1/Include/shared',
        r'C:/Program Files (x86)/Windows Kits/8.1/Include/um',
        r'C:/Program Files (x86)/Windows Kits/8.1/Include/winrt',
        r'C:/Program Files (x86)/Microsoft Visual Studio 14.0/VC/include',
        r'C:/dev/VS2019 Professional/IDE/VC/Tools/MSVC/14.29.30133/atlmfc/include',
        r'C:/Program Files (x86)/Microsoft Visual Studio 2019/Community/VC/Tools/MSVC/14.29.30133/include',
        r'C:/Program Files (x86)/Windows Kits/10/Include/10.0.19041.0/ucrt',
        r'C:/Program Files (x86)/Microsoft Visual Studio 14.0/VC/include',
        r'C:/Program Files (x86)/Microsoft Visual Studio 14.0/VC/atlmfc/include',
    ]
    # Only add paths that actually exist
    include_paths = [msvc_include_path] + [path for path in windows_sdk_include_paths if os.path.exists(path)]
elif system == "Linux":
    # Common Linux system include paths
    linux_include_paths = [
        '/usr/include',
        '/usr/include/c++',
        '/usr/local/include',
    ]
    include_paths = [path for path in linux_include_paths if os.path.exists(path)]
elif system == "Darwin":  # macOS
    # Common macOS include paths
    macos_include_paths = [
        '/usr/include',
        '/usr/local/include',
        '/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/usr/include',
    ]
    include_paths = [path for path in macos_include_paths if os.path.exists(path)]

'''
#27 헤더 인식 문제 (참고)
include 파일을 추가하지 않아도 <vector> 와 같은 기본 헤더는 발견시 인식되는 것 같다.
또 오히려 추가할 경우 임시 파일의 vector 선언을 인식 못 하는거 봐서
일단은 경로 추가는 사용 x 
'''
args = [
           '-std=c++14',  # C++14 표준 사용
           '-x', 'c++',  # 처리할 파일의 언어를 C++로 지정
           # '-nostdinc++', #활성화 할경우 기본 경로 무시 처리
           '-D_MSC_VER=1929',
           '-D__MSVCRT__',
        # f"-include {r'D:/temp/target/data/test_head.h'}",
       ] #+ [f'-I {path}' for path in include_paths]

# for path in include_paths:
#     args.extend(['-I', path])
# args

def parse_context(context: str, file_path:str = None, file_remove: bool = True) -> clang.cindex.TranslationUnit:
    """
    문자열을 입력받아 임시파일을 생성하고
    생선된 파일을 파싱후 삭제
    :param context:
    :return:
    """

    def generate_filename(prefix="file", extension="txt"):
        # 현재 시간을 기반으로 파일명 생성
        return


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



def simple_visit(node: clang.cindex.Cursor, i=0):
    in_tab = '\t' * i
    print(f"{in_tab}{node.kind} : {node.spelling}")

    for child_node in node.get_children():
        simple_visit(child_node, i+1)



def find_cpp_files(directory:str, add_h: bool = True) ->list[str]:
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
