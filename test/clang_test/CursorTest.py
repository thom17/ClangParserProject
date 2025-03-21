from clangParser.datas.CUnit import CUnit
from clangParser.datas.Cursor import Cursor

from clangParser.datas.ClangRange import ClangRange, RangeRelation

import time

def test_unit_cursor_gen_time():
    '''
    Cursor 에서 child_list를 추가함( 기본적으로 visit이 항상 수행)
    이로 인한 메서드별 시간 측정.
    '''
    file_path = r'D:\dev\EcoCad\trunk\pure\mod_SCWorkspace\UIDlgWorklistMain.cpp'
    my_unit = CUnit.parse(file_path=file_path)
    cursor_list: list[Cursor] = []
    for node in my_unit.this_file_nodes:
        st_time = time.time()
        my_cursor = Cursor(node, my_unit.code)
        ed_time = time.time()
        print(f'{my_cursor.get_src_name()} {my_cursor.get_line_size()} (size) : {ed_time - st_time} sec')
        cursor_list.append(my_cursor)
    return cursor_list
def test_visitor():
    cursor_list = test_unit_cursor_gen_time()
    for cursor in cursor_list:
        visitor = cursor.cursor_visitor
        visitor.get_stmt_list()
        visitor.get_stmt_map()
        visitor.get_visit_type_map()

        visitor.get_visit_line_size_map()
        visitor.get_visit_line_map()

        visitor.get_visit_def_map()

        visitor.get_visit_unit_map()

        visitor.visit_nodes()


def test_get_visit_line_call_map():
    print(test_get_visit_line_call_map)

    file_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation\CUIDlgWorklistMain.cpp'
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


def get_chageSystem() -> Cursor:
    file_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation\UIDlgImplantLib.cpp'
    my_unit = CUnit.parse(file_path=file_path)
    node = my_unit.get_method_body(2222)
    my_cursor = Cursor(node)
    return my_cursor

def test_range():
    print(test_range)

    file_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation\UIDlgImplantLib.cpp'
    my_unit = CUnit.parse(file_path=file_path)
    node = my_unit.get_method_body(2222)
    my_cursor = Cursor(node)

    print(my_cursor.get_range_code())

    def_extent = my_cursor.extent
    ch_list = [Cursor(ch) for ch in my_cursor.node.get_children()]
    body_stmt = ch_list[2]
    body_extent = body_stmt.extent

    print(def_extent)
    print(body_extent)


    # print(def_extent < body_extent)


def get_visit_all_nodes(cursor: Cursor):
    all_datas = []
    for datas in cursor.get_visit_type_map().values():
        all_datas += datas
    return all_datas

from collections import defaultdict
import itertools

def test_visit_file_map():
    node = get_chageSystem()
    all_nodes = get_visit_all_nodes(node)
    path_map = defaultdict(list)
    for node in all_nodes:
        node: Cursor
        path_map[f'{node.location.file}, {node.extent.start.file}, {node.extent.end.file}'].append(node)

    for key, li in path_map.items():
        print(key, " : ",len(li))

def test_enum():
    a_in_b = RangeRelation.A_CONTAINED_IN_B
    if a_in_b != a_in_b.get_swap():
        print('else A_CONTAINED_IN_B')
        print(a_in_b, a_in_b.get_swap())
        a_in_b= a_in_b.get_swap()

        print(a_in_b, a_in_b.get_swap())


    a_same_b = RangeRelation.IDENTICAL
    if a_same_b != a_same_b.get_swap():
        print('else IDENTICAL')

    node = get_chageSystem()
    map = visit_make_range_map(node)
    print(len(map))

def test_range_map():
    node = get_chageSystem()
    map = visit_make_range_map(node)
    print(len(map))


def test_enable_parse_std():
    '''
    for (auto pair : _bvhDataMap) std::map<CString, ST_CONFLICT_DATASET>
    위와 같은 구문을 분석이 되는지 체크. -> 해당파일에 include를 선언 해주어도 파싱 x
    '''
    #
    conflict_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\AppCommon_AP\ExtractorConflict.cpp'
    my_unit = CUnit.parse(file_path=conflict_path)
    extractorConflict = Cursor(my_unit.get_method_body(543))
    block = extractorConflict.get_children()[2]
    print()
    print(block.get_range_code())
    for ch in block.get_children():
        print(ch)
    assert len(block.get_children()) == 4, 'for 분석 안됨'

def test_enable_parse_for_size():
    '''
    for (int i = 0; i < vStr.size() - 1; i++)
    위와 같은 구문은 분석 가능. vStr.size()는 UnExposed 일수도 있으나
    '''
    conflict_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\AppCommon_AP\ExtractorConflict.cpp'
    my_unit = CUnit.parse(file_path=conflict_path)
    GetHitNames = Cursor(my_unit.get_method_body(484))
    block = GetHitNames.get_children()[3]
    block = block.get_children()[5].child_list[1]
    print()
    print(block.get_range_code())
    for ch in block.get_children():
        print(ch)
    assert len(block.get_children()) == 2, 'for 분석 안됨'

def test_enable_parse_for_tooth():
    '''
for (auto i : listTooth)
    위와 같은 구문은 분석 가능. vStr.size()는 UnExposed 일수도 있으나
    '''
    conflict_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\AppCommon_AP\ToolbarModuleBase.cpp'
    my_unit = CUnit.parse(file_path=conflict_path)
    GetVisibleCrown = Cursor(my_unit.get_method_body(969))
    block = GetVisibleCrown.get_children()[1]
    print(block.get_range_code())
    for ch in block.get_children():
        print(ch)
    assert len(block.get_children()) == 2, 'for 분석 안됨'


def test_enable_parse():
    temp_path = (r'D:\temp\target\data\test_cpp.cpp')
    my_unit = CUnit.parse(file_path=temp_path)
    main = Cursor(my_unit.get_method_body(4))
    block = main.get_children()[0]
    print()
    print(block.get_range_code())
    for ch in block.get_children():
        print(ch)
    # assert len(block.get_children()) == 4, 'for 분석 안됨'

    print('-=-' * 10)
    for ch in block.get_children()[2].get_children():
        print(ch)


def visit_make_range_map(cursor: Cursor):
    node_map = defaultdict(lambda: defaultdict(list))
    node_li = get_visit_all_nodes(cursor)
    node_comb = list(itertools.combinations(node_li, 2))
    print("comb " , len(node_comb))
    for n1, n2 in node_comb:
        rel = RangeRelation.get_relation(ClangRange(n1), ClangRange(n2))
        node_map[n1][rel].append(n2)

        if rel != rel.get_swap():
            node_map[n2][rel.get_swap()].append(n1)

    return node_map

