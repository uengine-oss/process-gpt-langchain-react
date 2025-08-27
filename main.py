import asyncio

from langchain_react.server import run_mcp_action_server


if __name__ == "__main__":
    # 전역 print 자동 flush 활성화
    asyncio.run(run_mcp_action_server())


