from oms.dataset.info_base import InfoBase, CoreInfoData


class ClassInfo(InfoBase):

    def __init__(self, core_info: CoreInfoData, owner: InfoBase = None):
        super().__init__(core_info, owner)


    def get_has_fun_list(self):
        return self.relationInfo.hasInfoMap.functionInfos.values()



