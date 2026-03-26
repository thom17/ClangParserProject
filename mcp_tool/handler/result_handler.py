import json
from abc import ABC, abstractmethod
from typing import Any, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from oms.dataset.function_info import FunctionInfo
    from mcp_tool.handler.info_matcher import MatchPair


class ResultHandler(ABC):
    """결과 처리 인터페이스"""

    @abstractmethod
    def handle(self, func_info: 'FunctionInfo', result: dict) -> Any:
        """단일 결과 처리"""
        ...

    @abstractmethod
    def handle_batch(self, matched_results: List['MatchPair']) -> Dict[str, list]:
        """파일 단위 일괄 처리
        return: {file_path: [처리 결과, ...]}
        """
        ...


class HashResultHandler(ResultHandler):
    """테스트용 해시 태그 결과 핸들러"""

    def handle(self, func_info: 'FunctionInfo', result: dict) -> dict:
        return {
            "src_name": func_info.src_name,
            "hash": result.get("hash", ""),
            "code_length": len(func_info.code) if func_info.code else 0,
            "verified": True
        }

    def handle_batch(self, matched_results: List['MatchPair']) -> Dict[str, list]:
        from collections import defaultdict
        grouped = defaultdict(list)

        for match in matched_results:
            if match.status != "matched":
                continue
            if match.sub_task is None or match.sub_task.get("status") != "done":
                continue
            if match.func_info is None:
                continue

            result_data = match.sub_task.get("result")
            if result_data:
                result = json.loads(result_data)
                handled = self.handle(match.func_info, result)
                grouped[match.file_path].append(handled)

        return dict(grouped)
