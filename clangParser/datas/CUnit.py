import os.path

from clang.cindex import Cursor as clangCursor
from clang.cindex import TranslationUnit

from typing import List, Dict, Tuple, Optional

import chardet

# if __name__ == "__main__":
#     from Cursor import Cursor
#     from clangParser import parsing, parse_project
# else:
#     from .Cursor import Cursor
#     from .clangParser import parsing, parse_project

from clangParser.datas.Cursor import Cursor
from clangParser.clangParser import parsing, parse_project

class CUnit:
    """
    3
    노드 필터링을 위한 TranslationUnit 정의
    일단 완성된 cpp 파일을 파싱하는걸 기준으로?

    this_file_nodes : 해당 AST의 같은 파일내 자식들 (#include, #ifdef와 같은 매크로 및 정의는 재외되는듯)
    """

    def __init__(self, unit: Optional[TranslationUnit] = None):
        self.unit: Optional[TranslationUnit] = unit
        self.this_file_nodes: List[clangCursor] = []
        self.preprocessor_line_map: Dict[int, str] = {}

        self.file_path: str = ""
        self.file_name: str = ""
        self.file_extension: str = ""
        self.code: str = ""

        if self.unit:
            self.file_path: str = unit.spelling
            self.file_name, self.file_extension = os.path.splitext(self.file_path)
            self.code: str = self.read_file()

            #전처리관련 코드를 포함할 경우 매우 복잡해진다.
            cursor: clangCursor = unit.cursor
            for child_node in cursor.get_children():
                if child_node.location.file.name == self.file_path:
                    self.this_file_nodes.append(child_node)
                    #self.this_file_nodes.append(Cursor.Cursor(child_node, self.file_path))

            #전처리 관련 코드는 여기서 별도로 관리
            line_codes = self.code.splitlines()
            for idx, line in enumerate(line_codes):
                if line.lstrip().startswith('#'):
                    self.preprocessor_line_map[idx+1] = line

    # def get_method_body_in_range(self, start_line, end_line):
    #     '''
    #     2025-01-06
    #     모든 자식 노드를 순회하여 내장 함수 (window kit) 호출됨
    #     일단은 사용 x. this_node 내에서 검색하도록 변경해야함
    #     '''
    #     node = self.unit.cursor
    #     target_range = []
    #     for child in node.walk_preorder():
    #         if (child.location.line >= start_line and child.location.line <= end_line):
    #             target_range.append(child)
    #     # target_range에 포함된 노드를 기반으로 필요한 처리 수행.
    #     return target_range

    @staticmethod
    def parse(file_path)-> 'CUnit':
        compliationunit = parsing(file_path)
        return CUnit(compliationunit)

    @staticmethod
    def parse_project(file_path)-> 'CUnit':
        my_units = []
        for tunit in parse_project(file_path):
            my_units.append(CUnit(tunit))
        return my_units

    @staticmethod
    def get_src_pair_map(unit1: 'CUnit', unit2:'CUnit') -> Dict[str, Tuple[Optional[Cursor], Optional[Cursor]]]:
        first = unit1.get_this_Cursor()
        second = unit2.get_this_Cursor()

        src_pair_map :Dict[str, Tuple[Optional[Cursor], Optional[Cursor]]]= {}
        for c1 in first:
            src_pair_map[c1.get_src_name()] = (c1, None)
        for c2 in second:
            src = c2.get_src_name()
            c1 = src_pair_map.get(src, None)
            if c1:
                c1 = c1[0]
            src_pair_map[src] = (c1, c2)

        return src_pair_map

    def __str__(self):
        return f"Unit : {self.file_path} : {self.this_file_nodes.__len__()}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.file_path == other.file_path

    def __hash__(self):
        return hash(self.file_path)

    def to_dict(self):
        return {
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_extension": self.file_extension,
            "code": self.code,
        }



    def get_this_Cursor(self) -> list[Cursor]:
        '''
        사실상 h 파일을 위해 추가로 작성한 메서드
        실질적인 this_file_nodes를 Cursor로 생성하여 반환함
        '''
        if self.file_path.endswith('.h'):
            head_dec_cursor = [Cursor(node, self.code) for node in self.this_file_nodes]
            in_dec_cursor = []
            for cursor in head_dec_cursor:
                in_dec_cursor = in_dec_cursor + [Cursor(ch, self.code) for ch in cursor.node.get_children()]
            return  head_dec_cursor + in_dec_cursor

        if self.file_path.endswith('.cpp'):
            return [Cursor(node, self.code) for node in self.this_file_nodes]







    def read_file(self):
        with open(self.file_path, 'rb') as file:
            raw_data = file.read()
        file_encode = chardet.detect(raw_data)['encoding']

        # 파일 읽기
        with open(self.file_path, 'r', encoding=file_encode) as file:
            return file.read()

    def get_in_range_node(self, line_num: int) -> clangCursor:
        assert(isinstance(line_num, int))

        for node in self.this_file_nodes:
            node:clangCursor = node

            st_line = node.extent.start.line
            ed_line = node.extent.end.line

            if st_line <= line_num <= ed_line:
                return node

    def get_method_body(self, line_num: int) -> clangCursor:
        assert(isinstance(line_num, int))

        for node in self.this_file_nodes:
            node:clangCursor = node

            st_line = node.extent.start.line
            ed_line = node.extent.end.line

            if st_line <= line_num <= ed_line:
                return node





if __name__ == "__main__":
    import time
    from simpleVisitor import SimpleVisitor as visitor
    # line_info = r"D:\dev\AutoPlanning\trunk\AP-6979-TimeTask\mod_APScanEdit/CommandToothRemove.cpp:14"
    # file_path = line_info.split(":")[0]
    # line_num = line_info.split(":")[1]
    #
    # print(file_path)
    # print(line_num)

    start_time = time.time()
    myunit = CUnit.parse(r"D:\dev\AutoPlanning\trunk\AP-6979-TimeTask\mod_APImplantSimulation/ActuatorHybridFixture.cpp")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Make Unit time :", elapsed_time, "seconds")
    print(myunit)

    method_dec_node = myunit.get_method_body(line_num=321)
    target_my_cursor: Cursor = Cursor(method_dec_node)

    with open("../target_code.cpp", "w", encoding="euc-kr") as file:
        file.write(target_my_cursor.get_range_code())

    #라인맵 순환
    line_map = target_my_cursor.get_visit_line_map()
    file_map: {str, list} = {}
    for line in line_map:
        node_list:[Cursor] = line_map[line]
        for node in node_list:
            print(f"{line} {node.kind} {node.spelling} ")
            file_name = node.location.file.name if node.location.file else "None"
            if file_name not in file_map:
                file_map[file_name] = []
            file_map[file_name].append(node)

    #파일맵 순환
    for path in file_map:
        print(f"{path} : {file_map[path].__len__()}")

    for node in file_map["None"]:
        print(f"{node.kind} {node.spelling}")



    #유닛(원본) 확인 (하나만 나온다)
    visit_map = target_my_cursor.get_visit_unit_map()
    for unit in visit_map:
        print(f"{unit.spelling} : {visit_map[unit].__len__()}")


    defi: clangCursor = target_my_cursor.node.get_definition()
    print(defi.displayname)

    if defi == target_my_cursor.node:
        print("Same")

    vs = visitor(target_my_cursor.node, r"D:\dev\AutoPlanning\trunk\AP-6979-TimeTask\mod_APImplantSimulation/ActuatorHybridFixture.cpp")
    cmd_code = vs.make_comment_code()

    with open("../comment_code.cpp", "w") as file:
        file.write(cmd_code)

