import clang.cindex

class SimpleVisitor:
    def __init__(self, node, base_path: str):
        self.node: clang.cindex.Cursor = node
        self.base_path: str = base_path
        self.base_path_cpp: str = base_path.replace(".cpp", ".h")
        self.base_path_h: str = base_path.replace(".h", ".cpp")
        self.location: clang.cindex.SourceLocation = self.node.location
        self.child_node = self.node.get_children()

    def get_source_code(self):
        file = self.location.file
        if file:
            file_path: str = file.name
        else:
            file_path = self.base_path
        with open(file_path, 'r') as file:
            return file.read()

    def make_comment_code(self, code: str = None):
        if code is None:
            code = self.get_source_code()

        code2list = code.splitlines()
        line = self.location.line
        # 현재 노드에 대한 주석 추가
        try:
            code2list[line - 1] += f" // {self.node.kind.name}({self.node.spelling})"
        except:
            print(f"line={line} size = {code2list.__len__()}")
        code = '\n'.join(code2list)

        # 모든 자식 노드에 대해 재귀적으로 처리
        for child in self.node.get_children():
            child_visitor = SimpleVisitor(child, self.base_path)
            code = child_visitor.make_comment_code(code)

        return code

    def compare_spelling_display(self):
        if self.node.spelling != self.node.displayname:
            print(f"{node.kind}: spelling='{node.spelling}', displayname='{node.displayname}', location={node.location.file}:{node.location.line}:{node.location.column}")
        for chid_node in self.node.get_children():
            visitor = SimpleVisitor(chid_node, self.base_path)
            visitor.compare_spelling_display()


    def is_base_file(self):
        """
        재귀에서 node와 str을 입력 받음
        node 자체는 경로가 원래 상위의 경로가 아니니까
        :return:
        """
        location: clang.cindex.SourceLocation = self.node.location
        file: clang.cindex.File = location.file

        parsing_file_path: str = file.__str__()
        return parsing_file_path.__contains__(self.base_path) and parsing_file_path


    def visit(self):
        spelling = self.node.spelling
        location: clang.cindex.SourceLocation = self.node.location
        file: clang.cindex.File = location.file

        # print(f"node.base_path = {self.base_path}")

        parsing_file_path: str = file.__str__()
        # print("path : ", parsing_file_path)
        # is_need_print = self.is_base_file()
        is_need_print = True
        # print("->", is_need_print)
        if spelling and is_need_print:
            # self.node.kind의 이름을 출력하도록 수정
            print(f"Node found: {spelling} ({self.node.kind.name})")
            print(f"Node : {self.node}")
            print(f"Location : {location}")
            print(f"File : {file}")
            print()

        # 자식 노드에 대해 방문을 재귀적으로 진행
        for child in self.node.get_children():
            visitor = SimpleVisitor(child, self.base_path)
            visitor.visit()


    def for_make_file_map(self, map=dict()):
        spelling = self.node.spelling
        location: clang.cindex.SourceLocation = self.node.location
        file: clang.cindex.File = location.file
        str_file = file.__str__()
        if str_file in map:
            map[str_file].append(self.node)
        else:
            map[str_file] = [self.node]

        # 자식 노드에 대해 방문을 재귀적으로 진행
        for child in self.node.get_children():
            visitor = SimpleVisitor(child, self.base_path)
            visitor.for_make_file_map(map)

    def for_make_stmt_map(self, map):
        try:
            kind = self.node.kind
            if kind in map:
                map[kind].append(self.node)
            else:
                map[kind] = [self.node]

            for child in self.node.get_children():
                visitor = SimpleVisitor(child, self.base_path)
                visitor.for_make_stmt_map(map)

        except ValueError as e:
            print(f"Skipping node with unknown CursorKind: {e}")


    def for_make__map(self, map=dict()):
        spelling = self.node.spelling
        location: clang.cindex.SourceLocation = self.node.location
        file: clang.cindex.File = location.file
        str_file = file.__str__()
        if str_file in map:
            map[str_file].append(self.node)
        else:
            map[str_file] = [self.node]

        # 자식 노드에 대해 방문을 재귀적으로 진행
        for child in self.node.get_children():
            visitor = SimpleVisitor(child, self.base_path)
            visitor.for_make_file_map(map)


    def visit_for_location(self):
        # print(type(self.node))
        spelling = self.node.spelling
        location: clang.cindex.SourceLocation = self.node.location
        file = location.file
        print("file : ", type(file), " = ", file)

        print(f"{type(location)} = {location}")
        tokens = self.node.get_tokens()
        print(tokens)

        if spelling:  # 노드 이름이 있는 경우에만 출력
            location = self.node.location
            line = location.line
            column = location.column
            print(f"Node found: {spelling} ({self.node.kind.name}) at Line: {line}, Column: {column}")

        # 자식 노드에 대해 방문을 재귀적으로 진행
        for child in self.node.get_children():
            visitor = SimpleVisitor(child)
            visitor.visit_for_location()




if __name__ == "__main__":
    def read_specific_column(filename, line_number, column_index):
        try:
            with open(filename, 'r') as file:
                for current_line_number, line in enumerate(file, start=1):
                    if current_line_number == line_number:
                        if column_index <= len(line):
                            return line[:column_index - 1] + "->" + line[column_index - 1:]
                        else:
                            return "Error: The line does not have enough columns."
                return "Error: Line number out of range."
        except FileNotFoundError:
            return "Error: File not found."
        except Exception as e:
            return f"Error: {str(e)}"


    import clangParser as Parser

    # folder_path = r"../test"
    # tus = Parser.parse_project(folder_path)
    #
    # # 결과 처리 및 출력
    # for tu in tus:
    #     print(tu.spelling, "contains", len(list(tu.cursor.get_children())), "elements")
    #
    # print()
    # target = tus[2]

    target:clang.cindex.TranslationUnit = Parser.parsing(r"../test/onupdate.cpp")

    target_cursor:clang.cindex.Cursor  = target.cursor

    for child in target_cursor.get_children():
        if child.kind.name == "CXX_METHOD" and child.spelling == "OnUpdate" or child.kind.name == "FUNCTION_DECL":
            update_node:clang.cindex.Cursor = child
            break
    update_visitor = SimpleVisitor(update_node, update_node.location.file.name)

    childs = list(update_node.get_children())
    print(len(childs))

    stmt_map={}
    update_visitor.for_make_stmt_map(stmt_map)
    for stmt_key in stmt_map:
        print(f"{stmt_key} : {stmt_map.__len__()}")


    clang.cindex.CursorKind
    root_node: clang.cindex.Cursor = target.cursor

    other_file_nodes = []
    nodes = []

    for node in root_node.get_children():
        node_file: clang.cindex.File = node.location.file

        if node_file and node_file.name == target.spelling:
            nodes.append(node)
        else:
            other_file_nodes.append(node)

    for node in nodes:
        print(f"Node found: {node.spelling} ({node.kind.name})")
        print(f"Location : {node.location}")

    print(f"other size : {other_file_nodes.__len__()} size : {nodes.__len__()}")

    code = None
    for node in nodes:
        simpleVisit = SimpleVisitor(node, target.location.file.name)
        code = simpleVisit.make_comment_code(code)

    print(code)

    # 많이 나온다.. 파일 필터링은 필수.
    # for node in other_file_nodes:
    #     if node.kind == clang.cindex.CursorKind.CXX_METHOD or node.kind == clang.cindex.CursorKind.CONSTRUCTOR:
    #         print(f"Node found: {node.spelling} ({node.kind.name})")
    #         print(f"Location : {node.location}")






    print("target :->", target.spelling)
    print()

    simpleVisit = SimpleVisitor(target.cursor, target.spelling)
    # simpleVisit.visit()
    dataMap:dict[str, list[clang.cindex.Cursor]] = {}

    source_code = simpleVisit.get_source_code()

    print(source_code)
    print("========")

    source_code = simpleVisit.make_comment_code()
    print(source_code)

    cpp_list = []
    simpleVisit.for_make_file_map(dataMap)
    for key in dataMap:
        print(f"{key} : {dataMap[key].__len__()}")
        if key.__contains__(".cpp"):
            cpp_list.append((key, dataMap[key]))

    print("=================")

    for key, data in cpp_list:
        print(f"{key} : {data.__len__()}")
        for node in data:
            location: clang.cindex.SourceLocation = node.location
            source = read_specific_column(key, location.line, location.column)
            print("=================")
            print(f"{source}[{location.line}:{location.column}]{node.spelling} {node.kind}" )
            print("=================")

    stmt_map = {}
    simpleVisit.for_make_stmt_map(stmt_map)

    for stmt in stmt_map:
        print(f"{stmt.name} {stmt_map[stmt].__len__()}")

    for node in stmt_map[clang.cindex.CursorKind.CALL_EXPR]:
        location: clang.cindex.SourceLocation = node.location

        file_name: str = location.file.name
        if file_name.__contains__(target.spelling):
            source = read_specific_column(location.file.name, location.line, location.column)
            print("=================")
            print(f"{source}[{location.line}:{location.column}]{node.spelling} {node.kind}")




