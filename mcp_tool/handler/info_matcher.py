from typing import Optional, List, Dict, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from oms.parse_manager import ParseManager
    from oms.dataset.function_info import FunctionInfo
    from mcp_tool.db.task_db import TaskDB


@dataclass
class MatchPair:
    """FunctionInfo ↔ SubTask 대응 결과"""
    src_name: str
    file_path: str
    func_info: Optional['FunctionInfo']  # None이면 task_only
    sub_task: Optional[dict]             # None이면 info_only
    status: str                          # matched / task_only / info_only


class InfoMatcher:
    """
    ParserManager의 FunctionInfo ↔ TaskDB의 SubTask 대응 조회
    src_name을 키로 양쪽 데이터를 매칭
    """

    def __init__(self, parser_manager: 'ParseManager', task_db: 'TaskDB'):
        self.parser = parser_manager
        self.task_db = task_db

    def find_function(self, src_name: str) -> Optional['FunctionInfo']:
        """src_name으로 ParserManager에서 FunctionInfo 조회"""
        all_files = self.parser.db.load_all()
        for file_info in all_files:
            func = file_info.info_set.get_function_info(src_name)
            if func is not None:
                return func
        return None

    def find_sub_task(self, src_name: str, main_task_id: int) -> Optional[dict]:
        """src_name으로 TaskDB에서 SubTask 조회"""
        tasks = self.task_db.sub_task.fetch_pending_by_main_id(main_task_id)
        for task in tasks:
            if task["src_name"] == src_name:
                return task
        return None

    def _build_function_map(self) -> Dict[str, tuple]:
        """ParserManager에서 전체 FunctionInfo 맵 생성
        return: {src_name: (FunctionInfo, FileInfo)}
        """
        func_map = {}
        all_files = self.parser.db.load_all()
        for file_info in all_files:
            for src_name, func in file_info.info_set.functionInfos.items():
                func_map[src_name] = (func, file_info)
        return func_map

    def _build_sub_task_map(self, main_task_id: int) -> Dict[str, dict]:
        """TaskDB에서 전체 SubTask 맵 생성
        return: {src_name: sub_task_dict}
        """
        all_tasks = self.task_db.sub_task.get_all()
        task_map = {}
        for task in all_tasks:
            if task["main_task_id"] == main_task_id:
                task_map[task["src_name"]] = task
        return task_map

    def match(self, main_task_id: int) -> List[MatchPair]:
        """전체 대응 결과 반환"""
        func_map = self._build_function_map()
        task_map = self._build_sub_task_map(main_task_id)

        all_src_names = set(func_map.keys()) | set(task_map.keys())
        results = []

        for src_name in all_src_names:
            func_tuple = func_map.get(src_name)
            sub_task = task_map.get(src_name)

            func_info = func_tuple[0] if func_tuple else None
            file_path = func_tuple[1].file_path if func_tuple else sub_task["file_path"]

            if func_info and sub_task:
                status = "matched"
            elif sub_task:
                status = "task_only"
            else:
                status = "info_only"

            results.append(MatchPair(
                src_name=src_name,
                file_path=file_path,
                func_info=func_info,
                sub_task=sub_task,
                status=status
            ))

        return results

    def match_by_file(self, main_task_id: int, file_path: str) -> List[MatchPair]:
        """파일 단위 대응 조회"""
        all_matches = self.match(main_task_id)
        return [m for m in all_matches if m.file_path == file_path]
