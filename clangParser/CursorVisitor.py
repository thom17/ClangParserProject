from collections import defaultdict
from typing import Dict, List
import clang.cindex as ClangIndex

from clang.cindex  import Cursor as clangCursor, TranslationUnit

from clangParser.datas.Cursor import Cursor


class CursorVisitor:
    '''
    cursor의 visit 관련 메서드들.
    to do : Cursor to Cursor 관련한 visitor가 되어야함 (CursorVisitor 이므로)
    cindex to cindex 나 cindex to cursor는 각각의 visitor로 분리해야함
    '''
    def __init__(self, cursor: Cursor):
        self.cursor = cursor
        self.node = cursor.node

    def get_visit_def_map(self, node=None) -> [str, clangCursor]:
        visit_map: [str, 'clangCursor'] = {}  # 1:1 대응으로 바꿔도 문제없어야 함
        if node is None:
            node = self.node
        queue = [node]
        while queue:
            node = queue.pop(0)
            if node.is_definition():
                visit_map[Cursor(node).get_src_name()] = node
            queue.extend(node.get_children())
        return visit_map

    def get_visit_line_map(self) -> Dict[int, List['Cursor']]:
        line_map = {}
        queue = [self.node]
        if self.node.location.file:
            base_file_path = self.node.location.file.name
        while queue:
            node = queue.pop(0)
            c = get_cursor(node)
            line: int = node.location.line
            if line not in line_map:
                line_map[line] = []
            line_map[line].append(c)
            queue.extend(node.get_children())
        return line_map

    def get_file_map(self) -> Dict[str, List['Cursor']]:
        file_map = {}
        queue: [clangCursor] = [self.node]
        file_name = self.node.location.file.name if self.node.location.file else "None"

        while queue:
            node = queue.pop(0)
            new_cursor = get_cursor(node)
            if file_name not in file_map:
                file_map[file_name] = []
            file_map[file_name].append(new_cursor)
            queue.extend(node.get_children())
        return file_map

    def get_visit_type_map(self) -> Dict[str, List['Cursor']]:
        stmt_map = {}
        queue = [self.node]

        while queue:
            node = queue.pop(0)
            c = get_cursor(node)
            type_name: str = node.kind.name
            if type_name not in stmt_map:
                stmt_map[type_name] = []
            stmt_map[type_name].append(c)
            queue.extend(node.get_children())
        return stmt_map

    def  get_stmt_list(self) -> List['Cursor']:
        stmt_list = []
        queue = [self.node]

        while queue:
            node = queue.pop(0)
            if node.kind.is_statement():
                stmt_list.append(get_cursor(node))
            queue.extend(node.get_children())
        return stmt_list

    def get_stmt_map(self) -> Dict['Cursor', List['Cursor']]:
        stmt_map = defaultdict(list)
        self.__visit_stmt(stmt_map=stmt_map, key=self.node)
        return stmt_map

    def __visit_stmt(self, stmt_map: Dict['Cursor', List['Cursor']], key: clangCursor):
        for child in key.get_children():
            child_cursor = get_cursor(child)
            stmt_map[key].append(child_cursor)

            if child_cursor.node.kind.is_statement():
                self.__visit_stmt(stmt_map=stmt_map, key=child_cursor)

    def visit_print(self):
        queue = [(self.node, "")]

        while queue:
            node, lv = queue.pop(0)
            print(f"{lv}{node.spelling} ({node.kind} {node.location.line}:{node.location.column})")
            c = get_cursor(node)
            print(c.get_range_code())
            new_lv = lv + "* "
            childs = [(child, new_lv) for child in node.get_children()]
            queue = childs + queue

    def visit_nodes(self) -> List[clangCursor]:
        visit_list = []
        queue = [self.node]

        while queue:
            node = queue.pop(0)
            visit_list.append(node)
            queue[:0] = node.get_children()
        return visit_list

    def get_visit_unit_map(self) -> Dict[TranslationUnit, List['Cursor']]:
        unit_map = {}
        queue = [self.node]

        while queue:
            node = queue.pop(0)
            c = get_cursor(node)
            unit = node.translation_unit
            if unit not in unit_map:
                unit_map[unit] = []
            unit_map[unit].append(c)
            queue.extend(node.get_children())
        return unit_map
    
    def get_visit_line_size_map(self) -> dict[int, ['Cursor']]:
        line_size_map = defaultdict(list)
        queue = [self.node]

        while queue:
            node: clangCursor = queue.pop(0)
            c:Cursor = get_cursor(node)
            line_size = c.get_line_size()
            line_size_map[line_size].append(c)
            queue.extend(node.get_children())
        return line_size_map
    
    def get_visit_line_token_map(self, node = None)->dict[int, [ClangIndex.Token]]:
        line_map = {}
        if node is None:
            node=self.node
        for token in node.get_tokens():
            line: int = token.location.line
            if line not in line_map:
                line_map[line] = []
            line_map[line].append(token)
        return line_map

    def get_visit_kind_token_map(self, node = None)->dict[str, [ClangIndex.Token]]:
        kind_map = {}
        if node is None:
            node=self.node
        for token in node.get_tokens():
            kind = token.kind
            if kind not in kind_map:
                kind_map[kind] = []
            kind_map[kind].append(token)
        return kind_map


def get_cursor(node: clangCursor) -> 'Cursor':
    if isinstance(node, Cursor):
        return node
    else:
        return Cursor(node)



