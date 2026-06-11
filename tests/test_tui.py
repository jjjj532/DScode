from __future__ import annotations

import pytest
from textual.widgets import Input, RichLog


class TestCScodeTUI:
    async def test_app_starts(self):
        """TUI 应用可以启动"""
        from cscode.tui.app import CScodeTUI

        app = CScodeTUI()
        async with app.run_test(size=(80, 24)) as pilot:
            assert app.is_running

    async def test_has_input_widget(self):
        """界面包含输入框"""
        from cscode.tui.app import CScodeTUI

        app = CScodeTUI()
        async with app.run_test(size=(80, 24)) as pilot:
            input_widget = app.query_one(Input)
            assert input_widget is not None
            assert input_widget.placeholder is not None

    async def test_has_output_panel(self):
        """界面包含输出面板"""
        from cscode.tui.app import CScodeTUI

        app = CScodeTUI()
        async with app.run_test(size=(80, 24)) as pilot:
            output = app.query_one(RichLog)
            assert output is not None

    async def test_input_empty_does_nothing(self):
        """空输入不发送"""
        from cscode.tui.app import CScodeTUI

        app = CScodeTUI()
        async with app.run_test(size=(80, 24)) as pilot:
            input_widget = app.query_one(Input)
            input_widget.value = ""
            await pilot.press("enter")
            # 空输入应该被忽略

    async def test_quit_via_ctrl_c(self):
        """Ctrl+C 退出"""
        from cscode.tui.app import CScodeTUI

        app = CScodeTUI()
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.press("ctrl+c")
