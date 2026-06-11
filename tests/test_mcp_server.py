from __future__ import annotations

import pytest

from cscode.mcp.client import MCPClient
from cscode.mcp.server import MCPServer
from cscode.tools.base import ToolRegistry
from cscode.tools.echo import EchoTool


@pytest.fixture
def registry() -> ToolRegistry:
    r = ToolRegistry()
    r.register(EchoTool())
    return r


class TestMCPServer:
    async def test_server_initialization(self, registry: ToolRegistry):
        """MCPServer 初始化时加载所有注册工具"""
        server = MCPServer(registry)
        assert len(server.tool_schemas) == 1
        assert server.tool_schemas[0]["name"] == "echo"

    async def test_handle_tools_list(self, registry: ToolRegistry):
        """处理 tools/list 请求"""
        server = MCPServer(registry)
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }
        response = await server.handle_request(request)
        assert response["id"] == 1
        tools = response["result"]["tools"]
        assert len(tools) == 1
        assert tools[0]["name"] == "echo"

    async def test_handle_initialize(self, registry: ToolRegistry):
        """处理 initialize 请求"""
        server = MCPServer(registry)
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2025-03-26", "capabilities": {}},
        }
        response = await server.handle_request(request)
        assert response["id"] == 1
        assert "serverInfo" in response["result"]

    async def test_handle_tools_call(self, registry: ToolRegistry):
        """处理 tools/call 请求"""
        server = MCPServer(registry)
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {"text": "hello"},
            },
        }
        response = await server.handle_request(request)
        assert response["id"] == 1
        content = response["result"]["content"]
        assert len(content) > 0

    async def test_handle_tools_call_unknown(self, registry: ToolRegistry):
        """调用不存在的工具返回错误"""
        server = MCPServer(registry)
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "nonexistent",
                "arguments": {},
            },
        }
        response = await server.handle_request(request)
        assert "error" in response
