'''

initlog.cpp 파일에 로그 추가
'''
from filemanager.window_file_open import get_folder_path
from filemanager.FolderManager import FolderManager
from tests.svn_test.manager_test import project_path

import os

def get_log_file_paths(file_path: str) -> list[str]:
    folder_path = get_folder_path('프로젝트 폴더 선택')
    # print(folder_path)
    folder_manager = FolderManager(folder_path, skip_dir=['.git', '.vs', '.svn', 'x64'])
    file_map = folder_manager.get_file_map()
    init_log_files = file_map.get('InitLog.cpp')

    log_cpp_file_paths = [os.path.normpath(folder_path + '/' + package_path) for package_path in init_log_files]
    # print(log_cpp_file_paths)
    return log_cpp_file_paths

from clangParser.datas.CUnit import CUnit, Cursor

def set_log_init(file_path: str, log_tags: list[str]) -> None:
    if not os.path.exists(file_path):
        print(f"파일이 존재하지 않습니다: {file_path}")
        return

    # 파싱 및 init_logger 메서드 찾기
    unit = CUnit.parse(file_path)
    init_logger_method = None
    for cursor in unit.get_this_Cursor():
        # print(f'cursor: {cursor.kind} - {cursor.get_range_code()}')
        if cursor.kind == 'FUNCTION_DECL' and cursor.spelling == 'init_logger':
            init_logger_method = cursor
            break

    # init_logger 메서드에서 log 태그 여부 체크
    if not init_logger_method:
        print('init_logger 메서드를 찾을 수 없습니다. ', file_path)
    else:
        codes = init_logger_method.get_range_code()
        need_to_add_tags = []
        for tag in log_tags:
            if not f'<{tag}>' in codes:
                need_to_add_tags.append(tag)

        if need_to_add_tags:
            sb = ''
            for tag in need_to_add_tags:
                sb += f'''
    if (plog::get<{tag}>() == nullptr)
	{"{"}
		plog::init<{tag}>(plog::debug, get{tag}Logger());
	{"}"}
'''
            idx = codes.rfind('}') # 마지막 중괄호 위치 찾기
            if idx != -1:
                codes = codes[:idx] + sb + codes[idx:]
            with open(file_path, 'w') as file:
                new_code = unit.code.replace(init_logger_method.get_range_code(), codes)
                file.write(new_code)

if __name__ == "__main__":
    #1. 프로젝트 폴더 선택 및 cpp 파일 경로 가져오기
    log_file_paths = get_log_file_paths(project_path)

    #2. 로그 추가
    log_tags = ['System', 'QA', 'Msg', 'Start', 'End']
    for file_path in log_file_paths:
        set_log_init(file_path, log_tags)

    # if not log_file_paths:
    #     print("InitLog.cpp 파일을 찾을 수 없습니다.")
    # else:
    #     for log_file_path in log_file_paths:
    #         with open(log_file_path, 'a') as log_file:
    #             log_file.write('\n// InitLog.cpp에 로그 추가\n')
    #         print(f'로그가 {log_file_path}에 추가되었습니다.')

