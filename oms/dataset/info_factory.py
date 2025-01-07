import clang.cindex
from clang.cindex import Cursor
import clangParser.clangParser as clangParser
import clangParser.clang_utill as ClangUtil
from clangParser.Cursor import Cursor as MyCursor
from clangParser.CUnit import CUnit


from oms.info_set import InfoSet
# from oms.info_set import InfoSet, RelationInfo
from oms.dataset.info_base import InfoBase, CoreInfoData
from oms.dataset.class_info import ClassInfo
from oms.dataset.function_info import FunctionInfo
from oms.dataset.var_info import VarInfo

from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class_kind_list=[
    "STRUCT_DECL", "CLASS_DECL", "ENUM_DECL", "TYPEDEF_DECL", "NAMESPACE"
                 ]


method_kind_list=[
    "FUNCTION_DECL", "CXX_METHOD", "ENUM_DECL", "CONSTRUCTOR", "DESTRUCTOR", "CONVERSION_FUNCTION"
                 ]


var_kind_list=[
    "FIELD_DECL", "ENUM_CONSTANT_DECL", "ENUM_DECL", "PARM_DECL",
                 ]

kind_list = class_kind_list + method_kind_list + var_kind_list

base_info_set = InfoSet()
src_map:[str, ] = {}



def make_core_info(mycursor: MyCursor):
    """
    클래스의 생성을 여기서 하는게 맞을까?
    일단 외부 클래스와 OMS의 연결 담당이니까?
    :param mycursor:
    :return:
    """
    node = mycursor.node
    src_name = mycursor.get_src_name()
    name = mycursor.node.spelling
    is_virtual =node.is_virtual_method()
    is_static=node.is_static_method()
    modifier=""
    package_str=node.location.file.name
    code = mycursor.get_range_code()

    return CoreInfoData(src_name=src_name, name=name,
             is_virtual=is_virtual, is_static=is_static,
             modifier=modifier, package_str=package_str,
             code=code, comment="", type_str="")


def new_class_info(mycursor: MyCursor, base_info_set, clang_src_map):
    owner_oms = Cursor2OMS(mycursor.node.semantic_parent, base_info_set, clang_src_map)
    cls_info = ClassInfo(make_core_info(mycursor), owner_oms)
    # in_defs = find_has_infos(mycursor.node)
    # for info in in_defs:
    #     cls_info.relationInfo.hasInfoMap.put_info(info)

    src_map[cls_info.src_name] = mycursor

    return cls_info



def new_var_info(mycursor: MyCursor, base_info_set, clang_src_map):
    owner_oms = Cursor2OMS(mycursor.node.semantic_parent, base_info_set, clang_src_map)
    core_info = make_core_info(mycursor)
    core_info.type_str = mycursor.node.type.spelling

    var_info = VarInfo(core_info, owner_oms)
    src_map[var_info.src_name] = mycursor
    return var_info


def new_fun_info(mycursor: MyCursor, base_info_set, clang_src_map):
    owner_oms = Cursor2OMS(mycursor.node.semantic_parent, base_info_set, clang_src_map)
    core_info = make_core_info(mycursor)
    core_info.type_str = mycursor.node.result_type.spelling
    method_info = FunctionInfo(core_info, owner_oms)

    src_map[method_info.src_name] = mycursor
    return method_info

def __cursor2cls_info(cursor: Cursor, base_info_set, clang_src_map):
    mycursor = MyCursor(cursor)
    src_name = mycursor.get_src_name()
    cls_info = base_info_set.get_class_info(src_name)
    if cls_info is None:
        cls_info = new_class_info(mycursor, base_info_set, clang_src_map)
        base_info_set.put_info(cls_info)
    return cls_info

def __cursor2var_info(cursor: Cursor, base_info_set, clang_src_map):
    mycursor = MyCursor(cursor)
    src_name = mycursor.get_src_name()
    var_info = base_info_set.get_var_info(src_name)
    if var_info is None:
        var_info = new_var_info(mycursor, base_info_set, clang_src_map)
        base_info_set.put_info(var_info)
    return var_info


def __cursor2fun_info(cursor: Cursor, base_info_set, clang_src_map):
    mycursor = MyCursor(cursor)
    src_name = mycursor.get_src_name()
    method_info = base_info_set.get_function_info(src_name)
    if method_info is None:
        method_info = new_fun_info(mycursor, base_info_set, clang_src_map)
        base_info_set.put_info(method_info)
    return method_info

def Cursor2InfoBase(cursor: Cursor)->Optional[InfoBase]:
    base_info_set = InfoSet()
    clang_src_map = defaultdict(list)
    return Cursor2OMS(cursor=cursor, base_info_set=base_info_set, clang_src_map=clang_src_map)





def Cursor2OMS(cursor: Cursor, base_info_set, clang_src_map):
    """
    Cursor 2 OMS
    없으면 OMS 생성
    :param cursor:
    :return:
    """

    def is_target_node(node: Cursor):
        if node is None:
            return False
        elif node.is_definition() and node.get_definition() == node and not node.kind.name == 'CXX_ACCESS_SPEC_DECL':
            return True
        elif node.kind.name in kind_list:
            return True



    if cursor is None:
        return None

    if isinstance(cursor, MyCursor):
        cursor = cursor.node

    src_name = ClangUtil.get_src_name(cursor)
    if not clang_src_map[src_name].__contains__(cursor):
        clang_src_map[src_name].append(cursor)

    oms_info = base_info_set.get_info(src_name)
    if oms_info:
        return oms_info

    #srcName을 토큰을 통해 정의해서 문제가 안될듯? 추가적으로 기존 데이터에 업데이트는 필요할수있음
    # cursor = cursor.get_definition()
    if is_target_node(cursor):
        kind: str = cursor.kind.name
        if kind in class_kind_list:
            return __cursor2cls_info(cursor, base_info_set, clang_src_map)
        elif kind in method_kind_list:
            return __cursor2fun_info(cursor, base_info_set, clang_src_map)
        elif kind in var_kind_list:
            return __cursor2var_info(cursor, base_info_set, clang_src_map)
    else:
        return None

def get_target_cursor(data):
    '''
    어떤 파라미터든 Mapping이 되는 기본 노드리스트로 반환한다.
    :param data:
    :return:
    '''
    data_list = data
    if not isinstance(data, list):
        data_list = [data]

    target_cursors = []
    for data in data_list:
        if isinstance(data, str):
            data = clangParser.parsing(data)

        if isinstance(data, clang.cindex.TranslationUnit):
            for child_node in data.cursor.get_children():
                if child_node.location.file.name == data.spelling:
                    target_cursors.append(child_node)

        elif isinstance(data, CUnit):
            target_cursors = target_cursors + data.this_file_nodes

        elif isinstance(data, clang.cindex.Cursor):
            target_cursors.append(data)
        else:
            assert False, f"잘못된 데이터 입력. {type(data)}"

    return target_cursors




def parsing(cursor_list: List[Cursor], do_update = True) ->Tuple[InfoSet, Dict[str, List[Cursor]]]:
    """
    Cursor 2 OMS
    없으면 OMS 생성
    :param [cursor]:
    :return InfoSet:
    """

    def update_call(my_cursor: MyCursor, oms_data: InfoBase, oms_set: InfoSet, clang_src_map: [str, Cursor]):
        visit_line_map = my_cursor.get_visit_line_map()

        for line in visit_line_map:
            for cursor in visit_line_map[line]:
                def_node = cursor.node.get_definition()

                if def_node is None:
                    def_node = cursor.node.referenced
                    call_data = Cursor2OMS(def_node, oms_set, clang_src_map)
                else:
                    call_data = Cursor2OMS(def_node, oms_set, clang_src_map)

                if call_data:
                    oms_data.add_callInfo(call_data)
                    owner_data = oms_data.owner
                    if owner_data:
                        owner_data.add_callInfo(call_data)

    cursor_list = get_target_cursor(cursor_list)

    if not isinstance(cursor_list, list):
        cursor_list = [cursor_list]

    all_data_set = InfoSet()
    clang_src_map = defaultdict(list)

    size = len(cursor_list)
    done = 0
    for cursor in cursor_list:
        data = Cursor2OMS(cursor, all_data_set, clang_src_map)
        done += 1
        percent = (done/size) * 100
        print(f"\rMapping ({percent:.2f}%) {done}/{size}", end="")

    print("\nMapping done")

    if do_update:
        sorted_key = sorted(all_data_set.functionInfos)
        size = len(sorted_key)
        done = 0
        for fun_src_name in sorted_key:
            mycursor = src_map[fun_src_name]
            method_info = all_data_set.functionInfos[fun_src_name]
            update_call(mycursor, method_info, all_data_set, clang_src_map)
            done += 1
            percent = (done / size) * 100
            print(f"\rUpdate Call ({percent:.2f}%) {done}/{size}", end="")

        print("\nUpdate done")

    return all_data_set, clang_src_map







if __name__ == "__main__":
    from clangParser.CUnit import CUnit
    files = [r'D:\dev\EcoCad\trunk\pure\mod_SCCrownDesign\ToolBarCrownDesign.cpp', r'D:\dev\EcoCad\trunk\pure\mod_SCCrownDesign\UIDlgCrownLibrary.cpp']
    result, clang_src_map=parsing(files)

    print("doen")

    print(f"""
{len(result.classInfos)} cls    
{len(result.functionInfos)} methods
{len(result.varInfos)} vars
          """)

    for src in result.classInfos:
        cls_info: ClassInfo = result.classInfos[src]
        core_dict = cls_info.to_dict()
        # print(core_dict)

    cpp_info_set = {}

    # from neo4j_handler import Neo4jHandler
    #
    # neo4j_handler = Neo4jHandler("bolt://localhost:7687", "neo4j", "123456789")
    # neo4j_handler.delete_all_nodes()
    # neo4j_handler.make_db(result)

    # unit = CUnit.parse(r"D:\dev\EcoCad\trunk\SimpleTask\mod_SCCrownDesign\CommandCrownDesignContact.h")

#     for node in unit.this_file_nodes:
#         info = Cursor2OMS(node, base_info_set)
#         if info:
#             if info.src_name not in header_info_set:
#                 cpp_info_set[info.src_name] = info
#             # print(info.src_name)
#
#         for child_node in node.get_children():
#             info = Cursor2OMS(child_node, base_info_set)
#             if info:
#                 # print("\t", info.src_name)
#                 if info.src_name not in header_info_set:
#                     cpp_info_set[info.src_name] = info
#
#     print(f"""
# {len(base_info_set.classInfos)} cls
# {len(base_info_set.functionInfos)} methods
# {len(base_info_set.varInfos)} vars
#           """)
#
#     for src_name in cpp_info_set:
#         print(src_name, "\t\t", type(cpp_info_set[src_name]))
    print("done")