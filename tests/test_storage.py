from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from cscode.storage.db import Database
from cscode.storage.session import SessionStore
from cscode.core.messages import Message, MessageRole


@pytest.fixture
async def db(tmp_path: Path) -> Database:
    db = Database(db_path=tmp_path / "test.db")
    await db.init()
    yield db
    await db.close()


@pytest.fixture
async def session_store(db: Database) -> SessionStore:
    return SessionStore(db)


class TestDatabase:
    async def test_init_creates_tables(self, tmp_path: Path):
        db_path = tmp_path / "test.db"
        db = Database(db_path=db_path)
        await db.init()

        # 验证表已创建
        async with db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ) as cursor:
            tables = [row[0] for row in await cursor.fetchall()]

        assert "sessions" in tables
        assert "messages" in tables

    async def test_init_idempotent(self, db: Database):
        """多次 init 不会报错"""
        await db.init()
        await db.init()


class TestSessionStore:
    async def test_create_and_get_session(self, session_store: SessionStore):
        session = await session_store.create(
            title="test session",
            provider="openai",
            model="gpt-4o",
        )
        assert session.id is not None
        assert session.title == "test session"
        assert session.provider == "openai"
        assert session.model == "gpt-4o"
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.updated_at, datetime)

        fetched = await session_store.get(session.id)
        assert fetched is not None
        assert fetched.id == session.id
        assert fetched.title == session.title

    async def test_get_nonexistent_session(self, session_store: SessionStore):
        session = await session_store.get("nonexistent-id")
        assert session is None

    async def test_list_sessions(self, session_store: SessionStore):
        await session_store.create(title="session 1", provider="openai")
        await session_store.create(title="session 2", provider="anthropic")

        sessions = await session_store.list()
        assert len(sessions) >= 2

    async def test_delete_session(self, session_store: SessionStore):
        session = await session_store.create(title="to delete", provider="openai")
        assert session.id is not None

        await session_store.delete(session.id)
        fetched = await session_store.get(session.id)
        assert fetched is None

    async def test_save_and_get_messages(self, session_store: SessionStore):
        session = await session_store.create(title="msg test", provider="openai")
        assert session.id is not None

        msgs = [
            Message(role=MessageRole.USER, content="Hello"),
            Message(role=MessageRole.ASSISTANT, content="Hi there!"),
        ]
        await session_store.save_messages(session.id, msgs)

        loaded = await session_store.get_messages(session.id)
        assert len(loaded) == 2
        assert loaded[0].role == MessageRole.USER
        assert loaded[0].content == "Hello"
        assert loaded[1].role == MessageRole.ASSISTANT
        assert loaded[1].content == "Hi there!"

    async def test_update_session_title(self, session_store: SessionStore):
        session = await session_store.create(title="old title", provider="openai")
        assert session.id is not None

        await session_store.update_title(session.id, "new title")
        updated = await session_store.get(session.id)
        assert updated is not None
        assert updated.title == "new title"
