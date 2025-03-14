from typing import Optional, List
from oms.dataset.function_info import FunctionInfo





class FlowAST:
    def __init__(self):
        self.kind: Optional[str] = None
        self.line: Optional[int] = None
        self.column: Optional[int] = None
        self.end_line: Optional[int] = None
        self.end_column: Optional[int] = None

        self.code: Optional[str] = None
        self.parents: List['FlowAST'] = []

        self.next_flow: Optional['FlowAST'] = None

        self.extended_info: Optional['FlowAST'] = None

    def set_next_flow(self, next_flow: 'FlowAST'):
        assert next_flow is not None, "next_flow cannot be None"
        self.next_flow = next_flow
        if next_flow:
            next_flow.parents.append(self)

    def set_parent(self, parents: List['FlowAST']):
        self.parents = parents
        for parent in parents:
            parent.next_flow = self

class IfFlowInfo:
    def __init__(self, flowAST: FlowAST):
        self.flowAST = flowAST
        flowAST.extended_info = self
    
        self.condition: Optional[FlowAST] = None
        self.else_flow: Optional[FlowAST] = None



if __name__ == "__main__":
    di = {}
    print(None in di)


    pass
    # print