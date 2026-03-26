import sqlite3
from typing import List, Optional, Dict, TYPE_CHECKING
from collections import defaultdict

if TYPE_CHECKING:
    from oms.dataset.function_info import FunctionInfo
    from oms.dataset.file_info import FileInfo


class SubTaskDB:
    """
    SubTask 테이블 전용 클래스
    FunctionInfo + FileInfo 기반으로 태스크를 생성/관리
    """

    COLUMNS = "id, main_task_id, src_name, file_path, file_modified_at, code, status, result"

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def init_schema(self):
        """SubTask 테이블 생성"""
        c = self.conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS SubTask (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_task_id INTEGER,
            src_name TEXT,
            file_path TEXT,
            file_modified_at REAL,
            code TEXT,
            status TEXT,
            result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(main_task_id) REFERENCES MainTask(id)
        )""")
        self.conn.commit()

    def _row_to_dict(self, row) -> dict:
        return {
            "id": row[0],
            "main_task_id": row[1],
            "src_name": row[2],
            "file_path": row[3],
            "file_modified_at": row[4],
            "code": row[5],
            "status": row[6],
            "result": row[7]
        }

    # ==================== Create ====================

    def create_from_function_info(self, main_task_id: int,
                                  func_info: 'FunctionInfo',
                                  file_info: 'FileInfo') -> int:
        """FunctionInfo 1개 → SubTask 생성"""
        c = self.conn.cursor()
        c.execute("""
            INSERT INTO SubTask(main_task_id, src_name, file_path, file_modified_at, code, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            main_task_id,
            func_info.src_name,
            file_info.file_path,
            file_info.file_data.file_modified_at,
            func_info.code,
            "pending"
        ))
        self.conn.commit()
        return c.lastrowid

    def create_batch_from_file_info(self, main_task_id: int, file_info: 'FileInfo'):
        """FileInfo의 전체 FunctionInfo → SubTask 벌크 생성"""
        func_infos = file_info.info_set.functionInfos.values()
        if not func_infos:
            return

        c = self.conn.cursor()
        c.executemany("""
            INSERT INTO SubTask(main_task_id, src_name, file_path, file_modified_at, code, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            (
                main_task_id,
                func.src_name,
                file_info.file_path,
                file_info.file_data.file_modified_at,
                func.code,
                "pending"
            ) for func in func_infos
        ])
        self.conn.commit()

    def create_batch_from_parse_results(self, main_task_id: int,
                                        results: list):
        """smart_parse_project() 결과 직접 투입
        results: List[Tuple[str, FileInfo]]
        """
        rows = []
        for file_path, file_info in results:
            for func in file_info.info_set.functionInfos.values():
                rows.append((
                    main_task_id,
                    func.src_name,
                    file_info.file_path,
                    file_info.file_data.file_modified_at,
                    func.code,
                    "pending"
                ))

        if not rows:
            return

        c = self.conn.cursor()
        c.executemany("""
            INSERT INTO SubTask(main_task_id, src_name, file_path, file_modified_at, code, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, rows)
        self.conn.commit()

    # ==================== Read ====================

    def fetch_pending(self) -> List[dict]:
        """미해결 전체 SubTask 조회"""
        c = self.conn.cursor()
        c.execute(f"SELECT {self.COLUMNS} FROM SubTask WHERE status='pending'")
        return [self._row_to_dict(row) for row in c.fetchall()]

    def fetch_pending_by_main_id(self, main_task_id: int) -> List[dict]:
        """특정 MainTask의 미해결 SubTask 조회"""
        c = self.conn.cursor()
        c.execute(
            f"SELECT {self.COLUMNS} FROM SubTask WHERE main_task_id=? AND status='pending'",
            (main_task_id,)
        )
        return [self._row_to_dict(row) for row in c.fetchall()]

    def get_all(self) -> List[dict]:
        """모든 SubTask 조회"""
        c = self.conn.cursor()
        c.execute(f"SELECT {self.COLUMNS} FROM SubTask")
        return [self._row_to_dict(row) for row in c.fetchall()]

    def get_by_id(self, sub_task_id: int) -> Optional[dict]:
        """특정 SubTask 조회"""
        c = self.conn.cursor()
        c.execute(f"SELECT {self.COLUMNS} FROM SubTask WHERE id=?", (sub_task_id,))
        row = c.fetchone()
        if row:
            return self._row_to_dict(row)
        return None

    def get_results_by_file(self, main_task_id: int) -> Dict[str, List[dict]]:
        """file_path별 done 결과 그룹핑"""
        c = self.conn.cursor()
        c.execute(
            f"SELECT {self.COLUMNS} FROM SubTask WHERE main_task_id=? AND status='done'",
            (main_task_id,)
        )
        grouped = defaultdict(list)
        for row in c.fetchall():
            d = self._row_to_dict(row)
            grouped[d["file_path"]].append(d)
        return dict(grouped)

    # ==================== Update ====================

    def update(self, sub_task_id: int, result: str):
        """SubTask 상태를 'done'으로 변경하고 결과 저장"""
        c = self.conn.cursor()
        c.execute(
            "UPDATE SubTask SET status='done', result=? WHERE id=?",
            (result, sub_task_id)
        )
        self.conn.commit()

    def count_pending_by_main_id(self, main_task_id: int) -> int:
        """특정 MainTask의 미해결 SubTask 개수"""
        c = self.conn.cursor()
        c.execute(
            "SELECT COUNT(*) FROM SubTask WHERE main_task_id=? AND status='pending'",
            (main_task_id,)
        )
        return c.fetchone()[0]
