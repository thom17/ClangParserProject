from clang.cindex import Cursor as clangCursor
from clang.cindex import Token, CursorKind, TokenKind

from collections import defaultdict

def to_clang(cursor:'Cursor') -> clangCursor:
    if isinstance(cursor, 'Cursor'):
        return cursor.node
    else:
        assert isinstance(cursor, clangCursor)
        return cursor


def get_stmt_map(cursor_list: [clangCursor]) -> [str, [clangCursor]]:
    result_map = defaultdict(list)
    for node in cursor_list:
        # node = to_clang(node)
        result_map[node.kind.name].append(node)

    return result_map


def get_file_map(cursor_list: [clangCursor]) -> [str, [clangCursor]]:
    result_map = defaultdict(list)
    for node in cursor_list:
        # node = to_clang(node)
        file_path = None
        if node.location.file:
            file_path=node.location.file.name
        result_map[file_path].append(node)

    return result_map


def get_src_name(node: clangCursor):
    kind: CursorKind = node.kind
    def_node = node.get_definition()
    if kind.is_declaration():
        name = __get_def_name(node)
    else:
        name = __get_exp_name(node)

    if __is_root_node(node):
        return name
    else:
        return get_src_name(node.semantic_parent) + "." + name


def __is_root_node(node: clangCursor):
    parent = node.semantic_parent
    if parent is None or parent.kind == CursorKind.TRANSLATION_UNIT:
        return True
    else:
        return False


def __get_exp_name(node: clangCursor):
    # 연산과 관련된 식
    return node.kind.name+"(" + node.spelling + "):" + str(node.location.line)


def __get_def_name(node: clangCursor):
    # 메서드의 경우
    if node.kind.name in ["CXX_METHOD", "CONSTRUCTOR", "DESTRUCTOR", "FUNCTION_DECL"]:
        return node.spelling + __get_argument_sig(node)
    # 단순한 타입의 경우 (변수)
    else:
        return node.spelling


def __get_argument_sig(node: clangCursor):
    result_sig = ""
    for dec_node in node.get_arguments():
        # dec_oms = CursorOMS(dec_node)
        # dec_code = dec_oms.get_range_code()

        parm_sig = __get_param_sig_by_token(dec_node)
        result_sig += ", " + parm_sig

    if result_sig:
        return "(" + result_sig[2:] + ")"
    else:
        return "()"


def __get_param_sig_by_token(node: clangCursor):
    """
    token을 사용하여 PARM_DECL 하나의 시그니쳐를 구함.
    blabla type id (= blabla )에서 ()를 날림.
    """
    assert node.kind == CursorKind.PARM_DECL, f"파라미터 이름을 구하는 용도. {node.kind} 입력됨"
    result = ""
    last_token_type = TokenKind.PUNCTUATION
    for token in node.get_tokens():
        token: Token
        if token.kind != TokenKind.PUNCTUATION:
            if token.spelling == node.spelling:  # 종료 지점 찾음. 타입 정보만 필요함
                break
            elif last_token_type == TokenKind.PUNCTUATION:  #:: < & * 와 같은 기호들은 붙여서 출력
                result += token.spelling
            else:  # 그 외는 한칸 공백
                result += " " + token.spelling
        else:  # 식별자가 아니라면 그냥 더한다.
            result += token.spelling

        last_token_type = token.kind  # 공백 여부를 위해 아무튼 마지막 토큰 타입 저장
    return result
