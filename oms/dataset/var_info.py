from dataclasses import dataclass
from typing import List
from oms.dataset.info_base import InfoBase, CoreInfoData

class VarInfo(InfoBase):
    assign_list: List[str]

    def __init__(self, core_info: CoreInfoData, owner: InfoBase):
        super().__init__(core_info, owner)