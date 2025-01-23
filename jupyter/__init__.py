"""
두개의 파일 비교.
유사한 두개의 파일 한쪽에 맞도록 변형하여 복사처리 (to do)
"""

import sys

sys.path.append('../')

ap_path_list = [
    # r'D:\dev\AutoPlanning\Pano\Pano_pure\mod_APImplantSimulation\UIDlgCrownLibrary.cpp',
        r'D:\dev\AutoPlanning\Pano\Pano_pure\mod_APImplantSimulation\ToolBarCrownDesign.cpp'
]

cad_path_list = [
    # r'D:\dev\EcoCad\trunk\pure\mod_SCCrownDesign\UIDlgCrownLibrary.cpp',
    r'D:\dev\EcoCad\trunk\pure\mod_SCCrownDesign\ToolBarCrownDesign.cpp'
]
#
# from oms.Mapper import parsing as ParsingOMS
# st = time.time()
# ap_oms_infos, ap_clang_src_map = ParsingOMS(ap_path_list)
# cad_oms_infos, cad_clang_src_map = ParsingOMS(cad_path_list)
# ed = time.time()
# print(ed-st)


from clangParser.datas.CUnit import CUnit, Cursor
import clang.cindex as clangIndex
unit = CUnit.parse(r'D:\dev\EcoCad\trunk\pure\mod_SCCrownDesign\ToolBarCrownDesign.cpp')
node_list = [Cursor(node) for node in unit.this_file_nodes]

for idx, node in enumerate(node_list):
    print(idx," :",node)

from collections import defaultdict
line_num_map = defaultdict(list)

# target_node = node_list[9] #onUpate
# target_node = node_list[56] #OnBnClickedBtnWaxing
target_node = node_list[49] #OnBnClickedBtnSelectLibrary
line_map = target_node.get_visit_line_map()
for line, nodes in line_map.items():
    # print(line, " : ")
    for node in nodes:
        node: Cursor
        line_num_map[node.get_line_size()].append(node)

for line_size, nodes in sorted(line_num_map.items()):
    print(line_size, " line size : ")
    for node in nodes:
        kind: clangIndex.CursorKind = node.node.kind
        is_stmt = kind.is_statement()

        print(node, " is stmt ", is_stmt)

stmt_map = target_node.get_stmt_map()
# lex_p = n.lexical_parent
# is_same = (lex_p == n)

# for key in stmt_map:
#     print(f"{key.get_line_size()} : {key} {key.get_range()}")

# stmt_map 딕셔너리의 키를 key.get_range() 반환값에 따라 정렬
sorted_keys = sorted(stmt_map.keys(), key=lambda key: key.get_range())

# 정렬된 키를 사용하여 출력
for key in sorted_keys:
    line_size = key.get_line_size()
    range_value = key.get_range()
    print(f"{line_size} : {key} {range_value}")

#세미 클론 생략됨. 다 붙어서 나옴. 	_pDlgCrownLibrary->SetToothList(vTooth)_pDlgCrownLibrary->ShowWindow(SW_SHOW)_pDlgCrownLibrary->ShowPreview(true)if (TRUE == _pDlgCrownLibrary->IsWindowVisible())
#range를 정교하게 다룰 필요가 있음.
# def get_sub_code(data: Cursor, text:str):
#     line_map = data.get_visit_line_map()
#     line_codes =data.get_range_code().splitlines()
#     source_line = data.location.line
#
#     block_orders = []
#     n_line_set = set()
#     contain_lines:[Cursor] = []
#     for line, nodes in line_map.items():
#         for node in nodes:
#             if text in node.spelling:
#                 contain_lines.append(node)
#                 n_line_set.add(line)
#             if node.node.kind.is_statement():
#                 block_orders.append(node)
#
#     last_code_range = None
#     code = "//auto-gen toolbar copy start\n"
#
#     end_line = 0
#     end_column = -1
#     for line in n_line_set:
#         if end_line <= line:    #blaba; blabla;\n 와 같은 구조도 있어서?
#             for node in line_map[line]:
#                 start_pos:clangIndex.SourceLocation = node.extend.start
#                 start_column = start_pos.column
#                 if end_line < line or (end_line == line and end_column <= start_column):
#                     in_tab=""
#                     if end_line != line:
#                         in_tab = '\t' * line_codes[line-source_line].count('\t') + ' ' * line_codes[line-source_line].count(' ')
#                     code += in_tab+node.get_range_code()
#                     end_line = node.extend.end.line
#                     end_column = node.extend.end.column
#
#     code += "\n//auto-gen toolbar copy end\n"
#     return code
def get_sub_code(data: Cursor, text:str):
    data = data.get_stmt_list()[0] #메서드 블럭
    line_map = data.get_visit_line_map()
    line_codes =data.get_range_code().splitlines()
    source_line = data.location.line
    method_block_node = data.node

    block_orders = []
    n_line_set = set()
    contain_lines:[Cursor] = []
    for line, nodes in line_map.items():
        for node in nodes:
            if method_block_node == node.node: #이러면 전체 코드가 잡힌다.
                continue

            if text in node.get_range_code():
                contain_lines.append(node)
                n_line_set.add(line)
                if 1 < node.get_line_size():
                    for l in range(node.line_size):
                        n_line_set.add(l+line+1)

            if node.node.kind.is_statement():
                block_orders.append(node)

    code = "//auto-gen toolbar copy start\n"
    for line in sorted(n_line_set):
        code+=line_codes[line-source_line]+'\n'
    code += "//auto-gen toolbar copy end\n"
    return code


print("#"*100)
print(get_sub_code(target_node, '_pDlgCrownLibrary'))

print("#"*100)

# print(line_map)



