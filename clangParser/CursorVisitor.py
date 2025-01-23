from collections import defaultdict
from typing import Dict, List, Optional
import clang.cindex as ClangIndex

# from clang.cindex  import Cursor as clangCursor, TranslationUnit


#해당 visitor는 cursor를 기반으로 작동함. clang을 사용하면 안됨
from clangParser.datas.Cursor import Cursor


class CursorVisitor:
    '''
    cursor의 visit 관련 메서드들.
    to do : Cursor to Cursor 관련한 visitor가 되어야함 (CursorVisitor 이므로)
    cindex to cindex 나 cindex to cursor는 각각의 visitor로 분리해야함
    '''
    def __init__(self, cursor: Cursor):
        self.cursor: Cursor = cursor
        self.node: Optional[Cursor] = cursor.node

    def get_visit_def_map(self, node=None) -> Dict[str, Cursor]:
        visit_map: Dict[str, Cursor] = {}  # 1:1 대응으로 바꿔도 문제없어야 함
        if node is None:
            node = self.cursor
        queue = [node]

        while queue:
            node = queue.pop(0)
            if node.is_definition():
                visit_map[node.get_src_name()] = node
            queue.extend(node.get_children())
        return visit_map

    def get_visit_line_map(self) -> Dict[int, List[Cursor]]:
        line_map: Dict[int, List[Cursor]] = {}
        queue = [self.cursor]

        while queue:
            node = queue.pop(0)

            line: int = node.location.line
            if line not in line_map:
                line_map[line] = []
            line_map[line].append(node)
            queue.extend(node.get_children())
        return line_map

    def get_file_map(self) -> Dict[str, List[Cursor]]:
        file_map = {}
        queue: List[Cursor] = [self.cursor]
        file_name = self.cursor.location.file.name if self.cursor.location.file else "None"

        while queue:
            node = queue.pop(0)
            if file_name not in file_map:
                file_map[file_name] = []
            file_map[file_name].append(node)
            queue.extend(node.get_children())
        return file_map

    def get_visit_type_map(self) -> Dict[str, List[Cursor]]:
        stmt_map = {}
        queue = [self.cursor]

        while queue:
            node = queue.pop(0)
            type_name: str = node.kind

            if type_name not in stmt_map:
                stmt_map[type_name] = []
            stmt_map[type_name].append(node)
            queue.extend(node.get_children())
        return stmt_map

    def get_stmt_list(self) -> List[Cursor]:
        stmt_list = []
        queue = [self.cursor]

        while queue:
            node = queue.pop(0)
            if node.is_statement():
                stmt_list.append(node)
            queue.extend(node.get_children())
        return stmt_list

    def get_stmt_map(self) -> Dict[Cursor, List[Cursor]]:
        stmt_map = defaultdict(list)
        self.__visit_stmt(stmt_map=stmt_map, key=self.cursor)
        return stmt_map

    def __visit_stmt(self, stmt_map: Dict[Cursor, List[Cursor]], key: Cursor):
        for child_cursor in key.get_children():
            stmt_map[key].append(child_cursor)

            if child_cursor.is_statement():
                self.__visit_stmt(stmt_map=stmt_map, key=child_cursor)

    def visit_print(self):
        queue = [(self.cursor, "")]

        while queue:
            node, lv = queue.pop(0)
            print(f"{lv}{node.spelling} ({node.kind} {node.location.line}:{node.location.column})")
            print(node.get_range_code())
            new_lv = lv + "* "
            childs = [(child, new_lv) for child in node.get_children()]
            queue = childs + queue

    def visit_nodes(self) -> List[Cursor]:
        visit_list = []
        queue = [self.cursor]

        while queue:
            node = queue.pop(0)
            visit_list.append(node)
            queue[:0] = node.get_children()
        return visit_list

    # 사실상 type map 에서 추리면 되며 사용빈도가 낮을듯 사용 x
    # def get_visit_unit_map(self) -> Dict[TranslationUnit, List[Cursor]]:
    #     unit_map = {}
    #     queue = [self.cursor]

    #     while queue:
    #         node = queue.pop(0)
    #         c = get_cursor(node)
    #         unit = node.translation_unit
    #         if unit not in unit_map:
    #             unit_map[unit] = []
    #         unit_map[unit].append(c)
    #         queue.extend(node.get_children())
    #     return unit_map
    
    def get_visit_line_size_map(self) -> Dict[int, List[Cursor]]:
        line_size_map = defaultdict(list)
        queue = [self.cursor]

        while queue:
            node: Cursor = queue.pop(0)
            line_size = node.get_line_size()
            line_size_map[line_size].append(node)
            queue.extend(node.get_children())
        return dict(line_size_map)

    #토큰은 추후에 ClangVisitor에서 구현하자    
    # def get_visit_line_token_map(self, node = None)->Dict[int, List[ClangIndex.Token]]:
    #     line_map:Dict[int, List[ClangIndex.Token]] = {}
    #     if node is None:
    #         node=self.cursor
    #     for token in node.get_tokens():
    #         line: int = token.location.line
    #         if line not in line_map:
    #             line_map[line] = []
    #         line_map[line].append(token)
    #     return line_map

    # def get_visit_kind_token_map(self, node = None)->Dict[str, List[ClangIndex.Token]]:
    #     kind_map = {}
    #     if node is None:
    #         node=self.cursor
    #     for token in node.get_tokens():
    #         kind = token.kind
    #         if kind not in kind_map:
    #             kind_map[kind] = []
    #         kind_map[kind].append(token)
    #     return kind_map


# def get_cursor(node: clangCursor) -> Cursor:
#     if isinstance(node, Cursor):
#         return node
#     else:
#         return Cursor(node)



