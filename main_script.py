import sys
from snResult.ClangAST import *
from clangParser.datas.Cursor import Cursor
import clangParser.clangParser as Parser

def print_all():
    """데이터베이스의 모든 AST 데이터를 출력"""
    db_path = 'snResult/dataset.db'
    sn_result = get_all_table(db_path)
    for ast_set in sn_result:
        print(ast_set.srcSig)
        print_a_line(ast_set, 10)

def table2cursor(ast_set: TClangAST) -> Cursor:
    """AST 테이블 데이터를 Cursor 객체로 변환"""
    tunit = Parser.parse_context(ast_set.sourceCode)
    return Cursor(tunit.cursor)

def print_line(ast_set):
    """AST 데이터의 모든 라인을 출력"""
    cursor = table2cursor(ast_set)
    line_map = cursor.get_visit_line_map()
    for num in sorted(line_map):
        print(num, end=" ")
        for c in line_map[num]:
            print(f"<{c.kind} {c.spelling} {c.get_range()}>", end=" ")
        print()

def print_a_line(ast_set, line_num: int):
    """AST 데이터의 특정 라인을 출력"""
    cursor = table2cursor(ast_set)
    line_map = cursor.get_visit_line_map()
    if line_num not in line_map:
        return "None"
    print(line_num, end=" ")
    for c in line_map[line_num]:
        print(f"<{c.kind} {c.spelling} {c.get_range()}>", end=" ")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_all()

