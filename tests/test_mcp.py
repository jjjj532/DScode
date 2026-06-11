from __future__ import annotations

import json
from pathlib import Path

import pytest

from cscode.mcp.client import MCPClient, MCPError

MOCK_MCP = str(Path(__file__).parent / "mock_mcp.py")


@pytest.fixture
async def client():
    c = MCPClient(server_command=["python3", MOCK_MCP])
    await c.connect()
    yield c
    await c.disconnect()


class TestMCPClient:
    async def test_connect_and_disconnect(self):
        """启动和关闭 MCP 连接"""
        client = MCPClient(server_command=["python3", MOCK_MCP])
        await client.connect()
        assert client.is_connected
        await client.disconnect()
        assert not client.is_connected

    async def test_list_tools(self, client: MCPClient):
        """列出 MCP 服务器提供的工具"""
        tools = await client.list_tools()
        assert len(tools) > 0
        tool_names = [t["name"] for t in tools]
        assert "read_file" in tool_names
        assert "echo" in tool_names

    async def test_call_tool(self, client: MCPClient):
        """调用 MCP 工具"""
        result = await client.call_tool("echo", {"text": "hello"})
        assert result is not None
        # mock 返回结果

    async def test_call_nonexistent_tool(self, client: MCPClient):
        """调用不存在的工具应该报错"""
        with pytest.raises(MCPError, match="not found"):
            await client.call_tool("nonexistent", {})

    async def test_invalid_server(self):
        """无效的 server 命令报错"""
        client = MCPClient(server_command=["nonexistent_mcp"])
        with pytest.raises(MCPError, match="Failed to start"):
            await client.connect()
