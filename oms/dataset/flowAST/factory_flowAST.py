from oms.dataset.flowAST.flowAST import FlowAST, IfFlowInfo, WhileFlowInfo, ForFlowInfo
from clangParser.datas.Cursor import Cursor
from typing import List

def from_cursor(cursor: Cursor, flow_ast: FlowAST = None) -> FlowAST:
    if flow_ast is None:
        flow_ast = FlowAST()
    flow_ast.kind = cursor.kind
    flow_ast.line = cursor.location.line
    flow_ast.column = cursor.location.column
    flow_ast.end_line = cursor.extent.end.line
    flow_ast.end_column = cursor.extent.end.column
    flow_ast.code = cursor.get_range_code()
    return flow_ast



class CursorVisitor:
    '''
    Cursor를 FlowAST로 변환하는 방법을 정의하는 클래스
    추후 파싱하는 깊이나 연결 구조가 변경될 수 있으니 일단 CursorFlowASTFactory 와 분리
    시작과 종료인 빈 FlowAST를 생성하고 방문한 노드에 따라 해당 노드를 변경 및 교체
    '''
    SKIP_TYPE = ['COMPOUND_STMT', 'CXX_METHOD'] # FlowAST로 생성하지 않는 cursor
    BRANCH_TYPE = ['IF_STMT', 'WHILE_STMT', 'FOR_STMT'] #마찬가지로 생성하진 않지만 next

    def __init__(self, cursor: Cursor):
        assert cursor.is_definition(), '이 visitor는 definition으로 출발'
        self.cursor2node = {}
        self.source_cursor = cursor
        self.head_node = FlowAST() #커서 관련 정의의를 헤드로 할까...?
        
        current_node = FlowAST()
        self.head_node.set_next_flow(current_node)

        visit_que = [ch for ch in cursor.get_children()]
        self.visit(current_flowAST=current_node, visit_que_cursor=visit_que)

    def is_visit_type(self, cursor: Cursor) -> bool:
        '''
        visit이 필요한 노드인 경우만 판단하는 함수.
        
        '''
        return cursor.kind in self.SKIP_TYPE or cursor.kind in self.BRANCH_TYPE
    
    def is_brach_type(self, cursor: Cursor) -> bool:
        return cursor.kind in self.BRANCH_TYPE


    def visit(self, current_flowAST: FlowAST, visit_que_cursor: List[Cursor])->FlowAST:
        '''
        cursor chid를 방문하면서 FlowAST를 갱신하는 재귀 함수
        마지막FlowAST를 반환
        '''
        
        def visit_ifstmt(if_stmt_cursor: Cursor):
            childs = if_stmt_cursor.get_children()
            condition_cursor = childs[0]
            then_cursor = childs[1]
            else_cursor = childs[2] if len(childs) == 3 else None

            from_cursor(cursor=if_stmt_cursor, flow_ast=current_flowAST)
            self.cursor2node[if_stmt_cursor] = current_flowAST

            extended_info = IfFlowInfo(current_flowAST)
            extended_info.condition = from_cursor(condition_cursor)
            self.cursor2node[condition_cursor] = extended_info.condition
            
            #if then 연결
            then_flow = FlowAST()
            current_flowAST.set_next_flow(then_flow)
            then_end_node = self.visit(current_flowAST=then_flow, visit_que_cursor=[then_cursor]) # 기존 que 이전에 if 내부 먼저 처리

            else_flow = FlowAST()
            extended_info.else_flow = else_flow

            #else는 없을 수도 있음
            if else_cursor is not None:
                else_end_node = self.visit(current_flowAST=else_flow, visit_que_cursor=[else_cursor])
                else_end_node.set_next_flow(then_end_node) #else 끝에 then의 끝(공백) 연결
                else_flow = else_end_node
            
            else_flow.set_next_flow(then_end_node) #else가 없을 경우 then의 끝(공백) 연결

            return then_end_node
        
        def visit_whilestmt(while_stmt_cursor: Cursor):
            childs = while_stmt_cursor.get_children()
            if while_stmt_cursor.kind == 'DO_STMT':
                condition_cursor = childs[1]
                body_cursor = childs[0]

            elif while_stmt_cursor.kind == 'WHILE_STMT':
                condition_cursor = childs[0]
                body_cursor = childs[1]
            else:
                assert False, 'while 혹은 do while 문이 아닙니다.'

            from_cursor(cursor=while_stmt_cursor, flow_ast=current_flowAST)
            self.cursor2node[while_stmt_cursor] = current_flowAST

            extended_info = WhileFlowInfo(current_flowAST)
            extended_info.condition = from_cursor(condition_cursor)
            self.cursor2node[condition_cursor] = extended_info.condition
            extended_info.else_flow = FlowAST()

            body_flow = FlowAST()
            current_flowAST.set_next_flow(body_flow)
            body_end_node = self.visit(current_flowAST=body_flow, visit_que_cursor=[body_cursor])
            extended_info.else_flow.set_next_flow(body_end_node)

            return body_end_node
        
        def visit_forstmt(for_stmt_cursor: Cursor):
            assert for_stmt_cursor.kind == 'FOR_STMT', 'for문이 아닙니다.'
            childs = for_stmt_cursor.get_children()

            condition_cursor = childs[0]
            body_cursor = childs[1]
            end_cursor = childs[2]

            from_cursor(cursor=for_stmt_cursor, flow_ast=current_flowAST)
            self.cursor2node[for_stmt_cursor] = current_flowAST

            #조건 부분
            extended_info = ForFlowInfo(current_flowAST)
            extended_info.condition = from_cursor(condition_cursor)
            self.cursor2node[condition_cursor] = extended_info.condition
            extended_info.else_flow = FlowAST()

            #종료 부분
            end_flow = from_cursor(cursor=end_cursor)
            self.cursor2node[end_cursor] = end_flow

            #body 부분            
            body_flow = FlowAST()
            current_flowAST.set_next_flow(body_flow)
            body_end_node = self.visit(current_flowAST=body_flow, visit_que_cursor=[body_cursor])
            
            #for end와 else 연결
            body_end_node.set_next_flow(end_flow)
            end_flow.set_next_flow(extended_info.else_flow) 
            
            return extended_info.else_flow
        
        new_node = None
        if visit_que_cursor:
            cursor = visit_que_cursor.pop(0)

            if cursor.kind == 'IF_STMT':
                new_node = visit_ifstmt(cursor)
            elif cursor.kind in ['WHILE_STMT', 'DO_STMT']:
                new_node = visit_whilestmt(cursor)
            elif cursor.kind == 'FOR_STMT':
                new_node = visit_forstmt(cursor)
            elif self.is_visit_type(cursor):
                visit_que_cursor = cursor.get_children() + visit_que_cursor
            else:
                from_cursor(cursor=cursor, flow_ast=current_flowAST)
                self.cursor2node[cursor] = current_flowAST
                new_node = FlowAST()
                current_flowAST.set_next_flow(new_node)
            
            
        if new_node:
            return self.visit(current_flowAST=new_node, visit_que_cursor=visit_que_cursor)
        elif visit_que_cursor:
            return self.visit(current_flowAST=current_flowAST, visit_que_cursor=visit_que_cursor)
        else:
            return current_flowAST

        



class CursorFlowASTFactory:
    '''
    skip_by_cursor_type: List[str] FlowAST로 생성하지 않는 cursor
    '''
    def __init__(self):
        self.skip_cursor_type = ['COMPOUND_STMT', 'CXX_METHOD'] # FlowAST로 생성하지 않는 cursor
        self.branch_cursor = ['IF_STMT', 'WHILE_STMT', 'FOR_STMT'] #마찬가지로 생성하진 않지만 next에 활용

    def is_visit_type(self, cursor: Cursor) -> bool:
        '''
        visit이 필요한 노드인 경우만 판단하는 함수.
        
        '''
        return cursor.kind in self.skip_cursor_type or cursor.kind in self.branch_cursor

    def is_branch_type(self, cursor: Cursor) -> bool:
        return cursor.kind in self.branch_cursor

    # def make_ast(self, cursor: Cursor) -> FlowAST:

    #     head_node = None
    #     cursor2node = {}

    #     def visit(self, cursor: Cursor) -> FlowAST:
    #         if cursor.kind in self.branch_cursor:
                
                

    #         if self.is_visit_type(cursor):
    #             return None
    #         return self.from_cursor(cursor)



    #     if self.is_visit_type(cursor):
    #         cursor2node[cursor] = from_cursor(cursor)
    #         self.visit(cursor, cursor2node, cursor2node[cursor])
    #     else:



    @staticmethod
    def from_cursor(cursor: Cursor) -> FlowAST:
        flow_ast = FlowAST()
        flow_ast.kind = cursor.kind
        flow_ast.line = cursor.location.line
        flow_ast.column = cursor.location.column
        flow_ast.end_line = cursor.extent.end.line
        flow_ast.end_column = cursor.extent.end.column
        flow_ast.code = cursor.get_range_code()
        return flow_ast


