from typing import Optional, List, Dict, Any, TYPE_CHECKING

from mcp_tool.db.task_db import TaskDB
from mcp_tool.handler.info_matcher import InfoMatcher, MatchPair
from mcp_tool.handler.sync_checker import SyncChecker, SyncReport
from mcp_tool.handler.result_handler import ResultHandler

if TYPE_CHECKING:
    from oms.parse_manager import ParseManager


class TaskManager:
    """
    통합 관리 메인 클래스
    ParserManager ↔ TaskDB 브릿지
    InfoMatcher, SyncChecker를 합성하고 ResultHandler를 주입받아 사용
    """

    def __init__(self, parser_manager: 'ParseManager', task_db: TaskDB):
        self.parser = parser_manager
        self.task_db = task_db
        self.matcher = InfoMatcher(parser_manager, task_db)
        self.sync = SyncChecker(parser_manager, task_db)

    # ==================== 태스크 생성 ====================

    def create_task(self, request: str, search_key: str = None) -> int:
        """ParserManager에서 FunctionInfo를 식별하여 태스크 생성

        Args:
            request: 태스크 설명
            search_key: 특정 메서드만 필터링 (None이면 전체)

        Returns:
            main_task_id
        """
        main_id = self.task_db.create_main_task(request)

        all_files = self.parser.db.load_all()
        count = 0

        for file_info in all_files:
            funcs = file_info.info_set.functionInfos
            for src_name, func_info in funcs.items():
                if search_key and search_key not in src_name:
                    continue
                self.task_db.sub_task.create_from_function_info(
                    main_id, func_info, file_info
                )
                count += 1

        print(f"Task created: main_id={main_id}, sub_tasks={count}")
        return main_id

    def create_task_from_file(self, request: str, file_path: str) -> int:
        """특정 파일의 FunctionInfo만 태스크로 생성"""
        main_id = self.task_db.create_main_task(request)

        file_info = self.parser.db.load(file_path)
        if file_info is None:
            print(f"File not found in DB: {file_path}")
            return main_id

        self.task_db.sub_task.create_batch_from_file_info(main_id, file_info)
        count = len(file_info.info_set.functionInfos)
        print(f"Task created: main_id={main_id}, sub_tasks={count}, file={file_path}")
        return main_id

    def create_task_from_parse_results(self, request: str, results: list) -> int:
        """smart_parse_project() 결과로 태스크 생성"""
        main_id = self.task_db.create_main_task(request)
        self.task_db.sub_task.create_batch_from_parse_results(main_id, results)

        count = sum(
            len(fi.info_set.functionInfos) for _, fi in results
        )
        print(f"Task created: main_id={main_id}, sub_tasks={count}")
        return main_id

    # ==================== 결과 적용 ====================

    def apply(self, main_task_id: int, handler: ResultHandler,
              force: bool = False) -> Dict[str, list]:
        """동기화 체크 → 대응 조회 → 핸들러 적용

        Args:
            main_task_id: 대상 MainTask ID
            handler: ResultHandler 구현체
            force: True이면 동기화 체크 무시

        Returns:
            {file_path: [핸들러 처리 결과, ...]}
        """
        if not force:
            report = self.sync.check(main_task_id)
            if not report.is_clean:
                print(f"Sync check failed:\n{report}")
                return {"__error__": "sync_failed", "__report__": str(report)}

        matched = self.matcher.match(main_task_id)
        return handler.handle_batch(matched)

    # ==================== 상태 조회 ====================

    def get_sync_report(self, main_task_id: int) -> SyncReport:
        """동기화 리포트 조회"""
        return self.sync.check(main_task_id)

    def get_matches(self, main_task_id: int) -> List[MatchPair]:
        """대응 조회"""
        return self.matcher.match(main_task_id)

    def get_progress(self, main_task_id: int) -> dict:
        """태스크 진행 상황"""
        all_tasks = self.task_db.sub_task.get_all()
        tasks = [t for t in all_tasks if t["main_task_id"] == main_task_id]

        total = len(tasks)
        done = sum(1 for t in tasks if t["status"] == "done")
        pending = total - done

        return {
            "main_task_id": main_task_id,
            "total": total,
            "done": done,
            "pending": pending,
            "progress": f"{done}/{total}" if total > 0 else "0/0"
        }
