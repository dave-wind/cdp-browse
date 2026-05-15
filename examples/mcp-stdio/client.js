// client.js — MCP 客户端模拟
// 启动 server 子进程，通过 stdin/stdout 通信

const { spawn } = require("child_process");
const server = spawn("node", ["server.js"]);

let id = 0;

// 读取 server 的 stdout
server.stdout.on("data", (data) => {
  const msg = JSON.parse(data.toString().trim());
  console.log("← 收到回复:", msg);
});

// 通过 stdin 发送指令
function send(method, params) {
  const msg = { id: ++id, method, params };
  console.log("→ 发送指令:", msg);
  server.stdin.write(JSON.stringify(msg) + "\n");
}

// 模拟发送几条指令
setTimeout(() => send("browser_scan", { url: "https://example.com" }), 100);
setTimeout(() => send("browser_execute_js", { code: "document.title" }), 500);
setTimeout(() => send("browser_screenshot", {}), 900);
setTimeout(() => server.kill(), 1500);
