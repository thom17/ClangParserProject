import sys
import json
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_tool.db.task_db import TaskDB
from mcp.server.fastmcp import FastMCP

TASK_DB_PATH = os.environ.get("TASK_DB_PATH", r"D:\temp\taskdb\cp_taskDB.db")

print(f"TASK_DB_PATH: {TASK_DB_PATH}")
taskDB = TaskDB(TASK_DB_PATH)
mcp = FastMCP("cp_taskDB")


@mcp.tool()
def solve_sub_task(task_id: int, result: str) -> str:
    """
    서브 작업을 해결합니다.
    :param task_id: 작업 ID
    :param result: 답변 (JSON 문자열)
    :return: 결과 메시지
    """
    taskDB.update_sub_task(task_id, result)
    after_tasks = taskDB.fetch_pending_sub_tasks()
    return f'{len(after_tasks)} 개의 서브 작업이 남아 있습니다.'


@mcp.tool()
def get_task():
    """
    현재 처리 안된 서브 작업 하나를 조회합니다.
    서브 작업의 src_name, file_path, code와 메인 작업의 request를 반환합니다.
    :return: 작업 정보 (JSON)
    """
    pending = taskDB.fetch_pending_sub_tasks()
    if not pending:
        return json.dumps({"message": "처리할 작업이 없습니다."}, ensure_ascii=False)

    task = pending[0]
    main_task = taskDB.main_task.get_by_id(task["main_task_id"])
    if main_task:
        task["request"] = main_task["request"]

    return json.dumps(task, ensure_ascii=False, indent=2)


@mcp.tool()
def print_path_info():
    """
    현재 작업 DB의 경로 정보와 메인 작업 목록을 출력합니다.
    :return: 경로 정보 문자열
    """
    main_tasks = taskDB.get_all_main_tasks()
    info_lines = [f"TASK_DB_PATH: {TASK_DB_PATH}"]
    for mt in main_tasks:
        pending = taskDB.sub_task.count_pending_by_main_id(mt["id"])
        info_lines.append(
            f"  [{mt['id']}] {mt['request']} "
            f"(status={mt['status']}, pending={pending})"
        )
    return "\n".join(info_lines)


if __name__ == "__main__":
    print(get_task())
