import clang.cindex


def calculate_complexity(node, complexity=1):
    """재귀적으로 AST 노드를 순회하며 복잡도를 계산"""
    kind = node.kind
    # 결정 노드를 확인하고 복잡도를 증가
    if kind in [clang.cindex.CursorKind.IF_STMT, clang.cindex.CursorKind.FOR_STMT,
                clang.cindex.CursorKind.WHILE_STMT, clang.cindex.CursorKind.DO_STMT,
                clang.cindex.CursorKind.CASE_STMT]:
        complexity += 1

    # 자식 노드를 순회
    for child in node.get_children():
        complexity = calculate_complexity(child, complexity)
    return complexity


def analyze_function_complexity(source_file):
    index = clang.cindex.Index.create()
    tu = index.parse(source_file)
    complexities = {}

    # 함수 정의 노드 찾기
    for node in tu.cursor.get_children():
        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            func_name = node.spelling
            complexities[func_name] = calculate_complexity(node)

    return complexities


# 파일 분석
source_file = 'example.c'
complexities = analyze_function_complexity(source_file)
print(complexities)
