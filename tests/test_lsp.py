from __future__ import annotations

from pathlib import Path

import pytest

from cscode.lsp.client import LSPClient, LSPError

MOCK_LSP = str(Path(__file__).parent / "mock_lsp.py")


@pytest.fixture
async def client():
    c = LSPClient(server_command=["python3", MOCK_LSP])
    await c.start()
    yield c
    await c.stop()


class TestLSPClient:
    async def test_initialization(self):
        client = LSPClient(server_command=["echo"])
        assert client.server_command == ["echo"]

    async def test_invalid_server(self):
        client = LSPClient(server_command=["nonexistent_lsp_server"])
        with pytest.raises(LSPError, match="Failed to start"):
            await client.start()

    async def test_request_before_start(self):
        client = LSPClient(server_command=["echo"])
        with pytest.raises(LSPError, match="not started"):
            await client.request("textDocument/definition", {})

    async def test_notify_before_start(self):
        client = LSPClient(server_command=["echo"])
        with pytest.raises(LSPError, match="not started"):
            await client.notify("textDocument/didOpen", {})

    async def test_stop_without_start(self):
        client = LSPClient(server_command=["echo"])
        await client.stop()


class TestLSPWithMockServer:
    async def test_start_and_stop(self):
        client = LSPClient(server_command=["python3", MOCK_LSP])
        await client.start()
        assert client.is_running
        await client.stop()
        assert not client.is_running

    async def test_double_start(self, client: LSPClient):
        await client.start()
        assert client.is_running

    async def test_definition_request(self, client: LSPClient):
        result = await client.request("textDocument/definition", {
            "textDocument": {"uri": "file:///test.py"},
            "position": {"line": 1, "character": 5},
        })
        assert result is not None
        assert "uri" in result

    async def test_completion_request(self, client: LSPClient):
        result = await client.request("textDocument/completion", {
            "textDocument": {"uri": "file:///test.py"},
            "position": {"line": 0, "character": 0},
        })
        assert result is not None
        assert "items" in result
        labels = [item["label"] for item in result["items"]]
        assert "print" in labels

    async def test_notification(self, client: LSPClient):
        await client.notify("textDocument/didOpen", {
            "textDocument": {
                "uri": "file:///test.py",
                "languageId": "python",
                "version": 1,
                "text": "print('hello')",
            },
        })
