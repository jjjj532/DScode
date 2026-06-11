from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from cscode.core.config import load_config
from cscode.core.engine import Agent, AgentOptions
from cscode.providers import create_provider
from cscode.storage.db import Database
from cscode.storage.session import SessionStore
from cscode.tools.base import ToolRegistry
from cscode.tools.bash import BashTool
from cscode.tools.edit import EditTool
from cscode.tools.glob import GlobTool
from cscode.tools.grep import GrepTool
from cscode.tools.ls import LsTool
from cscode.tools.read import ReadTool
from cscode.tools.write import WriteTool

WEB_DIST = Path(__file__).resolve().parent.parent / "web" / "dist"

app = FastAPI(title="CScode API", version="0.1.0")

if WEB_DIST.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIST), html=True), name="web")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_db: Database | None = None
_session_store: SessionStore | None = None
_agent: Agent | None = None


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.on_event("startup")
async def startup() -> None:
    global _db, _session_store, _agent
    _db = Database()
    await _db.init()
    _session_store = SessionStore(_db)
    config = load_config()
    provider = create_provider(config)
    registry = ToolRegistry()
    registry.register(ReadTool())
    registry.register(WriteTool())
    registry.register(EditTool())
    registry.register(BashTool())
    registry.register(GrepTool())
    registry.register(GlobTool())
    registry.register(LsTool())
    _agent = Agent(
        config=config,
        provider=provider,
        registry=registry,
        options=AgentOptions(
            system_prompt="You are CScode, an AI-powered coding assistant.",
        ),
    )


@app.on_event("shutdown")
async def shutdown() -> None:
    if _db is not None:
        await _db.close()


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    if _agent is None or _session_store is None:
        raise HTTPException(status_code=503, detail="Server not initialized")

    session_id = request.session_id or str(uuid.uuid4())

    try:
        response = await _agent.run(request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return ChatResponse(response=response, session_id=session_id)


@app.get("/api/sessions")
async def list_sessions() -> list[dict[str, Any]]:
    if _session_store is None:
        raise HTTPException(status_code=503, detail="Server not initialized")
    sessions = await _session_store.list()
    return [
        {
            "id": s.id,
            "title": s.title,
            "provider": s.provider,
            "model": s.model,
            "created_at": s.created_at.isoformat() if s.created_at else "",
            "updated_at": s.updated_at.isoformat() if s.updated_at else "",
        }
        for s in sessions
    ]
