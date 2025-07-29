# import os
# import re
#
#
# def add_try_catch_to_methods(project_path,
#                              exception_handler_code='// TODO: Add specific exception handling logic here'):
#     """
#     지정된 MFC C++ 프로젝트 경로 내의 모든 .cpp 파일에서 메서드에 try-catch 블록을 추가합니다.
#
#     Args:
#         project_path (str): MFC C++ 프로젝트의 루트 경로.
#         exception_handler_code (str): catch 블록 내에 삽입할 코드. 기본값은 TODO 주석.
#     """
#
#     print(f"'{project_path}' 경로에서 .cpp 파일들을 스캔하며 메서드에 try-catch를 추가합니다...")
#
#     method_start_pattern = re.compile(
#         r'^(?P<indent>\s*)(?P<return_type>\S.*\S)\s+(?P<class_name>\w+::)?(?P<method_name>\w+)\s*\((?P<params>.*)\)\s*\{'
#     )
#     # 메서드 정의 시작 부분을 찾기 위한 정규식
#     # 그룹: indent (들여쓰기), return_type (반환형), class_name (클래스::), method_name (메서드명), params (매개변수)
#
#     processed_files_count = 0
#
#     for root, _, files in os.walk(project_path):
#         for file_name in files:
#             if file_name.endswith('.cpp'):
#                 file_path = os.path.join(root, file_name)
#                 print(f"  파일 처리 중: {file_path}")
#
#                 with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
#                     lines = f.readlines()
#
#                 new_lines = []
#                 in_method = False
#                 brace_level = 0
#                 method_indent = ""
#                 method_name = ""
#
#                 for i, line in enumerate(lines):
#                     match = method_start_pattern.match(line)
#
#                     if match and not in_method:
#                         # 메서드 시작 부분을 찾음
#                         # 단, 현재 줄에 'class'나 'struct' 키워드가 포함되어 타입 정의일 가능성이 있는 경우는 건너김.
#                         # (간단한 회피책, 완벽하지 않음)
#                         if 'class' in line or 'struct' in line:
#                             new_lines.append(line)
#                             continue
#
#                         in_method = True
#                         method_indent = match.group('indent')
#                         method_name = f"{match.group('class_name') or ''}{match.group('method_name')}"
#
#                         # 메서드 시작 줄에 'try {' 삽입
#                         new_lines.append(line.rstrip() + '\n')  # 기존 '}' 줄 유지
#                         new_lines.append(f"{method_indent}    try\n")
#                         new_lines.append(f"{method_indent}    {{\n")
#                         brace_level = 1  # try { } 블록의 첫 번째 중괄호
#
#                         # 다음 줄부터 실제 메서드 내용 시작
#                         continue
#
#                     if in_method:
#                         # 메서드 내부 로직
#                         for char in line:
#                             if char == '{':
#                                 brace_level += 1
#                             elif char == '}':
#                                 brace_level -= 1
#
#                         if brace_level == 0:
#                             # 메서드의 끝 중괄호 '}'를 찾음
#                             new_lines.append(f"{method_indent}    }}\n")  # try 블록 닫기
#                             new_lines.append(f"{method_indent}    catch (const CException* pEx)\n")  # MFC CException 처리
#                             new_lines.append(f"{method_indent}    {{\n")
#                             new_lines.append(f"{method_indent}        // '{method_name}' 메서드에서 MFC CException 발생!\n")
#                             new_lines.append(f"{method_indent}        pEx->ReportError();\n")  # MFC CException 보고
#                             new_lines.append(f"{method_indent}        pEx->Delete();\n")  # CException 객체 삭제
#                             new_lines.append(f"{method_indent}    }}\n")  # catch 블록 닫기
#                             new_lines.append(f"{method_indent}    catch (const std::exception& e)\n")  # 표준 C++ 예외 처리
#                             new_lines.append(f"{method_indent}    {{\n")
#                             new_lines.append(
#                                 f"{method_indent}        TRACE(L\"'%s' 메서드에서 표준 예외 발생: %S\\n\", L\"{method_name}\", e.what());\n")
#                             new_lines.append(
#                                 f"{method_indent}        OutputDebugStringW(L\"'%s' 메서드에서 표준 예외 발생: \");\n")
#                             new_lines.append(f"{method_indent}        OutputDebugStringA(e.what());\n")
#                             new_lines.append(f"{method_indent}        OutputDebugStringW(L\"\\n\");\n")
#                             new_lines.append(f"{method_indent}        {exception_handler_code}\n")
#                             new_lines.append(f"{method_indent}    }}\n")  # catch 블록 닫기
#                             new_lines.append(f"{method_indent}    catch (...)\n")  # 알 수 없는 예외 처리
#                             new_lines.append(f"{method_indent}    {{\n")
#                             new_lines.append(
#                                 f"{method_indent}        TRACE(L\"'%s' 메서드에서 알 수 없는 예외 발생!\\n\", L\"{method_name}\");\n")
#                             new_lines.append(
#                                 f"{method_indent}        OutputDebugStringW(L\"'%s' 메서드에서 알 수 없는 예외 발생!\\n\");\n")
#                             new_lines.append(f"{method_indent}        {exception_handler_code}\n")
#                             new_lines.append(f"{method_indent}    }}\n")  # catch 블록 닫기
#
#                             new_lines.append(line)  # 원래 닫는 중괄호 '}' 추가
#
#                             in_method = False
#                             method_indent = ""
#                             method_name = ""
#                         else:
#                             new_lines.append(line)
#                     else:
#                         new_lines.append(line)
#
#                 # 파일에 쓰기 (기존 파일 덮어쓰기)
#                 # **주의: 실제 사용 시에는 백업본을 만들거나 다른 이름으로 저장하는 로직을 추가하는 것이 좋습니다.**
#                 with open(file_path, 'w', encoding='utf-8') as f:
#                     f.writelines(new_lines)
#                 processed_files_count += 1
#
#     print(f"\n총 {processed_files_count}개의 .cpp 파일에 try-catch 블록 추가를 시도했습니다.")
#     print("수동 검토 및 테스트가 필수적입니다.")
#
#
# # 사용 예시:
# if __name__ == "__main__":
#     # TODO: 여기에 실제 MFC C++ 프로젝트의 경로를 입력하세요.
#     # 예: project_root_directory = "C:/MyMFCProject"
#     project_root_directory = r"D:\dev\AutoPlanning\trunk\Ap-Trunk-auto-task\mod_APWorkSpace"
#
#     if not os.path.isdir(project_root_directory):
#         print(f"오류: 지정된 경로 '{project_root_directory}'를 찾을 수 없습니다.")
#         print("스크립트를 실행하기 전에 'project_root_directory' 변수를 올바른 프로젝트 경로로 설정하세요.")
#     else:
#         add_try_catch_to_methods(project_root_directory)