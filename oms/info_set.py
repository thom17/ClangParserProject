from typing import Dict, List, Optional
from collections import defaultdict

class InfoSet:
    def __init__(self):
        self.classInfos: Dict[str, 'ClassInfo'] = {}
        self.functionInfos: Dict[str, 'FunctionInfo'] = {}
        self.varInfos: Dict[str, 'VarInfo'] = {}

    def __add__(self, other: 'InfoSet') -> 'InfoSet':
        if not isinstance(other, InfoSet):
            raise TypeError(f"Unsupported operand type(s) for +: 'InfoSet' and '{type(other).__name__}'")

        new_info_set = InfoSet()
        new_info_set.update(self)
        duplicate_src = new_info_set.update(other)
        assert duplicate_src == 0, f'duplicate_src {len(duplicate_src)} 개의 중복 키.'

        return new_info_set

    def update(self, other: 'InfoSet') -> List[str]:
        if not isinstance(other, InfoSet):
            raise TypeError(f"Unsupported operand type(s) for update: 'InfoSet' and '{type(other).__name__}'")

        duplicate_src = []
        other_src_map = other.get_src_map()
        for src in other_src_map:
            if not self.get_info(src) is None:
                duplicate_src.append(src)

        # 중복 키의 경우 `other`의 값으로 덮어씀
        self.classInfos.update(other.classInfos)
        self.functionInfos.update(other.functionInfos)
        self.varInfos.update(other.varInfos)

        return duplicate_src


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

    def get_info(self, src_name)->'InfoBase':
        infos = []
        if src_name in self.classInfos:
            infos.append(self.classInfos.get(src_name))
        if src_name in self.functionInfos:
            infos.append(self.functionInfos.get(src_name))
        if src_name in self.varInfos:
            infos.append(self.varInfos.get(src_name))

        if len(infos) == 0:
            return None
        elif len(infos) == 1:
            return infos[0]
        else:
            assert False, f"srcName 충돌 {src_name}"
            # return infos

    def search_info(self, search_key) -> List['InfoBase']:
        infos = []
        for src_name in self.classInfos:
            if search_key in src_name:
                infos.append(self.classInfos.get(src_name))

        for src_name in self.functionInfos:
            if search_key in src_name:
                infos.append(self.functionInfos.get(src_name))

        for src_name in self.varInfos:
            if search_key in src_name:
                infos.append(self.varInfos.get(src_name))


        return infos

    def get_src_map(self) -> dict:
        """
        Class, Method, Var을 하나의 리스트로
        src_map을 생성
        :return:
        """

        info_map:[str, ['InfoBase']] = defaultdict(list)
        for src_name in self.classInfos:
            assert len(info_map[src_name]) == 0, "src_name 충돌"
            info_map[src_name].append(self.classInfos[src_name])

        for src_name in self.functionInfos:
            assert len(info_map[src_name]) == 0, "src_name 충돌"
            info_map[src_name].append(self.functionInfos[src_name])

        for src_name in self.varInfos:
            assert len(info_map[src_name]) == 0, "src_name 충돌"
            info_map[src_name].append(self.varInfos[src_name])

        return info_map

    def __str__(self):
        return f"InfoSet(cls:{len(self.classInfos)}, fun:{len(self.functionInfos)}, var:{len(self.varInfos)})"

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.get_src_map())

