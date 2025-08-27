"""
LangChain ReAct 서버 실행기 (복사본)
원본: mcp_react_client/pgpt_server.py
주의: 원본을 변경하지 않고, 이 복사본을 서버 진입점으로 사용합니다.
"""

import asyncio
import json
import io
import sys
import re
import os
import uuid
from datetime import datetime, timezone
import base64
import mimetypes
from typing import Any, Dict, Optional

from processgpt_agent_sdk.server import ProcessGPTAgentServer
from processgpt_agent_sdk.utils.logger import (
    write_log_message,
    handle_application_error,
)
from mcp import ClientSession, StdioServerParameters, stdio_client
from .tool_loader import load_all_tools
from .agent import run_react_agent


DEFAULT_POLLING_INTERVAL = 5


class MCPActionExecutor:
    """ProcessGPT 서버용 Executor (동일 프로세스 실행)."""

    def __init__(self) -> None:
        self._running: bool = False

    async def execute(self, context, event_queue) -> None:
        """컨텍스트에서 입력을 모아 작업을 실행하고 이벤트를 발행합니다."""
        try:
            self._running = True

            user_message: str = (getattr(context, "get_user_input", lambda: "")() or "").strip()
            context_data: Dict[str, Any] = getattr(context, "get_context_data", lambda: {})() or {}

            write_log_message(
                f"[mcp-action] start todo_id={context_data.get('task_id')} "
                f"activity={context_data.get('activity_name')}"
            )

            inputs: Dict[str, Any] = {
                "todo_id": context_data.get("task_id"),
                "proc_inst_id": context_data.get("proc_inst_id"),
                "current_activity_name": context_data.get("activity_name", ""),
                "description": (context_data.get("description") or ""),
                "agent_info": context_data.get("agent_list"),
                "user_info": context_data.get("user_info"),
                "form_id": context_data.get("form_id"),
                "form_types": context_data.get("form_types"),
                "form_html": context_data.get("form_html"),
                "output_summary": context_data.get("output_summary", ""),
                "feedback_summary": context_data.get("feedback_summary", ""),
                "human_users": context_data.get("human_users"),
            }

            # 실제 실행 로직 호출 (main.py 흐름 재사용)
            await self._run_task(inputs, event_queue)

            # 완료 이벤트 발행
            done_payload = {
                "type": "done",
                "data": {
                    "event_type": "crew_completed",
                    "data": {},
                    "job_id": "CREW_FINISHED",
                    "crew_type": "crew",
                    "todo_id": inputs.get("todo_id"),
                    "proc_inst_id": inputs.get("proc_inst_id"),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            }
            event_queue.enqueue_event(done_payload)

        except Exception as e:
            handle_application_error("Executor 실행 오류", e, raise_error=True)
        finally:
            self._running = False

    async def cancel(self, context, event_queue) -> None:
        """취소 요청: 중단 없음 가정, 로그만 남김."""
        write_log_message("[mcp-action] cancel requested - no-op (no interruption)")

    async def _run_task(self, inputs: Dict[str, Any], event_queue) -> None:
        """ReAct 클라이언트 흐름을 그대로 재사용하여 실행."""
        todo_id = inputs.get("todo_id")
        proc_inst_id = inputs.get("proc_inst_id")
        activity_name = inputs.get("current_activity_name")
        description = inputs.get("description") or ""
        previous_result = inputs.get("output_summary")
        feedback_summary = inputs.get("feedback_summary")
        form_id = inputs.get("form_id")
        form_html = inputs.get("form_html")
        form_types = inputs.get("form_types")

        # 작업 시작 이벤트 저장
        job_id = str(uuid.uuid4())
        event_queue.enqueue_event({
            "type": "event",
            "data": {
                "event_type": "task_started",
                "data": {
                    "role": "Langchain React Agent",
                    "name": "Langchain React Agent",
                    "goal": "요청된 작업시지에 따라 적절한 툴을 선택하여 작업을 수행합니다.",
                    "agent_profile": "/images/chat-icon.png",
                    "activity_name": activity_name,
                    "description": description,
                    "previous_result": previous_result,
                    "feedback_summary": feedback_summary,
                },
                "job_id": job_id,
                "crew_type": "react",
                "todo_id": str(todo_id) if todo_id is not None else None,
                "proc_inst_id": str(proc_inst_id) if proc_inst_id is not None else None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        })
        # 이 실행에서 생성된 파일만 식별하기 위한 기준 시간
        start_ts = datetime.now(timezone.utc).timestamp()

        raw_result: Dict[str, Any] = {}

        work_dir = os.getenv("PGPT_WORK_DIR", "C:/uEngine/temp")
        python_path = os.getenv("PGPT_PYTHON_PATH", os.getenv("PYTHON", "python"))
        server_params = StdioServerParameters(
            command="uvx",
            args=[
                "mcp-python-code-interpreter",
                "--dir",
                work_dir,
                "--python-path",
                python_path
            ],
            env={
                "MCP_ALLOW_SYSTEM_ACCESS": "0",
                "PYTHONIOENCODING": os.getenv("PYTHONIOENCODING", "utf-8")
            }
        )

        def _to_json_str(obj: Any) -> str:
            try:
                return json.dumps(obj, ensure_ascii=False)
            except Exception:
                return str(obj) if obj is not None else ""

        # 프롬프트를 동적으로 구성: 값이 없는 섹션(이전결과물/피드백)은 생략
        def _sec(title: str, val: Any) -> str:
            s = (val or "").strip()
            return f"[{title}]\n{s}\n\n" if s else ""

        composite_query = (
            "다음 입력을 바탕으로 작업을 수행하세요. 최종 출력은 반드시 JSON 하나만 반환하세요(코드블록/설명 금지).\n\n"
            # 피드백이 있으면 최우선으로 반영하도록 최상단에 배치
            f"{_sec('피드백 내용', feedback_summary)}"
            f"{_sec('워크아이템 이름', activity_name)}"
            f"{_sec('지시사항', description)}"
            f"{_sec('이전결과물', previous_result)}"
            + (f"[form_type]\n{_to_json_str(form_types)}\n\n" if form_types else "")
            + (f"[form_html]\n{_to_json_str(form_html)}\n\n" if form_html else "")
            + "[결과형식 요구]\n"
            + "- 피드백 내용이 제공된 경우, 피드백을 최우선 기준으로 반영하세요.\n"
            + "- 결과는 form_type의 폼 키에 맞는 JSON 객체여야 합니다. (폼키: 값)\n"
            + "- 각 폼키의 타입(수치/문자/배열/객체 등)을 준수하세요.\n"
            + "- form_html은 form_type을 해석하는 힌트입니다. 구조(예: items 배열 등)를 파악해 값 형식을 맞추세요.\n"
            + "- 추가 설명 문장 없이 JSON만 반환하세요.\n\n"
            + "[출력 JSON 예시]\n"
            + "{\n  \"폼키예시_숫자\": 123,\n  \"폼키예시_문자\": \"텍스트\",\n}\n\n"
            + "주의: 위 예시는 형식 안내용으로, 최종 출력에서는 form_type에 정의된 실제 폼 키만 포함하고, 각 키의 타입과 이름에 맞는 값을 반환하세요. 추가 텍스트/설명/코드블록 없이 JSON만 반환하세요.\n"
        )
        
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await load_all_tools(session)
                    response = await run_react_agent(
                        tools,
                        composite_query,
                        verbose=False,
                        event_queue=event_queue,
                        job_id=job_id,
                        todo_id=todo_id,
                        proc_inst_id=proc_inst_id,
                    )

                    final_text = ""
                    try:
                        if response and "messages" in response:
                            msg = response["messages"][-1]
                            final_text = getattr(msg, "content", str(msg))
                        else:
                            final_text = str(response)
                    except Exception:
                        final_text = str(response)

                    raw_result = {
                        "operation": "react",
                        "status": "succeeded",
                        "result": final_text,
                    }

        except Exception as e:
            handle_application_error("[mcp-action] 실행 오류", e, raise_error=False)


        def _extract_json(text: str) -> Any:
            s = (text or "").strip()
            if not s:
                return {}
            fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", s, re.IGNORECASE)
            if fence_match:
                candidate = fence_match.group(1).strip()
                try:
                    return json.loads(candidate)
                except Exception:
                    pass
            start = s.find("{")
            end = s.rfind("}")
            if start != -1 and end != -1 and end > start:
                candidate = s[start:end+1]
                try:
                    return json.loads(candidate)
                except Exception:
                    pass
            return {"result": s}

        if raw_result.get("status") == "succeeded":
            text = raw_result.get("result", "")
            data_payload: Any = _extract_json(text)
        else:
            data_payload = raw_result
        
        # 최종 결과 중 이번 실행에서 생성된 로컬 이미지 파일만 Base64(Data URI)로 인라인
        def _is_generated_local_image(value: Any) -> tuple[bool, str]:
            if not isinstance(value, str):
                return False, ""
            try:
                path = value
                if not os.path.isfile(path):
                    return False, ""
                # 생성 시점 필터: 이번 작업 시작 이후 생성/수정된 파일만 허용
                if os.path.getmtime(path) < start_ts:
                    return False, ""
                ext = os.path.splitext(path)[1].lower()
                if ext not in [".png", ".jpg", ".jpeg", ".webp", ".gif"]:
                    return False, ""
                mime, _ = mimetypes.guess_type(path)
                return True, (mime or "image/png")
            except Exception:
                return False, ""

        def _file_to_markdown_image(path: str, mime: str) -> str:
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
            return f"![Generated Image](data:{mime};base64,{b64})"

        def _inline_images(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: _inline_images(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_inline_images(v) for v in obj]
            is_img, mime = _is_generated_local_image(obj)
            if is_img:
                try:
                    return _file_to_markdown_image(obj, mime)
                except Exception:
                    return obj
            return obj

        final_payload = _inline_images(data_payload)

        # 작업 완료 이벤트 저장
        event_queue.enqueue_event({
            "type": "event",
            "data": {
                "event_type": "task_completed",
                "data": final_payload,
                "job_id": job_id,
                "crew_type": "react",
                "todo_id": str(todo_id) if todo_id is not None else None,
                "proc_inst_id": str(proc_inst_id) if proc_inst_id is not None else None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        })

        event_queue.enqueue_event({
            "type": "output",
            "data": {
                "final": "true",
                "data": {form_id: final_payload}
            }
        })

        print(data_payload)


async def run_mcp_action_server(polling_interval: Optional[int] = None) -> None:
    interval = polling_interval or DEFAULT_POLLING_INTERVAL
    server = ProcessGPTAgentServer(
        executor=MCPActionExecutor(),
        polling_interval=interval,
        agent_orch="langchain-react",
    )
    await server.run()


def main() -> None:
    asyncio.run(run_mcp_action_server())


if __name__ == "__main__":
    main()


