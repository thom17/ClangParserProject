# import pytest
from clangParser.CUnit import CUnit
from clangParser.Cursor import Cursor
import clangParser.clangParser as Parser

def test_get_visit_line_call_map():
    print(test_get_visit_line_call_map)

    file_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation\UIDlgImplantLib.cpp'
    my_unit = CUnit.parse(file_path=file_path)
    node = my_unit.get_method_body(2222)
    my_cursor = Cursor(node)
    line_call = my_cursor.get_line_call_trace()

    for code, src_set in line_call:
        if src_set:
            print(code, '\t', src_set)
        else:
            print(code)

    return my_cursor
