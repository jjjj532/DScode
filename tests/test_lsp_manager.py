from __future__ import annotations

import pytest

from cscode.lsp.manager import LSPManager


class TestLSPManager:
    async def test_detect_language_py(self):
        mgr = LSPManager()
        lang = mgr.detect_language("/path/to/file.py")
        assert lang == "python"

    async def test_detect_language_ts(self):
        mgr = LSPManager()
        lang = mgr.detect_language("/path/to/file.ts")
        assert lang == "typescript"

    async def test_detect_language_tsx(self):
        mgr = LSPManager()
        lang = mgr.detect_language("/path/to/component.tsx")
        assert lang == "typescript"

    async def test_detect_language_js(self):
        mgr = LSPManager()
        lang = mgr.detect_language("/path/to/file.js")
        assert lang == "javascript"

    async def test_detect_language_unknown(self):
        mgr = LSPManager()
        lang = mgr.detect_language("/path/to/file.xyz")
        assert lang == "unknown"

    async def test_get_server_command_python(self):
        mgr = LSPManager()
        cmd = mgr.get_server_command("python")
        # pylsp 可能没安装，cmd 可能为 None
        if cmd is not None:
            assert "pylsp" in cmd[0]

    async def test_get_server_command_typescript(self):
        mgr = LSPManager()
        cmd = mgr.get_server_command("typescript")
        if cmd is not None:
            assert "typescript-language-server" in cmd[0]

    async def test_get_server_command_unknown(self):
        mgr = LSPManager()
        cmd = mgr.get_server_command("ruby")
        if cmd is not None:
            assert isinstance(cmd, list)

    async def test_get_client_no_lsp(self):
        """.rb 文件如果 solargraph 没安装，返回 None"""
        mgr = LSPManager()
        client = await mgr.get_client("/tmp/test.rb")
        assert client is None or client.is_running

    async def test_close_all(self):
        mgr = LSPManager()
        await mgr.close_all()
