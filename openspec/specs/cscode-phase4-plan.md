# Implementation Plan: CScode Phase 4 — Tauri Desktop

## Task Breakdown

### Task 4.1: Tauri 项目搭建
- 创建 `desktop/` 目录结构
- 创建 `desktop/src-tauri/Cargo.toml` (tauri v2, serde, reqwest)
- 创建 `desktop/src-tauri/tauri.conf.json` (白名单端口 8080, 窗口配置)
- 创建 `desktop/src-tauri/capabilities/default.json` (权限)
- 创建 `desktop/src-tauri/build.rs`
- 创建 `desktop/package.json` (npm run tauri dev/build)
- 创建 `desktop/vite.config.ts` (Vite 指向 web/dist)
- 生成占位图标
- 验证: `npm run tauri dev` 启动空窗口

### Task 4.2: Rust 端 — Sidecar 进程管理 + WebView
- **sidecar.rs**: Python 子进程生命周期管理
  - `start_backend()`: 启动 `python -m cscode.server`
  - `stop_backend()`: 发送 SIGTERM, 超时后 SIGKILL
  - `wait_for_health()`: 轮询 `/api/health`, 最多重试 10 秒
  - `auto_restart()`: 进程退出后自动重启
- **lib.rs**: Tauri Builder 配置
  - `setup` hook: 启动 Python, 等待健康, 加载 WebView
  - `on_window_event`: 关闭时停止 Python
- 验证: 启动 app → Python 自动启动 → WebView 加载 UI

### Task 4.3: Python CLI — `cs desktop` 命令
- `src/cscode/desktop_cli.py`
  - 检测 Tauri 是否已构建
  - 调用 `npm run tauri dev` 或 `cargo run`
  - 环境变量传递给子进程
- CLI 注册: `cli.py` 中的 `@cli.command()`
- 验证: `cs desktop` 启动桌面应用

### Task 4.4: 安装包构建配置
- `tauri.conf.json` 中配置 bundle
  - macOS: .dmg, 图标
  - Linux: .deb, AppImage
  - Windows: .msi
- PyInstaller 配置 (`desktop/pyinstaller.spec`)
- 验证: `npm run tauri build` 生成本平台安装包

## Dependencies

```
Task 4.1 (Scaffold) → Task 4.2 (Sidecar) → Task 4.4 (Build)
                                            ↓
Task 4.3 (CLI, 可与 4.1 并行)
```

## Complexity Estimates

| Task | 复杂度 | 文件数 | 估计时间 |
|------|--------|--------|----------|
| 4.1 Tauri 搭建 | Low | 10+ | 30min |
| 4.2 Sidecar + WebView | Medium | 3 | 1h |
| 4.3 CLI 命令 | Low | 2 | 15min |
| 4.4 构建配置 | Medium | 3 | 30min |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Tauri v2 API 与文档不一致 | Medium | 参考官方示例，最小化插件依赖 |
| PyInstaller 打包 Python 后端 | Medium | 先不做 PyInstaller，用开发模式 sidecar |
| 跨平台 WebView 行为差异 | Low | Tauri 自带抽象，仅在需要时特化 |
