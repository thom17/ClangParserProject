from clangParser.CursorVisitor import CursorVisitor
from clangParser.datas.CUnit import CUnit, Cursor

visitor: CursorVisitor = None


def get_mpr_fixutre_unit():
    return CUnit.parse(r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation\ActuatorMPRFixrueBase.cpp')

def test_all_method(visitor=None):
    if visitor is None:
        unit = get_mpr_fixutre_unit()
        node = unit.get_in_range_node(80) #onUpdate
        cursor = Cursor(node)
        visitor = cursor.cursor_visitor

    visitor.get_visit_def_map()
    visitor.get_visit_line_map()
    visitor.get_file_map()
    visitor.get_visit_type_map()
    visitor.get_stmt_list()
    visitor.get_stmt_map()
    visitor.visit_print()
    visitor.visit_nodes()
    # visitor.get_visit_unit_map()
    visitor.get_visit_line_size_map()
    # visitor.get_visit_line_token_map()
    # visitor.get_visit_kind_token_map()