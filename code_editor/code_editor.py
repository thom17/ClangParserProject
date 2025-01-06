from dataclasses import dataclass
from clangParser.CUnit import CUnit, Cursor

from typing import Union, Dict


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


class CodeEditor:
    '''https://github.com/thom17/ClangParserProject/issues/12
    위의 이슈에 따라 아래 규칙을 따르자.
    1. 이 클래스는 cpp, h 한 쌍을 관리한다.(주로 cpp)
    2. 수정 코드를 구하는 것은 이 클래스의 역활이 아니며 이는 최종 파일을 관리하는 클래스다.
    3. 따라서 타겟 노드 (주로 STMT)와 대체 코드 (str) 을 맵핑해서 받아 관리한다.
    4. 필요시 매핑된 데이터를 활용해서 최종 파일을 출력하거나 생산한다.
    '''

    def __init__(self, path_or_unit: Union[CUnit, str]):
        self.__work_cpp: str = ''
        self.__work_h: str = ''
        self.__edit_option: EditOption = EditOption()

        self.__replace_code_map: Dict[Cursor, str] = {}
        self.__planned_methods: Dict[str, MethodArg] = {}

        if isinstance(path_or_unit, str):
            self.cpp_path = path_or_unit.replace('.h', '.cpp')
            self.h_path = path_or_unit.replace('.cpp', '.h')


        elif isinstance(path_or_unit, CUnit):
            self.cpp_path = path_or_unit.path.replace('.h', '.cpp')
            self.h_path = path_or_unit.path.replace('.cpp', '.h')

        self.cpp_unit: CUnit = CUnit.parse(self.cpp_path)
        self.h_unit: CUnit = CUnit.parse(self.h_path)

    def add_new_method(self, method_arg: MethodArg):
        self.__planned_methods[method_arg.get_src()] = method_arg
        # body = make_def_body(method_arg=method_arg)
        # self.work_cpp += self.edit_option.add_method_before + body

    def add_replace_node(self, node: Cursor, replace_code: str):
        self.__replace_code_map[node] = replace_code

    def generate_replace_cpp(self, code: str = None) -> str:
        if code == None:
            code = self.cpp_unit.code
        self.__work_cpp = code

        for node, new_code in self.__replace_code_map.items():
            old_code = node.get_range_code()
            self.__work_cpp = self.__work_cpp.replace(old_code, new_code)

        for method_arg in self.__planned_methods.values():
            new_code = make_def_body(method_arg=method_arg, open_brace_style=self.__edit_option.open_brace_style)
            self.__work_cpp += self.__edit_option.add_method_before + new_code
        return self.__work_cpp



