# Spec: CScode Phase 4 — Tauri 桌面应用

## Objective

为 CScode 提供跨平台桌面应用体验。用户在 macOS/Linux/Windows 上通过原生桌面图标启动 CScode，获得与传统桌面应用一致的体验（托盘、快捷键、原生菜单）。

## Architecture

```
┌─────────────────────────────────────────┐
│           Tauri v2 (Rust)               │
│  ┌───────────────────────────────────┐  │
│  │  Sidecar Manager                   │  │
│  │  • 启动/停止 Python 后端           │  │
│  │  • 健康检查                        │  │
│  │  • 崩溃重启                        │  │
│  └──────────────┬────────────────────┘  │
│                 │ HTTP :8080             │
│  ┌──────────────▼────────────────────┐  │
│  │  WebView (系统原生)               │  │
│  │  • React UI (来自 web/dist/)       │  │
│  │  • Tauri Commands (文件对话框等)   │  │
│  └───────────────────────────────────┘  │
│                                         │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ 系统托盘      │  │ 原生菜单      │    │
│  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────┘
         │
         │ 创建子进程 (sidecar)
         ▼
┌─────────────────────────────────────────┐
│     Python 后端 (cs server)              │
│     FastAPI on 127.0.0.1:8080            │
└─────────────────────────────────────────┘
```

## Tech Stack

| 层 | 技术 | 说明 |
|---|------|------|
| 桌面壳 | Tauri v2 | Rust + WebView |
| 通信 | HTTP (localhost) | WebView → FastAPI |
| 进程管理 | Tauri Sidecar API | 自动管理 Python 子进程 |
| 打包 | Tauri Bundler | .dmg / .deb / .msi |
| Python 分发 | PyInstaller | 单文件 Python 可执行 |

## Commands

```bash
# 开发模式
cs desktop                    # 启动桌面应用（开发模式，不打包）
cs desktop --dev              # 启动 + 显示 DevTools

# 构建
cd desktop
npm run tauri build           # 构建分发版
npm run tauri dev              # 开发模式热重载

# 测试
pytest tests/test_desktop/    # 桌面相关测试
```

## Project Structure

```
/Users/mac/AI/CScode/
├── desktop/
│   ├── src-tauri/              # Rust 项目
│   │   ├── Cargo.toml
│   │   ├── tauri.conf.json     # Tauri 配置
│   │   ├── capabilities/       # Tauri v2 权限
│   │   ├── icons/              # 应用图标
│   │   └── src/
│   │       ├── main.rs         # 入口
│   │       ├── lib.rs          # Tauri setup
│   │       └── sidecar.rs      # Python 进程管理
│   ├── package.json            # Tauri JS API + 构建脚本
│   ├── vite.config.ts          # Vite 配置（指向 web/dist）
│   └── src/                    # 桌面前端源码
│       └── main.ts             # Tauri JS API 入口
│
├── src/cscode/
│   ├── desktop_cli.py          # `cs desktop` 命令实现
│   └── server/app.py           # FastAPI (已有, 桌面复用)
```

## Sidecar Data Flow

```
Tauri 启动:
  1. Tauri 从资源目录解压 Python 可执行文件
  2. 启动子进程: python -m cscode server --port 8080
  3. 轮询 http://127.0.0.1:8080/api/health (最多 10 秒)
  4. 健康通过 → 加载 WebView → http://127.0.0.1:8080
  5. 健康失败 → 显示错误页面

Tauri 关闭:
  1. WebView 关闭
  2. 向 Python 进程发送 SIGTERM
  3. 等待 3 秒，未退出则 SIGKILL
```

## Code Style

```rust
// Rust: snake_case 函数, PascalCase 类型
// Tauri v2: Builder pattern 配置

use tauri::Manager;

#[tauri::command]
async fn greet(name: &str) -> String {
    format!("Hello, {name}!")
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

## Testing Strategy

| 层级 | 框架 | 位置 | 目标 |
|------|------|------|------|
| CLI 测试 | pytest | `tests/test_cli.py` | `cs desktop` 命令 |
| Rust 单元测试 | cargo test | `desktop/src-tauri/` | Sidecar 管理等 |
| 集成测试 | Playwright | `desktop/tests/` | Tauri E2E（可选） |

## Boundaries

### Always
- Tauri 启动失败时显示友好的错误页面
- Python 进程异常退出时自动重启
- 桌面应用快捷键和标准桌面行为一致

### Ask First
- 新增 Tauri 插件
- 修改 sidecar 通信协议
- 添加原生功能（文件系统操作、系统通知）

### Never
- 在 Rust 中硬编码 API Key 或敏感信息
- 阻塞主线程的 IO 操作
- 忽略不安全 Rust 警告

## Success Criteria (Phase 4)

- [ ] `cs desktop` 启动桌面应用，自动启动 Python 后端，WebView 加载 UI
- [ ] 桌面应用功能与 Web UI 一致（对话 + 工具执行）
- [ ] 关闭窗口时 Python 后端自动退出
- [ ] Python 后端崩溃时桌面应用自动重启
- [ ] `npm run tauri build` 生成本平台安装包
- [ ] 全部 111+ 测试通过

## Open Questions

1. PyInstaller 打包策略：后端单独打包 vs 嵌入到 Tauri 资源目录？
2. 是否需要系统托盘功能（常驻后台）？
3. 是否需要系统级快捷键（全局快捷键）？
