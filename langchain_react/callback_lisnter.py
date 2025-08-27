from datetime import datetime, timezone
from typing import Any, Optional, Dict

from langchain_core.callbacks import BaseCallbackHandler


class QueueCallback(BaseCallbackHandler):
    """
    LangChain/Graph 에이전트의 LLM/툴 사용을 큐에 기록하는 단순 콜백 핸들러.

    이벤트 페이로드 예:
    {
      "type": "event",
      "data": {
        "event_type": "llm_started | tool_usage_started | tool_usage_finished | tool_usage_error",
        "job_id": "…",
        "crew_type": "react",
        "data": { ... },    # 이벤트별 정보 (query, tool_name 등)
        "todo_id": "…" | null,
        "proc_inst_id": "…" | null,
        "timestamp": "ISO8601"
      }
    }
    """

    PREVIEW_MAX = 400  # 프리뷰 문자열 최대 길이

    def __init__(self, event_queue, job_id: str, todo_id: Optional[str] = None, proc_inst_id: Optional[str] = None):
        self.q = event_queue
        self.job_id = job_id
        self.todo_id = todo_id
        self.proc_inst_id = proc_inst_id
        self._tool_name: Optional[str] = None

    # ---------- helpers ----------
    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def _preview(cls, value: Any) -> str:
        """값을 문자열로 변환 후 길이 제한."""
        s = str(value) if value is not None else ""
        return s if len(s) <= cls.PREVIEW_MAX else (s[:cls.PREVIEW_MAX] + "…")

    def _emit(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        payload = {
            "type": "event",
            "data": {
                "event_type": event_type,
                "job_id": self.job_id,
                "crew_type": "react",
                "data": data or {},
                "todo_id": self.todo_id,
                "proc_inst_id": self.proc_inst_id,
                "timestamp": self._now_iso(),
            },
        }
        try:
            if hasattr(self.q, "enqueue_event"):
                self.q.enqueue_event(payload)
        except Exception:
            # 큐 전송 실패는 무시 (흐름 방해 금지)
            pass

    # ---------- TOOL ----------
    def on_tool_start(self, serialized, input_str, **kwargs):
        name = None
        if isinstance(serialized, dict):
            name = serialized.get("name")
        self._tool_name = name or kwargs.get("name") or "unknown"

        self._emit(
            "tool_usage_started",
            {
                "tool_name": self._tool_name,
                "query": self._preview(input_str),
            },
        )

    def on_tool_end(self, output, **kwargs):
        self._emit(
            "tool_usage_finished",
            {
                "tool_name": self._tool_name,
                "result": self._preview(output),
            },
        )
        self._tool_name = None
