from typing import Optional, List
from oms.dataset.function_info import FunctionInfo

class FlowAST:
    s_id = 0
    def __init__(self):
        self.id = FlowAST.s_id
        FlowAST.s_id += 1

        self.kind: Optional[str] = None
        self.line: Optional[int] = None
        self.column: Optional[int] = None
        self.end_line: Optional[int] = None
        self.end_column: Optional[int] = None

        self.code: Optional[str] = None
        self.parents: List['FlowAST'] = []

        self.next_flow: Optional['FlowAST'] = None

        self.extended_info: Optional['FlowInfo'] = None

    def set_next_flow(self, next_flow: 'FlowAST'):
        assert next_flow is not None, "next_flow cannot be None"
        self.next_flow = next_flow
        if next_flow:
            next_flow.parents.append(self)

    def set_parent(self, parents: List['FlowAST']):
        self.parents = parents
        for parent in parents:
            parent.next_flow = self

    def to_dict(self):
        return {
            'id': self.id,
            'kind': self.kind,
            'line': self.line,
            'column': self.column,
            'end_line': self.end_line,
            'end_column': self.end_column,
            'code': self.code,
            # 'next_flow': self.next_flow.to_dict() if self.next_flow else None,
            # 'extended_info': self.extended_info.to_dict() if self.extended_info else None,
        }



class FlowInfo:
    def __init__(self, flowAST: FlowAST):
        self.flowAST = flowAST
        flowAST.extended_info = self


class IfFlowInfo(FlowInfo):
    def __init__(self, flowAST: FlowAST):
        super().__init__(flowAST)
        self.condition: Optional[FlowAST] = None
        self.else_flow: Optional[FlowAST] = None

class WhileFlowInfo(FlowInfo):
    def __init__(self, flowAST: FlowAST):
        super().__init__(flowAST)
        self.condition: Optional[FlowAST] = None
        self.else_flow: Optional[FlowAST] = None


if __name__ == "__main__":
    di = {}
    print(None in di)


    pass
    # print