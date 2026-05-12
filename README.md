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
2. **Python 3.10+**
3. **uv** — The fast Python package runner

#### Install uv

`uv` is the recommended way to run Python tools. It replaces `pipx` and avoids common issues on Python 3.12+.

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Or with pip:**
```bash
pip install uv
```

**Or with Homebrew (macOS):**
```bash
brew install uv
```

After installation, `uvx` command is also available (it's an alias for `uv tool run`).

### Installation

#### Step 1: Load the Chrome Extension

The CDP-Bridge extension connects your browser to the MCP server.

```bash
# Clone cdp-bridge-mcp repo to get the extension
git clone https://github.com/Unagi-cq/cdp-bridge-mcp.git
```

Then load it in Chrome:

1. Open `chrome://extensions/`
2. Enable **Developer mode** (top right toggle)
3. Click **Load unpacked**
4. Select the extension folder inside the cloned repo: `cdp-bridge-mcp/src/cdp_bridge/tmwd_cdp_bridge`
5. The extension icon should show **green "Connected"**

> The extension connects to `127.0.0.1:18765` by default. Make sure your system proxy bypasses `localhost` and `127.0.0.1`.

#### Step 2: Install the Skill

**Option A: uvx one-click (recommended)**

Auto-detects installed agents and installs to the right place:

```bash
# Install
uvx --from cdp-browse cdp-browse                      # auto-detect all agents
uvx --from cdp-browse cdp-browse --agent claude       # Claude Code only
uvx --from cdp-browse cdp-browse --agent codex        # Codex (CLI + App)
uvx --from cdp-browse cdp-browse --agent all          # all agents

# Uninstall
uvx --from cdp-browse cdp-browse --uninstall
```

> If `uvx` is not available, use `uv tool run --from cdp-browse cdp-browse` instead.

**Clean reinstall** (if upgrading or fixing issues):

```bash
rm -rf ~/.codex/skills/cdp-browse ~/.agents/skills/cdp-browse && uv cache clean --force && uvx --from cdp-browse cdp-browse --agent codex
```

**Option B: git clone (manual)**

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

#### Step 3: Python SDK (auto-managed)

No separate install needed. The skill uses `uvx --from cdp-browse python` to run code, which automatically provides the SDK. If you want to use the SDK in your own scripts:

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

### Skill vs MCP — Which to Use?

Both Skill (cdp_sdk) and MCP (browser_* tools) control the same browser. Choose based on the task:

| Scenario | Use | Why |
|----------|-----|-----|
| "Check this page" | **MCP** | `browser_scan` filters noise, returns clean content, zero startup |
| "Scrape this list" | **Skill** | `query_all` extracts only what you need, saves tokens |
| "Scroll and load more" | **Skill** | Loop in one script, no multi-round conversation |
| "Take a screenshot" | **MCP** | Only MCP has `browser_screenshot` |
| "Read cookies" | **MCP** | Only MCP has `browser_cookies` |
| "Multi-step flow (login → click → submit)" | **Skill** | One script completes the flow, no back-and-forth |
| "List open tabs" | **MCP** | `browser_get_tabs` / `browser_switch_tab` |

**Speed**: Simple operations are faster via MCP (no uvx startup). Complex multi-step operations are faster via Skill (one script vs multiple MCP rounds).

**Token efficiency**: `browser_scan` auto-filters scripts/styles/hidden elements (~1/3 to 1/5 of raw text). `query_all()` in Skill extracts only targeted data. Both beat `extract_text('body')` which returns everything raw.

**Best practice**: Install both. Use MCP for quick lookups, Skill for complex scraping.

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
│   ├── install.py          # Skill installer
│   └── page.py             # Page — high-level operations
├── pyproject.toml          # pip package config
├── release.py              # Release script
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
| `uvx: command not found` | Install uv: see [Install uv](#install-uv) section |

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
2. **Python 3.10+**
3. **uv** — 快速 Python 包运行器

#### 安装 uv

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

### 安装

#### 第 1 步：加载 Chrome 扩展

CDP-Bridge 扩展负责连接浏览器和 MCP 服务。

```bash
# 克隆 cdp-bridge-mcp 仓库获取扩展
git clone https://github.com/Unagi-cq/cdp-bridge-mcp.git
```

在 Chrome 中加载：

1. 打开 `chrome://extensions/`
2. 开启右上角 **开发者模式**
3. 点击 **加载已解压的扩展程序**
4. 选择克隆仓库中的扩展文件夹：`cdp-bridge-mcp/src/cdp_bridge/tmwd_cdp_bridge`
5. 扩展图标应显示 **绿色 "Connected"**

> 扩展默认连接 `127.0.0.1:18765`。请确保系统代理绕过 `localhost` 和 `127.0.0.1`。

#### 第 2 步：安装 Skill

**方式 A：uvx 一键安装（推荐）**

自动检测已安装的 agent 并安装到对应目录：

```bash
# 安装
uvx --from cdp-browse cdp-browse                      # 自动检测所有 agent
uvx --from cdp-browse cdp-browse --agent claude       # 仅 Claude Code
uvx --from cdp-browse cdp-browse --agent codex        # 仅 Codex（CLI + App）
uvx --from cdp-browse cdp-browse --agent all          # 所有 agent

# 卸载
uvx --from cdp-browse cdp-browse --uninstall
```

> 如果 `uvx` 不可用，使用 `uv tool run --from cdp-browse cdp-browse`。

**清理重装**（升级或修复问题时使用）：

```bash
rm -rf ~/.codex/skills/cdp-browse ~/.agents/skills/cdp-browse && uv cache clean --force && uvx --from cdp-browse cdp-browse --agent codex
```

**方式 B：git clone（手动）**

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

#### 第 3 步：Python SDK（自动管理）

无需单独安装。Skill 使用 `uvx --from cdp-browse python` 运行代码，SDK 自动可用。如果要在自己的脚本中使用 SDK：

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

### Skill vs MCP — 该用哪个？

Skill（cdp_sdk）和 MCP（browser_* 工具）控制的是同一个浏览器，按场景选择：

| 场景 | 推荐方式 | 原因 |
|------|---------|------|
| "帮我看看这个网页" | **MCP** | `browser_scan` 自动降噪，返回干净内容，零启动开销 |
| "抓取这个列表的数据" | **Skill** | `query_all` 精准提取，只拿你要的，省 token |
| "滚动加载更多内容" | **Skill** | 一个脚本循环跑完，不需要多轮对话 |
| "帮我截个图" | **MCP** | 只有 MCP 有 `browser_screenshot` |
| "读取 Cookie" | **MCP** | 只有 MCP 有 `browser_cookies` |
| "多步操作（登录→点击→提交）" | **Skill** | 一次脚本搞定整个流程 |
| "看看有哪些标签页" | **MCP** | `browser_get_tabs` / `browser_switch_tab` |

**速度**：简单操作 MCP 更快（无需 uvx 启动）；复杂多步操作 Skill 更快（一次脚本 vs MCP 多轮对话）。

**Token 效率**：`browser_scan` 自动过滤 script/style/隐藏元素（约为原文的 1/3 ~ 1/5）；Skill 的 `query_all()` 只提取目标数据；两者都比 `extract_text('body')` 全量返回更省 token。

**最佳实践**：两个都装。查看页面用 MCP，复杂爬取用 Skill。

### 常见问题

| 问题 | 解决方案 |
|------|---------|
| `CDPError: 没有找到任何浏览器 session` | Chrome 未打开或扩展未连接 |
| `CDP-Bridge 连接失败` | 检查 `lsof -i :18765`，确认服务在运行 |
| 扩展图标不是绿色 | 检查代理绕过 `localhost`/`127.0.0.1` |
| 页面内容不完整 | 增加等待时间或使用 `wait_for_selector` |
| `ModuleNotFoundError: No module named 'cdp_sdk'` | 运行 `pip install cdp-browse` |
| `uvx: command not found` | 安装 uv：见[安装 uv](#安装-uv) 章节 |

### 相关项目

- [cdp-bridge-mcp](https://github.com/Unagi-cq/cdp-bridge-mcp) — MCP 服务和 Chrome 扩展

### License

MIT
