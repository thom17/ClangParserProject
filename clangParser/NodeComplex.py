from clang.cindex import Cursor as clangCursor
from clang.cindex import CursorKind as cursorKind
class NodeComplex:
    def __init__(self, node: clangCursor):
        assert isinstance(node, clangCursor), "clang.Cursor로 초기화"

        self.node = node

    def calculate_cyclomatic(self, node=None, complexity=1):
        """
        재귀적으로 AST 노드를 순회하며 복잡도를 계산
        람다식, 매크로 같은 경우 정확하지 않을듯
        """
        if node is None:
            node = self.node

        kind = node.kind
        # 결정 노드를 확인하고 복잡도를 증가
        if kind in [cursorKind.IF_STMT, cursorKind.FOR_STMT,
                    cursorKind.WHILE_STMT, cursorKind.DO_STMT,
                    cursorKind.CASE_STMT]:
            complexity += 1

        # 자식 노드를 순회
        for child in node.get_children():
            complexity = self.calculate_cyclomatic(child, complexity)

        return complexity

    def calculate_coupling(self, node=None):
        if node is None:
            node = self.node

        source_file = node.location.file.name

        external_calls = {}

        for child_node in node.walk_preorder():
            if child_node.kind == cursorKind.CALL_EXPR:
                callee = child_node.referenced
                if callee and callee.location.file and callee.location.file.name != source_file:
                    if callee.spelling not in external_calls:
                        external_calls[callee.spelling] = 0
                    external_calls[callee.spelling] += 1

        return external_calls
