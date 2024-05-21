from clang.cindex import Cursor as clangCursor
from clang.cindex import TranslationUnit, CursorKind
from clang.cindex import SourceLocation as ClangSourceLocation
from clang.cindex import SourceRange as ClangSourceRange
from clang.cindex import CursorKind
import os

from dataclasses import dataclass, asdict, field
from sympy.physics.units import force
from typing import Optional


def get_simple_file_name(path: str):
    # 경로를 표준화합니다.
    normalized_path = os.path.normpath(path)

    # 경로를 구성하는 파트들을 리스트로 분리합니다.
    parts = normalized_path.split(os.sep)

    # 마지막 파일 이름과 그 바로 상위 디렉토리만 포함하도록 조정합니다.
    if len(parts) > 1:
        result_path = os.path.join(parts[-2], parts[-1])
    else:
        result_path = parts[-1]  # 파일 또는 폴더만 있는 경우

    return result_path

def calculate_offset(source_code, line, column):
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

@dataclass
class SourceLocation:
    @staticmethod
    def from_clang(location : ClangSourceLocation):
        file_name=location.file.name if location.file else None
        return SourceLocation(file=file_name, line=location.line, column=location.column)
    file: Optional[str]
    line: int
    column: int

    def to_dict(self):
        return asdict(self)

@dataclass
class SourceRange:

    start: SourceLocation
    end: SourceLocation
    @staticmethod
    def from_clang(extnd: ClangSourceRange):
        start = SourceLocation.from_clang(extnd.start)
        end = SourceLocation.from_clang(extnd.end)
        return SourceRange(start=start, end=end)

    def to_dict(self):
        return {
            'start': self.start.to_dict(),
            'end': self.end.to_dict()
        }



@dataclass
class ClangCursor:
    """
    clangParser.Cursor 복사
    clang.cindex.Cursor 가 불편해서 정의
    """
    id : int
    spelling: str
    kind: str
    location: str
    extend: str
    unit_path: str
    is_def: bool
    source_code: Optional[str] = None
    src_name: Optional[str] = None

    s_id : int = 0
    @staticmethod
    def from_clang(node: clangCursor):
        location = SourceLocation.from_clang(node.location)
        return ClangCursor(
            spelling=node.spelling,
            kind=node.kind.name,
            location= str(location.file + ":" + str(location.line) + ":" + str(location.column)),
            extend=ClangCursor.get_extnd_str(node.extent),
            unit_path=node.translation_unit.spelling,
            is_def=node.is_definition(),
            source_code=ClangCursor.get_range_code(node),
            src_name=ClangCursor.get_src_name(node),
            id=ClangCursor.s_id
        )

    def to_dict(self):
        return asdict(self)

    def __post_init__(self):
        # 클래스 속성 증가
        ClangCursor.s_id += 1
    @staticmethod
    def get_extnd_str(extend):
        start: SourceLocation = extend.start
        end: SourceLocation = extend.end

        return f"{start.line}:{start.column}~{end.line}:{end.column}"

    @staticmethod
    def get_src_name(node):
        """
        그 srcName
        클래스.메서드.메서드.변수, 파일.변수, 파일.매서드
        정리되기 전까지는 특정 노드만 사용하자
        :return:
        """

        #assert node.type in safe_src_type, f"{node.type}은 srcName 출력 불가"
        #assert node.semantic_parent, f"{node.kind}은 srcName 출력 불가"

        #파일 자체의 매서드, 변수이거나 클래스 내부이거나
        # if node.kind == CursorKind.CLASS_DECL or node.kind == CursorKind.TRANSLATION_UNIT:

        #AST 직전까지
        if node is None:
            return ""
        elif node.semantic_parent and node.semantic_parent.kind == CursorKind.TRANSLATION_UNIT:
            return node.spelling
        elif CursorKind.PARM_DECL in [child_node.kind for child_node in node.get_children()]:   #아마도 메서드 정의
            return ClangCursor.get_src_name(node.semantic_parent) + "." + ClangCursor.get_method_sig(node)
        else:
            return ClangCursor.get_src_name(node.semantic_parent) + "." + node.displayname #display가 sig로 나오는듯

    @staticmethod
    def get_type_def_arg(node: clangCursor):
        result = "("
        for param_dec in node.get_arguments():
            # Identifier 제거
            result += ", " + ClangCursor.get_range_code(param_dec).replace(" " + param_dec.spelling, "")
        result += ")"
        return result.replace("(, ", "(")

    @staticmethod
    def get_method_sig(node):
        return node.spelling +ClangCursor.get_type_def_arg(node)



    def get_call_definition(self, target_stmt= ["CALL_EXPR", "MEMBER_REF_EXPR", "DECL_REF_EXPR", "UNEXPOSED_EXPR"]):
        """
        DFS로 target_stmt의 defintion node를 구한다.
        :param target_stmt:
        :return:
        """
        dec_list: ['Cursor'] = []
        queue = [self.node]

        while queue:
            node = queue.pop(0)
            stmt = node.kind.name
            if stmt in target_stmt:
                def_node = node.get_definition()
                if def_node:
                    new_cursor = get_cursor(def_node)
                    dec_list.append(new_cursor)
            queue[:0] = node.get_children()
        return dec_list

    def get_call_definition_map(self, target_stmt= ["CALL_EXPR", "MEMBER_REF_EXPR", "DECL_REF_EXPR", "UNEXPOSED_EXPR"])->dict[clangCursor, clangCursor]:
        """
        DFS로 target_stmt의 defintion node를 구한다.
        :param target_stmt:
        :return dec_dict: [call_node: clangCursor, def_node: clangCursor]
        """
        dec_dict: ['Cursor' 'Cursor'] = {}
        queue = [self.node]

        while queue:
            node = queue.pop(0)
            stmt = node.kind.name
            if stmt in target_stmt:
                def_node = node.get_definition()
                if def_node:
                    dec_dict[node] = def_node
            queue[:0] = node.get_children()
        return dec_dict

    @staticmethod
    def read_file(node) -> (str, int):
        """
        해당 노드의 파일 읽기. 우선순위도 함께 반환
        1. range 코드
        2. location Code
        3. unit path
        :return:
        """

        extent = node.extent
        start = extent.start
        end = extent.end

        mod = None
        while True:
            if start.file and end.file and start.file.name == end.file.name and not mod:
                mod = 1
                file_path = start.file.name
            elif node.location.file and mod != 2:
                mod = 2
                file_path = node.location.file.name
            elif mod != 3:
                mod = 3
                file_path = node.translation_unit.spelling
            else:
                assert True, "Read File Fail"
                return "Read File Fail", 0
            try:
                normalized_path = os.path.normpath(file_path)
                with open(normalized_path, 'r') as file:
                    return (file.read(), mod)
            except:
                error =normalized_path +" read Fail"
                return error, -1

    @staticmethod
    def get_range_code(node):
        """
        Returns the source code for the specific range including column information.
        """

        source_code, mod = ClangCursor.read_file(node)
        try:
            if mod == 1:
                extent = node.extent
                start = extent.start
                end = extent.end

                start_index = calculate_offset(source_code, start.line, start.column)
                end_index = calculate_offset(source_code, end.line, end.column)

                return source_code[start_index:end_index]
            else:
                # line = source_code.splitlines()[node.location.line-1]
                # return line[node.location.column-1:]
                return source_code

        except:
            print(mod)
            return "range read fail"

    @staticmethod
    def get_range_line_code(node):
        """
        Returns the entire lines of code from the start to the end line without considering the columns.
        """
        extent = node.extent
        start = extent.start
        end = extent.end

        assert start.file.name == end.file.name, "Start and end are in different files."

        with open(start.file.name, 'r') as file:
            lines = file.readlines()

            # Lines are 0-based in Python, adjust by -1 since Clang lines are 1-based
            return ''.join(lines[start.line - 1:end.line])
    @staticmethod
    def get_visit_line_map(root)->dict[int, list]:
        line_map = {}
        queue = [root]
        if root.location.file:
            base_file_path = root.location.file.name
        while queue:
            node = queue.pop(0)
            c = get_cursor(node)
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
            new_cursor = get_cursor(node)
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
            c = get_cursor(node)
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
            c = get_cursor(node)
            print(c.get_range_code())
            # Update the level indicator for child nodes
            new_lv = lv + "* "

            # Prepare child nodes to be added to the queue
            childs = [(child, new_lv) for child in node.get_children()]
            queue = childs + queue

    def visit_nodes(self)->[clangCursor]:
        visit_list: ['Cursor'] = []
        queue = [self.node]

        while queue:
            node = queue.pop(0)
            visit_list.append(node)
            queue[:0] = node.get_children()
        return visit_list


    def get_visit_unit_map(self) -> dict[TranslationUnit, list['Cursor']]:
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

    def print_node(self, node = None):
        if node:
            print(f"{node.kind}")
            #print(f"{self.get_range_code()}")
            print(f"display : {node.displayname}")
            print(f"spelling : {node.spelling}")
            print(f"{node.location}")
            print(f"{node.extent}")
        else:
            print(f"{self.node.kind}")
            print(f"{self.get_range_code()}")
            print(f"display : {self.node.displayname}")
            print(f"spelling : {self.node.spelling}")
            print(f"{self.node.location}")
            print(f"{self.node.extent}")

cursor_map ={}
def get_cursor(cursor)->ClangCursor:
    if isinstance(cursor, ClangCursor):
        assert (cursor_map[cursor.node] == cursor), "cursor map 오류"
        return cursor
    else:
        assert isinstance(cursor, clangCursor), f"타입 오류 {type(cursor)}"
        if cursor in cursor_map:
            return cursor_map[cursor]
        else:
            cursor_map[cursor] = ClangCursor.from_clang(cursor)
            return cursor_map[cursor]


if __name__ == "__main__":
    # with open(r"D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation\DSILibraryDrawer.cpp", 'r') as file:
    #     print(file.read())
    import clangParser.clangParser as Parser
    import time

    start_time = time.time()
    compliationunit = Parser.parsing(r"D:\dev\AutoPlanning\trunk\AP-6979-TimeTask\mod_APImplantSimulation\ActuatorHybridFixture.cpp")
    end_time = time.time()

    elapsed_time = end_time - start_time
    print("Parsing time:", elapsed_time, "seconds")

    mycursor = get_cursor(compliationunit.cursor)

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
