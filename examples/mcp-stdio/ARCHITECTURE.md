# CDP Browse 架构说明

## 通信链路

```
Claude Code (MCP 客户端)
  │
  │  spawn 子进程 (stdio)
  │
  ├── stdin.write()  ──→  cdp-bridge (MCP Server)
  │                         │
  │                         ├── 处理 MCP 指令 (browser_scan 等)
  │                         │
  │                         └── WebSocket Server :18765
  │                               │
  │                               └── WebSocket 双向通信
  │                                     │
  └── stdout.on()  ←──                    │
        返回结果                            ▼
                                    Chrome 扩展 (WebSocket 客户端)
                                      │
                                      ├── chrome.scripting.executeScript
                                      └── chrome.debugger (CDP 协议)
                                              │
                                              ▼
                                          网页 DOM (执行 JS，获取数据)
```

## MCP 通信模型

MCP 有两种传输方式：

| 方式 | 场景 | 例子 |
|------|------|------|
| **stdio** | 本地工具 | `claude mcp add cdp-bridge -- uvx cdp-bridge@latest` |
| **HTTP/SSE** | 远程服务 | 云端 API 服务 |

本项目用的是 **stdio 模式**。Claude Code 把 cdp-bridge 当子进程启动，通过 stdin/stdout 管道通信（JSON-RPC 格式）。

## 各组件角色

| 组件 | 角色 | 职责 |
|------|------|------|
| Claude Code / Codex | MCP 客户端 | spawn 子进程，通过 stdin 发指令，stdout 收结果 |
| cdp-bridge (`uvx cdp-bridge@latest`) | MCP Server + WebSocket Server | 接收 MCP 指令，转发给浏览器扩展 |
| Chrome 扩展 | WebSocket 客户端 | 连接 cdp-bridge，在页面中执行 JS 并返回结果 |

## 最简 stdio 示例

用 Node.js 理解 stdio 进程通信：

**server.js**（相当于 cdp-bridge）
```javascript
const readline = require("readline");
const rl = readline.createInterface({ input: process.stdin });
rl.on("line", (line) => {
  const msg = JSON.parse(line);
  const result = { id: msg.id, result: `处理完毕: ${msg.method}` };
  process.stdout.write(JSON.stringify(result) + "\n");
});
```

**client.js**（相当于 Claude Code）
```javascript
const { spawn } = require("child_process");
const server = spawn("node", ["server.js"]);

// 收结果
server.stdout.on("data", (data) => {
  console.log("← 收到:", JSON.parse(data.toString()));
});

// 发指令
server.stdin.write(JSON.stringify({
  id: 1, method: "browser_scan", params: { url: "https://example.com" }
}) + "\n");
```

运行 `node client.js`，它会自动 spawn server.js，无需手动启动服务端。

真实项目的区别：cdp-bridge（server.js）多了一层 WebSocket，把指令转发给 Chrome 扩展执行。

## 完整数据流

以"帮我看看这个网页"为例：

```
① 用户: "帮我看看 https://example.com"
② Claude Code 通过 stdin 发送: {"method": "browser_scan", "params": {"url": "https://example.com"}}
③ cdp-bridge 收到 MCP 指令，通过 WebSocket 转发给 Chrome 扩展
④ 扩展用 chrome.scripting.executeScript 在页面执行 JS
⑤ JS 返回页面内容给扩展
⑥ 扩展通过 WebSocket 把结果发回 cdp-bridge
⑦ cdp-bridge 通过 stdout 把结果返回给 Claude Code
⑧ Claude Code 拿到页面内容，回复用户
```
