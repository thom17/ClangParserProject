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

from filemanager.window_file_open import get_file_path

def get_file_list():
    #step1. 파일 리스트 입력 받기.
    if len(sys.argv) == 1:
        root = tk.Tk()
        root.withdraw()
        # pathinfo = filedialog.askopenfilename(title="파일을 선택하세요")
        pathinfo = filedialog.askdirectory(title="폴더를 선택하세요")

        # return [get_file_path(file_types=[], title='파일 입력', multiple=True)[0]]
        
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
            debug_code = 'try { //add-macro'
            if is_skip_method(method_cursor, debug_code, src_pair_map): #이미 추가된 코드 스킵
                continue
            else:
                replace_block = insert_code_in_block_start(block=stmt_cursor, insert_code= debug_code)
                replace_block += get_catch_code(method_cursor)
                org_block = stmt_cursor.get_range_code()
                replace_method = org_method_code.replace(org_block, replace_block)
                editor.add_replace_node(method_cursor, replace_code=replace_method)
                change_counts += 1

    if change_counts:
        # editor.add_define('#include "../DataAccessor/DAutoGenTester.h"')
        editor.add_define('#include "../BaseTools/plogger.h"') #다중 지원 안됨
        # editor.add_define('#include "../DataAccessor/DAutoGenTester.h"\n#include "../BaseTools/plogger.h"')

        editor.write_file()
        print(editor.file_unit.file_path)




def get_set(node: ClangIndex.Cursor, source_code: str)-> Tuple[Cursor, Optional[Cursor]]:
    #step 3-1. 메서드 필터링
    cursor = Cursor(node=node, source_code=source_code)

    for ch in [Cursor(ch, source_code=source_code) for ch in node.get_children()]:
        if ch.kind == 'COMPOUND_STMT':
            return cursor, ch
    return cursor, None

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

# with open('filtered_methods.csv', 'w', newline='', encoding='utf-8') as csvfile:
#     writer = csv.writer(csvfile)
# writer.writerow(['Method Name'])  # Header
# for method_name in sorted(src_name_set):
#     writer.writerow([method_name])

def is_skip_method(method_cursor: Cursor, debug_code: str, src_pair_map: Dict[str, Tuple[Optional[Cursor], Optional[Cursor]]]):
    # step 3-2. 메서드 필터링
    method_code = method_cursor.get_range_code()
    is_cls_method = method_cursor.kind == 'CXX_METHOD'

    dup_check = debug_code in method_code
    mfc_expect = 'BEGIN_MESSAGE_MAP' in method_code or 'IMPLEMENT_DYNAMIC' in method_code
    return dup_check or mfc_expect
    #
    # head_cursor = src_pair_map[method_cursor.get_src_name()][1]
    # if head_cursor:
    #     is_static = head_cursor.node.is_static_method()
    # else:
    #     is_static = False

    # file_srcs = read_filter_csv_file(r'target_methods.csv')
    # is_in_file = method_cursor.src_name in file_srcs


    ## 필요한 키워드가 있다면
    # if is_in_file:
    #     for keyword in need_keywords:
    #         if keyword.lower() in method_cursor.get_src_name().lower():
    #             return dup_check or mfc_expect or is_static or not is_cls_method
    #
    ## 필요한 키워드가 없다면 스킵
    # return True

def get_catch_code(method_cursor: Cursor) -> str:
    def is_pointer_type(type_name: str) -> bool:
        pointer_types = ['*', '*&', '*const']
        for tp in pointer_types:
            if type_name.strip().endswith(tp):
                return True
        return False
    def is_collection_type(type_name: str) -> bool:
        collection_types = ['vector', 'std::list', 'std::set', 'std::map', 'unordered_map', 'unordered_set']
        for tp in collection_types:
            if tp in type_name:
                return True
        return False

    def is_enable_type(type_name: str) -> bool:
        base_types = [
            'int', 'float', 'double', 'char', 'bool', 'void', 'UINT', 'uint', 'WPARAM', 'CUpdateParam',
            'LPVOID', 'BOOL', 'LPARAM', 'CString', 'LPCTSTR'
        ]
        # 타입명에서 *, &, const 등 제거
        clean_type = type_name.replace('*', '').replace('&', '').replace('const', '').strip()
        # 정확히 일치하는 경우만 True
        return any(clean_type == tp for tp in base_types)

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
            dot = '.'
            if is_pointer_type(child_types[idx]):
                dot = '->'
            if 'CArray' in child_types[idx]:
                continue
            elif is_collection_type(child_types[idx]):
                parm_log += f'<<" {name} size : "<<{name}{dot}size()'
            elif 'CPoint' in child_types[idx]:
                parm_log += f'<<" {name} : "<<{name}{dot}x<<","<<{name}{dot}y'
            elif 'Point' in child_types[idx]:
                parm_log += f'<<" {name} : "<<{name}{dot}X<<","<<{name}{dot}Y'
            elif 'float3' in child_types[idx] and not 'vector' in child_types[idx]:
                parm_log += f'<<" {name} : "<<{name}{dot}toCString()'
            elif 'CRect' in child_types[idx]:
                parm_log += f'<<" {name} : "<<{name}{dot}left<<","<<{name}{dot}top<<","<<{name}{dot}right<<","<<{name}{dot}bottom'
            elif is_enable_type(child_types[idx]):
                parm_log += f'<<" {name} : "<<{name}'
    try:
        is_static = method_cursor.node.is_static_method() or method_cursor.kind != 'CXX_METHOD'
    except Exception as e:
        is_static = True
        print(f'{method_cursor.get_range_code()} static check error', e)
    cls_name ='<<typeid(*this).name() '
    if is_static:
        cls_name = ''

    catch_txt = f'catch (const std::exception& e) ' + '{\n'
    if cls_name + parm_log:
        catch_txt +=f'\tLOGN_(System)' + cls_name + parm_log + ';\n'
    catch_txt += f'\tLOGN_(System)<<"Exception: "<<e.what();\n'

    # type_map = method_cursor.get_visit_type_map()
    # if 'RETURN_STMT' in type_map:
    #     datas = type_map['RETURN_STMT']
    #     last_return = datas[-1].get_range_code()
    #     catch_txt += last_return
    catch_txt += "}\n}\n"


    return catch_txt




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
        



