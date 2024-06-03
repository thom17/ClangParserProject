import clang.cindex
from clang.cindex import Cursor
from clangParser.Cursor import Cursor as MyCursor

from oms.info_set import InfoSet
# from oms.info_set import InfoSet, RelationInfo
from oms.dataset.info_base import InfoBase, CoreInfoData
from oms.dataset.class_info import ClassInfo
from oms.dataset.function_info import FunctionInfo
from oms.dataset.var_info import VarInfo

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


def new_class_info(mycursor: MyCursor):
    cls_info = ClassInfo(make_core_info(mycursor))
    in_defs = find_has_infos(mycursor.node)
    for info in in_defs:
        cls_info.relationInfo.hasInfoMap.put_info(info)

    return cls_info


def is_target_node(node: Cursor):
    return node.is_definition() or node.kind.name in kind_list

def new_var_info(mycursor: MyCursor):
    core_info = make_core_info(mycursor)
    core_info.type_str = mycursor.node.type.spelling
    return VarInfo(core_info)


def new_fun_info(mycursor: MyCursor):
    core_info = make_core_info(mycursor)
    core_info.type_str = mycursor.node.result_type.spelling
    method_info = FunctionInfo(core_info)
    return method_info

def cursor2cls_info(cursor: Cursor):
    mycursor = MyCursor(cursor)
    src_name = mycursor.get_src_name()
    cls_info = base_info_set.get_class_info(src_name)
    if cls_info is None:
        cls_info = new_class_info(mycursor)
        base_info_set.put_info(cls_info)
    return cls_info

def cursor2var_info(cursor: Cursor):
    mycursor = MyCursor(cursor)
    src_name = mycursor.get_src_name()
    var_info = base_info_set.get_var_info(src_name)
    if var_info is None:
        var_info = new_var_info(mycursor)
        base_info_set.put_info(var_info)
    return var_info


def cursor2fun_info(cursor: Cursor):
    mycursor = MyCursor(cursor)
    src_name = mycursor.get_src_name()
    method_info = base_info_set.get_function_info(src_name)
    if method_info is None:
        method_info = new_fun_info(mycursor)
        base_info_set.put_info(method_info)
    return method_info

def find_has_infos(cursor: Cursor):
    """
    하나의 커서 내의 dec 노드들 찾기.
    h와 cpp 두개가 발생할수도 있는대... src_name 기준이니 중복안되겠지??
    아마도??
    :param cursor:
    :return:
    """
    info_list: [InfoBase] =[]

    for node in cursor.get_children():
        node:Cursor = node
        if is_target_node(node):
            info = Cursor2OMS(node)
            info_list.append(info)
        # else:
        #     print(node.kind,"\t",MyCursor(node).get_range_code())
    return info_list

def Cursor2OMS(cursor: Cursor):
    """
    Cursor 2 OMS
    없으면 OMS 생성
    :param cursor:
    :return:
    """
    if is_target_node(cursor):
        kind: str = cursor.kind.name
        if kind in class_kind_list:
            return cursor2cls_info(cursor)
        elif kind in method_kind_list:
            return cursor2fun_info(cursor)
        elif kind in var_kind_list:
            return cursor2var_info(cursor)

if __name__ == "__main__":
    from clangParser.CUnit import CUnit
    header_info_set = {}
#     unit=CUnit.parse(r"D:\dev\EcoCad\trunk\SimpleTask\mod_SCCrownDesign\CommandCrownDesignContact.h")
#
#     for node in unit.this_file_nodes:
#         info = Cursor2OMS(node)
#         if info:
#             header_info_set[info.src_name]=info
#             # print(info.src_name)
#
#         for child_node in node.get_children():
#             info = Cursor2OMS(child_node)
#             if info:
#             #     print("\t",info.src_name)
#                 header_info_set[info.src_name] = info
#
#     print("doen")
#
#     print(f"""
# {len(base_info_set.classInfos)} cls
# {len(base_info_set.functionInfos)} methods
# {len(base_info_set.varInfos)} vars
#           """)

    cpp_info_set = {}

    unit = CUnit.parse(r"D:\dev\EcoCad\trunk\SimpleTask\mod_SCCrownDesign\CommandCrownDesignContact.h")

    for node in unit.this_file_nodes:
        info = Cursor2OMS(node)
        if info:
            if info.src_name not in header_info_set:
                cpp_info_set[info.src_name] = info
            # print(info.src_name)

        for child_node in node.get_children():
            info = Cursor2OMS(child_node)
            if info:
                # print("\t", info.src_name)
                if info.src_name not in header_info_set:
                    cpp_info_set[info.src_name] = info

    print(f"""
{len(base_info_set.classInfos)} cls
{len(base_info_set.functionInfos)} methods
{len(base_info_set.varInfos)} vars          
          """)

    for src_name in cpp_info_set:
        print(src_name, "\t\t", type(cpp_info_set[src_name]))
    print()