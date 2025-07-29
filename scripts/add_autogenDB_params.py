'''
모든 메서드에 생성하는걸 목표로.
파라미터 추가
'''
import sys
import argparse
import os

from typing import Tuple, Optional, Dict


from clangParser.datas.Cursor import Cursor
import clang.cindex as ClangIndex
import tkinter as tk
from tkinter import filedialog

import clangParser.clangParser as ClangParser
from clangParser.datas.CUnit import CUnit
from code_editor.code_editor import CodeEditor, insert_code_in_block_start


def get_file_list():
    #step1. 파일 리스트 입력 받기.
    if len(sys.argv) == 1:
        root = tk.Tk()
        root.withdraw()
        pathinfo = filedialog.askdirectory(title="폴더를 선택하세요")
    elif len(sys.argv) < 2:
        pathinfo = sys.argv[1]
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument('--path', type=str, required=True, help="Input dir or file path")
        args = parser.parse_args()
        pathinfo = args.path

    return list(ClangParser.find_cpp_files(pathinfo, add_h=False))

def parse_files(file_paths: list[str]) -> dict[str, CodeEditor]:
    #step2. 각각의 파일 파싱 및 임시 파일 생성.
    file_edit_map = {}


    for progress, file_path in enumerate(file_paths):
        print(f'\r({progress} / {len(file_paths)}) ', end=file_path+'\t\t')
        if os.path.isfile(file_path.replace('.cpp', '.h')): # 짝이 있는 파일만 파싱
            unit = CUnit.parse(file_path)
            file_edit_map[file_path] = CodeEditor(unit)
    return file_edit_map



def edit_unit(editor: CodeEditor):
    #step3. 하나의 파일에 대하여 수정


    head_unit = CUnit.parse(editor.file_unit.file_path.replace('.cpp', '.h'))
    src_pair_map = CUnit.get_src_pair_map(editor.file_unit, head_unit)
    change_counts = 0

    for node in editor.file_unit.this_file_nodes:
        method_cursor, stmt_cursor = get_set(node=node, source_code=editor.file_unit.code)
        if stmt_cursor:
            org_method_code = method_cursor.get_range_code()
            debug_code = get_planned_code(method_cursor=method_cursor)
            if is_skip_method(method_cursor, debug_code, src_pair_map): #이미 추가된 코드 스킵
                replace_method = org_method_code.replace(debug_code, '')
                editor.add_replace_node(method_cursor, replace_code=replace_method)
            else:
                replace_block = insert_code_in_block_start(block=stmt_cursor, insert_code= debug_code)
                org_block = stmt_cursor.get_range_code()
                replace_method = org_method_code.replace(org_block, replace_block)
                editor.add_replace_node(method_cursor, replace_code=replace_method)
                change_counts += 1
    if change_counts:
        editor.add_define('#include "../DataAccessor/DAutoGenTester.h"')
        editor.write_file()
        print(editor.file_unit.file_path)




def get_set(node: ClangIndex.Cursor, source_code: str)-> Tuple[Cursor, Optional[Cursor]]:
    #step 3-1. 메서드 필터링
    cursor = Cursor(node=node, source_code=source_code)

    for ch in [Cursor(ch, source_code=source_code) for ch in node.get_children()]:
        if ch.kind == 'COMPOUND_STMT':
            return cursor, ch
    return cursor, None


# need_keywords = ['LButton', 'Click', 'OnBn', 'LBDown', 'LBUp', 'KeyDown', 'KeyUp', '_selectTooth']
# skip_method = ['GetLbuttonDown', 'OnLButtonDown', 'OnLButtonUp', 'SetLbuttonDown']

#일단 모두 추가

skip_method = []

import csv
def read_filter_csv_file(file_path: str = 'filtered_methods.csv') -> Dict[str, str]:
    result = {}
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # 첫 줄은 헤더
        for row in reader:
            if row:
                result[row[0]] = row[0]
    return result

def is_skip_method(method_cursor: Cursor, debug_code: str, src_pair_map: Dict[str, Tuple[Optional[Cursor], Optional[Cursor]]]):
    # step 3-2. 메서드 필터링
    for skip in skip_method:
        if skip in method_cursor.get_src_name():
            return True

    method_code = method_cursor.get_range_code()


    dup_check = debug_code in method_code
    mfc_expect = 'BEGIN_MESSAGE_MAP' in method_code or 'IMPLEMENT_DYNAMIC' in method_code
    head_cursor = src_pair_map[method_cursor.get_src_name()][1]
    if head_cursor:
        is_static = head_cursor.node.is_static_method()
    elif method_code.startswith('UINT'):
        is_static = True  # UINT 으로 시작하는 경우는 static 함수로 간주
    else:
        is_static = False

    target_methods = read_filter_csv_file(r'target_methods.csv')
    if method_cursor.get_src_name() in target_methods:
        return dup_check or mfc_expect or is_static
    else:
        return True
    # return dup_check or mfc_expect or is_static

    # # 필요한 키워드가 있다면
    # for keyword in need_keywords:
    #     if keyword.lower() in method_cursor.get_src_name().lower():
    #         return dup_check or mfc_expect or is_static
    #
    # # 필요한 키워드가 없다면 스킵
    # return True

def get_planned_code(method_cursor: Cursor) -> str:
    #step 3-2. 메서드에 해당하는 삽입 코드 구하기
    if method_cursor.kind != 'CXX_METHOD':
        return ''

    #단순 출력
    src_name = method_cursor.get_src_name()
    print(src_name)
    # print(method_cursor.get_range_code())
    # for ch in method_cursor.get_children():
    #     print(f"{ch} {ch.get_range_code()}")
    # #단순 출력

    child_types: list[str] = []
    child_names : list[str] = []
    for ch in method_cursor.get_children():
        if ch.kind == 'PARM_DECL':
            if ch.node.spelling:
                child_names.append(ch.node.spelling)
                child_types.append(ch.get_range_code().replace(ch.node.spelling, ''))

    parm_log = ""
    parm_refs = ''
    parm_info_txt = ''
    if 0 < len(child_names):
        for idx, name in enumerate(child_names):
            def is_pointer_type(type_name: str) -> bool:
                # 포인터 타입인지 확인하는 함수
                type_name = type_name.strip()
                type_name=type_name.replace('const', '')  # const 제거
                return type_name.endswith('*') or type_name.endswith('*&')
            is_pointer = is_pointer_type(child_types[idx])
            connect = '->' if is_pointer else '.'

            if 'CArray' in child_types[idx]:
                parm_log += f'{name}.size: %d\\n'
                parm_refs += f', {name}{connect}GetSize()'
            elif 'vector' in child_types[idx] or 'std::map' in child_types[idx] or 'std::set' in child_types[idx]:
                parm_log += f'{name}.size : %d\\n'
                parm_refs += f', {name}{connect}size()'
            elif 'CPoint' in child_types[idx]:
                parm_log += f'{name} : %d, %d\\n'
                parm_refs += f', {name}{connect}x, {name}{connect}y'
            elif 'float3' in child_types[idx] and not 'vector' in child_types[idx]:
                parm_log += f'{name} : %s\\n'
                parm_refs += f', {name}{connect}toCString()'
            elif 'CPanoCSPosInfo' in child_types[idx] or 'CArray' in child_types[idx]:
                continue
            elif 'CRect' in child_types[idx]:
                parm_log += f'{name} : %d, %d, %d, %d = (%d x %d)\\n'
                parm_refs += f', {name}{connect}left, {name}{connect}top, {name}{connect}right, {name}{connect}bottom, {name}{connect}Width(), {name}{connect}Height()'
            # elif is_enable_type(child_types[idx]):
            else:
                def get_format(type_name:str):
                    type_name = type_name.strip()
                    if type_name in ['int', 'bool', 'UINT', 'WPARAM', 'BOOL']:
                        return '%d'
                    elif type_name in ['float', 'double']:
                        return '%.2f'
                    elif type_name in ['char', 'CString', 'LPCTSTR']: #'LPVOID', 'void*']:
                        return '%s'
                    else:
                        return ''

                format = get_format(child_types[idx])
                if format:
                    parm_log += f'{name} : {format}\\n'
                    parm_refs += f', {name}'


        parm_info_txt = f'CString parmInfos = L""; parmInfos.Format(_T("{parm_log}"){parm_refs});\n\t'
    if parm_info_txt:
        log_txt = f'DAutoGenDB debugDB(L"{src_name}", CString(typeid(*this).name()), parmInfos); //macro'
    else:
        log_txt =f'DAutoGenDB debugDB(L"{src_name}", CString(typeid(*this).name())); //macro'
    log_txt = "//macro\n\t"+parm_info_txt + log_txt
    return log_txt


    # add_code = f'\t//auto-gen\n\tCString _debug_name_id = L"{src_name}";\n'
    # add_code += '\t_debug_name_id.Format(_T("%s::%s"), _debug_name_id, typeid(*this).name());\n'
    # add_code += '\tDAutoGenDB debugGen(_debug_name_id);\n'
    # return add_code

if __name__ == "__main__":
    print(sys.argv)
    file_paths = get_file_list()
    print('find .cpp files', len(file_paths))

    file_edit_map = parse_files(file_paths=file_paths)
    print('parse_files files', len(file_edit_map))

    for path, editor in file_edit_map.items():
        edit_unit(editor=editor)
        



