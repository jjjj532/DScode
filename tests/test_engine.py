from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from cscode.core.config import Config
from cscode.core.engine import Agent, AgentOptions
from cscode.core.messages import Message, MessageRole
from cscode.providers.base import LLMResult
from cscode.tools.base import BaseTool, ToolResult, ToolRegistry


class TestEngine:
    @pytest.fixture
    def registry(self) -> ToolRegistry:
        r = ToolRegistry()

        class EchoTool(BaseTool):
            name = "echo"
            description = "Echo text back"
            parameters = {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                },
                "required": ["text"],
            }

            async def execute(self, args: dict) -> ToolResult:
                return ToolResult(success=True, data=args.get("text", ""))

        r.register(EchoTool())
        return r

    @pytest.fixture
    def mock_provider(self):
        provider = AsyncMock()
        provider.model = "test-model"
        return provider

    @pytest.fixture
    def agent(self, registry: ToolRegistry, mock_provider) -> Agent:
        return Agent(
            config=Config(api_key="test", model="test-model"),
            provider=mock_provider,
            registry=registry,
            options=AgentOptions(max_tool_rounds=5),
        )

    async def test_simple_response(self, agent: Agent, mock_provider):
        """Agent 返回简单文本回复"""
        mock_provider.complete.return_value = LLMResult(
            content="Hello! How can I help?",
            finish_reason="stop",
        )

        response = await agent.run("Hi")
        assert "Hello! How can I help?" in response

    async def test_tool_call_then_response(self, agent: Agent, mock_provider):
        """Agent 调用工具后返回结果"""
        # 第一次调用：LLM 返回工具调用
        mock_provider.complete.return_value = LLMResult(
            content="",
            tool_calls=[
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "echo",
                        "arguments": '{"text": "hello world"}',
                    },
                }
            ],
            finish_reason="tool_calls",
        )

        # 模拟 LLM 第二次调用返回最终回复
        second_result = LLMResult(
            content="The echo said: hello world",
            finish_reason="stop",
        )

        original_complete = mock_provider.complete
        call_count = 0

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                return second_result
            return original_complete.return_value

        mock_provider.complete.side_effect = side_effect

        response = await agent.run("Echo hello")
        assert "hello world" in response

    async def test_tool_error_handling(self, agent: Agent, mock_provider):
        """工具调用出错时 Agent 不崩溃"""
        mock_provider.complete.return_value = LLMResult(
            content="",
            tool_calls=[
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "nonexistent_tool",
                        "arguments": "{}",
                    },
                }
            ],
            finish_reason="tool_calls",
        )

        second_result = LLMResult(
            content="The tool is not available",
            finish_reason="stop",
        )

        call_count = 0

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                return second_result
            return mock_provider.complete.return_value

        mock_provider.complete.side_effect = side_effect

        response = await agent.run("Run unknown tool")
        assert "not available" in response

    async def test_max_tool_rounds(self, agent: Agent, mock_provider):
        """达到最大工具调用轮次后停止"""
        mock_provider.complete.return_value = LLMResult(
            content="",
            tool_calls=[
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "echo",
                        "arguments": '{"text": "hi"}',
                    },
                }
            ],
            finish_reason="tool_calls",
        )

        agent.options.max_tool_rounds = 3
        response = await agent.run("Loop")
        assert isinstance(response, str)
