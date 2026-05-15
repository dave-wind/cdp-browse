// server.js — MCP 服务端模拟
// 接收 stdin 的 JSON 指令，处理后通过 stdout 返回结果

const readline = require("readline");

const rl = readline.createInterface({ input: process.stdin });

rl.on("line", (line) => {
  const msg = JSON.parse(line);
  const result = { id: msg.id, result: `处理完毕: ${msg.method}(${JSON.stringify(msg.params)})` };
  process.stdout.write(JSON.stringify(result) + "\n");
});
