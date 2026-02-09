'''
모든 메서드에 메서드 src로 DAutoGen을 생성하는걸 목표로.
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

    for node in editor.file_unit.this_file_nodes:
        method_cursor, stmt_cursor = get_set(node=node, source_code=editor.file_unit.code)
        if stmt_cursor:
            org_method_code = method_cursor.get_range_code()
            debug_code = get_planned_code(method_cursor=method_cursor, head_unit=head_unit)
            if is_skip_method(method_cursor, debug_code, head_unit): #이미 추가된 코드 스킵
                continue

            replace_block = insert_code_in_block_start(block=stmt_cursor, insert_code= debug_code)
            org_block = stmt_cursor.get_range_code()
            replace_method = org_method_code.replace(org_block, replace_block)
            editor.add_replace_node(method_cursor, replace_code=replace_method)

    editor.add_define('#include "../BaseTools/plogger.h"', check_dup=False)
    editor.write_file()
    print(editor.file_unit.file_path)




def get_set(node: ClangIndex.Cursor, source_code: str)-> Tuple[Cursor, Optional[Cursor]]:
    #step 3-1. 메서드 필터링
    cursor = Cursor(node=node, source_code=source_code)

    for ch in [Cursor(ch, source_code=source_code) for ch in node.get_children()]:
        if ch.kind == 'COMPOUND_STMT':
            return cursor, ch
    return cursor, None

def is_skip_method(method_cursor: Cursor, debug_code: str, head_unit: CUnit) -> bool:
    # step 3-2. 메서드 필터링
    method_code = method_cursor.get_range_code()

    dup_check = debug_code in method_code
    mfc_expect = 'BEGIN_MESSAGE_MAP' in method_code or 'IMPLEMENT_DYNAMIC' in method_code
    

    return dup_check or mfc_expect


def get_planned_code(method_cursor: Cursor, head_unit: CUnit) -> str:
    #step 3-2. 메서드에 해당하는 삽입 코드 구하기

    src_name = method_cursor.get_src_name()
    if '.' in src_name: #method_cursor == 'CXX_METHOD': (생성자, 소멸자 등 단순 처리로는 복잡할듯. 뭔가 host 개념이 있다면 . 이 있을것
        src_pair_map: Dict[str, Tuple[Optional[Cursor], Optional[Cursor]]] = CUnit.get_src_pair_map(editor.file_unit, head_unit)
        head_cursor = src_pair_map[method_cursor.get_src_name()][1]
        
        is_static = False
        if head_cursor:
            is_static = head_cursor.node.is_static_method()
        else: # 헤더에 없는 경우아마도 파싱 실패일 가능성이 있음.
            simple_name = src_name.split('.')[-1].split('(')[0]

            for line in head_unit.code.splitlines():
                if 'static' in line and simple_name in line:
                    is_static = True
                    break   

        if not is_static:
            return f'LOGN_(System)<<"AutoGen "<<CString(typeid(*this).name());'

    return f'LOGN_(System)<<"AutoGen";'


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
        



