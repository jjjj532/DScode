from __future__ import annotations

from pathlib import Path

import pytest

from cscode.tools.base import ToolResult
from cscode.tools.read import ReadTool
from cscode.tools.write import WriteTool
from cscode.tools.edit import EditTool
from cscode.tools.bash import BashTool
from cscode.tools.grep import GrepTool
from cscode.tools.glob import GlobTool
from cscode.tools.ls import LsTool


class TestReadTool:
    @pytest.fixture
    def tool(self) -> ReadTool:
        return ReadTool()

    async def test_read_existing_file(self, tool: ReadTool, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        result = await tool.execute({"path": str(f)})
        assert result.success
        assert "hello world" in result.data

    async def test_read_nonexistent_file(self, tool: ReadTool, tmp_path: Path):
        result = await tool.execute({"path": str(tmp_path / "nope.txt")})
        assert not result.success
        assert "not found" in result.error.lower()


class TestWriteTool:
    @pytest.fixture
    def tool(self) -> WriteTool:
        return WriteTool()

    async def test_write_new_file(self, tool: WriteTool, tmp_path: Path):
        f = tmp_path / "new.txt"
        result = await tool.execute({"path": str(f), "content": "hello"})
        assert result.success
        assert f.read_text() == "hello"

    async def test_write_creates_parent_dirs(self, tool: WriteTool, tmp_path: Path):
        target = tmp_path / "sub" / "file.txt"
        result = await tool.execute({
            "path": str(target),
            "content": "test",
        })
        assert result.success
        assert target.read_text() == "test"


class TestEditTool:
    @pytest.fixture
    def tool(self) -> EditTool:
        return EditTool()

    async def test_edit_file(self, tool: EditTool, tmp_path: Path):
        f = tmp_path / "edit.txt"
        f.write_text("hello world")
        result = await tool.execute({
            "path": str(f),
            "old_string": "hello",
            "new_string": "goodbye",
        })
        assert result.success
        assert f.read_text() == "goodbye world"

    async def test_edit_nonexistent_string(self, tool: EditTool, tmp_path: Path):
        f = tmp_path / "edit.txt"
        f.write_text("hello world")
        result = await tool.execute({
            "path": str(f),
            "old_string": "nope",
            "new_string": "goodbye",
        })
        assert not result.success


class TestBashTool:
    @pytest.fixture
    def tool(self) -> BashTool:
        return BashTool()

    async def test_run_echo(self, tool: BashTool):
        result = await tool.execute({"command": "echo hello"})
        assert result.success
        assert "hello" in result.data

    async def test_run_failing_command(self, tool: BashTool):
        result = await tool.execute({"command": "exit 1"})
        assert not result.success

    async def test_run_with_timeout(self, tool: BashTool):
        result = await tool.execute({"command": "echo hi", "timeout": 5000})
        assert result.success
        assert "hi" in result.data


class TestGrepTool:
    @pytest.fixture
    def tool(self) -> GrepTool:
        return GrepTool()

    async def test_grep_basic(self, tool: GrepTool, tmp_path: Path):
        f = tmp_path / "search.txt"
        f.write_text("line1\nmatch_this\nline3\nmatch_this\nline5")
        result = await tool.execute({
            "pattern": "match",
            "path": str(tmp_path),
        })
        assert result.success
        assert "search.txt" in result.data
        assert "match_this" in result.data


class TestGlobTool:
    @pytest.fixture
    def tool(self) -> GlobTool:
        return GlobTool()

    async def test_glob_basic(self, tool: GlobTool, tmp_path: Path):
        (tmp_path / "a.py").write_text("")
        (tmp_path / "b.py").write_text("")
        (tmp_path / "c.txt").write_text("")
        result = await tool.execute({
            "pattern": "*.py",
            "path": str(tmp_path),
        })
        assert result.success
        assert "a.py" in result.data
        assert "b.py" in result.data
        assert "c.txt" not in result.data


class TestLsTool:
    @pytest.fixture
    def tool(self) -> LsTool:
        return LsTool()

    async def test_ls_directory(self, tool: LsTool, tmp_path: Path):
        (tmp_path / "file_a.txt").write_text("")
        (tmp_path / "file_b.txt").write_text("")
        result = await tool.execute({"path": str(tmp_path)})
        assert result.success
        assert "file_a.txt" in result.data
        assert "file_b.txt" in result.data
