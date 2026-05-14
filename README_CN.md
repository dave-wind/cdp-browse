# CDP Browse

浏览器自动化 Skill，面向 AI 编码助手。通过 CDP-Bridge 控制本地 Chrome —— 爬取页面、点击元素、提取数据，复用已有登录态。

[English](README.md) | 中文

---

## 它是什么

CDP Browse 让你的 AI 编码助手（Claude Code、Codex、OpenCode、GitHub Copilot）能够控制你的 **真实 Chrome 浏览器**——Cookie、登录态、JS 渲染全部复用，不需要重新登录。

两种模式 — 选一个或都装：

| 模式 | 工作方式 | 适用场景 |
|------|---------|---------|
| **MCP** | Agent 通过 CDP-Bridge MCP 服务直接调用 `browser_scan`、`browser_execute_js` 等工具 | 快速查看页面、截图、读取 Cookie、单页任务 |
| **SDK（Skill）** | Agent 运行 Python 脚本 `from cdp_sdk import CDPClient, Page` | 复杂爬取、多步操作（登录→点击→提交）、数据提取 |

## 前置条件

1. **Chrome**（或其他 Chromium 浏览器）
2. **Python 3.10+**
3. **uv** — 快速 Python 包运行器

### 安装 uv

`uv` 是运行 Python 工具的推荐方式，替代 `pipx`，避免 Python 3.12+ 上的常见问题。

**macOS / Linux：**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows：**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**或用 pip 安装：**
```bash
pip install uv
```

**或用 Homebrew（macOS）：**
```bash
brew install uv
```

安装后 `uvx` 命令也可用（它是 `uv tool run` 的别名）。

**让 `uv` 重启终端后仍然可用：**

如果新终端中找不到 `uv`，需要手动加入 PATH：

| Shell | 命令 |
|-------|------|
| **zsh**（macOS 默认） | `echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc` |
| **bash**（Linux） | `echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc` |
| **Windows** | 无需操作 — 安装程序会自动加入 PATH |

> **国内用户加速提示：** 使用阿里云镜像加速 uvx 下载，在任何 `uvx` 命令前加镜像前缀：
> ```bash
> UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ uvx cdp-bridge@latest
> ```
> 或永久设置：
> ```bash
> export UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
> ```

## 安装

### 第 1 步：加载 Chrome 扩展

CDP-Bridge 扩展负责连接浏览器和 MCP 服务。**必须先安装扩展**，再执行后续操作。

**一键下载：**
```bash
git clone https://gitee.com/dave-wind/cdp-browse-extenssion.git cdp_browse_extension
```

下载到当前目录的 `./cdp_browse_extension/`。也可指定目录：
```bash
git clone https://gitee.com/dave-wind/cdp-browse-extenssion.git /path/to/dest
```

> **备选方式（GitHub 托管脚本）：**
> ```bash
> curl -sSL https://raw.githubusercontent.com/dave-wind/cdp-browse/master/download-extension.sh | bash
> ```

在 Chrome 中加载：

1. 打开 `chrome://extensions/`
2. 开启右上角 **开发者模式**
3. 点击 **加载已解压的扩展程序**
4. 选择下载好的扩展文件夹
5. 扩展图标应显示 **绿色 "Connected"**

> 扩展默认连接 `127.0.0.1:18765`。请确保系统代理绕过 `localhost` 和 `127.0.0.1`。

### 第 2 步：选择你的模式

#### 模式 A：MCP（推荐大多数用户使用）

在 Agent 客户端中配置 MCP 服务即可。Agent 会在需要时自动启动服务 — **无需手动在新窗口中运行 `uvx cdp-bridge`。**

**Claude Code：**
```bash
claude mcp add cdp-bridge -- uvx cdp-bridge@latest
```

**Codex：**
```bash
codex mcp add cdp-bridge -- uvx cdp-bridge@latest
```

**GitHub Copilot（VS Code）** — 在项目中创建 `.vscode/mcp.json`：
```json
{
  "servers": {
    "cdp-bridge": {
      "command": "uvx",
      "args": ["cdp-bridge@latest"]
    }
  }
}
```

**OpenCode** — 编辑 `~/.config/opencode/opencode.json`：
```json
{
  "mcp": {
    "cdp-bridge": {
      "type": "local",
      "command": ["uvx", "cdp-bridge@latest"],
      "enabled": true
    }
  }
}
```

**其他客户端**（Claude Desktop、Cursor、Windsurf 等）— 添加 MCP 配置：
```json
{
  "mcpServers": {
    "cdp-bridge": {
      "command": "uvx",
      "args": ["cdp-bridge@latest"]
    }
  }
}
```

> **国内用户加速：** 使用镜像加速 MCP 服务启动：
> ```bash
> claude mcp add cdp-bridge -- sh -c 'UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ uvx cdp-bridge@latest'
> ```

> 如需替换，将 `uvx` 改为 `uv tool run`。

#### 模式 B：SDK / Skill

安装 Skill，让 Agent 可以运行 Python 浏览器自动化脚本。

**uvx 一键安装（推荐）：**

```bash
# 安装
uvx --from cdp-browse cdp-browse                      # 自动检测所有 agent
uvx --from cdp-browse cdp-browse --agent claude       # 仅 Claude Code
uvx --from cdp-browse cdp-browse --agent codex        # 仅 Codex（CLI + App）
uvx --from cdp-browse cdp-browse --agent all          # 所有 agent

# 卸载
uvx --from cdp-browse cdp-browse --uninstall
```

> **国内用户加速：** 加镜像前缀加速下载：
> ```bash
> UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ uvx --from cdp-browse cdp-browse
> ```

> 如果 `uvx` 不可用，使用 `uv tool run --from cdp-browse cdp-browse`。

**清理重装**（升级或修复问题时使用）：

```bash
rm -rf ~/.codex/skills/cdp-browse ~/.agents/skills/cdp-browse && uv cache clean --force && uvx --from cdp-browse cdp-browse --agent codex
```

**git clone（手动）：**

```bash
# Claude Code
mkdir -p ~/.claude/skills && git clone https://github.com/dave-wind/cdp-browse.git ~/.claude/skills/cdp-browse

# Codex App（新统一路径）
mkdir -p ~/.agents/skills && git clone https://github.com/dave-wind/cdp-browse.git ~/.agents/skills/cdp-browse

# Codex CLI（旧路径）
mkdir -p ~/.codex/skills && git clone https://github.com/dave-wind/cdp-browse.git ~/.codex/skills/cdp-browse

# 项目级（团队共享）
mkdir -p .agents/skills && git clone https://github.com/dave-wind/cdp-browse.git .agents/skills/cdp-browse
```

**Python SDK** — 无需单独安装。Skill 使用 `uvx --from cdp-browse python` 运行代码，SDK 自动可用。如果要在自己的脚本中使用 SDK：

```bash
pip install cdp-browse
```

## 使用

### 通过 MCP 工具（模式 A）

MCP 服务配置好后，Agent 可以直接调用以下工具 — 服务在首次使用时自动启动：

| 工具 | 说明 |
|------|------|
| `browser_scan` | 扫描页面内容（简化 HTML 或纯文本） |
| `browser_execute_js` | 在页面中执行 JavaScript |
| `browser_navigate` | 导航到指定 URL |
| `browser_screenshot` | 页面截图 |
| `browser_get_tabs` | 获取打开的标签页列表 |
| `browser_switch_tab` | 切换活动标签页 |
| `browser_cookies` | 读取 Cookie |

### 通过 Skill / SDK（模式 B）

直接跟 Agent 说：
```
帮我打开 https://example.com 看看页面上有什么
```

```
抓取这个 GitLab 页面上所有的 commit 信息
```

或写 Python 脚本：
```python
from cdp_sdk import CDPClient, Page

client = CDPClient()
client.find_session()
page = Page(client)

# 导航并等待内容加载
page.navigate("https://example.com", wait_for_selector="h1")
print(page.title)          # "Example Domain"
print(page.extract_text())  # 全页文本

# 提取特定元素
page.query_all("a", "a => ({text: a.textContent.trim(), href: a.href})")

# 点击和交互
page.click("button.submit")
page.scroll_to_bottom()
```

**完整 API 参考见 [SKILL.md](SKILL.md)。**

### MCP vs SDK — 该用哪个？

| 场景 | 推荐方式 | 原因 |
|------|---------|------|
| "帮我看看这个网页" | **MCP** | `browser_scan` 自动降噪，返回干净内容，零启动开销 |
| "抓取这个列表的数据" | **SDK** | `query_all` 精准提取，只拿你要的，省 token |
| "滚动加载更多内容" | **SDK** | 一个脚本循环跑完，不需要多轮对话 |
| "帮我截个图" | **MCP** | 只有 MCP 有 `browser_screenshot` |
| "读取 Cookie" | **MCP** | 只有 MCP 有 `browser_cookies` |
| "多步操作（登录→点击→提交）" | **SDK** | 一次脚本搞定整个流程 |
| "看看有哪些标签页" | **MCP** | `browser_get_tabs` / `browser_switch_tab` |

**最佳实践**：两个都装。查看页面用 MCP，复杂爬取用 SDK。

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| `CDPError: 没有找到任何浏览器 session` | Chrome 未打开或扩展未连接 |
| `CDP-Bridge 连接失败` | 检查 `lsof -i :18765`，确认服务在运行 |
| 扩展图标不是绿色 | 检查代理绕过 `localhost`/`127.0.0.1` |
| 页面内容不完整 | 增加等待时间或使用 `wait_for_selector` |
| `ModuleNotFoundError: No module named 'cdp_sdk'` | 运行 `pip install cdp-browse` |
| `uvx: command not found` | 安装 uv：见[安装 uv](#安装-uv) 章节 |
| `uvx` 国内下载慢 | 使用镜像：`UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ uvx ...` |

## 相关项目

- [cdp-bridge-mcp](https://github.com/Unagi-cq/cdp-bridge-mcp) — MCP 服务（`uvx cdp-bridge@latest`）和 Chrome 扩展的原始来源。本仓库的 `extension/` 目录为该项目的副本，方便用户直接使用。

## License

MIT
