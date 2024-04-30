from clang.cindex import Cursor as clangCursor
from clang.cindex import SourceLocation
from clang.cindex import TranslationUnit
from clang.cindex import SourceRange


class Cursor:
    """
    clang.cindex.Cursor 가 불편해서 정의
    """

    def __init__(self, node: clangCursor, source_code: str = None):
        assert isinstance(node, clangCursor), f"node{type(node)} must be an instance of clang.cindex.Cursor"
        self.node = node
        self.spelling = node.spelling
        self.location: SourceLocation = node.location
        self.extend: SourceRange = node.extent
        self.kind: str = node.kind.name
        self.translation_unit: TranslationUnit =node.translation_unit
        self.unit_path: str = self.translation_unit.spelling
        self.source_code = source_code


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

    def to_dict(self):
        # Convert to a dictionary or other JSON-serializable format
        location = {
            'file': self.location.file.name if self.location.file else None,
            'line': self.location.line,
            'column': self.location.column
        }

        start: SourceLocation = self.extend.start
        end: SourceLocation = self.extend.end

        range = {
            'startLine': start.line,
            'startColumn': start.column,
            'endLine': end.line,
            'endColumn': end.column,
        }
        return {
            'spelling': self.spelling,
            'kind': self.kind,
            'range': range,
            'location': location,
            'code': self.get_range_code()
        }


    # 기존 코드
    # def get_range_code(self):
    #     extent = self.extend
    #     start: SourceLocation = extent.start
    #     end: SourceLocation = extent.end
    #
    #     assert start.file.name == end.file.name, f"시작과 끝이 서로 다른 파일{start} , {end}"
    #
    #     with open(start.file.name, 'r') as file:
    #         source_code = file.read()
    #
    #         # 소스 코드 내에서 시작 위치와 종료 위치를 계산합니다.
    #         # libclang은 1 기반 인덱싱을 사용하므로, 파이썬의 0 기반 인덱싱으로 조정합니다.
    #         start_offset = source_code.rfind('\n', 0, source_code.find('\n', self.extend.start.offset)) + 1
    #         end_offset = source_code.find('\n', self.extend.end.offset)
    #
    #         # 시작 위치와 종료 위치 사이의 문자열을 반환합니다.
    #         return source_code[start_offset:end_offset]

    def get_range_code(self, code: str = None):
        """
        Returns the source code for the specific range including column information.
        """
        extent = self.node.extent
        start = extent.start
        end = extent.end

        if not (start.file and end.file and start.file.name == end.file.name):
            print("시작과 끝이 다른 파일")

            return ""

        try:
            with open(start.file.name, 'r') as file:
                source_code = file.read()
        except:
            print(start.file.name," read Fail")
            source_code = self.source_code
            return ""
            # Calculate the exact character offset for start and end
        start_index = self.calculate_offset(source_code, start.line, start.column)
        end_index = self.calculate_offset(source_code, end.line, end.column)

        return source_code[start_index:end_index]

    def get_range_line_code(self):
        """
        Returns the entire lines of code from the start to the end line without considering the columns.
        """
        extent = self.node.extent
        start = extent.start
        end = extent.end

        assert start.file.name == end.file.name, "Start and end are in different files."

        with open(start.file.name, 'r', encoding='utf-8') as file:
            lines = file.readlines()

            # Lines are 0-based in Python, adjust by -1 since Clang lines are 1-based
            return ''.join(lines[start.line - 1:end.line])

    def calculate_offset(self, source_code, line, column):
        """
        Calculates the offset of the specified line and column in the source code.
        """
        current_line = 1
        offset = 0
        # Iterate through the source code line by line
        for current_line_content in source_code.split('\n'):
            if current_line == line:
                # Columns are 1-based, adjust by -1 for 0-based indexing
                return offset + (column - 1)
            offset += len(current_line_content) + 1  # +1 for newline character
            current_line += 1

        return offset  # If line/column are out of bounds, this will be the end of the source code

    def get_visit_line_map(self)->dict[int, list]:
        line_map = {}
        queue = [self.node]
        if self.location.file:
            base_file_path = self.location.file.name
        while queue:
            node = queue.pop(0)
            c = Cursor(node, self.source_code)
            line: int = node.location.line
            if line not in line_map:
                line_map[line] = []
            line_map[line].append(c)
            queue.extend(node.get_children())
        return line_map

    def get_file_map(self) -> {str, list}:
        file_map = {}
        queue: [clangCursor] = [self.node]
        file_name = self.location.file.name if self.location.file else "None"

        while queue:
            node = queue.pop(0)
            new_cursor = Cursor(node, self.source_code)
            if file_name not in file_map:
                file_map[file_name] = []
            file_map[file_name].append(new_cursor)
            queue.extend(node.get_children())
        return file_map


    def get_visit_stmt_map(self) ->dict[str, list]:
        stmt_map = {}
        queue = [self.node]

        while queue:
            node = queue.pop(0)
            c = Cursor(node, self.source_code)
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


    def get_visit_unit_map(self) -> dict[TranslationUnit, list['Cursor']]:
        unit_map = {}
        queue = [self.node]

        while queue:
            node = queue.pop(0)
            c = Cursor(node, self.source_code)
            unit = node.translation_unit
            if unit not in unit_map:
                unit_map[unit] = []
            unit_map[unit].append(c)
            queue.extend(node.get_children())
        return unit_map


    def make_comment_code(self, code: str = None):
        """
        재귀적으로 순환해서 노드의 정보를 주석화
        :param code: None은 시작 그외 재귀시 파라미터로
        :return:
        """
        source_name = self.translation_unit.spelling

        if code is None:
            with open(source_name, 'r') as file:
                code = file.read()

        code2list = code.splitlines()

        extent = self.node.extent
        start = extent.start
        end = extent.end

        line = start.line
        # 현재 노드에 대한 주석 추가
        # try:
        #     code2list[line - 1] += f" // {self.node.kind.name}({self.node.spelling})"
        # except:
        #     print(f"line={line} size = {code2list.__len__()}")
        # code = '\n'.join(code2list)
        #
        # # 모든 자식 노드에 대해 재귀적으로 처리
        # for child in self.node.get_children():
        #     child_visitor = SimpleVisitor(child, self.base_path)
        #     code = child_visitor.make_comment_code(code)
        #
        # return code





if __name__ == "__main__":
    # with open(r"D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation\DSILibraryDrawer.cpp", 'r') as file:
    #     print(file.read())
    import clangParser
    import time

    start_time = time.time()
    compliationunit = clangParser.parsing(r"D:\dev\AutoPlanning\trunk\AP-6979-TimeTask\mod_APImplantSimulation\ActuatorHybridFixture.cpp")
    end_time = time.time()

    elapsed_time = end_time - start_time
    print("Parsing time:", elapsed_time, "seconds")

    mycursor = Cursor(compliationunit.cursor)

    start_time = time.time()
    line_map = mycursor.get_visit_line_map()
    end_time = time.time()

    elapsed_time = end_time - start_time
    print("Visit time:", elapsed_time, "seconds")

    for line in line_map:
        print(line, end=" ")
        for node in line_map[line]:
            print(f"{node.kind}({node.spelling})")
        print()
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
