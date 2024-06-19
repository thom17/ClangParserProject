import clang.cindex
from clang.cindex import Cursor as clangCursor
if __name__ == "__main__":
    from Cursor import Cursor

else:
    from .Cursor import Cursor


class CursorOMS(Cursor):
    """
    OMS 측과 확장하기 위해 사용한다.
    가능하면 clang.cindex 쪽은 접근하지 말자.
    ->Cursor로 해결하기
    """
    cursor_map: [clangCursor, 'CursorOMS'] = {}
    @staticmethod
    def GetCursorOMS(cursor)->'CursorOMS':
        if isinstance(cursor, Cursor):  # Cursor 또는 CursorOMS
            assert (CursorOMS.cursor_map[cursor.node] == cursor), "cursor map 오류"
            return cursor
        else:
            assert isinstance(cursor, clangCursor), f"타입 오류 {type(cursor)}"
            if cursor in CursorOMS.cursor_map:
                return CursorOMS.cursor_map[cursor]
            else:
                CursorOMS.cursor_map[cursor] = CursorOMS(cursor)
                return CursorOMS.cursor_map[cursor]

    #너무 복잡하다.. 그냥 무조건 cursor를 받고 생성
    def __init__(self, node: clangCursor):
        assert isinstance(node, clangCursor)
        super().__init__(node)

        #겁나 많이 나온다. (약 122665)
        target_stmt = []
        for kind in clang.cindex.CursorKind.get_all_kinds():
            target_stmt.append(kind.name)
            # if kind.name.__contains__("EXPR"):
            #     target_stmt.append(kind.name)
        dec_list = self.get_call_definition(target_stmt)
        #print(target_stmt)

        #print(dec_list.__len__())
        dec_set = set(dec_list)
        # print(dec_set.__len__())

        self.call_nodes = dec_set
        #has는 나중에 Cursor 측에서 vist_node 추가하자. (def 관련 필터링해서)
        # self.has_nodes: [clangCursor] = set()
        # for node in self.visit_nodes():
        #     if node.kind ==
        #         self.has_nodes.add(node)
        self.has_nodes: [clangCursor] = []
        def_map = self.get_visit_def_map()
        for src_name in def_map:
            self.has_nodes.append(def_map[src_name])
            
    def to_clangCursor(self, cursor=None):
        if cursor is None:
            return self.node
        elif isinstance(cursor, Cursor):
            return cursor.node
        else:
            assert isinstance(cursor, clangCursor), f"Cursor 관련 클래스가 입력으로 들어오지 않음 {type(cursor)}"
            return cursor
    

    def to_dict(self):
        result = {}
        result['node'] = super().to_dict()
        result['call'] =[ Cursor.get_src_name(node) for node in self.call_nodes]
        return result




if __name__ == "__main__":
    # with open(r"D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation\DSILibraryDrawer.cpp", 'r') as file:
    #     print(file.read())
    import clangParser
    import time

    from CUnit import CUnit

    start_time = time.time()
    compliationunit = clangParser.parsing(r"D:\dev\AutoPlanning\trunk\AP-6979-TimeTask\mod_APImplantSimulation\ToolBarFixture.cpp")
    end_time = time.time()

    elapsed_time = end_time - start_time
    print("Parsing time:", elapsed_time, "seconds")

    myunit = CUnit(compliationunit)
    id = 0
    for node in myunit.this_file_nodes:
        print(f"{id} : {node.displayname}" , end=" ")
        id += 1
        oms = CursorOMS.GetCursorOMS(node)

    target_node = myunit.this_file_nodes[105]
    oms = CursorOMS.GetCursorOMS(target_node)

    for node in oms.call_nodes:
        print()
        Cursor.print_node(node)
    print("###############"*5)
    type_map = oms.get_visit_stmt_map()
    for type_name in type_map:

        print(f"{'*'*10} {type_name}")
        for node in type_map[type_name]:
            if node in oms.call_nodes:
                print(f"얘가 아마도 has {Cursor.print_node(node)}")

    mydict = oms.to_dict()
    print(type(mydict))
    for key in mydict:
        print(key, " ", mydict[key])
    print(mydict['call'])

    oms.visit_print()