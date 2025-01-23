from clangParser.clangParser import parse_project
from clangParser.CUnit import CUnit, Cursor

from neo4jclang.ClangCursor import ClangCursor

from typing import Dict

import sys
sys.path.append(r'D:\dev\python_pure_projects\PyUtil')


from neo4j_manager.neo4jHandler import Neo4jHandler

def visit_unit_to_db(unit: CUnit):
    '''
    2025-01-17
    unit 입력받고 자식들을 순회하며 DB에 저장하는 함수
    1. unit to db
    2. child to db
    3. add relationship
    '''

    cursor_map: Dict[Cursor, ClangCursor] = {}

    save_datas = [unit]
    for child in unit.this_file_nodes:
        cursor = Cursor(child, source_code=unit.code)
        cursor_map[cursor] = ClangCursor.from_cursor(cursor)
        save_datas.append(cursor_map[cursor])

    print('save_datas : ', len(save_datas))

    db = Neo4jHandler("bolt://localhost:7687", "neo4j", "123456789")
    print('connect db')
    db.print_info()
    db.delete_all_nodes()
    db.save_data(save_datas)
    db.print_info()


    searchs = db.search_node_map(save_datas)
    finds = 0
    for key, nodes in searchs:
        if nodes:
            finds+=1
    print('clang searchs : ', len(searchs), 'finds : ', finds)

    searchs = db.search_node_map(cursor_map.keys())
    finds = 0
    for key, nodes in searchs:
        if nodes:
            finds+=1
    print('cursor searchs : ', len(cursor_map.keys()), 'finds : ', finds)


    print(len(save_datas), " -> ", finds)
    # Neo4jHandler.save_data(save_datas)

