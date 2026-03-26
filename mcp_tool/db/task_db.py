import sqlite3
from typing import List, Dict, TYPE_CHECKING

from mcp_tool.db.main_task_db import MainTaskDB
from mcp_tool.db.sub_task_db import SubTaskDB

if TYPE_CHECKING:
    from oms.dataset.file_info import FileInfo


class TaskDB:
    """
    MainTaskDB와 SubTaskDB를 조합하는 Facade 클래스
    DB 연결을 관리하고 하위 클래스들을 조합하여 제공
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.main_task = MainTaskDB(self.conn)
        self.sub_task = SubTaskDB(self.conn)
        self._init_schema()

    def _init_schema(self):
        """테이블 스키마 초기화"""
        self.main_task.init_schema()
        self.sub_task.init_schema()

    # ==================== 위임 메서드 ====================

    def create_main_task(self, request: str) -> int:
        return self.main_task.create(request)

    def create_sub_tasks_from_file_info(self, main_task_id: int, file_info: 'FileInfo'):
        self.sub_task.create_batch_from_file_info(main_task_id, file_info)

    def create_sub_tasks_from_parse_results(self, main_task_id: int, results: list):
        self.sub_task.create_batch_from_parse_results(main_task_id, results)

    def fetch_pending_sub_tasks(self) -> List[dict]:
        return self.sub_task.fetch_pending()

    def fetch_pending_sub_tasks_by_main_id(self, main_task_id: int) -> List[dict]:
        return self.sub_task.fetch_pending_by_main_id(main_task_id)

    def get_all_sub_tasks(self) -> List[dict]:
        return self.sub_task.get_all()

    def get_all_main_tasks(self) -> List[dict]:
        return self.main_task.get_all()

    def update_sub_task(self, sub_task_id: int, result: str):
        self.sub_task.update(sub_task_id, result)

    def get_results_by_file(self, main_task_id: int) -> Dict[str, List[dict]]:
        return self.sub_task.get_results_by_file(main_task_id)

    def close(self):
        """DB 연결 종료"""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
