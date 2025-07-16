import sys
from snResult.ClangAST import *
from clangParser.datas.Cursor import Cursor
import clangParser.clangParser as Parser

def print_all():
    dbPath = 'snResult/dataset.db'
    snResult: [TClangAST] = get_all_table(dbPath)
    for ast_set in snResult:
        print(ast_set.srcSig)
        print_a_line(ast_set, 10)

def table2cursor(ast_set:TClangAST):
    tunit = Parser.parse_context(ast_set.sourceCode)
    return Cursor(tunit.cursor)

def print_line(ast_set):
    cursor = table2cursor(ast_set)
    line_map = cursor.get_visit_line_map()
    for num in sorted(line_map):
        print(num, end=" ")
        for c in line_map[num]:
            print(f"<{c.kind} {c.spelling} {c.get_range()}>", end=" ")
        print()

def print_a_line(ast_set, line_num):
    cursor = table2cursor(ast_set)
    line_map = cursor.get_visit_line_map()
    if line_num not in line_map:
        return "None"
    print(line_num, end=" ")
    for c in line_map[line_num]:
        print(f"<{c.kind} {c.spelling} {c.get_range()}>", end=" ")



if __name__ == "__main__":

    arg_length = sys.argv.__len__()
    if arg_length == 1:
        print_all()

