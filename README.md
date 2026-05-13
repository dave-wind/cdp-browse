# CDP Browse

Browser automation skill for AI coding agents. Control your local Chrome through CDP-Bridge — scrape pages, click elements, extract data, all while reusing your existing login sessions.

English | [中文](README_CN.md)

---

## What It Does

CDP Browse gives your AI agent (Claude Code, Codex, OpenCode) the ability to browse the web through **your real Chrome browser** — with cookies, login sessions, and JavaScript rendering intact.

Three usage modes in one package:

| Mode | When to Use |
|------|-------------|
| **Skill** | Agent auto-uses it when you say "open this URL", "check this page", etc. |
| **MCP** | Direct tool calls via CDP-Bridge MCP server (scan, execute JS, screenshot) |
| **SDK** | Write Python scripts with `from cdp_sdk import CDPClient, Page` |

## Prerequisites

1. **Chrome** (or any Chromium browser)
2. **Python 3.10+**
3. **uv** — The fast Python package runner

### Install uv

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

**Make `uv` available after restart:**

If `uv` is not found in a new terminal, add it to your PATH:

| Shell | Command |
|-------|---------|
| **zsh** (macOS default) | `echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc` |
| **bash** (Linux) | `echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc` |
| **Windows** | No action needed — installer adds to PATH automatically |

> **Chinese users (国内用户):** Use the Aliyun mirror for faster downloads. Prefix any `uvx` command with the mirror:
> ```bash
> UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ uvx cdp-bridge@latest
> ```
> Or set it permanently:
> ```bash
> export UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
> ```

## Installation

### Step 1: Load the Chrome Extension

The CDP-Bridge extension connects your browser to the MCP server. Install it **first**, before any `uvx` commands.

**One-click download:**
```bash
git clone https://gitee.com/dave-wind/cdp-browse-extenssion.git cdp_browse_extension
```

This downloads to `./cdp_browse_extension/` in the current directory. To specify a custom path:
```bash
git clone https://gitee.com/dave-wind/cdp-browse-extenssion.git /path/to/dest
```

> **Alternative (GitHub hosted script):**
> ```bash
> curl -sSL https://raw.githubusercontent.com/dave-wind/cdp-browse/master/download-extension.sh | bash
> ```

Then load it in Chrome:

1. Open `chrome://extensions/`
2. Enable **Developer mode** (top right toggle)
3. Click **Load unpacked**
4. Select the downloaded extension folder
5. The extension icon should show **green "Connected"**

> The extension connects to `127.0.0.1:18765` by default. Make sure your system proxy bypasses `localhost` and `127.0.0.1`.

### Step 2: Install the Skill

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

> **Chinese users (国内用户):** Add mirror prefix for faster downloads:
> ```bash
> UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ uvx --from cdp-browse cdp-browse
> ```

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

### Step 3: Configure MCP

The MCP server lets your agent use browser tools directly. Choose your client:

**Claude Code:**
```bash
claude mcp add cdp-bridge -- uvx cdp-bridge@latest
```

**Codex:**
```bash
codex mcp add cdp-bridge -- uvx cdp-bridge@latest
```

**Chinese users (国内用户):** Use mirror for faster MCP server startup:
```bash
claude mcp add cdp-bridge -- sh -c 'UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ uvx cdp-bridge@latest'
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

### Step 4: Python SDK (auto-managed)

No separate install needed. The skill uses `uvx --from cdp-browse python` to run code, which automatically provides the SDK. If you want to use the SDK in your own scripts:

```bash
pip install cdp-browse
```

## Usage

### Via Skill (just talk to your agent)

```
Open https://example.com and tell me what's on the page
```

```
帮我看看这个网页 https://git.nevint.com/...
```

```
Scrape all the commit messages from this GitLab page
```

### Via SDK (Python scripts)

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

### Via MCP tools

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

## Skill vs MCP — Which to Use?

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

## Compatible Agents

| Agent | Skill Path |
|-------|-----------|
| **Codex App / CLI / IDE** | `~/.agents/skills/cdp-browse/` |
| **Codex CLI (legacy)** | `~/.codex/skills/cdp-browse/` |
| **Claude Code** | `~/.claude/skills/cdp-browse/` |
| **OpenCode** | `~/.opencode/skills/cdp-browse/` |

Any agent supporting the `SKILL.md` format works.

## File Structure

```
cdp-browse/
├── SKILL.md                # Skill instructions (agent reads this)
├── agents/
│   └── openai.yaml         # Codex App UI metadata
├── extension/              # Chrome extension (CDP-Bridge)
│   ├── manifest.json
│   ├── background.js
│   ├── content.js
│   ├── popup.html / popup.js
│   └── icons/
├── cdp_sdk/                # Python SDK (pip install cdp-browse)
│   ├── __init__.py
│   ├── client.py           # CDPClient — HTTP layer
│   ├── install.py          # Skill installer
│   └── page.py             # Page — high-level operations
├── pyproject.toml          # pip package config
├── release.py              # Release script
└── README.md
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| No browser session found | Chrome not open or extension not connected |
| CDP-Bridge connection failed | Check `lsof -i :18765`, confirm service is running |
| Extension icon not green | Check proxy bypasses `localhost`/`127.0.0.1` |
| Page content incomplete | Increase wait time or use `wait_for_selector` |
| `ModuleNotFoundError: No module named 'cdp_sdk'` | Run `pip install cdp-browse` |
| `uvx: command not found` | Install uv: see [Install uv](#install-uv) section |
| `uvx` slow in China | Use mirror: `UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ uvx ...` |

## Related Projects

- [cdp-bridge-mcp](https://github.com/Unagi-cq/cdp-bridge-mcp) — MCP server (`uvx cdp-bridge@latest`) and original Chrome extension source. The `extension/` folder in this repo is a copy from that project for convenience.

## License

MIT
