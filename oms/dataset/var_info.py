from dataclasses import dataclass
from typing import List
from oms.dataset.info_base import InfoBase

class VarInfo(InfoBase):
    assign_list: List[str]