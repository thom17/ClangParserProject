import clang.cindex

def find_call_expressions_and_definitions(tu):
    def recursive_node_search(node):
        print(f"{node.spelling} {node.kind} {node.location.line}")
        if node.kind == clang.cindex.CursorKind.CALL_EXPR:
            for child in node.get_children():
                if child.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
                    function_decl = child.get_definition() or child.get_declaration()
                    if function_decl:
                        print("Function call:", child.spelling)
                        print("Defined at:", function_decl.location.file, function_decl.location.line)
                        print("Function declaration:", function_decl.spelling)
        for child in node.get_children():
            recursive_node_search(child)

def main():
    clang.cindex.Config.set_library_file(r"C:\Program Files\LLVM\bin\libclang.dll")
    index = clang.cindex.Index.create()
    tu = index.parse("example.cpp")
    find_call_expressions_and_definitions(tu)

if __name__ == "__main__":
    main()
