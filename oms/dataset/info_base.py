from dataclasses import dataclass, replace
from oms.info_set import InfoSet
from dataclasses import asdict

from abc import ABC
@dataclass
class CoreInfoData:
    """
    dataclass로 dict으로 간단하게 처리되는 데이터이자 핵심 데이터
    """
    name: str
    src_name: str
    comment: str
    is_static: bool
    is_virtual: bool
    modifier: str
    package_str: str
    code: str
    type_str: str

class RelationInfo:
    def __init__(self):
        self.callInfoMap = InfoSet()
        self.callByInfoMap = InfoSet()
        self.hasInfoMap = InfoSet()

        #추후 확장을 고려하여
        self.infoMap: [str, InfoSet] = {}
        self.infoMap["call"] = self.callInfoMap
        self.infoMap["callBy"] = self.callByInfoMap
        self.infoMap["has"] = self.hasInfoMap

    def __str__(self):
        this_str = 'RelationInfo('
        for relation_name, info_set in self.infoMap.items():
            this_str += f'\n\t{relation_name}:{info_set}'
        this_str += '\t)'
        return this_str

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        le = 0
        for info_set in self.infoMap.values():
            le += len(info_set)
        return le

class InfoBase(CoreInfoData, ABC):
    typeInfo: 'ClassInfo'
    relationInfo: RelationInfo

    def __init__(self, core_info: CoreInfoData, owner: 'InfoBase'= None):
        super().__init__(
            name=core_info.name,
            src_name=core_info.src_name,
            comment=core_info.comment,
            is_static=core_info.is_static,
            is_virtual=core_info.is_virtual,
            modifier=core_info.modifier,
            package_str=core_info.package_str,
            code=core_info.code,
            type_str=core_info.type_str
        )
        self.core_info = core_info
        self.typeInfo = None
        self.relationInfo = RelationInfo()
        self.owner = self
        if owner:
            self.owner = owner
            owner.relationInfo.hasInfoMap.put_info(self)

    def to_dict(self):
        core_info_dict = asdict(self.core_info)
        return core_info_dict

    def add_callInfo(self, info:'InfoBase'):

        self.relationInfo.callInfoMap.put_info(info)
        info.relationInfo.callByInfoMap.put_info(self)

    def add_callByInfo(self, info: 'InfoBase'):
        self.relationInfo.callByInfoMap.put_info(info)
        info.relationInfo.callInfoMap.put_info(self)
