from dataclasses import dataclass
from typing import List
from oms.dataset.info_base import InfoBase, CoreInfoData

class VarInfo(InfoBase):
    assign_list: List[str]

    def __init__(self, core_info: CoreInfoData, owner: InfoBase = None):
        super().__init__(core_info, owner)

    @classmethod
    def from_dict(cls, di: dict, owner: InfoBase = None) -> 'VarInfo':
        core_info = CoreInfoData.from_dict(di)
        return cls(core_info, owner)