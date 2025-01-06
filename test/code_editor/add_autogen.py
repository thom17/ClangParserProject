from code_editor.code_editor import CodeEditor, insert_code_in_block_end, insert_code_in_block_start
from clangParser.Cursor import Cursor
import clang.cindex as ClangIndex

from typing import Tuple, Optional

editor = CodeEditor(r"D:\dev\AutoPlanning\trunk\Ap-Trunk-auto-task\mod_APImplantSimulation\ActuatorHybridFixture.cpp")
source_code = editor.cpp_unit.code
def get_set(node: ClangIndex.Cursor)-> Tuple[Cursor, Optional[Cursor]]:
    # source_code = None
    cursor = Cursor(node=node, source_code=source_code)

    for ch in [Cursor(ch, source_code=source_code) for ch in node.get_children()]:
        if ch.kind == 'COMPOUND_STMT':
            return cursor, ch
    return cursor, None





def test_add_replace_node():
    for node in editor.cpp_unit.this_file_nodes:
        method, block = get_set(node)
        if block:
            replace_block = insert_code_in_block_start(block, '\tAutoGentTest;')
            block_code = block.get_range_code()
            method_code = method.get_range_code()
            code = method_code.replace(block_code, replace_block)
            editor.add_replace_node(method, code)

def test_generate_replace_cpp():
    print(editor.generate_replace_cpp())


