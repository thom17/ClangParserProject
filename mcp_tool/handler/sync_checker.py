import os
from typing import List, Dict, TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from oms.parse_manager import ParseManager
    from mcp_tool.db.task_db import TaskDB


@dataclass
class SyncReport:
    """동기화 리포트"""
    synced: List[str] = field(default_factory=list)    # 변경 없는 파일
    stale: List[str] = field(default_factory=list)     # 변경된 파일
    missing: List[str] = field(default_factory=list)   # 삭제된 파일

    @property
    def is_clean(self) -> bool:
        return len(self.stale) == 0 and len(self.missing) == 0

    def __str__(self):
        lines = [f"SyncReport: {'CLEAN' if self.is_clean else 'DIRTY'}"]
        lines.append(f"  synced:  {len(self.synced)} files")
        lines.append(f"  stale:   {len(self.stale)} files")
        lines.append(f"  missing: {len(self.missing)} files")
        if self.stale:
            for f in self.stale:
                lines.append(f"    [STALE]   {f}")
        if self.missing:
            for f in self.missing:
                lines.append(f"    [MISSING] {f}")
        return "\n".join(lines)


class SyncChecker:
    """
    TaskDB ↔ ParserManager 동기화 상태 판단
    file_modified_at + code 내용으로 변경 여부 체크
    """

    def __init__(self, parser_manager: 'ParseManager', task_db: 'TaskDB'):
        self.parser = parser_manager
        self.task_db = task_db

    def check(self, main_task_id: int) -> SyncReport:
        """전체 동기화 리포트"""
        report = SyncReport()

        # SubTask에서 file_path별 file_modified_at 추출
        all_tasks = self.task_db.sub_task.get_all()
        file_mtime_map: Dict[str, float] = {}
        for task in all_tasks:
            if task["main_task_id"] == main_task_id:
                fp = task["file_path"]
                if fp not in file_mtime_map:
                    file_mtime_map[fp] = task["file_modified_at"]

        for file_path, task_mtime in file_mtime_map.items():
            status = self.check_file(file_path, task_mtime)
            if status == "synced":
                report.synced.append(file_path)
            elif status == "stale":
                report.stale.append(file_path)
            else:
                report.missing.append(file_path)

        return report

    def check_file(self, file_path: str, task_modified_at: float) -> str:
        """파일 수정 시간 비교
        return: 'synced' / 'stale' / 'missing'
        """
        if not os.path.exists(file_path):
            return "missing"

        current_mtime = os.path.getmtime(file_path)
        if current_mtime == task_modified_at:
            return "synced"
        return "stale"

    def check_code(self, src_name: str, task_code: str) -> bool:
        """코드 내용 일치 여부 (메서드 단위 정밀 체크)"""
        all_files = self.parser.db.load_all()
        for file_info in all_files:
            func = file_info.info_set.get_function_info(src_name)
            if func is not None:
                return func.code == task_code
        return False

    def is_applicable(self, main_task_id: int) -> bool:
        """결과 적용 가능 여부 (stale/missing 없으면 True)"""
        report = self.check(main_task_id)
        return report.is_clean
