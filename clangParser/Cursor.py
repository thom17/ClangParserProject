from clang.cindex import Cursor as clangCursor
from clang.cindex import SourceLocation
from clang.cindex import TranslationUnit
from clang.cindex import SourceRange


class Cursor:
    """
    clang.cindex.Cursor 가 불편해서 정의
    """

    def __init__(self, node: clangCursor):
        assert isinstance(node, clangCursor), "node must be an instance of clang.cindex.Cursor"
        self.node = node
        self.spelling = node.spelling
        self.location: SourceLocation = node.location
        self.extend: SourceRange = node.extent
        self.kind: str = node.kind.name
        self.translation_unit: TranslationUnit =node.translation_unit
        self.unit_path: str = self.translation_unit.spelling

        # try:
        #     if self.unit_path:
        #         with open(self.unit_path, 'r') as file:
        #             self.unit_source_code = file.read()
        #
        #         if self.location.file:
        #             with open(self.location.file.name, 'r') as file:
        #                 self.node_source_code = file.read()
        #         else:
        #             self.node_source_code = self.unit_source_code
        # except:
        #     print("error ",node.location)
    def get_range(self):
        start: SourceLocation = self.extend.start
        end: SourceLocation = self.extend.end

        return f"{start.line}:{start.column}~{end.line}:{end.column}"

    # def visit_for_range(self):
    def get_range_code(self):
        extent = self.extend
        start: SourceLocation = extent.start
        end: SourceLocation = extent.end

        assert start.file.name == end.file.name, f"시작과 끝이 서로 다른 파일{start} , {end}"

        with open(start.file.name, 'r') as file:
            source_code = file.read()

            # 소스 코드 내에서 시작 위치와 종료 위치를 계산합니다.
            # libclang은 1 기반 인덱싱을 사용하므로, 파이썬의 0 기반 인덱싱으로 조정합니다.
            start_offset = source_code.rfind('\n', 0, source_code.find('\n', self.extend.start.offset)) + 1
            end_offset = source_code.find('\n', self.extend.end.offset)

            # 시작 위치와 종료 위치 사이의 문자열을 반환합니다.
            return source_code[start_offset:end_offset]

    def get_visit_line_map(self)->dict[int, list]:
        line_map = {}
        queue = [self.node]
        if self.location.file:
            base_file_path = self.location.file.name
        while queue:
            node = queue.pop(0)
            c = Cursor(node)
            line: int = node.location.line
            if line not in line_map:
                line_map[line] = []
            line_map[line].append(c)
            queue.extend(node.get_children())
        return line_map

    def get_visit_stmt_map(self) ->dict[str, list]:
        stmt_map = {}
        queue = [self.node]

        while queue:
            node = queue.pop(0)
            c = Cursor(node)
            type_name = node.kind.name
            if type_name not in stmt_map:
                stmt_map[type_name] = []
            stmt_map[type_name].append(c)
            queue.extend(node.get_children())
        return stmt_map

    def visit_print(self):
        queue = [(self.node, "")]

        while len(queue):
            node, lv = queue.pop(0)
            print(f"{lv}{node.spelling} ({node.kind} {node.location.line}:{node.location.column})")
            c = Cursor(node)
            print(c.get_range_code())
            # Update the level indicator for child nodes
            new_lv = lv + "* "

            # Prepare child nodes to be added to the queue
            childs = [(child, new_lv) for child in node.get_children()]
            queue = childs + queue







if __name__ == "__main__":
    # with open(r"D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation\DSILibraryDrawer.cpp", 'r') as file:
    #     print(file.read())



    import clangParser

    compliationunit = clangParser.parsing("../test/temp.cpp")
    mycursor = Cursor(compliationunit.cursor)
    print(mycursor.visit_print())

    same = compliationunit == mycursor.node.translation_unit
    print("is ", same)

    print(mycursor.get_range_code())

    stmt_map = mycursor.get_visit_stmt_map()

    for type_name in stmt_map:
        cursor_list = stmt_map[type_name]
        print(f"{type_name} : {cursor_list.__len__()} size")

    expr_list = stmt_map["CALL_EXPR"]
    print(type(expr_list))
    for c in expr_list:
        print(c)
        print(f"{c.get_range_code()} @{c.spelling}")

    line_map = mycursor.get_visit_line_map()
    for num in line_map:
        print(num, line_map[num])


    print("done")
