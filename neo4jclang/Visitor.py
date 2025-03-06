import time

from clangParser.clangParser import parse_project
from clangParser.datas.CUnit import CUnit, Cursor

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
        save_datas.append(cursor) #Cursor 저장
    print('save_datas : ', len(save_datas))
        # cursor_map[cursor] = ClangCursor.from_cursor(cursor)
        # save_datas.append(cursor_map[cursor]) #ClangCursor 저장



    db = Neo4jHandler("bolt://localhost:7687", "neo4j", "123456789")
    print('connect db')
    db.print_info()
    db.delete_all_nodes()

    # assert db.data2node(save_datas[1]) == db.data2node(save_datas[1]), 'unit not equal'

    
    #1. 유닛 자식들만 저장.
    db.save_data(save_datas)
    db.print_info()

    def search_test(search_datas):
        searches = db.search_node_map(search_datas)
        finds = 0
        for key, nodes in searches:
            if nodes:
                finds+=1
            else:
                print(key, 'not found')
        print('searchs : ', len(searches), 'finds : ', finds)
    search_test(save_datas)

    #for debug
    def visit_print(cursor: Cursor, depth=0):
        front = f"{' ' * depth}->({depth})"
        print(front, cursor.get_src_name())
        for child in cursor.get_children():
            visit_print(child, depth+1)


    save_datas = set()
    save_relations = set()
    def visit_data(cursor: Cursor):
        print(f'\rvisit_data : {len(save_datas)} rel : {len(save_relations)}', end='\t')
        for child in cursor.get_children():
            save_datas.add(child)
            save_relations.add((cursor, child, 'child'))

            #debug
            ###############################
            if child.extent.end.line - child.extent.start.line == 0 and child.extent.end.column - child.extent.start.column == 0:
                org_extent = child.node.extent
                sem_parent = child.node.semantic_parent
                lex_parent = child.node.lexical_parent

                org_extent_str = f'{org_extent.start.line}:{org_extent.start.column}~{org_extent.end.line}:{org_extent.end.column}'
                # print('zero extent : ', org_extent_str)


            ###########################
            if child.is_stmt and child.kind != 'UNEXPOSED_EXPR':
                visit_data(child)
            # if cursor.def_node:
            #     save_datas.add(cursor.def_node)
            #     save_relations.add((cursor, cursor.def_node, 'def_node'))

    #2. 관계 추가
    for cursor in unit.get_this_Cursor():
        save_relations.add((unit, cursor, 'child'))

        visit_data(cursor)
        # if cursor.def_node:
        #     save_datas.add(cursor.def_node)
        #     save_relations.add((cursor, cursor.def_node, 'def_node'))

    def check_visit_data():
        print("check visit Data")
        src_map = {}
        for data in save_datas:

            #for debug
            #########################
            import clangParser.clang_utill as ClangUtill

            sp = data.node.semantic_parent
            if sp:
                ClangUtill.get_src_name(sp)
            else:
                print('none parent : ', data.node.kind.name)
            #########################

            assert not data.get_src_name() in src_map, f'already exists : {data.get_src_name()} \n \
            {src_map[data.get_src_name()].get_range_str()} {data.get_range_str()}'
            src_map[data.get_src_name()] = data
        return src_map
    check_visit_data()

    st = time.time()
    db.save_data(list(save_datas))
    ed = time.time()
    print('save_data time : ', ed-st)

    st = time.time()
    db.add_relationship(data_list=list(save_relations))
    ed = time.time()
    print('add_relationship time : ', ed-st)


    db.print_info()




    


