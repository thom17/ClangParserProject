'''
Claude 3.7 sonnet을 사용하여 생성한 코드.
 if문 extended_info 에 대한 정보는 그리지 않음.
'''
from typing import Dict, Set
import graphviz
from oms.dataset.flowAST.flowAST import FlowAST, FlowInfo, IfFlowInfo

class FlowASTVisualizer:
    def __init__(self):
        self.graph = graphviz.Digraph('FlowAST', format='png')
        self.graph.attr('node', shape='box')
        self.visited_nodes: Set[int] = set()
        self.node_attributes: Dict[int, Dict] = {}

    def add_node(self, ast_node: FlowAST) -> str:
        """그래프에 노드를 추가하고 노드 ID를 반환합니다."""
        node_id = str(id(ast_node))

        if id(ast_node) not in self.visited_nodes:
            self.visited_nodes.add(id(ast_node))

            # 노드 레이블 생성
            label = f"{ast_node.kind if ast_node.kind else 'Unknown'}"
            if ast_node.code:
                # 문자열이 너무 길면 자르기
                code_snippet = ast_node.code[:50] + "..." if len(ast_node.code) > 50 else ast_node.code
                label += f"\n{code_snippet}"

            # 위치 정보 추가
            if ast_node.line is not None:
                label += f"\nLine: {ast_node.line}"

            # 노드에 특별한 스타일 적용
            attrs = {'label': label}

            # 특정 노드 타입에 따라 색상 지정
            if ast_node.kind in ['if', 'IF_STMT']:
                attrs['color'] = 'blue'
            elif ast_node.kind in ['while', 'WHILE_STMT', 'for', 'FOR_STMT']:
                attrs['color'] = 'green'
            elif ast_node.kind == 'return':
                attrs['color'] = 'red'

            self.graph.node(node_id, **attrs)

        return node_id

    def visualize(self, ast: FlowAST, output_file: str = "flow_ast"):
        """FlowAST를 그래프로 시각화합니다."""
        self._build_graph(ast)
        self.graph.render(output_file, view=True)

    def _build_graph(self, ast: FlowAST):
        """재귀적으로 AST를 그래프로 구축합니다."""
        if ast is None:
            return

        node_id = self.add_node(ast)

        # 확장 정보 처리
        if ast.extended_info:
            self._handle_extended_info(ast, node_id)

        # 다음 흐름으로의 연결 추가
        if ast.next_flow:
            next_id = self.add_node(ast.next_flow)
            self.graph.edge(node_id, next_id, color='black')
            self._build_graph(ast.next_flow)

    def _handle_extended_info(self, ast: FlowAST, node_id: str):
        """확장 정보(extended_info)를 시각화합니다."""
        # If 문 처리
        if isinstance(ast.extended_info, IfFlowInfo):
            if_info = ast.extended_info

            # 조건문 시각화
            if if_info.condition:
                cond_id = self.add_node(if_info.condition)
                self.graph.edge(node_id, cond_id, label='condition', color='blue', style='dashed')
                self._build_graph(if_info.condition)

            # else 흐름 시각화
            if if_info.else_flow:
                else_id = self.add_node(if_info.else_flow)
                self.graph.edge(node_id, else_id, label='else', color='red', style='dashed')
                self._build_graph(if_info.else_flow)

def visualize_flow_ast(ast: FlowAST, output_file: str = "flow_ast"):
    """FlowAST를 시각화하는 편의 함수"""
    visualizer = FlowASTVisualizer()
    visualizer.visualize(ast, output_file)


# 사용 예시
if __name__ == "__main__":
    # 테스트 FlowAST 생성
    root = FlowAST()
    root.kind = "function"
    root.code = "void example() { ... }"
    root.line = 1

    if_node = FlowAST()
    if_node.kind = "if"
    if_node.code = "if (x > 0)"
    if_node.line = 2

    if_info = IfFlowInfo(if_node)

    condition = FlowAST()
    condition.kind = "condition"
    condition.code = "x > 0"
    condition.line = 2
    if_info.condition = condition

    then_block = FlowAST()
    then_block.kind = "statement"
    then_block.code = "return x;"
    then_block.line = 3

    else_block = FlowAST()
    else_block.kind = "statement"
    else_block.code = "return 0;"
    else_block.line = 5
    if_info.else_flow = else_block

    # 흐름 연결
    root.set_next_flow(if_node)
    if_node.set_next_flow(then_block)

    # 시각화
    visualize_flow_ast(root, "example_flow")