# import pytest
from clangParser.datas.CUnit import CUnit
from clangParser.datas.Cursor import Cursor
import clangParser.clangParser as Parser
from collections import defaultdict
import time

def test_print_time():
    print()
    time_map = defaultdict(list)
    files = Parser.find_cpp_files( r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation')
    for path in files:
        st = time.time()
        unit = CUnit.parse(path)
        ed = time.time()

        time_map[ed-st].append(unit)

    for t, units in sorted(time_map.items()):
        if 1 < len(units):
            print(f'{t} : {len(units)} units.')
        else:
            unit:CUnit = units[0]
            print(f'{t:.2f}  line {len(unit.code.splitlines())} / txt : {len(unit.code)}')

def test_get_method_body():
    print(test_get_method_body)

    file_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation\UIDlgImplantLib.cpp'
    my_unit = CUnit.parse(file_path=file_path)
    node = my_unit.get_method_body(2222)
    my_cursor = Cursor(node)
    print(my_cursor.get_range_code())

    return my_cursor



def test_compare_copy_file():
    print(test_get_method_body)
    file_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation\UIDlgImplantLib.cpp'
    in_project_unit = CUnit.parse(file_path=file_path)

    source_code = in_project_unit.read_file()
    print('file line : ' , len(source_code.splitlines()))

    temp_unit = CUnit(Parser.parse_context(context=source_code, file_remove=True))

    print('is same == ', temp_unit.unit == in_project_unit.unit)

    print('\t\tIn Proj / Temp')
    print(f'child len: {len(in_project_unit.this_file_nodes)} / {len(temp_unit.this_file_nodes)}')

    def get_merge_stmt_map(unit1: CUnit, unit2: CUnit):
        stmt_map1 = Cursor(unit1.unit.cursor).get_visit_type_map()
        stmt_map2 = Cursor(unit2.unit.cursor).get_visit_type_map()

        keys = set(stmt_map1.keys()) | set(stmt_map2.keys())

        stmt_map = {}
        for key in keys:
            li1 = stmt_map1.get(key, [])
            li2 = stmt_map2.get(key, [])

            stmt_map[key] = (li1, li2)

        return stmt_map

    merge_map = get_merge_stmt_map(in_project_unit, temp_unit)
    for key, (pj_li, tp_li) in merge_map.items():
        if len(pj_li) == len(tp_li):
            print(f'{key}\t\t:  {len(pj_li)}')
        else:
            print(f'{key}\t\t:  {len(pj_li)} / {len(tp_li)}')





def print_this_file_node(my_unit):
    print(len(my_unit.this_file_nodes))

    node = Cursor(my_unit.this_file_nodes[0])
    print(node.location.line, ' ' ,node.get_range_code())


def test_parse_temp_file():
    print(test_parse_temp_file)


    file_path = r'D:\temp\UIDlgImplantLib.cpp'
    my_unit = CUnit.parse(file_path=file_path)

    # print_this_file_node(my_unit)

    unit_cursor = Cursor(my_unit.unit.cursor)
    stmt_map = unit_cursor.get_visit_type_map()
    # print(stmt_map)
    for key, datas in stmt_map.items():
        print(f'{key} : {len(datas)}')


    # print(f'child len: {len(in_project_unit.this_file_nodes)} / {len(temp_unit.this_file_nodes)}')
import difflib
from typing import List

def find_most_similar(str_list: List[str], data: str) -> str:
    # get_close_matches는 리스트에서 가장 유사한 문자열을 찾습니다.
    # n=1은 가장 유사한 하나의 결과만 반환하도록 설정
    # cutoff=0은 모든 유사도 수준을 허용
    matches = difflib.get_close_matches(data, str_list, n=1, cutoff=0)
    if matches:
        return matches[0]
    else:
        return None  # 유사한 문자열이 없는 경우
def test_dec_similar():
    print(test_dec_similar)


    file_path = r'D:\dev\AutoPlanning\Bum\Merge\mod_APImplantSimulation\ActuatorHybridFixture.cpp'
    my_unit = CUnit.parse(file_path=file_path)
    dec_list = list(my_unit.preprocessor_line_map.values())
    dec = '#include "../DataAccessor/DAutoGenTester.h"'
    print(find_most_similar(dec_list, dec))

def test_src_pair():
    path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\AppUICore\ActuatorImage.cpp'
    cpp_unit = CUnit.parse(path)
    head_unit = CUnit.parse(path.replace('.cpp', '.h'))

    src_pair = CUnit.get_src_pair_map(cpp_unit, head_unit)
    for src, (cpp, h) in sorted(src_pair.items()):
        if cpp:
            cpp = cpp.kind
        else:
            cpp = None
        if h:
            h = h.kind
        else:
            h= None

        # cpp = bool(cpp)
        # h = bool(h)

        print(f'{src} : {cpp}, {h}')