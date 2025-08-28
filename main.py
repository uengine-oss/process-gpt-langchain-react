# main.py
import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from langchain_react.server import run_mcp_action_server

_mcp_task: Optional[asyncio.Task] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _mcp_task
    _mcp_task = asyncio.create_task(run_mcp_action_server())
    try:
        yield
    finally:
        if _mcp_task and not _mcp_task.done():
            _mcp_task.cancel()
            try:
                await _mcp_task
            except asyncio.CancelledError:
                pass

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
