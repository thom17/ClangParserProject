# import pytest
from clangParser.CUnit import CUnit
from clangParser.Cursor import Cursor
import clangParser.clangParser as Parser

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