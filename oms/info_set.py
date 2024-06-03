from typing import Dict, List
from dataclasses import dataclass

class InfoSet:

    def __init__(self):
        self.classInfos: Dict[str, 'ClassInfo'] = {}
        self.functionInfos: Dict[str, 'FunctionInfo'] = {}
        self.varInfos: Dict[str, 'VarInfo'] = {}

    def get_class_info(self, src_name: str) -> 'ClassInfo':
        return self.classInfos.get(src_name)

    def get_function_info(self, src_name: str) -> 'FunctionInfo':
        return self.functionInfos.get(src_name)

    def get_var_info(self, src_name: str) -> 'varInfos':
        return self.varInfos.get(src_name)

    # def get_infos(self, src_name: str) -> ['InfoBase']:

    def __put_class_info(self, new_info):
        old_info = None
        if new_info.src_name in self.classInfos:
            old_info = self.classInfos[new_info.src_name]
        self.classInfos[new_info.src_name] = new_info
        return old_info

    def __put_var_info(self, new_info):
        old_info = None
        if new_info.src_name in self.varInfos:
            old_info = self.varInfos[new_info.src_name]
        self.varInfos[new_info.src_name] = new_info
        return old_info

    def __put_fun_info(self, new_info):
        old_info = None
        if new_info.src_name in self.functionInfos:
            old_info = self.functionInfos[new_info.src_name]
        self.functionInfos[new_info.src_name] = new_info
        return old_info

    def put_info(self, new_info):
        if new_info.__class__.__name__ == 'ClassInfo':
            return self.__put_class_info(new_info)
        elif new_info.__class__.__name__ == 'FunctionInfo':
            return self.__put_fun_info(new_info)
        elif new_info.__class__.__name__ == 'VarInfo':
            return self.__put_var_info(new_info)


    # def putInfo(self, new_info:Info):
    #     if isinstance(new_info, 'ClassInfo'):
    #         if new_info classInfos