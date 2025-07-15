'''
모든 메서드에 QA 생성하는걸 목표로.
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
        editor.add_define('#include "../BaseTools/plogger.h"')
        editor.write_file()
        print(editor.file_unit.file_path)




def get_set(node: ClangIndex.Cursor, source_code: str)-> Tuple[Cursor, Optional[Cursor]]:
    #step 3-1. 메서드 필터링
    cursor = Cursor(node=node, source_code=source_code)

    for ch in [Cursor(ch, source_code=source_code) for ch in node.get_children()]:
        if ch.kind == 'COMPOUND_STMT':
            return cursor, ch
    return cursor, None


need_keywords = ['LButton', 'Click', 'OnBn', 'LBDown', 'LBUp', 'KeyDown', 'KeyUp', '_selectTooth']
skip_method = ['GetLbuttonDown', 'OnLButtonDown', 'OnLButtonUp', 'SetLbuttonDown']

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
    else:
        is_static = False

    # 필요한 키워드가 있다면
    for keyword in need_keywords:
        if keyword.lower() in method_cursor.get_src_name().lower():
            return dup_check or mfc_expect or is_static
    
    # 필요한 키워드가 없다면 스킵
    return True

def get_planned_code(method_cursor: Cursor) -> str:
    def is_enable_type(type_name: str) -> bool:
        # 기본 타입인지 확인하는 함수
        base_types = ['int', 'float', 'double', 'char', 'bool', 'void', 'uint', 'WPARAM', 'CUpdateParam', 'LPVOID']
        for tp in base_types:
            if tp in type_name:
                return True
        return False


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
    if 0 < len(child_names):
        for idx, name in enumerate(child_names):
            if 'CPoint' in child_types[idx]:
                parm_log += f'<<" {name} : "<<{name}.x<<","<<{name}.y'
            elif 'float3' in child_types[idx] and not 'vector' in child_types[idx]:
                parm_log += f'<<" {name} : "<<{name}.toCString()'
            elif 'vector' in child_types[idx] or 'std::map' in child_types[idx] or 'std::set' in child_types[idx]:
                parm_log += f'<<" {name} : "<<{name}.size()'
            elif 'CPanoCSPosInfo' in child_types[idx] or 'CArray' in child_types[idx]:
                continue
            elif 'CRect' in child_types[idx]:
                parm_log += f'<<" {name} : "<<{name}.left<<","<<{name}.top<<","<<{name}.right<<","<<{name}.bottom'
            # elif is_enable_type(child_types[idx]):
            else:
                parm_log += f'<<" {name} : "<<{name}'

    log_txt =f'LOGN_(QA){parm_log}; //macro'
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
        



