from oms.info_set import InfoSet
from oms.dataset.info_base import InfoBase, CoreInfoData

class FunctionInfo(InfoBase):
    def __init__(self, core_info: CoreInfoData):
        self.parameters: [InfoBase] = []

        super().__init__(core_info)

