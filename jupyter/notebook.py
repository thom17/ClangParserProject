import clang
from clangParser.clangParser import parsing, parse_project

tus = parse_project("temp.cpp")
tu :clang.cindex.TranslationUnit= tus[0]

tu.__str__()
print(tu.spelling)
