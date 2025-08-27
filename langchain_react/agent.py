import os
import uuid
from typing import List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from .callback_lisnter import QueueCallback


async def run_react_agent(
    tools: List,
    query: str,
    verbose: bool = False,
    *,
    event_queue=None,
    job_id: str | None = None,
    todo_id: str | None = None,
    proc_inst_id: str | None = None,
):
    """ReAct 에이전트를 실행하고 필요 시 콜백을 연결합니다."""

    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it using: export OPENAI_API_KEY='your-api-key'")

    model = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        api_key=openai_api_key,
    )

    agent = create_react_agent(model, tools)

    invoke_kwargs = {}
    if event_queue is not None:
        handler = QueueCallback(event_queue, job_id or str(uuid.uuid4()), todo_id, proc_inst_id)
        invoke_kwargs["config"] = {"callbacks": [handler]}

    response = await agent.ainvoke({"messages": [("user", query)]}, **invoke_kwargs)
    return response


