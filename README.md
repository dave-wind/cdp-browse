# CDP Browse

Browser automation skill for AI coding agents. Control your local Chrome through CDP-Bridge — scrape pages, click elements, extract data, all while reusing your existing login sessions.

English | [中文](#中文)

---

## English

### What It Does

CDP Browse gives your AI agent (Claude Code, Codex, OpenCode) the ability to browse the web through **your real Chrome browser** — with cookies, login sessions, and JavaScript rendering intact.

Three usage modes in one package:

| Mode | When to Use |
|------|-------------|
| **Skill** | Agent auto-uses it when you say "open this URL", "check this page", etc. |
| **MCP** | Direct tool calls via CDP-Bridge MCP server (scan, execute JS, screenshot) |
| **SDK** | Write Python scripts with `from cdp_sdk import CDPClient, Page` |

### Prerequisites

1. **Chrome** (or any Chromium browser)
2. **Python 3.10+** with `pip`
3. **uv** — Python package runner (`pip install uv` or `brew install uv`)

### Installation

#### Step 1: Load the Chrome Extension

The CDP-Bridge extension connects your browser to the MCP server.

```bash
# Clone cdp-bridge-mcp (only needed for the extension)
git clone https://github.com/Unagi-cq/cdp-bridge-mcp.git /tmp/cdp-bridge-mcp
```

Then load it in Chrome:

1. Open `chrome://extensions/`
2. Enable **Developer mode** (top right toggle)
3. Click **Load unpacked**
4. Select the folder: `/tmp/cdp-bridge-mcp/src/cdp_bridge/tmwd_cdp_bridge`
5. The extension icon should show **green "Connected"**

> The extension connects to `127.0.0.1:18765` by default. Make sure your system proxy bypasses `localhost` and `127.0.0.1`.

#### Step 2: Install the Skill

**Option A: pipx one-click (recommended)**

Auto-detects installed agents and installs to the right place:

```bash
pipx run --spec cdp-browse cdp-browse                      # auto-detect all agents
pipx run --spec cdp-browse cdp-browse --agent claude       # Claude Code only
pipx run --spec cdp-browse cdp-browse --agent codex        # Codex (CLI + App)
pipx run --spec cdp-browse cdp-browse --agent all          # all agents
pipx run --spec cdp-browse cdp-browse --uninstall          # remove
```

**Option B: git clone**

```bash
# Claude Code
mkdir -p ~/.claude/skills && git clone https://github.com/dave-wind/cdp-browse.git ~/.claude/skills/cdp-browse

# Codex App (new unified path)
mkdir -p ~/.agents/skills && git clone https://github.com/dave-wind/cdp-browse.git ~/.agents/skills/cdp-browse

# Codex CLI (legacy path)
mkdir -p ~/.codex/skills && git clone https://github.com/dave-wind/cdp-browse.git ~/.codex/skills/cdp-browse
```

**Option C: Project-level (team sharing)**

```bash
mkdir -p .agents/skills
git clone https://github.com/dave-wind/cdp-browse.git .agents/skills/cdp-browse
```

#### Step 3: Install the Python SDK

```bash
pip install cdp-browse
```

#### Step 4: Configure MCP

The MCP server lets your agent use browser tools directly. Choose your client:

**Claude Code:**
```bash
claude mcp add cdp-bridge -- uvx cdp-bridge@latest
```
> If `uvx` is not available: `claude mcp add cdp-bridge -- uv tool run cdp-bridge@latest`

**Codex:**
```bash
codex mcp add cdp-bridge -- uvx cdp-bridge@latest
```

**Manual config** (any MCP client, e.g. Claude Desktop, Cursor):
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

> Replace `uvx` with `uv tool run` if needed.

### Usage

#### Via Skill (just talk to your agent)

```
Open https://example.com and tell me what's on the page
```

```
帮我看看这个网页 https://git.nevint.com/...
```

```
Scrape all the commit messages from this GitLab page
```

#### Via SDK (Python scripts)

```python
from cdp_sdk import CDPClient, Page

client = CDPClient()
client.find_session()
page = Page(client)

# Navigate and wait for content
page.navigate("https://example.com", wait_for_selector="h1")
print(page.title)          # "Example Domain"
print(page.extract_text())  # full page text

# Extract specific elements
page.query_all("a", "a => ({text: a.textContent.trim(), href: a.href})")

# Click and interact
page.click("button.submit")
page.scroll_to_bottom()
```

**Full API reference is in the [SKILL.md](SKILL.md).**

#### Via MCP tools

When the MCP server is running, your agent can call these tools directly:

| Tool | Description |
|------|-------------|
| `browser_scan` | Scan page content (simplified HTML or plain text) |
| `browser_execute_js` | Execute JavaScript in the page |
| `browser_navigate` | Navigate to a URL |
| `browser_screenshot` | Take a screenshot |
| `browser_get_tabs` | List open tabs |
| `browser_switch_tab` | Switch active tab |
| `browser_cookies` | Read cookies |

### Compatible Agents

| Agent | Skill Path |
|-------|-----------|
| **Codex App / CLI / IDE** | `~/.agents/skills/cdp-browse/` |
| **Codex CLI (legacy)** | `~/.codex/skills/cdp-browse/` |
| **Claude Code** | `~/.claude/skills/cdp-browse/` |
| **OpenCode** | `~/.opencode/skills/cdp-browse/` |

Any agent supporting the `SKILL.md` format works.

### File Structure

```
cdp-browse/
├── SKILL.md                # Skill instructions (agent reads this)
├── agents/
│   └── openai.yaml         # Codex App UI metadata
├── cdp_sdk/                # Python SDK (pip install cdp-browse)
│   ├── __init__.py
│   ├── client.py           # CDPClient — HTTP layer
│   └── page.py             # Page — high-level operations
├── pyproject.toml          # pip package config
├── install.py              # pipx installer
└── README.md
```

### Troubleshooting

| Symptom | Fix |
|---------|-----|
| `CDPError: 没有找到任何浏览器 session` | Chrome not open or extension not connected |
| `CDP-Bridge 连接失败` | Check `lsof -i :18765`, confirm service is running |
| Extension icon not green | Check proxy bypasses `localhost`/`127.0.0.1` |
| Page content incomplete | Increase wait time or use `wait_for_selector` |
| `ModuleNotFoundError: No module named 'cdp_sdk'` | Run `pip install cdp-browse` |

### Related Projects

- [cdp-bridge-mcp](https://github.com/Unagi-cq/cdp-bridge-mcp) — The MCP server and Chrome extension

---

## 中文

### 它是什么

CDP Browse 让你的 AI 编码助手（Claude Code、Codex、OpenCode）能够控制你的 **真实 Chrome 浏览器**——Cookie、登录态、JS 渲染全部复用，不需要重新登录。

一个包，三种用法：

| 模式 | 适用场景 |
|------|---------|
| **Skill** | 对 agent 说"帮我看看这个网页"自动触发 |
| **MCP** | 通过 CDP-Bridge MCP 服务直接调用浏览器工具 |
| **SDK** | 用 Python 写脚本 `from cdp_sdk import CDPClient, Page` |

### 前置条件

1. **Chrome**（或其他 Chromium 浏览器）
2. **Python 3.10+** 和 `pip`
3. **uv** — Python 包运行器（`pip install uv` 或 `brew install uv`）

### 安装

#### 第 1 步：加载 Chrome 扩展

CDP-Bridge 扩展负责连接浏览器和 MCP 服务。

```bash
# 克隆 cdp-bridge-mcp（只需要扩展文件夹）
git clone https://github.com/Unagi-cq/cdp-bridge-mcp.git /tmp/cdp-bridge-mcp
```

在 Chrome 中加载：

1. 打开 `chrome://extensions/`
2. 开启右上角 **开发者模式**
3. 点击 **加载已解压的扩展程序**
4. 选择文件夹：`/tmp/cdp-bridge-mcp/src/cdp_bridge/tmwd_cdp_bridge`
5. 扩展图标应显示 **绿色 "Connected"**

> 扩展默认连接 `127.0.0.1:18765`。请确保系统代理绕过 `localhost` 和 `127.0.0.1`。

#### 第 2 步：安装 Skill

**方式 A：pipx 一键安装（推荐）**

自动检测已安装的 agent 并安装到对应目录：

```bash
pipx run --spec cdp-browse cdp-browse                      # 自动检测所有 agent
pipx run --spec cdp-browse cdp-browse --agent claude       # 仅 Claude Code
pipx run --spec cdp-browse cdp-browse --agent codex        # 仅 Codex（CLI + App）
pipx run --spec cdp-browse cdp-browse --agent all          # 所有 agent
pipx run --spec cdp-browse cdp-browse --uninstall          # 卸载
```

**方式 B：git clone**

```bash
# Claude Code
mkdir -p ~/.claude/skills && git clone https://github.com/dave-wind/cdp-browse.git ~/.claude/skills/cdp-browse

# Codex App（新统一路径）
mkdir -p ~/.agents/skills && git clone https://github.com/dave-wind/cdp-browse.git ~/.agents/skills/cdp-browse

# Codex CLI（旧路径）
mkdir -p ~/.codex/skills && git clone https://github.com/dave-wind/cdp-browse.git ~/.codex/skills/cdp-browse
```

**方式 C：项目级安装（团队共享）**

```bash
mkdir -p .agents/skills
git clone https://github.com/dave-wind/cdp-browse.git .agents/skills/cdp-browse
```

#### 第 3 步：安装 Python SDK

```bash
pip install cdp-browse
```

#### 第 4 步：配置 MCP

MCP 服务让 agent 可以直接使用浏览器工具。

**Claude Code：**
```bash
claude mcp add cdp-bridge -- uvx cdp-bridge@latest
```
> 如果 `uvx` 不可用：`claude mcp add cdp-bridge -- uv tool run cdp-bridge@latest`

**Codex：**
```bash
codex mcp add cdp-bridge -- uvx cdp-bridge@latest
```

**手动配置**（任何 MCP 客户端，如 Claude Desktop、Cursor）：
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
> 如需替换，将 `uvx` 改为 `uv tool run`。

### 使用

#### 通过 Skill（直接跟 agent 说）

```
帮我打开 https://example.com 看看页面上有什么
```

```
抓取这个 GitLab 页面上所有的 commit 信息
```

#### 通过 SDK（Python 脚本）

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

#### 通过 MCP 工具

MCP 服务运行时，agent 可以直接调用以下工具：

| 工具 | 说明 |
|------|------|
| `browser_scan` | 扫描页面内容（简化 HTML 或纯文本） |
| `browser_execute_js` | 在页面中执行 JavaScript |
| `browser_navigate` | 导航到指定 URL |
| `browser_screenshot` | 页面截图 |
| `browser_get_tabs` | 获取打开的标签页列表 |
| `browser_switch_tab` | 切换活动标签页 |
| `browser_cookies` | 读取 Cookie |

### 常见问题

| 问题 | 解决方案 |
|------|---------|
| `CDPError: 没有找到任何浏览器 session` | Chrome 未打开或扩展未连接 |
| `CDP-Bridge 连接失败` | 检查 `lsof -i :18765`，确认服务在运行 |
| 扩展图标不是绿色 | 检查代理绕过 `localhost`/`127.0.0.1` |
| 页面内容不完整 | 增加等待时间或使用 `wait_for_selector` |
| `ModuleNotFoundError: No module named 'cdp_sdk'` | 运行 `pip install cdp-browse` |

### 相关项目

- [cdp-bridge-mcp](https://github.com/Unagi-cq/cdp-bridge-mcp) — MCP 服务和 Chrome 扩展

### License

MIT
