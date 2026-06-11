from __future__ import annotations

from pathlib import Path

import pytest

from cscode.plugins.loader import PluginLoader


def _create_plugin(tmp_path: Path, name: str, code: str) -> Path:
    plugin_dir = tmp_path / name
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text(code)
    return plugin_dir


class TestPluginLoader:
    async def test_load_plugin_from_dir(self, tmp_path: Path):
        plugin_dir = _create_plugin(tmp_path, "my_plugin", """
from cscode.tools.base import BaseTool, ToolResult

class HelloTool(BaseTool):
    name = "hello"
    description = "Say hello"
    async def execute(self, args):
        return ToolResult(success=True, data="hello!")

__tools__ = [HelloTool]
""")
        loader = PluginLoader()
        tools = await loader.load_plugin(str(plugin_dir))
        assert len(tools) == 1
        assert tools[0].name == "hello"

    async def test_load_invalid_plugin(self, tmp_path: Path):
        plugin_dir = _create_plugin(tmp_path, "bad_plugin", """
raise ImportError("broken!")
""")
        loader = PluginLoader()
        tools = await loader.load_plugin(str(plugin_dir))
        assert len(tools) == 0

    async def test_load_nonexistent_plugin(self):
        loader = PluginLoader()
        tools = await loader.load_plugin("/nonexistent/path")
        assert len(tools) == 0

    async def test_discover_plugins(self, tmp_path: Path):
        _create_plugin(tmp_path, "plugin_a", """
from cscode.tools.base import BaseTool, ToolResult
class ToolA(BaseTool):
    name = "a"
    description = ""
    async def execute(self, args):
        return ToolResult(success=True, data="a")
__tools__ = [ToolA]
""")
        _create_plugin(tmp_path, "plugin_b", """
from cscode.tools.base import BaseTool, ToolResult
class ToolB(BaseTool):
    name = "b"
    description = ""
    async def execute(self, args):
        return ToolResult(success=True, data="b")
__tools__ = [ToolB]
""")
        loader = PluginLoader()
        tools = await loader.discover([str(tmp_path)])
        tool_names = {t.name for t in tools}
        assert "a" in tool_names
        assert "b" in tool_names
