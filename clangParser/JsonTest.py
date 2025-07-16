import json
import clang.cindex

from clang.cindex import CursorKind

target_kind = {CursorKind.CALL_EXPR,  CursorKind.UNEXPOSED_EXPR, CursorKind.CXX_METHOD}

def init_clang():
    # libclang 경로 설정
    clang.cindex.Config.set_library_file(r"C:\Program Files\LLVM\bin\libclang.dll")

def parse_to_json(source_file):
    index = clang.cindex.Index.create()
    tu = index.parse(source_file, args=['-x', 'c++', '-std=c++14'])

    # cursor = Cursor.Cursor(tu.cursor)
    # stmt_map = cursor.get_visit_stmt_map()
    # for i in stmt_map:
    #     print(f"{i} {stmt_map[i].__len__()}")

    print("has child ", list(tu.cursor.get_children()).__len__())
    parsed_data = [traverse_cursor(c) for c in tu.cursor.get_children() if is_relevant(c, source_file)]

    return json.dumps(parsed_data, indent=4)

def is_relevant(cursor, source_file):
    # 파일 위치 검사
    # if str(cursor.location.file) != source_file:
    if not str(cursor.location.file).__contains__("AutoPlanning"):
        return False
    # 관심 있는 cursor 종류 (예: 함수 정의)
    return cursor.kind in target_kind
    # return cursor.kind in {clang.cindex.CursorKind.FUNCTION_DECL, clang.cindex.CursorKind.CXX_METHOD}

def traverse_target_cursor(cursor):
    if cursor.kind in target_kind:
        result = {
            'kind': str(cursor.kind),
            'spelling': cursor.spelling,
            'location': str(cursor.location),
            'children': []
        }
        for c in cursor.get_children():
            child_result = traverse_cursor(c)
            if child_result:  # 데이터가 유효하면 추가
                result['children'].append(child_result)
        if result['children'] or cursor.kind in target_kind:  # 유효한 데이터가 있거나 중요 노드인 경우만 반환
            return result
    return None  # 불필요한 노드는 제외

def traverse_cursor(cursor):
    if cursor.kind:
        result = {
            'kind': str(cursor.kind),
            'spelling': cursor.spelling,
            'location': str(cursor.location),
            'children': []
        }
        for c in cursor.get_children():
            child_result = traverse_cursor(c)
            if child_result:  # 데이터가 유효하면 추가
                result['children'].append(child_result)
                return result
    return None  # 불필요한 노드는 제외


if __name__ == "__main__":
    # 사용 예시
    init_clang()
    json_output = parse_to_json(r"D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation\ActuatorHybridFixture.cpp")
    print(json_output)
