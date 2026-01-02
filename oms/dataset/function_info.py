from oms.info_set import InfoSet
from oms.dataset.info_base import InfoBase, CoreInfoData

class FunctionInfo(InfoBase):
    def __init__(self, core_info: CoreInfoData, owner: InfoBase = None):
        self.parameters: [InfoBase] = []

        super().__init__(core_info, owner)

    @classmethod
    def from_dict(cls, di: dict, owner: InfoBase = None) -> 'FunctionInfo':
        core_info = CoreInfoData.from_dict(di)
        return cls(core_info, owner)



