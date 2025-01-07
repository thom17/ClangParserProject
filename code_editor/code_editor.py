from dataclasses import dataclass
from clangParser.CUnit import CUnit, Cursor

from typing import Union, Dict, List, Optional
import chardet


@dataclass
class MethodArg:
    return_type: str
    sig_name: str
    pure_block: str
    class_name: str

    def get_src(self) -> str:
        return self.class_name + '.' + self.sig_name


@dataclass
class EditOption:
    open_brace_style: str = '\n'
    add_method_before: str = '\n'


def insert_code_in_block_start(block: Cursor, insert_code: str) -> str:
    '''
    compount_stmt {} 노드를 입력받아 맨앞에 code 삽입.
    compount_stmt는 광범위하게 사용되서 유용할듯
    '''

    assert block.kind == 'COMPOUND_STMT', f'{block.kind}'

    code = block.get_range_code()
    tab = '\t'
    # first_child = next(block.node.get_children(), None) #탭은 나중에 정상동작을 안한다.
    # if first_child:
    #     first_child = Cursor(first_child)
    #     first_pure_code = first_child.get_range_code()
    #     tab = first_child.get_range_line_code().replace(first_pure_code, '')
    return '{\n' + tab + insert_code + code[1:]


def insert_code_in_block_end(block: Cursor, insert_code: str) -> str:
    '''
    compount_stmt {} 노드를 입력받아 맨앞에 code 삽입.
    compount_stmt는 광범위하게 사용되서 유용할듯
    '''

    assert block.kind == 'COMPOUND_STMT', f'{block.kind}'

    code = block.get_range_code()
    tab = '\t'
    # first_child = next(block.node.get_children(), None) #탭은 나중에 정상동작을 안한다.
    # if first_child:
    #     first_child = Cursor(first_child)
    #     first_pure_code = first_child.get_range_code()
    #     tab = first_child.get_range_line_code().replace(first_pure_code, '')
    return code[:-1] + tab + insert_code + '\n}'


def make_def_body(method_arg: MethodArg, open_brace_style='\n') -> str:
    front = method_arg.return_type + ' '
    if method_arg.class_name:
        return front + method_arg.class_name + "::" + method_arg.sig_name + open_brace_style + method_arg.pure_block
    else:
        return front + method_arg.sig_name + open_brace_style + method_arg.pure_block

import difflib
from typing import List

def make_added_include(unit:CUnit, include_code: str)->str:
    def find_most_similar(str_list: List[str], data: str) -> str:
        # get_close_matches는 리스트에서 가장 유사한 문자열을 찾습니다.
        # n=1은 가장 유사한 하나의 결과만 반환하도록 설정
        # cutoff=0은 모든 유사도 수준을 허용
        matches = difflib.get_close_matches(data, str_list, n=1, cutoff=0)
        if matches:
            return matches[0]
        else:
            return None  # 유사한 문자열이 없는 경우


    dec_map:dict = {}
    last_pos_line = 1
    #그냥 unit 측에서 include, define은 따로 저장해야겠다. (#에서도 분류를 해야할듯)
    for line_num, code in sorted(unit.preprocessor_line_map.items()):
        if include_code in code:
            return unit.code #정의 된 경우 변화 x
        elif '#include ' in code:
            dec_map[code] = line_num

            #마지막 include 라인 갱신
            if last_pos_line < line_num:
                last_pos_line = line_num

    sim_text = find_most_similar(list(dec_map.keys()), include_code)

    #유사한 택스트나 마지막 위치로 인덱스 저장
    if sim_text:
        change_index = dec_map[sim_text] - 1
    else:
        change_index = last_pos_line - 1

    code_lines = unit.code.splitlines()
    code_lines[change_index] = code_lines[change_index] + '\n' + include_code
    return '\n'.join(code_lines)





class CodeEditor:
    '''https://github.com/thom17/ClangParserProject/issues/12
    위의 이슈에 따라 아래 규칙을 따르자.
    1. 이 클래스는 cpp, h 한 쌍을 관리한다.(주로 cpp)
    2. 수정 코드를 구하는 것은 이 클래스의 역활이 아니며 이는 최종 파일을 관리하는 클래스다.
    3. 따라서 타겟 노드 (주로 STMT)와 대체 코드 (str) 을 맵핑해서 받아 관리한다.
    4. 필요시 매핑된 데이터를 활용해서 최종 파일을 출력하거나 생산한다.

    하나의 파일만 관리하는게 나을수도?
    '''

    def __init__(self, path_or_unit: Union[CUnit, str]):
        self.__work_code: str = ''
        self.__edit_option: EditOption = EditOption()
        self.__file_path: str = ''
        self.file_unit: CUnit = None

        self.__replace_code_map: Dict[Cursor, str] = {}
        self.__planned_methods: Dict[str, MethodArg] = {}
        self.__planned_define: List[str] = []

        if isinstance(path_or_unit, str):
            self.__file_path = path_or_unit

        elif isinstance(path_or_unit, CUnit):
            self.file_unit: CUnit = path_or_unit
            self.__file_path = path_or_unit.file_path

    def add_new_method(self, method_arg: MethodArg):
        self.__planned_methods[method_arg.get_src()] = method_arg
        # body = make_def_body(method_arg=method_arg)
        # self.work_cpp += self.edit_option.add_method_before + body

    def add_replace_node(self, node: Cursor, replace_code: str):
        self.__replace_code_map[node] = replace_code

    def generate_replace_cpp(self, code: str = None) -> str:
        if code == None:
            code = self.file_unit.code

        if self.__planned_define:
            assert len(self.__planned_define) < 2, 'to do : 다중 include 처리 동작 안함.'
            assert '#include' in self.__planned_define[0], f'to do include 구문만 처리 가능. ({ self.__planned_define[0]})'
            code = make_added_include(self.file_unit,  self.__planned_define[0])

        self.__work_code = code

        for node, new_code in self.__replace_code_map.items():
            old_code = node.get_range_code()
            self.__work_code = self.__work_code.replace(old_code, new_code)

        for method_arg in self.__planned_methods.values():
            new_code = make_def_body(method_arg=method_arg, open_brace_style=self.__edit_option.open_brace_style)
            self.__work_code += self.__edit_option.add_method_before + new_code

        return self.__work_code


    def add_define(self, insert):
        if insert in self.__planned_define:
            return
        else:
            self.__planned_define.append(insert)

    def write_file(self, path: Optional[str] = None):
        if path is None:
            path = self.__file_path
        replace_code = self.generate_replace_cpp()
        with open(path, 'rb') as file:
            raw_data = file.read()
        file_encode = chardet.detect(raw_data)['encoding']

        with open(path, 'w', encoding=file_encode) as f:
            f.write(replace_code)