'''
nullptr 관련 매크로 처리
'''
from typing import Optional
from clangParser.datas.CUnit import CUnit, Cursor
import clang.cindex
from code_editor.code_editor import CodeEditor
from dataclasses import dataclass, field
@dataclass
class EditMethod:
    '''
    수정중인 메서드 상태를 관리
    '''
    method_cursor: Cursor
    replace_line_map: dict[int, str]

    @classmethod
    def from_cursor(cls, method_cursor: Cursor) -> 'EditMethod':
        """
        Cursor로부터 EditMethod 객체를 생성합니다.
        """
        code = method_cursor.get_range_code()
        lines_code = code.splitlines()
        replace_line_map = {}
        line = method_cursor.location.line

        for idx, line_code in enumerate(lines_code):
            replace_line_map[line + idx] = line_code

        return cls(method_cursor=method_cursor, replace_line_map=replace_line_map)

    def insert_front(self, line: int, code: str) -> None:
        """
        지정된 줄 앞에 코드를 삽입합니다.
        """
        if line in self.replace_line_map:
            self.replace_line_map[line] = code + self.replace_line_map[line]
        else:
            self.replace_line_map[line] = code
    def insert_back(self, line: int, code: str) -> None:
        """
        지정된 줄 뒤에 코드를 삽입합니다.
        """
        if line in self.replace_line_map:
            self.replace_line_map[line] += '\n' + code
        else:
            self.replace_line_map[line] = code


    def get_replaced_code(self) -> str:
        """
        수정된 코드를 반환합니다.
        """
        lines = []
        for line_num in sorted(self.replace_line_map.keys()):
            lines.append(self.replace_line_map[line_num])
        return '\n'.join(lines)


def get_unsafe_var_decs(method_cursor: Cursor):
    '''
    1. 포인터 변수 선언을 찾습니다.
    '''
    pointer_vars = []
    type_map = method_cursor.get_visit_type_map()
    dec_list = type_map.get('VAR_DECL', [])

    #먼저 변수 선언문 서치
    for dec_cursor in dec_list:
        # print(dec_cursor.get_range_code())
        var_line_code = dec_cursor.get_range_line_code()
        use_new = ' new ' in var_line_code or '=new ' in var_line_code
        if use_new:
            # new로 선언된 포인터 변수는 nullptr 체크가 필요하지 않음
            continue

        #포인터 타입의 변수 선언
        elif dec_cursor.node.type.kind == clang.cindex.TypeKind.POINTER:
            pointer_vars.append(dec_cursor)

        #auto 타입의 변수 선언
        elif dec_cursor.node.type.kind == clang.cindex.TypeKind.AUTO:
            point_cast = dec_cursor.spelling+'->'
            #auto 타입은 전체 메서드로 포인터 사용을 서치
            if point_cast in method_cursor.get_range_code():
                pointer_vars.append(dec_cursor)


    return pointer_vars

def get_use_first(method_cursor: Cursor, var_dec:Cursor) -> Optional[Cursor]:
    """
    2. 변수가 처음 사용되는 위치를 찾습니다.
    """
    call_def_map = method_cursor.get_call_definition_map()
    code_lines = method_cursor.get_range_code().splitlines()

    for call_node, def_node in call_def_map.items():
        line_index = call_node.location.line - method_cursor.location.line
        if line_index < 0:
            #비정상적인 clang.index 인식됨
            continue
        strip_line_code = code_lines[line_index].strip().replace(' ', '')
        #초기화 여부 판단
        if strip_line_code.startswith(f'{var_dec.spelling}='):
            continue


        if def_node == var_dec.node and call_node.location.line != var_dec.location.line:
            # print('Found use of variable declaration at:', call_cursor.get_range_line_code())
            return Cursor.CINDEX_2_CURSOR_MAP[call_node]
    # print('None Found')
    return None
def get_this_start_cursor(cursor: Cursor) -> Optional[Cursor]:
    """
    3. 코드 삽입을 위한 커서 위치를 찾는다. (아래와 같은 이슈때문에)
    if (bAdd) \n pData->Use();
    """
    #클랭은 완전하게 파싱이 불가
    # lex_parent = cursor.node.lexical_parent
    # semantic_parent = cursor.node.semantic_parent

    # lex_cursor = Cursor.CINDEX_2_CURSOR_MAP.get(lex_parent, None) #[lex_parent]
    # semantic_cursor = Cursor.CINDEX_2_CURSOR_MAP.get(semantic_parent, None) # [semantic_parent]
    # print(f'lex_cursor: {lex_cursor}, semantic_cursor: {semantic_cursor}')
    # if lex_cursor:
    #     print(f'lexcursor({lex_cursor.kind}): {lex_cursor.get_range_code()}')
    # if semantic_cursor:
    #     print(f'semantic_cursor({semantic_cursor.kind}): {semantic_cursor.get_range_code()}')


    pos = cursor
    assert pos.parent_cursor, f'parent_cursor is None for {pos.kind} : {pos.get_range_code()}'
    parent_kind = pos.parent_cursor.kind
    is_end = 'BLOCK_STMT' == parent_kind or 'COMPOUND_STMT' == parent_kind

    # print(f'start : {cursor.kind} : {cursor.get_range_code()}')

    while not is_end:
        pos = pos.parent_cursor
        # print(f'{pos.kind}{pos.get_range()}:{pos.get_range_line_code()}')
        parent_kind = pos.parent_cursor.kind
        is_end = 'BLOCK_STMT' == parent_kind or 'COMPOUND_STMT' == parent_kind



    # print(f'find{pos.get_range()}{pos.kind} : {pos.get_range_code()}')

    # print('==' *  20)

    return pos


def is_null_check(call_node: Cursor, dec_cursor: Cursor) -> bool:
    """
    3. nullptr 체크를 위한 함수
    """
    name = dec_cursor.spelling
    line_code = call_node.get_range_line_code() #코드 한줄만

    #UNEXPOSED_EXPR 또한 조건식으로 인식된다. 따라서 Kind 사용 없이 그냥 문자열 비교 사용
    strip_code = line_code.strip().replace(' ', '')
    is_if = strip_code.startswith('if(') or strip_code.startswith('elseif(')
    # 조건식이 아니면 무조건 사용하는 라인
    if not is_if:
        return False
    # nullptr 체크를 위한 조건식이 아닌 경우
    elif name + '->' in line_code or '*' + name in line_code:
        return False
    else:
        return True

def insert_null_check(edit_method: EditMethod, call_cursor: Cursor, dec_cursor: Cursor) -> None:
    """
    4. nullptr 체크를 위한 코드 삽입
    """
    to_insert_cursor = get_this_start_cursor(call_cursor)  # 삽입 하기 위한 부모 커서 찾기 (여러줄의 문장 고려)

    name = dec_cursor.spelling
    insert_code = f'if({name}==nullptr) LOGE_(System) << "{name} is nullptr (macro check)";\n'
    
    is_use_cast = f'{name}->' in call_cursor.get_range_code()
    
    def is_to_insert_back(dec_cursor: Cursor) -> bool:
        """
        삽입 위치가 블록의 시작인지 확인합니다.
        """

        full_dec_code= get_this_start_cursor(dec_cursor).get_range_code()
        strip_code = full_dec_code.strip().replace(' ', '')
        import re
        init_pattern = r'.*' + re.escape(name) + r'=.*'
        if re.search(init_pattern, strip_code):
            # 초기화가 의미 업으면 뒤에 삽입
            return '=nullptr' in strip_code or '=NULL' in strip_code


        else:
            return True

        # if to_insert_cursor.kind == 'CALL_EXPR':
        #     strip_code = to_insert_cursor.get_range_code().strip().replace(' ', '')
        #     # get.*info($name) 형태라면 nullptr 체크가 이미 있는 것으로 간주
        #     import re
        #     pattern = r'.*get\w*info\((\w*,)?' + re.escape(name) + r'(,\w*)?\)'
        #     if re.search(pattern, strip_code, re.IGNORECASE):
        #         return True
        # #그 외는 모두 False
        # return False

    #호출 식에 -> 연산자가 없으면서 뒤에 배치할 필요가 있다면
    if not is_use_cast and is_to_insert_back(dec_cursor):
        replace_line = to_insert_cursor.extent.end.line
        edit_method.insert_back(replace_line, insert_code)
    else:
        replace_line = to_insert_cursor.extent.start.line
        edit_method.insert_front(replace_line, insert_code)


def get_replaced_method(method_cursor: Cursor) -> str:
    """
    5. 수정된 메서드를 반환합니다.
    """

    edit_method = EditMethod.from_cursor(method_cursor)
    for dec_cursor in get_unsafe_var_decs(method_cursor):
        if dec_cursor.spelling == 'it' or dec_cursor.spelling == 'iter': #iterator 변수는 nullptr 체크를 하지 않음
            continue

        first_call_cursor = get_use_first(method_cursor, dec_cursor)

        # 호출하지 않는 경우도 있음
        if first_call_cursor:
            # nullptr 체크가 없는 경우
            if not is_null_check(first_call_cursor, dec_cursor):
                insert_null_check(edit_method, first_call_cursor, dec_cursor)

    # 메서드 전체단위로 replace
    replace_method_code = edit_method.get_replaced_code()
    return replace_method_code

def replace_file(unit: CUnit):
    """
    1~4 파일단위 (모든 메서드에 적용)
    """
    code_editor = CodeEditor(unit)
    code_editor.add_define('#include "../BaseTools/plogger.h"')

    #메서드별 수행
    for method_cursor in unit.get_this_Cursor():
        replace_method_code = get_replaced_method(method_cursor)
        code_editor.add_replace_node(method_cursor, replace_method_code)

    #모든 메서드 처리후 파일에 적용
    code_editor.write_file()

def replace_project(project_path: str):
    """
    프로젝트 전체 파일에 대해 nullptr 체크를 추가합니다.
    """
    file_edit_map = {}

    from clangParser.clangParser import find_cpp_files
    file_paths = list(find_cpp_files(project_path, add_h=False))
    import os

    for progress, file_path in enumerate(file_paths):
        print(f'\r({progress} / {len(file_paths)}) ', end=file_path + '\t\t')
        if os.path.isfile(file_path.replace('.cpp', '.h')):  # 짝이 있는 파일만 파싱
            unit = CUnit.parse(file_path)
            replace_file(unit)
    print(f'\nnullptr 매크로가 완료되었습니다.\n {project_path}')

import tkinter as tk
from tkinter import filedialog
import sys


def main():
    if len(sys.argv) == 1:
        root = tk.Tk()
        root.withdraw()
        pathinfo = filedialog.askdirectory(title="폴더를 선택하세요")
        replace_project(project_path=pathinfo)

if __name__ == '__main__':

    def simple_test():
        path = r'D:\dev\AutoPlanning\trunk\Ap-Trunk-auto-task\AppUICore\ActuatorHybrid.cpp'
        unit = CUnit.parse(path)
        method_cursor: Cursor = None
        for cursor in unit.get_this_Cursor():
            # print(cursor.get_src_name())
            if 'ActuatorHybrid._crownCrossSectionView' in cursor.get_src_name():
                method_cursor = cursor
                break
        if method_cursor:
            r = get_replaced_method(method_cursor)
            print(r)
        replace_file(unit)


    main()
    # simple_test()

    # import re
    # name = 'name'
    # pattern = r'.*get\w*info\((\w*,)?' + name + r'(,\w*)?\);'
    # init_pattern = r'.*' + re.escape(name) + r'=.*'
    # pattern = init_pattern
    # strip_code ='auto name =_pToolbarBase->GetToothDoc();'.strip().replace(' ', '')
    # if re.search(pattern, strip_code, re.IGNORECASE):
    #     print(strip_code)
    #
    # strip_code ='auto * name;'.strip()
    # if re.search(pattern, strip_code, re.IGNORECASE):
    #     print(strip_code)
    #
    #
    #
    #
