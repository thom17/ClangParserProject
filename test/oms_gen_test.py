"""
프로젝트 파싱
OMS 생성
자바 파서와 동일한 순서?
일단 차근차근 해보고 클래스화 하던지 하자
"""

import sys
sys.path.append('/')

from clangParser.clangParser import parse_project
from clangParser.datas.CUnit import CUnit
from clangParser.datas.Cursor import Cursor
from clangParser.datas.CursorOMS import CursorOMS

from clang.cindex import Cursor as clangCursor

target_project = ""

oms_map:[str, [clangCursor] ] ={}

def get_oms_cursor(src_name: str):
    return CursorOMS.GetCursorOMS(oms_map[src_name])

def update_def_oms(src_name: str, node: clangCursor):
    # assert src_name not in oms_map, "충돌"

    if src_name not in oms_map:
        oms_map[src_name]: [clangCursor] = []
    oms_map[src_name].append(node)

def parsing():
    """
    MyUnit객체들을 생성
    :return:
    """
    units = parse_project(directory=r"D:\dev\AutoPlanning\trunk\AP-6979-TimeTask\AppCommon_AP")
    unit_map: [str, ] ={}
    for trans_unit in units:
        unit = CUnit(trans_unit)

        if unit.file_extension == ".h":
            head_parsing(unit)
        else:
            cpp_parsing(unit)

def head_parsing(unit: CUnit):
    for node in unit.this_file_nodes:
        if list(node.get_children()).__len__():
            update_def_oms(Cursor(node).get_src_name(), node)
        else:
            continue
def cpp_parsing(unit: CUnit):
    for node in unit.this_file_nodes:
        update_def_oms(Cursor(node).get_src_name(), node)

if __name__ == "__main__":
    parsing()